# -*- coding: utf-8 -*-
# Third Party Stuff
from rest_framework import serializers

from .models import HomePagePhrase


class HomePagePhraseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePagePhrase
        fields = ["id", "headline", "sub_headline"]
        read_only_fields = fields
