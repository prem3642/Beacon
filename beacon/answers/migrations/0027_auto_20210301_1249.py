# Generated by Django 3.1.6 on 2021-03-01 12:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("answers", "0026_auto_20210216_1215"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userappointment",
            name="f2f_zip",
            field=models.CharField(
                blank=True,
                max_length=10,
                null=True,
                validators=[
                    django.core.validators.MinLengthValidator(5),
                    django.core.validators.RegexValidator(
                        message="Enter a zip code in the format XXXXX or XXXXX-XXXX.",
                        regex="^\\d{5}(?:-\\d{4})?$",
                    ),
                ],
                verbose_name="F2F Zip",
            ),
        ),
    ]
