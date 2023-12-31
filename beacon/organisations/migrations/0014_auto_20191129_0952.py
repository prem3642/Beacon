# -*- coding: utf-8 -*-
# Generated by Django 2.2.6 on 2019-11-29 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0013_organisation_parent_code"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="organisation",
            options={
                "ordering": ["parent_code", "username", "-created_at"],
                "verbose_name": "organisation",
                "verbose_name_plural": "organisations",
            },
        ),
    ]
