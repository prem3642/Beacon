# -*- coding: utf-8 -*-
# beacon Stuff
from beacon.answers import constants
from beacon.questionnaire.models import Question, TemplateQuestionMapping


def starting_question_next_service(user_response):
    if (
        user_response.chief_complaint1 == constants.ALCOHOL
        or user_response.chief_complaint2 == constants.ALCOHOL
    ):
        # if template.show_safety_screen is True and user_response.is_employee is True:
        #     return Question.objects.filter(user_response_attribute=constants.SAFETY_SENSITIVE_POSITION).first()
        return Question.objects.filter(
            user_response_attribute=constants.FELT_CUT_DOWN_DRINKING
        ).first()
    if user_response.chief_complaint1 in [constants.ANXIETY, constants.STRESS]:
        return Question.objects.filter(
            user_response_attribute=constants.HOW_OFTEN_NERVOUS
        ).first()
    return Question.objects.filter(
        user_response_attribute=constants.HOW_OFTEN_LESS_INTEREST_IN_THINGS
    ).first()


def is_employee_question_next_service(user_response):
    if (
        user_response.chief_complaint1 == constants.ALCOHOL
        or user_response.chief_complaint2 == constants.ALCOHOL
    ):
        return Question.objects.filter(
            user_response_attribute=constants.SAFETY_SENSITIVE_POSITION
        ).first()
    return starting_question_next_service(user_response)


#
#
# def safety_screen_question_next_service(user_response):
#     if user_response.chief_complaint1 == constants.ALCOHOL or user_response.chief_complaint2 == constants.ALCOHOL:
#         return starting_question_next_service(user_response)
#     if user_response.is_employee is True and user_response.felt_cut_down_drinking is None:
#         return Question.objects.filter(user_response_attribute=constants.FELT_CUT_DOWN_DRINKING).first()
#     if (user_response.is_employee is True and user_response.felt_cut_down_drinking is True and
#             user_response.difficulty_in_keeping_drinking_limit is None):
#         return Question.objects.filter(user_response_attribute=constants.DIFFICULTY_IN_KEEPING_DRINKING_LIMIT).first()
#     return Question.objects.filter(user_response_attribute=constants.HOW_EMOTIONALLY_DOING).first()


def safety_screen_felt_cut_down_drinking_question_next_service(user_response):
    if (
        user_response.safety_sensitive_position is None
        and user_response.is_employee is True
        and user_response.felt_cut_down_drinking is True
    ):
        return Question.objects.filter(
            user_response_attribute=constants.SAFETY_SENSITIVE_POSITION
        ).first()
    return Question.objects.filter(
        user_response_attribute=constants.DIFFICULTY_IN_KEEPING_DRINKING_LIMIT
    ).first()


def safety_screen_difficulty_in_keeping_drinking_limit_question_next_service(
    user_response,
):
    if (
        user_response.safety_sensitive_position is None
        and user_response.is_employee is True
        and user_response.difficulty_in_keeping_drinking_limit is True
    ):
        return Question.objects.filter(
            user_response_attribute=constants.SAFETY_SENSITIVE_POSITION
        ).first()
    return Question.objects.filter(
        user_response_attribute=constants.HOW_EMOTIONALLY_DOING
    ).first()


def starting_question_previous_service(user_response):
    if user_response.is_employee is False:
        follower_question = Question.objects.filter(
            user_response_attribute=constants.EMPLOYEE_NAME
        ).first()
        if follower_question:
            return follower_question.leader_question
    if user_response.is_employee is True:
        if user_response.safety_sensitive_position is True:
            return Question.objects.filter(
                user_response_attribute=constants.SAFETY_SENSITIVE_POSITION
            ).first()
    return Question.objects.filter(
        user_response_attribute=constants.EMOTIONAL_SUPPORT_FOR
    ).first()


def f2f_search_address_previous_service(user_response):
    appointment = user_response.appointments.first()
    if appointment:
        if appointment.f2f_counselor_search_address == constants.F2F_OTHER_ADDRESS:
            follower_question = Question.objects.filter(
                user_appointment_attribute=constants.F2F_ADDRESS1
            ).first()
            if follower_question:
                return follower_question.leader_question
    return Question.objects.filter(
        user_appointment_attribute=constants.F2F_COUNSELOR_SEARCH_ADDRESS
    )


