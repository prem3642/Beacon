# -*- coding: utf-8 -*-
# Standard Library
import json
from collections import namedtuple

# Third Party Stuff
import pytest
from django.conf import settings
from django.urls import reverse
from django_dynamic_fixture import G

# beacon Stuff
from beacon.answers.services import get_token_for_user_response
from beacon.answers.tests import factories as answers_f
from beacon.base.models import SiteConfiguration
from beacon.mdlive import services as mdlive_services
from beacon.users.tests import factories as users_f

from ..models import Contact, Message, Provider, ProviderMessage, UserMessage
from . import factories as f

pytestmark = pytest.mark.django_db


def test_fake_user_token(client, mocker):
    url = reverse("mdlive-fake-user-token")
    user_response = answers_f.create_user_response()
    answer_token = get_token_for_user_response(user_response, "authentication")
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = f.get_mocked_mdlive_token_response()

    # should require answer auth
    response = client.json.get(url)
    assert response.status_code == 403

    response = client.json.get(url, HTTP_AUTHORIZATION="Token {}".format(answer_token))
    assert response.status_code == 200
    assert mocked_mdlive_user_token.called
    assert response.data.get("user").get("id") == 52


def test_search_providers(client, mocker):
    url = reverse("mdlive-search-providers")
    # Configuring fake user data
    G(SiteConfiguration, fake_patient={"first_name": "User01"})

    user_response = answers_f.create_user_response()
    answer_token = get_token_for_user_response(user_response, "authentication")
    mocked_mdlive_search_provider = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_search_provider.return_value = (
        f.get_mocked_mdlive_providers_search_response()
    )

    # should require answer auth
    response = client.json.post(url)
    assert response.status_code == 403

    response = client.json.post(url, HTTP_AUTHORIZATION="Token {}".format(answer_token))
    assert response.status_code == 400
    assert (
        response.data["errors"][0]["message"]
        == "mdlive_token query param should be present"
    )
    response = client.json.post(
        url + "?mdlive_token=dummy-token",
        HTTP_AUTHORIZATION="Token {}".format(answer_token),
    )
    assert response.status_code == 400
    assert (
        response.data["errors"][0]["message"]
        == "patient_id query param should be present"
    )

    response = client.json.post(
        url + "?patient_id=999999&mdlive_token=dummy-token",
        HTTP_AUTHORIZATION="Token {}".format(answer_token),
    )
    assert response.status_code == 200
    assert mocked_mdlive_search_provider.called
    assert response.data.get("providers")[0].get("id") == 642183606


def test_providers_profile(client, mocker):
    url = reverse("mdlive-providers-profile")

    user_response = answers_f.create_user_response()
    answer_token = get_token_for_user_response(user_response, "authentication")

    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = f.get_mocked_mdlive_token_response()

    data = dict(id=4)
    mocked_mdlive_providers_profile = mocker.patch(
        "beacon.mdlive.services.requests_get"
    )
    mocked_mdlive_providers_profile.return_value = (
        f.get_mocked_mdlive_provider_profile_response(data)
    )

    # should require answer auth
    response = client.json.get(url)
    assert response.status_code == 403

    # Provider's id required
    response = client.json.get(url, HTTP_AUTHORIZATION="Token {}".format(answer_token))
    assert response.status_code == 400

    response = client.json.get(
        "{}?provider_id=4".format(url),
        HTTP_AUTHORIZATION="Token {}".format(answer_token),
    )
    assert response.status_code == 400
    assert (
        response.data["errors"][0]["message"]
        == "mdlive_token query param should be present"
    )

    response = client.json.get(
        "{}?provider_id=4&mdlive_token=dummy-token".format(url),
        HTTP_AUTHORIZATION="Token {}".format(answer_token),
    )
    assert response.status_code == 200
    assert mocked_mdlive_providers_profile.called
    assert response.data.get("provider_details").get("id") == 4


