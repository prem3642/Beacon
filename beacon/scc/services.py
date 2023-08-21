# -*- coding: utf-8 -*-
# Standard Library
import datetime

# Third Party Stuff
import phonenumbers
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.utils import timezone
from phonenumbers import NumberParseException
from rest_framework.exceptions import PermissionDenied, ValidationError

from beacon.answers.models import UserAppointment

# beacon Stuff
from beacon.answers.serializers import AnswerSccSyncSerializer
from beacon.answers.services import get_question_answer_json, save_answer_serializer
from beacon.base.exceptions import SccIntegrityError
from beacon.base.utils.helpers import (
    get_diff_of_changes,
    model_to_json_serializable_dict,
)
from beacon.organisations.services import search_organisation
from beacon.questionnaire.choices import QUESTION_KEYS
from beacon.users.models import UserManager
from beacon.users.serializers import (
    SCCForceUpdateUserSerializer,
    SCCPersonalInfoUserSerializer,
    UserSerializer,
)
from beacon.users.services import (
    get_default_user_password,
    search_user_by_connects_member_id,
    search_user_by_contact_data,
    search_user_by_demographic_data,
    search_user_by_mdlive_id,
    send_welcome_email_to_user,
    sync_user_data_with_cognito_and_mdlive,
)
from beacon.users.views import create_user_account

from . import choices, constants
from .models import SccApiLog
from .scc_api import SccApiClient
from .tasks import send_user_data_to_scc_task
from .tokens import generate_outgoing_scc_auth_token


# Conversion methods to translate SCC data to BWB format
def _parse_ibm_date_format(date):
    century_type = date[0]
    year = date[1:3]
    if century_type == "1":
        year = "19" + year
    else:
        year = "20" + year

    month = date[3:5]
    day = date[5:]
    return year, month, day


def get_bwb_birthdate_value(scc_date_of_birth):
    """Converts CYYMMDD to YYYY-MM-DD format"""
    if scc_date_of_birth is None:
        return None
    validate_ibm_date_format(scc_date_of_birth)
    year, month, day = _parse_ibm_date_format(scc_date_of_birth)
    date = f"{year}-{month}-{day}"
    validate_iso_8601_date_format(date)
    return date


def validate_ibm_date_format(date):
    if len(date) > 7 or date[0] not in ("1", "2") or not date.isdigit():
        raise ValidationError("Invalid IBM date format (CYYMMDD).")


def validate_iso_8601_date_format(date):
    date_format = "%Y-%m-%d"
    try:
        datetime.datetime.strptime(date, date_format)
    except ValueError as exc:
        raise ValidationError(f"Invalid ISO 8601 date format. {exc}")


def get_bwb_phone_value(
    scc_phone_area_code, scc_phone_central_office_code, scc_phone_exchange_code
):
    if scc_phone_area_code or scc_phone_central_office_code or scc_phone_exchange_code:
        phone_number = f"+1{scc_phone_area_code}{scc_phone_central_office_code}{scc_phone_exchange_code}"
        try:
            if not phonenumbers.is_valid_number_for_region(
                phonenumbers.parse(phone_number), "US"
            ):
                raise ValidationError("Invalid phone number!")
        except NumberParseException as exc:
            raise ValidationError(f"Invalid phone number. {exc}")

        return phone_number


def convert_scc_data_into_bwb_format(scc_data):
    bwb_data = {}

    for scc_key, mapping in constants.SCC_KEYS_MAPPING.items():
        if scc_key in scc_data.keys():
            value = scc_data.get(scc_key)
            # Convert SCC "value" in BWB format only if a mapping exists for it, as not every SCC value needs mapping.
            # However, SCC "keys" always need to be converted into BWB format as they all are different.
            if mapping:
                value = mapping.get(value)
            key = constants.SCC_TO_BWB_KEYS.get(scc_key)
            bwb_data.update({key: value})

    if is_phone_field_present(scc_data):
        phone_number = get_bwb_phone_value(
            scc_phone_area_code=scc_data.get("phoneNumberAreaCode"),
            scc_phone_central_office_code=scc_data.get("phoneNumberCentralOfficeCode"),
            scc_phone_exchange_code=scc_data.get("phoneNumberExchange"),
        )
        bwb_data.update({"phone": phone_number})

    if "dateOfBirth" in scc_data.keys():
        birthdate = get_bwb_birthdate_value(scc_data.get("dateOfBirth"))
        bwb_data.update({"birthdate": birthdate})

    if "email" in scc_data.keys():
        bwb_data.update({"email": UserManager.normalize_email(scc_data.get("email"))})

    return bwb_data


