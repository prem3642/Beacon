# -*- coding: utf-8 -*-
# Generated by Django 2.2.9 on 2020-02-07 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0023_userresponse_request_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="userresponse",
            name="amtrek_safety_sensitive_position",
            field=models.NullBooleanField(default=None),
        ),
    ]
