# -*- coding: utf-8 -*-
# Standard Library
import json
from unittest.mock import ANY

# Third Party Stuff
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

# beacon Stuff
from beacon.answers.tests import factories as answer_f
from beacon.organisations.tests import factories as organisation_f
from beacon.questionnaire.tests import factories as question_f
from beacon.scc import choices, constants, models
from beacon.scc import services as scc_services
from beacon.scc.tokens import generate_incoming_scc_auth_token
from beacon.users.tests import factories as user_f

from .test_data import scc_organisation_data, scc_user_data, scc_user_response_data
from .test_utils import get_data_in_bwb_format

pytestmark = pytest.mark.django_db

user_sync_request_data = {
    **scc_user_data,
    **scc_user_response_data,
    **scc_organisation_data,
}


@pytest.fixture(scope="function")
def mock_mdlive_and_cognito_sync(mocker):
    return mocker.patch("beacon.scc.services.sync_user_data_with_cognito_and_mdlive")


def test_user_sync_authentication_required(client, mocker):
    url = reverse("users-sync")
    data = user_sync_request_data
    user = user_f.create_user()
    mocked_sync_service = mocker.patch(
        "beacon.scc.api.services.process_user_sync_request"
    )
    mocked_sync_service.return_value = (user.id, None)

    # Authentication required
    response = client.json.post(url, data=json.dumps(data))
    assert response.status_code == 403

    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )
    assert response.status_code == 200


