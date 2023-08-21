# -*- coding: utf-8 -*-
# Generated by Django 2.2.9 on 2020-01-30 10:38

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0016_organisationhomepagenav_allow_search"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomepageNavCategory",
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
                ("name", models.CharField(max_length=50, verbose_name="name")),
                (
                    "homepage_nav",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="categories",
                        to="organisations.HomepageNav",
                    ),
                ),
            ],
            options={
                "verbose_name": "homepage nav category",
                "verbose_name_plural": "homepage nav categories",
                "db_table": "homepage_nav_category",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="HomepageNavSubCategory",
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
                ("name", models.CharField(max_length=50, verbose_name="name")),
                ("url", models.URLField(blank=True, null=True, verbose_name="url")),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subcategories",
                        to="organisations.HomepageNavCategory",
                    ),
                ),
            ],
            options={
                "verbose_name": "homepage nav subcategory",
                "verbose_name_plural": "homepage nav subcategories",
                "db_table": "homepage_nav_subcategory",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="ExcludedOrganisationHomepageNavSubCategories",
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
                    "homepage_nav_subcategory",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organisations",
                        to="organisations.HomepageNavSubCategory",
                    ),
                ),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="navs_subcategories",
                        to="organisations.Organisation",
                    ),
                ),
            ],
            options={
                "verbose_name": "excluded homepage nav subcategory",
                "verbose_name_plural": "excluded homepage nav subcategories",
                "db_table": "excluded_organisation_homepage_nav_subcategory",
                "ordering": ["created_at"],
            },
        ),
    ]
