# Generated by Django 3.2.11 on 2023-03-28 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_alter_user_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='dfd_user_id',
            field=models.CharField(blank=True, max_length=60, null=True, unique=True, verbose_name='dfd user id'),
        ),
    ]