def test_new_user_sync(client, mocker, mock_mdlive_and_cognito_sync):
    mocked_cognito_register = mocker.patch(
        "beacon.users.services.cognito_services.register"
    )
    mocked_mdlive_get_user_token = mocker.patch(
        "beacon.users.services.mdlive_services.get_user_token"
    )
    mocked_mdlive_sync_timezone_task = mocker.patch(
        "beacon.users.services.mdlive_tasks.sync_user_timezone_with_mdlive_timezone_id_task.delay"
    )
    mocker.patch("beacon.scc.services.send_welcome_email_to_user")
    bwb_org_data = get_data_in_bwb_format(scc_data=scc_organisation_data)
    organisation_f.create_organisation(**bwb_org_data)

    cognito_user_response = {
        "UserConfirmed": False,
        "CodeDeliveryDetails": {
            "Destination": "t***@e***.com",
            "DeliveryMedium": "EMAIL",
            "AttributeName": "email",
        },
        "UserSub": "df4bd40d-11ed-4da8-8dca-6422e235e5cc",
    }

    mdlive_response = {
        "jwt": "dummy-jwt",
        "user": {"id": 11111, "type": "Patient", "time_to_live_minutes": 60},
    }

    mocked_cognito_register.return_value = cognito_user_response
    mocked_mdlive_get_user_token.return_value = mdlive_response

    data = user_sync_request_data.copy()
    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 200

    # Search users using DB id and Mdlive ID. Both should be same.
    user = (
        get_user_model()
        .objects.filter(mdlive_id=mdlive_response.get("user").get("id"))
        .first()
    )
    user_two = (
        get_user_model().objects.filter(id=cognito_user_response.get("UserSub")).first()
    )
    assert user.id is not None
    assert str(user.id) == str(user_two.id)
    assert user.source == get_user_model().SCC
    assert user.mdlive_id == 11111

    mocked_mdlive_get_user_token.assert_called()
    mocked_mdlive_sync_timezone_task.assert_called()
    mocked_cognito_register.assert_called()

    # Check all fields are set as per conversion layer output
    bwb_data = scc_services.convert_scc_data_into_bwb_format(scc_data=data)
    assert user.email == bwb_data.get("email")
    assert user.connects_mbr_id == bwb_data.get("connects_mbr_id")
    assert user.first_name == bwb_data.get("first_name")
    assert user.last_name == bwb_data.get("last_name")
    assert str(user.birthdate) == bwb_data.get("birthdate")
    assert user.gender == bwb_data.get("gender")
    assert user.address1 == bwb_data.get("address1")
    assert user.address2 == bwb_data.get("address2")
    assert user.city == bwb_data.get("city")
    assert user.state == bwb_data.get("state")
    assert user.zip == bwb_data.get("zip")
    assert user.phone == bwb_data.get("phone")
    assert user.relationship_status == bwb_data.get("relationship_status")
    assert user.employment_status == bwb_data.get("employment_status")
    assert user.job_title == bwb_data.get("job_title")
    assert user.organisation.parent_code == bwb_data.get("parent_code")
    assert user.organisation.group_number == bwb_data.get("group_number")
    assert user.organisation.benefit_package == bwb_data.get("benefit_package")
    assert user.answer.chief_complaint1 == bwb_data.get("chief_complaint1")
    assert user.answer.chief_complaint2 == bwb_data.get("chief_complaint2")
    assert user.answer.how_often_less_interest_in_things == bwb_data.get(
        "how_often_less_interest_in_things"
    )
    assert user.answer.how_often_depressed == bwb_data.get("how_often_depressed")
    assert user.answer.how_often_nervous == bwb_data.get("how_often_nervous")
    assert user.answer.how_often_worry == bwb_data.get("how_often_worry")
    assert user.answer.difficulty_in_keeping_drinking_limit == bwb_data.get(
        "difficulty_in_keeping_drinking_limit"
    )
    assert user.answer.felt_cut_down_drinking == bwb_data.get("felt_cut_down_drinking")
    assert user.answer.how_emotionally_doing == bwb_data.get("how_emotionally_doing")
    assert user.answer.how_physical_health == bwb_data.get("how_physical_health")
    assert user.answer.people_support == bwb_data.get("people_support")
    assert user.answer.comfortable_in_managing_finances == bwb_data.get(
        "comfortable_in_managing_finances"
    )
    assert user.answer.resources_to_manage == bwb_data.get("resources_to_manage")
    assert user.answer.number_of_days_missed_work == bwb_data.get(
        "number_of_days_missed_work"
    )
    assert user.answer.number_of_days_less_productive == bwb_data.get(
        "number_of_days_less_productive"
    )
    assert user.answer.response is not None
    assert user.answer.response_backup is None

    # New user is created on all Cognito, MDLive, and BWB system. No need to separately
    # sync again with MDLive and Cognito (in case of new user registration).
    mock_mdlive_and_cognito_sync.assert_not_called()

    # SCC API log generated for incoming request from SCC for new user registration
    scc_api_log = models.SccApiLog.objects.get(user=user)
    assert scc_api_log.status == choices.STATUS_CHOICES.SUCCESSFUL

    # No change diff exists in case of a new user registration
    assert scc_api_log.change_diff is None
    assert scc_api_log.request_direction == choices.REQUEST_DIRECTION_CHOICES.INCOMING
    assert scc_api_log.request.items() == data.items()
    assert "'message': 'User synced successfully'" in str(scc_api_log.response)


