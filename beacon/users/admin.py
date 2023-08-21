# -*- coding: utf-8 -*-
# Third Party Stuff
import pandas as pd
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.models import Group
from django.db.models import OuterRef, Subquery
from django.forms import ValidationError as DjangoFormValidationError
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError
from reversion.admin import VersionAdmin

# beacon Stuff
from beacon.answers.models import UserAppointment
from beacon.base.utils.csv_export import convert_to_dataframe
from beacon.campaign_monitor.services import add_multiple_subscribers

from .models import ReadOnlyProxyUser, User, UserAgent
from .services import sync_user_data_with_cognito_and_mdlive
from .utils import get_changed_dict_keys


# Forms
# ----------------------------------------------------------------------------


class MyUserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ("email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_staff = True
        user.save()
        call_center_staff_group, _ = Group.objects.get_or_create(
            name="Call Center Staff"
        )
        user.groups.add(call_center_staff_group)
        if commit:
            user.save()
        return user


class MyUserChangeForm(DjangoUserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.fields.get("address2", None):
            self.fields["address2"].required = False
        if self.fields.get("gender", None):
            self.fields["gender"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not self.is_valid():
            return cleaned_data  # other errors exists

        user = self.instance
        # Ensure user is deactivated if deactivation reason is given.
        if cleaned_data.get("deactivation_reason") and cleaned_data.get("is_active"):
            error_msg = "User must be set inactive if deactivation reason is given."
            raise DjangoFormValidationError(error_msg)

        if user.is_superuser or user.is_staff:
            return cleaned_data

        old_user_data = model_to_dict(instance=user, fields=self.fields.keys())
        changed_user_attributes = get_changed_dict_keys(
            new_dict=self.cleaned_data,
            old_dict=old_user_data,
        )
        raise_mdlive_exception = True
        # https://fueled.slack.com/archives/CCXP93TT9/p1618930939066900?thread_ts=1618851355.065200&cid=CCXP93TT9
        # As per discussion on above thread, if only active status is changed then we'll be ignoring MDLive errors.
        if set(changed_user_attributes).issubset({"is_active", "deactivation_reason"}):
            raise_mdlive_exception = False

        # Data should be synced only for patients created through
        # `Register New User` button on the admin, FE APIs, and SCC APIs.
        try:
            sync_user_data_with_cognito_and_mdlive(
                new_user_data=self.data,
                user_id=str(user.id),
                raise_mdlive_exception=raise_mdlive_exception,
            )
        except ValidationError as exc:
            exc_msg = (
                ". ".join(exc.detail) if isinstance(exc.detail, list) else exc.detail
            )
            raise DjangoFormValidationError(f"{exc_msg}")

        return cleaned_data


# ModelAdmins
# ----------------------------------------------------------------------------
@admin.register(User)
class UserAdmin(VersionAdmin, AuthUserAdmin):
    add_form_template = "admin/auth/user/add_form.html"
    model = User
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "connects_mbr_id",
                    "email",
                    "password",
                    "user_agent",
                    "organisation",
                )
            },
        ),
        (
            "Personal Info",
            {
                "fields": (
                    "user_response",
                    "first_name",
                    "last_name",
                    "birthdate",
                    "gender",
                    "phone",
                    "job_title",
                    "relationship_status",
                    "employment_status",
                    "agrees_to_beacon_privacy_notice",
                    "timezone",
                    "dfd_user_id"
                )
            },
        ),
        ("Address", {"fields": ("address1", "address2", "city", "state", "zip")}),
        ("Groups & Permissions", {"fields": ("groups",)}),
        (
            "MDLive",
            {
                "fields": (
                    "mdlive_id",
                    "agrees_to_mdlive_informed_consent",
                    "agrees_to_mdlive_privacy_agreement",
                    "mdlive_consent_user_initials",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_verified",
                    "is_active",
                    "deactivation_reason",
                    "is_staff",
                    "is_superuser",
                    "source",
                    "source_admin",
                    "is_sent_to_campaign_monitor",
                )
            },
        ),
        ("Important dates", {"fields": ("date_joined", "modified_at")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    readonly_fields = (
        "date_joined",
        "modified_at",
        "last_login",
        "mdlive_id",
        "agrees_to_beacon_privacy_notice",
        "agrees_to_mdlive_informed_consent",
        "agrees_to_mdlive_privacy_agreement",
        "is_verified",
        "job_title",
        "relationship_status",
        "employment_status",
        "is_sent_to_campaign_monitor",
        "user_response",
        "source",
        "source_admin",
        "user_agent",
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = (
        "email",
        "mdlive_id",
        "is_verified",
        "is_active",
        "connects_mbr_id",
        "source",
        "get_parent_code",
        "get_benefit_package",
        "get_group_number",
        "date_joined",
    )
    list_filter = (
        "is_superuser",
        "is_active",
        "is_verified",
        "is_sent_to_campaign_monitor",
        "source",
        "source_admin",
        "organisation__parent_code",
    )
    search_fields = ("email", "mdlive_id", "connects_mbr_id")
    ordering = ("email",)
    actions = ["send_data_to_campaign_monitor", "export_as_csv"]

    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            "user_agent": "User's recent device/browser and login activity.",
            "organisation": format_html(
                '<span style="color: #cc0033;"><span "font-weight: bold;">WARNING: </span>Do not change unless MDLIVE has corrected member\'s affiliation in their system.</span>'
            ),
        }
        kwargs.update({"help_texts": help_texts})
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "organisation":
            kwargs["queryset"] = db_field.related_model.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_module_permission(self, request):
        """
        Returning False would ensure that this
        edit view of the user is not visible
        from admin index page and the only way
        to access this admin view is coming
        via `UserReadOnlyAdmin` read-only user view.
        """
        return False

    @admin.display(description="User Agent")
    def get_user_agent(self, obj):
        if obj.user_agent:
            return obj.user_agent
        return None

    def user_response(self, obj):
        user_response_id = str(obj.answer.pk)
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:answers_userresponse_change", args=(user_response_id,)),
                user_response_id,
            )
        )

    def send_data_to_campaign_monitor(self, request, queryset):
        response, error = add_multiple_subscribers(queryset)
        if error is None:
            self.message_user(
                request,
                "Selected users data has been sent to Campaign Monitor Successfully!",
            )
        else:
            self.message_user(request, f"{error}")

    send_data_to_campaign_monitor.short_description = (
        "Send selected users data to campaign monitor"
    )

    @admin.display(description="Parent Code", ordering="organisation__parent_code")
    def get_parent_code(self, obj):
        if obj.organisation:
            return obj.organisation.parent_code
        return None

    @admin.display(
        description="Benefit Package", ordering="organisation__benefit_package"
    )
    def get_benefit_package(self, obj):
        if obj.organisation:
            return obj.organisation.benefit_package
        return None

    @admin.display(description="Group Number", ordering="organisation__group_number")
    def get_group_number(self, obj):
        if obj.organisation:
            return obj.organisation.group_number
        return None

    def export_as_csv(self, request, queryset):
        model_name = slugify(self.model.__name__)
        filename = "{}.csv".format(model_name)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        appointment_method_subquery = Subquery(
            (
                UserAppointment.objects.filter(user_response=OuterRef("answer")).values(
                    "appointment_method"
                )[:1]
            )
        )
        qs = queryset.select_related("answer", "organisation").filter(
            answer__emotional_support_for="Self"
        )
        qs = qs.exclude(answer__how_emotionally_doing__isnull=True).exclude(
            answer__how_emotionally_doing__exact=""
        )
        qs = qs.annotate(appointment_method=appointment_method_subquery)
        csv_fields = [
            "appointment_method",
            "organisation__parent_code",
            "organisation__domain",
            "organisation__username",
            "first_name",
            "last_name",
            "birthdate",
            "gender",
            "address1",
            "address2",
            "city",
            "state",
            "zip",
            "date_joined",
            "phone",
            "email",
            "answer__emotional_support_for",
            "relationship_status",
            "employment_status",
            "job_title",
            "answer__chief_complaint1",
            "answer__chief_complaint2",
            "answer__how_often_less_interest_in_things",
            "answer__how_often_depressed",
            "answer__how_often_nervous",
            "answer__how_often_worry",
            "answer__difficulty_in_keeping_drinking_limit",
            "answer__felt_cut_down_drinking",
            "answer__how_emotionally_doing",
            "answer__how_physical_health",
            "answer__people_support",
            "answer__comfortable_in_managing_finances",
            "answer__resources_to_manage",
            "answer__number_of_days_missed_work",
            "answer__number_of_days_less_productive",
            "organisation__parent__parent_code",
        ]
        column_names = [
            "Appointment Type",
            "ParentCode",
            "Source",
            "Company",
            "FirstName",
            "LastName",
            "DOB",
            "Gender",
            "Address 1",
            "Address 2",
            "City",
            "State",
            "Zip",
            "Date/Time Registered",
            "Phone",
            "Email",
            "Relationship to Member",
            "Relationship Status",
            "Employment Status",
            "Job Category",
            "1. Presenting Problem",
            "2. Secondary Problem",
            "3A. Depression",
            "3B. Depression",
            "5A. Anxiety",
            "5B. Anxiety",
            "7A. Substance Use",
            "7B. Substance Use",
            "8. Emotional",
            "9. Physical",
            "10. Community",
            "11. Finance",
            "12. Resiliency",
            "Outcomes - Days missed work",
            "Outcomes - Days missed work",
            "ParentOrganisationParentCode",
        ]
        df = convert_to_dataframe(
            qs, fields=csv_fields, annotated_fields=["appointment_method"]
        )
        # Reindexing again as django queryset values method was moving annotated fields to the last
        df = df.reindex(columns=csv_fields)
        df.columns = column_names
        # Using parent organisation parent code if its null
        df["ParentCode"] = df["ParentCode"].mask(
            pd.isnull, df["ParentOrganisationParentCode"]
        )

        complaint_mapping = {
            "Family Issues": "FAMILY PROBLEM",
            "Depression": "DEPRESSION",
            "Anxiety": "ANXIETY",
            "Grief or Loss": "GRIEF/LOSS",
            "Relationship Issues": "MARITAL/RELATIONSHIP PROBLEM",
            "Stress": "STRESS",
            "Alcohol or Drug use": "MIXED ALCOHOL AND DRUG ABUSE",
        }
        col_name1 = "1. Presenting Problem"
        col_name2 = "2. Secondary Problem"
        df[col_name1] = df[col_name1].map(complaint_mapping).fillna(df[col_name1])
        df[col_name2] = df[col_name2].map(complaint_mapping).fillna(df[col_name2])
        df.to_csv(response, date_format="%m/%d/%y", columns=column_names[:-1])
        return response

    export_as_csv.short_description = "Export Selected"


