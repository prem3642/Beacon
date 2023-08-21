# -*- coding: utf-8 -*-
# Third Party Stuff
import pytest
from django.urls import reverse

# beacon Stuff
from beacon.questionnaire.models import Question

from . import factories as f

pytestmark = pytest.mark.django_db


def test_get_questions(client):
    url = reverse("questions-list")
    question1 = f.create_question(
        next_question=None,
        previous_question=None,
        nested_question=None,
        leader_question=None,
    )
    question2 = f.create_question(
        next_question=question1,
        previous_question=None,
        nested_question=None,
        leader_question=None,
    )
    question4 = f.create_question(
        next_question=None,
        previous_question=None,
        nested_question=None,
        leader_question=None,
    )
    question3 = f.create_question(
        next_question=question2,
        previous_question=None,
        nested_question=question4,
        leader_question=None,
    )
    question5 = f.create_question(
        next_question=None,
        previous_question=question3,
        nested_question=None,
        leader_question=None,
        kind=Question.MULTIPLE_QUESTIONS,
    )
    question6 = f.create_question(
        next_question=None,
        previous_question=None,
        nested_question=None,
        leader_question=question5,
    )
    question7 = f.create_question(
        next_question=None,
        previous_question=None,
        nested_question=None,
        leader_question=question5,
    )
    question1.previous_question = question2
    question1.save()

    response = client.json.get(url)
    assert response.status_code == 200
    expected_keys = [
        "id",
        "kind",
        "text",
        "placeholder",
        "is_required",
        "min_length",
        "max_length",
        "is_start",
        "next_question",
        "previous_question",
        "choices",
        "nested_question",
        "show_safety_screen",
    ]
    assert set(expected_keys).issubset(response.data.get("results")[0].keys())
    assert len(response.data.get("results")) == 5
    assert response.data["results"][0].get("id") == str(question5.id)
    assert response.data["results"][0].get("next_question") is None
    assert response.data["results"][0].get("nested_question") is None
    assert response.data["results"][0].get("previous_question") == question3.id
    assert len(response.data["results"][0].get("multiple_questions")) == 2
    assert response.data["results"][0].get("multiple_questions")[0].get("id") == str(
        question7.id
    )
    assert response.data["results"][0].get("multiple_questions")[1].get("id") == str(
        question6.id
    )
    assert response.data["results"][1].get("id") == str(question3.id)
    assert response.data["results"][1].get("next_question") == question2.id
    assert response.data["results"][1].get("nested_question") == question4.id
    assert response.data["results"][1].get("previous_question") is None
    assert response.data["results"][2].get("id") == str(question4.id)
    assert response.data["results"][2].get("next_question") is None
    assert response.data["results"][2].get("previous_question") is None
    assert response.data["results"][3].get("id") == str(question2.id)
    assert response.data["results"][3].get("next_question") == question1.id
    assert response.data["results"][3].get("previous_question") is None
    assert response.data["results"][4].get("id") == str(question1.id)
    assert response.data["results"][4].get("next_question") is None
    assert response.data["results"][4].get("previous_question") == question2.id


def test_get_start_questions(client):
    url = reverse("questions-starting-question")
    question = f.create_question(
        next_question=None,
        previous_question=None,
        nested_question=None,
        leader_question=None,
        is_start=True,
    )
    f.create_question(
        next_question=question,
        previous_question=None,
        nested_question=None,
        leader_question=None,
        is_start=False,
    )

    response = client.json.get(url)
    assert response.status_code == 200
    expected_keys = [
        "id",
        "kind",
        "text",
        "placeholder",
        "is_required",
        "min_length",
        "max_length",
        "is_start",
        "next_question",
        "previous_question",
        "choices",
        "nested_question",
        "show_safety_screen",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("id") == str(question.id)


def test_get_appointment_start_questions(client):
    url = reverse("questions-appointment-starting-question")
    question = f.create_question(
        next_question=None,
        previous_question=None,
        nested_question=None,
        leader_question=None,
        is_appointment_start=True,
    )
    f.create_question(
        next_question=question,
        previous_question=None,
        nested_question=None,
        leader_question=None,
        is_appointment_start=False,
    )

    response = client.json.get(url)
    assert response.status_code == 200
    expected_keys = [
        "id",
        "kind",
        "text",
        "placeholder",
        "is_required",
        "min_length",
        "max_length",
        "is_start",
        "next_question",
        "previous_question",
        "choices",
        "nested_question",
        "show_safety_screen",
    ]
    assert set(expected_keys).issubset(response.data.keys())
    assert response.data.get("id") == str(question.id)


# Commenting it out as this feature is de-prioritized
# def test_get_questions_per_organisation(client):
#     url = reverse('questions-starting-question')
#     org2 = org_f.create_organisation(domain='test2.example.com', parent=None)
#     org_f.create_organisation(domain='test.example.com', parent=None)
#
#     question1 = f.create_question(next_question=None, previous_question=None, nested_question=None,
#                                   leader_question=None, is_start=True)
#     question2 = f.create_question(next_question=question1, previous_question=question1, nested_question=None,
#                                   leader_question=None)
#     question3 = f.create_question(next_question=None, previous_question=question1, nested_question=None,
#                                   leader_question=None)
#     option = f.create_option(question=question1, next_question=question2, previous_question=None)
#     f.create_organisation_next_question(organisation=org2, question=None, option=option, next_question=question3,
#                                         previous_question=None)
#
#     headers = {
#         'Referer': 'https://test.example.com/',
#         'Origin': 'https://test.example.com'
#     }
#     response = client.json.get(url, HTTP_ORIGIN='http://test.example.com', headers=headers)
#     expected_keys = ['id', 'kind', 'text', 'placeholder', 'is_required', 'min_length', 'max_length',
#                      'is_start', 'next_question', 'previous_question', 'choices', 'nested_question']
#     assert response.status_code == 200
#     assert set(expected_keys).issubset(response.data.keys())
#     assert response.data.get('id') == str(question1.id)
#     assert response.data.get('choices')[0].get('id') == str(option.id)
#     assert response.data.get('choices')[0].get('next_question') == question2.id
#
#     headers2 = {
#         'Referer': 'https://test2.example.com/',
#         'Origin': 'https://test2.example.com'
#     }
#     response = client.json.get(url, HTTP_ORIGIN='http://test2.example.com', headers=headers2)
#     assert response.status_code == 200
#     assert response.data.get('id') == str(question1.id)
#     assert response.data.get('choices')[0].get('id') == str(option.id)
#     assert response.data.get('choices')[0].get('next_question') == question3.id
