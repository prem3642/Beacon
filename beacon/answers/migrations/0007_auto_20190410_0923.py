# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-04-10 09:23

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("answers", "0006_auto_20190410_0814"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Answer",
            new_name="UserResponse",
        ),
    ]
