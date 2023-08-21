# -*- coding: utf-8 -*-
# Standard Library
import re

# Third Party Stuff
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

# beacon Stuff
from beacon.base.exceptions import NotAuthenticated
from beacon.users.tokens import get_user_for_token
from beacon.users.utils import get_auth_token_from_request

from .services import get_user_response_for_token


class UserResponseAccess(BasePermission):

    auth_rx = re.compile(r"^Token (.+)$")

    def has_permission(self, request, view):
        if "HTTP_AUTHORIZATION" not in request.META:
            raise PermissionDenied("Invalid Auth Token!")

        token_rx_match = self.auth_rx.search(request.META["HTTP_AUTHORIZATION"])
        if not token_rx_match:
            raise PermissionDenied("Invalid Auth Token!")

        token = token_rx_match.group(1)

        # Pass request object to save the session object in request
        user_response = get_user_response_for_token(token, "authentication")
        if user_response is None:
            raise PermissionDenied("Invalid Auth Token!")

        request.user_response = user_response
        return True


class LoggedInUserResponseAccess(BasePermission):

    auth_rx = re.compile(r"^Token (.+)$")

    def has_permission(self, request, view):
        token = get_auth_token_from_request(request, self.auth_rx)
        if token is None:
            raise PermissionDenied("Invalid Token!")
        try:
            user = get_user_for_token(token, "authentication")
            user_response = None
            if hasattr(user, "answer") is True:
                user_response = user.answer
        except NotAuthenticated:
            # Pass request object to save the session object in request
            user_response = get_user_response_for_token(token, "authentication")

        if user_response is None:
            raise PermissionDenied("Invalid Auth Token!")
        request.user_response = user_response
        return True
