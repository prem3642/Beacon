# -*- coding: utf-8 -*-
# Third Party Stuff
import pytest
from rest_framework.exceptions import ValidationError

from beacon.answers.tests import factories as answer_f
from beacon.organisations.tests import factories as organisation_f

# beacon Stuff
from beacon.scc import services as scc_services
from beacon.users.tests import factories as user_f

from . import test_data
from .test_utils import generate_test_data, get_data_in_bwb_format

pytestmark = pytest.mark.django_db

user_sync_request_data = {
    **test_data.scc_user_data,
    **test_data.scc_user_response_data,
    **test_data.scc_organisation_data,
}


# Conversion test from SCC to BWB data
def test_error_raised_on_invalid_scc_phone_number():
    # Invalid phone number
    scc_invalid_phone_data = test_data.scc_test_data_invalid_phone
    with pytest.raises(ValidationError) as exc_case_1:
        scc_services.convert_scc_data_into_bwb_format(scc_invalid_phone_data)

    assert exc_case_1.typename == "ValidationError"
    assert "Invalid phone number" in str(exc_case_1.value.detail[0])

    # Valid but partial phone number
    scc_partial_phone_data = test_data.scc_normal_data.copy()
    scc_partial_phone_data.pop("phoneNumberCentralOfficeCode")
    with pytest.raises(ValidationError) as exc_case_2:
        scc_services.convert_scc_data_into_bwb_format(scc_partial_phone_data)

    assert exc_case_2.typename == "ValidationError"
    assert "Invalid phone number" in str(exc_case_2.value.detail[0])


def test_conversion_outcome_esd_questions_scc_to_bwb():
    data = {
        "outcomesESDQuestion1": "SAH",
        "outcomesESDQuestion2": "5",
    }

    result = scc_services.convert_scc_data_into_bwb_format(data)

    assert result["number_of_days_missed_work"] is None
    assert result["number_of_days_less_productive"] == 5


def test_conversion_normal_scc_data_to_bwb():
    scc_data = test_data.scc_normal_data
    expected_bwb_data = test_data.bwb_normal_data

    actual_bwb_data = scc_services.convert_scc_data_into_bwb_format(scc_data)

    assert expected_bwb_data == actual_bwb_data


def test_conversion_lower_bound_scc_data_to_bwb():
    scc_data = test_data.scc_lower_bound_data
    expected_bwb_data = test_data.bwb_lower_bound_data

    actual_bwb_data = scc_services.convert_scc_data_into_bwb_format(scc_data)

    assert expected_bwb_data == actual_bwb_data


def test_conversion_upper_bound_scc_data_to_bwb():
    scc_data = test_data.scc_upper_bound_data
    expected_bwb_data = test_data.bwb_upper_bound_data

    actual_bwb_data = scc_services.convert_scc_data_into_bwb_format(scc_data)

    assert expected_bwb_data == actual_bwb_data


def test_conversion_partial_scc_data_to_bwb():
    scc_data = test_data.scc_partial_data
    expected_bwb_data = test_data.bwb_partial_data

    actual_bwb_data = scc_services.convert_scc_data_into_bwb_format(scc_data)

    assert expected_bwb_data == actual_bwb_data


def test_error_raised_on_invalid_birthdate():
    scc_data_invalid_dob = test_data.scc_test_data_invalid_dob

    with pytest.raises(ValidationError) as exc:
        scc_services.convert_scc_data_into_bwb_format(scc_data_invalid_dob)

    assert exc.typename == "ValidationError"
    assert "Invalid IBM date format (CYYMMDD)." in str(exc.value.detail[0])


# Test conversion from BWB to SCC data
def test_generate_scc_user_registration_request():
    bwb_organisation_data = get_data_in_bwb_format(test_data.scc_organisation_data)
    organisation = organisation_f.create_organisation(
        number_of_sessions=4, **bwb_organisation_data
    )

    bwb_user_data = get_data_in_bwb_format(test_data.scc_user_data)
    user = user_f.create_user(organisation=organisation, **bwb_user_data)

    bwb_answers = get_data_in_bwb_format(test_data.scc_user_response_data)
    answer_f.create_user_response(user=user, **bwb_answers)

    scc_request_body = scc_services.generate_scc_user_registration_request(user=user)

    date_of_birth = scc_request_body.pop("dateOfBirth")
    assert date_of_birth == str(user.birthdate)

    date_registered = scc_request_body.pop("dateRegistered")
    assert date_registered == str(user.date_joined.date().strftime("%Y-%m-%d"))

    time_registered = scc_request_body.pop("timeRegistered")
    assert time_registered == str(user.date_joined.time().strftime("%H:%M:%S"))

    # Asymmetric mapping (SCC's "foo" converts to BWB's "bar", but BWB's "bar" doesn't always converts to SCC's "foo")
    # Such asymmetric mapping are checked outside loop.
    assert 4 == scc_request_body.pop("requestedUnits")
    assert "03" == scc_request_body.pop("outcomesESDQuestion1")
    assert "03" == scc_request_body.pop("outcomesESDQuestion2")

    for key, value in scc_request_body.items():
        assert value == user_sync_request_data.get(key)


