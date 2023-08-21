# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-03-20 09:53

import uuid

import django.contrib.auth.validators
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Organisation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 100 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=100,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "domain",
                    models.URLField(
                        db_index=True,
                        unique=True,
                        verbose_name="Domain as unique identifier",
                    ),
                ),
                (
                    "phone",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, unique=True
                    ),
                ),
                (
                    "enterprise_hash",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this organisation should be treated as active. Unselect this instead of deleting.",
                        verbose_name="active",
                    ),
                ),
            ],
            options={
                "verbose_name": "organisation",
                "verbose_name_plural": "organisations",
                "db_table": "organisation",
                "ordering": ["-created_at"],
            },
        ),
    ]