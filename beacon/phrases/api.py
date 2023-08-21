# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from beacon.base import response

from . import models, serializers

User = get_user_model()


class HomePagePhraseViewSet(GenericViewSet):
    serializer_class = serializers.HomePagePhraseSerializer
    queryset = models.HomePagePhrase.objects.filter(is_published=True)
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return response.Ok(serializer.data)
