# -*- coding: utf-8 -*-
# Standard Library
from collections import namedtuple

# Third Party Stuff
from django.core.management.base import BaseCommand
from rest_framework.exceptions import NotAuthenticated, ValidationError

# beacon Stuff
from beacon.cognito import services as cognito_services


def test_register(data: dict):
    print("Test user registration....")
    try:
        cognito_services.register(data)
        print("User registration successful....")
    except ValidationError as e:
        print(f"User registration failed with error: {e}")

    # register again with same email
    try:
        cognito_services.register(data)
    except ValidationError:
        print("Successfully raised error on registering again with same email!")


def test_authenticate(user, password: str, original_email):
    print("Test authentication with wrong password....")
    try:
        cognito_services.authenticate(user, "Test1234")
    except ValidationError:
        print("Successfully raised error!")

    print("Test authentication wrong email....")
    user._replace(email="test12345@about.me")
    try:
        cognito_services.authenticate(user, password)
    except ValidationError:
        print("Successfully raised error!")

    print("Test successful authentication....")
    user._replace(email=original_email)
    try:
        cognito_user = cognito_services.authenticate(user, password)
        print("Successfully authenticated!")
    except ValidationError as e:
        print(f"Login failed with error: {e}!")
    return cognito_user


def test_reset_password(email: str):
    print("Testing reset password with wrong email....")
    try:
        cognito_services.initiate_password_reset("test1234@about.me")
    except ValidationError:
        print("Successfully raised error!")

    print("Testing successful initiate password reset....")
    try:
        cognito_services.initiate_password_reset(email)
        print("Successfully initiated!")
    except ValidationError as e:
        print(f"Password reset initiation failed with error: {e}!")


def test_resend_verification_email(email: str):
    print("Testing resend verification with wrong email....")
    try:
        cognito_services.resend_verification_email("test1234@about.me")
    except ValidationError:
        print("Successfully raised error!")

    print("Testing successful resend verification email....")
    try:
        cognito_services.resend_verification_email(email)
        print("Successfully sent!")
    except ValidationError as e:
        print(f"Resend verification email failed with error: {e}!")


def test_change_password(user_obj):
    old_password = user_obj.password
    new_password = "Test123456"
    print("Testing change password with invalid old password....")
    try:
        cognito_services.change_password(user_obj, "test12", new_password)
    except NotAuthenticated:
        print("Successfully raised error!")

    print("Testing successful change password....")
    try:
        cognito_services.change_password(user_obj, old_password, new_password)
        print("Successfully changed!")
        # Reset password to old one
        cognito_services.change_password(user_obj, new_password, old_password)
    except ValidationError as e:
        print(f"Password change failed with error: {e}!")


class Command(BaseCommand):
    help = "Test Cognito Services"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)

    def handle(self, *args, **options):
        simulator_email = "success@simulator.amazonses.com"
        email = options["email"]
        password = options["password"]
        data = {
            "first_name": "beacon",
            "last_name": "health",
            "gender": "M",
            "birthdate": "1988-08-08",
            "subscriber_id": "beacon1234",
            "phone": "+18888888888",
            "email": email,
            "address1": "123 Test Road",
            "city": "Sunrise",
            "state": "FL",
            "zip": "33325",
            "relationship_status": "Never Married",
            "employment_status": "Full Time",
            "job_title": "Technical",
            "password": password,
        }
        test_register(data)
        test_resend_verification_email(email)
        cognito_services.cognito_admin_verifies_user(email)
        user = namedtuple(
            "user",
            [
                "email",
                "num_of_failed_login_attempts",
                "access_token",
                "id_token",
                "refresh_token",
            ],
        )
        user_obj = user(email, 0, "access_token", "id_token", "refresh_token")
        cognito_user = test_authenticate(user_obj, password, original_email=email)

        user_obj_tuple = namedtuple(
            "user_obj",
            [
                "email",
                "password",
                "cognito_access_token",
                "cognito_id_token",
                "cognito_refresh_token",
            ],
        )
        user_obj = user_obj_tuple(
            email,
            password,
            cognito_user.access_token,
            cognito_user.id_token,
            cognito_user.refresh_token,
        )
        test_reset_password(simulator_email)
        test_change_password(user_obj)
