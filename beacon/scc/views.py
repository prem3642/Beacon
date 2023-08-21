# -*- coding: utf-8 -*-

# Third Party Stuff
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from .models import SccApiLog


@method_decorator(staff_member_required, name="dispatch")
class GetLatestSCCAPILog(View):
    def get(self, request, *args, **kwargs):
        user_list_url = reverse("admin:users_user_changelist")
        scc_api_log_list_url = reverse("admin:scc_sccapilog_changelist")
        user_id = self.kwargs.get("pk")

        user = get_user_model().objects.filter(id=user_id).first()
        if not user or not user.email:
            messages.error(request, "User with this id does not exists!")
            success_url = user_list_url
            return HttpResponseRedirect(success_url)

        user_latest_scc_api_log = (
            SccApiLog.objects.filter(user=user).order_by("-created_at").first()
        )
        if not user_latest_scc_api_log:
            messages.error(request, "No latest SCC API log found for this user")
            success_url = scc_api_log_list_url + f"?q={user.email}"
        else:
            messages.success(request, "Redirected to latest SCC API logs for the user.")
            success_url = scc_api_log_list_url + f"{user_latest_scc_api_log.id}"

        return HttpResponseRedirect(success_url)


@method_decorator(staff_member_required, name="dispatch")
class GetSCCAPILogs(View):
    def get(self, request, *args, **kwargs):
        user_list_url = reverse("admin:users_user_changelist")
        scc_api_log_list_url = reverse("admin:scc_sccapilog_changelist")
        user_id = self.kwargs.get("pk")

        user = get_user_model().objects.filter(id=user_id).first()
        if not user or not user.email:
            messages.error(request, "User with this id does not exists!")
            success_url = user_list_url
        else:
            messages.success(request, "Redirected to SCC API logs for the user.")
            success_url = scc_api_log_list_url + f"?q={user.email}"

        return HttpResponseRedirect(success_url)
