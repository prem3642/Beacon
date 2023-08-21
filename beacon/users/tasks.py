# -*- coding: utf-8 -*-
# Standard Library
import logging
from smtplib import SMTPException

# Third Party Stuff
from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import BadHeaderError
from django.forms.models import model_to_dict
from django_sites import get_by_id as get_site_by_id
from django_sites import get_current
from mail_templated import send_mail
from requests.exceptions import RequestException
from rest_framework.exceptions import ValidationError

# beacon Stuff
from beacon.base.models import UserCSVUpload
from beacon.cognito import tasks as cognito_tasks
from beacon.users.choices import USER_DEACTIVATION_CHOICES

from .utils import (
    get_relationship_from_user,
    send_appointment_email_to_user,
    send_f2f_data_to_bwb_server,
)

log = logging.getLogger(__name__)


def send_error_email(
    exc,
    user_appointment_id=None,
    organisation_username=None,
    user_appointment_ids=None,
    user_id=None,
    inquiry_id=None,
    template_name="email/bwb_server_error_email.tpl",
):
    ctx = {
        "organisation_username": organisation_username,
        "appointment_id": user_appointment_id,
        "appointment_ids": user_appointment_ids,
        "site": get_current(),
        "user_id": user_id,
        "inquiry_id": inquiry_id,
        "exception": str(exc),
    }
    return send_mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=settings.BWB_SERVER_ADMINS,
        template_name=template_name,
        context=ctx,
    )


@shared_task(bind=True, default_retry_delay=60, max_retries=5)
def send_f2f_data_task(self, user_appointment_id, bwb_data):
    """
    :param self: Self referencing object
    :param user_appointment_id: id of user f2f appointment
    :param bwb_data: dict of user data
    :return: response from bwb server
    """

    def handle_exception(exc, appointment_id, organisation_username):
        if self.request.retries >= self.max_retries:
            send_error_email(
                exc,
                user_appointment_id=appointment_id,
                organisation_username=organisation_username,
            )
            return False
        raise self.retry(exc=exc)

    try:
        response = send_f2f_data_to_bwb_server(user_appointment_id, bwb_data)
    except RequestException as e:
        return handle_exception(
            e, user_appointment_id, bwb_data.get("organisation_username")
        )
    except ValidationError as e:
        return handle_exception(
            e, user_appointment_id, bwb_data.get("organisation_username")
        )
    return response


@shared_task(bind=True, default_retry_delay=60, max_retries=5)
def send_multiple_f2f_appointments_data_task(self, appointment_ids):
    """
    :param self: Self referencing object
    :param appointment_ids: ids of appointments
    :return: response from bwb server
    """
    # Importing locally to avoid circular imports
    from beacon.users.services import get_bwb_data

    def handle_exception(exc, user_appointment_ids):
        if self.request.retries >= self.max_retries:
            send_error_email(exc, user_appointment_ids=user_appointment_ids)
            return False
        raise self.retry(exc=exc)

    user_appointment_model = apps.get_model("answers", "UserAppointment")
    appointments = user_appointment_model.objects.select_related(
        "user_response__user"
    ).filter(id__in=appointment_ids)

    failed_appointments_ids = list()
    for appointment in appointments:
        if appointment is None:
            continue
        if appointment.appointment_method == user_appointment_model.FACE_TO_FACE:
            user = appointment.user_response.user
            if user:
                user_appointment_id = str(appointment.id)
                relationship = get_relationship_from_user(user)
                bwb_data = get_bwb_data(
                    user.__dict__,
                    str(user.id),
                    str(user.mdlive_id),
                    relationship,
                    appointment.user_response,
                    appointment,
                    user.organisation,
                )

                try:
                    send_f2f_data_to_bwb_server(user_appointment_id, bwb_data)
                except RequestException:
                    failed_appointments_ids.append(user_appointment_id)
                except ValidationError:
                    failed_appointments_ids.append(user_appointment_id)
    if failed_appointments_ids:
        handle_exception(None, failed_appointments_ids)
    return True


