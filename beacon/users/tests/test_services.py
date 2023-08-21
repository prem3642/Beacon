# -*- coding: utf-8 -*-

# Third Party Stuff
import pytest
from django.forms.models import model_to_dict

# beacon Stuff
from beacon.users import services

from . import factories

pytestmark = pytest.mark.django_db


def test_admin_updates_on_active_user_are_sent_to_cognito_and_mdlive(client, mocker):
    mocked_cognito = mocker.patch(
        "beacon.users.services.cognito_services.admin_update_profile"
    )
    mocked_mdlive = mocker.patch(
        "beacon.users.services.mdlive_services.get_mdlive_token_data_for_user"
    )
    user = factories.create_user(is_active=True)
    user_data = model_to_dict(user)

    # user data updates
    user_data["address1"] = "New Address 1"
    services.sync_user_data_with_cognito_and_mdlive(
        user_id=user.id, new_user_data=user_data
    )
    assert mocked_cognito.called
    assert mocked_mdlive.called


def test_admin_updates_on_inactive_user_are_sent_to_cognito_not_mdlive(client, mocker):
    mocked_cognito = mocker.patch(
        "beacon.users.services.cognito_services.admin_update_profile"
    )
    mocked_mdlive = mocker.patch(
        "beacon.users.services.mdlive_services.get_mdlive_token_data_for_user"
    )
    user = factories.create_user(is_active=False)
    user_data = model_to_dict(user)

    # user data updates
    user_data["address1"] = "New Address 1"
    services.sync_user_data_with_cognito_and_mdlive(
        user_id=user.id, new_user_data=user_data
    )
    assert mocked_cognito.called
    assert not mocked_mdlive.called


def test_activating_an_inactive_user_is_sent_to_cognito_and_mdlive(client, mocker):
    mocked_cognito = mocker.patch(
        "beacon.users.services.cognito_services.admin_update_profile"
    )
    mocked_mdlive = mocker.patch(
        "beacon.users.services.mdlive_services.get_mdlive_token_data_for_user"
    )
    user = factories.create_user(is_active=False)
    user_data = model_to_dict(user)

    # user data updates
    user_data["is_active"] = True
    services.sync_user_data_with_cognito_and_mdlive(
        user_id=user.id, new_user_data=user_data
    )
    assert mocked_cognito.called
    assert mocked_mdlive.called