def test_user_token(client, mocker):
    url = reverse("mdlive-user-token")
    user, mdlive_res, cognito_res = users_f.create_user_with_mocked_values()
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = mdlive_res

    # should require auth
    response = client.get(url)
    assert response.status_code == 401

    client.login(user)
    response = client.get(url)
    assert response.status_code == 200
    assert mocked_mdlive_user_token.called
    assert response.data.get("user").get("id") == 52


def test_extend_token(client, mocker):
    url = reverse("mdlive-extend-token")
    mocked_data = f.get_mocked_mdlive_token_response()
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = mocked_data
    user = users_f.create_user()

    post_data = dict(jwt_token="jdgsjhfajkjshaubdz,kdshidnajdgzjfjzg")

    # should require auth
    response = client.json.post(url, json.dumps(post_data))
    assert response.status_code == 401

    client.login(user)
    response = client.json.post(url, json.dumps(post_data))
    expected_keys = ["jwt_token"]
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data.keys())
    assert mocked_mdlive_user_token.called


def test_get_message_api(client):
    user = users_f.create_user()
    user2 = users_f.create_user()
    provider = f.create_provider()
    provider2 = f.create_provider()
    message = f.create_message(message_type=Message.USER_MESSAGE, is_read=True)
    message2 = f.create_message(message_type=Message.PROVIDER_MESSAGE, is_read=False)
    message3 = f.create_message(message_type=Message.PROVIDER_MESSAGE, is_read=False)
    f.create_user_message(message=message, message_from=user, message_to=provider)
    f.create_provider_message(message=message2, message_to=user, message_from=provider)
    f.create_provider_message(
        message=message3, message_to=user2, message_from=provider2
    )
    f.create_contact(user=user, provider=provider)
    f.create_contact(user=user, provider=provider2)
    url = reverse("messages-detail", kwargs={"mdlive_id": message3.mdlive_id})

    # should require auth
    response = client.json.get(url)
    assert response.status_code == 401

    # Can't access someone else message
    client.login(user)
    response = client.json.get(url)
    assert response.status_code == 404

    url = reverse("messages-detail", kwargs={"mdlive_id": message2.mdlive_id})
    response = client.json.get(url)
    expected_keys = [
        "id",
        "subject",
        "message",
        "unread_status",
        "replied_to_message_id",
        "date_time",
        "from",
        "from_id",
        "to",
        "to_id",
        "reply_allowed",
    ]
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("id") == message2.mdlive_id
    assert response.data.get("from_id") == provider.mdlive_id
    assert response.data.get("to_id") == user.mdlive_id


def test_get_messages_api(client):
    url = reverse("messages-list")
    user = users_f.create_user()
    provider = f.create_provider()
    provider2 = f.create_provider()
    message = f.create_message(message_type=Message.USER_MESSAGE, is_read=True)
    message2 = f.create_message(message_type=Message.PROVIDER_MESSAGE, is_read=False)
    message3 = f.create_message(message_type=Message.PROVIDER_MESSAGE, is_read=False)
    f.create_user_message(message=message, message_from=user, message_to=provider)
    f.create_provider_message(message=message2, message_to=user, message_from=provider)
    f.create_provider_message(message=message3, message_to=user, message_from=provider2)
    f.create_contact(user=user, provider=provider)
    f.create_contact(user=user, provider=provider2)

    # should require auth
    response = client.json.get(url)
    assert response.status_code == 401

    client.login(user)
    response = client.json.get(url)
    expected_keys = [
        "id",
        "subject",
        "message",
        "unread_status",
        "replied_to_message_id",
        "date_time",
        "from",
        "from_id",
        "to",
        "to_id",
        "reply_allowed",
    ]
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data.get("results")[0].keys())
    assert response.data.get("count") == 3
    assert response.data.get("results")[0].get("id") == message3.mdlive_id
    assert response.data.get("results")[0].get("from_id") == provider2.mdlive_id
    assert response.data.get("results")[0].get("to_id") == user.mdlive_id
    assert response.data.get("results")[2].get("id") == message.mdlive_id
    assert response.data.get("results")[2].get("from_id") == user.mdlive_id
    assert response.data.get("results")[2].get("to_id") == provider.mdlive_id

    response = client.json.get(f"{url}?provider={provider.mdlive_id}")
    assert response.data.get("count") == 2
    assert response.data.get("results")[0].get("id") == message2.mdlive_id
    assert response.data.get("results")[1].get("id") == message.mdlive_id

    response = client.json.get(
        f"{url}?provider={provider.mdlive_id}&unread_status=true"
    )
    assert response.data.get("count") == 1
    assert response.data.get("results")[0].get("id") == message2.mdlive_id


