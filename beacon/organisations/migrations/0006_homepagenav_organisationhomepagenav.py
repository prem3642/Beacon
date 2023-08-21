# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-09-23 09:43

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0005_auto_20190325_1510"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomepageNav",
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
                ("nav_id", models.CharField(max_length=50, verbose_name="nav id")),
                ("label", models.CharField(max_length=250, verbose_name="label")),
                ("url", models.CharField(max_length=50, verbose_name="url")),
            ],
            options={
                "verbose_name": "homepage nav",
                "db_table": "homepage_nav",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrganisationHomepageNav",
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
                    "homepage_nav",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organisations",
                        to="organisations.HomepageNav",
                    ),
                ),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="homepage_navs",
                        to="organisations.Organisation",
                    ),
                ),
            ],
            options={
                "verbose_name": "organisation homepage nav",
                "db_table": "organisation_homepage_nav",
                "ordering": ["created_at"],
            },
        ),
    ]
