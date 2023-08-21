# -*- coding: utf-8 -*-
# Third Party Stuff
from django.db.models import F, Q
from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

# beacon Stuff
from beacon.base.models import SiteConfiguration

from .models import (
    HomepageNav,
    HomepageNavCategory,
    HomepageNavSubCategory,
    Organisation,
)


class HomepageNavSubcategorySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = HomepageNavSubCategory
        fields = ["id", "name", "url"]
        read_only_fields = fields

    def get_url(self, obj):
        url = obj.url
        parent_code = self.context.get("parent_code")
        if url:
            return url + parent_code
        return url


class HomepageNavCategorySerializer(serializers.ModelSerializer):
    subcategories = HomepageNavSubcategorySerializer(
        source="filtered_subcategories", many=True
    )

    class Meta:
        model = HomepageNavCategory
        fields = ["id", "name", "subcategories"]
        read_only_fields = fields


class HomepageNavSerializer(serializers.ModelSerializer):
    sort_order = serializers.SerializerMethodField(required=False)

    class Meta:
        model = HomepageNav
        fields = [
            "id",
            "label",
            "url",
            "description",
            "is_emergency_nav",
            "sort_order",
            "is_url_target_blank",
        ]
        read_only_fields = fields

    def get_sort_order(self, obj):
        return obj.sort_order if obj.sort_order else None


class ChildOrganisationSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()
    number_of_sessions = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()
    company_code = serializers.SerializerMethodField()
    show_international_section = serializers.SerializerMethodField()
    parent_code = serializers.SerializerMethodField()
    term_date = serializers.DateField(allow_null=True)

    class Meta:
        model = Organisation
        fields = (
            "id",
            "domain",
            "location",
            "phone",
            "username",
            "term_date",
            "program_name",
            "number_of_sessions",
            "session_frequency",
            "is_no_of_sessions_hidden",
            "share_url",
            "company_code",
            "show_international_section",
            "parent_code",
        )
        read_only_fields = (
            "id",
            "domain",
            "location",
            "phone",
            "username",
            "program_name",
            "logo",
            "glyph",
            "glyph_width",
            "glyph_height",
            "number_of_sessions",
            "session_frequency",
            "is_no_of_sessions_hidden",
            "share_url",
            "company_code",
            "show_international_section",
            "parent_code",
        )

    def get_location(self, obj):
        location = obj.location if obj.location else obj.parent.location
        return location

    def get_phone(self, obj):
        phone = obj.phone if obj.phone else obj.parent.phone
        return phone

    def get_program_name(self, obj):
        program_name = obj.program_name if obj.program_name else obj.parent.program_name
        return program_name

    def get_number_of_sessions(self, obj):
        number_of_sessions = (
            obj.number_of_sessions
            if obj.number_of_sessions
            else obj.parent.number_of_sessions
        )
        return number_of_sessions

    def get_share_url(self, obj):
        share_url = obj.share_url if obj.share_url else obj.parent.share_url
        return share_url

    def get_company_code(self, obj):
        company_code = obj.company_code if obj.company_code else obj.parent.company_code
        return company_code

    def get_show_international_section(self, obj):
        if obj.show_international_section is None:
            return obj.parent.show_international_section
        return obj.show_international_section

    def get_parent_code(self, obj):
        parent_code = obj.parent_code if obj.parent_code else obj.parent.parent_code
        return parent_code


class OrganisationSearchSerializer(serializers.ModelSerializer):
    """
    This exposes limited details about the organisations -- being part of an API to search for the organisation
    """

    class Meta:
        model = Organisation
        fields = (
            "title",
            "domain",
            "location",
        )


class OrganisationSerializer(serializers.ModelSerializer):
    logo = VersatileImageFieldSerializer(sizes="logo_image")
    glyph = VersatileImageFieldSerializer(sizes="logo_image")
    homepage_navs = serializers.SerializerMethodField()
    child_organisations = serializers.SerializerMethodField()
    mdlive_provider_type = serializers.SerializerMethodField()
    term_date = serializers.DateField(allow_null=True)

    class Meta:
        model = Organisation
        fields = (
            "id",
            "domain",
            "location",
            "phone",
            "username",
            "term_date",
            "program_name",
            "logo",
            "glyph",
            "glyph_width",
            "glyph_height",
            "number_of_sessions",
            "session_frequency",
            "is_no_of_sessions_hidden",
            "share_url",
            "company_code",
            "show_international_section",
            "parent_code",
            "mdlive_provider_type",
            "homepage_navs",
            "child_organisations",
            "show_safety_screen",
            "safety_screen_phone",
            "safety_screen_url",
            "show_disclaimer",
            "introduction",
            "dfd_client",
        )
        read_only_fields = fields

    def get_homepage_navs(self, obj):
        homepage_navs_qs = HomepageNav.objects.filter(
            Q(is_active=True), Q(Q(organisations__organisation=obj) | Q(is_global=True))
        ).annotate(sort_order=F("organisations__sort_order"))
        return HomepageNavSerializer(homepage_navs_qs, many=True).data

    def get_child_organisations(self, obj):
        child_orgs = Organisation.objects.select_related("parent").filter(
            is_active=True, parent=obj
        )
        return ChildOrganisationSerializer(child_orgs, many=True).data

    def get_mdlive_provider_type(self, obj):
        site_config = SiteConfiguration.get_solo()
        return site_config.mdlive_provider_type
