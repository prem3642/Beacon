# -*- coding: utf-8 -*-
# Third Party Stuff
import jwt
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.utils import timezone
from rest_framework.exceptions import ValidationError

# beacon Stuff
from beacon.questionnaire.choices import QUESTION_KEYS
from beacon.questionnaire.models import Option, Question
from beacon.users.choices import STATE_CHOICES

from . import constants, utils
from .models import UserAppointment, UserResponse

ALGORITHM = "HS256"  # type: str


def get_user_response_for_token(token, scope):
    signer = TimestampSigner()
    try:
        token = signer.unsign(
            token, max_age=60 * settings.ANSWER_PERMISSION_SESSION_TIMEOUT
        )
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.DecodeError:
        return None

    try:
        user_response = UserResponse.objects.get(pk=data["user_response_%s_id" % scope])
    except (UserResponse.DoesNotExist, KeyError):
        return None
    else:
        return user_response


def get_token_for_user_response(user_response, scope):
    data = {
        "user_response_%s_id" % scope: str(user_response.id),
    }
    token = jwt.encode(data, settings.SECRET_KEY)
    signer = TimestampSigner()
    return signer.sign(token)


def get_formatted_response(question, response, text_mapped_value=None):
    formatted_response = {
        "question": question.text,
        "answer": response,
        "user_response_attribute": question.user_response_attribute,
        "user_appointment_attribute": question.user_appointment_attribute,
    }

    # Text mapped value will be used if we need to store mapped value in the database instead what user answered
    if text_mapped_value is not None:
        formatted_response["text_mapped_value"] = text_mapped_value

    # For multiple questions type answer will be used for its follower question, root question is just the text
    # so keeping its answer explicitly None to avoid mistakes
    if question.kind == Question.MULTIPLE_QUESTIONS:
        formatted_response["answer"] = None

    # User answers the string specified in button text
    # Saving boolean value depending on what user selects
    if question.kind == Question.YES_NO:
        if response is True:
            formatted_response["answer"] = question.yes_button_text
            formatted_response["text_mapped_value"] = True
        else:
            formatted_response["answer"] = question.no_button_text
            formatted_response["text_mapped_value"] = False

    # If we show Yes/No as options to bisect the flow depending on user response
    # than parse the text mapped value string to return python boolean
    if question.kind == Question.YES_NO_OPTIONS:
        if text_mapped_value in (True, 1, "1", "True", "true", "yes", "Yes"):
            formatted_response["text_mapped_value"] = True
        elif text_mapped_value in (False, 0, "0", "False", "false", "no", "No"):
            formatted_response["text_mapped_value"] = False
        else:
            formatted_response["text_mapped_value"] = None
    return formatted_response


def validate_multiple_choice_or_checkbox(question, response):
    if type(response) != list:
        raise ValidationError(
            "Response for Question id {} should be an array type".format(question.id)
        )
    min_length = question.min_length
    max_length = question.max_length
    if min_length:
        if len(response) < min_length:
            raise ValidationError(
                "Length of array should be minimum {} for question id {} "
                "response!".format(min_length, question.id)
            )
    if max_length:
        if len(response) > max_length:
            raise ValidationError(
                "Length of array should be maximum {} for question id {} "
                "response!".format(max_length, question.id)
            )
    choices = list(question.choices.all().values_list("text", flat=True))
    text_mapped_values = list()
    for res in response:
        choice = next((item for item in choices if item[0] == res), None)
        if choice is None:
            raise ValidationError(
                f"'{response}' doesn't exists in valid choices of question"
                f" id = '{question.id}', info = '{get_question_info(question)}'"
            )
        text_mapped_value = choice[1] if choice[1] is not None else choice[0]
        text_mapped_values.append(text_mapped_value)
    return get_formatted_response(
        question, response, text_mapped_value=text_mapped_values
    )


def validate_string_type(question, response):
    if type(response) != str:
        raise ValidationError(
            "Response for Question id {} should be string type".format(question.id)
        )
    min_length = question.min_length
    max_length = question.max_length
    if min_length:
        if len(response) < min_length:
            raise ValidationError(
                f"Length of response should be minimum {min_length} characters for question id {question.id}"
            )
    if max_length:
        if len(response) > max_length:
            raise ValidationError(
                f"Length of response should be minimum {max_length} characters for question id {question.id}"
            )
    return get_formatted_response(question, response)


