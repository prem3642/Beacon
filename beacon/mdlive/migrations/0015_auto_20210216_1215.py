# Generated by Django 3.1.6 on 2021-02-16 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mdlive", "0014_auto_20200303_1205"),
    ]

    operations = [
        migrations.AlterField(
            model_name="provider",
            name="specialities",
            field=models.JSONField(blank=True, null=True, verbose_name="Specialities"),
        ),
    ]
