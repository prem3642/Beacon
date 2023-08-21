# -*- coding: utf-8 -*-
# Standard Library
import json
import logging
import re
from copy import deepcopy
from typing import Any, Dict, Optional, Union

# Third Party Stuff
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_sites import get_current
from mail_templated import send_mail
from pyzipcode import ZipCodeDatabase
from requests import delete as requests_delete
from requests import (
    get as requests_get,  # import get/post func to mock multiple requests in tests
)
from requests import patch as requests_patch
from requests import post as requests_post
from requests import put as requests_put
from rest_framework.exceptions import ValidationError
from timezonefinder import TimezoneFinder

# beacon Stuff
from beacon.base.models import SiteConfiguration
from beacon.users.choices import ALLOWED_TIMEZONES
from beacon.users.utils import get_relationship_from_user

from . import constants, models

log = logging.getLogger(__name__)


def get_timezone_from_zip(zip_code):
    zc = ZipCodeDatabase()
    try:
        zip_code_data = zc[zip_code]
    except KeyError:
        zip_code_data = None
    if zip_code_data:
        tf = TimezoneFinder()
        try:
            time_zone = tf.timezone_at(
                lng=zip_code_data.longitude, lat=zip_code_data.latitude
            )
        except ValueError:
            time_zone = None
        if time_zone in ALLOWED_TIMEZONES:
            return time_zone
    # By Default EST timezone will be returned.
    return "America/New_York"


def get_mdlive_data_from_cognito_data(
    cognito_data: dict,
    cognito_sub: str,
    birth_date_str: str,
    relationship: str,
    is_new_user: bool = False,
    time_zone: str = None,
    source: Optional[str] = None,
) -> dict:
    """
    Method to return data from cognito data to sync with MDLive.

    :param cognito_data: Data intended to sync with cognito
    :param cognito_sub: UUID of the user at cognito
    :param birth_date_str: Birthdate of user in string
    :param relationship: Relationship status
    :param is_new_user: Designate if the user is a new registration
    :param time_zone: Timezone to sync with MDLive (Optionally needed if the user is a new registration)
    :param source: Source of the user creation (API, ADMIN, SCC)
    :return: Data dictionary intended to sync with MDLive
    """
    birth_date = timezone.datetime.strptime(birth_date_str, "%Y-%m-%d")

    # MDLive only accepts  10 digit phone number
    # Removed country code before passing it to MDLive
    phone = cognito_data.get("phone")
    address2 = cognito_data.get("address2", "")
    address2 = "" if address2 is None else address2
    mdlive_data: Dict[str, Dict[Union[str, Any], Union[str, Any]]] = {
        "auth": {
            "first_name": cognito_data.get("first_name"),
            "last_name": cognito_data.get("last_name"),
            "gender": cognito_data.get("gender"),
            "birthdate": birth_date.strftime("%Y-%m-%d"),
            "member_id": cognito_sub,
            "subscriber_id": "",
            "email": cognito_data.get("email"),
            "phone": phone[-10:] if phone else phone,
            "address1": cognito_data.get("address1"),
            "address2": address2,
            "city": cognito_data.get("city"),
            "state": cognito_data.get("state"),
            "zip": cognito_data.get("zip"),
            "relationship": relationship,
        }
    }

    # send timezone only at time of registration
    if is_new_user:
        if source != get_user_model().API:
            # For source SCC / ADMIN
            time_zone = get_timezone_from_zip(cognito_data.get("zip"))
        mdlive_data["auth"]["us_time_zone_id"] = get_mdlive_us_time_zone_id(time_zone)

    return mdlive_data


