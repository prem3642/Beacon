# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

# beacon Stuff
from beacon.base import response
from beacon.base.api.mixins import MultipleSerializerMixin
from beacon.organisations.services import get_organisation
from beacon.scc.services import send_user_data_to_scc_if_non_f2f
from beacon.users.services import send_data_to_bwb_server_and_email_user

from . import models, permissions, serializers, services

User = get_user_model()


class AnswerViewSet(
    MultipleSerializerMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet
):
    serializer_class = serializers.AnswerSerializer
    queryset = models.UserResponse.objects.all()
    serializer_classes = {
        "create": serializers.AnswerResponseSerializer,
        "update": serializers.AnswerSerializer,
        "partial_update": serializers.AnswerSerializer,
        "add_answer": serializers.AddOrUpdateAnswerSerializer,
        "add_or_update_answer": serializers.AddOrUpdateAnswerSerializer,
        "extend_token": serializers.ExtendAnswerTokenSerializer,
    }

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [permissions.UserResponseAccess]
        return super().get_permissions()

    # Making auth classes None to run only permission classes
    def get_authenticators(self):
        return list()

    def get_serializer_context(self):
        organisation, _ = get_organisation(self.request)
        context = super().get_serializer_context()
        context["organisation"] = organisation
        return context

    def perform_create(self, serializer):
        super().perform_create(serializer)
        services.set_attributes_from_response_json(serializer.instance)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        services.set_attributes_from_response_json(serializer.instance)

    # TODO: Remove this after FE migrate to add or update api
    @action(methods=["POST"], detail=True, url_path="add-answer")
    def add_answer(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_response = serializer.validated_data.get("response")
        services.replace_or_append_response(instance, validated_response)
        services.set_attributes_from_response_json(instance)
        return response.Ok({"message": "Answer appended successfully!"})

    @action(methods=["PATCH"], detail=True, url_path="add-or-update-answer")
    def add_or_update_answer(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_response = serializer.validated_data.get("response")
        services.replace_or_append_response(instance, validated_response)
        services.set_attributes_from_response_json(instance)
        return response.Ok({"message": "Answer updated successfully!"})

    @action(
        methods=[
            "POST",
        ],
        detail=False,
        url_path="extend-token",
    )
    def extend_token(self, request):
        user_response = request.user_response
        return response.Ok(self.get_serializer(user_response).data)


class AppointmentViewSet(
    MultipleSerializerMixin, CreateModelMixin, UpdateModelMixin, GenericViewSet
):
    serializer_class = serializers.AppointmentSerializer
    queryset = models.UserAppointment.objects.all()
    serializer_classes = {
        "create": serializers.AppointmentSerializer,
        "update": serializers.AppointmentSerializer,
        "partial_update": serializers.AppointmentSerializer,
        "finalize": serializers.LatestAppointmentSerializer,
        "latest": serializers.LatestAppointmentSerializer,
    }

    def get_queryset(self):
        queryset = self.queryset.filter(user_response__user=self.request.user)
        return queryset

    def get_serializer_context(self):
        organisation, _ = get_organisation(self.request)
        context = super().get_serializer_context()
        context["organisation"] = organisation
        return context

    def set_attribute_from_response_json(self, obj):
        user_appointment_object = None
        for answer in obj.response:
            _, user_appointment_object = services.set_attribute_from_response(
                obj.user_response, obj, answer
            )
        user_appointment_object.save()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        return self.set_attribute_from_response_json(serializer.instance)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_response = serializer.validated_data.get("response")
        services.replace_or_append_response(instance, validated_response)
        self.set_attribute_from_response_json(instance)
        return response.Ok(serializer.data)

    @action(methods=["POST"], detail=True, url_path="finalize")
    def finalize(self, request, pk=None):
        instance = self.get_object()
        send_data_to_bwb_server_and_email_user(
            request.user, instance.user_response, user_appointment=instance
        )
        send_user_data_to_scc_if_non_f2f(
            user=request.user, appointment_method=instance.appointment_method
        )
        return response.Ok({"message": "Appointment created successfully!"})

    @action(methods=["GET"], detail=False, url_path="latest")
    def latest(self, request, pk=None):
        last_appointment = None
        user_response = request.user.answer if hasattr(request.user, "answer") else None
        if user_response:
            last_appointment = user_response.appointments.first()
        return response.Ok(self.get_serializer(last_appointment).data)
