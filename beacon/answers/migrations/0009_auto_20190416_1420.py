# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-04-16 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0008_auto_20190415_0857"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userresponse",
            name="felt_cut_down_drinking",
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name="userresponse",
            name="used_drugs",
            field=models.NullBooleanField(),
        ),
    ]
