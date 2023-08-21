# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _

from beacon.base.models import TimeStampedUUIDModel


class HomePagePhrase(TimeStampedUUIDModel):
    """Store answers from each individual"""

    headline = models.CharField(_("headline"), max_length=256, null=False, blank=False)
    sub_headline = models.CharField(
        _("sub-headline"), max_length=350, null=False, blank=False
    )
    is_published = models.BooleanField(
        "published",
        default=True,
        help_text="Designates whether this message is visible on frontend or not!",
    )

    class Meta:
        db_table = "home_page_phrase"
        verbose_name = _("home page phrase")
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return "{} - {}".format(self.id, self.headline)
