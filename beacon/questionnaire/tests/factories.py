# -*- coding: utf-8 -*-
# Third Party Stuff
import pytest
from django_dynamic_fixture import G

from beacon.answers import constants

from ..models import Option, Question


def create_option(**kwargs):
    return G(Option, **kwargs)


@pytest.fixture
def option(*args, **kwargs):
    return create_option()


def create_question(**kwargs):
    return G(Question, **kwargs)


@pytest.fixture
def question(*args, **kwargs):
    return create_question()


def create_question_number_of_days_missed_work(**kwargs):
    data = {
        "kind": kwargs.get("kind", Question.NUMBER),
        "min_length": kwargs.get("min_length", 0),
        "max_length": kwargs.get("max_length", 30),
        "next_question": None,
        "user_response_attribute": kwargs.get(
            "user_response_attribute", constants.NUMBER_OF_DAYS_MISSED_WORK
        ),
        "text": kwargs.get(
            "test",
            "During the past 30 days, how many days did you miss from your job because of your behavioral health issues?",
        ),
    }
    return G(Question, **data)
