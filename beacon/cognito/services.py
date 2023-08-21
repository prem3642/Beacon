# -*- coding: utf-8 -*-
# Third Party Stuff
from django.conf import settings
from rest_framework.exceptions import NotAuthenticated, ValidationError
from pycognito.aws_srp import AWSSRP

from beacon.base.exceptions import CognitoAuthenticationFailedError

from .utils import CustomCognito as Cognito


def user_obj_to_dict(user_obj):
    return user_obj._data


def get_exception_handling_classes(email):

    # Get Exception classes
    # The exception handling classes are not available directly
    # They gets generated whenever the object of gets initialised
    # To initialise it, we need to pass username and password
    # But through that object we are not calling any cognito service just getting the exception classes.
    # So, passing the random password (12345) in AWSSRP class
    aws_rp = AWSSRP(
        email,
        "12345",
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        pool_region=settings.COGNITO_APP_REGION,
    )
    return vars(aws_rp.client.exceptions)


def authenticate(user, password: str):
    # This api call uses aws IAM access keys which boto3 picks directly from environment variables
    u = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        username=user.email,
    )

    # Get Exception classes
    exceptions_mapping = get_exception_handling_classes(user.email)

    # This failed count will be updated if the current
    # attempt is a failed one.
    error_response = {
        "num_of_failed_login_attempts": user.num_of_failed_login_attempts + 1
    }

    try:
        u.authenticate(password=password)
    except exceptions_mapping["_code_to_exception"]["UserNotConfirmedException"]:
        error_response["error"] = "User is not verified!"
        raise CognitoAuthenticationFailedError([error_response])
    except exceptions_mapping["_code_to_exception"]["NotAuthorizedException"]:
        error_response["error"] = "Either email or password not valid!"
        raise CognitoAuthenticationFailedError([error_response])
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        error_response["error"] = "Either email or password not valid!"
        raise CognitoAuthenticationFailedError([error_response])
    except exceptions_mapping["_code_to_exception"]["TooManyFailedAttemptsException"]:
        error_response["error"] = "Too many failed attempts, try after some time!"
        raise CognitoAuthenticationFailedError([error_response])
    except exceptions_mapping["_code_to_exception"]["InvalidPasswordException"]:
        error_response["error"] = "Either email or password not valid!"
        raise CognitoAuthenticationFailedError([error_response])

    cognito_user = u.get_user(attr_map=settings.COGNITO_ATTR_MAPPING)
    return cognito_user


def get_cognito_data(user_obj):
    if user_obj.cognito_access_token is None:
        raise NotAuthenticated("Session expired, please login again!")

    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        id_token=user_obj.cognito_id_token,
        access_token=user_obj.cognito_access_token,
        refresh_token=user_obj.cognito_refresh_token,
    )

    cognito_user = cognito_user.get_user(attr_map=settings.COGNITO_ATTR_MAPPING)
    return user_obj_to_dict(cognito_user), cognito_user.sub


def get_cognito_data_as_admin(email: str):
    # This api call uses aws IAM access keys which boto3 picks directly from environment variables
    cognito_instance = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        username=email,
    )

    # Get Exception classes
    exceptions_mapping = get_exception_handling_classes(email)
    try:
        cognito_user = cognito_instance.admin_get_user(
            attr_map=settings.COGNITO_ATTR_MAPPING
        )
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        # raise ValidationError('Either otp or email is invalid!')
        return None, None
    return user_obj_to_dict(cognito_user), cognito_user.sub


def cognito_admin_delete_user(email: str):
    # This api call uses aws IAM access keys which boto3 picks directly from environment variables
    cognito_instance = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        username=email,
    )

    return cognito_instance.admin_delete_user()


def cognito_admin_verifies_user(email: str):
    # This api call uses aws IAM access keys which boto3 picks directly from environment variables
    cognito_instance = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        username=email,
    )

    return cognito_instance.admin_confirm_sign_up()


def verify_email_of_user(code, user_obj, exceptions_mapping):
    # For this to happen user must be logged in first as it requires access token
    # When email is updated by admin, it gets automatically verified
    # If email is updated by user, on confirm sign up api it'll verifies his email
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        id_token=user_obj.cognito_id_token,
        access_token=user_obj.cognito_access_token,
        refresh_token=user_obj.cognito_refresh_token,
    )
    try:
        cognito_user.validate_verification(confirmation_code=code, attribute="email")
    except AttributeError:
        raise ValidationError("User must be logged in before email verification!")
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        raise ValidationError("Either otp or email is invalid!")
    except exceptions_mapping["_code_to_exception"]["NotAuthorizedException"]:
        raise ValidationError("Either otp or email is invalid!")
    except exceptions_mapping["_code_to_exception"]["ExpiredCodeException"]:
        raise ValidationError("OTP is expired, please resend the verification code!")
    except exceptions_mapping["_code_to_exception"]["CodeMismatchException"]:
        raise ValidationError("Invalid OTP!")

    return cognito_user


