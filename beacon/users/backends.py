# -*- coding: utf-8 -*-
"""
Authentication backends for rest framework.

This module exposes two backends: session and token.

The first (session) is a modified version of standard
session authentication backend of rest-framework with
csrf token disabled.

And the second (token) implements own version of oauth2
like authentication but with self contained tokens. That
makes authentication totally stateless.

It uses django signing framework for create new
self contained tokens. This trust tokes from external
fraudulent modifications.
"""

# Standard Library
import re

# Third Party Stuff
from rest_framework.authentication import BaseAuthentication

from .tokens import get_user_for_token
from .utils import get_auth_token_from_request


class UserTokenAuthentication(BaseAuthentication):
    """
    Self-contained stateless authentication implementation
    that work similar to OAuth2.
    It uses json web tokens (https://github.com/jpadilla/pyjwt) for trust
    data stored in the token.
    """

    auth_rx = re.compile(r"^Token (.+)$")

    def authenticate(self, request):
        token = get_auth_token_from_request(request, self.auth_rx)
        if token is None:
            return None

        user = get_user_for_token(token, "authentication")
        return user, token

    def authenticate_header(self, request):
        return 'Token realm="api"'