def test_get_unread_messages_count_api(client):
    url = reverse("messages-unread-messages-count")
    user = users_f.create_user()
    provider = f.create_provider()
    provider2 = f.create_provider()
    message = f.create_message(message_type=Message.USER_MESSAGE, is_read=True)
    message2 = f.create_message(message_type=Message.PROVIDER_MESSAGE, is_read=False)
    message3 = f.create_message(message_type=Message.PROVIDER_MESSAGE, is_read=False)
    f.create_user_message(message=message, message_from=user, message_to=provider)
    f.create_provider_message(message=message2, message_to=user, message_from=provider)
    f.create_provider_message(message=message3, message_to=user, message_from=provider2)
    f.create_contact(user=user, provider=provider)
    f.create_contact(user=user, provider=provider2)

    # should require auth
    response = client.json.get(url)
    assert response.status_code == 401

    client.login(user)
    response = client.json.get(url)
    assert response.status_code == 200
    assert response.data.get("count") == 2

    response = client.json.get(f"{url}?provider={provider.mdlive_id}")
    assert response.data.get("count") == 1


def test_get_contact_api(client):
    user = users_f.create_user()
    user2 = users_f.create_user()
    provider = f.create_provider()
    provider2 = f.create_provider()
    f.create_contact(user=user, provider=provider)
    f.create_contact(user=user2, provider=provider2)
    url = reverse("contacts-detail", kwargs={"mdlive_id": provider2.mdlive_id})

    # should require auth
    response = client.json.get(url)
    assert response.status_code == 401

    # Don't have access to other user provider
    client.login(user)
    response = client.json.get(url)
    assert response.status_code == 404

    url = reverse("contacts-detail", kwargs={"mdlive_id": provider.mdlive_id})
    response = client.json.get(url)
    expected_keys = (
        "id",
        "fullname",
        "prefix",
        "gender",
        "speciality",
        "photo_url",
        "photo_url_absolute",
    )
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("id") == provider.mdlive_id


def test_get_contacts_api(client):
    url = reverse("contacts-list")
    user = users_f.create_user()
    provider = f.create_provider()
    provider2 = f.create_provider()
    f.create_contact(user=user, provider=provider)
    f.create_contact(user=user, provider=provider2)

    # should require auth
    response = client.json.get(url)
    assert response.status_code == 401

    client.login(user)
    response = client.json.get(url)
    expected_keys = (
        "id",
        "fullname",
        "prefix",
        "gender",
        "speciality",
        "photo_url",
        "photo_url_absolute",
    )
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data[0].keys())
    assert len(response.data) == 2
    assert response.data[0].get("id") == provider2.mdlive_id
    assert response.data[1].get("id") == provider.mdlive_id


