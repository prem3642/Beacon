# -*- coding: utf-8 -*-
import pytest
from django_dynamic_fixture import G

from ..models import UserAppointment, UserResponse


def create_user_response(**kwargs):
    return G(UserResponse, **kwargs)


@pytest.fixture
def user_response(*args, **kwargs):
    return create_user_response()


def create_user_appointment(**kwargs):
    return G(UserAppointment, **kwargs)


@pytest.fixture
def user_appointment(*args, **kwargs):
    return create_user_appointment()