def is_phone_field_present(scc_data):
    return any(
        x in scc_data.keys()
        for x in [
            "phoneNumberAreaCode",
            "phoneNumberCentralOfficeCode",
            "phoneNumberExchange",
        ]
    )


# Conversion methods to translate BWB data to SCC format
def get_scc_date_of_birthdate_value(bwb_birthdate):
    """Converts YYYY-MM-DD format to CYYMMDD"""
    validate_iso_8601_date_format(bwb_birthdate)
    year, month, day = tuple(bwb_birthdate.split("-"))

    century = int(year[:2])
    if century == 20:
        century_type = 1
    elif century == 19:
        century_type = 0
    else:
        raise ValidationError("Invalid date of birth!")

    ibm_date = f"{century_type}{year[2:]}{month}{day}"
    validate_ibm_date_format(ibm_date)
    return ibm_date


def get_scc_phone_area_code(bwb_phone_number):
    if bwb_phone_number:
        return bwb_phone_number[2:5]


def get_scc_phone_central_office_code(bwb_phone_number):
    if bwb_phone_number:
        return bwb_phone_number[5:8]


def get_scc_phone_exchange_code(bwb_phone_number):
    if bwb_phone_number:
        return bwb_phone_number[8:]


def process_user_sync_request(data):
    users_qs = (
        search_user_by_connects_member_id(data.get("connects_mbr_id"))
        | search_user_by_mdlive_id(data.get("mdlive_id"))
        | search_user_by_demographic_data(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            gender=data.get("gender"),
            birthdate=data.get("birthdate"),
        )
        | search_user_by_contact_data(
            email=data.get("email"),
            address1=data.get("address1"),
            address2=data.get("address2"),
            city=data.get("city"),
            state=data.get("state"),
            zip=data.get("zip"),
            phone=data.get("phone"),
        )
    )

    # case 1: if user not found
    if users_qs.count() == 0:
        new_user = register_and_return_new_user(data)
        return new_user.id, None

    # case 2: if single user found
    elif users_qs.count() == 1:
        user_obj = users_qs.first()
        error_msg = get_single_user_discrepancies(user_obj, data)
        if error_msg:
            raise SccIntegrityError(error_msg)
        else:
            user_serializer = SCCPersonalInfoUserSerializer(
                instance=user_obj, data=data
            )
            change_diff = sync_user_and_get_changes(
                user_obj=user_obj,
                user_serializer=user_serializer,
                bwb_data=data,
            )
            return user_obj.id, change_diff

    # case 3: if multiple users found
    else:
        error_msg = get_multiple_users_discrepancies(users_qs, data)
        raise SccIntegrityError(error_msg)


def get_single_user_discrepancies(user, data):
    discrepancies = get_discrepancies(user, data)
    if discrepancies:
        return [discrepancies]


def get_multiple_users_discrepancies(users_qs, request):
    multiple_user_discrepancies = []
    for user in users_qs:
        discrepancies = get_discrepancies(user, request)
        if discrepancies:
            multiple_user_discrepancies.append(discrepancies)

    return multiple_user_discrepancies


