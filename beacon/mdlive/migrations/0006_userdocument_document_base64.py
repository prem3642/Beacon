# -*- coding: utf-8 -*-
# Generated by Django 2.2.9 on 2020-01-17 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mdlive", "0005_userdocument"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdocument",
            name="document_base64",
            field=models.TextField(
                blank=True, null=True, verbose_name="document base64"
            ),
        ),
    ]
