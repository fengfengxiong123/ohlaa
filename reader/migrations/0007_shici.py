# Generated by Django 3.0 on 2020-01-05 16:23

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0006_artchapter_section_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiCi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='题目')),
                ('dynasty', models.CharField(max_length=10, verbose_name='朝代')),
                ('author', models.CharField(max_length=20, verbose_name='作者')),
                ('paragraphs', tinymce.models.HTMLField(verbose_name='内容')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]