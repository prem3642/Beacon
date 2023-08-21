# -*- coding: utf-8 -*-
# Third Party Stuff
import requests
from django.conf import settings


class SccApiClient:
    MEMBER_REGISTRATION_URI = (
        "/ConnectsESBWeb/rest/resources/registration/1.0/memberregistration"
    )

    def __init__(self, auth_token):
        self._base_url = settings.SCC_BASE_URL
        self._auth_token = auth_token
        self.headers = {
            "Content-type": "application/json",
            "Token": f"{self._auth_token}",
        }

    def make_request(self, method, uri, **kwargs):
        url = self._base_url + uri
        kwargs["headers"] = self.headers
        response = requests.request(
            method, url, verify=settings.VERIFY_CONNECTS_SSL, **kwargs
        )
        response.raise_for_status()
        return response.json()

    def send_new_user_registration(self, request, scc_uri=MEMBER_REGISTRATION_URI):
        response = self.make_request(method="POST", uri=scc_uri, json=request)
        return response
