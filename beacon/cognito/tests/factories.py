# -*- coding: utf-8 -*-
import uuid
from unittest.mock import MagicMock

from django.conf import settings
from pycognito import UserObj

from ..utils import CustomCognito


def get_attribute_list(data):
    mapping = {
        "address": "address1",
        "birthdate": "birthdate",
        "gender": "gender",
        "given_name": "first_name",
        "phone_number": "phone",
        "family_name": "last_name",
        "email": "email",
        "custom:id": "id",
        "custom:job_title": "job_title",
        "custom:state": "state",
        "custom:city": "city",
        "custom:address2": "address2",
        "custom:zip": "zip",
        "custom:employment_status": "employment_status",
        "custom:relationship": "relationship",
        "custom:relationship_status": "relationship_status",
    }
    attribute_list = list()

    for key, value in mapping.items():
        attribute_list.append({"name": key, "value": data.get(value)})

    attribute_list.append(
        {
            "name": "sub",
            "value": str(uuid.uuid4()) if data.get("sub") is None else data["sub"],
        }
    )
    attribute_list.append(
        {
            "name": "email_verified",
            "value": "true"
            if data.get("email_verified") is None
            else data["email_verified"],
        }
    )
    attribute_list.append(
        {
            "name": "phone_number_verified",
            "value": "true"
            if data.get("phone_number_verified") is None
            else data["phone_number_verified"],
        }
    )
    return attribute_list


def get_mocked_user_obj(
    data=None,
    cog_object=None,
    sub=None,
    email_verified=None,
    phone_number_verified=None,
):
    if cog_object is None:
        cog_object = CustomCognito(
            settings.COGNITO_USER_POOL_ID,
            "test@example.com",
            user_pool_region=settings.COGNITO_APP_REGION,
        )
    if data is None:
        data = dict(
            first_name="beacon",
            last_name="health",
            gender="M",
            birthdate="1988-08-08",
            subscriber_id="beacon1234",
            phone="+18888888888",
            email="test@example.com",
            address1="123 Test Road",
            city="Sunrise",
            state="FL",
            zip="33325",
            relationship="Self",
            relationship_status="Never Married",
            employment_status="Full Time",
            job_title="Technical",
            password="Test1234",
        )
    username = data.get("email") if data else "test@example.com"
    user_obj = UserObj(
        username,
        get_attribute_list(data),
        cog_object,
        attr_map=settings.COGNITO_ATTR_MAPPING,
    )
    user_obj._data = data
    user_obj.sub = sub if sub else str(uuid.uuid4())
    user_obj.email_verified = True if email_verified is None else email_verified
    user_obj.phone_number_verified = (
        True if phone_number_verified is None else phone_number_verified
    )
    return user_obj


def get_register_response(sub=None, user_confirmed=False):
    if sub is None:
        sub = str(uuid.uuid4())
    return dict(
        UserConfirmed=user_confirmed,
        CodeDeliveryDetails={
            "Destination": "t***@e***.com",
            "DeliveryMedium": "EMAIL",
            "AttributeName": "email",
        },
        UserSub=sub,
    )


def get_mocked_cognito_object(data=None):
    cog = CustomCognito(
        settings.COGNITO_USER_POOL_ID,
        "test@example.com",
        user_pool_region=settings.COGNITO_APP_REGION,
    )
    cog.authenticate = MagicMock(return_value=None)
    cog.get_user = MagicMock(
        return_value=get_mocked_user_obj(data=data, cog_object=cog)
    )
    cog.confirm_sign_up = MagicMock()
    cog.add_base_attributes = MagicMock()
    cog.add_custom_attributes = MagicMock()
    cog.register = MagicMock(return_value=get_register_response())
    cog.resend_confirmation_code = MagicMock()
    cog.change_password = MagicMock()
    cog.initiate_forgot_password = MagicMock()
    cog.confirm_forgot_password = MagicMock()
    cog.update_profile = MagicMock()
    return cog
