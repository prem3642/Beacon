# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.fields import CIEmailField
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# beacon Stuff
from beacon.base.models import TimeStampedUUIDModel, UUIDModel
from beacon.organisations.models import Organisation

from . import choices


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str,
        is_staff: bool,
        is_superuser: bool,
        **extra_fields,
    ):
        """Creates and saves a User with the given email and password."""
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class User(AbstractBaseUser, UUIDModel, PermissionsMixin):
    API = "api"
    ADMIN = "admin"
    CSV = "csv"
    SCC = "scc"
    SOURCE_CHOICES = ((API, API), (ADMIN, ADMIN), (CSV, CSV), (SCC, SCC))

    # https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/fields/#citext-fields
    email = CIEmailField(_("email address"), unique=True, db_index=True, max_length=50)
    first_name = models.CharField(_("first name"), max_length=35, null=True)
    last_name = models.CharField(_("last name"), max_length=60, null=True)
    dfd_user_id = models.CharField(_("dfd user id"), max_length=60, unique=True, null=True, blank=True)
    phone = models.CharField(_("phone"), max_length=15, null=True)
    birthdate = models.DateField(_("birth date"), null=True)
    address1 = models.CharField(_("address1"), max_length=55, null=True)
    address2 = models.CharField(_("address2"), max_length=55, null=True)
    city = models.CharField(_("city"), max_length=30, null=True)
    zip = models.CharField(
        _("zip"),
        max_length=5,
        null=True,
        validators=[
            MinLengthValidator(5),
            RegexValidator(
                regex=r"\b\d{5}\b", message="Enter a zip code in the format XXXXX"
            ),
        ],
    )
    gender = models.CharField(
        _("gender"), choices=choices.GENDER_CHOICES, null=True, max_length=2
    )
    state = models.CharField(
        _("state"), choices=choices.STATE_CHOICES, null=True, max_length=3
    )
    employment_status = models.CharField(
        _("employment status"),
        choices=choices.EMPLOYMENT_STATUS_CHOICES,
        null=True,
        max_length=50,
    )
    relationship_status = models.CharField(
        _("relationship status"),
        choices=choices.RELATIONSHIP_STATUS_CHOICES,
        null=True,
        max_length=20,
    )
    job_title = models.CharField(
        _("job title"), choices=choices.JOB_TITLE_CHOICE, null=True, max_length=20
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )

    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as "
                  "active. Unselect this instead of deleting accounts.",
    )
    deactivation_reason = models.CharField(
        _("deactivation reason"),
        choices=choices.USER_DEACTIVATION_CHOICES,
        null=True,
        blank=True,
        default=None,
        max_length=30,
    )
    is_verified = models.BooleanField(
        "verified",
        default=False,
        help_text="Designates whether this user email has been verified "
                  "on cognito or not.",
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    mdlive_id = models.IntegerField(
        _("MDLive Id"), null=True, blank=True, db_index=True
    )
    cognito_id_token = models.TextField(_("Cognito Id Token"), null=True, blank=True)
    cognito_refresh_token = models.TextField(
        _("Cognito Refresh Token"), null=True, blank=True
    )
    cognito_access_token = models.TextField(
        _("Cognito Access Token"), null=True, blank=True
    )
    agrees_to_beacon_privacy_notice = models.BooleanField(
        _("agrees to beacon privacy notice"), default=False
    )
    agrees_to_mdlive_informed_consent = models.BooleanField(
        _("agrees to mdlive informed consent"), default=False
    )
    agrees_to_mdlive_privacy_agreement = models.BooleanField(
        _("agrees to mdlive privacy agreement"), default=False
    )
    mdlive_consent_user_initials = models.CharField(
        _("mdlive consent user initials of two characters"),
        max_length=2,
        null=True,
        blank=True,
    )
    organisation = models.ForeignKey(
        Organisation,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="users",
    )
    is_sent_to_campaign_monitor = models.BooleanField(
        "sent to campaign monitor",
        default=False,
        help_text="Designates whether this user's data has been sent"
                  " to campaign monitor or not.",
    )
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    num_of_failed_login_attempts = models.PositiveSmallIntegerField(
        _("Number of failed login attempts"), default=0
    )
    last_failed_login_attempt_datetime = models.DateTimeField(
        _("Last Failed Login Attempt Datetime"), default=None, null=True, blank=True
    )
    source = models.CharField(
        _("source"), max_length=5, choices=SOURCE_CHOICES, default=API
    )
    source_admin = CIEmailField(_("Source Admin Email"), null=False, blank=True)
    connects_mbr_id = models.CharField(
        _("Connects Member ID"), max_length=15, null=False, blank=True
    )
    send_to_scc_if_non_f2f = models.BooleanField(
        _("Send user data to SCC if user doesn't opt for F2F"),
        default=False,
        help_text="Designates whether this user's data is to be send to SCC System"
                  " or not, provided that the user hasn't opted for F2F appointment.",
    )
    # Beacon team needs only a few timezones right now.
    # See: https://linear.app/beacon-health/issue/BEA-172/add-timezone-to-register-endpoint-model
    timezone = models.CharField(
        max_length=32,
        choices=choices.CURRENTLY_ALLOWED_TIMEZONE_CHOICES,
        blank=True,
        null=False,
    )

    USERNAME_FIELD = "email"
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("-date_joined",)

    def __str__(self):
        return str(self.email)


class ReadOnlyProxyUser(User):
    """
    This is only to provide a default read-only admin view, while
    providing a way to actually do write-only permissions in a
    separate tab by the user, so they do not mistakenly make changes.
    """

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        proxy = True


class UserAgent(TimeStampedUUIDModel):
    MOBILE = "mobile"
    PC = "pc"
    TABLET = "tablet"
    BOT = "bot"
    DEVICE_TYPE_CHOICES = (
        (MOBILE, "Mobile"),
        (PC, "PC"),
        (TABLET, "Tablet"),
        (BOT, "Bot"),
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_agent"
    )
    device_type = models.CharField(
        _("Device Type"),
        null=True,
        blank=True,
        max_length=7,
        choices=DEVICE_TYPE_CHOICES,
    )
    is_touch_capable = models.BooleanField(_("is touch capable"), null=True, blank=True)
    browser = models.CharField(_("browser"), max_length=30, null=True, blank=True)
    browser_version = models.CharField(
        _("browser version"), max_length=30, null=True, blank=True
    )
    os = models.CharField(_("os"), max_length=30, null=True, blank=True)
    os_version = models.CharField(_("os version"), max_length=30, null=True, blank=True)
    device = models.CharField(_("device"), max_length=30, null=True, blank=True)
    device_brand = models.CharField(
        _("device brand"), max_length=30, null=True, blank=True
    )
    device_model = models.CharField(
        _("device model"), max_length=30, null=True, blank=True
    )

    class Meta:
        db_table = "user_agent"
        verbose_name = _("user agent")
        verbose_name_plural = _("user agents")
        ordering = ("-modified_at",)

    def __str__(self):
        return f"{self.user} - {self.browser}"
