# -*- coding: utf-8 -*-
# Generated by Django 3.2.11 on 2022-04-05 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0035_auto_20220328_1248"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="timezone",
            field=models.CharField(
                blank=True,
                choices=[
                    ("America/Anchorage", "America/Anchorage"),
                    ("America/Chicago", "America/Chicago"),
                    ("America/Denver", "America/Denver"),
                    ("US/Hawaii", "US/Hawaii"),
                    ("America/Los_Angeles", "America/Los_Angeles"),
                    ("America/New_York", "America/New_York"),
                    ("America/Phoenix", "America/Phoenix"),
                    ("America/Puerto_Rico", "America/Puerto_Rico"),
                ],
                max_length=32,
            ),
        ),
    ]
