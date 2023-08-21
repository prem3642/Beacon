# -*- coding: utf-8 -*-
# Standard Library
import json
from collections import namedtuple

# Third Party Stuff
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

# beacon Stuff
from beacon.answers import constants
from beacon.answers.models import UserAppointment, UserResponse
from beacon.answers.tests import factories as answers_f
from beacon.cognito.tests import factories as cognito_f
from beacon.organisations.tests import factories as org_f
from beacon.questionnaire.models import Question
from beacon.questionnaire.tests import factories as questionnaire_f

from ..models import UserAgent
from . import factories as f

pytestmark = pytest.mark.django_db


def test_user_registration(client, mocker):
    url = reverse("auth-register")
    org = org_f.create_organisation(parent=None)
    answer = answers_f.create_user_response(
        user=None,
        chief_complaint1="Anxiety",
        chief_complaint2="Depression",
        appointment_state="PR",
    )
    answers_f.create_user_appointment(
        user_response=answer,
        appointment_method=UserAppointment.FACE_TO_FACE,
        bwb_inquiry_id=None,
    )

    mdlive_res_data = dict(
        jwt="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjUyLCJ1c2VybmFtZSI6ImRlbW9wYXRpZW50MSIsInByaW",
        user=dict(id=52, type="Patient", time_to_live_minutes=60),
    )
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    mdlive_res = mdlive_response(200, json.dumps(mdlive_res_data))
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = mdlive_res
    mocked_mdlive_timezone_sync_task = mocker.patch(
        "beacon.users.services.mdlive_tasks.sync_user_timezone_with_mdlive_timezone_id_task.delay"
    )

    data = dict(
        first_name="User",
        last_name="Test",
        gender="M",
        birthdate="06/21/1988",
        phone="8888888888",
        email="user@example.com",
        address1="Address line 1",
        address2=None,
        city="the Hague",
        state="AZ",
        zip="12345",
        relationship="Self",
        relationship_status="Never Married",
        employment_status="Part Time",
        job_title="Professional",
        password="TestUser01$",
        answer=str(answer.id),
        agrees_to_mdlive_informed_consent=True,
        agrees_to_beacon_privacy_notice=True,
        agrees_to_mdlive_privacy_agreement=True,
        mdlive_consent_user_initials="ut",
        organisation=str(org.id),
        timezone="America/New_York",
    )
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_f.get_mocked_cognito_object(data)

    # TODO: fix this later as requests modules response is conflicting between mdlive and bwb
    bwb_res_data = b"11234-2345"
    bwb_response = namedtuple("bwb_response", ["status_code", "content"])
    bwb_res = bwb_response(200, bwb_res_data)
    mocked_bwb_server_request = mocker.patch("beacon.users.utils.requests_post")
    mocked_bwb_server_request.return_value = bwb_res

    response = client.json.post(url, json.dumps(data))
    assert response.status_code == 201
    expected_keys = [
        "id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "address1",
        "address2",
        "city",
        "zip",
        "gender",
        "state",
        "employment_status",
        "relationship_status",
        "job_title",
        "is_verified",
        "mdlive_id",
        "agrees_to_beacon_privacy_notice",
        "agrees_to_mdlive_informed_consent",
        "agrees_to_mdlive_privacy_agreement",
        "mdlive_consent_user_initials",
        "chief_complaint1",
        "chief_complaint2",
        "appointment_state",
        "md_live",
        "md_live_ou",
        "auth_token",
        "timezone",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert mocked_cognito.called
    assert mocked_mdlive_user_token.called
    assert mocked_bwb_server_request.called
    assert mocked_mdlive_timezone_sync_task.called
    assert response.data.get("appointment_state") == "PR"
    assert (
        response.data.get("md_live").get("user").get("id")
        == mdlive_res_data["user"]["id"]
    )

    user = get_user_model().objects.get(id=response.data.get("id"))
    assert user.send_to_scc_if_non_f2f is True


def test_user_confirm_sign_up(client, mocker):
    url = reverse("auth-confirm-sign-up")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res

    confirm_data = {"email": user.email, "otp": "123456"}
    response = client.json.post(url, json.dumps(confirm_data))
    assert response.status_code == 200
    assert mocked_cognito.called


def test_user_resend_verification_email(client, mocker):
    url = reverse("auth-resend-verification-email")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res

    post_data = {"email": user.email}
    response = client.json.post(url, json.dumps(post_data))
    assert response.status_code == 200
    assert mocked_cognito.called


def test_user_login(client, mocker):
    url = reverse("auth-login")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mdlive_res_data = json.loads(mdlive_res.content)
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = mdlive_res
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res
    mocked_sync_user_messages = mocker.patch(
        "beacon.users.api.sync_user_mdlive_messages.delay"
    )

    assert UserAgent.objects.first() is None

    credentials = {"email": user.email, "password": "TestUser01"}
    response = client.json.post(url, json.dumps(credentials))
    assert response.status_code == 200
    expected_keys = [
        "id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "address1",
        "address2",
        "city",
        "zip",
        "gender",
        "state",
        "employment_status",
        "relationship_status",
        "job_title",
        "is_verified",
        "mdlive_id",
        "agrees_to_beacon_privacy_notice",
        "agrees_to_mdlive_informed_consent",
        "agrees_to_mdlive_privacy_agreement",
        "mdlive_consent_user_initials",
        "chief_complaint1",
        "chief_complaint2",
        "appointment_state",
        "md_live",
        "md_live_ou",
        "auth_token",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert mocked_cognito.called
    assert mocked_mdlive_user_token.called
    assert mocked_sync_user_messages.called
    # Answer is not created for them
    assert response.data.get("appointment_state") is None
    assert response.data.get("chief_complaint1") is None
    assert response.data.get("chief_complaint2") is None
    assert (
        response.data.get("md_live").get("user").get("id")
        == mdlive_res_data["user"]["id"]
    )
    assert UserAgent.objects.first().user.id == user.id


def test_user_logout(client, mocker):
    login_url = reverse("auth-login")
    me_url = reverse("me")
    url = reverse("auth-logout")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = mdlive_res
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res
    mocker.patch("beacon.users.api.sync_user_mdlive_messages.delay")

    credentials = {"email": user.email, "password": "TestUser01"}
    response = client.json.post(login_url, json.dumps(credentials))
    assert response.status_code == 200
    auth_token = response.data.get("auth_token")

    # Logout
    response = client.json.post(url, HTTP_AUTHORIZATION="Token {}".format(auth_token))
    assert response.status_code == 200

    # Get my profile again
    response = client.get(me_url, HTTP_AUTHORIZATION="Token {}".format(auth_token))
    assert response.status_code == 401


def test_extend_token(client, mocker):
    login_url = reverse("auth-login")
    url = reverse("auth-extend-token")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = mdlive_res
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res
    mocker.patch("beacon.users.api.sync_user_mdlive_messages.delay")

    credentials = {"email": user.email, "password": "TestUser01"}
    response = client.json.post(login_url, json.dumps(credentials))
    assert response.status_code == 200
    assert mocked_mdlive_user_token.called
    assert mocked_cognito.called
    auth_token = response.data.get("auth_token")

    # should require auth
    response = client.json.post(url)
    assert response.status_code == 401

    response = client.json.post(url, HTTP_AUTHORIZATION="Token {}".format(auth_token))
    expected_keys = ["auth_token"]
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data.keys())
    assert mocked_mdlive_user_token.call_count == 1
    assert mocked_cognito.call_count == 1


def test_user_password_change(client, mocker):
    url = reverse("auth-password-change")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res
    current_password = "password1"
    new_password = "paSswOrd2.#$"
    change_password_payload = {
        "current_password": current_password,
        "new_password": new_password,
    }

    # should require auth
    response = client.json.post(url, json.dumps(change_password_payload))
    assert response.status_code == 401

    client.login(user=user)
    response = client.json.post(url, json.dumps(change_password_payload))
    assert response.status_code == 200
    assert mocked_cognito.called
    client.logout()

    url = reverse("auth-login")
    mocker.patch("beacon.users.api.sync_user_mdlive_messages.delay")
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = mdlive_res
    credentials = {"email": user.email, "password": new_password}

    response = client.json.post(url, json.dumps(credentials))
    assert response.status_code == 200
    expected_keys = [
        "id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "address1",
        "address2",
        "city",
        "zip",
        "gender",
        "state",
        "employment_status",
        "relationship_status",
        "job_title",
        "is_verified",
        "mdlive_id",
        "agrees_to_beacon_privacy_notice",
        "agrees_to_mdlive_informed_consent",
        "agrees_to_mdlive_privacy_agreement",
        "mdlive_consent_user_initials",
        "chief_complaint1",
        "chief_complaint2",
        "appointment_state",
        "md_live",
        "md_live_ou",
        "auth_token",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert mocked_cognito.call_count == 2
    assert mocked_mdlive_user_token.called

    user.refresh_from_db()
    assert user.check_password(new_password)


def test_user_password_reset(client, mocker):
    url = reverse("auth-password-reset")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res

    # User is not verified yet
    user.is_verified = False
    user.save()
    response = client.json.post(url, json.dumps({"email": user.email}))
    assert response.status_code == 420

    user.is_verified = True
    user.save()
    response = client.json.post(url, json.dumps({"email": user.email}))
    assert response.status_code == 200
    assert mocked_cognito.called


def test_user_password_reset_and_confirm(client, mocker):
    url = reverse("auth-password-reset-confirm")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res

    new_password = "CompLicatedpaSswOrd2$"
    password_reset_confirm_data = {
        "email": user.email,
        "new_password": new_password,
        "otp": "123456",
    }
    response = client.json.post(url, json.dumps(password_reset_confirm_data))
    assert response.status_code == 200
    assert mocked_cognito.called

    user.refresh_from_db()
    assert user.check_password(new_password)


def test_get_current_user_api(client, mocker):
    url = reverse("me")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
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
    expected_keys = [
        "id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "address1",
        "address2",
        "city",
        "zip",
        "gender",
        "state",
        "employment_status",
        "relationship_status",
        "job_title",
        "is_verified",
        "mdlive_id",
        "agrees_to_beacon_privacy_notice",
        "agrees_to_mdlive_informed_consent",
        "agrees_to_mdlive_privacy_agreement",
        "mdlive_consent_user_initials",
        "chief_complaint1",
        "chief_complaint2",
        "appointment_state",
        "md_live",
        "md_live_ou",
        "organisation",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert not mocked_cognito.called  # profile data being returned from our database
    assert mocked_mdlive_user_token.called
    assert response.data["id"] == str(user.id)


def test_update_appointment_state_api(client, mocker):
    url = reverse("me-update-appointment-state")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    # mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    # mocked_cognito.return_value = cognito_res
    # mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    # mocked_mdlive_user_token.return_value = mdlive_res
    payload = {"appointment_state": "Florida"}
    # should require auth
    response = client.json.post(url, data=json.dumps(payload))
    assert response.status_code == 401

    client.login(user)
    response = client.json.post(url, data=json.dumps(payload))
    assert response.status_code == 400
    assert (
        response.data["errors"][0]["message"]
        == "No user response found to update appointment_state."
    )

    user_response = answers_f.create_user_response(user=user, response=[])
    question = questionnaire_f.create_question(
        kind=Question.DROPDOWN, user_response_attribute=constants.APPOINTMENT_STATE
    )
    questionnaire_f.create_option(
        text="Florida", question=question, text_mapped_value="FL"
    )
    response = client.json.post(url, data=json.dumps(payload))
    assert response.status_code == 200
    assert response.data["message"] == "Appointment State updated successfully!"
    user_response.refresh_from_db()
    assert set(
        [
            "question",
            "answer",
            "text_mapped_value",
            "user_response_attribute",
            "user_appointment_attribute",
        ]
    ).issubset(user_response.response[0].keys())
    assert user_response.response[0]["answer"] == "Florida"
    assert user_response.response[0]["text_mapped_value"] == "FL"
    assert (
        user_response.response[0]["user_response_attribute"]
        == constants.APPOINTMENT_STATE
    )
    assert user_response.response[0]["user_appointment_attribute"] is None
    assert user_response.appointment_state == "FL"


# TODO: uncomment this when user profile update is approved by client
# def test_update_user_profile(client, mocker):
#     url = reverse('me')
#     user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
#     mocked_cognito = mocker.patch('beacon.cognito.services.Cognito')
#     mocked_cognito.return_value = cognito_res
#
#     data = {
#         'first_name': 'User',
#         'state': 'FL',
#         'phone': '8888888888'
#     }
#
#     # should require auth
#     response = client.json.patch(url, json.dumps(data))
#     assert response.status_code == 401
#
#     client.login(user)
#     response = client.json.patch(url, json.dumps(data))
#     assert response.status_code == 200
#     assert mocked_cognito.called


def test_update_user_responses_api(client, mocker):
    url = reverse("me-update-responses")
    user, mdlive_res, cognito_res = f.create_user_with_mocked_values()
    mocked_cognito = mocker.patch("beacon.cognito.services.Cognito")
    mocked_cognito.return_value = cognito_res
    mocked_mdlive_user_token = mocker.patch("beacon.mdlive.services.requests_post")
    mocked_mdlive_user_token.return_value = mdlive_res
    answers_f.create_user_response(
        chief_complaint1="Anxiety",
        how_often_depressed=1,
        user=user,
        response=[
            {
                "question": "Chief Complaint",
                "answer": "Anxiety",
                "text_mapped_value": "Anxiety",
                "user_appointment_attribute": None,
                "user_response_attribute": constants.CHIEF_COMPLAINT1,
            }
        ],
    )
    new_response = answers_f.create_user_response(
        chief_complaint1="Depression",
        how_often_depressed=2,
        user=None,
        response=[
            {
                "question": "Chief Complaint",
                "answer": "Depression",
                "text_mapped_value": "Depression",
                "user_appointment_attribute": None,
                "user_response_attribute": constants.CHIEF_COMPLAINT1,
            }
        ],
    )

    data = {"id": str(new_response.id)}

    # should require auth
    response = client.json.patch(url, data=json.dumps(data))
    assert response.status_code == 401

    client.login(user)
    response = client.json.patch(url, data=json.dumps(data))
    assert response.status_code == 200
    user_response = UserResponse.objects.filter(user=user).first()
    assert user_response.chief_complaint1 == "Depression"
