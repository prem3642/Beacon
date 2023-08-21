# -*- coding: utf-8 -*-
# Generated by Django 2.2.10 on 2020-02-25 10:26

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0019_auto_20200214_1125"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organisation",
            name="username",
            field=models.CharField(
                help_text="Username sent to MDLive to link with affiliation. Please only change this field if you know what you are doing.",
                max_length=100,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                verbose_name="username",
            ),
        ),
    ]
