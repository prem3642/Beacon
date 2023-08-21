# -*- coding: utf-8 -*-
# Standard Library
import csv
import time
from datetime import datetime
from smtplib import SMTPException
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

# Third Party Stuff
import reversion
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import BadHeaderError
from django.forms.models import model_to_dict
from django.utils import timezone
from django_sites import get_by_id as get_site_by_id
from django_sites import get_current
from mail_templated import send_mail
from requests.exceptions import RequestException
from rest_framework.exceptions import ValidationError

# beacon Stuff
from beacon.answers.models import UserAppointment, UserResponse
from beacon.base.exceptions import NotVerified
from beacon.base.models import UserCSVUpload
from beacon.campaign_monitor.services import (
    add_multiple_subscribers_from_data,
    add_new_subscriber,
)
from beacon.cognito import services as cognito_services
from beacon.mdlive import services as mdlive_services
from beacon.mdlive import tasks as mdlive_tasks
from beacon.organisations.models import Organisation
from beacon.organisations.services import get_organisation

from .models import UserManager
from .tasks import send_appointment_email_to_user_task, send_f2f_data_task
from .utils import (
    get_auth_token_from_request,
    get_relationship_from_user,
    send_appointment_email_to_user,
    send_f2f_data_to_bwb_server,
)

if TYPE_CHECKING:
    from .models import User


def get_cache_key(key, **kwargs):
    mapping = {"USER_TOKEN": "user:{id}:tokens"}
    return mapping[key].format(**kwargs)


def get_default_user_password(first_name, last_name, birth_date):
    return "{}{}{}".format(
        first_name[0].capitalize(), last_name.capitalize(), birth_date.year
    )


def set_logged_in_user_token_to_cache(
    user_id, token, max_age_in_minutes=settings.JWT_TOKEN_EXPIRATION_DURATION
):
    cache_key = get_cache_key("USER_TOKEN", id=user_id)
    user_tokens = cache.get(cache_key, [])
    user_tokens.append(token)
    cache.set(cache_key, user_tokens, timeout=60 * max_age_in_minutes)


def get_logged_in_user_tokens_from_cache(user_id):
    cache_key = get_cache_key("USER_TOKEN", id=user_id)
    user_tokens = cache.get(cache_key, [])
    return user_tokens


def remove_user_token_from_cache(
    request, max_age_in_minutes=settings.JWT_TOKEN_EXPIRATION_DURATION
):
    user_id = str(request.user.id)
    token = get_auth_token_from_request(request)
    cache_key = get_cache_key("USER_TOKEN", id=user_id)
    user_tokens = cache.get(cache_key, [])
    user_tokens = [t for t in user_tokens if t != token]
    cache.set(cache_key, user_tokens, timeout=60 * max_age_in_minutes)


