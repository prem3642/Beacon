# -*- coding: utf-8 -*-
# Standard Library
import json

# Third Party Stuff
import pytest
from django.urls import reverse

# beacon Stuff
from beacon.answers import constants
from beacon.answers.models import UserAppointment, UserResponse
from beacon.questionnaire.models import Question
from beacon.questionnaire.tests import factories as questionnaire_f
from beacon.users.tests import factories as users_f

from . import factories as f

pytestmark = pytest.mark.django_db


def test_create_answer(client):
    url = reverse("answers-list")
    question = questionnaire_f.create_question(kind=Question.DROPDOWN)
    option1 = questionnaire_f.create_option(text="option 1", question=question)
    option2 = questionnaire_f.create_option(text="option 2")

    data = {"response": [{"question": str(question.id), "answer": option2.text}]}

    # Option not linked with provided question
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 400

    data["response"][0]["answer"] = option1.text
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 201
    expected_keys = [
        "id",
        "response",
        "mdlive_provider_id",
        "selected_time_slot",
        "appointment_method",
        "last_answered_question",
        "answer_token",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("response")[0].get("question") == question.text
    assert response.data.get("response")[0].get("answer") == option1.text


def test_add_answer(client):
    create_url = reverse("answers-list")
    question = questionnaire_f.create_question(kind=Question.DROPDOWN)
    question2 = questionnaire_f.create_question(
        kind=Question.NUMBER, min_length=1, max_length=50
    )
    option = questionnaire_f.create_option(text="option 1", question=question)

    data = {"response": [{"question": str(question.id), "answer": option.text}]}
    response = client.json.post(create_url, data=json.dumps(data))
    assert response.status_code == 201
    answer_token = response.data.get("answer_token")

    data = {"response": {"question": str(question2.id), "answer": 12}}
    url = reverse("answers-add-answer", kwargs={"pk": response.data.get("id")})
    # Answer auth required
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 403

    response = client.json.post(
        url, data=json.dumps(data), HTTP_AUTHORIZATION="Token {}".format(answer_token)
    )
    assert response.status_code == 200


def test_create_answer_multiple_questions(client):
    create_url = reverse("answers-list")
    question = questionnaire_f.create_question(
        kind=Question.MULTIPLE_QUESTIONS,
        user_appointment_attribute=constants.F2F_GENDER_PREFERENCE,
        next_question=None,
        previous_question=None,
        nested_question=None,
        leader_question=None,
        user_response_attribute=None,
    )
    question1 = questionnaire_f.create_question(
        kind=Question.DROPDOWN,
        leader_question=question,
        user_appointment_attribute=constants.F2F_COMFORTABLE_LANGUAGE,
        next_question=None,
        previous_question=None,
        nested_question=None,
        user_response_attribute=None,
    )
    question2 = questionnaire_f.create_question(
        kind=Question.NUMBER,
        min_length=1,
        max_length=50,
        leader_question=question,
        user_appointment_attribute=constants.F2F_PREFERRED_CONTACT,
        next_question=None,
        previous_question=None,
        nested_question=None,
        user_response_attribute=None,
    )
    option = questionnaire_f.create_option(
        text="option 1", question=question1, text_mapped_value=None
    )

    data = {
        "response": [
            {
                "question": str(question.id),
                "answer": None,
                "multiple_questions_response": [
                    {"question": str(question1.id), "answer": option.text},
                    {"question": str(question2.id), "answer": 10},
                ],
            }
        ]
    }
    response = client.json.post(create_url, data=json.dumps(data))
    assert response.status_code == 201
    user_response = UserResponse.objects.all().first()
    assert user_response is not None
    user_appointment = user_response.appointments.first()
    assert user_appointment is not None
    assert user_appointment.f2f_comfortable_language == option.text
    assert user_appointment.f2f_preferred_contact == "10"


def test_update_answer(client):
    create_url = reverse("answers-list")
    question = questionnaire_f.create_question(
        kind=Question.DROPDOWN, user_response_attribute=constants.CHIEF_COMPLAINT1
    )
    option = questionnaire_f.create_option(
        text="option 1", text_mapped_value="option 1", question=question
    )
    option2 = questionnaire_f.create_option(
        text="option 2", text_mapped_value="option 2", question=question
    )

    user_response = UserResponse.objects.all().first()
    assert user_response is None

    data = {"response": [{"question": str(question.id), "answer": option.text}]}
    response = client.json.post(create_url, data=json.dumps(data))
    assert response.status_code == 201
    user_response = UserResponse.objects.all().first()
    assert user_response is not None
    assert user_response.chief_complaint1 == option.text

    answer_token = response.data.get("answer_token")

    data = {"response": {"question": str(question.id), "answer": option2.text}}
    url = reverse(
        "answers-add-or-update-answer", kwargs={"pk": response.data.get("id")}
    )
    # Answer auth required
    response = client.json.patch(url, data=json.dumps(data))
    assert response.status_code == 403

    response = client.json.patch(
        url, data=json.dumps(data), HTTP_AUTHORIZATION="Token {}".format(answer_token)
    )
    assert response.status_code == 200
    user_response = UserResponse.objects.all().first()
    assert user_response is not None
    assert user_response.chief_complaint1 == option2.text


def test_update_answer_f2f_zip(client):
    create_url = reverse("answers-list")
    question = questionnaire_f.create_question(
        kind=Question.REGEX,
        text="Zip",
        placeholder="Zip",
        max_length=10,
        min_length=5,
        user_appointment_attribute=constants.F2F_ZIP,
        regex=r"^\d{5}(?:-\d{4})?$",
        regex_error_message="Enter a zip code in the format XXXXX or XXXXX-XXXX.",
    )

    user_response = UserResponse.objects.all().first()
    assert user_response is None

    data = {"response": [{"question": str(question.id), "answer": "33033"}]}
    response = client.json.post(create_url, data=json.dumps(data))
    assert response.status_code == 201
    user_response = UserResponse.objects.all().first()
    assert user_response is not None
    assert user_response.response[0]["user_appointment_attribute"] == constants.F2F_ZIP

    answer_token = response.data.get("answer_token")

    data = {"response": {"question": str(question.id), "answer": "330334330344"}}
    url = reverse(
        "answers-add-or-update-answer", kwargs={"pk": response.data.get("id")}
    )
    # Answer auth required
    response = client.json.patch(url, data=json.dumps(data))
    assert response.status_code == 403

    response = client.json.patch(
        url, data=json.dumps(data), HTTP_AUTHORIZATION="Token {}".format(answer_token)
    )
    assert response.status_code == 400
    assert (
        response.data["errors"][0]["message"]
        == f"Length of response should be minimum 10 characters for question id {question.id}"
    )

    data = {"response": {"question": str(question.id), "answer": "3303343303"}}
    response = client.json.patch(
        url, data=json.dumps(data), HTTP_AUTHORIZATION="Token {}".format(answer_token)
    )
    assert response.status_code == 400
    assert (
        response.data["errors"][0]["message"]
        == "Enter a zip code in the format XXXXX or XXXXX-XXXX."
    )

    data = {"response": {"question": str(question.id), "answer": "33033-3303"}}
    response = client.json.patch(
        url, data=json.dumps(data), HTTP_AUTHORIZATION="Token {}".format(answer_token)
    )
    assert response.status_code == 200
    user_response = UserResponse.objects.all().first()
    assert user_response is not None
    assert user_response.response[0]["user_appointment_attribute"] == constants.F2F_ZIP
    assert user_response.response[0]["answer"] == "33033-3303"


def test_extend_token(client):
    url = reverse("answers-extend-token")
    create_url = reverse("answers-list")
    question = questionnaire_f.create_question(kind=Question.DROPDOWN)
    option = questionnaire_f.create_option(text="option 1", question=question)

    data = {"response": [{"question": str(question.id), "answer": option.text}]}
    response = client.json.post(create_url, data=json.dumps(data))
    assert response.status_code == 201
    answer_token = response.data.get("answer_token")

    # should require auth
    response = client.json.post(url)
    assert response.status_code == 403

    response = client.json.post(url, HTTP_AUTHORIZATION="Token {}".format(answer_token))
    expected_keys = ["answer_token"]
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data.keys())


