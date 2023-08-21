# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MaxValueValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from uuid_upload_path import upload_to
from versatileimagefield.fields import PPOIField, VersatileImageField

# beacon Stuff
from beacon.base.models import TimeStampedUUIDModel
from beacon.questionnaire.models import IntakeQuestionTemplate
from beacon.users.validators import validate_phone_number

from . import choices


class Organisation(TimeStampedUUIDModel):
    """Store answers from each individual"""

    username_validator = UnicodeUsernameValidator()

    title = models.CharField(_("Title"), max_length=100, null=True, blank=True)
    introduction = models.CharField(
        _("Introduction"), max_length=1024, null=False, blank=True
    )
    location = models.CharField(_("Location"), max_length=30, null=True, blank=True)
    alternate_names = ArrayField(
        models.CharField(max_length=256, blank=True),
        null=True,
        blank=True,
        help_text="Alternate names of this organisation for search purposes. Use commas between names if entering multiple.",
    )
    username = models.CharField(
        _("username"),
        max_length=100,
        help_text=_(
            "Username sent to MDLive to link with affiliation. "
            "Please only change this field if you know what you are doing."
        ),
        validators=[username_validator],
    )
    domain = models.CharField(
        _("Domain or Host as unique identifier"),
        db_index=True,
        max_length=50,
        help_text="e.g.: client.mybeaconwellbeing.com",
    )
    ####BWB3-3
    term_date = models.DateField(_("Client Term Date"), null=True, blank=True)
    program_name = models.CharField(
        _("Program Name"),
        max_length=50,
        null=True,
        blank=True,
        help_text="e.g.: Beacon Wellbeing",
    )
    logo = VersatileImageField(_("Logo"), upload_to=upload_to, null=True, blank=True)
    logo_poi = PPOIField(verbose_name="logo's point of interest")  # point of interest
    glyph = VersatileImageField(
        _("Client Glyph"), upload_to=upload_to, null=True, blank=True
    )
    glyph_poi = PPOIField(
        verbose_name="Client glyph's point of interest"
    )  # point of interest
    glyph_width = models.PositiveSmallIntegerField(
        _("Width of the glyph"),
        null=True,
        blank=True,
        help_text="Width of glyph in px",
    )
    glyph_height = models.PositiveSmallIntegerField(
        _("Height of the glyph"),
        null=True,
        blank=True,
        help_text="Height of glyph in px",
    )
    number_of_sessions = models.PositiveSmallIntegerField(
        _("Number of covered sessions per year"),
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(9999),
        ],
    )
    session_frequency = models.CharField(
        _("Sessions frequency"),
        max_length=120,
        null=False,
        blank=True,
        help_text="Indicates if the number of sessions are per year, per quarter, etc.",
    )
    is_no_of_sessions_hidden = models.BooleanField(
        _("Is number of session hidden"), null=False, blank=True, default=False
    )
    phone = models.CharField(
        _("Phone"), max_length=15, validators=[validate_phone_number]
    )
    share_url = models.URLField(
        _("Share URL"),
        null=True,
        blank=True,
        help_text="e.g.: https://client.mybeaconwellbeing.com",
    )
    parent_code = models.CharField(
        _("Parent Code"),
        null=True,
        blank=True,
        max_length=50,
        help_text="This field is to match internal beacon server code. e.g. NGC, COT",
    )
    company_code = models.CharField(
        _("Company Code"), null=True, blank=True, max_length=50, help_text="e.g.: 3344"
    )
    show_international_section = models.BooleanField(
        _("Show Not in US Section"), default=True
    )
    enterprise_hash = models.CharField(max_length=100, null=True, blank=True)
    dfd_client = models.BooleanField(_("dfd client"),default=False)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this organisation should be treated as "
                  "active. Unselect this instead of deleting.",
    )
    deactivation_reason = models.CharField(
        _("deactivation reason"),
        choices=choices.ORG_DEACTIVATION_CHOICES,
        null=True,
        blank=True,
        default=None,
        max_length=30,
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    show_safety_screen = models.BooleanField(
        _("Show safety screen"),
        default=False,
        help_text="Designates whether this organisation needs to show safety "
                  "screen on Alcohol selection as chief complaint",
    )
    safety_screen_phone = models.CharField(
        _("Safety screen contact number"),
        max_length=15,
        validators=[validate_phone_number],
        null=True,
        blank=True,
    )
    safety_screen_url = models.URLField(_("Safety screen url"), null=True, blank=True)
    show_disclaimer = models.BooleanField(_("Show Disclaimer"), default=False)
    template = models.ForeignKey(
        IntakeQuestionTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="organisations",
        help_text="Template of intake questions flow",
    )
    group_number = models.CharField(
        _("Group Number"), null=False, blank=True, max_length=6
    )
    benefit_package = models.CharField(
        _("Benefit Package"), null=False, blank=True, max_length=4
    )
    search_vector = SearchVectorField(null=True)

    class Meta:
        db_table = "organisation"
        verbose_name = _("organisation")
        verbose_name_plural = _("organisations")
        ordering = [
            "parent_code",
            "username",
            "-created_at",
        ]
        indexes = (GinIndex(fields=["search_vector"]),)

    def clean(self):
        if self.parent is None:
            if self.parent_code is None:
                raise ValidationError(
                    "Parent Code is required for root level organisation!", "invalid"
                )

            qs = self.__class__.objects.filter(domain=self.domain, parent__isnull=True)
            if not self._state.adding:
                qs = qs.exclude(id=self.id)
            if qs.exists():
                raise ValidationError(
                    "Organisation with given domain already exists!", "invalid"
                )
        if self.parent_code is not None:
            qs = self.__class__.objects.filter(
                parent_code=self.parent_code, parent__isnull=True
            )
            if not self._state.adding:
                qs = qs.exclude(id=self.id)
            if qs.exists():
                if self.parent and self.parent.parent_code != self.parent_code:
                    raise ValidationError(
                        "Child organisation parent-code does not matches with parent",
                        "invalid",
                    )
        if self.parent and self.parent.parent is not None:
            raise ValidationError(
                "Assigning a sub-organisation as parent is not allowed!", "invalid"
            )

        if self.deactivation_reason and self.is_active:
            raise ValidationError(
                "Organisation must be set inactive if deactivation reason is specified.",
                "invalid",
            )

    def __str__(self):
        parent_code = self.parent_code
        if not parent_code and self.parent:
            parent_code = self.parent.parent_code
        return f"{parent_code} - {self.username} - {self.title} - {self.location}"


class HomepageNav(TimeStampedUUIDModel):
    label = models.CharField(_("label"), max_length=250)
    url = models.CharField(_("url"), max_length=250)
    description = models.CharField(
        _("description"), null=True, blank=True, max_length=200
    )
    is_emergency_nav = models.BooleanField(
        _("is emergency"),
        default=False,
        help_text="Designates whether this nav is an emergency or not",
    )
    is_global = models.BooleanField(
        _("is_global"),
        default=False,
        help_text="Designates whether this nav is available for all clients or not",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this nav should be treated as " "active.",
    )
    is_url_target_blank = models.BooleanField(
        _("Open URL in new tab"),
        default=False,
        help_text="Designates whether URL opens in new browser tab (instead of same tab)",
    )

    class Meta:
        db_table = "homepage_nav"
        verbose_name = _("homepage nav")
        ordering = ["is_emergency_nav", "created_at"]

    def __str__(self):
        return f"{self.label}-{self.url}"


class OrganisationHomepageNav(TimeStampedUUIDModel):
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="homepage_navs"
    )
    homepage_nav = models.ForeignKey(
        HomepageNav, on_delete=models.CASCADE, related_name="organisations"
    )
    sort_order = models.PositiveIntegerField(
        _("Sort Order"),
        default=0,
        null=False,
        blank=False,
        editable=True,
        unique=False,
        help_text="Designates the position in the list of organisation's homepage navs.",
    )

    class Meta:
        db_table = "organisation_homepage_nav"
        verbose_name = _("organisation homepage nav")
        ordering = [
            "sort_order",
            "created_at",
        ]

    def __str__(self):
        return f"{self.organisation}-{self.homepage_nav}"


