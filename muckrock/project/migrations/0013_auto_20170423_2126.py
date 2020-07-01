# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-04-23 21:26


from django.db import migrations, models
import muckrock.core.storage


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_auto_20161211_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=muckrock.core.storage.QueuedS3DietStorage(), upload_to=b'project_images/%Y/%m/%d'),
        ),
    ]
