# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-27 13:12


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0029_auto_20200518_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='entitlement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.Entitlement'),
        ),
    ]
