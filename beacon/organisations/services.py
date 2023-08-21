# -*- coding: utf-8 -*-
# Third party Stuff
from urllib.parse import urlparse

from django.apps import apps
from django.conf import settings
from rest_framework.exceptions import ValidationError

from .models import Organisation


def get_organisation(request, queryset=None):
    if queryset is None:
        org_model = apps.get_model("organisations", "Organisation")
        queryset = org_model.objects.filter(is_active=True, parent__isnull=True)
    origin = request.META.get("HTTP_ORIGIN")
    domain = urlparse(origin).hostname if origin else request.get_host()
    default_org_for_testing = settings.DEFAULT_ORG_FOR_TESTING
    organisation = None
    if domain:
        if default_org_for_testing is not None:
            organisation = queryset.filter(id=default_org_for_testing).first()
        else:
            organisation = queryset.filter(domain=domain).first()
    return organisation, domain

def get_organisation_new(request, queryset=None,domain=None):
    if queryset is None:
        org_model = apps.get_model("organisations", "Organisation")
        queryset = org_model.objects.filter(is_active=True, parent__isnull=True)
    origin = request.META.get("HTTP_ORIGIN")

    # domain = urlparse(domain).hostname if origin else request.get_host()

    default_org_for_testing = settings.DEFAULT_ORG_FOR_TESTING
    organisation = None
    organisation = queryset.filter(domain=domain).first()
    if domain and not organisation:
        if default_org_for_testing is not None:
            organisation = queryset.filter(id=default_org_for_testing).first()
        else:
            organisation = queryset.filter(domain__startswith=domain+'.my').first()
            if not organisation:
                organisation = queryset.filter(domain__endswith='com/'+ domain).first()
    return organisation, domain


def search_organisation(
    parent_code, group_number, benefit_package, raise_exception=False
):
    organisation_qs = Organisation.objects.filter(is_active=True)
    organisation_qs = organisation_qs.filter(parent_code=parent_code)
    organisation_qs_count = organisation_qs.count()
    if organisation_qs_count > 1:
        organisation_qs = organisation_qs.filter(group_number=group_number)
        organisation_qs_count = organisation_qs.count()
        if organisation_qs_count > 1:
            organisation_qs = organisation_qs.filter(benefit_package=benefit_package)
            organisation_qs_count = organisation_qs.count()
            if organisation_qs_count == 1:
                return organisation_qs.first()
        elif organisation_qs_count == 1:
            # Single organisation found with combination of
            # parent code and group number
            return organisation_qs.first()
    elif organisation_qs_count == 1:
        # Single Organisation found with just parent code match
        return organisation_qs.first()

    if raise_exception:
        if organisation_qs_count == 0 or organisation_qs_count > 1:
            # American-English spelling specifically requested
            # for this message on SCC.
            raise ValidationError(
                "We cannot find this organization within BWB. Please register this user manually within BWB admin"
            )

    return organisation_qs.first()
