# -*- coding: utf-8 -*-
# Standard Library
import json

# Third Party Stuff
from django.contrib import admin
from django.forms import Select
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

# beacon Stuff
from beacon.base.utils.admin_filters import NullFieldListFilter
from beacon.questionnaire.choices import get_question_choices
from beacon.users.tasks import send_multiple_f2f_appointments_data_task

from .models import UserAppointment, UserResponse
from .services import backup_user_response_json, generate_user_response_json
from .utils import ordered


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "request_type",
                    "emotional_support_for",
                    "appointment_state",
                    "self_harm",
                    "safety_sensitive_position",
                    "chief_complaint1",
                    "chief_complaint2",
                    "how_often_less_interest_in_things",
                    "how_often_depressed",
                    "how_often_nervous",
                    "how_often_worry",
                    "difficulty_in_keeping_drinking_limit",
                    "felt_cut_down_drinking",
                    "how_emotionally_doing",
                    "how_physical_health",
                    "comfortable_in_managing_finances",
                    "people_support",
                    "resources_to_manage",
                    "number_of_days_less_productive",
                    "number_of_days_missed_work",
                    "is_employee",
                    "relationship_with_employee",
                    "employee_name",
                    "employee_birth_date",
                    "employee_organisation",
                    "last_answered_question",
                    "response_prettified",
                )
            },
        ),
        ("Important dates", {"fields": ("created_at", "modified_at")}),
    )
    readonly_fields = (
        "created_at",
        "modified_at",
        "response_prettified",
        "last_answered_question",
        "emotional_support_for",
        "appointment_state",
        "chief_complaint1",
        "chief_complaint2",
        "how_often_less_interest_in_things",
        "how_often_depressed",
        "how_often_nervous",
        "how_often_worry",
        "difficulty_in_keeping_drinking_limit",
        "felt_cut_down_drinking",
        "how_emotionally_doing",
        "how_physical_health",
        "comfortable_in_managing_finances",
        "people_support",
        "resources_to_manage",
        "number_of_days_less_productive",
        "number_of_days_missed_work",
        "is_employee",
        "relationship_with_employee",
        "employee_name",
        "employee_birth_date",
        "employee_organisation",
        "self_harm",
        "safety_sensitive_position",
        "request_type",
    )
    search_fields = ("user__id", "user__email")
    list_display = ("id", "user")
    raw_id_fields = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")

    def response_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.response, sort_keys=True, indent=2)

        # Get the Pygments formatter
        formatter = HtmlFormatter(style="igor")

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    response_prettified.short_description = "response"

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            return super().get_form(request, obj, **kwargs)

        # For superusers make the following fields editable.
        editable_fields = ("appointment_state", "chief_complaint1", "chief_complaint2")
        readonly_fields = [x for x in self.readonly_fields if x not in editable_fields]
        self.readonly_fields = tuple(readonly_fields)
        form = super().get_form(request, obj, **kwargs)

        # By default all answer fields in `UserResponse` model are char fields.
        # Therefore, adding `Select` to render these fields as choice fields (dropdown) on admin.
        STATE_CHOICES = get_question_choices("appointment_state", is_optional=True)
        form.base_fields["appointment_state"].widget = Select(choices=STATE_CHOICES)
        CHIEF_COMPLAINT_1_CHOICES = get_question_choices(
            "chief_complaint1", is_optional=True
        )
        form.base_fields["chief_complaint1"].widget = Select(
            choices=CHIEF_COMPLAINT_1_CHOICES
        )
        CHIEF_COMPLAINT_2_CHOICES = get_question_choices(
            "chief_complaint2", is_optional=True
        )
        form.base_fields["chief_complaint2"].widget = Select(
            choices=CHIEF_COMPLAINT_2_CHOICES
        )
        return form

    def save_model(self, request, obj, form, change):
        """Generates and validates response JSON of answers before saving the object"""
        user_response = form.instance
        old_response_json = user_response.response.copy()
        new_response_json = generate_user_response_json(user_response=user_response)
        if old_response_json:
            if ordered(old_response_json) != ordered(new_response_json):
                backup_user_response_json(
                    answer_obj=user_response, response_json=old_response_json
                )
        user_response.response = new_response_json
        super().save_model(request, obj, form, change)


@admin.register(UserAppointment)
class UserAppointmentAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user_response",
                    "mdlive_provider_id",
                    "selected_time_slot",
                    "appointment_method",
                    "f2f_gender_preference",
                    "f2f_comfortable_language",
                    "f2f_preferred_contact",
                    "f2f_preferred_time",
                    "f2f_okay_to_leave_voicemail",
                    "f2f_counselor_search_address",
                    "f2f_address1",
                    "f2f_address2",
                    "f2f_city",
                    "f2f_state",
                    "f2f_zip",
                    "f2f_counselor_notes",
                    "bwb_inquiry_id",
                    "response_prettified",
                )
            },
        ),
        ("Important dates", {"fields": ("created_at", "modified_at")}),
    )
    readonly_fields = (
        "created_at",
        "modified_at",
        "mdlive_provider_id",
        "selected_time_slot",
        "appointment_method",
        "f2f_gender_preference",
        "f2f_comfortable_language",
        "f2f_preferred_contact",
        "f2f_preferred_time",
        "f2f_okay_to_leave_voicemail",
        "f2f_counselor_search_address",
        "f2f_address1",
        "f2f_address2",
        "f2f_city",
        "f2f_state",
        "f2f_zip",
        "f2f_counselor_notes",
        "bwb_inquiry_id",
        "response_prettified",
        "created_at",
        "modified_at",
    )
    search_fields = ("id", "user_response__user__id", "user_response__user__email")
    list_display = ("id", "appointment_method", "bwb_inquiry_id", "created_at")
    list_filter = ("appointment_method", ("bwb_inquiry_id", NullFieldListFilter))
    raw_id_fields = ("user_response",)
    actions = ["send_data_to_beacon_server"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user_response__user")

    def response_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.response, sort_keys=True, indent=2)

        # Get the Pygments formatter
        formatter = HtmlFormatter(style="igor")

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    response_prettified.short_description = "response"

    def send_data_to_beacon_server(self, request, queryset):
        user_appointment_ids = list(queryset.values_list("id", flat=True))
        send_multiple_f2f_appointments_data_task.delay(user_appointment_ids)
        self.message_user(request, "Sending data to beacon server has been started!")

    send_data_to_beacon_server.short_description = (
        "Send selected users data to beacon server"
    )
