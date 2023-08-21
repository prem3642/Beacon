# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

# beacon Stuff
# Beacon Stuff
from beacon.answers.permissions import LoggedInUserResponseAccess
from beacon.base import response
from beacon.organisations.services import get_organisation

from . import models, serializers, services

User = get_user_model()


class QuestionViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.QuestionSerializer
    queryset = models.Question.objects.prefetch_related("choices").filter(
        is_active=True, leader_question__isnull=True
    )

    def get_authenticators(self):
        return list()

    def get_permissions(self):
        if self.action in ["get_next_question", "get_previous_question"]:
            self.permission_classes = [LoggedInUserResponseAccess]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        organisation, _ = get_organisation(self.request)
        context["organisation"] = organisation
        return context

    @action(methods=["GET"], detail=False, url_path="starting-question")
    def starting_question(self, request):
        instance = self.get_queryset().filter(is_start=True).first()
        if instance:
            serializer = self.get_serializer(instance)
            return response.Ok(serializer.data)
        return response.NoContent()

    @action(methods=["GET"], detail=False, url_path="appointment-starting-question")
    def appointment_starting_question(self, request):
        instance = self.get_queryset().filter(is_appointment_start=True).first()
        if instance:
            serializer = self.get_serializer(instance)
            return response.Ok(serializer.data)
        return response.NoContent()

    @action(methods=["GET"], detail=False, url_path="nested-questions")
    def nested_questions(self, request):
        qs = self.get_queryset().filter(
            nested_question__isnull=False, nested_parent__isnull=True
        )
        return response.Ok(
            serializers.NestedQuestionSerializer(
                qs, many=True, context=self.get_serializer_context()
            ).data
        )

    def get_template_from_organisation(self, request):
        organisation, _ = get_organisation(self.request)
        template = None
        if organisation:
            template = organisation.template
        if template is None:
            template = models.IntakeQuestionTemplate.objects.filter(
                is_default=True
            ).first()
        return template

    @action(methods=["GET"], detail=True, url_path="next-question")
    def get_next_question(self, request, pk):
        template = self.get_template_from_organisation(request)
        instance = self.get_object()
        next_question = services.get_next_question_service(
            template, instance, request.user_response
        )
        return response.Ok(self.get_serializer(next_question).data)

    @action(methods=["GET"], detail=True, url_path="previous-question")
    def get_previous_question(self, request, pk):
        template = self.get_template_from_organisation(request)
        instance = self.get_object()
        next_question = services.get_previous_question_service(
            template, instance, request.user_response
        )
        return response.Ok(self.get_serializer(next_question).data)
