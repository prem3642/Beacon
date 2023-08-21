# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth import get_user_model, logout
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from beacon.answers.models import UserResponse
from beacon.users.models import User
from beacon.users.serializers import LoginSerializer, UserSerializer

# beacon Stuff
from beacon.answers.serializers import (
    UpdateAppointmentStateSerializer,
    UpdateUserResponseSerializer,
)
from beacon.answers.services import (
    replace_or_append_response,
    set_attributes_from_response_json,
    validate_single_response,
)
from beacon.base import exceptions, response
from beacon.base.api.mixins import MultipleSerializerMixin
from beacon.cognito import services as cognito_services
from beacon.mdlive import services as mdlive_services
from beacon.organisations.models import Organisation
from beacon.organisations.services import get_organisation
from beacon.questionnaire.models import Question
from beacon.users import services as user_services

from . import models, serializers
from .services import remove_user_token_from_cache, update_or_create_user_agent
from .tasks import sync_user_mdlive_messages
from .utils import get_relationship_from_user
import environ

env = environ.Env()
REDIRECT_URL = env("DFD_REDIRECT_URL", default="dev-th.carelonwellbeing.com")


class AuthViewSet(MultipleSerializerMixin, viewsets.GenericViewSet):
    permission_classes = [
        AllowAny,
    ]
    serializer_classes = {
        "login": serializers.LoginSerializer,
        "register": serializers.RegisterSerializer,
        "resend_verification_email": serializers.PasswordResetSerializer,
        "logout": serializers.EmptySerializer,
        "confirm_sign_up": serializers.ConfirmSignUpSerializer,
        "extend_token": serializers.ExtendTokenSerializer,
        "password_change": serializers.PasswordChangeSerializer,
        "password_reset": serializers.PasswordResetSerializer,
        "password_reset_confirm": serializers.PasswordResetConfirmSerializer,
    }

    @action(methods=["POST"], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, cognito_user = user_services.get_and_authenticate_user(
            **serializer.validated_data
        )
        organisation, _ = get_organisation(
            request,
            queryset=Organisation.objects.filter(is_active=True, parent__isnull=True),
        )
        if organisation and user.organisation:
            child_organisations = [
                str(org_id)
                for org_id in organisation.children.all().values_list("id", flat=True)
            ]
            if (
                user.organisation != organisation
                and str(user.organisation.id) not in child_organisations
            ):
                raise PermissionDenied(
                    "You are not allowed to login for this organisation!"
                )

        cognito_user_data = cognito_services.user_obj_to_dict(cognito_user)
        relationship = get_relationship_from_user(user)
        mdlive_data = mdlive_services.get_mdlive_data_from_cognito_data(
            cognito_data=cognito_user_data,
            cognito_sub=str(user.id),
            birth_date_str=cognito_user_data.get("birthdate"),
            relationship=relationship,
        )
        mdlive_user_token_data = mdlive_services.get_user_token(
            mdlive_data, organisation=user.organisation
        )
        sync_user_mdlive_messages.delay(str(user.id))
        update_or_create_user_agent(user, request)
        ctx = self.get_serializer_context()
        ctx["mdlive_user_token_data"] = mdlive_user_token_data
        ctx["cognito_user_data"] = cognito_user_data
        ctx["user_response"] = user.answer if hasattr(user, "answer") else None
        data = serializers.AuthUserSerializer(user, context=ctx).data
        return response.Ok(data)

    @action(methods=["POST"], detail=False, url_path="confirm-sign-up")
    def confirm_sign_up(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_services.get_user_by_email(serializer.validated_data.get("email"))
        if user:
            cognito_services.confirm_sign_up(serializer.validated_data.get("otp"), user)
            user.is_verified = True
            user.save()
            return response.Ok({"message": "User is successfully verified"})
        raise ValidationError("Either otp or email is invalid!")

    @action(methods=["POST"], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, mdlive_user_token_data, _ = user_services.create_user_account(
            serializer.validated_data, request=request, source=get_user_model().API
        )

        # link user with the user_response
        user_response = serializer.validated_data.get("answer")
        user_response.user = user
        user_response.save()

        # Check F2F and send data to bwb server and email to user as well
        user_services.send_data_to_bwb_server_and_email_user(user, user_response)

        ctx = self.get_serializer_context()
        ctx["mdlive_user_token_data"] = mdlive_user_token_data

        # NOTE: currently variable on django and cognito matches
        #       so we can pass validated data directly as cognito data
        #       pass the mapped data if variable name on django and cognito changes
        ctx["cognito_user_data"] = serializer.validated_data
        ctx["user_response"] = user.answer if hasattr(user, "answer") else None
        data = serializers.AuthUserSerializer(user, context=ctx).data
        return response.Created(data)

    @action(methods=["POST"], detail=False, url_path="resend-verification-email")
    def resend_verification_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_services.get_user_by_email(serializer.data["email"])
        if user:
            cognito_services.resend_verification_email(user.email)
        return response.Ok(
            {"message": "Further instructions will be sent to the email if it exists"}
        )

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Calls Django logout method; Does not work for UserTokenAuth.
        """
        # removing token from current logged in sessions
        remove_user_token_from_cache(request)
        logout(request)
        return response.Ok({"message": "Successfully logged out."})

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path="extend-token",
    )
    def extend_token(self, request):
        user = request.user
        return response.Ok(self.get_serializer(user).data)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path="password-change",
    )
    def password_change(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cognito_services.change_password(
            user,
            serializer.validated_data.get("current_password"),
            serializer.validated_data.get("new_password"),
        )
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return response.Ok({"message": "Password changed successfully!"})

    @action(
        methods=["POST"],
        detail=False,
        url_path="password-reset",
    )
    def password_reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_services.get_user_by_email(serializer.data["email"])
        if user is None:
            raise ValidationError("That email does not exist in our system, sorry!")
        if user.is_verified is False:
            raise exceptions.NotVerified("User is not verified yet!")
        cognito_services.initiate_password_reset(user.email)
        return response.Ok(
            {"message": "Further instructions will be sent to the email if it exists"}
        )

    @action(
        methods=["POST"],
        detail=False,
        url_path="password-reset-confirm",
    )
    def password_reset_confirm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_services.get_user_by_email(serializer.data["email"])
        if user:
            cognito_services.confirm_password_reset(
                serializer.validated_data.get("otp"),
                user.email,
                serializer.validated_data.get("new_password"),
            )
            user.set_password(serializer.validated_data["new_password"])
            user.num_of_failed_login_attempts = 0
            user.save()
            return response.Ok({"message": "Password changed successfully!"})
        raise ValidationError("Either email or otp is invalid!")


class CurrentUserViewSet(MultipleSerializerMixin, viewsets.GenericViewSet):
    serializer_class = serializers.CurrentUserSerializer
    queryset = models.User.objects.filter(is_active=True)

    serializer_classes = {
        "list": serializers.CurrentUserSerializer,
        "partial_update": serializers.UpdateUserProfileSerializer,
        "update_responses": UpdateUserResponseSerializer,
        "update_appointment_state": UpdateAppointmentStateSerializer,
    }

    def get_object(self):
        return self.request.user

    def list(self, request):
        """Get logged in user profile"""
        user = self.get_object()
        relationship = get_relationship_from_user(user)
        user_data = user.__dict__
        cognito_data = user_services.get_cognito_data_from_user_data(user_data)
        mdlive_data = mdlive_services.get_mdlive_data_from_cognito_data(
            cognito_data=cognito_data,
            cognito_sub=str(user.id),
            birth_date_str=user.birthdate.strftime("%Y-%m-%d"),
            relationship=relationship,
        )
        mdlive_user_token_data = mdlive_services.get_user_token(
            mdlive_data, organisation=user.organisation
        )
        ctx = self.get_serializer_context()
        ctx["mdlive_user_token_data"] = mdlive_user_token_data
        ctx["user_response"] = user.answer if hasattr(user, "answer") else None
        data = self.serializer_class(user, context=ctx).data
        return response.Ok(data)

    # TODO: Uncomment this after client confirmation to allow profile update
    # def partial_update(self, request):
    #     """Update logged in user profile"""
    #     instance = self.get_object()
    #     serializer = self.get_serializer(data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     cognito_services.update_profile(instance, serializer.validated_data)
    #     return response.Ok({
    #         'message': 'User profile has been updated successfully!'
    #     })

    @action(
        methods=["PATCH"],
        detail=False,
        url_path="update-responses",
    )
    def update_responses(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_user_response_instance = (
            request.user.answer if hasattr(request.user, "answer") else None
        )
        new_user_response_instance = serializer.validated_data.get(
            "user_response_obj", None
        )
        if new_user_response_instance:
            old_user_response_instance.response = new_user_response_instance.response
            old_user_response_instance.save()
        else:
            validated_response = serializer.validated_data.get("response")
            for answer in validated_response:
                replace_or_append_response(old_user_response_instance, answer)
        set_attributes_from_response_json(old_user_response_instance)
        return response.Ok({"message": "User responses updated successfully!"})

    @action(
        methods=["POST"],
        detail=False,
        url_path="update-appointment-state",
    )
    def update_appointment_state(self, request):
        """
        The usual way to update appointment state requires FE
        to keep track of question ids, map those to the question
        for appointment state and then update the particular response, requiring a total of 3 API calls.
        This API call make it simpler to update appointment_state for the current user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment_state = serializer.validated_data.get("appointment_state")
        user_response_instance = UserResponse.objects.filter(user=request.user).first()

        if not user_response_instance:
            raise ValidationError("No user response found to update appointment_state.")
        questions_qs = Question.objects.filter(
            user_response_attribute="appointment_state"
        )
        answer_response = {
            "question": str(questions_qs.first().id),
            "answer": appointment_state,
        }
        answer = validate_single_response(answer_response, questions_qs)
        replace_or_append_response(user_response_instance, [answer])
        set_attributes_from_response_json(user_response_instance)
        return response.Ok({"message": "Appointment State updated successfully!"})


#####v2 registration API for DFD
from rest_framework.views import APIView
from beacon.answers.models import UserResponse
from beacon.organisations.models import Organisation
from beacon.mdlive.services import get_timezone_from_zip
from .choices import STATE_CHOICES
from beacon.scc.constants import CHIEF_COMPLAINT1_ANSWER_MAPPING_BWB_TO_SCC


class DFDRegistration(APIView):
    permission_classes = [
        AllowAny,
    ]

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def post(self, request):
        state = request.data['state']
        ap_state = request.data['answer'].get('appointment_state')
        if len(state) > 2:
            state_code = list(filter(lambda x: dict(STATE_CHOICES)[x] == state, dict(STATE_CHOICES)))[0]
            request.data['state'] = state_code
        if len(ap_state) > 2:
            state_code1 = list(filter(lambda x: dict(STATE_CHOICES)[x] == ap_state, dict(STATE_CHOICES)))[0]
            request.data['answer']['appointment_state'] = state_code1
        elif ap_state is None:
            request.data['answer']['appointment_state'] = state_code

        if request.data['answer'].get('chief_complaint1') not in CHIEF_COMPLAINT1_ANSWER_MAPPING_BWB_TO_SCC.keys():
            chief_complaint1 = 'Stress'
        else:
            chief_complaint1 = request.data['answer'].get('chief_complaint1')

        try:

            user_response = UserResponse(emotional_support_for=request.data['answer'].get('emotional_support_for'),
                                         appointment_state=request.data['answer'].get('appointment_state'),
                                         chief_complaint1=chief_complaint1, response={})
            user_response.save()
        except Exception as e:
            return response.BadRequest('please validate answer object')

        try:
            organisation = Organisation.objects.get(username=request.data['organisation'].get('username'),
                                                    parent_code=request.data['organisation'].get('parent_code'))
        except Exception as e:
            return response.BadRequest('please verify organisation data ')
        data = request.data
        data['answer'] = user_response.id
        data['organisation'] = organisation.id
        data['dfd_user_id'] = data.pop('DFD_id')
        data['password'] = data['first_name'][0].capitalize() + data['last_name'][0].lower() + '!' + data[
            'birthdate'].replace('/', '')
        data['timezone'] = get_timezone_from_zip(data['zip'])
        data['mdlive_consent_user_initials'] = data['first_name'][0].capitalize() + data['last_name'][
            0].capitalize()
        serializer = serializers.RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user, mdlive_user_token_data, _ = user_services.create_user_account(
            serializer.validated_data, request=request, source=get_user_model().API
        )
        # link user with the user_response
        user_response = serializer.validated_data.get("answer")
        user_response.user = user
        user_response.save()

        # Check F2F and send data to bwb server and email to user as well
        user_services.send_data_to_bwb_server_and_email_user(user, user_response)

        ctx = self.get_serializer_context()
        ctx["mdlive_user_token_data"] = mdlive_user_token_data

        # NOTE: currently variable on django and cognito matches
        #       so we can pass validated data directly as cognito data
        #       pass the mapped data if variable name on django and cognito changes
        ctx["cognito_user_data"] = serializer.validated_data
        ctx["user_response"] = user.answer if hasattr(user, "answer") else None
        data = serializers.AuthUserSerializer(user, context=ctx).data
        #send_user_eap_to_mdlive(user=user)
        user = User.objects.get(id=user.id)
        user.is_verified = True
        user.save()
        if organisation.domain and 'wellbeing.com' not in organisation.domain:
            data['redirect_url'] = REDIRECT_URL + organisation.domain + '/dfd'
        elif organisation.domain and 'mybeaconwellbeing' in organisation.domain:
            domain = organisation.domain
            domain = domain.split('.')[0]
            data['redirect_url'] = REDIRECT_URL + domain + '/dfd'
        elif organisation.domain and 'carelonwellbeing' in organisation.domain:
            data['redirect_url'] = organisation.domain + '/dfd'
        return response.Created(data)


from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from django.conf import settings
from django.core.signing import TimestampSigner
import jwt

ALGORITHM = "HS256"


class DFDlogin(APIView):
    permission_classes = [
        AllowAny | HasAPIKey
    ]

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def post(self, request):
        try:
            key = request.META["HTTP_AUTHORIZATION"].split()[1]

            api_key = APIKey.objects.get_from_key(key)

            # return response.Ok('cool')
            if not api_key:
                return response.Unauthorized('token is missing or invalid ')
            if api_key.has_expired:
                return response.Unauthorized('token is Expired ')
            else:
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')
                birthdate = request.data.get('birthdate')
                email = request.data.get('email')
                dfd_id = request.data.get('dfd_id')
                user = User.objects.get(dfd_user_id=dfd_id)
                organisation = Organisation.objects.get(id=user.organisation.id)

                if User.objects.get(dfd_user_id=dfd_id):
                    data = {}
                    data['email'] = email
                    data['password'] = first_name[0].capitalize() + last_name[0].lower() + '!' + birthdate.replace('/',
                                                                                                                   '')
                    cognito_user_data = UserSerializer(User.objects.get(dfd_user_id=dfd_id)).data
                    cognito_user_data['birthdate'] = birthdate
                    relationship = 'Self'
                    mdlive_data = mdlive_services.get_mdlive_data_from_cognito_data(
                        cognito_data=cognito_user_data,
                        cognito_sub=str(user.id),
                        birth_date_str=cognito_user_data.get("birthdate"),
                        relationship=relationship,
                    )
                    mdlive_user_token_data = mdlive_services.get_user_token(
                        mdlive_data, organisation=user.organisation
                    )
                    sync_user_mdlive_messages.delay(str(user.id))
                    update_or_create_user_agent(user, request)
                    ctx = self.get_serializer_context()
                    ctx["mdlive_user_token_data"] = mdlive_user_token_data
                    ctx["cognito_user_data"] = cognito_user_data
                    ctx["user_response"] = user.answer if hasattr(user, "answer") else None
                    data = serializers.AuthUserSerializer(user, context=ctx).data

                    if organisation.domain and 'wellbeing.com' not in organisation.domain:
                        data['redirect_url'] = REDIRECT_URL + organisation.domain + '/dfd'
                    elif organisation.domain and 'mybeaconwellbeing' in organisation.domain:
                        domain = organisation.domain
                        domain = domain.split('.')[0]
                        data['redirect_url'] = REDIRECT_URL + domain + '/dfd'
                    elif organisation.domain and 'carelonwellbeing' in organisation.domain:
                        data['redirect_url'] = organisation.domain + '/dfd'
                    return response.Ok(data)
                return response.NotFound('User doesnt exist')
        except Exception as e:
            return response.BadRequest(str(e))

    def get(self, request):
        try:

            max_age_in_minutes = settings.JWT_TOKEN_EXPIRATION_DURATION
            token = request.headers.get('Authorization')
            signer = TimestampSigner()
            token1 = signer.unsign(token, max_age=60 * max_age_in_minutes)
            data = jwt.decode(token1, settings.SECRET_KEY, algorithms=[ALGORITHM])

            model_cls = get_user_model()
            scope = 'authentication'
            user = model_cls.objects.get(pk=data["user_%s_id" % scope])
            cognito_user_data = UserSerializer(User.objects.get(email=user.email)).data
            cognito_user_data['birthdate'] = user.birthdate.strftime('%Y-%m-%d')
            relationship = 'Self'
            mdlive_data = mdlive_services.get_mdlive_data_from_cognito_data(
                cognito_data=cognito_user_data,
                cognito_sub=str(user.id),
                birth_date_str=cognito_user_data.get("birthdate"),
                relationship=relationship,
            )
            mdlive_user_token_data = mdlive_services.get_user_token(
                mdlive_data, organisation=user.organisation
            )
            sync_user_mdlive_messages.delay(str(user.id))
            update_or_create_user_agent(user, request)
            ctx = self.get_serializer_context()
            ctx["mdlive_user_token_data"] = mdlive_user_token_data
            ctx["cognito_user_data"] = cognito_user_data
            ctx["user_response"] = user.answer if hasattr(user, "answer") else None

            data = serializers.AuthUserSerializer(user, context=ctx).data

            return response.Ok(data)
        except Exception as e:
            return response.Unauthorized(str(e))
