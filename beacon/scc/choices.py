# -*- coding: utf-8 -*-

from extended_choices import Choices

REQUEST_DIRECTION_CHOICES = Choices(
    ("INCOMING", "incoming", "Incoming"),
    ("OUTGOING", "outgoing", "Outgoing"),
)

STATUS_CHOICES = Choices(
    ("SUCCESSFUL", "successful", "Successful"),
    ("FAILED", "failed", "Failed"),
)