def test_existing_user_sync(client, mock_mdlive_and_cognito_sync):
    bwb_user_data = get_data_in_bwb_format(scc_data=scc_user_data)
    bwb_user_response_data = get_data_in_bwb_format(scc_data=scc_user_response_data)

    user = user_f.create_user(**bwb_user_data)
    answer_f.create_user_response(user=user, **bwb_user_response_data)
    assert user.answer.number_of_days_missed_work != 10
    assert user.job_title != "Professional"
    assert user.employment_status != "Part Time"
    assert user.relationship_status != "Married"
    assert user.mdlive_id is not None

    data = user_sync_request_data.copy()
    data["outcomesESDQuestion1"] = "10"
    data["jobTitle"] = "PROF"  # "Professional"
    data["employmentStatus"] = "PT"  # "Part time"
    data["relationshipStatus"] = "M"  # "Married"
    data["mdLiveMemberID"] = None

    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 200
    user.refresh_from_db()

    # Answer data is updated
    assert user.answer.number_of_days_missed_work == 10
    assert user.answer.response is not None

    # User `job_title`, `relationship_status`, and `employment_status` is updated.
    assert user.job_title == "Professional"
    assert user.employment_status == "Part Time"
    assert user.relationship_status == "Married"

    # MDLive ID is not updated
    assert user.mdlive_id is not None

    # SCC API log generated for incoming request from SCC to update existing user
    scc_api_log = models.SccApiLog.objects.get(user=user)
    assert scc_api_log.status == choices.STATUS_CHOICES.SUCCESSFUL
    assert scc_api_log.change_diff is not None
    assert scc_api_log.request_direction == choices.REQUEST_DIRECTION_CHOICES.INCOMING
    assert scc_api_log.request.items() == data.items()
    assert "'message': 'User synced successfully'" in str(scc_api_log.response)

    mock_mdlive_and_cognito_sync.assert_called()


def test_existing_user_sync_with_case_insensitive_values(
    client, mock_mdlive_and_cognito_sync
):
    bwb_user_data = get_data_in_bwb_format(scc_data=scc_user_data)
    bwb_user_response_data = get_data_in_bwb_format(scc_data=scc_user_response_data)

    user = user_f.create_user(**bwb_user_data)
    answer_f.create_user_response(user=user, **bwb_user_response_data)

    data = user_sync_request_data.copy()
    # Convert data values to uppercase for some fields
    for bwb_field in constants.FIND_CASE_INSENSITIVE_DISCREPANCY_FOR_FIELDS:
        scc_field = constants.BWB_TO_SCC_KEYS.get(bwb_field)
        if data[scc_field] and isinstance(data[scc_field], str):
            data[scc_field] = data[scc_field].upper()

    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    # No discrepancy error arrived as fields were matched case insensitively
    assert response.status_code == 200

    mock_mdlive_and_cognito_sync.assert_called()


def test_existing_user_sync_with_discrepancies(client, mock_mdlive_and_cognito_sync):
    bwb_user_data = get_data_in_bwb_format(scc_data=scc_user_data)
    bwb_user_response_data = get_data_in_bwb_format(scc_data=scc_user_response_data)

    user = user_f.create_user(**bwb_user_data)
    answer_f.create_user_response(user=user, **bwb_user_response_data)

    data = user_sync_request_data.copy()
    data["firstName"] = "New Name"

    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )
    assert response.status_code == 409
    assert response.data["error_type"] == "IntegrityError"
    assert len(response.data["errors"]) == 1
    mock_mdlive_and_cognito_sync.assert_not_called()


def test_discrepancy_error_return_upper_case_values_for_some_fields(
    client, mock_mdlive_and_cognito_sync
):
    bwb_user_data = get_data_in_bwb_format(scc_data=scc_user_data)
    bwb_user_response_data = get_data_in_bwb_format(scc_data=scc_user_response_data)

    bwb_user_data["first_name"] = "real first"
    bwb_user_data["last_name"] = "real last"
    bwb_user_data["address1"] = "real address1"
    bwb_user_data["address2"] = "real address2"
    bwb_user_data["city"] = "real city"
    user = user_f.create_user(**bwb_user_data)
    answer_f.create_user_response(user=user, **bwb_user_response_data)

    data = user_sync_request_data.copy()
    data["firstName"] = "test first"
    data["lastName"] = "test last"
    data["addressLine1"] = "test address1"
    data["addressLine2"] = "test address2"
    data["addressCity"] = "test city"

    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 409
    assert response.data["error_type"] == "IntegrityError"
    assert len(response.data["errors"]) == 1
    for scc_field in constants.RETURN_DISCREPANCY_IN_UPPERCASE_FOR_SCC_FIELDS:
        bwb_field = constants.SCC_TO_BWB_KEYS.get(scc_field)
        assert (
            response.data["errors"][0]["message"][scc_field]["bwb_value"]
            == bwb_user_data[bwb_field].upper()
        )
        assert (
            response.data["errors"][0]["message"][scc_field]["scc_value"]
            == data[scc_field].upper()
        )
    mock_mdlive_and_cognito_sync.assert_not_called()


