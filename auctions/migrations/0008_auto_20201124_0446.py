# Generated by Django 3.1.3 on 2020-11-24 04:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_auto_20201123_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='current_bid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auctions.bid'),
        ),
    ]
