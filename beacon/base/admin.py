# -*- coding: utf-8 -*-
import json

from django.contrib import admin
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer
from solo.admin import SingletonModelAdmin

from .models import SiteConfiguration, UserCSVUpload

admin.site.register(SiteConfiguration, SingletonModelAdmin)


@admin.register(UserCSVUpload)
class UserCSVUploadAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "status",
                    "csv_total_count",
                    "csv_completed_count",
                    "errors_prettified",
                    "modified_at",
                )
            },
        ),
    )
    readonly_fields = (
        "csv_total_count",
        "csv_completed_count",
        "errors_prettified",
        "modified_at",
    )

    def errors_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.errors, sort_keys=True, indent=2)

        # Get the Pygments formatter
        formatter = HtmlFormatter(style="igor")

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    errors_prettified.short_description = "errors"
