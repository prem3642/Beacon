# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib import admin

from .models import AppointmentSlotQuery, Contact, Provider, UserDocument


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    search_fields = (
        "user__email",
        "user__mdlive_id",
        "user__first_name",
        "user__last_name",
        "provider__id",
        "user__id",
        "provider__mdlive_id",
        "provider__fullname",
    )
    list_display = ("user", "provider")
    readonly_fields = ("user", "provider")
    raw_id_fields = ("user", "provider")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "provider")

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    search_fields = ("mdlive_id", "fullname", "speciality")
    list_display = ("mdlive_id", "fullname", "speciality")
    list_filter = ("gender",)
    readonly_fields = (
        "mdlive_id",
        "fullname",
        "prefix",
        "gender",
        "speciality",
        "specialities",
        "photo_url",
        "photo_url_absolute",
        "photo_in_binary_data",
        "photo_format",
        "created_at",
        "modified_at",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions


@admin.register(AppointmentSlotQuery)
class AppointmentSlotQueryAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "mdlive_id",
                    "provider_id",
                    "preferred_time",
                    "appointment_method",
                    "appointment_date",
                    "chief_complaint",
                    "chief_complaint_comments",
                    "contact_number",
                    "appointment_request_state",
                    "is_cancelled",
                )
            },
        ),
        ("important dates", {"fields": ("created_at", "modified_at")}),
    )
    search_fields = (
        "user__email",
        "user__mdlive_id",
        "user__first_name",
        "user__last_name",
        "user__id",
        "mdlive_id",
        "provider_id",
    )
    list_display = (
        "mdlive_id",
        "user",
        "provider_id",
        "appointment_method",
        "is_cancelled",
    )
    list_filter = ("appointment_method", "is_cancelled")
    readonly_fields = (
        "user",
        "mdlive_id",
        "provider_id",
        "preferred_time",
        "appointment_method",
        "appointment_date",
        "chief_complaint",
        "chief_complaint_comments",
        "contact_number",
        "appointment_request_state",
        "is_cancelled",
        "created_at",
        "modified_at",
    )
    raw_id_fields = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "mdlive_id",
                    "document_name",
                    "mime_type",
                    "record_type",
                    "extension",
                )
            },
        ),
        ("important dates", {"fields": ("created_at", "modified_at")}),
    )
    search_fields = (
        "user__email",
        "user__mdlive_id",
        "user__first_name",
        "user__last_name",
        "user__id",
        "document_name",
        "mime_type",
        "record_type",
    )
    list_display = ("document_name", "user", "record_type")
    list_filter = ("record_type",)
    readonly_fields = (
        "user",
        "mdlive_id",
        "document_name",
        "mime_type",
        "record_type",
        "extension",
        "created_at",
        "modified_at",
    )
    raw_id_fields = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions
