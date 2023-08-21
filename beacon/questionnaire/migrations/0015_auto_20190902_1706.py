# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-09-02 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0014_question_user_appointment_attribute"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="kind",
            field=models.CharField(
                choices=[
                    ("dropdown", "Dropdown"),
                    ("checkbox", "Checkbox"),
                    ("number", "Number"),
                    ("text", "Text"),
                    ("yes_no", "Yes/No"),
                    ("terminal", "Terminal"),
                    ("multiple_questions", "Multiple Questions"),
                ],
                max_length=20,
                verbose_name="Type",
            ),
        ),
    ]
