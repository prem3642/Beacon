# -*- coding: utf-8 -*-
# Standard Library
from copy import deepcopy

# Third Party Stuff
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import FormView
from django_sites import get_by_id as get_site_by_id
from django_sites import get_current
from mail_templated import send_mail
from rest_framework.exceptions import ValidationError

# beacon Stuff
from beacon.answers.models import UserResponse
from beacon.campaign_monitor import services as campaign_monitor_services
from beacon.cognito import services as cognito_services

from .forms import ConfirmRegisterForm, RegisterForm, UploadUserCSVForm
from .services import (
    create_user_account,
    get_default_user_password,
    handle_uploaded_file,
)
from .tasks import (
    create_users_from_csv,
    generate_password_and_send_welcome_email,
    send_users_to_campaign_monitor_from_csv,
)


@method_decorator(staff_member_required, name="dispatch")
class RegisterView(FormView):
    template_name = "admin/users/register.html"
    email_template_name = "email/welcome_mail.tpl"
    form_class = RegisterForm
    success_url = "/users/register"

    def form_valid(self, form):
        data = deepcopy(form.cleaned_data)
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        birth_date = data.get("birthdate")
        password = get_default_user_password(first_name, last_name, birth_date)
        data["agrees_to_beacon_privacy_notice"] = True
        data["agrees_to_mdlive_informed_consent"] = True
        data["agrees_to_mdlive_privacy_agreement"] = True
        data["mdlive_consent_user_initials"] = "{}{}".format(
            first_name[0], last_name[0]
        ).upper()
        data["password"] = password
        chief_complaint1 = data.get("chief_complaint1")
        chief_complaint2 = data.get("chief_complaint2")
        appointment_state = data.get("appointment_state")
        admin_force_registration = data.get("admin_force_registration")

        try:
            user, mdlive_user_token_data, _ = create_user_account(
                data,
                request=None,
                admin_force_registration=admin_force_registration,
                source=get_user_model().ADMIN,
                source_admin=self.request.user.email,
            )
            UserResponse.objects.create(
                user=user,
                response={},
                chief_complaint1=chief_complaint1,
                chief_complaint2=chief_complaint2,
                appointment_state=appointment_state,
                emotional_support_for="Self",
            )
        except ValidationError as e:
            form.add_error(None, e.detail[0])
            return super().form_invalid(form)

        # Send email to user regarding the new account and password
        ctx = {
            "user": user,
            "organisation": user.organisation,
            "first_name": first_name,
            "password": password,
            "site": get_current(),
            "frontend_site": get_site_by_id("frontend"),
        }
        send_mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            template_name=self.email_template_name,
            context=ctx,
        )
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(staff_member_required, name="dispatch")
class ConfirmRegisterView(FormView):
    template_name = "admin/users/confirm_register.html"
    form_class = ConfirmRegisterForm
    success_url = "/admin/users/user/"

    def form_valid(self, form):
        data = deepcopy(form.cleaned_data)
        user_id = self.kwargs.get("pk")
        user = get_user_model().objects.filter(id=user_id).first()
        if user is None:
            form.add_error(None, "User is Invalid!")
            return super().form_invalid(form)

        try:
            cognito_services.confirm_sign_up(data.get("otp"), user)
        except ValidationError as e:
            form.add_error(None, e.detail[0])
            return super().form_invalid(form)
        user.is_verified = True
        user.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(staff_member_required, name="dispatch")
class ResendVerificationView(View):
    user_detail_url = "/admin/users/user/{id}/change/"
    user_list_url = "/admin/users/user/"

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get("pk")
        user = get_user_model().objects.filter(id=user_id).first()
        success_url = self.user_detail_url.format(id=user_id)
        if user is None:
            messages.error(request, "User with this id does not exists!")
            success_url = self.user_list_url
        else:
            try:
                cognito_services.resend_verification_email(user.email)
                messages.success(
                    request, "OTP is sent successfully to the user's email!"
                )
            except ValidationError as e:
                messages.error(request, e.args[0])
        return HttpResponseRedirect(success_url)


@staff_member_required
def upload_users_csv(request):
    template_name = "admin/users/upload_users_csv.html"
    success_url = "/admin/base/usercsvupload"
    if request.method == "POST":
        form = UploadUserCSVForm(request.POST, request.FILES)
        if form.is_valid():
            create_users = form.cleaned_data.get("create_users")
            handle_uploaded_file(request.FILES["csv_file"])
            if create_users is True:
                create_users_from_csv.delay()
            else:
                send_users_to_campaign_monitor_from_csv.delay()
            messages.success(
                request, "User upload process has been started successfully!"
            )
            return HttpResponseRedirect(success_url)
    else:
        form = UploadUserCSVForm()
    return render(request, template_name, {"form": form})


@method_decorator(staff_member_required, name="dispatch")
class SendUserDataToCampaignMonitorView(View):
    user_detail_url = "/admin/users/user/{id}/change/"
    user_list_url = "/admin/users/user/"

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get("pk")
        user = get_user_model().objects.filter(id=user_id).first()
        success_url = self.user_detail_url.format(id=user_id)
        if user is None:
            messages.error(request, "User with this id does not exists!")
            success_url = self.user_list_url
        else:
            _, error = campaign_monitor_services.add_new_subscriber(user)
            if error is None:
                messages.success(
                    request, "User data has been successfully sent to Campaign Monitor!"
                )
            else:
                messages.error(
                    request, f"Error in sending data to campaign monitor: {error}"
                )
        return HttpResponseRedirect(success_url)


@method_decorator(staff_member_required, name="dispatch")
class SendUserToConnectsView(View):
    def get(self, request, *args, **kwargs):

        # Importing internally to avoid circular import
        from django.urls import reverse

        from beacon.scc.services import prepare_scc_data_and_send_user_to_scc

        user_list_url = reverse("admin:users_user_changelist")
        scc_api_log_list_url = reverse("admin:scc_sccapilog_changelist")
        user_id = self.kwargs.get("pk")

        user = get_user_model().objects.filter(id=user_id).first()
        if user is None:
            messages.error(request, "User with this id does not exists!")
            success_url = user_list_url
        else:
            prepare_scc_data_and_send_user_to_scc(user=user)
            success_url = scc_api_log_list_url + f"?q={user.email}"
            messages.success(
                request,
                f"The user {user.email} is sent to Service Care Connect. "
                "A new SCC API response log will be available on top. "
                "Try refreshing the page after some time.",
            )

        return HttpResponseRedirect(success_url)


@method_decorator(staff_member_required, name="dispatch")
class ResendWelcomeEmailView(View):
    user_detail_url = "/admin/users/user/{id}/change/"
    user_list_url = "/admin/users/user/"

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get("pk")
        User = get_user_model()
        user = User.objects.filter(id=user_id).first()
        success_url = self.user_detail_url.format(id=user_id)
        if user is None:
            messages.error(request, "User with this id does not exists!")
            success_url = self.user_list_url
        else:
            if user.source in (User.ADMIN, User.SCC, User.CSV):
                generate_password_and_send_welcome_email.apply_async(
                    kwargs={"user_id": user_id}
                )
                messages.success(
                    request,
                    'Welcome email has been re-sent. If member needs a new verification code, click "RESEND VERIFICATION".',
                )
            else:
                messages.error(
                    request,
                    'Cannot send Welcome email, as user self-registered with a custom password. Advise member to use the "Forgot?" password option on their Beacon Wellbeing login page.',
                )
        return HttpResponseRedirect(success_url)
