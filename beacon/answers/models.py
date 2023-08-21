# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

# beacon Stuff
from beacon.base.models import TimeStampedUUIDModel
from beacon.organisations.models import Organisation


class UserResponse(TimeStampedUUIDModel):
    """Store answers from each individual"""

    VIDEO = "video"
    PHONE = "phone"
    FACE_TO_FACE = "face_to_face"
    APPOINTMENT_CHOICES = [VIDEO, PHONE, FACE_TO_FACE]

    response = JSONField()
    # Creating a backup of response JSON. Because SCC can update the existing answers of a user to "null", which if
    # creates any unforeseeable issue in future, we can use this response backup to get the working data back. And this
    # also helps in tracking answer changes.
    response_backup = JSONField(null=True, default=None)

    request_type = models.CharField(max_length=30, null=True, default="Emotional")
    emotional_support_for = models.CharField(max_length=20, null=True, blank=True)
    appointment_state = models.CharField(max_length=2, null=True, blank=True)
    chief_complaint1 = models.CharField(max_length=50, null=True, blank=True)
    chief_complaint2 = models.CharField(max_length=50, null=True, blank=True)
    self_harm = models.BooleanField(null=True, blank=True)
    safety_sensitive_position = models.BooleanField(null=True, blank=True, default=None)
    how_often_less_interest_in_things = models.CharField(
        max_length=50, null=True, blank=True
    )
    how_often_depressed = models.CharField(max_length=50, null=True, blank=True)
    how_often_nervous = models.CharField(max_length=50, null=True, blank=True)
    how_often_worry = models.CharField(max_length=50, null=True, blank=True)
    difficulty_in_keeping_drinking_limit = models.BooleanField(null=True, blank=True)
    felt_cut_down_drinking = models.BooleanField(null=True, blank=True)
    how_emotionally_doing = models.CharField(max_length=50, null=True, blank=True)
    how_physical_health = models.CharField(max_length=50, null=True, blank=True)
    comfortable_in_managing_finances = models.CharField(
        max_length=30, null=True, blank=True
    )
    people_support = models.CharField(max_length=30, null=True, blank=True)
    resources_to_manage = models.CharField(max_length=30, null=True, blank=True)
    number_of_days_less_productive = models.PositiveIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(30)]
    )
    number_of_days_missed_work = models.PositiveIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(30)]
    )
    # User null is True as user response is created first and user gets registered later
    # So, in register api FE send the user_response id through which we link the user
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="answer",
    )
    last_answered_question = models.CharField(
        _("Last Answered Question"), null=True, blank=True, max_length=50
    )
    is_employee = models.BooleanField(null=True, blank=True)
    relationship_with_employee = models.CharField(max_length=20, null=True, blank=True)
    employee_name = models.CharField(
        _("employee full name"),
        max_length=50,
        null=True,
        blank=True,
        help_text="Designates employee full name if user is dependent",
    )
    employee_birth_date = models.DateField(
        _("employee date of birth"),
        null=True,
        help_text="Designates employee DoB if user is dependent",
    )
    employee_organisation = models.ForeignKey(
        Organisation,
        null=True,
        blank=True,
        related_name="user_responses",
        on_delete=models.SET_NULL,
        help_text="Designates the employee organisation if user is dependent",
    )

    class Meta:
        db_table = "answer"
        verbose_name = _("answer")
        verbose_name_plural = _("answers")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return "{} - {}".format(self.id, self.user)


class UserAppointment(TimeStampedUUIDModel):
    VIDEO = "video"
    PHONE = "phone"
    FACE_TO_FACE = "face_to_face"
    APPOINTMENT_CHOICES = [VIDEO, PHONE, FACE_TO_FACE]

    response = JSONField(null=True)

    user_response = models.ForeignKey(
        UserResponse, on_delete=models.PROTECT, related_name="appointments"
    )
    # `appointment_state` is being duplicated here to keep track
    # of the original appointment_state this appointment was created
    # for. Due to a new feature, it is possible to update appointment_state
    # in UserResponse. We are just maintaining the history through
    # this field for an appointment.
    appointment_state = models.CharField(max_length=2, null=True, blank=True)
    mdlive_provider_id = models.IntegerField(
        _("MdLive selected provider id"), null=True, blank=True
    )
    selected_time_slot = models.CharField(
        _("Selected Time Slot"), null=True, blank=True, max_length=40
    )
    appointment_method = models.CharField(
        _("Appointment Method"),
        null=True,
        blank=True,
        max_length=15,
        choices=zip(APPOINTMENT_CHOICES, APPOINTMENT_CHOICES),
    )
    f2f_gender_preference = models.CharField(
        _("F2F Gender Preference"), null=True, blank=True, max_length=15
    )
    f2f_comfortable_language = models.CharField(
        _("F2F Comfortable Language"), null=True, blank=True, max_length=15
    )
    f2f_preferred_contact = models.CharField(
        _("F2F Preferred Contact"), null=True, blank=True, max_length=10
    )
    f2f_preferred_time = models.CharField(
        _("F2F Preferred Time"), null=True, blank=True, max_length=20
    )
    f2f_okay_to_leave_voicemail = models.BooleanField(
        _("F2F Okay to Leave Voicemail"), null=True, blank=True
    )
    f2f_counselor_search_address = models.CharField(
        _("F2F Counselor Search Address"), max_length=20, null=True, blank=True
    )
    f2f_address1 = models.CharField(
        _("F2F Address1"), max_length=55, null=True, blank=True
    )
    f2f_address2 = models.CharField(
        _("F2F Address2"), null=True, blank=True, max_length=55
    )
    f2f_city = models.CharField(_("F2F City"), max_length=30, null=True, blank=True)
    f2f_zip = models.CharField(
        _("F2F Zip"),
        max_length=10,
        null=True,
        blank=True,
        validators=[
            MinLengthValidator(5),
            RegexValidator(
                regex=r"^\d{5}(?:-\d{4})?$",
                message="Enter a zip code in the format XXXXX or XXXXX-XXXX.",
            ),
        ],
    )
    f2f_state = models.CharField(_("F2F State"), max_length=3, null=True, blank=True)
    f2f_counselor_notes = models.TextField(
        _("F2F Counselor Notes"), null=True, blank=True
    )
    last_answered_question = models.CharField(
        _("Last Answered Question"), null=True, blank=True, max_length=50
    )
    bwb_inquiry_id = models.CharField(_("BWB Inquiry Id"), null=True, max_length=40)

    class Meta:
        db_table = "appointment"
        verbose_name = _("appointment")
        verbose_name_plural = _("appointments")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return "{} - {}".format(self.id, self.user_response)
