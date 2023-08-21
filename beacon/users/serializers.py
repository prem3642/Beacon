# -*- coding: utf-8 -*-
# Third Party Stuff
from django.conf import settings
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    NumericPasswordValidator,
)
from django.core.validators import RegexValidator
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers

# beacon Stuff
from beacon.answers.models import UserResponse
from beacon.base.password_validators import ComplexPasswordValidator
from beacon.organisations.models import Organisation

from . import choices, models, services, tokens


class UserSerializer(serializers.ModelSerializer):
    chief_complaint1 = serializers.SerializerMethodField()
    chief_complaint2 = serializers.SerializerMethodField()
    appointment_state = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "address1",
            "address2",
            "city",
            "zip",
            "gender",
            "state",
            "employment_status",
            "relationship_status",
            "job_title",
            "mdlive_id",
            "is_verified",
            "agrees_to_beacon_privacy_notice",
            "agrees_to_mdlive_informed_consent",
            "agrees_to_mdlive_privacy_agreement",
            "mdlive_consent_user_initials",
            "chief_complaint1",
            "chief_complaint2",
            "appointment_state",
            "timezone",
        ]

    def get_chief_complaint1(self, obj):
        user_response = self.context.get("user_response")
        if user_response:
            return user_response.chief_complaint1
        return None

    def get_chief_complaint2(self, obj):
        user_response = self.context.get("user_response")
        if user_response:
            return user_response.chief_complaint2
        return None

    def get_appointment_state(self, obj):
        user_response = self.context.get("user_response")
        if user_response:
            return user_response.appointment_state
        return None


class EmptySerializer(serializers.Serializer):
    pass


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50, required=True)
    password = serializers.CharField(required=True)


class ConfirmSignUpSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50, required=True)
    otp = serializers.CharField(required=True, max_length=10)


# Not in use until users.api.CurrentUserViewSet.partial_update comes into use
class UpdateUserProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=35)
    last_name = serializers.CharField(max_length=60)
    phone = serializers.CharField(max_length=15)
    address1 = serializers.CharField(max_length=55)
    address2 = serializers.CharField(required=False, max_length=55, allow_null=True)
    city = serializers.CharField(max_length=30)
    zip = serializers.CharField(
        min_length=5,
        max_length=5,
        validators=[
            RegexValidator(
                regex=r"\b\d{5}\b", message="Enter a zip code in the format XXXXX"
            )
        ],
    )
    gender = serializers.ChoiceField(choices=choices.GENDER_CHOICES)
    state = serializers.ChoiceField(choices=choices.STATE_CHOICES)
    employment_status = serializers.ChoiceField(
        choices=choices.EMPLOYMENT_STATUS_CHOICES
    )
    relationship_status = serializers.ChoiceField(
        choices=choices.RELATIONSHIP_STATUS_CHOICES
    )
    job_title = serializers.ChoiceField(choices=choices.JOB_TITLE_CHOICE)
    timezone = serializers.ChoiceField(
        required=False, choices=choices.CURRENTLY_ALLOWED_TIMEZONE_CHOICES
    )

    def validate_phone(self, value):
        # Save phone number with country code as Cognito raises error without it
        # Only US 10 digit numbers are allowed
        # Here we just add `+1` with the last 10 digits and validate the number
        value_without_hiphens = value.replace("-", "")
        if value_without_hiphens:
            if value_without_hiphens.startswith("+1") is False:
                value_without_hiphens = "+1{}".format(value_without_hiphens)
            if len(value_without_hiphens) > 12:
                raise serializers.ValidationError(
                    'Only valid US numbers of format "+1xxxxxxxxxx, +1-xxx-xxx-xxxx,'
                    ' xxxxxxxxxx, xxx-xxx-xxxx" are allowed!'
                )
            new_val = value_without_hiphens
            validate_international_phonenumber(new_val)
        return value_without_hiphens