def validate_dropdown_or_checkbox_choice(question, response):
    validate_string_type(question, response)
    choices = list(question.choices.all().values_list("text", "text_mapped_value"))
    choice = next((item for item in choices if item[0] == response), None)
    if choice is None:
        raise ValidationError(
            f"'{response}' doesn't exists in valid choices of question"
            f" id = '{question.id}', info = '{get_question_info(question)}'"
        )
    text_mapped_value = choice[1] if choice[1] is not None else choice[0]
    return get_formatted_response(
        question, response, text_mapped_value=text_mapped_value
    )


def validate_number(question, response):
    try:
        response = int(response)
    except ValueError:
        raise ValidationError(
            "Response for Question id {} should be number type".format(question.id)
        )
    min_length = question.min_length
    max_length = question.max_length
    if min_length == 0 or min_length:
        if response < min_length:
            raise ValidationError(
                "Response should be minimum {} for question id "
                "{}".format(min_length, question.id)
            )
    if max_length == 0 or max_length:
        if response > max_length:
            raise ValidationError(
                "Response should be maximum {} for question id "
                "{}".format(max_length, question.id)
            )
    return get_formatted_response(question, response)


def validate_regex(question, response):
    validate_string_type(question, response)
    if question.regex:
        if question.regex.match(response) is None:
            raise ValidationError(question.regex_error_message)
    return get_formatted_response(question, response)


def validate_yes_no(question, response):
    if type(response) is not bool:
        raise ValidationError(
            "Response for Question id {} should be a bool type".format(question.id)
        )
    return get_formatted_response(question, response)


def validate_organisation(question, response, organisation=None):
    if organisation is None:
        raise ValidationError(
            "Response for Question id {} not valid as no organisation exists".format(
                question.id
            )
        )
    choices = list(
        organisation.children.filter(is_active=True).values_list("location", "id")
    )
    choice = next((item for item in choices if item[0] == response), None)
    if choice is None:
        raise ValidationError(
            f"'{response}' doesn't exists in valid choices of question"
            f" id = '{question.id}', info = '{get_question_info(question)}'"
        )
    text_mapped_value = str(choice[1]) if choice[1] is not None else None
    return get_formatted_response(
        question, response, text_mapped_value=text_mapped_value
    )


def validate_on_question_type(question, answer, organisation=None):
    kind = question.kind
    if kind == Question.FRONTEND:
        kind = question.backend_kind
    # if kind == Question.MULTIPLE_CHECKBOX or kind == Question.MULTIPLE_CHOICE:
    #     return validate_multiple_choice_or_checkbox(question, answer)
    if (
        kind == Question.CHECKBOX
        or kind == Question.DROPDOWN
        or kind == Question.RADIO
        or kind == Question.YES_NO_OPTIONS
    ):
        return validate_dropdown_or_checkbox_choice(question, answer)
    elif kind == Question.YES_NO:
        return validate_yes_no(question, answer)
    elif kind == Question.TEXT or kind == Question.TEXT_BOX:
        return validate_string_type(question, answer)
    elif kind == Question.NUMBER:
        return validate_number(question, answer)
    elif kind == Question.REGEX:
        return validate_regex(question, answer)
    elif kind == Question.ORGANISATION:
        return validate_organisation(question, answer, organisation)

    return get_formatted_response(question, answer)


def validate_nested_response(question, response, organisation=None):
    nested_response = None
    if question.nested_question:
        nested_response = response.pop("nested_response", None)
    answer = response.get("answer")
    formatted_response = validate_on_question_type(question, answer, organisation)
    if nested_response:
        formatted_response["nested_response"] = validate_nested_response(
            question.nested_question, nested_response, organisation
        )
    return formatted_response


def validate_multiple_questions_response(
    question, response, questions_qs, organisation=None
):
    if response:
        multiple_questions_response = response.pop("multiple_questions_response", None)
        if multiple_questions_response and type(multiple_questions_response) is list:
            formatted_response = get_formatted_response(question, response)
            formatted_response["multiple_questions_response"] = list()
            for question_response in multiple_questions_response:
                question_id = question_response.get("question")
                answer = question_response.get("answer")
                array_questions = list(
                    filter(lambda q: str(q.id) == question_id, questions_qs)
                )
                if not array_questions:
                    raise ValidationError(
                        f"Question with id {question_id} does not exists"
                    )
                array_question = array_questions[0]
                formatted_response["multiple_questions_response"].append(
                    validate_on_question_type(array_question, answer, organisation)
                )
            return formatted_response
    raise ValidationError(
        "Question with id {} is of multiple-questions type which require response of format: "
        '{"multiple_questions_response: [{"answer": ".."}, {"answer": ".."}]}'
    )


