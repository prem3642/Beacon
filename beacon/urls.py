# -*- coding: utf-8 -*-
"""Root url routering file.

You should put the url config in their respective app putting only a
reference to them here.
"""

# Third Party Stuff
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

# beacon Stuff
from beacon.answers.views import ResendF2FAppointmentDataView
from beacon.scc.views import GetLatestSCCAPILog, GetSCCAPILogs
from beacon.users.views import (
    ConfirmRegisterView,
    RegisterView,
    ResendVerificationView,
    ResendWelcomeEmailView,
    SendUserDataToCampaignMonitorView,
    SendUserToConnectsView,
    upload_users_csv,
)

from . import api_urls
from .base import views as base_views
from .base.api import schemas as api_schemas

admin.site.site_title = admin.site.site_header = "Carelon Wellbeing Admin"
handler500 = base_views.server_error
uuid_regex = "[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[1345][a-fA-F0-9]{3}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12}"

# Top Level Pages
# ==============================================================================
urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Your stuff: custom urls go here
]

urlpatterns += [
    re_path(
        r"^(?P<filename>(robots.txt)|(humans.txt))$",
        base_views.root_txt_files,
        name="root-txt-files",
    ),
    # Rest API
    path("api/", include(api_urls)),
    re_path(
        r"^user-appointment/(?P<pk>%s)/resend-f2f-appointment-data" % uuid_regex,
        ResendF2FAppointmentDataView.as_view(),
        name="user-appointment-resend-f2f-data",
    ),
    re_path(
        r"^users/(?P<pk>%s)/confirm-register" % uuid_regex,
        ConfirmRegisterView.as_view(),
        name="users-confirm-register",
    ),
    re_path(
        r"^users/(?P<pk>%s)/resend-verification" % uuid_regex,
        ResendVerificationView.as_view(),
        name="users-resend-verification",
    ),
    path("users/register", RegisterView.as_view(), name="users-register"),
    path(
        "users/<uuid:pk>/resend-welcome-email",
        ResendWelcomeEmailView.as_view(),
        name="users-resend-welcome-email",
    ),
    path("users/upload_user_csv", upload_users_csv, name="upload-users-csv"),
    re_path(
        r"^users/(?P<pk>%s)/send-campaign-monitor" % uuid_regex,
        SendUserDataToCampaignMonitorView.as_view(),
        name="users-send-campaign-monitor",
    ),
    path(
        "users/<uuid:pk>/send-to-connects",
        SendUserToConnectsView.as_view(),
        name="users-send-to-connects",
    ),
    path(
        "users/<uuid:pk>/latest-scc-api-log",
        GetLatestSCCAPILog.as_view(),
        name="users-latest-scc-api-log",
    ),
    path(
        "users/<uuid:pk>/scc-api-logs",
        GetSCCAPILogs.as_view(),
        name="users-scc-api-logs",
    ),
    # Django Admin
    path(f"{settings.DJANGO_ADMIN_URL}/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.API_DEBUG:
    urlpatterns += [
        # Browsable API
        path("schema/", api_schemas.schema_view, name="schema"),
        path("api-playground/", api_schemas.swagger_schema_view, name="api-playground"),
        path("api/auth-n/", include("rest_framework.urls", namespace="rest_framework")),
    ]

if settings.DEBUG:
    from django.urls import get_callable
    from django.views import defaults as dj_default_views

    urlpatterns += [
        path(
            "400/",
            dj_default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            dj_default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied!")},
        ),
        path("403_csrf/", get_callable(settings.CSRF_FAILURE_VIEW)),
        path(
            "404/",
            dj_default_views.page_not_found,
            kwargs={"exception": Exception("Not Found!")},
        ),
        path("500/", handler500),
    ]

    # Django Debug Toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
