# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-03-22 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0002_auto_20190320_1012"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="company_code",
            field=models.CharField(
                blank=True,
                help_text="e.g.: 3344",
                max_length=50,
                null=True,
                verbose_name="Company Code",
            ),
        ),
        migrations.AddField(
            model_name="organisation",
            name="share_url",
            field=models.URLField(
                blank=True,
                help_text="e.g.: https://client.mybeaconwellbeing.com",
                null=True,
                verbose_name="Share URL",
            ),
        ),
        migrations.AlterField(
            model_name="organisation",
            name="domain",
            field=models.CharField(
                db_index=True,
                help_text="e.g.: client.mybeaconwellbeing.com",
                max_length=50,
                unique=True,
                verbose_name="Domain or Host as unique identifier",
            ),
        ),
    ]