def validate_single_response(response, questions_qs, organisation=None):
    question_id = response.get("question")
    answer = response.get("answer")
    questions = list(filter(lambda q: str(q.id) == question_id, questions_qs))
    if not questions:
        raise ValidationError(f"Question with id {question_id} doesn't exists")
    question = questions[0]
    if question.nested_question:
        return validate_nested_response(question, response, organisation=None)
    elif question.kind == question.MULTIPLE_QUESTIONS:
        return validate_multiple_questions_response(
            question, response, questions_qs, organisation
        )
    return validate_on_question_type(question, answer, organisation)


def validate_response_json(json_data, organisation=None):
    """
    Method to validate user response json (question-answers) data, convert and return it in a verbose format.
    Example input `json_data`:
    ```json
    [
      {
        "question": "3b2390f1-c55a-4492-a36d-861d8a6a7bd9",
        "answer": "Not true at all"
      }
    ]
    ```

    Example returning value:
    ```json
    [
      {
        "answer": "Not true at all",
        "question": "I have the tools to manage life challenges",
        "text_mapped_value": "1",
        "user_appointment_attribute": null,
        "user_response_attribute": "resources_to_manage"
      }
    ]
    ```
    """
    validated_json = list()
    if json_data:
        questions = Question.objects.prefetch_related("choices").all()
        for response in json_data:
            validated_json.append(
                validate_single_response(response, questions, organisation)
            )
    return validated_json


def update_or_create_appointment(appointment_instance, appointment_data: dict):
    if appointment_instance is None:
        return UserAppointment.objects.create(**appointment_data)

    for attr, value in appointment_data.items():
        setattr(appointment_instance, attr, value)
    return appointment_instance.save()


def replace_or_append_response(instance, validated_response):
    """
    Update existing json with new response
    :param instance: instance of UserResponse or UserAppointment
    :param validated_response:
    :return: updated instance
    """
    response = instance.response
    if response == {}:
        response = []
    for answer in validated_response:
        # Check question already exists or not
        question_index = next(
            (
                index
                for (index, dct) in enumerate(response)
                if dct["question"] == answer["question"]
            ),
            None,
        )
        if question_index is None:
            response.append(answer)
        else:
            response[question_index] = answer

    instance.response = response
    instance.save()
    return instance


def set_attribute_from_response(
    user_response_object, user_appointment_object, response
):
    user_response_attribute = response.get("user_response_attribute")
    user_appointment_attribute = response.get("user_appointment_attribute")
    value = response.get("answer")
    text_mapped_value = response.get("text_mapped_value")
    if text_mapped_value is not None:
        value = text_mapped_value
        # For one choice we need to save null value but None as value gets discarded
        # Adding None as string then map it to null
        if text_mapped_value == "None":
            value = None
    if user_response_attribute:
        if user_response_attribute == constants.APPOINTMENT_STATE:
            if len(value) > 2:
                value = next(
                    (code for (code, name) in STATE_CHOICES if name == value), None
                )
        setattr(user_response_object, user_response_attribute, value)

    if user_appointment_attribute:
        if user_appointment_object is None:
            user_appointment_object = user_response_object.appointments.first()
        update_or_create_appointment(
            user_appointment_object,
            {user_appointment_attribute: value, "user_response": user_response_object},
        )

    multiple_questions_response = response.get("multiple_questions_response", None)
    if multiple_questions_response:
        for question_response in multiple_questions_response:
            user_response_object, user_appointment_object = set_attribute_from_response(
                user_response_object, user_appointment_object, question_response
            )

    nested_response = response.get("nested_response", None)
    if nested_response:
        user_response_object, user_appointment_object = set_attribute_from_response(
            user_response_object, user_appointment_object, nested_response
        )
    return user_response_object, user_appointment_object


def set_attributes_from_response_json(user_response_object):
    user_appointment_object = None
    for answer in user_response_object.response:
        user_response_object, user_appointment_object = set_attribute_from_response(
            user_response_object, user_appointment_object, answer
        )
    user_response_object.save()
    if user_appointment_object:
        user_appointment_object.save()
    return user_response_object, user_appointment_object


