# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-04-29 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0010_auto_20190425_1123"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userresponse",
            name="physical_health",
        ),
    ]
