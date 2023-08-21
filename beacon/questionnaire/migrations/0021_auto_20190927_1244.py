# -*- coding: utf-8 -*-
# Generated by Django 2.1.11 on 2019-09-27 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0020_auto_20190924_0831"),
    ]

    operations = [
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
                ],
                max_length=20,
                verbose_name="Type",
            ),
        ),
    ]
