# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-08-31 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0014_auto_20190831_1704"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userresponse",
            name="appointment_method",
        ),
        migrations.RemoveField(
            model_name="userresponse",
            name="mdlive_provider_id",
        ),
        migrations.RemoveField(
            model_name="userresponse",
            name="selected_timeslot",
        ),
    ]