def get_bwb_data(
    user_data: dict,
    cognito_sub: str,
    mdlive_id: str,
    relationship: str,
    user_response: UserResponse,
    user_appointment: UserAppointment,
    organisation: Organisation,
) -> dict:
    """
    create and returns the dict for BWB
    :param user_data:
    :param cognito_sub:
    :param mdlive_id:
    :param relationship:
    :param user_response:
    :param user_appointment:
    :param organisation:
    :return: dict of mdlive data
    """
    intake_questions_data: dict = {}
    appointment_data: dict = {}

    # MDLive only accepts  10 digit phone number
    # Removed country code before passing it to MDLive
    bwb_data = {
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "gender": user_data.get("gender"),
        "birthdate": str(user_data.get("birthdate")),
        "cognito_id": cognito_sub,
        "mdlive_id": mdlive_id,
        "email": UserManager.normalize_email(user_data.get("email")),
        "phone": user_data.get("phone"),
        "address": {
            "address1": user_data.get("address1"),
            "address2": user_data.get("address2", ""),
            "city": user_data.get("city"),
            "state": user_data.get("state"),
            "zip": user_data.get("zip"),
        },
        "employment_status": user_data.get("employment_status"),
        "relationship_status": user_data.get("relationship_status"),
        "job_title": user_data.get("job_title"),
        "emotional_support_for": relationship,
    }
    if organisation:
        bwb_data["organisation_parent_code"] = organisation.parent_code
        bwb_data["organisation_location"] = organisation.location
        if not organisation.parent_code and organisation.parent:
            bwb_data["organisation_parent_code"] = organisation.parent.parent_code
    if user_response:
        intake_questions_data = {
            "chief_complaint1": user_response.chief_complaint1,
            "chief_complaint2": user_response.chief_complaint2,
            "appointment_state": user_response.appointment_state,
            "safety_sensitive_position": user_response.safety_sensitive_position,
            "how_often_less_interest_in_things": user_response.how_often_less_interest_in_things,
            "how_often_depressed": user_response.how_often_depressed,
            "how_often_nervous": user_response.how_often_nervous,
            "how_often_worry": user_response.how_often_worry,
            "difficulty_in_keeping_drinking_limit": user_response.difficulty_in_keeping_drinking_limit,
            "felt_cut_down_drinking": user_response.felt_cut_down_drinking,
            "how_emotionally_doing": user_response.how_emotionally_doing,
            "how_physical_health": user_response.how_physical_health,
            "comfortable_in_managing_finances": user_response.comfortable_in_managing_finances,
            "people_support": user_response.people_support,
            "resources_to_manage": user_response.resources_to_manage,
            "number_of_days_less_productive": user_response.number_of_days_less_productive,
            "number_of_days_missed_work": user_response.number_of_days_missed_work,
            "is_employee": user_response.is_employee,
            "relationship_with_employee": user_response.relationship_with_employee,
            "employee_name": user_response.employee_name,
            "employee_birth_date": str(user_response.employee_birth_date),
            "organisation_username": organisation.username if organisation else None,
        }
    if user_appointment:
        appointment_data = {
            "f2f_gender_preference": user_appointment.f2f_gender_preference,
            # 'f2f_comfortable_language': user_appointment.f2f_comfortable_language,
            "f2f_preferred_contact": user_appointment.f2f_preferred_contact,
            # 'f2f_preferred_time': user_appointment.f2f_preferred_time,
            "f2f_okay_to_leave_voicemail": user_appointment.f2f_okay_to_leave_voicemail,
            "f2f_counselor_search_address": user_appointment.f2f_counselor_search_address,
            "f2f_address": {
                "f2f_address1": user_appointment.f2f_address1,
                "f2f_address2": user_appointment.f2f_address2,
                "f2f_city": user_appointment.f2f_city,
                "f2f_zip": user_appointment.f2f_zip,
                "f2f_state": user_appointment.f2f_state,
            },
            "f2f_counselor_notes": user_appointment.f2f_counselor_notes,
        }
    bwb_data.update(intake_questions_data)
    bwb_data.update(appointment_data)
    return bwb_data


def get_user_by_email(email: str) -> Optional["User"]:
    return get_user_model().objects.filter(email__iexact=email).first()


def get_and_authenticate_user(email: str, password: str) -> tuple:
    """
    Authenticate user on cognito and fetch its details from it
    Request param is to set cognito refresh, session tokens

    :return: user object and cognito user object
    :param email: Email of the user
    :param password: Password of the user
    """
    user = get_user_by_email(email)
    if user is None:
        raise ValidationError("That email does not exist in our system, sorry!")

    if (
        user.num_of_failed_login_attempts
        >= settings.NUM_OF_FAILED_LOGIN_ATTEMPTS_ALLOWED
    ):
        if user.last_failed_login_attempt_datetime:
            duration = timezone.now() - user.last_failed_login_attempt_datetime
            if (
                duration.seconds / 60
            ) < settings.ACCOUNT_LOCK_DURATION_AFTER_FAILED_LOGIN_ATTEMPTS:
                raise ValidationError(
                    "Due to many unsuccessful login attempts, your account has been "
                    "temporarily disabled. Please try again later."
                )
            else:
                user.num_of_failed_login_attempts = 0

    if user.is_verified is False:
        raise NotVerified("User is not verified yet!")

    try:
        cognito_user = cognito_services.authenticate(user, password)
    except ValidationError as e:
        user.num_of_failed_login_attempts += 1
        user.last_failed_login_attempt_datetime = timezone.now()
        user.save()
        raise e
    user.cognito_id_token = cognito_user.id_token
    user.cognito_access_token = cognito_user.access_token
    user.cognito_refresh_token = cognito_user.refresh_token
    user.num_of_failed_login_attempts = 0
    user.save()
    return user, cognito_user


