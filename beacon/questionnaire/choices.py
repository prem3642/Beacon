# -*- coding: utf-8 -*-

# Third Party Stuff
from .models import Question


def get_question_choices(user_response_attribute, is_optional):
    """
    Given a user response attribute, the method reads available answer options for the question from Database,
    generates and return a list of choice tuples in the format of Django's choices field (e.g. [(A, B), (A, B) ...]).

    :param user_response_attribute: User response attribute for the question.
    :param is_optional: Designates if the given question is optional. If True, then a blank mapping is added to the
    choices.
    """
    choices = []
    if is_optional:
        choices.append((None, "-------"))

    question_obj = Question.objects.filter(
        user_response_attribute=user_response_attribute
    ).first()
    if question_obj:
        options = question_obj.choices.all().order_by("text")
        for option in options:
            choice_tuple = (option.text_mapped_value, option.text)
            choices.append(choice_tuple)

    return choices


#  The list contains `user_response_attributes` for all the questions in DB. User response attribute in each
#  question object refers to the name of field (key) in UserResponse model for that corresponding question. For e.i:
#  `user_response_attribute` is `chief_complaint1` for the question of primary chief complaint.
QUESTION_KEYS = [
    "emotional_support_for",
    "appointment_state",
    "chief_complaint1",
    "chief_complaint2",
    "self_harm",
    "safety_sensitive_position",
    "is_employee",
    "employee_name",
    "employee_birth_date",
    "employee_organisation_id",
    "relationship_with_employee",
    "how_often_less_interest_in_things",
    "how_often_depressed",
    "how_often_nervous",
    "how_often_worry",
    "felt_cut_down_drinking",
    "difficulty_in_keeping_drinking_limit",
    "how_emotionally_doing",
    "how_physical_health",
    "comfortable_in_managing_finances",
    "people_support",
    "resources_to_manage",
    "number_of_days_less_productive",
    "number_of_days_missed_work",
]