def test_none_values_not_changing_to_string_in_discrepancies_msg(
    client, mock_mdlive_and_cognito_sync
):
    bwb_user_data = get_data_in_bwb_format(scc_data=scc_user_data)
    bwb_user_response_data = get_data_in_bwb_format(scc_data=scc_user_response_data)

    bwb_user_data["city"] = None
    user = user_f.create_user(**bwb_user_data)
    answer_f.create_user_response(user=user, **bwb_user_response_data)

    data = user_sync_request_data.copy()
    data["addressCity"] = "New City"

    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )
    assert response.status_code == 409
    assert response.data["error_type"] == "IntegrityError"
    assert len(response.data["errors"]) == 1
    assert response.data["errors"][0]["message"]["addressCity"]["bwb_value"] is None
    assert (
        str(response.data["errors"][0]["message"]["addressCity"]["scc_value"])
        == "NEW CITY"
    )
    mock_mdlive_and_cognito_sync.assert_not_called()


def test_existing_user_sync_match_with_multiple_users(
    client, mock_mdlive_and_cognito_sync
):
    bwb_user_data = get_data_in_bwb_format(scc_data=scc_user_data)
    bwb_user_response_data = get_data_in_bwb_format(scc_data=scc_user_response_data)

    user = user_f.create_user(**bwb_user_data)
    answer_f.create_user_response(user=user, **bwb_user_response_data)

    # Two other matching users
    user_f.create_user(connects_mbr_id=user.connects_mbr_id)
    user_f.create_user(mdlive_id=user.mdlive_id)

    data = user_sync_request_data.copy()

    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )
    assert response.status_code == 409
    assert response.data["error_type"] == "IntegrityError"
    assert len(response.data["errors"]) == 2
    mock_mdlive_and_cognito_sync.assert_not_called()


def test_user_sync_api_raises_error_if_missing_required_fields(
    client, mock_mdlive_and_cognito_sync
):
    url = reverse("users-sync")
    data = user_sync_request_data.copy()

    # Remove a required field
    data.pop("memberId")

    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 400
    assert response.data["error_type"] == "ValidationError"
    assert response.data["errors"][0]["field"] == "memberId"
    assert response.data["errors"][0]["message"] == "This field is required."
    mock_mdlive_and_cognito_sync.assert_not_called()


def test_user_sync_api_return_error_if_bwb_mapping_is_absent(
    client, mock_mdlive_and_cognito_sync
):
    url = reverse("users-sync")
    data = user_sync_request_data.copy()

    # Invalid value for which mapping doesn't exists
    data["gender"] = "ABCD"

    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 400
    assert response.data["error_type"] == "ValidationError"
    assert response.data["errors"][0]["field"] == "gender"
    assert "Mapping not found" in response.data["errors"][0]["message"]
    mock_mdlive_and_cognito_sync.assert_not_called()


def test_force_user_sync_authentication_required(
    client, mock_mdlive_and_cognito_sync, mocker
):
    user = user_f.create_user()
    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})
    data = user_sync_request_data

    mocked_sync_service = mocker.patch("beacon.scc.api.services.force_save_user_data")
    mocked_sync_service.return_value = {"diff": "test"}

    # Authentication required
    response = client.json.put(url, data=json.dumps(data))
    assert response.status_code == 403

    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )
    assert response.status_code == 200


