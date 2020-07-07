# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-08 13:18

# Django
import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DataField',
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
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('field_number', models.PositiveSmallIntegerField()),
                (
                    'type',
                    models.CharField(
                        choices=[('multi',
                                  'Multiline Text'), ('number', 'Number'),
                                 ('money', 'Money'), ('email',
                                                      'Email'), ('url', 'URL'),
                                 ('bool', 'Boolean'), ('color', 'Color'),
                                 ('date', 'Date'), ('choice',
                                                    'Choice'), ('text',
                                                                'Text')],
                        default='text',
                        max_length=6
                    )
                ),
            ],
            options={
                'ordering': ('field_number',),
            },
        ),
        migrations.CreateModel(
            name='DataRow',
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
                ('row_number', models.PositiveIntegerField(db_index=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'ordering': ('row_number',),
            },
        ),
        migrations.CreateModel(
            name='DataSet',
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
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                (
                    'custom_format',
                    models.CharField(
                        blank=True,
                        choices=[('', '---'), ('email', 'Email Viewer')],
                        max_length=5
                    )
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL
                    )
                ),
            ],
        ),
        migrations.AddField(
            model_name='datarow',
            name='dataset',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rows',
                to='dataset.DataSet'
            ),
        ),
        migrations.AddField(
            model_name='datafield',
            name='dataset',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='fields',
                to='dataset.DataSet'
            ),
        ),
        migrations.AlterUniqueTogether(
            name='datarow',
            unique_together=set([('dataset', 'row_number')]),
        ),
        migrations.AlterUniqueTogether(
            name='datafield',
            unique_together=set([('dataset', 'slug'), ('dataset', 'name'),
                                 ('dataset', 'field_number')]),
        ),
    ]