def confirm_sign_up(code, user_obj):
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
    )

    # Get Exception classes
    exceptions_mapping = get_exception_handling_classes(user_obj.email)

    try:
        cognito_user.confirm_sign_up(code, username=user_obj.email)
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        raise ValidationError("Either otp or email is invalid!")
    except exceptions_mapping["_code_to_exception"]["NotAuthorizedException"]:
        # In case of email update, user is confirmed but his email is unverified
        # Cognito raise Not Authorized for confirm Sign up
        # So, we'll check for email verification here
        # TODO: remove this when a new screen is built in between login to verify email
        return verify_email_of_user(code, user_obj, exceptions_mapping)
    except exceptions_mapping["_code_to_exception"]["ExpiredCodeException"]:
        raise ValidationError("OTP is expired, please resend the verification code!")
    except exceptions_mapping["_code_to_exception"]["CodeMismatchException"]:
        raise ValidationError("Invalid OTP!")

    return cognito_user


def register(data):
    """
    Register user on AWS Cognito

    :param data: User registration data
    e.g. of data:
    {'first_name': 'beacon',
     'last_name': 'health',
     'gender': 'M',
     'birthdate': '1988-08-08',
     'subscriber_id': 'beacon1234',
     'phone': '+18888888888',
     'email': 'mayank+14@fueled.com',
     'address1': '123 Test Road',
     'city': 'Sunrise',
     'state': 'FL',
     'zip': '33325',
     'relationship_status': 'Never Married',
     'employment_status': 'Full Time',
     'job_title': 'Technical',
     'password': 'Test1234'}

    :return: Response object received from cognito
    """
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
    )
    cognito_user.set_base_attributes(
        email=data.get("email"),
        given_name=data.get("first_name"),
        family_name=data.get("last_name"),
        address=data.get("address1"),
        birthdate=data.get("birthdate"),
        gender=data.get("gender"),
        phone_number=data.get("phone"),
    )
    cognito_user.add_custom_attributes(
        state=data.get("state"),
        city=data.get("city"),
        zip=data.get("zip"),
        id=str(data.get("id")),
        employment_status=data.get("employment_status"),
        relationship_status=data.get("relationship_status"),
        job_title=data.get("job_title"),
    )

    # Get Exception classes
    exceptions_mapping = get_exception_handling_classes(data.get("email"))

    try:
        cognito_response = cognito_user.register(
            data.get("email"), data.get("password")
        )
    except exceptions_mapping["_code_to_exception"]["UsernameExistsException"]:
        raise ValidationError(
            "We have an email conflict with this email ID. Please choose another one!"
        )
    except exceptions_mapping["_code_to_exception"]["InvalidPasswordException"]:
        raise ValidationError("Invalid Password detected by Cognito.")
    return cognito_response


def update_profile(user_obj, data):
    """
    Update user's profile on Cognito
    :param user_obj: user object to be updated
    :param data: User's profile data
    e.g. of data:
    {'first_name': 'beacon',
     'last_name': 'health',
     'gender': 'M',
     'subscriber_id': 'beacon1234',
     'phone': '+18888888888',
     'address1': '123 Test Road',
     'city': 'Sunrise',
     'state': 'FL',
     'zip': '33325',
     'relationship_status': 'Never Married',
     'employment_status': 'Full Time',
     'job_title': 'Technical'}
    :return: Response object received from cognito
    """
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        id_token=user_obj.cognito_id_token,
        access_token=user_obj.cognito_access_token,
        refresh_token=user_obj.cognito_refresh_token,
    )
    return cognito_user.update_profile(data, attr_map=settings.COGNITO_ATTR_MAPPING)


