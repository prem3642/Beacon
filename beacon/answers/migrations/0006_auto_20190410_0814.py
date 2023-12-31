# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-04-10 08:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0005_auto_20190410_0810"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answer",
            name="number_of_days_less_productive",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MaxValueValidator(365)],
            ),
        ),
        migrations.AlterField(
            model_name="answer",
            name="number_of_days_missed_work",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MaxValueValidator(30)],
            ),
        ),
    ]
