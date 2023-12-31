# Generated by Django 3.1.6 on 2021-10-26 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0028_auto_20210312_1135"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="benefit_package",
            field=models.CharField(
                blank=True, max_length=4, verbose_name="Benefit Package"
            ),
        ),
        migrations.AddField(
            model_name="organisation",
            name="group_number",
            field=models.CharField(
                blank=True, max_length=6, verbose_name="Group Number"
            ),
        ),
    ]