# discrepancies are checked for connects member id, demographics and contact data.
def get_discrepancies(user, data):
    field_differences = {}
    is_discrepancy_found = False

    for field in constants.FIND_DISCREPANCY_FOR_FIELDS:
        scc_value, bwb_value = data.get(field), getattr(user, field, None)
        if field in constants.FIND_CASE_INSENSITIVE_DISCREPANCY_FOR_FIELDS:
            # These fields should always have
            # case-insensitive matching
            # The search queryset already uses iexact
            # but discrepancy set-up would also
            # require manual checking for fields.
            if scc_value and bwb_value:
                # if any of the value in both systems is not null
                # then compare the lower representations.
                if scc_value.lower() != bwb_value.lower():
                    is_discrepancy_found = True
            else:
                # Case when either of the value can be null.
                if scc_value != bwb_value:
                    is_discrepancy_found = True
        else:
            if scc_value != bwb_value:
                is_discrepancy_found = True

        field_differences.update(
            format_discrepancy(
                field_name=constants.BWB_TO_SCC_KEYS.get(field),
                bwb_value=bwb_value,
                scc_value=scc_value,
            )
        )

    # special cases birthdate and phone
    scc_birthdate, bwb_birthdate = data.get("birthdate"), str(user.birthdate)
    scc_phone, bwb_phone = data.get("phone"), user.phone

    if scc_birthdate != bwb_birthdate:
        is_discrepancy_found = True
    field_differences.update(
        format_discrepancy(
            field_name=constants.BWB_TO_SCC_KEYS.get("birthdate"),
            bwb_value=bwb_birthdate,
            scc_value=scc_birthdate,
        )
    )

    scc_phone_keys_and_get_value_methods = {
        "phoneNumberAreaCode": get_scc_phone_area_code,
        "phoneNumberCentralOfficeCode": get_scc_phone_central_office_code,
        "phoneNumberExchange": get_scc_phone_exchange_code,
    }

    for scc_field, get_value in scc_phone_keys_and_get_value_methods.items():
        scc_value, bwb_value = get_value(scc_phone), get_value(bwb_phone)
        if scc_value != bwb_value:
            is_discrepancy_found = True
        field_differences.update(
            format_discrepancy(
                field_name=scc_field,
                bwb_value=bwb_value,
                scc_value=scc_value,
            )
        )

    if is_discrepancy_found:
        field_differences.update({"bwb_user_id": str(user.id)})
        return field_differences


def format_discrepancy(field_name, bwb_value, scc_value):
    """
    Method to format discrepancy error message to return in the response to SCC.

    :param field_name: Name of field in the SCC format for which discrepancy error
                       message to prepare.
    :param bwb_value: Value for that field in BWB system
    :param scc_value: Value for that field in SCC system (received in the request body
                      of /api/users/sync API)
    """

    def to_uppercase_if_string(value):
        """
        Method to return uppercase string if the given `value` param is a valid String.
        Otherwise, returns the value as it as.
        """
        if value and isinstance(value, str):
            return value.upper()
        return value

    if field_name in constants.RETURN_DISCREPANCY_IN_UPPERCASE_FOR_SCC_FIELDS:
        bwb_value = to_uppercase_if_string(bwb_value)
        scc_value = to_uppercase_if_string(scc_value)

    return {field_name: {"bwb_value": bwb_value, "scc_value": scc_value}}


def register_and_return_new_user(data):
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    iso_8601_date_format = "%Y-%m-%d"
    birth_date_time = timezone.datetime.strptime(
        data.get("birthdate"), iso_8601_date_format
    )
    birth_date = datetime.date(
        birth_date_time.year, birth_date_time.month, birth_date_time.day
    )
    data["birthdate"] = birth_date
    password = get_default_user_password(first_name, last_name, birth_date)
    data.update({"password": password})

    data.update({"agrees_to_beacon_privacy_notice": True})
    data.update({"agrees_to_mdlive_informed_consent": True})
    data.update({"agrees_to_mdlive_privacy_agreement": True})
    data.update(
        {
            "mdlive_consent_user_initials": "{}{}".format(
                first_name[0], last_name[0]
            ).upper()
        }
    )

    organisation = search_organisation(
        parent_code=data.get("parent_code"),
        group_number=data.get("group_number"),
        benefit_package=data.get("benefit_package"),
        raise_exception=True,
    )
    data.update({"organisation": organisation})

    answer_data = get_answers_data(bwb_data=data)
    answer_serializer = get_answer_serializer(answer_data=answer_data)
    answer_serializer.is_valid(raise_exception=True)
    user_serializer = UserSerializer(data=data)
    user_serializer.is_valid(raise_exception=True)

    try:
        # Create user on Cognito, MDLive and BWB system
        user, mdlive_user_token_data, _ = create_user_account(
            data,
            request=None,
            admin_force_registration=False,
            source=get_user_model().SCC,
        )
    except ValidationError as exc:
        exc_msg = ". ".join(exc.detail) if isinstance(exc.detail, list) else exc.detail
        raise ValidationError(f"Error while registering a new user from SCC. {exc_msg}")

    save_answer_serializer(
        answer_serializer=answer_serializer, user_obj=user, answer_data=answer_data
    )
    # Send email to user regarding the new account and password
    send_welcome_email_to_user(user=user, password=data.get("password"))

    return user


