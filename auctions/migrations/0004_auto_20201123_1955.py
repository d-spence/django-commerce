# Generated by Django 3.1.3 on 2020-11-23 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20201123_1951'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auction',
            old_name='start_bid',
            new_name='current_bid',
        ),
    ]
