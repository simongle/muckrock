# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-15 12:58


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0008_agency_requires_proxy'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='manual_stale',
            field=models.BooleanField(default=False, help_text=b'For marking an agency stale by hand.'),
        ),
    ]