class HomepageNavCategory(TimeStampedUUIDModel):
    homepage_nav = models.ForeignKey(
        HomepageNav, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(_("name"), max_length=50)

    class Meta:
        db_table = "homepage_nav_category"
        verbose_name = _("homepage nav category")
        verbose_name_plural = _("homepage nav categories")
        ordering = [
            "created_at",
        ]

    def __str__(self):
        return f"{self.homepage_nav} - {self.name}"


class HomepageNavSubCategory(TimeStampedUUIDModel):
    category = models.ForeignKey(
        HomepageNavCategory, on_delete=models.CASCADE, related_name="subcategories"
    )
    name = models.CharField(_("name"), max_length=50)
    url = models.URLField(_("url"), null=True, blank=True)

    class Meta:
        db_table = "homepage_nav_subcategory"
        verbose_name = _("homepage nav subcategory")
        verbose_name_plural = _("homepage nav subcategories")
        ordering = [
            "created_at",
        ]

    def __str__(self):
        return f"{self.category} - {self.name}"


class ExcludedOrganisationHomepageNavSubCategories(TimeStampedUUIDModel):
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="navs_subcategories"
    )
    homepage_nav_subcategory = models.ForeignKey(
        HomepageNavSubCategory, on_delete=models.CASCADE, related_name="organisations"
    )

    class Meta:
        db_table = "excluded_organisation_homepage_nav_subcategory"
        verbose_name = _("excluded homepage nav subcategory")
        verbose_name_plural = _("excluded homepage nav subcategories")
        ordering = [
            "created_at",
        ]

    def __str__(self):
        return f"{self.organisation} - {self.homepage_nav_subcategory}"
