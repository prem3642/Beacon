# -*- coding: utf-8 -*-
# Third Party Stuff
from django.test import TestCase

# beacon Stuff
from beacon.users.models import User


class UserModelTestCase(TestCase):
    def test_create_user(self):
        u = User.objects.create_user(email="f@F.com", password="abc")
        assert u.is_active is True
        assert u.is_staff is False
        assert u.is_superuser is False
        assert u.email == "f@f.com"
        assert str(u) == u.email

    def test_create_super_user(self):
        u = User.objects.create_superuser(email="f@f.com", password="abc")
        assert u.is_active is True
        assert u.is_staff is True
        assert u.is_superuser is True
        assert str(u) == u.email
