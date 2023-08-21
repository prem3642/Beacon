# -*- coding: utf-8 -*-
# Third Party Stuff
from django import template

from ..utils.urls import get_absolute_url as _get_absolute_url
from ..utils.urls import resolve_frontend_url as _resolve_frontend_url
from ..utils.urls import (
    resolve_frontend_url_for_organisation as _resolve_frontend_url_for_organisation,
)

register = template.Library()


@register.simple_tag
def get_absolute_url(path, **kwargs):
    return _get_absolute_url(path, **kwargs)


@register.simple_tag
def resolve_frontend_url(name, **kwargs):
    """Templatetag to render absolute urls for frontend app via it's name.

    It makes use of the mapping in FRONTEND_URLS in settings, combined with
    FRONTEND_SITE_SCHEME and FRONTEND_SITE_DOMAIN and configuration.

    Usages:
    ```
    {% load resolve_frontend_url from urls_extra %}

    {% resolve_frontend_url "home" %}
    {% resolve_frontend_url "password-reset" token=token %}
    ```
    """
    return _resolve_frontend_url(name, **kwargs)


@register.simple_tag
def resolve_frontend_url_for_organisation(name, **kwargs):
    """Templatetag to render absolute urls for frontend app via it's name and organisation.

    It makes use of the mapping in FRONTEND_URLS in settings, combined with
    domain defined in organisation.

    Usages:
    ```
    {% load resolve_frontend_url_for_organisation from urls_extra %}

    {% resolve_frontend_url_for_organisation "home" organisation=organisation %}
    {% resolve_frontend_url_for_organisation "password-reset" organisation=organisation token=token %}
    ```
    """
    return _resolve_frontend_url_for_organisation(name, **kwargs)
