# -*- coding: utf-8 -*-
# Third Party Stuff
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from regex_field.fields import RegexField

# beacon Stuff
from beacon.answers.constants import (
    USER_APPOINTMENT_ATTRIBUTE_CHOICES,
    USER_RESPONSE_ATTRIBUTE_CHOICES,
)
from beacon.base.models import TimeStampedUUIDModel

# from beacon.organisations.models import Organisation


class Question(TimeStampedUUIDModel):
    """Store individual question

    There can be different kind of questions, currently
    limited to multiple choice, choice, text and yes/no types.
    """

    MULTIPLE_QUESTIONS = "multiple_questions"
    MULTIPLE_CHOICE = "multiple_choice"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    MULTIPLE_CHECKBOX = "multiple_checkbox"
    TEXT = "text"
    TEXT_BOX = "text_box"
    NUMBER = "number"
    YES_NO = "yes_no"
    YES_NO_OPTIONS = "yes_no_options"
    TERMINAL = "terminal"
    REGEX = "regex"
    DATE = "date"
    ORGANISATION = "organisation"
    # This type will pass json and linking fields for FE and FE will design the question
    # it'll be used for some custom designed questions templates
    FRONTEND = "frontend"

    QUESTION_TYPE_CHOICES = (
        (DROPDOWN, "Dropdown"),
        # (MULTIPLE_CHOICE, 'Multiple Choice'),
        (CHECKBOX, "Checkbox"),
        (RADIO, "Radio"),
        # (MULTIPLE_CHECKBOX, 'Multiple Checkbox'),
        (NUMBER, "Number"),
        (TEXT, "Text"),
        (TEXT_BOX, "Text Box"),
        (YES_NO, "Yes/No"),
        (YES_NO_OPTIONS, "Yes/No Options"),
        (TERMINAL, "Terminal"),
        (MULTIPLE_QUESTIONS, "Multiple Questions"),
        (REGEX, "Regex"),
        (DATE, "Date"),
        (ORGANISATION, "Organisation"),
        (FRONTEND, "Frontend"),
    )

    user_response_attribute = models.CharField(
        _("User Response Attribute"),
        max_length=50,
        null=True,
        blank=True,
        choices=USER_RESPONSE_ATTRIBUTE_CHOICES,
    )
    user_appointment_attribute = models.CharField(
        _("User Appointment Attribute"),
        max_length=50,
        null=True,
        blank=True,
        choices=USER_APPOINTMENT_ATTRIBUTE_CHOICES,
    )
    kind = models.CharField(_("Type"), max_length=20, choices=QUESTION_TYPE_CHOICES)
    backend_kind = models.CharField(
        _("Frontend Type mapped to"),
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        null=True,
        blank=True,
    )
    frontend_url = models.CharField(
        _("Frontend url"),
        max_length=50,
        null=True,
        blank=True,
        help_text='frontend route to render the template if kind is "Frontend"',
    )
    frontend_meta_data = JSONField(
        _("meta data"),
        null=True,
        blank=True,
        help_text="Extra meta data for rendering template on frontend",
    )
    text = models.CharField(
        _("Question"), max_length=300, help_text="Max. 300 characters allowed."
    )
    subheading = models.CharField(
        _("Subheading"),
        max_length=300,
        help_text="Max. 300 characters allowed.",
        null=True,
        blank=True,
    )
    yes_button_text = models.CharField(
        _("Yes Button text for YES/NO type"),
        max_length=50,
        null=True,
        blank=True,
        help_text="Required only for Yes/No question type!",
    )
    no_button_text = models.CharField(
        _("No Button text for YES/NO type"),
        max_length=50,
        null=True,
        blank=True,
        help_text="Required only for Yes/No question type!",
    )
    placeholder = models.CharField(
        _("Placeholder Text"), max_length=100, blank=True, null=False, default=""
    )
    is_required = models.BooleanField(
        _("Is Required?"),
        default=True,
        help_text="Whether user can skip this question.",
    )
    min_length = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum no. of characters or choices or number that the user "
        "must fill/select.",
    )
    max_length = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum no. of characters or choices or number that the user "
        "can fill/select.",
    )
    is_active = models.BooleanField(
        _("Is Published?"),
        default=True,
        help_text="Whether this question is published or not.",
    )
    is_start = models.BooleanField(
        _("Is Starting Question?"),
        default=False,
        help_text="Whether this question is start question or not.",
    )
    next_question = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="parent"
    )
    previous_question = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    nested_question = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nested_parent",
    )
    # Parent Child naming already in use in next-previous question flow
    leader_question = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="follower_questions",
    )
    is_appointment_start = models.BooleanField(
        _("Is Appointment Starting Question?"),
        default=False,
        help_text="Whether this question is start question for " "appointment or not.",
    )
    regex = RegexField(
        _("Regex for Validation"),
        max_length=128,
        null=True,
        help_text="Will be used to validate if question type is Regex",
    )
    regex_error_message = models.CharField(
        _("Regex Error Message"),
        max_length=128,
        null=True,
        help_text="Will be used if value is not getting matched with the regex",
    )
    show_safety_screen = models.BooleanField(
        _("Show Safety Screen"),
        default=False,
        help_text="Designates whether to show safety screen after this question"
        " if not answered yet!",
    )

    class Meta:
        db_table = "question"
        verbose_name = _("question")
        verbose_name_plural = _("questions")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.kind, self.text)


