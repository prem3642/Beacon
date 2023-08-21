# -*- coding: utf-8 -*-
# Third Party Stuff
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

# beacon Stuff
from beacon.base import exceptions as exc

from .services import (
    get_logged_in_user_tokens_from_cache,
    set_logged_in_user_token_to_cache,
)
from .utils import decode_uuid_from_base64, encode_uuid_to_base64

ALGORITHM = "HS256"  # type: str


def get_token_for_user(user, scope):
    """
    Generate a new signed token containing
    a specified user limited for a scope (identified as a string).
    """
    data = {
        "user_%s_id" % scope: str(user.id),
    }
    token = jwt.encode(data, settings.SECRET_KEY)
    signer = TimestampSigner()
    token = signer.sign(token)

    # Setting the token in cache to check logout and maintain multiple sessions
    set_logged_in_user_token_to_cache(str(user.id), token)
    return token


def get_user_for_token(
    signed_token, scope, max_age_in_minutes=settings.JWT_TOKEN_EXPIRATION_DURATION
):
    """
    Given a self contained token and a scope try to parse and
    un-sign it.

    If max_age is specified it checks token expiration.

    If token passes a validation, returns
    a user instance corresponding with user_id stored
    in the incoming token.
    """
    signer = TimestampSigner()
    try:
        token = signer.unsign(signed_token, max_age=60 * max_age_in_minutes)
    except SignatureExpired:
        raise exc.NotAuthenticated("Token expired")
    except BadSignature:
        raise exc.NotAuthenticated("Invalid token")

    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.DecodeError:
        raise exc.NotAuthenticated("Invalid token!")

    model_cls = get_user_model()

    try:
        user = model_cls.objects.get(pk=data["user_%s_id" % scope])
    except (model_cls.DoesNotExist, KeyError):
        raise exc.NotAuthenticated("Invalid token!")
    else:
        # getting all the tokens for this user from cache to check logged out users
        tokens = get_logged_in_user_tokens_from_cache(str(user.id))
        if signed_token in tokens:
            return user
        raise exc.NotAuthenticated("Invalid token!")


def get_token_for_password_reset(user):
    return "{}::{}".format(
        encode_uuid_to_base64(user.pk), PasswordResetTokenGenerator().make_token(user)
    )


def get_user_for_password_reset_token(token):
    default_error_messages = {
        "invalid_token": "Invalid token or the token has expired",
        "user_not_found": "No user exists for given token",
    }
    try:
        uidb64, reset_token = token.split("::")
    except ValueError:
        raise exc.RequestValidationError(default_error_messages["invalid_token"])

    user_id = decode_uuid_from_base64(uidb64)
    if not user_id:
        raise exc.RequestValidationError(default_error_messages["invalid_token"])

    user = get_user_model().objects.filter(id=user_id).first()

    if not user:
        raise exc.RequestValidationError(default_error_messages["user_not_found"])

    if not PasswordResetTokenGenerator().check_token(user, reset_token):
        raise exc.RequestValidationError(default_error_messages["invalid_token"])

    return user
