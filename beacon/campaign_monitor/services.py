# -*- coding: utf-8 -*-
# Standard Library
from datetime import datetime

# Third Party Stuff
import createsend
from django.conf import settings


def get_custom_fields_for_user(
    user_data, organisation_data, user_response_data, organisation_parent_data=None
):
    chief_complaint_mapping = {
        "Anxiety": "AX",
        "Depression": "DP",
        "Family Issues": "FI",
        "Grief or Loss": "GL",
        "Relationship Issues": "RI",
        "Stress": "ST",
        "Alcohol or Drug use": "AD",
    }

    date_joined = (
        user_data.get("date_joined")
        if user_data.get("date_joined") is not None
        else datetime.today().date()
    )
    custom_fields = [
        {"key": "First Name", "value": user_data.get("first_name")},
        {"key": "Last Name", "value": user_data.get("last_name")},
        {"key": "RegistrationDate", "value": date_joined.strftime("%Y/%m/%d")},
    ]
    if organisation_data:
        parent_code = organisation_data.get("parent_code")
        if parent_code is None and organisation_parent_data is not None:
            parent_code = organisation_parent_data.get("parent_code")
        program_name = organisation_data.get("program_name")
        if program_name is None and organisation_parent_data is not None:
            program_name = organisation_parent_data.get("program_name")
        number_of_sessions = organisation_data.get("number_of_sessions")
        if number_of_sessions is None and organisation_parent_data is not None:
            number_of_sessions = organisation_parent_data.get("number_of_sessions")
        custom_fields.append({"key": "ParentCode", "value": parent_code})
        custom_fields.append({"key": "URL", "value": organisation_data.get("domain")})
        custom_fields.append({"key": "ProgramName", "value": program_name})
        custom_fields.append({"key": "SessionNumber", "value": number_of_sessions})
        custom_fields.append(
            {"key": "ProgramTNF", "value": organisation_data.get("phone")}
        )
    if user_response_data:
        custom_fields.extend(
            [
                {"key": "RequestType", "value": user_response_data.get("request_type")},
                {
                    "key": "Emotional Support For",
                    "value": user_response_data.get("emotional_support_for"),
                },
                {
                    "key": "Presenting Problem",
                    "value": chief_complaint_mapping.get(
                        user_response_data.get("chief_complaint1")
                    ),
                },
                {
                    "key": "OtherReason",
                    "value": user_response_data.get("chief_complaint2"),
                },
                {
                    "key": "Emotional",
                    "value": user_response_data.get("how_emotionally_doing"),
                },
                {
                    "key": "Physical",
                    "value": user_response_data.get("how_physical_health"),
                },
                {"key": "Community", "value": user_response_data.get("people_support")},
                {
                    "key": "Financial",
                    "value": user_response_data.get("comfortable_in_managing_finances"),
                },
                {
                    "key": "Resiliency",
                    "value": user_response_data.get("resources_to_manage"),
                },
                {
                    "key": "SD1",
                    "value": user_response_data.get(
                        "difficulty_in_keeping_drinking_limit"
                    ),
                },
                {
                    "key": "SD2",
                    "value": user_response_data.get("felt_cut_down_drinking"),
                },
            ]
        )
    return custom_fields


def add_new_subscriber_from_data(
    user_data, organisation_data, user_response_data, organisation_parent_data
):
    """
    Add a new subscriber to campaign monitor list
    :param user_data: user object data as dict
    :param organisation_data: organisation object data as dict
    :param user_response_data: user response object data as dict
    :param organisation_parent_data: organisation parent object data as dict
    :return: Response, Error
    """
    auth = {"api_key": settings.CAMPAIGN_MONITOR_API_KEY}
    subscriber_client = createsend.Subscriber(
        auth=auth, list_id=settings.CAMPAIGN_MONITOR_LIST_ID
    )
    try:
        response = subscriber_client.add(
            list_id=settings.CAMPAIGN_MONITOR_LIST_ID,
            email_address=user_data.get("email"),
            name=f"{user_data.get('first_name')} {user_data.get('last_name')}",
            custom_fields=get_custom_fields_for_user(
                user_data,
                organisation_data,
                user_response_data,
                organisation_parent_data,
            ),
            resubscribe=False,
            consent_to_track="no",
        )
    except createsend.BadRequest as e:
        return None, e
    except createsend.Unauthorized as e:
        return None, e
    except createsend.ClientError as e:
        return None, e
    except createsend.ServerError as e:
        return None, e
    return response, None


def add_new_subscriber(user):
    """
    Add a new subscriber to campaign monitor list
    :param user: user object
    :return: Response, Error
    """
    response, error = add_new_subscriber_from_data(
        user.__dict__,
        user.organisation.__dict__ if user.organisation else None,
        user.answer.__dict__ if hasattr(user, "answer") else None,
        user.organisation.parent.__dict__
        if user.organisation and user.organisation.parent
        else None,
    )
    if error is None:
        if user.is_sent_to_campaign_monitor is False:
            user.is_sent_to_campaign_monitor = True
            user.save()
    return response, None


def add_multiple_subscribers_from_data(users_data):
    """
    Add multiple subscribers to campaign monitor list
    :param users_data: [(user_data, organisation_data, user_response_data, organisation.parent_data),...]
    :return: Response, Error
    """
    auth = {"api_key": settings.CAMPAIGN_MONITOR_API_KEY}
    subscriber_client = createsend.Subscriber(
        auth=auth, list_id=settings.CAMPAIGN_MONITOR_LIST_ID
    )
    subscribers = [
        {
            "EmailAddress": user_data[0].get("email"),
            "Name": f"{user_data[0].get('first_name')} {user_data[0].get('last_name')}",
            "CustomFields": get_custom_fields_for_user(
                user_data[0], user_data[1], user_data[2], user_data[3]
            ),
            "ConsentToTrack": "No",
        }
        for user_data in users_data
    ]
    try:
        response = subscriber_client.import_subscribers(
            list_id=settings.CAMPAIGN_MONITOR_LIST_ID,
            subscribers=subscribers,
            resubscribe=False,
        )
    except createsend.BadRequest as e:
        return None, e
    except createsend.Unauthorized as e:
        return None, e
    except createsend.ClientError as e:
        return None, e
    except createsend.ServerError as e:
        return None, e
    return response, None


def add_multiple_subscribers(users):
    """
    Add multiple subscribers to campaign monitor list
    :param users: users queryset
    :return: Response, Error
    """
    users = users.select_related("organisation__parent")
    users_data = [
        (
            user.__dict__,
            user.organisation.__dict__ if user.organisation else None,
            user.answer.__dict__ if hasattr(user, "answer") else None,
            user.organisation.parent.__dict__
            if user.organisation and user.organisation.parent
            else None,
        )
        for user in users
    ]
    response, error = add_multiple_subscribers_from_data(users_data)
    if error is None:
        users.update(is_sent_to_campaign_monitor=True)
    return response, None
