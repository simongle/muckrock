# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-15 15:03


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foia', '0067_auto_20190327_0852'),
    ]

    operations = [
        migrations.AddField(
            model_name='foiarequest',
            name='noindex',
            field=models.BooleanField(default=False, help_text=b"This request's page should not be indexed by search engines"),
        ),
    ]
