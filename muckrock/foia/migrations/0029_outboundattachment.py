# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-04-17 20:23

# Django
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

# MuckRock
import muckrock.foia.models.file


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foia', '0028_foiacommunication_fax_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutboundAttachment',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'ffile',
                    models.FileField(
                        max_length=255,
                        upload_to=muckrock.foia.models.file.attachment_path,
                        verbose_name='file'
                    )
                ),
                ('date_time_stamp', models.DateTimeField()),
                (
                    'foia',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='pending_attachments',
                        to='foia.FOIARequest'
                    )
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='pending_attachments',
                        to=settings.AUTH_USER_MODEL
                    )
                ),
            ],
        ),
    ]