@shared_task(bind=True, default_retry_delay=60, max_retries=5)
def send_appointment_email_to_user_task(
    self, user_appointment_id, user_id, bwb_response, first_name
):
    """
    :param self: Self referencing object
    :param user_id: id of user
    :param user_appointment_id: id of user f2f appointment
    :param bwb_response: response received from beacon server on sending the data
    :param first_name: First name of the user
    :return: status of the email
    """

    def handle_exception(exc, appointment_id, user_object_id, inquiry_id):
        if self.request.retries >= self.max_retries:
            send_error_email(
                exc,
                user_appointment_id=appointment_id,
                user_id=user_object_id,
                inquiry_id=inquiry_id,
            )
            return False
        raise self.retry(exc=exc)

    try:
        status = send_appointment_email_to_user(user_id, bwb_response, first_name)
    except SMTPException as e:
        return handle_exception(e, user_appointment_id, user_id, bwb_response)
    except BadHeaderError as e:
        return handle_exception(e, user_appointment_id, user_id, bwb_response)
    return status


# Not in use right now
@shared_task(bind=True)
def create_users_from_csv(self):
    # Importing internally to avoid circular import
    from . import services

    # get_solo will create the item if it does not already exist
    user_csv_upload_instance = UserCSVUpload.get_solo()
    # Update the instance to track the progress
    user_csv_upload_instance.csv_total_count = 0
    user_csv_upload_instance.csv_completed_count = 0
    user_csv_upload_instance.errors = None
    user_csv_upload_instance.status = UserCSVUpload.IN_PROGRESS
    user_csv_upload_instance.save()
    services.create_users_from_csv()


@shared_task(bind=True)
def send_users_to_campaign_monitor_from_csv(self):
    # Importing internally to avoid circular import
    from . import services

    services.send_users_to_campaign_monitor_from_csv()


@shared_task(bind=True)
def sync_user_mdlive_messages(self, user_id, send_new_message_email=False):
    # Importing internally to avoid circular import
    from beacon.mdlive import services
    from beacon.mdlive.models import Contact

    user_model = get_user_model()
    user = user_model.objects.filter(id=user_id).first()
    services.sync_user_contacts(user)
    contacts = Contact.objects.select_related("provider").filter(user=user)
    for contact in contacts:
        services.sync_user_messages(user, contact.provider.mdlive_id)
    if send_new_message_email is True:
        services.send_new_message_email_to_user(user)


@shared_task(bind=True)
def sync_users_active_status_with_organisation_task(self, org_id, is_active):
    """
    Task to sync user's active status with organisation's active status. If organisation is set inactive, then
    deactivate all its users and save deactivation reason as "Client terminated". Later on, if the organisation is set
    active, then re-activate all these users and clear their deactivation reason.

    :param org_id: UUID of the organisation object
    :param is_active: latest active status of the organisation
    """
    # Importing internally to avoid circular import
    from .services import get_cognito_data_from_user_data

    if not is_active:
        # Deactivate all the active users of the organisation
        users_qs = get_user_model().objects.filter(organisation=org_id, is_active=True)
        new_deactivation_reason = USER_DEACTIVATION_CHOICES.CLIENT_TERMINATED
    else:
        # Activate all users deactivated due to "Client terminated"
        users_qs = get_user_model().objects.filter(
            organisation=org_id,
            is_active=False,
            deactivation_reason=USER_DEACTIVATION_CHOICES.CLIENT_TERMINATED,
        )
        new_deactivation_reason = None

    for user in users_qs:
        cognito_data = get_cognito_data_from_user_data(model_to_dict(user))
        # Cognito does not accept boolean, so changing into string.
        cognito_data["is_active"] = str(is_active)
        cognito_tasks.update_user_on_cognito_task.delay(
            user_id=user.id, cognito_data=cognito_data
        )
    users_qs.update(is_active=is_active, deactivation_reason=new_deactivation_reason)


@shared_task(bind=True)
def generate_password_and_send_welcome_email(self, user_id):
    # Importing internally to avoid circular import
    from beacon.users import services

    user_model = get_user_model()
    user = user_model.objects.filter(id=user_id).first()

    password = services.get_default_user_password(
        user.first_name, user.last_name, user.birthdate
    )
    ctx = {
        "user": user,
        "organisation": user.organisation,
        "first_name": user.first_name,
        "password": password,
        "site": get_current(),
        "frontend_site": get_site_by_id("frontend"),
    }
    user.set_password(password)
    user.save()
    send_mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        template_name="email/welcome_mail.tpl",
        context=ctx,
    )