def test_message_mark_read(client, mocker):
    user = users_f.create_user()
    provider = f.create_provider()
    provider2 = f.create_provider()
    message = f.create_message(message_type=Message.USER_MESSAGE, is_read=True)
    message2 = f.create_message(message_type=Message.PROVIDER_MESSAGE, is_read=False)
    message3 = f.create_message(message_type=Message.PROVIDER_MESSAGE, is_read=False)
    f.create_user_message(message=message, message_from=user, message_to=provider)
    f.create_provider_message(message=message2, message_to=user, message_from=provider)
    f.create_provider_message(message=message3, message_to=user, message_from=provider2)
    f.create_contact(user=user, provider=provider)
    f.create_contact(user=user, provider=provider2)

    url = reverse("messages-mark-read", kwargs={"mdlive_id": message2.mdlive_id})
    unread_message_count_url = reverse("messages-unread-messages-count")
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = f.get_mocked_mdlive_token_response()
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    mdlive_res = mdlive_response(204, None)
    mocked_mdlive_message_mark_read = mocker.patch(
        "beacon.mdlive.services.requests_put"
    )
    mocked_mdlive_message_mark_read.return_value = mdlive_res

    # should require auth
    response = client.json.put(url)
    assert response.status_code == 401

    client.login(user)
    response = client.json.get(unread_message_count_url)
    assert response.status_code == 200
    assert response.data.get("count") == 2

    response = client.json.put(url)
    message2.refresh_from_db()
    assert response.status_code == 204
    assert mocked_mdlive_message_mark_read.called
    assert message2.is_read is True

    response = client.json.get(unread_message_count_url)
    assert response.status_code == 200
    assert response.data.get("count") == 1


def test_create_message(client, mocker):
    user = users_f.create_user()
    provider = f.create_provider()
    url = reverse("messages-list")

    data = {"to_id": provider.mdlive_id}
    (
        create_message_res,
        create_message_data,
    ) = f.get_mocked_mdlive_create_messages_response(user, data)

    def my_side_effect(*args, **kwargs):
        if (
            args[0]
            == f"{settings.MDLIVE_URL}/api/v1/patients/{user.mdlive_id}/messages"
        ):
            return create_message_res
        elif args[0] == f"{settings.MDLIVE_URL}/api/v1/sso_auth/auth_token":
            return f.get_mocked_mdlive_token_response()

    mocked_mdlive = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive.side_effect = my_side_effect

    message_data = {
        "to_id": provider.mdlive_id,
        "subject": create_message_data["message"]["subject"],
        "message": create_message_data["message"]["message"],
    }

    assert Message.objects.first() is None
    assert Contact.objects.first() is None
    assert UserMessage.objects.first() is None

    # should require auth
    response = client.json.post(url, data=json.dumps(message_data))
    assert response.status_code == 401

    client.login(user)
    response = client.json.post(url, data=json.dumps(message_data))
    expected_keys = [
        "id",
        "message_type",
        "to",
        "to_id",
        "subject",
        "message",
        "unread_status",
        "replied_to_message_id",
        "date_time",
        "from",
        "from_id",
        "documents",
    ]
    assert response.status_code == 201
    assert set(expected_keys).issubset(response.data.keys())
    assert Message.objects.first() is not None
    assert Contact.objects.first() is not None
    assert UserMessage.objects.first() is not None


def test_webhook(client, mocker):
    url = reverse("messages-webhook")
    user = users_f.create_user()
    mocked_sync_user_messages = mocker.patch(
        "beacon.mdlive.api.sync_user_mdlive_messages.delay"
    )
    data = {
        "event": {
            "token": "736a0864-5b1a-4e49-9791-ace850a8f7f1",
            "action": "consultation:provider:accepted",
            "data": {
                "message": {
                    "id": 3245678,
                    "from_id": 642183606,
                    "to_id": user.mdlive_id,
                    "unread_status": True,
                    "replied_to_message_id": None,
                }
            },
        }
    }
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 200
    assert not mocked_sync_user_messages.called

    data["event"]["action"] = "message:provider:created"
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 200
    assert mocked_sync_user_messages.called


