# -*- coding: utf-8 -*-
# Generated by Django 3.2.11 on 2022-02-22 16:02

from django.db import migrations


def remove_blank_address2(apps, schema_editor):
    """
    The field `address2` in `User` model is decided to be null=True, and blank=False.
    See `./docs/backend/decision_records/character_fields_with_null_true`

    So blank values are not valid for this field. However, users which have been created using "Register New User" form
    on Django Admin have saved blank values in their `address2` when no data provided for this field in the form at the
    time of registration. This migration removes all such blanks to `null`.
    """
    user_model = apps.get_model("users", "User")
    users_qs = user_model.objects.filter(address2="")
    users_qs.update(address2=None)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0031_alter_user_state"),
    ]

    operations = [
        migrations.RunPython(remove_blank_address2, migrations.RunPython.noop),
    ]
