# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-18 16:51


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdsource', '0004_auto_20180118_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='crowdsourceresponse',
            name='skip',
            field=models.BooleanField(default=False),
        ),
    ]
