# Generated by Django 3.0 on 2019-12-21 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_ohlaauser_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ohlaauser',
            name='avatar',
            field=models.FileField(default='/avatars/default.png', upload_to='avatar'),
        ),
    ]