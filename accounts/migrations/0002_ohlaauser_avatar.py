# Generated by Django 3.0 on 2019-12-21 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ohlaauser',
            name='avatar',
            field=models.FileField(blank=True, upload_to='avatar'),
        ),
    ]
