# -*- coding: utf-8 -*-
# Standard Library
import uuid

# Third Party Stuff
from django.db.models import Q
from django.utils.encoding import force_str
from rest_framework import filters
from rest_framework.compat import coreapi, coreschema
from rest_framework.exceptions import ValidationError

from .models import Message

TRUE_VALUES = {
    "t",
    "T",
    "y",
    "Y",
    "yes",
    "YES",
    "true",
    "True",
    "TRUE",
    "on",
    "On",
    "ON",
    "1",
    1,
    True,
}
FALSE_VALUES = {
    "f",
    "F",
    "n",
    "N",
    "no",
    "NO",
    "false",
    "False",
    "FALSE",
    "off",
    "Off",
    "OFF",
    "0",
    0,
    0.0,
    False,
}


def validate_uuid(uuid_value, param=None):
    try:
        uuid.UUID(hex=str(uuid_value))
    except ValueError:
        raise ValidationError(f"Invalid {param} id!")


class BaseFilterMixin(filters.BaseFilterBackend):
    param = None
    title = None
    description = None

    def get_schema_fields(self, view):
        assert (
            coreapi is not None
        ), "coreapi must be installed to use `get_schema_fields()`"
        assert (
            coreschema is not None
        ), "coreschema must be installed to use `get_schema_fields()`"
        return [
            coreapi.Field(
                name=self.param,
                required=False,
                location="query",
                schema=coreschema.String(
                    title=force_text(self.title),
                    description=force_text(self.description),
                ),
            )
        ]


class ProviderFilter(BaseFilterMixin):
    param = "provider"
    title = "Provider Filter"
    description = "Filter messages based on provider"

    def filter_queryset(self, request, queryset, view):
        provider_id = request.query_params.get(self.param, None)
        if provider_id:
            try:
                provider_id = int(provider_id)
            except ValueError:
                return queryset
            queryset = queryset.filter(
                Q(
                    message_type=Message.USER_MESSAGE,
                    user_message__message_to__mdlive_id=provider_id,
                )
                | Q(
                    message_type=Message.PROVIDER_MESSAGE,
                    provider_message__message_from__mdlive_id=provider_id,
                )
            )
        return queryset


class UnreadFilter(BaseFilterMixin):
    param = "unread_status"
    title = "Unread Message Filter"
    description = "Filter messages based on unread status"

    def filter_queryset(self, request, queryset, view):
        unread_status = request.query_params.get(self.param, None)
        if unread_status:
            if unread_status in TRUE_VALUES:
                queryset = queryset.filter(is_read=False)
            if unread_status in FALSE_VALUES:
                queryset = queryset.filter(is_read=True)
        return queryset


class SentMessageFilter(BaseFilterMixin):
    param = "sent"
    title = "Sent Message Filter"
    description = "Filter received messages"

    def filter_queryset(self, request, queryset, view):
        sent_message_flag = request.query_params.get(self.param, None)
        if sent_message_flag is not None and sent_message_flag in TRUE_VALUES:
            queryset = queryset.filter(message_type=Message.USER_MESSAGE)
        return queryset


class ReceivedMessageFilter(BaseFilterMixin):
    param = "received"
    title = "Received Message Filter"
    description = "Filter received messages"

    def filter_queryset(self, request, queryset, view):
        received_message_flag = request.query_params.get(self.param, None)
        if received_message_flag is not None and received_message_flag in TRUE_VALUES:
            queryset = queryset.filter(message_type=Message.PROVIDER_MESSAGE)
        return queryset
