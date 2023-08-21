# -*- coding: utf-8 -*-
# Generated by Django 2.2.9 on 2019-12-19 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0017_useragent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useragent",
            name="browser",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="browser"
            ),
        ),
        migrations.AlterField(
            model_name="useragent",
            name="os",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="os"
            ),
        ),
    ]