def test_force_sync(client, mock_mdlive_and_cognito_sync):
    user = user_f.create_user(email="email@test.com")
    answer_f.create_user_response(user=user, number_of_days_missed_work=1)
    user.refresh_from_db()
    assert user.answer.number_of_days_missed_work == 1
    assert user.email == "email@test.com"

    user_force_sync_request_data = {
        "emailAddress": "changed_email@test.com",
        "outcomesESDQuestion1": "10",
    }
    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url,
        data=json.dumps(user_force_sync_request_data),
        **{"HTTP_AUTHORIZATION": f"Token {auth_token}"},
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.answer.number_of_days_missed_work == 10
    assert user.email == "changed_email@test.com"
    # User was created with API by default and only
    # force synced from SCC system.
    assert user.source == get_user_model().API

    bwb_data = get_data_in_bwb_format(user_force_sync_request_data)
    bwb_data.pop("number_of_days_missed_work")  # remove non user data
    data_to_send_to_mdlive_and_cognito = scc_services.add_missing_user_data(
        new_user_data=bwb_data,
        existing_user=user,
    )
    mock_mdlive_and_cognito_sync.assert_called_with(
        new_user_data=data_to_send_to_mdlive_and_cognito, user_id=str(user.id)
    )


def test_force_sync_has_all_fields_as_optional(client, mock_mdlive_and_cognito_sync):
    user = user_f.create_user(email="email@test.com")
    answer_f.create_user_response(user=user)
    user_force_sync_request_data = {}

    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url,
        data=json.dumps(user_force_sync_request_data),
        **{"HTTP_AUTHORIZATION": f"Token {auth_token}"},
    )
    assert response.status_code == 200
    mock_mdlive_and_cognito_sync.assert_called_with(
        new_user_data=ANY, user_id=str(user.id)
    )
    mock_mdlive_and_cognito_sync.assert_called()


def test_response_json_changed_and_backup_not_present_then_create_new_backup(
    client, mock_mdlive_and_cognito_sync
):
    old_response_json = {"dummy": "test"}
    # BWB question must exist for response JSON to build
    # SCC's outcomesESDQuestion1 == number_of_days_missed_work in BWB
    question_f.create_question_number_of_days_missed_work()
    # This will create a response JSON which will be different than "old_response_json"
    scc_data = {"outcomesESDQuestion1": "11"}

    user = user_f.create_user(email="email@test.com")
    answer = answer_f.create_user_response(
        user=user, response=old_response_json, response_backup=None
    )

    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url,
        data=json.dumps(scc_data),
        **{"HTTP_AUTHORIZATION": f"Token {auth_token}"},
    )
    assert response.status_code == 200

    answer.refresh_from_db()
    response_backup = answer.response_backup
    assert response_backup is not None
    assert len(response_backup) == 1
    assert str(old_response_json) in str(response_backup)
    mock_mdlive_and_cognito_sync.assert_called()


def test_response_json_changed_and_backup_present_then_add_data_to_older_backup(
    client, mock_mdlive_and_cognito_sync
):
    old_response_json = {"dummy": "example"}
    # BWB question must exist for response JSON to build
    # SCC's outcomesESDQuestion1 == number_of_days_missed_work in BWB
    question_f.create_question_number_of_days_missed_work()
    # This will create a response JSON which will be different than "old_response_json"
    scc_data = {"outcomesESDQuestion1": "11"}

    user = user_f.create_user(email="email@test.com")
    existing_backup = {"2021-12-08 20:05:50.175795": {"dummy": "test"}}
    answer = answer_f.create_user_response(
        user=user,
        response=old_response_json,
        response_backup=existing_backup,
    )

    assert len(answer.response_backup) == 1
    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url,
        data=json.dumps(scc_data),
        **{"HTTP_AUTHORIZATION": f"Token {auth_token}"},
    )
    assert response.status_code == 200

    answer.refresh_from_db()
    response_backup = answer.response_backup
    assert response_backup is not None
    assert len(response_backup) == 2
    assert str(old_response_json) in str(response_backup)
    assert existing_backup.items() <= response_backup.items()
    mock_mdlive_and_cognito_sync.assert_called()


