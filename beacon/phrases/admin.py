# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import HomePagePhrase


@admin.register(HomePagePhrase)
class HomePagePhraseAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("headline", "sub_headline", "is_published")}),
        ("Important dates", {"fields": ("created_at", "modified_at")}),
    )
    readonly_fields = ("created_at", "modified_at")
    search_fields = ("headline", "sub_headline")
    list_display = ("headline", "is_published")
    list_filter = ("is_published",)
