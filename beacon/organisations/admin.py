# -*- coding: utf-8 -*-
# Third Party Stuff
from adminsortable2.admin import CustomInlineFormSet, SortableInlineAdminMixin
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

# Beacon Stuff
from beacon.users.tasks import sync_users_active_status_with_organisation_task

from . import choices, forms, models
from .utils import sync_child_org_active_status_with_parent_org


@admin.register(models.HomepageNav)
class HomepageNavAdmin(admin.ModelAdmin):
    form = forms.HomepageNavAdminForm
    search_fields = (
        "label",
        "url",
        "organisations__organisation__username",
        "organisations__organisation__domain",
        "organisations__organisation__title",
    )
    list_display = (
        "label",
        "url",
        "is_emergency_nav",
        "is_global",
        "is_active",
        "organisation",
    )
    list_filter = ("is_emergency_nav", "is_global", "is_active")

    def has_delete_permission(self, request, obj=None):
        return False

    def organisation(self, instance):
        multiple_clients_msg = "<multiple>"
        if instance.is_global:
            return multiple_clients_msg
        organisation_qs = instance.organisations.all()
        if organisation_qs.exists:
            org_count = organisation_qs.count()
            if org_count == 0:
                return None
            elif org_count == 1:
                return organisation_qs.first().organisation.username
            else:
                return multiple_clients_msg
        return None

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions


@admin.register(models.HomepageNavCategory)
class HomepageNavCategoryAdmin(admin.ModelAdmin):
    search_fields = ("name", "homepage_nav__label")
    list_display = ("name", "homepage_nav")
    raw_id_fields = ["homepage_nav"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("homepage_nav")


@admin.register(models.HomepageNavSubCategory)
class HomepageNavSubCategoryAdmin(admin.ModelAdmin):
    search_fields = ("name", "category__name")
    list_display = ("name", "category")
    raw_id_fields = ["category"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category__homepage_nav")


class HomepageNavInlineFormSet(CustomInlineFormSet, BaseInlineFormSet):
    def clean(self):
        super().clean()

        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data:
                nav = form.cleaned_data.get("homepage_nav")
                is_delete = form.cleaned_data.get("DELETE")
                if is_delete is False:
                    if nav and nav.is_global is True and nav.is_active is True:
                        raise ValidationError(
                            "Homepage Nav you selected is global and "
                            "available for all organisations!"
                        )


class HomepageNavAdminInline(SortableInlineAdminMixin, admin.TabularInline):
    formset = HomepageNavInlineFormSet
    model = models.OrganisationHomepageNav
    fields = ["homepage_nav"]
    raw_id_fields = ["homepage_nav"]
    extra = 0


class ExcludedHomepageNavSubCategoriesAdminInline(admin.TabularInline):
    model = models.ExcludedOrganisationHomepageNavSubCategories
    fields = ["homepage_nav_subcategory"]
    raw_id_fields = ["homepage_nav_subcategory"]
    extra = 0


class OrganisationAdminInline(admin.StackedInline):
    model = models.Organisation
    fields = [
        "title",
        "introduction",
        "location",
        "username",
        "domain",
        "term_date",
        "dfd_client",
        "program_name",
        "logo",
        "glyph",
        "glyph_width",
        "glyph_height",
        "number_of_sessions",
        "session_frequency",
        "is_no_of_sessions_hidden",
        "phone",
        "share_url",
        "parent_code",
        "company_code",
        "show_international_section",
        "enterprise_hash",
        "is_active",
        "deactivation_reason",
        "group_number",
        "benefit_package",
        "alternate_names",
    ]
    extra = 0

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "location":
            # Making location field required for child organisations
            db_field.null = False
            db_field.blank = False
        if db_field.name == "parent_code":
            # Inline inherit parent form restriction
            # Explicitly making parent_code field not required for child organisations
            db_field.null = True
            db_field.blank = True
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    fields = [
        "title",
        "introduction",
        "location",
        "username",
        "domain",
        "term_date",
        "dfd_client",
        "program_name",
        "logo",
        "glyph",
        "glyph_width",
        "glyph_height",
        "number_of_sessions",
        "session_frequency",
        "is_no_of_sessions_hidden",
        "phone",
        "share_url",
        "parent_code",
        "company_code",
        "show_international_section",
        "enterprise_hash",
        "is_active",
        "deactivation_reason",
        "show_safety_screen",
        "safety_screen_phone",
        "show_disclaimer",
        "group_number",
        "benefit_package",
        "alternate_names",
    ]  # , 'template']
    search_fields = (
        "domain",
        "phone",
        "username",
        "title",
        "parent_code",
        "group_number",
        "benefit_package",
    )
    list_filter = ("is_active", "show_international_section", "show_safety_screen")
    list_display = (
        "id",
        "title",
        "username",
        "parent_code",
        "domain",
        "phone",
        "is_active",
        "has_child",
    )
    inlines = [
        HomepageNavAdminInline,
        ExcludedHomepageNavSubCategoriesAdminInline,
        OrganisationAdminInline,
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "location":
            # Making location field not required for root organisations
            db_field.null = True
            db_field.blank = True
        if db_field.name == "parent_code":
            # Making parent_code field required for root organisations
            db_field.null = False
            db_field.blank = False
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)

        # This class is the admin model form of Parent organisation. Therefore, removing "Parent org deactivated" choice
        # from deactivation reasons as this choice isn't valid for a parent organisation.
        for choice in form.base_fields["deactivation_reason"].choices:
            value, display = choice
            if value == choices.ORG_DEACTIVATION_CHOICES.PARENT_ORG_DEACTIVATED:
                form.base_fields["deactivation_reason"].choices.remove(choice)

        return form

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(parent__isnull=True)
        return qs.prefetch_related("children")

    def has_child(self, obj):
        if obj.children.exists():
            return True
        return False

    has_child.boolean = True

    def save_model(self, request, obj, form, change):
        """
        If org's active status is changed, then trigger celery task to sync active status of its users.
        """
        super().save_model(request, obj, form, change)
        if "is_active" in form.changed_data:
            sync_users_active_status_with_organisation_task.delay(
                org_id=form.instance.id,
                is_active=form.instance.is_active,
            )

    def save_formset(self, request, form, formset, change):
        """
        If child org's (inlines) active status is changed, then trigger celery task to sync active status of its
        users. And if parent org's active status is changed, then ensure child org's active status is changed too.
        """
        super().save_formset(request, form, formset, change)
        if formset.model == models.Organisation:
            inline_org_forms = formset.forms
            for inline_form in inline_org_forms:
                child_org = inline_form.instance

                # If child org active status is changed individually
                if "is_active" in inline_form.changed_data:
                    sync_users_active_status_with_organisation_task.delay(
                        org_id=child_org.id,
                        is_active=child_org.is_active,
                    )

                # If parent org active status is changed
                elif "is_active" in form.changed_data:
                    sync_child_org_active_status_with_parent_org(
                        child_org=child_org,
                        is_parent_org_active=form.cleaned_data.get("is_active"),
                        deactivation_reason=choices.ORG_DEACTIVATION_CHOICES.PARENT_ORG_DEACTIVATED,
                    )


@admin.register(models.OrganisationHomepageNav)
class OrganisationHomepageAdmin(admin.ModelAdmin):
    fields = [
        "organisation",
        "homepage_nav",
    ]
    search_fields = (
        "organisation__username",
        "organisation__domain",
        "organisation__title",
        "homepage_nav__label",
    )
    list_display = ("organisation", "homepage_nav")
