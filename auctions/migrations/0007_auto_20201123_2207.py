# Generated by Django 3.1.3 on 2020-11-23 22:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20201123_2158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
