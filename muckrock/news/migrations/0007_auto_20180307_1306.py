# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-07 18:06

# Django
import django.core.files.storage
import django.utils.timezone
from django.db import migrations, models

# Third Party
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_auto_20170423_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=easy_thumbnails.fields.ThumbnailerImageField(
                blank=True,
                null=True,
                storage=django.core.files.storage.FileSystemStorage(),
                upload_to='news_images/%Y/%m/%d'
            ),
        ),
        migrations.AlterField(
            model_name='article',
            name='pub_date',
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name='Publish date'
            ),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(
                storage=django.core.files.storage.FileSystemStorage(),
                upload_to='news_photos/%Y/%m/%d'
            ),
        ),
    ]
