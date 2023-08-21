# -*- coding: utf-8 -*-

# Third Party Stuff
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

# beacon Stuff
from beacon.answers import permissions
from beacon.base import response
from beacon.base.api.mixins import MultipleSerializerMixin
from beacon.base.api.pagination import paginated_response
from beacon.organisations.services import get_organisation
from beacon.scc.services import send_user_data_to_scc_if_non_f2f
from beacon.users import services as user_services
from beacon.users.tasks import sync_user_mdlive_messages
from beacon.users.utils import get_relationship_from_user

from . import filters, models, serializers, services

User = get_user_model()


class MDLiveViewSet(MultipleSerializerMixin, GenericViewSet):
    serializer_class = serializers.UserMDLiveTokenSerializer
    queryset = User.objects.none()

    serializer_classes = {"extend_token": serializers.ExtendMDLiveTokenSerializer}

    def get_permissions(self):
        if self.action in [
            "fake_user_token",
            "register_patient",
            "search_providers",
            "providers_profile",
        ]:
            self.permission_classes = [permissions.UserResponseAccess]
        return super().get_permissions()

    @action(methods=["GET"], detail=False, url_path="user-token")
    def user_token(self, request):
        user_data = request.user.__dict__
        cognito_data = user_services.get_cognito_data_from_user_data(user_data)
        relationship = get_relationship_from_user(request.user)
        md_live_data = services.get_mdlive_data_from_cognito_data(
            cognito_data=cognito_data,
            cognito_sub=str(request.user.id),
            birth_date_str=request.user.birthdate.strftime("%Y-%m-%d"),
            relationship=relationship,
        )
        user_token = services.get_user_token(
            md_live_data, organisation=request.user.organisation
        )
        return response.Ok(user_token)

    # Authentication classes empty to run permission class for answer auth
    @action(
        methods=["GET"],
        detail=False,
        url_path="fake-user-token",
        authentication_classes=[],
    )
    def fake_user_token(self, request):
        organisation, _ = get_organisation(request)
        user_token = services.get_fake_user_token(organisation=organisation)
        return response.Ok(user_token)

    # Authentication classes empty to run permission class for answer auth
    @action(
        methods=["POST"],
        detail=False,
        url_path="search-providers",
        authentication_classes=[],
    )
    def search_providers(self, request):
        mdlive_fake_user_token = request.query_params.get("mdlive_token", None)
        if mdlive_fake_user_token is None:
            raise ValidationError("mdlive_token query param should be present")
        patient_id = request.query_params.get("patient_id", None)
        if patient_id is None:
            raise ValidationError("patient_id query param should be present")
        page = request.query_params.get("page")
        per_page = request.query_params.get("per_page")
        providers = services.get_providers(
            per_page=per_page,
            page=page,
            data=request.data,
            mdlive_fake_user_token=mdlive_fake_user_token,
            patient_id=patient_id,
        )
        return response.Ok(providers)

    # Authentication classes empty to run permission class for answer auth
    @action(
        methods=["GET"],
        detail=False,
        url_path="providers-profile",
        authentication_classes=[],
    )
    def providers_profile(self, request):
        mdlive_fake_user_token = request.query_params.get("mdlive_token", None)
        if mdlive_fake_user_token is None:
            raise ValidationError("mdlive_token query param should be present")
        provider_id = request.query_params.get("provider_id")
        availability_type = request.query_params.get("availability_type")
        provider_type = request.query_params.get("provider_type")
        specific_date = request.query_params.get("specific_date")
        state_abbrev = request.query_params.get("state_abbrev")
        show_next_availability = request.query_params.get("show_next_availability")
        provider = services.get_provider(
            provider_id=provider_id,
            availability_type=availability_type,
            provider_type=provider_type,
            specific_date=specific_date,
            state_abbrev=state_abbrev,
            show_next_availability=show_next_availability,
            mdlive_fake_user_token=mdlive_fake_user_token,
        )
        return response.Ok(provider)

    @action(methods=["POST"], detail=False, url_path="extend-token")
    def extend_token(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jwt_token = services.extend_user_token_time(
            serializer.validated_data.get("jwt_token"),
            organisation=request.user.organisation,
        )
        return response.Ok(dict(jwt_token=jwt_token))


class MessageViewSet(MultipleSerializerMixin, GenericViewSet):
    serializer_class = serializers.UserMDLiveTokenSerializer
    queryset = models.Message.objects.select_related(
        "provider_message__message_from",
        "provider_message__message_to",
        "user_message__message_from",
        "user_message__message_to",
    ).all()
    lookup_field = "mdlive_id"
    filter_backends = [
        filters.ProviderFilter,
        filters.UnreadFilter,
        filters.SentMessageFilter,
        filters.ReceivedMessageFilter,
    ]
    serializer_classes = {
        "create": serializers.UserMessageSerializer,
        "retrieve": serializers.MessageSerializerDetail,
        "list": serializers.MessageSerializer,
    }

    def get_permissions(self):
        if self.action == "webhook":
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            Q(
                message_type=models.Message.USER_MESSAGE,
                user_message__message_from=self.request.user,
            )
            | Q(
                message_type=models.Message.PROVIDER_MESSAGE,
                provider_message__message_to=self.request.user,
            )
        )
        queryset = queryset.prefetch_related("documents")
        return self.filter_queryset(queryset)

    @action(
        methods=["GET", "POST"],
        detail=False,
        url_path="webhook",
        authentication_classes=[],
    )
    def webhook(self, request):
        """
        e.g. webhook data
        data = {
          "event": {
            "token": "736a0864-5b1a-4e49-9791-ace850a8f7f1",
            "action": "message:provider:created",
            "data": {
              "message": {
                "id": 393759,
                "from_id": 642183606,
                "to_id": 642197878,
                "unread_status": True,
                "replied_to_message_id": None
              }
            }
          }
        }
        """
        if "event" in request.data:
            if "action" in request.data["event"] and "data" in request.data["event"]:
                if request.data["event"]["action"] == "message:provider:created":
                    message = request.data["event"]["data"]["message"]
                    user = (
                        get_user_model()
                        .objects.filter(mdlive_id=message.get("to_id"))
                        .first()
                    )
                    if user:
                        sync_user_mdlive_messages.delay(
                            str(user.id), send_new_message_email=True
                        )
        return response.Ok("Received")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mdlive_message_response = services.create_message_on_mdlive(
            serializer.validated_data, request.user
        )
        instance = services.create_user_message(
            mdlive_message_response.get("message"),
            request.user,
            serializer.validated_data.get("documents"),
        )
        return response.Created(serializers.MessageSerializerDetail(instance).data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Ok(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return paginated_response(request, queryset, self.get_serializer_class())

    @action(methods=["PUT", "PATCH"], detail=True, url_path="mark-read")
    def mark_read(self, request, *args, **kwargs):
        instance = self.get_object()
        services.mark_message_read(request.user, instance)
        return response.NoContent()

    @action(methods=["GET"], detail=False, url_path="unread-messages-count")
    def unread_messages_count(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = queryset.filter(is_read=False)
        queryset = queryset.filter(
            message_type=models.Message.PROVIDER_MESSAGE,
            provider_message__message_to=self.request.user,
        )
        return response.Ok({"count": queryset.count()})


class ContactViewSet(MultipleSerializerMixin, GenericViewSet):
    serializer_class = serializers.ProviderSerializer
    queryset = models.Provider.objects.all()
    lookup_field = "mdlive_id"
    filter_backends = [filters.ProviderFilter, filters.UnreadFilter]
    serializer_classes = {
        "retrieve": serializers.ProviderSerializer,
        "list": serializers.ProviderSerializer,
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        providers_id = models.Contact.objects.filter(
            user=self.request.user
        ).values_list("provider_id", flat=True)
        return queryset.filter(id__in=providers_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Ok(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return response.Ok(serializer.data)


class AppointmentSlotQueryViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = serializers.AppointmentSlotQuerySerializer
    queryset = models.AppointmentSlotQuery.objects.filter(is_cancelled=False)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mdlive_response = services.request_appointment(
            serializer.validated_data.get("user"),
            serializer.validated_data.get("provider_id"),
            serializer.validated_data.get("preferred_time"),
            serializer.validated_data.get("appointment_method"),
            str(serializer.validated_data.get("appointment_date")),
            serializer.validated_data.get("chief_complaint"),
            serializer.validated_data.get("chief_complaint_comments"),
            serializer.validated_data.get("contact_number"),
            serializer.validated_data.get("appointment_request_state"),
        )
        mdlive_id = mdlive_response.get("appointment_request").get("id")
        instance = serializer.save()
        instance.mdlive_id = mdlive_id
        instance.save()
        sync_user_mdlive_messages.delay(str(request.user.id))
        send_user_data_to_scc_if_non_f2f(
            user=serializer.validated_data.get("user"),
            appointment_method=serializer.validated_data.get("appointment_method"),
        )
        return response.Created(serializer.data)

    @action(methods=["POST"], detail=True, url_path="remind")
    def remind(self, request, *args, **kwargs):
        instance = self.get_object()
        services.appointment_request_remind(request.user, instance.mdlive_id)
        sync_user_mdlive_messages.delay(str(request.user.id))
        return response.Ok(
            {
                "message": "The Provider has been reminded about your appointment slot query"
            }
        )

    @action(methods=["POST"], detail=True, url_path="cancel")
    def cancel(self, request, *args, **kwargs):
        instance = self.get_object()
        services.appointment_request_cancel(request.user, instance.mdlive_id)
        instance.is_cancelled = True
        instance.save()
        sync_user_mdlive_messages.delay(str(request.user.id))
        return response.Ok(
            {"message": "Your appointment slot query has been cancelled"}
        )


class DocumentsViewSet(
    MultipleSerializerMixin,
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = serializers.UserDocumentSerializer
    queryset = models.UserDocument.objects.all()
    parser_classes = [FormParser, JSONParser, MultiPartParser]
    serializer_classes = {
        "create": serializers.UserDocumentCreateSerializer,
    }

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return response.Created(serializers.UserDocumentSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        services.delete_user_document(instance)
        instance.delete()
        return response.NoContent()