def test_conversion_normal_bwb_data_to_scc():
    bwb_organisation_data = generate_test_data(
        keys=test_data.bwb_organisation_keys, values=test_data.bwb_normal_data
    )
    organisation = organisation_f.create_organisation(
        number_of_sessions=4, **bwb_organisation_data
    )

    bwb_user_data = generate_test_data(
        keys=test_data.bwb_user_data_keys, values=test_data.bwb_normal_data
    )
    user = user_f.create_user(organisation=organisation, **bwb_user_data)

    bwb_answers = generate_test_data(
        keys=test_data.bwb_user_response_keys, values=test_data.bwb_normal_data
    )
    answer_f.create_user_response(user=user, **bwb_answers)

    scc_request_body = scc_services.generate_scc_user_registration_request(user=user)

    date_of_birth = scc_request_body.pop("dateOfBirth")
    assert date_of_birth == str(user.birthdate)

    date_registered = scc_request_body.pop("dateRegistered")
    assert date_registered == str(user.date_joined.date().strftime("%Y-%m-%d"))

    time_registered = scc_request_body.pop("timeRegistered")
    assert time_registered == str(user.date_joined.time().strftime("%H:%M:%S"))

    requested_units = scc_request_body.pop("requestedUnits")
    assert requested_units == 4

    for key, value in scc_request_body.items():
        assert value == test_data.scc_normal_data.get(key)


def test_conversion_lower_bound_bwb_data_to_scc():
    bwb_organisation_data = generate_test_data(
        keys=test_data.bwb_organisation_keys, values=test_data.bwb_lower_bound_data
    )
    organisation = organisation_f.create_organisation(
        number_of_sessions=4, **bwb_organisation_data
    )

    bwb_user_data = generate_test_data(
        keys=test_data.bwb_user_data_keys, values=test_data.bwb_lower_bound_data
    )
    user = user_f.create_user(organisation=organisation, **bwb_user_data)

    bwb_answers = generate_test_data(
        keys=test_data.bwb_user_response_keys, values=test_data.bwb_lower_bound_data
    )
    answer_f.create_user_response(user=user, **bwb_answers)

    scc_request_body = scc_services.generate_scc_user_registration_request(user=user)

    date_of_birth = scc_request_body.pop("dateOfBirth")
    assert date_of_birth == str(user.birthdate)

    date_registered = scc_request_body.pop("dateRegistered")
    assert date_registered == str(user.date_joined.date().strftime("%Y-%m-%d"))

    time_registered = scc_request_body.pop("timeRegistered")
    assert time_registered == str(user.date_joined.time().strftime("%H:%M:%S"))

    requested_units = scc_request_body.pop("requestedUnits")
    assert requested_units == 4

    # Asymmetric mapping (SCC's "foo" converts to BWB's "bar", but BWB's "bar" doesn't always converts to SCC's "foo")
    # Such asymmetric mapping are checked outside loop.
    assert scc_request_body.pop("primaryPresentingProblem") == "ST"
    assert scc_request_body.pop("outcomesESDQuestion1") is None
    assert scc_request_body.pop("outcomesESDQuestion2") is None

    for key, value in scc_request_body.items():
        assert value == test_data.scc_lower_bound_data.get(key)


def test_conversion_upper_bound_bwb_data_to_scc():
    bwb_organisation_data = generate_test_data(
        keys=test_data.bwb_organisation_keys, values=test_data.bwb_upper_bound_data
    )
    organisation = organisation_f.create_organisation(
        number_of_sessions=4, **bwb_organisation_data
    )

    bwb_user_data = generate_test_data(
        keys=test_data.bwb_user_data_keys, values=test_data.bwb_upper_bound_data
    )
    user = user_f.create_user(organisation=organisation, **bwb_user_data)

    bwb_answers = generate_test_data(
        keys=test_data.bwb_user_response_keys, values=test_data.bwb_upper_bound_data
    )
    answer_f.create_user_response(user=user, **bwb_answers)

    scc_request_body = scc_services.generate_scc_user_registration_request(user=user)

    date_of_birth = scc_request_body.pop("dateOfBirth")
    assert date_of_birth == str(user.birthdate)

    date_registered = scc_request_body.pop("dateRegistered")
    assert date_registered == str(user.date_joined.date().strftime("%Y-%m-%d"))

    time_registered = scc_request_body.pop("timeRegistered")
    assert time_registered == str(user.date_joined.time().strftime("%H:%M:%S"))

    requested_units = scc_request_body.pop("requestedUnits")
    assert requested_units == 4

    # Asymmetric mapping (SCC's "foo" converts to BWB's "bar", but BWB's "bar" doesn't always converts to SCC's "foo")
    # Such asymmetric mapping are checked outside loop.
    assert scc_request_body.pop("primaryPresentingProblem") == "ST"
    assert scc_request_body.pop("outcomesESDQuestion1") is None
    assert scc_request_body.pop("outcomesESDQuestion2") is None
    assert scc_request_body.pop("employmentStatus") is None

    for key, value in scc_request_body.items():
        assert value == test_data.scc_upper_bound_data.get(key)