def test_if_response_json_not_changed_then_do_not_create_backup(
    client, mock_mdlive_and_cognito_sync
):
    old_response_json = [
        {
            "question": "During the past 30 days, how many days did you miss from your job because of your behavioral health issues?",
            "answer": 11,
            "user_response_attribute": "number_of_days_missed_work",
            "user_appointment_attribute": None,
        }
    ]
    # BWB question must exist for response JSON to build
    # SCC's outcomesESDQuestion1 == number_of_days_missed_work in BWB
    question_f.create_question_number_of_days_missed_work()
    # This will create a response JSON which will be same as "old_response_json"
    scc_data = {"outcomesESDQuestion1": "11"}

    user = user_f.create_user(email="email@test.com")
    answer = answer_f.create_user_response(
        user=user,
        response=old_response_json,
        response_backup=None,
    )

    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url,
        data=json.dumps(scc_data),
        **{"HTTP_AUTHORIZATION": f"Token {auth_token}"},
    )
    assert response.status_code == 200

    answer.refresh_from_db()
    response_backup = answer.response_backup
    assert response_backup is None
    mock_mdlive_and_cognito_sync.assert_called()


def test_response_json_backup_gets_created_in_user_sync_api(
    client, mock_mdlive_and_cognito_sync
):
    old_response_json = {"dummy": "example"}
    # BWB question must exist for response JSON to build
    # SCC's outcomesESDQuestion1 == number_of_days_missed_work in BWB
    question_f.create_question_number_of_days_missed_work()

    bwb_user_data = get_data_in_bwb_format(scc_data=scc_user_data)
    bwb_user_response_data = get_data_in_bwb_format(scc_data=scc_user_response_data)

    user = user_f.create_user(**bwb_user_data)
    answer = answer_f.create_user_response(
        user=user,
        response=old_response_json,
        response_backup=None,
        **bwb_user_response_data,
    )

    data = user_sync_request_data.copy()
    data["outcomesESDQuestion1"] = "10"

    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.answer.number_of_days_missed_work == 10

    answer.refresh_from_db()
    assert answer.response is not None
    assert answer.response_backup is not None
    assert "number_of_days_missed_work" in str(answer.response)
    assert "10" in str(answer.response)
    assert str(old_response_json) in str(answer.response_backup)
    mock_mdlive_and_cognito_sync.assert_called()


def test_force_sync_does_not_update_mdlive_id_to_null(
    client, mock_mdlive_and_cognito_sync
):
    user = user_f.create_user(email="email@test.com", mdlive_id=12345)
    answer_f.create_user_response(user=user)
    data = {"mdLiveMemberID": None}

    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url,
        data=json.dumps(data),
        **{"HTTP_AUTHORIZATION": f"Token {auth_token}"},
    )

    assert response.status_code == 200
    mock_mdlive_and_cognito_sync.assert_called_with(
        new_user_data=ANY, user_id=str(user.id)
    )
    user.refresh_from_db()
    assert user.mdlive_id == 12345
    mock_mdlive_and_cognito_sync.assert_called()


