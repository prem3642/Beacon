# -*- coding: utf-8 -*-
# Generated by Django 2.2.10 on 2020-02-14 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0027_auto_20200207_1158"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="show_safety_screen",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether to show safety screen after this question if not answered yet!",
                verbose_name="Show Safety Screen",
            ),
        ),
    ]