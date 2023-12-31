# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-09-24 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0019_question_subheading"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="user_appointment_attribute",
            field=models.CharField(
                blank=True,
                choices=[
                    ("appointment_method", "appointment_method"),
                    ("f2f_confirm", "f2f_confirm"),
                    ("f2f_gender_preference", "f2f_gender_preference"),
                    ("f2f_comfortable_language", "f2f_comfortable_language"),
                    ("f2f_preferred_contact", "f2f_preferred_contact"),
                    ("f2f_preferred_time", "f2f_preferred_time"),
                    ("f2f_okay_to_leave_voicemail", "f2f_okay_to_leave_voicemail"),
                    ("f2f_counselor_search_address", "f2f_counselor_search_address"),
                    ("f2f_address1", "f2f_address1"),
                    ("f2f_address2", "f2f_address2"),
                    ("f2f_zip", "f2f_zip"),
                    ("f2f_city", "f2f_city"),
                    ("f2f_state", "f2f_state"),
                    ("f2f_counselor_notes", "f2f_counselor_notes"),
                ],
                max_length=50,
                null=True,
                verbose_name="User Appointment Attribute",
            ),
        ),
    ]
