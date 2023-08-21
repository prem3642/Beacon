# -*- coding: utf-8 -*-

# Standard Library
import json
from unittest.mock import Mock

# Third Party Stuff
import pytest
from django.conf import settings

# beacon Stuff
from beacon.users.tests import factories as users_f

from .. import services, tasks

pytestmark = pytest.mark.django_db


def test_sync_timezone_id_with_mdlive_if_different(client, mocker):
    mocked_requests_get = mocker.patch("beacon.mdlive.services.requests_get")
    mocked_requests_patch = mocker.patch("beacon.mdlive.services.requests_patch")
    response_content = {"patient_profile": {"us_time_zone_id": 1}}
    mocked_response = Mock(
        status_code=200,
        content=b'{"patient_profile": {"us_time_zone_id": 1}}',
    )
    mocked_response.json.return_value = response_content
    mocked_requests_get.return_value = mocked_response
    mocked_requests_patch.return_value = mocked_response

    user = users_f.create_user(
        # Eastern Standard Time (EST) == MDLive's "us_time_zone_id": 1
        timezone="America/New_York"
    )

    patient_id = user.mdlive_id
    md_live_token = "fake-token"
    timezone_id_to_update = 12  # Arizona Time (AZT)

    tasks.sync_user_timezone_with_mdlive_timezone_id_task(
        patient_id=user.mdlive_id,
        timezone_id=timezone_id_to_update,
        token=md_live_token,
    )

    url = f"{settings.MDLIVE_URL}/api/v2/patients/{patient_id}"
    request_headers = services.get_mdlive_headers(token=md_live_token)
    patch_request_data = json.dumps(
        {"patient": {"us_time_zone_id": timezone_id_to_update}}
    )

    mocked_requests_get.assert_called_with(url=url, headers=request_headers)
    # Since AZT and EST are different, MDLive's PATCH API will be called to
    # update patient on MDLive.
    request_headers.update({"Accept": "application/json"})
    mocked_requests_patch.assert_called_with(
        url=url,
        headers=request_headers,
        data=patch_request_data,
    )


def test_do_not_sync_timezone_id_with_mdlive_if_same(client, mocker):
    mocked_requests_get = mocker.patch("beacon.mdlive.services.requests_get")
    mocked_requests_patch = mocker.patch("beacon.mdlive.services.requests_patch")
    response_content = {"patient_profile": {"us_time_zone_id": 1}}
    mocked_response = Mock(
        status_code=200,
        content=b'{"patient_profile": {"us_time_zone_id": 1}}',
    )
    mocked_response.json.return_value = response_content
    mocked_requests_get.return_value = mocked_response
    mocked_requests_patch.return_value = mocked_response

    user = users_f.create_user(
        # Eastern Standard Time (EST) == `us_time_zone_id: 1`
        timezone="America/New_York"
    )

    patient_id = user.mdlive_id
    md_live_token = "fake-token"
    timezone_id_to_update = 1

    tasks.sync_user_timezone_with_mdlive_timezone_id_task(
        patient_id=user.mdlive_id,
        timezone_id=timezone_id_to_update,
        token=md_live_token,
    )

    url = f"{settings.MDLIVE_URL}/api/v2/patients/{patient_id}"
    request_headers = services.get_mdlive_headers(token=md_live_token)

    mocked_requests_get.assert_called_with(url=url, headers=request_headers)
    # Since timezone ID to update is same `1`, so no need to update on MDLive
    mocked_requests_patch.assert_not_called()
