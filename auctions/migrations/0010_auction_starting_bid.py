# Generated by Django 3.1.3 on 2020-11-24 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20201124_0502'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='starting_bid',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=10),
            preserve_default=False,
        ),
    ]
