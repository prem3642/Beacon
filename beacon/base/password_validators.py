# -*- coding: utf-8 -*-
# Standard Library
import re

# Third Party Stuff
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ComplexPasswordValidator:
    """
    Validate whether the password contains minimum one uppercase, one digit and one symbol.
    """

    def validate(self, password, user=None):
        if (
            re.search("[A-Z]", password) is None
            or re.search("[a-z]", password) is None
            or re.search("[0-9]", password) is None
        ) or re.search("[!#$~]", password) is None:
            raise ValidationError(
                _(
                    "Password must contain at least one uppercase, one lowercase, any of the special characters among "
                    "! # $ ~ and one number."
                ),
                code="password_is_weak",
            )

    def get_help_text(self):
        return _(
            "Password must contain at least one uppercase, one lowercase, any of the special characters among "
            "! # $ ~ and one number."
        )
