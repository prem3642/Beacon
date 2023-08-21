# Generated by Django 2.1.7 on 2019-02-26 08:37

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="siteconfiguration",
            options={"verbose_name": "site configuration"},
        ),
        migrations.AlterField(
            model_name="siteconfiguration",
            name="fake_patient",
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