def backup_user_response_json(answer_obj, response_json):
    """Method to create backup of a user's response json."""

    def format_timestamped_backup(value):
        timestamp = str(timezone.datetime.now())
        return {timestamp: value}

    existing_backup = answer_obj.response_backup
    new_response_to_backup = format_timestamped_backup(value=response_json)
    if existing_backup:
        existing_backup.update(new_response_to_backup)
    else:
        answer_obj.response_backup = new_response_to_backup

    answer_obj.save()


def generate_user_response_json(user_response):
    """Method to generate user response JSON given a UserResponse object."""
    answer_data = user_response_to_dict(user_response=user_response)
    question_answer_json = get_question_answer_json(
        answer_data=answer_data,
        user_response=user_response,
    )
    user_org = user_response.user.organisation if user_response.user else None

    # This converts the concise `question_answer_json` into a verbose format containing
    # both the display and DB values of both the question and answer.
    user_response_json = validate_response_json(
        json_data=question_answer_json,
        organisation=user_org,
    )
    return user_response_json


def user_response_to_dict(user_response):
    """Method to convert a UserResponse object into a dictionary having only question fields"""
    answers_data = {}
    for question in QUESTION_KEYS:
        if hasattr(user_response, question):
            answers_data.update({question: getattr(user_response, question)})
    return answers_data


def get_question_answer_json(answer_data, user_response=None):
    """
    Method to return user response in the format that BWB BE System receive from FE. For example:
    ```json
    [
        {
            "question": "3b2390f1-c55a-4492-a36d-861d8a6a7bd9",
            "answer": "lorem ipsum"
        }
    ]
    ```
    This is done so that returning value can be processed in "answers.services.validate_response_json()" that generates
    the final and verbose user response json.

    :param answer_data: Dictionary with `question.user_response_attribute` as keys and latest answers as values.
    :param user_response: Pre existing UserResponse object. Useful if `answer_data` is partial.
    """
    response = []

    def format_answer(question, answer):
        answer_option = Option.objects.filter(
            question=question.id, text_mapped_value=answer
        ).first()
        if not answer_option:
            return {"question": str(question.id), "answer": answer}
        return {"question": str(question.id), "answer": answer_option.text}

    def update_response(question_obj, answer):
        if answer is not None:
            answer = format_answer(question_obj, answer)
            response.append(answer)

    for question_key in QUESTION_KEYS:
        question = Question.objects.filter(user_response_attribute=question_key).first()
        if question:
            user_response_attribute = question.user_response_attribute
            if user_response_attribute in answer_data.keys():
                answer_received = answer_data.get(user_response_attribute)
                update_response(question, answer_received)
            elif user_response:
                existing_answer = getattr(user_response, question_key)
                update_response(question, existing_answer)

    return response


def get_question_info(question):
    """
    Method to return identifiable information about a given question.

    A `Question` object could have either `user_response_attribute` or `user_appointment_attribute` (never both). In
    case both are not available, then `text` can be used to identify question. Example values for these attributes are:

    user_response_attribute="chief_complaint1"
    user_appointment_attribute="f2f_address1"
    text="Get emotional support for"
    """
    if question.user_response_attribute:
        return question.user_response_attribute
    elif question.user_appointment_attribute:
        return question.user_appointment_attribute
    return question.text


def save_answer_serializer(answer_serializer, user_obj, answer_data):
    """
    This method saves answer serializer and handle creating the backups for user
    response JSON. If a user response JSON already present, and the new response JSON
    to save is different, then create a backup of the older JSON.

    Reasons:
    1. These updates are happening by Service Care Connect (SCC) system. So
    this backing up can be used to track the changes (if any).
    2. SCC can update the existing answers of a user to "null", which if creates any
    unforeseeable issue in future, we can use the backup to get back the working data.
    """
    old_response_json = (
        user_obj.answer.response if hasattr(user_obj, "answer") else None
    )
    new_response_json = answer_serializer.validated_data["response"]
    answer_serializer.save(user=user_obj, response=new_response_json, **answer_data)
    if old_response_json:
        if utils.ordered(old_response_json) != utils.ordered(new_response_json):
            backup_user_response_json(
                answer_obj=user_obj.answer, response_json=old_response_json
            )
