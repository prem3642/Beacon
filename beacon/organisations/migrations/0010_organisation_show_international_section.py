# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-09-25 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0009_auto_20190923_1105"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="show_international_section",
            field=models.BooleanField(
                default=True, verbose_name="Show Not in US Section"
            ),
        ),
    ]
