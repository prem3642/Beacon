# -*- coding: utf-8 -*-
# Generated by Django 2.1.11 on 2019-11-13 08:11

import regex_field.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0022_question_validate_number_length"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="validate_number_length",
        ),
        migrations.AddField(
            model_name="question",
            name="regex",
            field=regex_field.fields.RegexField(
                help_text="Will be used to validate if question type is Regex",
                max_length=128,
                null=True,
                verbose_name="Regex for Validation",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="kind",
            field=models.CharField(
                choices=[
                    ("dropdown", "Dropdown"),
                    ("checkbox", "Checkbox"),
                    ("radio", "Radio"),
                    ("number", "Number"),
                    ("text", "Text"),
                    ("text_box", "Text Box"),
                    ("yes_no", "Yes/No"),
                    ("terminal", "Terminal"),
                    ("multiple_questions", "Multiple Questions"),
                    ("regex", "Regex"),
                ],
                max_length=20,
                verbose_name="Type",
            ),
        ),
    ]
