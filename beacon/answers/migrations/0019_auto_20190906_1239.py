# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-09-06 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0018_auto_20190903_0616"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userappointment",
            name="f2f_confirm",
        ),
        migrations.AlterField(
            model_name="userappointment",
            name="f2f_gender_preference",
            field=models.CharField(
                blank=True,
                max_length=15,
                null=True,
                verbose_name="F2F Gender Preference",
            ),
        ),
    ]
