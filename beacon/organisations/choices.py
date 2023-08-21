# -*- coding: utf-8 -*-

# Third Party Stuff
from extended_choices import Choices

ORG_DEACTIVATION_CHOICES = Choices(
    ("PARENT_ORG_DEACTIVATED", "parent_org_deactivated", "Parent org deactivated"),
    ("CLIENT_TERMINATED", "client_terminated", "Client terminated"),
    ("DUPLICATED_ORG", "duplicate_org", "Duplicate org"),
    ("REGISTERED_IN_ERROR", "registered_in_error", "Registered in error"),
)
