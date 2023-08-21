# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-08-16 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0011_auto_20190506_1840"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="user_response_attribute",
            field=models.CharField(
                blank=True,
                choices=[
                    ("emotional_support_for", "emotional_support_for"),
                    ("appointment_state", "appointment_state"),
                    ("chief_complaint1", "chief_complaint1"),
                    ("chief_complaint2", "chief_complaint2"),
                    (
                        "how_often_less_interest_in_things",
                        "how_often_less_interest_in_things",
                    ),
                    ("how_often_depressed", "how_often_depressed"),
                    ("how_often_nervous", "how_often_nervous"),
                    ("how_often_worry", "how_often_worry"),
                    (
                        "difficulty_in_keeping_drinking_limit",
                        "difficulty_in_keeping_drinking_limit",
                    ),
                    ("felt_cut_down_drinking", "felt_cut_down_drinking"),
                    ("how_emotionally_doing", "how_emotionally_doing"),
                    ("how_physical_health", "how_physical_health"),
                    (
                        "comfortable_in_managing_finances",
                        "comfortable_in_managing_finances",
                    ),
                    ("people_support", "people_support"),
                    ("resources_to_manage", "resources_to_manage"),
                    (
                        "number_of_days_less_productive",
                        "number_of_days_less_productive",
                    ),
                    ("number_of_days_missed_work", "number_of_days_missed_work"),
                ],
                max_length=50,
                null=True,
                verbose_name="User Response Attribute",
            ),
        ),
    ]