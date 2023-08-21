# -*- coding: utf-8 -*-
# Third Party Stuff
from django.urls import re_path
from rest_framework.routers import DefaultRouter

# beacon Stuff
from beacon.answers.api import AnswerViewSet, AppointmentViewSet
from beacon.base.api.routers import SingletonRouter
from beacon.mdlive.api import (
    AppointmentSlotQueryViewSet,
    ContactViewSet,
    DocumentsViewSet,
    MDLiveViewSet,
    MessageViewSet,
)
from beacon.organisations.api import (
    HomepageNavViewSet,
    OrganisationConfigurationView,
    OrganisationsViewset,OrganisationConfigurationView2
)
from beacon.phrases.api import HomePagePhraseViewSet
from beacon.questionnaire.api import QuestionViewSet
from beacon.scc.api import SCCSyncViewSet
from beacon.users.api import AuthViewSet, CurrentUserViewSet, DFDRegistration,DFDlogin

default_router = DefaultRouter(trailing_slash=False)
singleton_router = SingletonRouter(trailing_slash=False)

# Register all the django rest framework viewsets below.
default_router.register("answers", AnswerViewSet, basename="answers")
default_router.register("appointments", AppointmentViewSet, basename="appointments")
default_router.register("organisations", OrganisationsViewset, basename="organisations")
default_router.register("auth", AuthViewSet, basename="auth")
default_router.register("questions", QuestionViewSet, basename="questions")
default_router.register("mdlive", MDLiveViewSet, basename="mdlive")
default_router.register("messages", MessageViewSet, basename="messages")
default_router.register("contacts", ContactViewSet, basename="contacts")
default_router.register("phrases/home", HomePagePhraseViewSet, basename="phrases-home")
default_router.register(
    "appointment-slot-queries",
    AppointmentSlotQueryViewSet,
    basename="appointment-slot-queries",
)
default_router.register("documents", DocumentsViewSet, basename="documents")
default_router.register("homepage-navs", HomepageNavViewSet, basename="homepage-navs")
default_router.register("users", SCCSyncViewSet, basename="users")
singleton_router.register("me", CurrentUserViewSet, basename="me")

# Combine urls from both default and singleton routers and expose as
# 'urlpatterns' which django can pick up from this module.
urlpatterns = (
    default_router.urls
    + singleton_router.urls
    + [
        re_path(
            r"^organisations/configuration$",
            OrganisationConfigurationView.as_view(),
            name="org-config",
        ),
        re_path(
            r"^organisations/v2/configuration$",
            OrganisationConfigurationView2.as_view(),
            name="org-config",
        ),
        re_path(
            r"^v2/userdetails",
            DFDlogin.as_view(),
            name="dfd_login",
        ),
        re_path(r"^auth/v2/registration",
                DFDRegistration.as_view(),
                name="org-config")
    ]
)