class Option(TimeStampedUUIDModel):
    text = models.CharField(_("Choice text"), max_length=256)
    text_mapped_value = models.CharField(
        _("Text mapped value"), max_length=30, null=True, blank=True
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="choices",
    )
    next_question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parent_options",
    )
    previous_question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children_options",
    )

    class Meta:
        db_table = "option"
        verbose_name = _("option")
        verbose_name_plural = _("options")
        ordering = [
            "created_at",
        ]

    def __str__(self):
        return "{} - {}".format(self.text, self.question.text)


# class OrganisationNextQuestion(TimeStampedUUIDModel):
#     """
#     Next/Previous question mapping based on Organisation
#     """
#     organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='next_question_mapping_org')
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True,
#                                  related_name='next_question_mapping_org')
#     option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True,
#                                related_name='next_question_mapping_org')
#     next_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='parent_question_mapping_org',
#                                       null=True, blank=True)
#     previous_question = models.ForeignKey(Question, on_delete=models.CASCADE,
#                                           related_name='children_question_mapping_org', null=True, blank=True)
#
#     class Meta:
#         db_table = 'organisation_next_question'
#         verbose_name = _('organisation next question')
#         ordering = ['created_at', ]
#
#     def __str__(self):
#         return f'{self.organisation} - {self.question} - {self.option}'


class IntakeQuestionTemplate(TimeStampedUUIDModel):
    name = models.CharField(_("template name"), max_length=30, unique=True)
    is_default = models.BooleanField(_("Is this template default"), default=False)
    show_safety_screen = models.BooleanField(_("Show Safety Screen"), default=False)

    class Meta:
        db_table = "question_template"
        verbose_name = _("question template")
        ordering = ["created_at"]

    def __str__(self):
        return self.name


class TemplateQuestionMapping(TimeStampedUUIDModel):
    template = models.ForeignKey(
        IntakeQuestionTemplate,
        on_delete=models.CASCADE,
        related_name="questions_mapping",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="next_question_mapping",
    )
    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="next_question_mapping",
    )
    next_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="parent_question_mapping",
        null=True,
        blank=True,
    )
    previous_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="children_question_mapping",
        null=True,
        blank=True,
    )
    next_question_service = models.CharField(
        _("Service name"),
        null=True,
        blank=True,
        max_length=75,
        help_text="Service to get the next question instead of direct link",
    )
    previous_question_service = models.CharField(
        _("Service name"),
        null=True,
        blank=True,
        max_length=75,
        help_text="Service to get the previous question",
    )

    class Meta:
        db_table = "template_question_mapping"
        verbose_name = _("template question mapping")
        ordering = ["created_at"]
