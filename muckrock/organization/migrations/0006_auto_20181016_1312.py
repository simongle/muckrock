# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-10-16 17:12
from __future__ import unicode_literals

# Django
from django.db import migrations

# Standard Library
import uuid


def create_uuid(apps, schema_editor):
    Organization = apps.get_model('organization', 'Organization')
    for org in Organization.objects.all():
        org.uuid = uuid.uuid4()
        org.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0005_auto_20181016_1312'),
    ]

    operations = [
        migrations.RunPython(
            create_uuid, reverse_code=migrations.RunPython.noop
        ),
    ]