# -*- coding: utf-8 -*-
# Generated by Django 3.2.8 on 2022-01-17 11:42

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0032_homepagenav_is_url_target_blank"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="alternate_names",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(blank=True, max_length=256),
                help_text="Alternate names of this organisation for search purpose.",
                null=True,
                size=None,
            ),
        ),
    ]