def get_cognito_data_from_user_data(user_data: dict) -> dict:
    """
    Creates a dict with specific fields only for cognito
    :param user_data: Dict of user data
    :return: dict of user data with only cognito specific parameters
    """

    def _remove_null_keys(user_dict):
        return {k: v for k, v in user_dict.items() if v is not None}

    user_data = _remove_null_keys(user_data)
    # Gender is nullable if user is created via SCC. In order to avoid failure of this
    # required attribute at Cognito, adding a default "U" (unknown) value.
    if user_data.get("gender", "") not in ("M", "F"):
        user_data.update({"gender": "U"})

    cognito_data: Dict[Union[str, Any], Union[str, Any]] = {
        "email": UserManager.normalize_email(user_data.get("email")),
        "password": user_data.get("password"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "birthdate": str(user_data.get("birthdate", "")),
        "phone": str(user_data.get("phone", "")),
        "address1": user_data.get("address1", ""),
        "address2": user_data.get("address2", ""),
        "city": user_data.get("city", ""),
        "state": user_data.get("state", ""),
        "zip": user_data.get("zip", ""),
        "gender": user_data.get("gender", ""),
        "employment_status": user_data.get("employment_status", ""),
        "relationship_status": user_data.get("relationship_status", ""),
        "job_title": user_data.get("job_title", ""),
        "is_active": str(user_data.get("is_active", False)),
    }

    return cognito_data


def create_user_account(
    user_data,
    relationship="Self",
    request=None,
    admin_force_registration=False,
    source=get_user_model().API,
    source_admin="",
):
    """
    Create user account on Beacon
    Create user account on Cognito
    Create user account on MDLive
    :param user_data: User data dict
    :param relationship: relationship with the person getting support for
    :param request: Request object
    :return: Beacon user and mdlive token details
    """
    user_data["email"] = UserManager.normalize_email(user_data.get("email"))
    organisation = user_data.get("organisation")
    if organisation is None and request is not None:
        organisation, _ = get_organisation(request)
        user_response = user_data.get("answer")
        if (
            user_response is not None
            and user_response.employee_organisation is not None
        ):
            organisation = user_response.employee_organisation
    cognito_data = get_cognito_data_from_user_data(user_data)
    cognito_user_response = cognito_services.register(cognito_data)
    cognito_sub = cognito_user_response["UserSub"]  # Cognito user unique uuid
    try:
        mdlive_data = mdlive_services.get_mdlive_data_from_cognito_data(
            cognito_data=cognito_data,
            cognito_sub=cognito_sub,
            birth_date_str=cognito_data.get("birthdate"),
            relationship=relationship,
            is_new_user=True,
            source=source,
            time_zone=user_data.get("timezone", None),
        )
        mdlive_user_data = mdlive_services.get_user_token(
            mdlive_data, organisation=organisation
        )
        mdlive_user_id = mdlive_user_data["user"]["id"]
        if not admin_force_registration:
            # Admin can override registration
            # with this flag and avoid
            # causing error if this is a
            # duplicate profile as per MDLive.
            existing_user = (
                get_user_model().objects.filter(mdlive_id=mdlive_user_id).first()
            )
            if existing_user:
                # Probably MDLive has already made the
                # updates with this new registration
                # form on the existing user
                # So, we will re-update the account
                # on their end with the actual
                # info that we have
                mdlive_services.get_mdlive_token_data_for_user(existing_user)
                raise ValidationError(
                    "This user account exists on MDlive and can't be created."
                )
    except ValidationError as e:
        # MDlive registration failed, so we'll rollback
        # AWS cognito registration
        cognito_services.cognito_admin_delete_user(email=cognito_data["email"])
        raise e
    # Update user's timezone at MDLive in background
    mdlive_user_jwt = mdlive_user_data.get("jwt", None)
    mdlive_tasks.sync_user_timezone_with_mdlive_timezone_id_task.delay(
        patient_id=mdlive_user_id,
        timezone_id=mdlive_data["auth"]["us_time_zone_id"],
        token=mdlive_user_jwt,
    )

    # Ensure initial revision of the user is created
    with reversion.create_revision():
        user = get_user_model().objects.create_user(
            email=user_data.get("email"),
            password=user_data.get("password"),
            mdlive_id=mdlive_user_data.get("user").get("id"),
            id=cognito_sub,
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            dfd_user_id=user_data.get("dfd_user_id"),
            birthdate=user_data.get("birthdate"),
            gender=user_data.get("gender"),
            phone=user_data.get("phone"),
            job_title=user_data.get("job_title"),
            relationship_status=user_data.get("relationship_status"),
            employment_status=user_data.get("employment_status"),
            address1=user_data.get("address1"),
            address2=user_data.get("address2"),
            city=user_data.get("city"),
            state=user_data.get("state"),
            zip=user_data.get("zip"),
            agrees_to_beacon_privacy_notice=user_data.get(
                "agrees_to_beacon_privacy_notice"
            ),
            agrees_to_mdlive_informed_consent=user_data.get(
                "agrees_to_mdlive_informed_consent"
            ),
            agrees_to_mdlive_privacy_agreement=user_data.get(
                "agrees_to_mdlive_privacy_agreement"
            ),
            mdlive_consent_user_initials=user_data.get("mdlive_consent_user_initials"),
            organisation=organisation,
            connects_mbr_id=user_data.get("connects_mbr_id", ""),
            send_to_scc_if_non_f2f=user_data.get("send_to_scc_if_non_f2f", False),
            timezone=mdlive_services.get_timezone_from_mdlive_us_time_zone_id(
                mdlive_data["auth"].get("us_time_zone_id", None)
            ),
            source=source,
            source_admin=source_admin,
        )
    return user, mdlive_user_data, cognito_user_response


def send_data_to_bwb_server_and_email_user(user, user_response, user_appointment=None):
    user_data = user.__dict__
    if user_appointment is None:
        user_appointment = user_response.appointments.first()

    # The appointment_state is being replicated in the user_appointment
    # from user_response, because the user_response's appointment state
    # can be modified in using the `/api/me/update-appointment-state` API
    # or using the update responses API call.
    # We are maintaining the actual appointment state in appointment
    # to track it's value historically.
    if user_appointment is not None:
        # During registration, we don't have user_appointment, so
        # appointment_state should be only set when user_appointment
        # is available to this service.
        user_appointment.appointment_state = user_response.appointment_state
        user_appointment.save()
    # Check F2F method and send data to BWB server
    if (
        user_appointment
        and user_appointment.appointment_method == UserAppointment.FACE_TO_FACE
    ):
        relationship = get_relationship_from_user(user)
        bwb_data = get_bwb_data(
            user_data,
            str(user.id),
            str(user.mdlive_id),
            relationship,
            user_response,
            user_appointment,
            user.organisation,
        )
        response = None
        try:
            response = send_f2f_data_to_bwb_server(str(user_appointment.id), bwb_data)
        except RequestException:
            send_f2f_data_task.delay(str(user_appointment.id), bwb_data)
        except ValidationError:
            send_f2f_data_task.delay(str(user_appointment.id), bwb_data)

        # Send email to user regarding the new account and password
        try:
            send_appointment_email_to_user(
                str(user.id), response, user_data.get("first_name")
            )
        except SMTPException:
            send_appointment_email_to_user_task.delay(
                str(user_appointment.id),
                str(user.id),
                response,
                user_data.get("first_name"),
            )
        except BadHeaderError:
            send_appointment_email_to_user_task.delay(
                str(user_appointment.id),
                str(user.id),
                response,
                user_data.get("first_name"),
            )
        return response


def handle_uploaded_file(f):
    # Only one file is going to be processed at a time
    # Saving file which celery can pick directly later on
    with open(settings.USER_CSV_IMPORT_FILE_PATH, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def check_user_already_exists(email):
    if get_user_model().objects.filter(email=email).exists():
        return f"User with email {email} already exists!"
    return None


def get_user_data_from_csv_upload_row(row, org_model):
    data = None
    parent_code = row.get("PARENT", None)
    org = org_model.objects.filter(parent_code=parent_code).first()

    email = row.get("EMAIL")
    if org is None:
        return data, f"Either ParentCode is null or does not exists for user {email}"

    # Need to set the registration date in csv as created_at
    date_joined = None
    date_joined_str = row.get("REFERRAL_DATE")
    if date_joined_str:
        date_joined = datetime.strptime(date_joined_str, "%m/%d/%Y").date()

    error = check_user_already_exists(email)
    if error is not None:
        return data, error

    first_name = row.get("FSTNAM")
    last_name = row.get("LSTNAM")
    date = datetime.today().date()
    password = f"CSVUploaded{date.year}"
    if first_name and last_name:
        password = get_default_user_password(first_name, last_name, date)
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "date_joined": date_joined,
        "organisation": org,
    }
    return data, error


# Not in use right now
def create_user_from_csv_upload_row(row, org_model):
    user = None
    data, error = get_user_data_from_csv_upload_row(row, org_model)
    if error is not None:
        return user, error

    cognito_data = get_cognito_data_from_user_data(data)
    try:
        cognito_user_response = cognito_services.register(cognito_data)
    except ValidationError as e:
        return user, f'Error from cognito for user {data.get("email")}: {e}'

    cognito_sub = cognito_user_response["UserSub"]  # Cognito user unique uuid
    user_model = get_user_model()
    user = user_model.objects.create_user(
        email=data.get("email"),
        password=data.get("password"),
        id=cognito_sub,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        organisation=data.get("organisation"),
        source=user_model.CSV,
    )
    if data.get("date_joined") is not None:
        user.date_joined = data.get("date_joined")
        user.save()
    return user, error  # error is None here as there is check for not null error above


def get_user_response_data_from_csv_upload_row(row):
    chief_complaint_mapping = {
        "FAMILY PROBLEM": "Family Issues",
        "MEDICAL PROBLEM": "Family Issues",
        "INTEGRATED CARE ISSUES": "Family Issues",
        "EATING DISORDER": "Family Issues",
        "DISABILITY": "Family Issues",
        "CHILD CARE PROBLEM": "Family Issues",
        "ADULT/ELDER CARE PROBLEM": "Family Issues",
        "DEPRESSION": "Depression",
        "ANXIETY": "Anxiety",
        "SITUATIONAL/ADJUSTMENT CONCERN": "Anxiety",
        "PSYCHOTIC THINKING?": "Anxiety",
        "IMPULSE CONTROL PROBLEM": "Anxiety",
        "HYPERACTIVITY LEARNING PROBLEM": "Anxiety",
        "GRIEF/LOSS": "Grief or Loss",
        "MARITAL/RELATIONSHIP PROBLEM": "Relationship Issues",
        "STRESS": "Stress",
        "JOB/OCCUPATIONAL PROBLEM": "Stress",
        "LEGAL PROBLEM": "Stress",
        "FINANCIAL PROBLEM": "Stress",
        "MIXED ALCOHOL AND DRUG ABUSE": "Alcohol or Drug use",
        "ALCOHOL ABUSE": "Alcohol or Drug use",
        "DRUG ABUSE": "Alcohol or Drug use",
    }

    felt_cut_down_drinking = None
    difficulty_in_keeping_drinking_limit = None
    if row.get("BWBQ7A") == "No":
        felt_cut_down_drinking = False
    if row.get("BWBQ7A") == "Yes":
        felt_cut_down_drinking = True
    if row.get("BWBQ7B") == "No":
        difficulty_in_keeping_drinking_limit = False
    if row.get("BWBQ7B") == "Yes":
        difficulty_in_keeping_drinking_limit = True
    user_response_data = {
        "emotional_support_for": "Self",
        "request_type": row.get("RequestType", "Emotional"),
        "chief_complaint1": chief_complaint_mapping.get(row.get("PRESENTING_PROBLEM")),
        "chief_complaint2": row.get("SECONDARY_PROBLEM"),
        "how_emotionally_doing": row.get("BWBQ8"),
        "how_physical_health": row.get("BWBQ9"),
        "people_support": row.get("BWBQ10"),
        "comfortable_in_managing_finances": row.get("BWBQ11"),
        "resources_to_manage": row.get("BWBQ12"),
        "difficulty_in_keeping_drinking_limit": difficulty_in_keeping_drinking_limit,
        "felt_cut_down_drinking": felt_cut_down_drinking,
    }
    return user_response_data


def get_csv_data_from_file():
    with open(settings.USER_CSV_IMPORT_FILE_PATH) as csv_file:
        reader = csv.DictReader(csv_file)
        errors = list()
        rows = dict()
        duplicate_users = list()
        null_email_rows_count = 0
        for index, row in enumerate(reader):
            email = row.get("EMAIL")
            if not email:
                errors.append(
                    f"Email does not exists for user on row number {index+2}!"
                )
                null_email_rows_count += 1
                continue
            if email in rows:
                errors.append(f"Duplicate entries exists for user {email}")
                duplicate_users.append(email)
            else:
                rows[email] = row

        total_count = len(rows) + len(duplicate_users) + null_email_rows_count
        # Removing duplicate users
        for user in duplicate_users:
            rows.pop(user, None)
        return rows, total_count, errors


# Not in use right now
def create_users_from_csv():
    """
    Parse CSV file and create user one by one on Cognito, Campaign Monitor and locally
    CSV file will be picked from the path defined in settings as `USER_CSV_IMPORT_FILE_PATH`
    :return: None
    """
    org_model = apps.get_model("organisations", "Organisation")
    user_response_model = apps.get_model("answers", "UserResponse")
    # get_solo will create the item if it does not already exist
    user_csv_upload_instance = UserCSVUpload.get_solo()
    rows, total_count, errors = get_csv_data_from_file()

    user_csv_upload_instance.csv_total_count = total_count
    user_csv_upload_instance.status = UserCSVUpload.IN_PROGRESS
    user_csv_upload_instance.save()
    # Update the instance to track the progress
    completed_count = user_csv_upload_instance.csv_completed_count
    for key in rows:
        if key:
            user, error = create_user_from_csv_upload_row(rows[key], org_model)
            if error is not None:
                errors.append(error)
                continue
            user_response_data = get_user_response_data_from_csv_upload_row(rows[key])
            user_response_model.objects.create(
                response=[], user=user, **user_response_data
            )

            # Send data to campaign monitor
            _, error = add_new_subscriber(user)
            if error is not None:
                errors.append(
                    f"Error in sending data to campaign monitor for {user.email}: {error}"
                )
                continue

            # Commented code increasing completed count by extra 1, need to debug later on
            # user_csv_upload_instance.csv_completed_count = F('csv_completed_count') + 1
            completed_count += 1
            user_csv_upload_instance.csv_completed_count = completed_count
            user_csv_upload_instance.save()
        # Adding delay as cognito allow only 10 requests per second
        time.sleep(0.2)

    user_csv_upload_instance.status = UserCSVUpload.DONE
    user_csv_upload_instance.errors = errors
    user_csv_upload_instance.save()


def send_users_to_campaign_monitor_from_csv():
    """
    Parse CSV file and send users data to Campaign Monitor
    CSV file will be picked from the path defined in settings as `USER_CSV_IMPORT_FILE_PATH`
    :return: campaign monitor response
    """
    org_model = apps.get_model("organisations", "Organisation")
    # get_solo will create the item if it does not already exist
    user_csv_upload_instance = UserCSVUpload.get_solo()
    rows, total_count, errors = get_csv_data_from_file()

    user_csv_upload_instance.csv_total_count = total_count
    user_csv_upload_instance.csv_completed_count = 0
    user_csv_upload_instance.errors = None
    user_csv_upload_instance.status = UserCSVUpload.IN_PROGRESS
    user_csv_upload_instance.save()
    # Update the instance to track the progress
    completed_count = user_csv_upload_instance.csv_completed_count
    campaign_monitor_data = list()
    for key in rows:
        if key:
            user_data, error = get_user_data_from_csv_upload_row(rows[key], org_model)
            if error is not None:
                errors.append(error)
                continue
            user_response_data = get_user_response_data_from_csv_upload_row(rows[key])
            org_data = None
            org_parent_data = None
            if user_data.get("organisation") is not None:
                org_data = user_data["organisation"].__dict__
                if user_data["organisation"].parent:
                    org_parent_data = user_data["organisation"].parent.__dict__
            campaign_monitor_data.append(
                (user_data, org_data, user_response_data, org_parent_data)
            )
            completed_count += 1

    cm_response, error = add_multiple_subscribers_from_data(campaign_monitor_data)
    if error is not None:
        errors.append(f"Error in sending data to campaign monitor: {error}")
        completed_count = 0

    user_csv_upload_instance.status = UserCSVUpload.DONE
    user_csv_upload_instance.errors = errors
    user_csv_upload_instance.csv_completed_count = completed_count
    user_csv_upload_instance.save()
    return cm_response


def update_or_create_user_agent(user, request):
    user_agent_model = apps.get_model("users", "UserAgent")
    if user.is_anonymous is True:
        return
    user_agent_instance = user.user_agent if hasattr(user, "user_agent") else None
    user_agent_dict = dict(
        user=user,
        is_touch_capable=request.user_agent.is_touch_capable,
        os=None,
        os_version=None,
        browser=None,
        browser_version=None,
        device=None,
        device_brand=None,
        device_model=None,
    )
    if request.user_agent.is_mobile is True:
        user_agent_dict["device_type"] = user_agent_model.MOBILE
    if request.user_agent.is_tablet is True:
        user_agent_dict["device_type"] = user_agent_model.TABLET
    if request.user_agent.is_pc is True:
        user_agent_dict["device_type"] = user_agent_model.PC
    if request.user_agent.is_bot is True:
        user_agent_dict["device_type"] = user_agent_model.BOT
    if request.user_agent.browser is not None:
        user_agent_dict["browser"] = request.user_agent.browser.family
        user_agent_dict["browser_version"] = request.user_agent.browser.version_string
    if request.user_agent.os is not None:
        user_agent_dict["os"] = request.user_agent.os.family
        user_agent_dict["os_version"] = request.user_agent.os.version_string
    if request.user_agent.device is not None:
        user_agent_dict["device"] = request.user_agent.device.family
        user_agent_dict["device_model"] = request.user_agent.device.model
        user_agent_dict["device_brand"] = request.user_agent.device.brand

    if user_agent_instance:
        for attr, value in user_agent_dict.items():
            setattr(user_agent_instance, attr, value)
        user_agent_instance.save()
    else:
        user_agent_instance = user_agent_model.objects.create(**user_agent_dict)

    return user_agent_instance


# This service is used on user profile update
# Don't use it on create user
def sync_user_data_with_cognito_and_mdlive(
    new_user_data, user_id, raise_mdlive_exception=True
):
    user_model = get_user_model()
    user_obj = user_model.objects.filter(id=user_id).first()
    cognito_data = get_cognito_data_from_user_data(new_user_data)
    cognito_services.admin_update_profile(user_obj=user_obj, data=cognito_data)
    # This will update the profile on mdlive
    try:
        # We don't want to send updates to MDLive if the user is inactive, because,
        # updating an inactive user on MDLive marks that user active in their system.
        if user_obj.is_active or new_user_data.get("is_active", None):
            mdlive_services.get_mdlive_token_data_for_user(
                user=user_obj, data_to_update=new_user_data
            )
    except ValidationError as e:
        if raise_mdlive_exception:
            # revert cognito updates as mdlive sync failed
            cognito_data = get_cognito_data_from_user_data(model_to_dict(user_obj))
            cognito_services.admin_update_profile(user_obj=user_obj, data=cognito_data)
            raise e


def send_welcome_email_to_user(user, password):
    ctx = {
        "user": user,
        "organisation": user.organisation,
        "first_name": user.first_name,
        "password": password,
        "site": get_current(),
        "frontend_site": get_site_by_id("frontend"),
    }

    send_mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        template_name="email/welcome_mail.tpl",
        context=ctx,
    )


def search_user_by_connects_member_id(connects_member_id):
    if connects_member_id:
        return get_user_model().objects.filter(
            is_active=True,
            connects_mbr_id=connects_member_id,
        )
    return get_user_model().objects.none()


def search_user_by_mdlive_id(mdlive_id):
    if mdlive_id:
        return get_user_model().objects.filter(is_active=True, mdlive_id=mdlive_id)
    return get_user_model().objects.none()


def search_user_by_demographic_data(first_name, last_name, gender, birthdate):
    return get_user_model().objects.filter(
        is_active=True,
        first_name__iexact=first_name,
        last_name__iexact=last_name,
        gender=gender,
        birthdate=birthdate,
    )


def search_user_by_contact_data(email, address1, address2, city, state, zip, phone):
    return get_user_model().objects.filter(
        is_active=True,
        email=email,
        address1__iexact=address1,
        address2__iexact=address2,
        city__iexact=city,
        state=state,
        zip=zip,
        phone=phone,
    )
