# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-15 11:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0003_auto_20171101_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='portal',
            name='created_timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.datetime_safe.datetime.now),
            preserve_default=False,
        ),
    ]