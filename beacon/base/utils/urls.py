# -*- coding: utf-8 -*-
# Standard Library
from urllib.parse import urlparse

# Third Party Stuff
import django_sites as sites
from django.conf import settings
from django.urls import reverse as django_reverse

URL_TEMPLATE = "{scheme}://{domain}/{path}"


def build_url(path, scheme="http", domain="localhost"):
    return URL_TEMPLATE.format(scheme=scheme, domain=domain, path=path.lstrip("/"))


def is_absolute_url(path):
    """Test wether or not `path` is absolute url."""
    return path.startswith("http")


def get_absolute_url(path, site_id=None):
    """Return a path as an absolute url."""
    if is_absolute_url(path):
        return path
    if site_id:
        site = sites.get_by_id(site_id)
    else:
        site = sites.get_current()
    return build_url(path, scheme=site.scheme, domain=site.domain)


def resolve_frontend_url(name, site_id="frontend", **kwargs):
    """Returns the absolute url for the frontend site.
    url
    resolve_front_urls('password-confirm', token="xyz", uuid="abc")
    """
    urls = settings.FRONTEND_URLS
    path = urls[name].format(**kwargs)
    return get_absolute_url(path=path, site_id=site_id)


def resolve_frontend_url_for_organisation(
    name, organisation=None, site_id="frontend", **kwargs
):
    """Returns the absolute url for the frontend site for an organisation.
    url
    resolve_frontend_url_for_organisation('password-confirm', organisation=organisation, token="xyz", uuid="abc")
    """
    if organisation is None:
        return resolve_frontend_url(name, site_id, **kwargs)
    domain = organisation.domain
    if domain is None and organisation.parent is not None:
        domain = organisation.parent.domain
    parsed_uri = urlparse(domain)
    urls = settings.FRONTEND_URLS
    path = urls[name].format(**kwargs)
    if is_absolute_url(path):
        return path

    # If scheme is None, urlparse parses the rest of the url as path
    return build_url(
        path,
        scheme=parsed_uri.scheme if parsed_uri.scheme else "https",
        domain=parsed_uri.netloc if parsed_uri.netloc else parsed_uri.path,
    )


def reverse(viewname, *args, **kwargs):
    """Same behavior as django's reverse but uses django_sites to compute absolute url."""
    return get_absolute_url(django_reverse(viewname, *args, **kwargs))
