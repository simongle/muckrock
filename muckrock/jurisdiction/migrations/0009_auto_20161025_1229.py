# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-25 12:29


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jurisdiction', '0008_appeal'),
    ]

    operations = [
        migrations.AddField(
            model_name='exampleappeal',
            name='title',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='exemption',
            name='aliases',
            field=models.TextField(blank=True),
        ),
    ]