# Not in use, originally was getting used in `scc.services.force_save_user_data` method
# But now, if these fields are received in request body, these are simply ignored at
# the serialization layer.
def _check_updates_for_demographic_data(data, raise_exception=True):
    fields = ["first_name", "last_name", "birthdate", "gender"]
    if any(x in data.keys() for x in fields):
        # These fields shouldn't be allowed for force update
        if raise_exception:
            raise PermissionDenied("You don't have permission for this action.")


def force_save_user_data(instance, bwb_data):
    if not bwb_data.get("email"):
        bwb_data.update({"email": instance.email})

    # SCC is currently sending "null" for MDLive ID to update in BWB using force-sync
    # API. This is creating problems because upon syncing users from connects
    # systems, their MDLive ID is getting deleted in BWB. Therefore, considering the
    # time it will take for SCC to release their next build to fix this,
    # we are adding the following temp fix, that is to ignore updates for MDLive ID
    # if "null" is received from SCC.
    if bwb_data.get("mdlive_id") is None:
        bwb_data.pop("mdlive_id", None)

    user_serializer = SCCForceUpdateUserSerializer(instance, data=bwb_data)
    change_diff = sync_user_and_get_changes(
        user_obj=instance,
        user_serializer=user_serializer,
        bwb_data=bwb_data,
    )
    return change_diff


def send_scc_updates_to_mdlive_and_cognito(new_user_data, existing_user):
    """Send SCC user updates on MDLive and Cognito."""
    new_user_data = add_missing_user_data(
        new_user_data=new_user_data,
        existing_user=existing_user,
    )
    sync_user_data_with_cognito_and_mdlive(
        new_user_data=new_user_data,
        user_id=str(existing_user.id),
    )


def add_missing_user_data(new_user_data, existing_user):
    """
    SCC can update partial data to BWB using API /users/:id/force-sync. But we need to send a legit request to update
    users on mdlive and cognito, both of which has different request bodies. To avoid any cause of failure while
    updating a user on mdlive and cognito, we are filling in the missing data using the existing user object.
    """
    complete_user_data = model_to_dict(existing_user)
    for k, v in new_user_data.items():
        complete_user_data[k] = v
    return complete_user_data


def get_answer_serializer(answer_data, user=None):
    data = answer_data.copy()
    if user and hasattr(user, "answer"):
        question_answer_json = get_question_answer_json(
            answer_data=answer_data, user_response=user.answer
        )
        data.update({"response": question_answer_json})
        return AnswerSccSyncSerializer(user.answer, data=data)
    else:
        question_answer_json = get_question_answer_json(answer_data=answer_data)
        data.update({"response": question_answer_json})
        return AnswerSccSyncSerializer(data=data)


def get_answers_data(bwb_data):
    answers = {}
    for question_key in QUESTION_KEYS:
        if question_key in bwb_data.keys():
            answer = bwb_data.get(question_key)
            answers.update({question_key: answer})
    # Pass in the user.state as answer.appointment state
    answers.update({"appointment_state": bwb_data.get("state")})
    return answers


def get_scc_api_client():
    auth_token = generate_outgoing_scc_auth_token()
    return SccApiClient(auth_token)


