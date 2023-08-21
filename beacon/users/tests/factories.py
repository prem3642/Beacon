# -*- coding: utf-8 -*-
# Standard Library
import json
from collections import namedtuple
from datetime import datetime

# Third Party Stuff
import pytest
from django.contrib.auth import get_user_model
from django_dynamic_fixture import G

# beacon Stuff
from beacon.cognito.tests import factories as cognito_f

USER = get_user_model()


def create_user(**kwargs):
    if not kwargs.get("birthdate"):
        kwargs["birthdate"] = datetime(1944, 1, 1)
    if not kwargs.get("mdlive_id"):
        kwargs["mdlive_id"] = 123456
    user = G(USER, **kwargs)
    user.set_password(kwargs.get("password", "test"))
    user.save()
    return user


def create_user_with_mocked_values(data=None, mdlive_res_data=None):
    if data is None:
        data = {
            "first_name": "User",
            "last_name": "Test",
            "gender": "M",
            "birthdate": "1988-06-21",  # Format for mdlive
            "phone": "8888888888",
            "email": "user@example.com",
            "address1": "Address line 1",
            "address2": "Address line 2",
            "city": "the Hague",
            "state": "AZ",
            "zip": "12345",
            # 'relationship': 'Self',
            "relationship_status": "Never Married",
            "employment_status": "Part Time",
            "job_title": "Professional",
            "password": "TestUser01",
            "agrees_to_mdlive_informed_consent": True,
            "agrees_to_beacon_privacy_notice": True,
            "agrees_to_mdlive_privacy_agreement": True,
            "mdlive_consent_user_initials": "ut",
            "appointment_state": "Puerto Rico",
        }
    if mdlive_res_data is None:
        mdlive_res_data = dict(
            jwt="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjUyLCJ1c2VybmFtZSI6ImRlbW9wYXRpZW50MSIsInByaW",
            user=dict(id=52, type="Patient", time_to_live_minutes=60),
        )
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    mdlive_res = mdlive_response(200, json.dumps(mdlive_res_data))
    user = create_user(
        email=data.get("email"),
        password=data.get("password"),
        first_name="User",
        last_name="Test",
        gender="M",
        birthdate="1988-06-21",  # Format for mdlive
        phone="8888888888",
        address1="Address line 1",
        address2="Address line 2",
        city="the Hague",
        state="AZ",
        zip="12345",
        # relationship="Self",
        relationship_status="Never Married",
        employment_status="Part Time",
        job_title="Professional",
        mdlive_id=mdlive_res_data.get("user").get("id"),
        agrees_to_beacon_privacy_notice=data.get("agrees_to_beacon_privacy_notice"),
        agrees_to_mdlive_informed_consent=data.get("agrees_to_mdlive_informed_consent"),
        agrees_to_mdlive_privacy_agreement=data.get(
            "agrees_to_mdlive_privacy_agreement"
        ),
        mdlive_consent_user_initials=data.get("mdlive_consent_user_initials"),
        # chief_complaint1=data.get("chief_complaint1"),
        # chief_complaint2=data.get("chief_complaint2"),
        # appointment_state="PR",
        is_verified=True,
        cognito_access_token="cognito-access-token",
    )
    return user, mdlive_res, cognito_f.get_mocked_cognito_object(data)


@pytest.fixture
def user(*args, **kwargs):
    return create_user()
