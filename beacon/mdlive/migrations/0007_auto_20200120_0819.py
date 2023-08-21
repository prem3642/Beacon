# -*- coding: utf-8 -*-
# Generated by Django 2.2.9 on 2020-01-20 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mdlive", "0006_userdocument_document_base64"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userdocument",
            name="document_base64",
        ),
        migrations.AlterField(
            model_name="userdocument",
            name="document",
            field=models.TextField(blank=True, null=True, verbose_name="document"),
        ),
    ]