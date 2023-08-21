# -*- coding: utf-8 -*-
# Standard Library
import uuid

from django.db import models

# Third Party Stuff
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel
from uuid_upload_path import upload_to
from versatileimagefield.fields import PPOIField, VersatileImageField


class UUIDModel(models.Model):
    """An abstract base class model that makes primary key `id` as UUID
    instead of default auto incremented number.
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class TimeStampedUUIDModel(UUIDModel):
    """An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields with UUID as primary_key field.
    """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class ImageMixin(models.Model):
    """An abstract base class model that provides a VersatileImageField Image with POI"""

    image = VersatileImageField(
        upload_to=upload_to,
        blank=True,
        null=True,
        ppoi_field="image_poi",
        verbose_name="image",
    )
    image_poi = PPOIField(verbose_name="image's Point of Interest")  # point of interest

    class Meta:
        abstract = True


class SiteConfiguration(SingletonModel):
    fake_patient = JSONField(null=True)
    mdlive_provider_type = models.PositiveSmallIntegerField(
        _("mdlive_provider_type"),
        default=38,
        help_text="Provider type that needs to be sent "
        "every time we search the list on MDLive",
    )

    class Meta:
        db_table = "site_configuration"
        verbose_name = _("site configuration")

    def __str__(self):
        return "Site Configuration"


class UserCSVUpload(SingletonModel):
    OPEN_FOR_UPLOAD = "open_for_upload"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    STATUSES = (
        (OPEN_FOR_UPLOAD, "Open for Upload"),
        (IN_PROGRESS, "In Progress"),
        (DONE, "Done"),
    )
    status = models.CharField(
        _("Status"), default=OPEN_FOR_UPLOAD, max_length=20, choices=STATUSES
    )
    # These fields will be used to show progress of csv upload
    csv_total_count = models.IntegerField(_("Total Count"), default=0)
    csv_completed_count = models.IntegerField(_("Completed Count"), default=0)
    errors = JSONField(null=True)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = "user_csv_upload"
        verbose_name = _("User CSV Upload")

    def __str__(self):
        return "User CSV Upload"