def generate_scc_user_registration_request(user):
    """
    Prepares and returns dictionary of data to be send to SCC for a new user non-f2f self-registration. All data keys
    and values are formatted as per SCC system, except data of birth that is to be send in BWB format.
    :param user: User object whose data is to be returned in SCC format.
    """
    user_response = user.answer
    user_organisation = user.organisation
    phone_number = user.phone
    phone_area_code = get_scc_phone_area_code(phone_number)
    phone_central_office_code = get_scc_phone_central_office_code(phone_number)
    phone_exchange = get_scc_phone_exchange_code(phone_number)
    return {
        "mdLiveMemberID": user.mdlive_id,
        "emailAddress": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "providerId": "959422",
        "vendorId": "E970051",
        "dateOfBirth": str(user.birthdate) if user.birthdate else None,
        "gender": constants.GENDER_MAPPING_BWB_TO_SCC.get(user.gender),
        "addressLine1": user.address1,
        "addressLine2": user.address2,
        "addressCity": user.city,
        "addressStateCode": user.state,
        "addressZipCode": user.zip,
        "phoneNumberAreaCode": phone_area_code,
        "phoneNumberCentralOfficeCode": phone_central_office_code,
        "phoneNumberExchange": phone_exchange,
        "dateRegistered": user.date_joined.date().strftime("%Y-%m-%d"),
        "timeRegistered": user.date_joined.time().strftime("%H:%M:%S"),
        "parentCode": user_organisation.parent_code,
        "groupNumber": user_organisation.group_number,
        "benefitPackage": user_organisation.benefit_package,
        "requestedUnits": user_organisation.number_of_sessions,
        "relationshipStatus": constants.RELATIONSHIP_STATUS_VALUE_MAPPING_BWB_TO_SCC.get(
            user.relationship_status, None
        ),
        "employmentStatus": constants.EMPLOYMENT_STATUS_VALUE_MAPPING_BWB_TO_SCC.get(
            user.employment_status, None
        ),
        "jobTitle": constants.JOB_TITLE_VALUE_MAPPING_BWB_TO_SCC.get(
            user.job_title, None
        ),
        "primaryPresentingProblem": constants.CHIEF_COMPLAINT1_ANSWER_MAPPING_BWB_TO_SCC.get(
            user_response.chief_complaint1, None
        ),
        "secondaryPresentingProblem": constants.CHIEF_COMPLAINT2_ANSWER_MAPPING_BWB_TO_SCC.get(
            user_response.chief_complaint2, None
        ),
        "depressionScreenerQuestion3A": constants.QUESTION_3A_ANSWER_MAPPING_BWB_TO_SCC.get(
            user_response.how_often_less_interest_in_things, None
        ),
        "depressionScreenerQuestion3B": constants.QUESTION_3B_ANSWER_MAPPING_BWB_TO_SCC.get(
            user_response.how_often_depressed, None
        ),
        "anxietyScreenerQuestion5A": constants.QUESTION_5A_ANSWER_MAPPING_BWB_TO_SCC.get(
            user_response.how_often_nervous, None
        ),
        "anxietyScreenerQuestion5B": constants.QUESTION_5B_ANSWER_MAPPING_BWB_TO_SCC.get(
            user_response.how_often_worry, None
        ),
        "substanceUseQuestion7A": constants.QUESTION_7A_ANSWER_MAPPING_BWB_TO_SCC.get(
            user_response.difficulty_in_keeping_drinking_limit, None
        ),
        "substanceUseQuestion7B": constants.QUESTION_7B_ANSWER_MAPPING_BWB_TO_SCC.get(
            user_response.felt_cut_down_drinking, None
        ),
        "wellbeingDomainQuestion8": user_response.how_emotionally_doing,
        "wellbeingDomainQuestion9": user_response.how_physical_health,
        "wellbeingDomainQuestion10": user_response.people_support,
        "wellbeingDomainQuestion11": user_response.comfortable_in_managing_finances,
        "wellbeingDomainQuestion12": user_response.resources_to_manage,
        "outcomesESDQuestion1": constants.QUESTION_OUTCOME_ESD_1_NON_DIGIT_VALUES_BWB_TO_SCC.get(
            user_response.number_of_days_missed_work, None
        ),
        "outcomesESDQuestion2": constants.QUESTION_OUTCOME_ESD_1_NON_DIGIT_VALUES_BWB_TO_SCC.get(
            user_response.number_of_days_less_productive, None
        ),
    }


