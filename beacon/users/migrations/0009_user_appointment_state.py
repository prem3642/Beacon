# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-04-04 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_auto_20190328_0950"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="appointment_state",
            field=models.CharField(
                blank=True,
                max_length=3,
                null=True,
                verbose_name="MDLive Appointment State",
            ),
        ),
    ]
