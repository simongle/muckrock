# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-05 18:41


from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foiamachine', '0004_auto_20161005_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='foiamachinerequest',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