def create_scc_api_log(
    user_id, request, response, is_successful, is_incoming, change_diff=None
):
    """
    Method to create SCC API Log objects.

    :param user_id: User's UUID to associate with the log
    :param request: Dictionary of Request body
    :param response: Dictionary of Response body
    :param is_successful: Designates if the log status should be successful or not
    :param is_incoming: Designates if the log is created for incoming or outgoing API requests
    :param change_diff: JSON Serializable object to store changes made (if any) on User/UserResponse objects.
    :return: Newly created SccApiLog object
    """
    if is_incoming:
        direction = choices.REQUEST_DIRECTION_CHOICES.INCOMING
    else:
        direction = choices.REQUEST_DIRECTION_CHOICES.OUTGOING

    if is_successful:
        status = choices.STATUS_CHOICES.SUCCESSFUL
    else:
        status = choices.STATUS_CHOICES.FAILED

    return SccApiLog.objects.create(
        user_id=user_id,
        request=request,
        response=response,
        status=status,
        request_direction=direction,
        change_diff=change_diff,
    )


def send_user_data_to_scc_if_non_f2f(user, appointment_method):
    """
    Send initial registrations/requests to the SCC. The requests will be sent after the member has answered the
    assessment questions, completed the registration, scheduled or requested an appointment in MDLive, and
    does not opt-in for F2F appointment method.
    :param user: User object whose data is to be send
    :param appointment_method: Method of appointment the user scheduled
    """
    if user.send_to_scc_if_non_f2f:
        if appointment_method != UserAppointment.FACE_TO_FACE:
            prepare_scc_data_and_send_user_to_scc(user=user)

        user.send_to_scc_if_non_f2f = False
        user.save()


def prepare_scc_data_and_send_user_to_scc(user):
    request_data = generate_scc_user_registration_request(user=user)
    send_user_data_to_scc_task.delay(
        user_id=str(user.id),
        request=request_data,
    )


def sync_user_and_get_changes(user_obj, user_serializer, bwb_data):
    """
    Common service between Users-Sync and Users-Force-sync SCC APIs to update a user,
    its answers, sync them with MDLive and Cognito, and return the diff of changes.

    :param user_obj: The `User` instance to update and sync
    :param user_serializer: user serializer different for sync and force-sync APIs.
    :param bwb_data: API Request data from SCC converted into BWB format
    :return: Diff of changes on user and user's answers
    """
    user_serializer.is_valid(raise_exception=True)

    answer_data = get_answers_data(bwb_data=bwb_data)
    answer_serializer = get_answer_serializer(answer_data=answer_data, user=user_obj)
    answer_serializer.is_valid(raise_exception=True)

    send_scc_updates_to_mdlive_and_cognito(
        new_user_data=user_serializer.validated_data,
        existing_user=user_obj,
    )

    old_user_data = model_to_json_serializable_dict(user_obj)
    user_serializer.save()
    updated_user = get_user_model().objects.get(id=user_obj.id)
    updated_user_data = model_to_json_serializable_dict(updated_user)
    user_diff = get_diff_of_changes(
        dict_one=old_user_data,
        dict_two=updated_user_data,
    )

    try:
        old_user_response = user_obj.answer
    except ObjectDoesNotExist:
        old_user_response = None

    old_user_response_data = model_to_json_serializable_dict(
        old_user_response, exclude=("response", "response_backup")
    )
    save_answer_serializer(answer_serializer, user_obj, answer_data)
    user_obj.refresh_from_db()
    updated_user_response = user_obj.answer if hasattr(user_obj, "answer") else None
    updated_user_response_data = model_to_json_serializable_dict(
        updated_user_response, exclude=("response", "response_backup")
    )
    user_response_diff = get_diff_of_changes(
        old_user_response_data,
        updated_user_response_data,
    )

    return user_diff + user_response_diff
