# Generated by Django 3.1.3 on 2020-11-23 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20201123_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='image',
            field=models.ImageField(upload_to='auction_imgs'),
        ),
    ]