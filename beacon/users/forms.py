# -*- coding: utf-8 -*-
# Third Party Stuff
from django import forms
from django.core.validators import FileExtensionValidator, RegexValidator
from phonenumber_field.validators import validate_international_phonenumber

# beacon Stuff
from beacon.answers import constants
from beacon.base.models import UserCSVUpload
from beacon.organisations.models import Organisation
from beacon.questionnaire.models import Question

from . import choices, models
from .services import get_user_by_email


class RegisterForm(forms.Form):
    connects_mbr_id = forms.CharField(
        label="Connects Member ID",
        max_length=15,
        required=False,
        help_text="If TEMP ID, leave field blank",
    )
    organisation = forms.ModelChoiceField(
        queryset=Organisation.objects.filter(is_active=True)
    )
    email = forms.EmailField(
        required=True,
        max_length=50,
        help_text="Confirm correct email before submitting",
    )
    first_name = forms.CharField(max_length=35)
    last_name = forms.CharField(max_length=60, min_length=3)
    birthdate = forms.DateField(
        input_formats=["%m/%d/%Y"], help_text="Enter a date of format mm/dd/yyyy"
    )
    gender = forms.ChoiceField(choices=choices.GENDER_CHOICES, required=True)
    phone = forms.CharField(max_length=15)
    address1 = forms.CharField(max_length=55)
    # Save None in DB if no data provided, because in `User` model `address2` is null=True and blank=False
    address2 = forms.CharField(required=False, max_length=55, empty_value=None)
    city = forms.CharField(max_length=30)
    state = forms.ChoiceField(choices=choices.STATE_CHOICES, required=True)
    appointment_state = forms.ChoiceField(
        choices=choices.STATE_CHOICES, label="MDLive Appointment State", required=True
    )
    zip = forms.CharField(
        max_length=5,
        min_length=5,
        validators=[
            RegexValidator(
                regex=r"\b\d{5}\b", message="Enter a zip code in the format XXXXX"
            )
        ],
    )
    employment_status = forms.ChoiceField(choices=choices.EMPLOYMENT_STATUS_CHOICES)
    job_title = forms.ChoiceField(choices=choices.JOB_TITLE_CHOICE)
    relationship_status = forms.ChoiceField(choices=choices.RELATIONSHIP_STATUS_CHOICES)
    chief_complaint1 = forms.CharField(required=False, max_length=50)
    chief_complaint2 = forms.CharField(required=False, max_length=50)
    admin_force_registration = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["gender"].choices = [
            (None, "---Please select gender---")
        ] + choices.GENDER_CHOICES
        self.fields["state"].choices = [
            (None, "---Please select state---")
        ] + choices.STATE_CHOICES
        self.fields["appointment_state"].choices = [
            (None, "---Please select appointment state---")
        ] + choices.STATE_CHOICES
        self.fields["chief_complaint1"].widget = forms.Select()
        question = (
            Question.objects.prefetch_related("choices")
            .filter(is_active=True, user_response_attribute=constants.CHIEF_COMPLAINT1)
            .first()
        )
        if question:
            self.fields["chief_complaint1"].widget.choices = [
                (option.text_mapped_value, option.text)
                for option in question.choices.all()
            ]
        self.fields["chief_complaint2"].widget = forms.Select()
        question = (
            Question.objects.prefetch_related("choices")
            .filter(is_active=True, user_response_attribute=constants.CHIEF_COMPLAINT2)
            .first()
        )
        self.fields["chief_complaint2"].widget.choices = [(None, "--- (optional) ---")]
        if question:
            self.fields["chief_complaint2"].widget.choices += [
                (option.text_mapped_value, option.text)
                for option in question.choices.all()
            ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user = get_user_by_email(email=email)
        if user:
            raise forms.ValidationError("Email is already taken!")
        return models.UserManager.normalize_email(email)

    def clean_phone(self):
        # Save phone number with country code as Cognito raises error without it
        # The phone validator checks number with US country code as default
        # Here we just need to add `+1` if doesn't exists
        phone = self.cleaned_data.get("phone")
        value_without_hiphens = phone.replace("-", "")
        if value_without_hiphens:
            if value_without_hiphens.startswith("+1") is False:
                value_without_hiphens = "+1{}".format(value_without_hiphens)
            if len(value_without_hiphens) > 12:
                raise forms.ValidationError(
                    'Only valid US numbers of format "+1xxxxxxxxxx, +1-xxx-xxx-xxxx,'
                    ' xxxxxxxxxx, xxx-xxx-xxxx" are allowed!'
                )
            new_val = value_without_hiphens
            validate_international_phonenumber(new_val)
        return value_without_hiphens

    def clean_chief_complaint2(self):
        # If "chief_complaint2" is "" (blank), then save `None` in the DB. Because blank is not a valid answer for this
        # question. Saving an invalid answer value results in answer validation errors later on for the user.
        if self.cleaned_data.get("chief_complaint2") == "":
            return None

    def clean(self):
        chief_complaint1 = self.cleaned_data.get("chief_complaint1")
        chief_complaint2 = self.cleaned_data.get("chief_complaint2")

        if chief_complaint1 == chief_complaint2:
            raise forms.ValidationError(
                "Chief Complaint1 and Chief Complaint2 can't be same!"
            )
        return self.cleaned_data


class ConfirmRegisterForm(forms.Form):
    otp = forms.CharField(required=True, max_length=10)


class UploadUserCSVForm(forms.Form):
    csv_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["csv"])]
    )
    create_users = forms.BooleanField(required=False)

    def clean(self):
        # get_solo will create the item if it does not already exist
        user_csv_upload_instance = UserCSVUpload.get_solo()
        if user_csv_upload_instance.status == UserCSVUpload.IN_PROGRESS:
            raise forms.ValidationError(
                "A file upload is already in progress, please try again after some time!"
            )
