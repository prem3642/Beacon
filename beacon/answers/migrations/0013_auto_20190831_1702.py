# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-08-31 17:02

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0012_auto_20190506_1840"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserAppointment",
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
                    "mdlive_provider_id",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="MdLive selected provider id",
                    ),
                ),
                (
                    "selected_time_slot",
                    models.CharField(
                        blank=True,
                        max_length=40,
                        null=True,
                        verbose_name="Selected Time Slot",
                    ),
                ),
                (
                    "appointment_method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("video", "video"),
                            ("phone", "phone"),
                            ("face_to_face", "face_to_face"),
                        ],
                        max_length=15,
                        null=True,
                        verbose_name="Appointment Method",
                    ),
                ),
            ],
            options={
                "verbose_name": "appointment",
                "verbose_name_plural": "appointments",
                "db_table": "appointment",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AlterField(
            model_name="userresponse",
            name="appointment_method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("video", "video"),
                    ("phone", "phone"),
                    ("face_to_face", "face_to_face"),
                ],
                max_length=15,
                null=True,
                verbose_name="Appointment Method",
            ),
        ),
        migrations.AlterField(
            model_name="userresponse",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="answer",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="userappointment",
            name="user_response",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="appointments",
                to="answers.UserResponse",
            ),
        ),
    ]