@admin.register(ReadOnlyProxyUser)
class UserReadOnlyAdmin(UserAdmin):
    def has_add_permission(self, request):
        return False

    def has_module_permission(self, request):
        """
        This view should be listed in the index page of the admin
        to provide read-only access to the user.
        """
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        response = super().render_change_form(
            request, context, add, change, form_url, obj
        )
        response.context_data["title"] = "View User"
        return response


@admin.register(UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "device_type",
                    "is_touch_capable",
                    "browser",
                    "browser_version",
                    "os",
                    "os_version",
                    "device",
                    "device_brand",
                    "device_model",
                )
            },
        ),
        (
            "Recent Login Activity",
            {
                "fields": (
                    "first_successful_login",
                    "last_successful_login",
                    "last_failed_login",
                    "number_failed_attempts",
                )
            },
        ),
    )
    search_fields = ("user__email", "browser", "device", "device_brand", "os")
    list_filter = ("device_type", "is_touch_capable")
    list_display = (
        "user",
        "device_type",
        "browser",
        "last_successful_login",
        "last_failed_login",
    )
    raw_id_fields = ("user",)
    readonly_fields = (
        "user",
        "device_type",
        "is_touch_capable",
        "browser",
        "browser_version",
        "os",
        "os_version",
        "device",
        "device_brand",
        "device_model",
        "created_at",
        "modified_at",
        "first_successful_login",
        "last_successful_login",
        "last_failed_login",
        "number_failed_attempts",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        # Disable Delete
        actions = super().get_actions(request)
        if actions and actions.get("delete_selected") is not None:
            del actions["delete_selected"]
        return actions

    def last_failed_login(self, obj):
        if obj.user.last_failed_login_attempt_datetime:
            return obj.user.last_failed_login_attempt_datetime.strftime(
                "%d %b %Y %H:%M:%S %Z"
            )
        return None

    def first_successful_login(self, obj):
        return obj.created_at.strftime("%d %b %Y %H:%M:%S %Z")

    def last_successful_login(self, obj):
        return obj.modified_at.strftime("%d %b %Y %H:%M:%S %Z")

    def number_failed_attempts(self, obj):
        return obj.user.num_of_failed_login_attempts
