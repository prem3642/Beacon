# -*- coding: utf-8 -*-
from phonenumber_field.validators import validate_international_phonenumber


def validate_phone_number(value):
    if value and value.startswith("+") is False:
        value = "+1{}".format(value)
    return validate_international_phonenumber(value)