def get_mdlive_headers(token=None):
    headers = {"Content-type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    return headers


def get_mdlive_auth_data():
    return dict(
        auth={"api_key": settings.MDLIVE_API_KEY, "password": settings.MDLIVE_PASSWORD}
    )


def get_mdlive_api_data():
    return dict(
        api={"api_key": settings.MDLIVE_API_KEY, "password": settings.MDLIVE_PASSWORD}
    )


def get_mdlive_organisation_data(organisation=None):
    data = dict(
        org={
            "ou": organisation.username
            if organisation
            else settings.MDLIVE_ORGANISATION_USERNAME
        }
    )
    if not organisation and settings.MDLIVE_ENTERPRISE_HASH:
        data["org"]["enterprise_hash"] = settings.MDLIVE_ENTERPRISE_HASH
    if organisation and organisation.enterprise_hash:
        data["org"]["enterprise_hash"] = organisation.enterprise_hash
    return data


def get_token_from_keys():
    url = "{}/auth/auth_token".format(settings.MDLIVE_URL)
    headers = get_mdlive_headers()
    data = get_mdlive_auth_data()
    response = requests_post(url, data=json.dumps(data), headers=headers)
    if response.status_code == 201:
        return json.loads(response.content).get("jwt")
    raise ValidationError(
        f"Error from mdlive: {response.status_code} {response.content}"
    )


def get_user_token(user_data, organisation=None):
    """
    :param user_data: user auth dict
    :param organisation: beacon.organisation.models.Organisation object
    e.g.:
    {'auth': {'first_name': 'beacon',
              'last_name': 'health',
              'gender': 'M',
              'birthdate': '1988-08-08',
              'subscriber_id': 'beacon1234',
              'phone': '8888888888',
              'email': 'mdlivedemo123@gmail.com',
              'address1': '123 Test Road',
              'city': 'Sunrise',
              'state': 'FL',
              'zip': '33325',
              'relationship': 'Self'}}
    :return: jwt token data
    """
    url = "{}/api/v1/sso_auth/auth_token".format(settings.MDLIVE_URL)
    headers = get_mdlive_headers()
    org_data = get_mdlive_organisation_data(organisation=organisation)
    api_data = get_mdlive_api_data()
    data = deepcopy(user_data)
    data.update(api_data)
    data.update(org_data)
    if data["auth"].get("member_id") is None:
        log.info(f"MDLive Member Id Data: {data}")

    # MDLive's `user-tokens` API supports only "M", "F", or "U" as valid values for gender.
    # See: https://developers.mdlivetechnology.com/#user-tokens
    valid_gender_choices = ("M", "F", "U")
    if data["auth"].get("gender") not in valid_gender_choices:
        data["auth"]["gender"] = "U"

    response = requests_post(url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    log.info(
        f"Error from MDLive User Token: {response.status_code} {response.content}\nData: {data}"
    )

    response_content = response.content
    if hasattr(response, "json") and callable(response.json):
        response_content = response.json()

    raise ValidationError(
        f"Error from mdlive: {response.status_code} {response_content}"
    )


def get_fake_user_token(organisation=None):
    site_config = SiteConfiguration.get_solo()
    if site_config.fake_patient:
        return get_user_token(
            {"auth": site_config.fake_patient}, organisation=organisation
        )
    raise ValidationError("Error: Fake patient details not configured")


def get_mdlive_us_time_zone_id(time_zone):
    return constants.TIMEZONE_TO_MDLIVE_ID_MAP.get(
        time_zone, constants.TIMEZONE_TO_MDLIVE_ID_MAP["America/New_York"]
    )


def get_timezone_from_mdlive_us_time_zone_id(mdlive_us_timezone_id):
    return constants.MDLIVE_ID_TO_TIMEZONE_NAME.get(
        mdlive_us_timezone_id, "America/New_York"
    )


def get_providers(
    per_page=None, page=None, data=None, mdlive_fake_user_token=None, patient_id=None
):
    url = "{}/api/v2/patients/{}/providers/search".format(
        settings.MDLIVE_URL, patient_id
    )
    headers = get_mdlive_headers(token=mdlive_fake_user_token)
    params = dict()
    if per_page:
        params["per_page"] = per_page
    if page:
        params["page"] = page
    response = requests_post(url, params=params, json=data, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    raise ValidationError(
        f"Error from mdlive: {response.status_code} {response.content}"
    )


def get_provider(
    provider_id,
    availability_type=None,
    provider_type=None,
    specific_date=None,
    state_abbrev=None,
    show_next_availability=None,
    mdlive_fake_user_token=None,
):
    if not provider_id:
        raise ValidationError("Provider id is required!")

    url = "{}/api/v2/providers/{}/profile".format(settings.MDLIVE_URL, provider_id)
    headers = get_mdlive_headers(token=mdlive_fake_user_token)
    params = dict()
    if availability_type:
        params["availability_type"] = availability_type
    if provider_type:
        params["provider_type"] = provider_type
    if specific_date:
        params["specific_date"] = specific_date
    if state_abbrev:
        params["state_abbrev"] = state_abbrev
    if show_next_availability:
        params["show_next_availability"] = (
            False if show_next_availability == "false" else True
        )
    response = requests_get(url, params=params, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    raise ValidationError(
        f"Error from mdlive: {response.status_code} {response.content}"
    )


def extend_user_token_time(token, organisation=None):
    """
    :param token: jwt token
    :param organisation: beacon.organisations.Organisation object to be used for linking it on mdlive
    :return: extended token
    """
    url = "{}/api/v1/sso_auth/auth_extend".format(settings.MDLIVE_URL)
    headers = get_mdlive_headers(token=token)
    org_data = get_mdlive_organisation_data(organisation=organisation)
    api_data = get_mdlive_api_data()
    data = org_data
    data.update(api_data)
    response = requests_post(url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        return json.loads(response.content).get("jwt")
    raise ValidationError(
        f"Error from mdlive: {response.status_code} {response.content}"
    )


def register_patient_on_mdlive(user_data):
    """
    :param user_data: dict of patient data
    e.g.:
    {
       "patient": {
         "first_name" : "Test",
         "last_name"  : "Test",
         "username"   : "beaconpatient3",
         "email"      : "test@gmail.com",
         "password"   : "123-abc-12",
         "password_confirmation" : "123-abc-12",
         "phone" : "9546666666",
         "zip" : "33327",
         "gender" : "male",
         "birthdate" : "02/22/1988",
         "affiliation_id": "96"
       }
    }
    :return: list of token returned from MDLive
    """
    token = get_token_from_keys()
    headers = get_mdlive_headers(token=token)
    data = deepcopy(user_data)
    url = "{}/api/v1/patients".format(settings.MDLIVE_URL)
    response = requests_post(url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        return json.loads(response.content).get("token")
    raise ValidationError(
        f"Error from mdlive: {response.status_code} {response.content}"
    )


def get_or_create_provider(provider_mdlive_id, provider_data=None):
    """
    Get or create `mdlive.Provider` object
    if provider object exists and provider data not None than update object with the data
    :param provider_mdlive_id: Provider MDLive id
    :param provider_data: Provider data (This data contains few fields like `prefix, speciality, ...`
                                         which does not exists in profile api data)
    :return mdlive.Provider object
    """
    speciality = None
    prefix = None
    photo_in_binary_data = None
    photo_format = None
    if provider_data:
        speciality = provider_data.get("specialty", "SystemBot")
        prefix = provider_data.get("prefix")
        provider_card = provider_data.get("provider_card")
        if provider_card:
            photo_in_binary_data = provider_card.get("photo_in_binary_data")
            photo_format = provider_card.get("photo_format")

    provider = models.Provider.objects.filter(mdlive_id=provider_mdlive_id).first()
    if provider:
        # Update provider data if exists
        if provider_data:
            provider.speciality = speciality
            provider.prefix = prefix
            provider.photo_in_binary_data = photo_in_binary_data
            provider.photo_format = provider.photo_format
            provider.save()
        return provider

    provider_profile = get_provider(provider_mdlive_id).get("provider_details")
    provider = models.Provider.objects.create(
        mdlive_id=provider_mdlive_id,
        fullname=provider_profile.get("fullname"),
        gender=provider_profile.get("gender"),
        speciality=speciality,
        specialities=provider_profile.get("specialties"),
        prefix=prefix,
        photo_url=provider_profile.get("photo_url"),
        photo_url_absolute=provider_profile.get("photo_url_absolute"),
        photo_in_binary_data=photo_in_binary_data,
        photo_format=photo_format,
    )
    return provider


def get_mdlive_token_data_for_user(user, data_to_update=None):
    """
    Get MDLive token for a user
    :param user: users.User object
    :param data_to_update: Specific data that is to be updated with MDLive.
    This will be used if present, else data in user object will be used.
    :return MDLive user token data
      e.g. {"jwt":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjY0MjE5NzkzNSwidXNlcm5hbWUiOiJNRExJVkUtNWU5Y...",
            "user":{"id":642197935,
                    "type":"Patient",
                    "time_to_live_minutes":60}
            }
    """
    if data_to_update is None:
        data_to_update = user.__dict__
        birthdate = user.birthdate.strftime("%Y-%m-%d")
    else:
        birthdate = data_to_update["birthdate"]
    relationship = get_relationship_from_user(user)
    mdlive_data = get_mdlive_data_from_cognito_data(
        cognito_data=data_to_update,
        cognito_sub=str(user.id),
        birth_date_str=str(birthdate),
        relationship=relationship,
    )
    return get_user_token(mdlive_data, organisation=user.organisation)


def get_parsed_datetime_from_message_string(datetime_string):
    """
    It parses datetime string and convert it into timezone aware datetime object
    :param datetime_string: Date-time string e.g. 2018-01-23T13:50:39+00:00
    :return timezone.datetime object
    """
    # This regex removes all colons and all
    # dashes EXCEPT for the dash indicating + or - utc offset for the timezone
    conformed_timestamp = re.sub(
        r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", "", datetime_string
    )
    return timezone.datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S%z")


def create_providers_message(mdlive_message_data, user):
    """
    This service will create `mdlive.Message`, `mdlive.ProviderMessage`, `mdlive.Contact` object
    :param mdlive_message_data: message data dict
    :param user: users.User object whose messages needs to be synced
    :return None
    """
    dt = get_parsed_datetime_from_message_string(mdlive_message_data["date_time"])
    from_id = mdlive_message_data.get("from_id")
    provider = get_or_create_provider(from_id)
    message = models.Message.objects.create(
        message_type=models.Message.PROVIDER_MESSAGE,
        subject=mdlive_message_data.get("subject"),
        message=mdlive_message_data.get("message"),
        mdlive_id=mdlive_message_data["id"],
        is_read=not (mdlive_message_data.get("unread_status")),
        replied_to_message_id=mdlive_message_data.get("replied_to_message_id"),
        reply_allowed=mdlive_message_data.get("reply_allowed", False),
    )
    message.datetime = dt
    message.save()
    models.ProviderMessage.objects.create(
        message=message, message_from=provider, message_to=user
    )
    contact = models.Contact.objects.filter(user=user, provider=provider).first()
    if contact is None:
        models.Contact.objects.create(user=user, provider=provider)


def sync_user_contacts(user):
    """
    Fetch list of all available contacts for user from MDLive and store on our end if does not exists
    :param user: users.User object whose messages needs to be synced
    :return None
    """
    token_data = get_mdlive_token_data_for_user(user)
    token = token_data.get("jwt")
    headers = get_mdlive_headers(token=token)
    contacts_url = (
        f"{settings.MDLIVE_URL}/api/v1/patients/{user.mdlive_id}/messages/contacts"
    )
    response = requests_get(contacts_url, headers=headers)
    if response.status_code != 200:
        raise ValidationError(
            f"Error from mdlive: {response.status_code} {response.content}"
        )
    data = json.loads(response.content)
    contacts_data = data.get("contacts")
    if contacts_data:
        for contact_data in contacts_data:
            provider_mdlive_id = contact_data.get("id")
            contact = models.Contact.objects.filter(
                user__mdlive_id=user.mdlive_id, provider__mdlive_id=provider_mdlive_id
            ).first()
            if contact is None:
                provider = get_or_create_provider(provider_mdlive_id, contact_data)
                models.Contact.objects.create(user=user, provider=provider)


def create_message_on_mdlive(message_data, user):
    """
    This service will hit MDLive api to create user message on mdlive
    :param message_data: message data dict
    :param user: users.User object whose messages needs to be synced
    :return MDLive response
    """
    token_data = get_mdlive_token_data_for_user(user)
    token = token_data.get("jwt")
    headers = get_mdlive_headers(token=token)
    data = {
        "message": {
            "message_type": message_data.get("message_type"),
            "to_id": message_data.get("to_id"),
            "subject": message_data.get("subject"),
            "message": message_data.get("message"),
        }
    }
    if message_data.get("replied_to_message_id") is not None:
        data["message"]["replied_to_message_id"] = message_data["replied_to_message_id"]
    if message_data.get("documents") is not None:
        documents = message_data.get("documents")
        documents_count = len(documents)
        documents_length_string = "files"
        documents_length_string2 = "These files"
        if len(documents) == 1:
            documents_length_string = "file"
            documents_length_string2 = "This file"
        extra_message = (
            f"{user.first_name} uploaded {documents_count} {documents_length_string} with this message. "
            f"{documents_length_string2} can be found in their user profile; named:\n"
        )
        for doc in documents:
            extra_message += f"{doc.document_name}\n"
        data["message"]["message"] += f"\n\n{extra_message}"
    url = f"{settings.MDLIVE_URL}/api/v1/patients/{user.mdlive_id}/messages"
    response = requests_post(url, data=json.dumps(data), headers=headers)
    if response.status_code in [200, 201]:
        return json.loads(response.content)
    raise ValidationError(
        f"Error from mdlive: {response.status_code} {response.content}"
    )


def create_user_message(mdlive_message_data, user, documents=None):
    """
    This service will create `mdlive.Message`, `mdlive.UserMessage`, `mdlive.Contact` object
    :param mdlive_message_data: message data dict
    :param user: users.User object whose messages needs to be synced
    :param documents: mdlive.models.UserDocument ids if they are attached with message
    :return mdlive.models.Message instance which got created
    """
    dt = get_parsed_datetime_from_message_string(mdlive_message_data["date_time"])
    to_id = mdlive_message_data.get("to_id")
    provider = get_or_create_provider(to_id)
    message = models.Message.objects.create(
        message_type=models.Message.USER_MESSAGE,
        subject=mdlive_message_data.get("subject"),
        message=mdlive_message_data.get("message"),
        mdlive_id=mdlive_message_data["id"],
        is_read=not (mdlive_message_data.get("unread_status")),
        replied_to_message_id=mdlive_message_data.get("replied_to_message_id"),
        reply_allowed=mdlive_message_data.get("reply_allowed", False),
        datetime=dt,
    )
    if documents:
        models.MessageDocument.objects.bulk_create(
            [models.MessageDocument(message=message, document=doc) for doc in documents]
        )
    models.UserMessage.objects.create(
        message=message, message_from=user, message_to=provider
    )
    contact = models.Contact.objects.filter(user=user, provider=provider).first()
    if contact is None:
        models.Contact.objects.create(user=user, provider=provider)
    return message


def sync_user_messages(user, provider_id):
    """
    Fetch list of all available messages between user and provider from MDLive
     and store on our end if does not exists
    :param user: users.User object whose messages needs to be synced
    :param provider_id: mdlive.Provider.mdlive_id of provider with whom user messages needs to be synced
    :return None
    """
    token_data = get_mdlive_token_data_for_user(user)
    token = token_data.get("jwt")
    headers = get_mdlive_headers(token=token)
    conversation_url = f"{settings.MDLIVE_URL}/api/v1/patients/{user.mdlive_id}/providers/{provider_id}/conversation"
    response = requests_get(conversation_url, headers=headers)
    if response.status_code != 200:
        raise ValidationError(
            f"Error from mdlive: {response.status_code} {response.content}"
        )
    data = json.loads(response.content)
    messages_data = data.get("messages")
    if messages_data:
        for message_data in messages_data:
            message = models.Message.objects.filter(
                mdlive_id=message_data.get("id")
            ).first()
            # if message exists that means this message and further messages are already synced
            if message:
                break
            from_id = message_data.get("from_id")
            if int(from_id) == int(user.mdlive_id):
                create_user_message(message_data, user)
            if int(from_id) == int(provider_id):
                create_providers_message(message_data, user)


def mark_message_read(user, message):
    """
    :param user: users.User object who is marking message as read
    :param message: mdlive.Message object to be marked as read
    :return None
    """
    token_data = get_mdlive_token_data_for_user(user)
    token = token_data.get("jwt")
    headers = get_mdlive_headers(token=token)
    mark_read_url = f"{settings.MDLIVE_URL}/api/v1/patients/{user.mdlive_id}/messages/{message.mdlive_id}/mark_read"
    response = requests_put(mark_read_url, headers=headers)
    if response.status_code != 204:
        raise ValidationError(
            f"Error from mdlive: {response.status_code} {response.content}"
        )
    message.is_read = True
    message.save()


def request_appointment(
    user,
    provider_id,
    preferred_time,
    appointment_method,
    appointment_date,
    chief_complaint,
    chief_complaint_comments,
    contact_number,
    appointment_request_state,
):
    """
    :param user: users.User object who is marking message as read
    :param provider_id: mdlive.Provider.mdlive_id of provider to whom user is requesting
    :param preferred_time: Preferred time of appointment. Should be one of:
                        (First Available, Morning, Afternoon, Evening)
    :param appointment_method: Requested type of appointment for the patient, should be 'video' or 'phone'
    :param appointment_date: Requested date for appointment
    :param chief_complaint: Chief Complaint for the requested appointment
    :param chief_complaint_comments: Extra comments about complaint for the requested appointment
    :param contact_number: Preferred phone number to contact the patient
    :param appointment_request_state: Preferred state abbreviation (e.g. FL) for the requested appointment
    :return mdlive response
    """
    token_data = get_mdlive_token_data_for_user(user)
    token = token_data.get("jwt")
    headers = get_mdlive_headers(token=token)
    request_appointment_url = (
        f"{settings.MDLIVE_URL}/api/v2/patients/{user.mdlive_id}/appointment_requests"
    )
    data = {
        "appointment_request": {
            "provider_id": provider_id,
            "chief_complaint": chief_complaint,
            "contact_number": contact_number,
            "appointment_date": appointment_date,
            "appointment_method": appointment_method,
            "preferred_time": preferred_time,
        }
    }
    if chief_complaint_comments:
        data["appointment_request"][
            "chief_complaint_comments"
        ] = chief_complaint_comments
    if appointment_request_state:
        data["appointment_request"]["state_abbrev"] = appointment_request_state
    response = requests_post(
        request_appointment_url, data=json.dumps(data), headers=headers
    )
    if response.status_code != 201:
        raise ValidationError(
            f"Error from mdlive: {response.status_code} {response.content}"
        )
    return json.loads(response.content)


def appointment_request_remind(user, appointment_request_id):
    """
    :param user: users.User object who is marking message as read
    :param appointment_request_id: mdlive_id of appointment request
    """
    token_data = get_mdlive_token_data_for_user(user)
    token = token_data.get("jwt")
    headers = get_mdlive_headers(token=token)
    appointment_requests_remind_url = (
        f"{settings.MDLIVE_URL}/api/v2/patients/{user.mdlive_id}/appointment_requests/"
        f"{appointment_request_id}/remind"
    )
    response = requests_post(appointment_requests_remind_url, headers=headers)
    if response.status_code != 200:
        raise ValidationError(
            f"Error from mdlive: {response.status_code} {response.content}"
        )
    return json.loads(response.content)


def appointment_request_cancel(user, appointment_request_id):
    """
    :param user: users.User object who is marking message as read
    :param appointment_request_id: mdlive_id of appointment request
    """
    token_data = get_mdlive_token_data_for_user(user)
    token = token_data.get("jwt")
    headers = get_mdlive_headers(token=token)
    appointment_requests_remind_url = (
        f"{settings.MDLIVE_URL}/api/v2/patients/{user.mdlive_id}/appointment_requests/"
        f"{appointment_request_id}/cancel"
    )
    response = requests_post(appointment_requests_remind_url, headers=headers)
    if response.status_code != 200:
        raise ValidationError(
            f"Error from mdlive: {response.status_code} {response.content}"
        )
    return json.loads(response.content)


def create_webhook():
    """
    Setup webhook on mdlive based on url defined in settings
    """
    token = get_token_from_keys()
    headers = get_mdlive_headers(token=token)
    url = f"{settings.MDLIVE_WEBHOOK_BASE_URL}{settings.MDLIVE_WEBHOOK_URL}"
    data = {"webhook": {"url": url}}
    url = f"{settings.MDLIVE_URL}/api/v1/webhook"
    response = requests_post(url, data=json.dumps(data), headers=headers)
    if response.status_code == 201:
        return json.loads(response.content)
    raise ValidationError(
        f"Error from mdlive: {response.status_code} {response.content}"
    )


def delete_user_document(user_document):
    """
    :param user_document: mdlive.UserDocument object
    :return mdlive response
    """
    if user_document and user_document.mdlive_id:
        user = user_document.user
        token_data = get_mdlive_token_data_for_user(user)
        token = token_data.get("jwt")
        headers = get_mdlive_headers(token=token)
        document_url = f"{settings.MDLIVE_URL}/api/v1/patients/{user.mdlive_id}/documents/{user_document.mdlive_id}"
        response = requests_delete(document_url, headers=headers)
        if response.status_code not in [200, 204]:
            raise ValidationError(
                f"Error from mdlive: {response.status_code} {response.content}"
            )
        return json.loads(response.content)
    # If it does not exists on MDLive we can delete directly on our end
    return True


def send_new_message_email_to_user(user, email_template="email/new_message_email.tpl"):
    program_name = None
    if user.organisation:
        program_name = user.organisation.program_name
        if program_name is None and user.organisation.parent is not None:
            program_name = user.organisation.parent.program_name
    ctx = {
        "first_name": user.first_name,
        "organisation": user.organisation,
        "program_name": program_name,
        "site": get_current(),  # for template images in base template
    }
    return send_mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        template_name=email_template,
        context=ctx,
    )


def get_patient_from_mdlive(patient_id, token):
    """
    Fetch and return patient's details from MDLive.
    http://developers.mdlivetechnology.com/#patients-update-a-patient

    :param patient_id: MDLive ID of the patient
    :param token: Patient specific JWT Auth token for MDLive APIs
    :return: response data from MDLive
    """
    url = f"{settings.MDLIVE_URL}/api/v2/patients/{patient_id}"
    headers = get_mdlive_headers(token=token)
    response = requests_get(url=url, headers=headers)

    response_content = response.content
    if response_content and hasattr(response, "json") and callable(response.json):
        response_content = response.json()
        # removing "affiliation" because it contains a lot of unnecessary text
        # like MDLive's Privacy Policy, etc.
        if response_content.get("patient_profile", None):
            response_content["patient_profile"].pop("affiliation", None)
    log.info(
        f"For MDLive ID: {patient_id}. "
        + f"Response from MDLive while fetching patient's details: {response_content}"
    )

    if response.status_code == 200:
        log.info(
            f"For MDLive ID: {patient_id}. "
            + "Patient's details retrieved successfully!"
        )
        return json.loads(response.content)

    log.info(
        f"For MDLive ID: {patient_id}. Failed to retrieve Patient's details."
        + f" {response_content}"
    )
    raise ValidationError(
        "Error while retrieving patient's details from MDLive:"
        + f" {response.status_code} {response_content}"
    )


def update_patient_on_mdlive(patient_id, data_to_update, token):
    """
    Update the patient's details on MDLive.
    http://developers.mdlivetechnology.com/#patients-update-a-patient

    :param patient_id: MDLive ID of the patient
    :param data_to_update: Data dictionary to update for patient
    :param token: Patient specific JWT Authorization token for MDLive APIs
    :return: updated patient resource from MDLive
    """
    url = f"{settings.MDLIVE_URL}/api/v2/patients/{patient_id}"
    headers = get_mdlive_headers(token=token)
    headers.update({"Accept": "application/json"})
    data = {"patient": data_to_update}
    response = requests_patch(url=url, data=json.dumps(data), headers=headers)

    response_content = response.content
    if response_content and hasattr(response, "json") and callable(response.json):
        response_content = response.json()
        # removing "affiliation" because it contains a lot of unnecessary text
        # like MDLive's Privacy Policy, etc.
        if response_content.get("patient_profile", None):
            response_content["patient_profile"].pop("affiliation", None)
    log.info(
        f"For MDLive ID: {patient_id} and request data: {data} "
        + f"Response from MDLive while updating patient's details: {response_content}"
    )
    if response.status_code == 200:
        log.info(
            f"For MDLive ID: {patient_id}. "
            + "Patient's details updated successfully on MDLive!"
        )
        return json.loads(response.content)

    log.info(
        f"For MDLive ID: {patient_id}. Failed to update Patient's details."
        + f" {response_content}"
    )
    raise ValidationError(
        "Error while updating patient's details on MDLive:"
        + f" {response.status_code} {response_content}"
    )