def test_create_appointment(client):
    url = reverse("appointments-list")
    user, _, _ = users_f.create_user_with_mocked_values()
    f.create_user_response(user=user)
    question = questionnaire_f.create_question(
        kind=Question.TEXT,
        user_response_attribute=None,
        user_appointment_attribute=constants.APPOINTMENT_METHOD,
    )

    data = {
        "response": [
            {"question": str(question.id), "answer": UserAppointment.FACE_TO_FACE}
        ]
    }

    # Authentication required
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 401

    client.login(user)
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 201
    expected_keys = [
        "id",
        "response",
        "mdlive_provider_id",
        "selected_time_slot",
        "last_answered_question",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("response")[0].get("question") == question.text
    assert (
        response.data.get("response")[0].get("answer") == UserAppointment.FACE_TO_FACE
    )


def test_update_appointment(client):
    user, _, _ = users_f.create_user_with_mocked_values()
    user_response = f.create_user_response(user=user, response=[])
    appointment = f.create_user_appointment(user_response=user_response, response=[])
    url = reverse("appointments-detail", kwargs={"pk": str(appointment.id)})
    question = questionnaire_f.create_question(
        kind=Question.TEXT,
        user_response_attribute=None,
        user_appointment_attribute=constants.F2F_GENDER_PREFERENCE,
    )
    questionnaire_f.create_option(text="Male", text_mapped_value="M", question=question)
    questionnaire_f.create_option(
        text="Female", text_mapped_value="F", question=question
    )

    data = {"response": {"question": str(question.id), "answer": "Male"}}

    # Authentication required
    response = client.json.patch(url, data=json.dumps(data))
    assert response.status_code == 401

    client.login(user=user)
    response = client.json.patch(url, data=json.dumps(data))
    assert response.status_code == 200
    expected_keys = [
        "id",
        "response",
        "mdlive_provider_id",
        "selected_time_slot",
        "last_answered_question",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("response")[-1].get("question") == question.text
    assert response.data.get("response")[-1].get("answer") == "Male"


def test_finalize_appointment(client, mocker):
    user, _, _ = users_f.create_user_with_mocked_values()
    user_response = f.create_user_response(
        user=user, response=[], appointment_state="FL"
    )
    appointment = f.create_user_appointment(
        user_response=user_response,
        response=[],
        appointment_method=UserAppointment.FACE_TO_FACE,
    )
    url = reverse("appointments-finalize", kwargs={"pk": str(appointment.id)})

    patched_bwb_server = mocker.patch(
        "beacon.users.services.send_f2f_data_to_bwb_server"
    )
    patched_scc_server = mocker.patch(
        "beacon.answers.api.send_user_data_to_scc_if_non_f2f"
    )
    patched_email = mocker.patch("beacon.users.utils.send_mail")

    # Authentication required
    response = client.json.post(url)
    assert response.status_code == 401

    client.login(user=user)
    response = client.json.post(url)
    appointment.refresh_from_db()
    assert appointment.appointment_state == "FL"
    assert response.status_code == 200
    assert patched_bwb_server.called
    assert patched_email.called
    patched_scc_server.assert_called_with(
        user=user, appointment_method=appointment.appointment_method
    )


def test_get_latest_appointment(client, mocker):
    user, _, cognito_res = users_f.create_user_with_mocked_values()
    user_response = f.create_user_response(user=user, response=[])
    appointment = f.create_user_appointment(
        user_response=user_response,
        response=[],
        appointment_method=UserAppointment.FACE_TO_FACE,
        bwb_inquiry_id="1111-1234",
    )
    url = reverse("appointments-latest")

    # Authentication required
    response = client.json.get(url)
    assert response.status_code == 401

    client.login(user=user)
    expected_keys = [
        "id",
        "appointment_method",
        "mdlive_provider_id",
        "selected_time_slot",
        "show_homepage_message",
        "bwb_inquiry_id",
        "created_at",
        "modified_at",
    ]
    response = client.json.get(url)
    assert response.status_code == 200
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("id") == str(appointment.id)
    assert response.data.get("show_homepage_message") is True
    assert response.data.get("bwb_inquiry_id") == "1111-1234"
