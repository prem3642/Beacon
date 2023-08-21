# -*- coding: utf-8 -*-
# Standard Library
import re

# Third Party Stuff
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

# beacon Stuff
from .tokens import is_incoming_scc_token_valid


class SCCAccess(BasePermission):
    """
    This permission is required by SCC system to connect and sync
    data with the BWB system.
    """

    auth_rx = re.compile(r"^Token (.+)$")

    def has_permission(self, request, view):
        if "HTTP_AUTHORIZATION" not in request.META:
            raise PermissionDenied("Invalid Auth Token!")

        token_rx_match = self.auth_rx.search(request.META["HTTP_AUTHORIZATION"])
        if not token_rx_match:
            raise PermissionDenied("Invalid Auth Token!")

        token = token_rx_match.group(1)

        if not is_incoming_scc_token_valid(token):
            raise PermissionDenied("Invalid Auth Token!")
        return True
