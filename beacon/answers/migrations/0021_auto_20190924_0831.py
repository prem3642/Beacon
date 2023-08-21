# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-09-24 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0020_userappointment_last_answered_question"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userappointment",
            name="f2f_preferred_time_agreement",
        ),
        migrations.AddField(
            model_name="userappointment",
            name="f2f_okay_to_leave_voicemail",
            field=models.NullBooleanField(verbose_name="F2F Okay to Leave Voicemail"),
        ),
    ]
