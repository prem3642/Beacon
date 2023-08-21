# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-03-13 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_auto_20190307_1009"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="agrees_to_beacon_privacy_notice",
            field=models.BooleanField(
                default=False, verbose_name="agrees to beacon privacy notice"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="agrees_to_mdlive_informed_consent",
            field=models.BooleanField(
                default=False, verbose_name="agrees to mdlive informed consent"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="agrees_to_mdlive_privacy_agreement",
            field=models.BooleanField(
                default=False, verbose_name="agrees to mdlive privacy agreement"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="mdlive_consent_user_initials",
            field=models.CharField(
                blank=True,
                max_length=2,
                null=True,
                verbose_name="mdlive consent user initials of two characters",
            ),
        ),
    ]
