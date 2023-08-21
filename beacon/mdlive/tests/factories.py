# -*- coding: utf-8 -*-
# Standard Library
import json
from collections import namedtuple

# Third Party Stuff
from django_dynamic_fixture import G

# beacon Stuff
from beacon.base.models import SiteConfiguration

from ..models import Contact, Message, Provider, ProviderMessage, UserMessage


def create_provider(**kwargs):
    return G(Provider, **kwargs)


def create_message(**kwargs):
    return G(Message, **kwargs)


def create_contact(*args, **kwargs):
    return G(Contact, **kwargs)


def create_user_message(*args, **kwargs):
    return G(UserMessage, **kwargs)


def create_provider_message(*args, **kwargs):
    return G(ProviderMessage, **kwargs)


def get_mocked_mdlive_token_response():
    # Configuring fake user data
    G(SiteConfiguration, fake_patient={"first_name": "User01"})

    mdlive_res_data = dict(
        jwt="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjUyLCJ1c2VybmFtZSI6ImRlbW9wYXRpZW50MSIsInByaW",
        user=dict(id=52, type="Patient", time_to_live_minutes=60),
    )
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    return mdlive_response(200, json.dumps(mdlive_res_data))


def get_mocked_mdlive_providers_search_response(providers_data=None):
    provider_id = 642183606
    mdlive_res_data = dict(
        providers=[
            dict(
                id=provider_id,
                fullname="Dr. Keylime Pie",
                gender="Female",
                photo_url=None,
                photo_url_absolute="https://patient.mdlive.com/assets/default-profile-picture.png",
                specialty="General Practice",
                group_name=None,
                is_visit_now_available=False,
                status="Available",
                next_appt_available_date="2017-11-09T13:45:00-05:00",
                availability_type=None,
            )
        ],
        refine_search_options=dict(
            default_provider_types=[
                dict(id=3, name="Family Physician", had_consult_24_hr=False),
                dict(id=5, name="Therapist", had_consult_24_hr=False),
                dict(id=6, name="Psychiatrist", had_consult_24_hr=False),
                dict(id=12, name="Dermatologist", had_consult_24_hr=False),
            ],
            availability_type=["phone", "video"],
        ),
    )
    if providers_data is not None:
        mdlive_res_data["providers"].update(providers_data)
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    return mdlive_response(200, json.dumps(mdlive_res_data))


def get_mocked_mdlive_provider_profile_response(provider_data=None):
    provider_id = 642183606
    mdlive_res_data = dict(
        provider_details=dict(
            id=provider_id,
            fullname="Travis Stork",
            gender="Male",
            city="MIAMI BEACH",
            state_abbrev="FL",
            phone="3057997818",
            photo_url="/users/4/photo",
            photo_url_absolute="https://patient.mdlive.com/assets/profile.png",
            years_in_practice=15,
            education="Certified Nurse Educator",
            about_me="This is my profile description",
            licenses=[dict(state_id=10, state="Florida")],
            languages=[dict(id=1, name="English", alpha3_code="eng")],
            specialties=[dict(id=1, name="Abdominal Surgery", code="AS")],
            publications="Over 15 peer review in the field of emergency medicine",
        ),
        availability_details=dict(
            available_hours=[
                dict(
                    timeslot="2018-01-10T15:00:00.000-05:00",
                    phys_availability_id=6096481,
                    availability_type=["video"],
                )
            ],
            is_visit_now_available=True,
            can_request_appointment=True,
            appointment_date="2018-01-15",
            patient_appointment_types=["video", "phone"],
        ),
    )
    if provider_data is not None:
        mdlive_res_data["provider_details"].update(provider_data)
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    return mdlive_response(200, json.dumps(mdlive_res_data))


def get_mocked_mdlive_contacts_response(contacts_data=None):
    provider_id = 642183606
    mdlive_res_data = dict(
        contacts=[
            {
                "id": provider_id,
                "prefix": "",
                "fullname": "Travis Stork",
                "gender": "Male",
                "photo_url": "/users/35/photo",
                "specialty": "General Practice",
                "specialities": ["Anxiety", "Depression"],
                "provider_card": {
                    "photo_in_binary_data": "nsdkjdhflaksjdgksdhghgasfkdsgjhds....",
                    "photo_format": "jpg",
                },
            }
        ]
    )
    if contacts_data is not None:
        mdlive_res_data["contacts"] = contacts_data
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    return mdlive_response(200, json.dumps(mdlive_res_data))


def get_mocked_mdlive_messages_response(user, messages_data=None):
    provider_id = 642183606
    mdlive_res_data = dict(
        messages=[
            {
                "id": 393835,
                "date_time": "2019-12-11T08:48:12-05:00",
                "from": "LCSW Jose Aponte",
                "from_id": provider_id,
                "to": "Test User",
                "to_id": user.mdlive_id,
                "subject": "Testing webhook",
                "message": "Its User! Testing mdlive.",
                "message_action": {},
                "unread_status": True,
                "confirm_appointment_data": {},
            }
        ]
    )
    if messages_data is not None:
        mdlive_res_data["messages"] = messages_data
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    return mdlive_response(200, json.dumps(mdlive_res_data))


def get_mocked_mdlive_create_messages_response(user, messages_data=None):
    provider_id = 642183606
    mdlive_res_data = dict(
        message={
            "id": 105,
            "date_time": "2018-01-23T02:33:13+00:00",
            "from": "Test Marino",
            "from_id": user.mdlive_id,
            "to": "Travis C Stork",
            "to_id": provider_id,
            "subject": "Prescription",
            "message": "Hello, I received a prescription for extra strength Ibuprofen.",
            "unread_status": True,
            "replied_to_message_id": None,
        }
    )
    if messages_data is not None:
        mdlive_res_data["message"].update(messages_data)
    mdlive_response = namedtuple("mdlive_response", ["status_code", "content"])
    return mdlive_response(201, json.dumps(mdlive_res_data)), mdlive_res_data
