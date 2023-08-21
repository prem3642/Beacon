# -*- coding: utf-8 -*-
# Standard Library
from copy import deepcopy
from datetime import timedelta

# Third Party Stuff
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from . import services
from .models import UserAppointment, UserResponse


class AppointmentSerializer(serializers.ModelSerializer):
    response = serializers.JSONField(label="Response")

    class Meta:
        model = UserAppointment
        fields = [
            "id",
            "response",
            "mdlive_provider_id",
            "selected_time_slot",
            "last_answered_question",
        ]

    def validate_response(self, value):
        if type(value) != list:
            value = [value]
        return services.validate_response_json(value, self.context.get("organisation"))

    def validate(self, attrs):
        data = deepcopy(attrs)
        user = self.context.get("request").user
        data["user_response"] = user.answer
        return data


class LatestAppointmentSerializer(serializers.ModelSerializer):
    show_homepage_message = serializers.SerializerMethodField()

    class Meta:
        model = UserAppointment
        fields = [
            "id",
            "appointment_method",
            "mdlive_provider_id",
            "selected_time_slot",
            "show_homepage_message",
            "bwb_inquiry_id",
            "created_at",
            "modified_at",
        ]
        read_only_fields = fields

    def get_show_homepage_message(self, obj):
        time_threshold = timezone.now() - timedelta(
            hours=settings.APPOINTMENT_HOMEPAGE_MESSAGE_TIME_THRESHOLD
        )
        return obj.modified_at > time_threshold


class AddOrUpdateAnswerSerializer(serializers.Serializer):
    response = serializers.JSONField(label="Response")
    last_answered_question = serializers.CharField(
        label="Last Answered Question", max_length=50, required=False
    )

    class Meta:
        fields = ["response", "last_answered_question"]

    def validate_response(self, value):
        if type(value) != dict:
            raise serializers.ValidationError("Invalid response object")
        validated_json = services.validate_response_json(
            [value], self.context.get("organisation")
        )
        return validated_json


class AnswerSerializer(serializers.ModelSerializer):
    appointment_method = serializers.ChoiceField(
        allow_blank=True,
        allow_null=True,
        choices=UserAppointment.APPOINTMENT_CHOICES,
        label="Appointment Method",
        required=False,
    )

    class Meta:
        model = UserResponse
        fields = [
            "id",
            "response",
            "mdlive_provider_id",
            "selected_time_slot",
            "appointment_method",
            "last_answered_question",
        ]

    def validate_response(self, value):
        validated_json = services.validate_response_json(
            value, self.context.get("organisation")
        )
        return validated_json

    def update_or_create_appointment(
        self, appointment_instance, appointment_data: dict
    ):
        if appointment_instance is None:
            return UserAppointment.objects.create(**appointment_data)

        for attr, value in appointment_data.items():
            setattr(appointment_instance, attr, value)
        return appointment_instance.save()

    def create(self, validated_data: dict):
        data = deepcopy(validated_data)
        mdlive_provider_id = data.pop("mdlive_provider_id", None)
        selected_time_slot = data.pop("selected_time_slot", None)
        appointment_method = data.pop("appointment_method", None)
        user_response = super().create(data)
        if mdlive_provider_id or selected_time_slot or appointment_method:
            appointment_data = dict(
                mdlive_provider_id=mdlive_provider_id,
                selected_time_slot=selected_time_slot,
                appointment_method=appointment_method,
                user_response=user_response,
            )
            self.update_or_create_appointment(None, appointment_data)
        return user_response

    def update(self, instance: UserResponse, validated_data: dict):
        data = deepcopy(validated_data)
        mdlive_provider_id = data.pop("mdlive_provider_id", None)
        selected_time_slot = data.pop("selected_time_slot", None)
        appointment_method = data.pop("appointment_method", None)
        if mdlive_provider_id or selected_time_slot or appointment_method:
            appointment_data = dict(
                mdlive_provider_id=mdlive_provider_id,
                selected_time_slot=selected_time_slot,
                appointment_method=appointment_method,
                user_response=instance,
            )
            existing_appointment = instance.appointments.all().first()
            self.update_or_create_appointment(existing_appointment, appointment_data)

        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AnswerResponseSerializer(AnswerSerializer):
    answer_token = serializers.SerializerMethodField(read_only=True)
    mdlive_provider_id = serializers.SerializerMethodField(read_only=True)
    selected_time_slot = serializers.SerializerMethodField(read_only=True)
    appointment_method = serializers.SerializerMethodField(read_only=True)

    class Meta(AnswerSerializer.Meta):
        fields = AnswerSerializer.Meta.fields + ["answer_token"]

    def get_answer_token(self, obj):
        return services.get_token_for_user_response(obj, "authentication")

    def get_mdlive_provider_id(self, obj):
        appointment = obj.appointments.first()
        if appointment is None:
            return None
        return appointment.mdlive_provider_id

    def get_selected_time_slot(self, obj):
        appointment = obj.appointments.first()
        if appointment is None:
            return None
        return appointment.selected_time_slot

    def get_appointment_method(self, obj):
        appointment = obj.appointments.first()
        if appointment is None:
            return None
        return appointment.appointment_method


class AnswerSccSyncSerializer(AnswerResponseSerializer):
    response = serializers.JSONField(required=True)


class ExtendAnswerTokenSerializer(serializers.ModelSerializer):
    answer_token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserResponse
        fields = ["answer_token"]

    def get_answer_token(self, obj):
        return services.get_token_for_user_response(obj, "authentication")


class UpdateUserResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    response = serializers.JSONField(
        style={"base_template": "textarea.html"}, required=False
    )

    class Meta:
        fields = ["id", "response"]

    # Validate method check if User Response instance exists for given id
    # If it exists then returns it in attrs
    def validate(self, attrs):
        user_response_id = attrs.get("id", None)
        response = attrs.get("response", None)
        if not user_response_id and not response:
            raise serializers.ValidationError("Either id or response is required.")

        if user_response_id:
            user_response = UserResponse.objects.filter(id=user_response_id).first()
            if not user_response:
                raise serializers.ValidationError(
                    "User response with given id does not exists."
                )
            attrs["user_response_obj"] = user_response
        if response:
            if type(response) != list:
                raise serializers.ValidationError(
                    "Response should be an array of answers"
                )
        return attrs


class UpdateAppointmentStateSerializer(serializers.Serializer):
    appointment_state = serializers.CharField(max_length=30, required=True)

    class Meta:
        fields = [
            "appointment_state",
        ]
