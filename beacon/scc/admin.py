# -*- coding: utf-8 -*-
import json

# Third Party Stuff
from django.contrib import admin
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from .models import SccApiLog


@admin.register(SccApiLog)
class SccApiLogAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "status",
                    "request_direction",
                    "change_diff_prettified",
                    "request_prettified",
                    "response_prettified",
                )
            },
        ),
        ("Important dates", {"fields": ("created_at", "modified_at")}),
    )
    readonly_fields = (
        "user",
        "request_prettified",
        "response_prettified",
        "change_diff_prettified",
        "request_direction",
        "status",
        "created_at",
        "modified_at",
    )
    search_fields = ("user__id", "user__email")
    list_display = (
        "id",
        "user",
        "status",
        "request_direction",
        "connects_member_id",
        "mdlive_id",
        "parent_code",
        "benefit_package",
        "group_number",
        "created_at",
    )
    list_filter = ("status",)
    ordering = ("-created_at",)
    raw_id_fields = ("user",)

    def request_prettified(self, instance):
        return self.prettified(json_field=instance.request)

    def response_prettified(self, instance):
        return self.prettified(json_field=instance.response)

    def change_diff_prettified(self, instance):
        return self.prettified(json_field=instance.change_diff)

    def connects_member_id(self, instance):
        response_json = instance.response
        if isinstance(response_json, dict):
            connects_mbr_id = response_json.get("memberId")
            if connects_mbr_id:
                return connects_mbr_id
        return instance.request.get("memberId")

    def mdlive_id(self, instance):
        return instance.request.get("mdLiveMemberID")

    def parent_code(self, instance):
        return instance.request.get("parentCode")

    def benefit_package(self, instance):
        return instance.request.get("benefitPackage")

    def group_number(self, instance):
        return instance.request.get("groupNumber")

    request_prettified.short_description = "request"
    response_prettified.short_description = "response"
    change_diff_prettified.short_description = "changes in BWB"

    def prettified(self, json_field):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(json_field, sort_keys=True, indent=2)

        # Get the Pygments formatter
        formatter = HtmlFormatter(style="igor")

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)