def f2f_counselor_notes_previous_service(user_response):
    appointment = user_response.appointments.first()
    if appointment:
        if appointment.f2f_preferred_contact == constants.F2F_PHONE:
            return Question.objects.filter(
                user_appointment_attribute=constants.F2F_OKAY_TO_LEAVE_VOICEMAIL
            ).first()
    return Question.objects.filter(
        user_appointment_attribute=constants.F2F_PREFERRED_CONTACT
    ).first()


def get_next_question_from_template_question_mapping(instance, user_response):
    services = {
        "starting_question_next_service": starting_question_next_service,
        # "safety_screen_starting_question_next_service": safety_screen_question_next_service,
        "safety_screen_felt_cut_down_drinking_question_next_service": safety_screen_felt_cut_down_drinking_question_next_service,
        "safety_screen_difficulty_in_keeping_drinking_limit_question_next_service": safety_screen_difficulty_in_keeping_drinking_limit_question_next_service,
        "is_employee_question_next_service": is_employee_question_next_service,
    }
    if instance.next_question_service is None:
        return instance.next_question
    if instance.next_question_service in services:
        return services[instance.next_question_service](user_response)
    return None


def get_previous_question_from_template_question_mapping(instance, user_response):
    services = {
        "starting_question_previous_service": starting_question_previous_service,
        "f2f_search_address_previous_service": f2f_search_address_previous_service,
        "f2f_counselor_notes_previous_service": f2f_counselor_notes_previous_service,
    }
    if instance.previous_question_service is None:
        return instance.previous_question
    if instance.previous_question_service in services:
        return services[instance.previous_question_service](user_response)
    return None


def get_next_question_service(template, question, user_response):
    appointment = user_response.appointments.first()
    appointment_value = None
    if appointment is not None and question.user_appointment_attribute is not None:
        appointment_value = getattr(
            appointment, question.user_appointment_attribute, None
        )
    mapping = list(
        TemplateQuestionMapping.objects.select_related("option", "question").filter(
            question=question, template=template
        )
    )
    if mapping:
        if len(mapping) == 1:
            return get_next_question_from_template_question_mapping(
                mapping[0], user_response
            )

        if question.user_response_attribute is not None:
            user_response_value = getattr(
                user_response, question.user_response_attribute, None
            )
            if user_response_value is not None:
                instance = next(
                    (
                        x
                        for x in mapping
                        if x.option.text_mapped_value == str(user_response_value)
                    ),
                    None,
                )
                if instance is None:
                    return None
                return get_next_question_from_template_question_mapping(
                    instance, user_response
                )

        if appointment_value is not None:
            instance = next(
                (
                    x
                    for x in mapping
                    if x.option.text_mapped_value == str(appointment_value)
                ),
                None,
            )
            if instance is None:
                return None
            return get_next_question_from_template_question_mapping(
                instance, user_response
            )

    return None


def get_previous_question_service(template, question, user_response):
    appointment = user_response.appointments.first()
    appointment_value = None
    if appointment is not None and question.user_appointment_attribute is not None:
        appointment_value = getattr(
            appointment, question.user_appointment_attribute, None
        )

    mapping = list(
        TemplateQuestionMapping.objects.select_related("option", "question").filter(
            question=question, template=template
        )
    )
    if mapping:
        user_response_value = getattr(
            user_response, question.user_response_attribute, None
        )
        if len(mapping) == 1 or (
            user_response_value is None and appointment_value is None
        ):
            return get_previous_question_from_template_question_mapping(
                mapping[0], user_response
            )

        if user_response_value is not None:
            instance = next(
                (
                    x
                    for x in mapping
                    if x.option.text_mapped_value == user_response_value
                ),
                None,
            )
            if instance is None:
                return None
            return get_previous_question_from_template_question_mapping(
                instance, user_response
            )

        if appointment_value is not None:
            instance = next(
                (x for x in mapping if x.option.text_mapped_value == appointment_value),
                None,
            )
            if instance is None:
                return None
            return get_previous_question_from_template_question_mapping(
                instance, user_response
            )

    return None