class RegisterSerializer(UpdateUserProfileSerializer):
    email = serializers.EmailField(required=True, max_length=50)
    password = serializers.CharField(
        required=True,
        max_length=20,
        validators=[
            MinimumLengthValidator(min_length=8).validate,
            NumericPasswordValidator().validate,
            ComplexPasswordValidator().validate,
        ],
    )
    birthdate = serializers.DateField(input_formats=["%m/%d/%Y"])
    dfd_user_id = serializers.CharField(required=False)
    answer = serializers.UUIDField()
    agrees_to_beacon_privacy_notice = serializers.BooleanField(default=False)
    agrees_to_mdlive_informed_consent = serializers.BooleanField(default=False)
    agrees_to_mdlive_privacy_agreement = serializers.BooleanField(default=False)
    mdlive_consent_user_initials = serializers.CharField(
        required=True,
        max_length=2,
        min_length=2,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z.\s_-]+$",
                message="Enter user initials " "of two characters only",
            )
        ],
    )
    organisation = serializers.UUIDField(required=False)
    send_to_scc_if_non_f2f = serializers.HiddenField(default=True)

    def validate_email(self, value):
        user = services.get_user_by_email(email=value)
        if user:
            raise serializers.ValidationError("Email is already taken.")
        return models.UserManager.normalize_email(value)

    def validate_answer(self, value):
        answer = UserResponse.objects.filter(id=value).first()
        if answer is None:
            raise serializers.ValidationError("Answer with provided id doesn't exists!")
        return answer

    def validate_organisation(self, value):
        org = Organisation.objects.filter(id=value, is_active=True).first()
        if org is None:
            raise serializers.ValidationError(
                "Organisation with provided id doesn't exists!"
            )
        return org

    def validate(self, attrs):
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")
        mdlive_consent_user_initials = attrs.get("mdlive_consent_user_initials")
        mdlive_consent_user_initials = mdlive_consent_user_initials.upper()
        user_initials = "{}{}".format(first_name[0], last_name[0]).upper()
        if mdlive_consent_user_initials != user_initials:
            raise serializers.ValidationError(
                "MDLive consent user initials must be initials of "
                "user's first name and last name"
            )
        attrs["mdlive_consent_user_initials"] = mdlive_consent_user_initials
        return attrs


class CurrentUserSerializer(UserSerializer):
    md_live = serializers.SerializerMethodField()
    md_live_ou = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["md_live", "md_live_ou", "organisation"]

    def get_md_live(self, obj):
        return self.context.get("mdlive_user_token_data")

    def get_md_live_ou(self, obj):
        if obj.organisation:
            return obj.organisation.username
        return settings.MDLIVE_ORGANISATION_USERNAME


class AuthUserSerializer(CurrentUserSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta(CurrentUserSerializer.Meta):
        fields = CurrentUserSerializer.Meta.fields + ["auth_token"]

    def get_auth_token(self, obj):
        return tokens.get_token_for_user(obj, "authentication")


class ExtendTokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta(CurrentUserSerializer.Meta):
        model = models.User
        fields = ["auth_token"]

    def get_auth_token(self, obj):
        return tokens.get_token_for_user(obj, "authentication")


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[
            MinimumLengthValidator(min_length=8).validate,
            NumericPasswordValidator().validate,
            ComplexPasswordValidator().validate,
        ],
    )

    def validate(self, attrs):
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        if current_password == new_password:
            raise serializers.ValidationError(
                "Can't use current password as new password!"
            )
        return attrs

    default_error_messages = {"invalid_password": "Current password does not match"}


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=50)


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=50)
    new_password = serializers.CharField(
        required=True,
        validators=[
            MinimumLengthValidator(min_length=8).validate,
            NumericPasswordValidator().validate,
            ComplexPasswordValidator().validate,
        ],
    )
    otp = serializers.CharField(required=True, max_length=10)

    def validate_new_password(self, value):
        email = self.initial_data.get("email")
        user = services.get_user_by_email(email)
        if user and user.check_password(value) is True:
            raise serializers.ValidationError("Can't use previous password!")
        return value


class SCCPersonalInfoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "employment_status",
            "relationship_status",
            "job_title",
        ]


class SCCForceUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "connects_mbr_id",
            "mdlive_id",
            "email",
            "address1",
            "address2",
            "city",
            "state",
            "zip",
            "phone",
            "employment_status",
            "relationship_status",
            "job_title",
        ]
