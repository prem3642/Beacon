# Generated by Django 2.1.7 on 2019-02-20 09:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questionnaire", "0002_auto_20190214_1132"),
    ]

    operations = [
        migrations.AddField(
            model_name="option",
            name="previous_question",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children_options",
                to="questionnaire.Option",
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="nested_question",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="nested_parent",
                to="questionnaire.Question",
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="previous_question",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="questionnaire.Question",
            ),
        ),
        migrations.AlterField(
            model_name="option",
            name="next_question",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="parent_options",
                to="questionnaire.Question",
            ),
        ),
    ]
