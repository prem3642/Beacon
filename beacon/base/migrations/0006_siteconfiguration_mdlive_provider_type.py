# -*- coding: utf-8 -*-
# Generated by Django 2.2.9 on 2020-01-23 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0005_usercsvupload_modified_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteconfiguration",
            name="mdlive_provider_type",
            field=models.PositiveSmallIntegerField(
                default=38,
                help_text="Provider type that needs to be sent every time we search the list on MDLive",
                verbose_name="mdlive_provider_type",
            ),
        ),
    ]
