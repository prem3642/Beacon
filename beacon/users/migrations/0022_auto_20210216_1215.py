# Generated by Django 3.1.6 on 2021-02-16 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0021_auto_20200128_0839"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useragent",
            name="is_touch_capable",
            field=models.BooleanField(
                blank=True, null=True, verbose_name="is touch capable"
            ),
        ),
    ]
