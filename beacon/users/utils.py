# -*- coding: utf-8 -*-
# Standard Library
import json
import re
from uuid import UUID

# Third Party Stuff
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_sites import get_current
from mail_templated import send_mail
from requests import post as requests_post
from rest_framework.exceptions import ValidationError

# beacon Stuff
from beacon.answers.models import UserAppointment


def get_auth_token_from_request(request, auth_rx=None):
    if auth_rx is None:
        auth_rx = re.compile(r"^Token (.+)$")

    if "HTTP_AUTHORIZATION" not in request.META:
        return None

    token_rx_match = auth_rx.search(request.META["HTTP_AUTHORIZATION"])
    if not token_rx_match:
        return None

    return token_rx_match.group(1)


def encode_uuid_to_base64(uuid_) -> str:
    """Returns a  urlsafe based64 encoded representation of a UUID object or UUID like string."""
    return urlsafe_base64_encode(force_bytes(uuid_))


def decode_uuid_from_base64(uuid_value: str):
    """Given a base64 encoded string, try to decode it to a valid UUID object.

    Returns a valid UUID value or None
    """
    try:
        return UUID(force_str(urlsafe_base64_decode(uuid_value)))
    except (ValueError, OverflowError, TypeError):
        return None


def send_f2f_data_to_bwb_server(user_appointment_id, bwb_data):
    """
    :param user_appointment_id: id of user f2f appointment
    :param bwb_data: dict of user data
    e.g.:
    {
        'first_name': 'Dwight',
        'last_name': 'Price',
        'gender': 'M',
        'birthdate': '1990-08-08',
        'cognito_id': '99586d04-1a1d-473a-aaf4-3347ea3b3857',
        'mdlive_id': '79586d04-1a1d-473a-aaf4-3347ea3b3857',
        'email': 'dwight@gmail.com',
        'phone': '+18888888888',
        'address': {'address1': '123 Test Road', 'address2': null, 'city': 'Sunrise',
                    'state': 'FL', 'zip': '33325'},
        'employment_status': 'Full Time',
        'relationship_status': 'Never Married',
        'job_title': 'Technical',
        'emotional_support_for': 'Self',
        'chief_complaint1': 'Grief or Loss',
        'chief_complaint2': 'Depression',
        'appointment_state': 'DC',
        'how_often_less_interest_in_things': '3',
        'how_often_depressed': '3',
        'how_often_nervous': '2',
        'how_often_worry': '2',
        'difficulty_in_keeping_drinking_limit': 1,
        'felt_cut_down_drinking': 0,
        'how_emotionally_doing': '2',
        'how_physical_health': '3',
        'comfortable_in_managing_finances': '3',
        'people_support': '2',
        'resources_to_manage': '4',
        'number_of_days_less_productive': '3',
        'number_of_days_missed_work': '4',
        'organisation_username': 'beaconeapwellness',
        'f2f_gender_preference': 'M',
        'f2f_comfortable_language': 'English',
        'f2f_preferred_contact': 'phone',
        'f2f_preferred_time': 'morning',
        'f2f_okay_to_leave_voicemail': 1,
        'f2f_counselor_search_address': 'home_address',
        'f2f_address': {'f2f_address1': null, 'f2f_address2': null, 'f2f_city': null,
                        'f2f_zip': null, 'f2f_state': null},
        'f2f_counselor_notes': 'Lorem Ipsum',
    }
    :return: response from bwb server
    """
    user_appointment = UserAppointment.objects.filter(id=user_appointment_id).first()
    if user_appointment.bwb_inquiry_id is None:
        url = "{}{}".format(
            settings.BWB_BASE_URL,
            settings.BWB_USER_REGISTER_DATA_SUBMIT_URL.format(
                service_id=settings.BWB_SERVICE_ID
            ),
        )
        headers = {"Content-Type": "application/json"}
        response = requests_post(url, data=json.dumps(bwb_data), headers=headers)
        if response.status_code == 200:
            return_data = response.content
            if type(return_data) == bytes:
                return_data = return_data.decode("utf-8")
            if user_appointment:
                user_appointment.bwb_inquiry_id = return_data
                user_appointment.save()
            return return_data
        raise ValidationError(
            f"Error in sending data to Beacon server: {response.content}"
        )
    return user_appointment.bwb_inquiry_id


def send_appointment_email_to_user(
    user_id, bwb_response, first_name, email_template="email/f2f_appointment_email.tpl"
):
    user = get_user_model().objects.filter(id=user_id).first()
    if user:
        ctx = {
            "user": user,
            "first_name": first_name,
            "organisation": user.organisation,
            "site": get_current(),
            "inquiry_id": bwb_response,
        }
        return send_mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            template_name=email_template,
            context=ctx,
        )
    return False


def get_relationship_from_user(user):
    answer = user.answer if hasattr(user, "answer") else None
    relationship = "Self"
    if answer and answer.emotional_support_for:
        relationship = answer.emotional_support_for
    return relationship


def get_changed_dict_keys(new_dict, old_dict):
    """
    Method to compare two dicts, and return list of keys whose value is changed in the new dict.
    """
    changed_keys = []
    for key, new_value in new_dict.items():
        old_value = old_dict.get(key)
        if isinstance(new_value, QuerySet) or isinstance(old_value, QuerySet):
            if set(new_value) != set(old_value):
                changed_keys.append(key)
        elif new_value != old_value:
            changed_keys.append(key)

    return changed_keys
