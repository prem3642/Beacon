# -*- coding: utf-8 -*-
from django.forms import ModelForm, ValidationError

from . import models


class HomepageNavAdminForm(ModelForm):
    class Meta:
        model = models.HomepageNav
        fields = "__all__"

    def clean_url(self):
        url = self.cleaned_data["url"]
        url_start = "/", "#", "http", "https"
        if url and not any(url.lower().startswith(x) for x in url_start):
            raise ValidationError(f"URL should begin with {', '.join(url_start)}")
        return url
