# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-09-23 11:05

from django.db import migrations


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    organisation_model = apps.get_model("organisations", "Organisation")
    homepage_nav_model = apps.get_model("organisations", "HomepageNav")
    organisation_homepage_nav_model = apps.get_model(
        "organisations", "OrganisationHomepageNav"
    )

    homepage_nav_model.objects.bulk_create(
        [
            homepage_nav_model(label="Get emotional support", url="/support"),
            homepage_nav_model(label="Find legal advice", url="/legal"),
            homepage_nav_model(label="Plan your finances", url="/financial"),
            homepage_nav_model(label="Care for your family", url="/family"),
        ]
    )

    homepage_navs = homepage_nav_model.objects.all()
    for org in organisation_model.objects.all():
        for nav in homepage_navs:
            organisation_homepage_nav_model.objects.create(
                organisation=org, homepage_nav=nav
            )


def reverse_func(apps, schema_editor):
    homepage_nav_model = apps.get_model("organisations", "HomepageNav")
    homepage_nav_model.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0008_remove_homepagenav_nav_id"),
    ]

    operations = [migrations.RunPython(forwards_func, reverse_func)]