def test_generate_failed_log_if_sync_api_fails_with_discrepancy_error(
    client, mock_mdlive_and_cognito_sync
):
    bwb_user_data = get_data_in_bwb_format(scc_data=scc_user_data)
    bwb_user_response_data = get_data_in_bwb_format(scc_data=scc_user_response_data)

    user = user_f.create_user(**bwb_user_data)
    answer_f.create_user_response(user=user, **bwb_user_response_data)

    data = user_sync_request_data.copy()
    # Add discrepancy in request data to enforce mismatch
    mismatch_value = "New Name"
    data["firstName"] = mismatch_value

    url = reverse("users-sync")
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )
    assert response.status_code == 409
    assert response.data["error_type"] == "IntegrityError"
    assert len(response.data["errors"]) == 1

    # SCC API log generated for incoming request from SCC in case discrepancy found
    scc_api_log = models.SccApiLog.objects.all().order_by("-created_at").first()
    assert scc_api_log.status == choices.STATUS_CHOICES.FAILED
    assert scc_api_log.change_diff is None
    assert scc_api_log.request_direction == choices.REQUEST_DIRECTION_CHOICES.INCOMING
    assert scc_api_log.request.items() == data.items()
    assert "firstName" in str(scc_api_log.response)
    assert f"{mismatch_value.upper()}" in str(scc_api_log.response)
    mock_mdlive_and_cognito_sync.assert_not_called()


def test_generate_failed_log_if_sync_api_fails_with_validation_error(client, mocker):
    user = user_f.create_user()
    url = reverse("users-sync")
    data = user_sync_request_data
    test_diff = {"diff": "test"}

    # Making data invalid
    invalid_value = "Not Valid"
    data["jobTitle"] = invalid_value

    mocked_sync_service = mocker.patch(
        "beacon.scc.api.services.process_user_sync_request"
    )
    mocked_sync_service.return_value = (user.id, test_diff)
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.post(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 400
    scc_api_log = models.SccApiLog.objects.all().order_by("-created_at").first()
    assert scc_api_log.user is None
    assert scc_api_log.status == choices.STATUS_CHOICES.FAILED
    assert scc_api_log.change_diff is None
    assert scc_api_log.request_direction == choices.REQUEST_DIRECTION_CHOICES.INCOMING
    assert scc_api_log.request.items() == data.items()
    assert "jobTitle" in str(scc_api_log.response)
    assert f"Invalid value. Mapping not found for value '{invalid_value}'" in str(
        scc_api_log.response
    )


def test_generate_success_log_if_force_sync_api_passes_old_user_updates(client, mocker):
    user = user_f.create_user()
    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})

    # Valid data
    data = {"jobTitle": "PROF"}
    test_diff = {"diff": "test"}

    mocked_sync_service = mocker.patch("beacon.scc.api.services.force_save_user_data")
    mocked_sync_service.return_value = test_diff
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 200
    scc_api_log = models.SccApiLog.objects.get(user=user)
    assert scc_api_log.status == choices.STATUS_CHOICES.SUCCESSFUL
    assert scc_api_log.change_diff == test_diff
    assert scc_api_log.request_direction == choices.REQUEST_DIRECTION_CHOICES.INCOMING
    assert scc_api_log.request.items() == data.items()
    assert "'message': 'User updated successfully'" in str(scc_api_log.response)


def test_generate_failed_log_if_force_sync_api_fails_with_validation_error(
    client, mocker
):
    user = user_f.create_user()
    url = reverse("users-force-sync", kwargs={"pk": str(user.id)})

    # Invalid data
    invalid_value = "Not Valid"
    data = {"jobTitle": invalid_value}
    test_diff = {"diff": "test"}

    mocked_sync_service = mocker.patch("beacon.scc.api.services.force_save_user_data")
    mocked_sync_service.return_value = test_diff
    auth_token = generate_incoming_scc_auth_token()
    response = client.json.put(
        url, data=json.dumps(data), **{"HTTP_AUTHORIZATION": f"Token {auth_token}"}
    )

    assert response.status_code == 400
    scc_api_log = models.SccApiLog.objects.get(user=user)
    assert scc_api_log.status == choices.STATUS_CHOICES.FAILED
    assert scc_api_log.change_diff is None
    assert scc_api_log.request_direction == choices.REQUEST_DIRECTION_CHOICES.INCOMING
    assert scc_api_log.request.items() == data.items()
    assert "jobTitle" in str(scc_api_log.response)
    assert f"Invalid value. Mapping not found for value '{invalid_value}'" in str(
        scc_api_log.response
    )
