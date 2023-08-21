# Generated by Django 3.1.6 on 2021-02-26 08:26

from django.db import migrations, models

import beacon.users.models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0023_user_connects_mbr_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReadOnlyProxyUser",
            fields=[],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("users.user",),
            managers=[
                ("objects", beacon.users.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name="user",
            name="connects_mbr_id",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="Connects Member ID"
            ),
        ),
    ]
