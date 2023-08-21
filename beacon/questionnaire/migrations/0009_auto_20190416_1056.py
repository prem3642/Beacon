# -*- coding: utf-8 -*-
# Generated by Django 2.1.7 on 2019-04-16 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0008_option_text_mapped_value"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="no_button_text",
            field=models.CharField(
                blank=True,
                help_text="Required only for Yes/No question type!",
                max_length=50,
                null=True,
                verbose_name="No Button text for YES/NO type",
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="yes_button_text",
            field=models.CharField(
                blank=True,
                help_text="Required only for Yes/No question type!",
                max_length=50,
                null=True,
                verbose_name="Yes Button text for YES/NO type",
            ),
        ),
        migrations.AlterField(
            model_name="option",
            name="text_mapped_value",
            field=models.CharField(
                blank=True, max_length=30, null=True, verbose_name="Text mapped value"
            ),
        ),
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
                ],
                max_length=20,
                verbose_name="Type",
            ),
        ),
    ]