def test_sync_user_messages_service(client, mocker):
    user = users_f.create_user()
    provider_id = 642183606
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = f.get_mocked_mdlive_token_response()

    def my_side_effect(*args, **kwargs):
        if (
            args[0]
            == f"{settings.MDLIVE_URL}/api/v1/patients/{user.mdlive_id}/providers/{provider_id}/conversation"
        ):
            return f.get_mocked_mdlive_messages_response(user)
        elif args[0] == f"{settings.MDLIVE_URL}/api/v2/providers/{provider_id}/profile":
            return f.get_mocked_mdlive_provider_profile_response()

    mocked_mdlive = mocker.patch("beacon.mdlive.services.requests_get")
    mocked_mdlive.side_effect = my_side_effect
    G(SiteConfiguration, fake_patient={"first_name": "User01"})

    assert Message.objects.first() is None
    assert Contact.objects.first() is None
    assert Provider.objects.first() is None
    assert ProviderMessage.objects.first() is None

    mdlive_services.sync_user_messages(user, provider_id)
    assert mocked_mdlive_user_token.called
    assert mocked_mdlive.call_count == 2
    assert Message.objects.first() is not None
    assert Contact.objects.first() is not None
    assert Provider.objects.first() is not None
    assert ProviderMessage.objects.first() is not None


def test_sync_contacts_service(client, mocker):
    user = users_f.create_user()
    provider_id = 642183606
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = f.get_mocked_mdlive_token_response()

    def my_side_effect(*args, **kwargs):
        if (
            args[0]
            == f"{settings.MDLIVE_URL}/api/v1/patients/{user.mdlive_id}/messages/contacts"
        ):
            return f.get_mocked_mdlive_contacts_response()
        elif args[0] == f"{settings.MDLIVE_URL}/api/v2/providers/{provider_id}/profile":
            data = {"id": provider_id}
            return f.get_mocked_mdlive_provider_profile_response(data)

    mocked_mdlive = mocker.patch("beacon.mdlive.services.requests_get")
    mocked_mdlive.side_effect = my_side_effect

    assert Contact.objects.first() is None
    assert Provider.objects.first() is None

    mdlive_services.sync_user_contacts(user)
    assert mocked_mdlive_user_token.called
    assert mocked_mdlive.call_count == 2
    assert Contact.objects.first() is not None
    assert Provider.objects.first() is not None


def test_create_appointment_slot_queries(client, mocker):
    user, _, _ = users_f.create_user_with_mocked_values()
    answers_f.create_user_response(user=user, response=[], appointment_state="FL")
    url = reverse("appointment-slot-queries-list")
    patched_mdlive_request_appointment = mocker.patch(
        "beacon.mdlive.api.services.request_appointment"
    )
    patched_mdlive_request_appointment.return_value = {
        "appointment_request": {"id": 123456}
    }
    patched_mdlive_task = mocker.patch(
        "beacon.mdlive.api.sync_user_mdlive_messages.delay"
    )
    patched_send_user_data_to_scc = mocker.patch(
        "beacon.mdlive.api.send_user_data_to_scc_if_non_f2f"
    )
    data = {
        "provider_id": 1234,
        "appointment_date": "2018-12-20",
        "appointment_method": "phone",
        "preferred_time": "first available",
    }
    client.login(user=user)
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 201
    expected_keys = [
        "id",
        "mdlive_id",
        "provider_id",
        "preferred_time",
        "appointment_method",
        "appointment_date",
        "chief_complaint",
        "chief_complaint_comments",
        "contact_number",
        "appointment_request_state",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("provider_id") == data.get("provider_id")
    assert response.data.get("appointment_date") == data.get("appointment_date")
    assert response.data.get("appointment_method") == data.get("appointment_method")
    assert response.data.get("preferred_time") == data.get("preferred_time")
    patched_mdlive_request_appointment.assert_called()
    patched_mdlive_task.assert_called_with(str(user.id))
    patched_send_user_data_to_scc.assert_called_with(
        user=user, appointment_method=data.get("appointment_method")
    )
