# -*- coding: utf-8 -*-
# Standard Libraries
from unittest.mock import ANY, Mock

# Third Party Stuff
import pytest
import requests

# beacon Stuff
from beacon.answers.models import UserAppointment
from beacon.answers.tests import factories as answer_f
from beacon.base.exceptions import CeleryTaskFailed
from beacon.organisations.tests import factories as organization_f
from beacon.users.tests import factories as user_f

from .. import choices, services
from ..models import SccApiLog
from ..tasks import send_user_data_to_scc_task

pytestmark = pytest.mark.django_db


def test_scc_api_log_create_services():
    user = user_f.create_user()
    request_data = {"request": "new"}
    response_data = {"response": "ok"}
    change_diff = {"changes": "test"}

    success_log = services.create_scc_api_log(
        user_id=str(user.id),
        request=request_data,
        response=response_data,
        is_successful=True,
        is_incoming=True,
        change_diff=change_diff,
    )
    assert success_log.status == choices.STATUS_CHOICES.SUCCESSFUL
    assert success_log.request == request_data
    assert success_log.response == response_data
    assert success_log.change_diff == change_diff
    assert success_log.request_direction == choices.REQUEST_DIRECTION_CHOICES.INCOMING

    failed_log = services.create_scc_api_log(
        user_id=str(user.id),
        request=request_data,
        response=response_data,
        is_successful=False,
        is_incoming=False,
        change_diff=None,
    )
    assert failed_log.status == choices.STATUS_CHOICES.FAILED
    assert failed_log.request == request_data
    assert failed_log.response == response_data
    assert failed_log.change_diff is None
    assert failed_log.request_direction == choices.REQUEST_DIRECTION_CHOICES.OUTGOING


def test_send_user_data_to_scc_if_non_f2f(mocker):
    organisation = organization_f.create_organisation()
    user = user_f.create_user(organisation=organisation, send_to_scc_if_non_f2f=True)
    answer_f.create_user_response(user=user)
    patched_celery_task = mocker.patch(
        "beacon.scc.services.send_user_data_to_scc_task.delay"
    )

    # If appointment is F2F, then do not call the celery task to send data to scc
    services.send_user_data_to_scc_if_non_f2f(
        user=user, appointment_method=UserAppointment.FACE_TO_FACE
    )
    assert user.send_to_scc_if_non_f2f is False
    patched_celery_task.assert_not_called()

    user.send_to_scc_if_non_f2f = True
    user.save()

    # If appointment is non F2F, then the celery task to send data to scc is called
    services.send_user_data_to_scc_if_non_f2f(
        user=user, appointment_method=UserAppointment.PHONE
    )
    assert user.send_to_scc_if_non_f2f is False
    patched_celery_task.assert_called_with(user_id=str(user.id), request=ANY)


def test_celery_task_to_send_data_to_scc_if_api_passes(mocker):
    user = user_f.create_user()
    request = {"request": "test"}
    response = {"memberId": "1111"}

    patched_request = mocker.patch("beacon.scc.scc_api.requests.request")
    patched_response = Mock()
    patched_response.json.return_value = response
    patched_request.return_value = patched_response

    send_user_data_to_scc_task(user_id=str(user.id), request=request)
    scc_api_log = SccApiLog.objects.filter(user=user).first()

    patched_request.assert_called_with(
        "POST", ANY, headers=ANY, json=request, verify=ANY
    )
    assert scc_api_log.status == choices.STATUS_CHOICES.SUCCESSFUL
    assert scc_api_log.request == request
    assert scc_api_log.response == response


def test_celery_task_to_send_data_to_scc_if_api_fails(mocker):
    user = user_f.create_user()
    request = {"request": "test"}
    patched_request = mocker.patch("beacon.scc.scc_api.requests.request")
    error_msg = "ErrorMessage"
    error = requests.RequestException()
    setattr(error, "response", requests.Response())
    setattr(error.response, "json", lambda: error_msg)
    patched_request.side_effect = error

    with pytest.raises(CeleryTaskFailed) as exc:
        send_user_data_to_scc_task(user_id=str(user.id), request=request)

    assert "Error received from SCC" in str(exc.value)
    assert error_msg in str(exc.value)
    scc_api_log = SccApiLog.objects.filter(user=user).first()

    patched_request.assert_called_with(
        "POST", ANY, headers=ANY, json=request, verify=ANY
    )
    assert scc_api_log.status == choices.STATUS_CHOICES.FAILED
    assert scc_api_log.request == request
    assert error_msg in str(scc_api_log.response)
