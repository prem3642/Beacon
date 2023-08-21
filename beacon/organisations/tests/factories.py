# -*- coding: utf-8 -*-
# Third Party Stuff
import pytest
from django_dynamic_fixture import G

from ..models import (
    ExcludedOrganisationHomepageNavSubCategories,
    HomepageNav,
    HomepageNavCategory,
    HomepageNavSubCategory,
    Organisation,
    OrganisationHomepageNav,
)


def create_organisation(**kwargs):
    return G(Organisation, **kwargs)


@pytest.fixture
def organisation(*args, **kwargs):
    return create_organisation()


def create_homepage_nav(**kwargs):
    return G(HomepageNav, **kwargs)


def create_organisation_homepage_nav(*args, **kwargs):
    return G(OrganisationHomepageNav, **kwargs)


def create_homepage_nav_category(**kwargs):
    return G(HomepageNavCategory, **kwargs)


def create_homepage_nav_subcategory(**kwargs):
    return G(HomepageNavSubCategory, **kwargs)


def create_excluded_organisation_homepage_nav_subcategory(*args, **kwargs):
    return G(ExcludedOrganisationHomepageNavSubCategories, **kwargs)
