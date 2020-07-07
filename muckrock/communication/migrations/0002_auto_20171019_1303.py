# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-19 13:03

# Django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaddress',
            name='status',
            field=models.CharField(
                choices=[('good', 'Good'), ('error', 'Error')],
                default='good',
                max_length=5
            ),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='status',
            field=models.CharField(
                choices=[('good', 'Good'), ('error', 'Error')],
                default='good',
                max_length=5
            ),
        ),
    ]
