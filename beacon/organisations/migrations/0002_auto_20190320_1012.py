# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-03-20 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organisation",
            name="domain",
            field=models.CharField(
                db_index=True,
                max_length=50,
                unique=True,
                verbose_name="Domain or Host as unique identifier",
            ),
        ),
    ]
