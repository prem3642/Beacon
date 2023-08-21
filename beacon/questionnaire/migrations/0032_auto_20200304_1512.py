# -*- coding: utf-8 -*-
# Generated by Django 2.2.10 on 2020-03-04 15:12

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0031_auto_20200303_1231"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="frontend_meta_data",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True,
                help_text="Extra meta data for rendering template on frontend",
                null=True,
                verbose_name="meta data",
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="frontend_url",
            field=models.CharField(
                blank=True,
                help_text='frontend route to render the template if kind is "Frontend"',
                max_length=50,
                null=True,
                verbose_name="Frontend url",
            ),
        ),
    ]