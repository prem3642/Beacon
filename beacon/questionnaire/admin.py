# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Option, Question


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    raw_id_fields = ("question", "next_question", "previous_question")
    readonly_fields = (
        "text",
        "text_mapped_value",
        "question",
        "next_question",
        "previous_question",
        "created_at",
        "modified_at",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions


class OptionInline(admin.TabularInline):
    model = Option
    fk_name = "question"
    raw_id_fields = ("next_question", "previous_question")
    readonly_fields = (
        "text",
        "text_mapped_value",
        "question",
        "next_question",
        "previous_question",
        "created_at",
        "modified_at",
    )
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class CustomQuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = "__all__"

    def clean(self):
        super().clean()
        if not self.is_valid():
            return  # other errors exists

        # TODO: Add handling of Multiple Questions type
        kind = self.cleaned_data.get("kind")
        yes_text = self.cleaned_data.get("yes_button_text")
        no_text = self.cleaned_data.get("no_button_text")
        is_start = self.cleaned_data.get("is_start")
        is_appointment_start = self.cleaned_data.get("is_appointment_start")
        choices_count = int(self.data.get("choices-TOTAL_FORMS", 0))
        if (
            kind == Question.DROPDOWN
            or kind == Question.CHECKBOX
            or kind == Question.RADIO
        ) and choices_count == 0:  # or kind == Question.MULTIPLE_CHOICE
            raise ValidationError(
                "Choices required with Dropdown/Checkbox/Radio question types"
            )
        if (
            kind == Question.TERMINAL
            or kind == Question.TEXT
            or kind == Question.TEXT_BOX
            or kind == Question.NUMBER
            or kind == Question.YES_NO
        ) and choices_count > 0:
            raise ValidationError(
                "Choices are not allowed with Terminal/Text/TextBox/Number/YesNo Types"
            )

        if kind == Question.YES_NO:
            if not yes_text or not no_text:
                raise ValidationError(
                    "Yes/No button text are required with Yes/No type question!"
                )
        else:
            self.cleaned_data["yes_button_text"] = None
            self.cleaned_data["no_button_text"] = None

        if is_start is True:
            starting_question = Question.objects.filter(is_start=True).first()
            if (
                starting_question
                and self.instance
                and self.instance.id != starting_question.id
            ):
                raise ValidationError("Only one starting question is allowed!")

        if is_appointment_start is True:
            appointment_starting_question = Question.objects.filter(
                is_appointment_start=True
            ).first()
            if (
                appointment_starting_question
                and self.instance
                and self.instance.id != appointment_starting_question.id
            ):
                raise ValidationError(
                    "Only one appointment starting question is allowed!"
                )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = CustomQuestionForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user_response_attribute",
                    "user_appointment_attribute",
                    "kind",
                    "text",
                    "subheading",
                    "placeholder",
                    "is_required",
                    "min_length",
                    "max_length",
                    "regex",
                    "is_active",
                    "is_start",
                    "is_appointment_start",
                    "show_safety_screen",
                    "yes_button_text",
                    "no_button_text",
                    "next_question",
                    "previous_question",
                    "nested_question",
                    "leader_question",
                )
            },
        ),
        ("Important dates", {"fields": ("created_at", "modified_at")}),
    )
    search_fields = ("text", "user_response_attribute")
    list_filter = (
        "is_active",
        "kind",
        "is_required",
        "is_start",
        "is_appointment_start",
    )
    list_display = (
        "id",
        "kind",
        "user_response_attribute",
        "user_appointment_attribute",
        "is_active",
        "is_start",
        "is_appointment_start",
        "text",
    )
    raw_id_fields = (
        "next_question",
        "previous_question",
        "nested_question",
        "leader_question",
    )
    readonly_fields = (
        "user_response_attribute",
        "user_appointment_attribute",
        "kind",
        "text",
        "subheading",
        "placeholder",
        "is_required",
        "min_length",
        "max_length",
        "regex",
        "is_active",
        "is_start",
        "is_appointment_start",
        "yes_button_text",
        "no_button_text",
        "next_question",
        "previous_question",
        "nested_question",
        "leader_question",
        "created_at",
        "modified_at",
        "show_safety_screen",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions

    inlines = (OptionInline,)


# Commenting it out as this feature is de-prioritized
# @admin.register(OrganisationNextQuestion)
# class OrganisationNextQuestionAdmin(admin.ModelAdmin):
#     fieldsets = (
#         (None, {'fields': ('organisation', 'question', 'option', 'next_question', 'previous_question')}),
#         ('Important dates', {'fields': ('created_at', 'modified_at')}),
#     )
#     search_fields = ('organisation__parent_code', 'organisation__domain', 'question__text', 'option__text',
#                      'next_question__text', 'previous_question__text')
#     list_display = ('organisation', 'question', 'option', 'next_question', 'previous_question')
#     raw_id_fields = ('organisation', 'question', 'option', 'next_question', 'previous_question')
#     readonly_fields = ('created_at', 'modified_at')
