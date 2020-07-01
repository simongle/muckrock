# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-22 10:47


import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsource', '0006_auto_20180119_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='crowdsource',
            name='multiple_per_page',
            field=models.BooleanField(default=False, verbose_name=b'Allow multiple submissions per data item'),
        ),
        migrations.AddField(
            model_name='crowdsourceresponse',
            name='number',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='crowdsourcedata',
            name='metadata',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
