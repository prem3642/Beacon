# -*- coding: utf-8 -*-

# Third Party Stuff
from django_dynamic_fixture.fixture_algorithms.sequential_fixture import (
    SequentialDataFixture,
)

from .random_generator import randint


class PatchedSequentialDataFixture(SequentialDataFixture):
    """
    Patches default SequentialDataFixture to support PhoneNumberField & return a actual image django file so that image
    processing can be done in the apis (by Versatile Image Field). Default Image file send by SequentialDataFixture is
    just a file on which image processing can't be done
    """

    def phonenumberfield_config(self, field, key):
        return "+12345603%s" % randint(100, 999)

    def jsonfield_config(self, field, key):
        return {}
