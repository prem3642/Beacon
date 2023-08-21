# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

# beacon Stuff
from beacon.base.models import TimeStampedUUIDModel

from . import choices

USER = get_user_model()


class SccApiLog(TimeStampedUUIDModel):
    user = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name="scc_api_log",
        null=True,
    )
    request = JSONField()
    response = JSONField()
    status = models.CharField(
        _("status"), max_length=15, choices=choices.STATUS_CHOICES
    )

    request_direction = models.CharField(
        _("Request Direction"),
        max_length=15,
        null=True,
        choices=choices.REQUEST_DIRECTION_CHOICES,
        help_text="The direction of API request with respect to BWB system.",
    )
    change_diff = JSONField(
        default=None,
        null=True,
        help_text="The updates made on existing data in BWB system.",
    )

    class Meta:
        db_table = "scc_api_log"
        verbose_name = _("scc api log")
        verbose_name_plural = _("scc api logs")
        ordering = ["created_at"]

    def __str__(self):
        if self.user:
            return f"{self.user}-{self.status}"
        return f"{self.id}-{self.status}"