def admin_update_profile(user_obj, data):
    """
    Update user's profile on Cognito using Admin's credentials

    :param user_obj: user object to be updated
    :param data: User's profile data
    e.g. of data:
    {'first_name': 'beacon',
     'last_name': 'health',
     'gender': 'M',
     'subscriber_id': 'beacon1234',
     'phone': '+18888888888',
     'address1': '123 Test Road',
     'city': 'Sunrise',
     'state': 'FL',
     'zip': '33325',
     'relationship_status': 'Never Married',
     'employment_status': 'Full Time',
     'job_title': 'Technical',
     'is_active': 'False',
     }

    :return: Response object received from cognito
    """
    # We are getting the earlier email
    # to ensure if the email field was
    # updated, we query cognito with old email
    # but provide new email as part of update.

    previous_email = user_obj.email
    # previous_is_active = user_obj.is_active

    exceptions_mapping = get_exception_handling_classes(data["email"])

    toggle_is_active_status(data, previous_email)
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        id_token=user_obj.cognito_id_token,
        username=previous_email,
    )
    # No need to mark user as not verified
    # We'll verify the email as admin for now
    # TODO: Uncomment this when new screen is built in between login to verify email
    # if previous_email != user_obj.email:
    #     # If the email is changing, mark it as unverified in Django
    #     # On Cognito, it will be marked un-verified automatically.
    #     user_obj.is_verified = False
    #     user_obj.save()
    # return cognito_user.admin_update_profile(data, attr_map=settings.cognito_attr_mapping)
    data.pop("password", None)
    is_email_updated = True if previous_email != data["email"] else False
    try:
        cognito_response = cognito_user.admin_update_profile_with_email_verified(
            data,
            is_email_updated=is_email_updated,
            attr_map=settings.COGNITO_ATTR_MAPPING,
        )
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        raise ValidationError("User not found on Cognito")
    except exceptions_mapping["_code_to_exception"]["AliasExistsException"]:
        raise ValidationError("User with this email already exists in Cognito")
    return cognito_response


def resend_verification_email(email: str):
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        username=email,
    )

    # Get Exception classes
    exceptions_mapping = get_exception_handling_classes(email)
    try:
        cognito_response = cognito_user.resend_confirmation_code()

    except exceptions_mapping["_code_to_exception"]["InvalidParameterException"]:
        raise ValidationError("User is already verified!")
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        raise ValidationError("Invalid User!")
    except exceptions_mapping["_code_to_exception"]["NotAuthorizedException"]:
        raise ValidationError("Cannot send verification for disabled user!")
    except exceptions_mapping["_code_to_exception"]["LimitExceededException"]:
        raise ValidationError(
            "You've exceeded attempts for re-sending emails. Please wait for some time before trying again."
        )
    return cognito_response


def change_password(user_obj, old_password, new_password):
    if user_obj.cognito_access_token is None:
        raise NotAuthenticated("Session expired, please login again!")

    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        id_token=user_obj.cognito_id_token,
        access_token=user_obj.cognito_access_token,
        refresh_token=user_obj.cognito_refresh_token,
    )

    # Get Exception classes
    exceptions_mapping = get_exception_handling_classes(user_obj.email)

    try:
        response = cognito_user.change_password(old_password, new_password)
    except exceptions_mapping["_code_to_exception"]["InvalidPasswordException"]:
        raise ValidationError("Old password is not valid!")
    except exceptions_mapping["_code_to_exception"]["NotAuthorizedException"]:
        raise NotAuthenticated("User not authorized or session expired!")
    except exceptions_mapping["_code_to_exception"]["InvalidPasswordException"]:
        raise ValidationError("Invalid Password detected by Cognito.")
    return response


def initiate_password_reset(email):
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        username=email,
    )

    # Get Exception classes
    exceptions_mapping = get_exception_handling_classes(email)
    try:
        response = cognito_user.initiate_forgot_password()
    except exceptions_mapping["_code_to_exception"]["InvalidParameterException"]:
        raise ValidationError("User with given email is not verified!")
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        raise ValidationError("User for this email does not exists!")
    except exceptions_mapping["_code_to_exception"]["LimitExceededException"]:
        raise ValidationError(
            "Failed attempt limit exceeded, please try again after sometime!"
        )
    except exceptions_mapping["_code_to_exception"]["NotAuthorizedException"]:
        raise ValidationError(
            "This account has been disabled. Please contact an administrator!"
        )
    return response


def confirm_password_reset(otp, email, new_password):
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        username=email,
    )

    # Get Exception classes
    exceptions_mapping = get_exception_handling_classes(email)

    try:
        response = cognito_user.confirm_forgot_password(otp, new_password)
    except exceptions_mapping["_code_to_exception"]["ExpiredCodeException"]:
        raise ValidationError("OTP is expired, please resend the verification code!")
    except exceptions_mapping["_code_to_exception"]["CodeMismatchException"]:
        raise ValidationError("Invalid OTP!")
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        raise ValidationError("Invalid User!")
    return response


def toggle_is_active_status(data, previous_email):
    exceptions_mapping = get_exception_handling_classes(previous_email)
    cognito_user = Cognito(
        settings.COGNITO_USER_POOL_ID,
        settings.COGNITO_APP_ID,
        user_pool_region=settings.COGNITO_APP_REGION,
        username=previous_email,
    )
    try:
        if data["is_active"] == "False":
            cognito_user.admin_disable_user()
        else:
            cognito_user.admin_enable_user()
    except exceptions_mapping["_code_to_exception"]["UserNotFoundException"]:
        raise ValidationError("User not found on Cognito")
