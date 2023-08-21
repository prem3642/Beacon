# -*- coding: utf-8 -*-
import pytest
from django_dynamic_fixture import G

from ..models import HomePagePhrase


def create_homepage_phrase(**kwargs):
    return G(HomePagePhrase, **kwargs)


@pytest.fixture
def homepage_phrase(*args, **kwargs):
    return create_homepage_phrase()
