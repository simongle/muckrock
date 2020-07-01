# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-18 18:52


# Django
from django.db import migrations

# Standard Library
import os


def entitlements(apps, schema_editor):
    Organization = apps.get_model("organization", "Organization")
    Plan = apps.get_model("organization", "Plan")
    Entitlement = apps.get_model("organization", "Entitlement")

    for plan in Plan.objects.all():
        resources = {
            'minimum_users': plan.minimum_users,
            'base_requests': plan.base_requests,
            'requests_per_user': plan.requests_per_user,
            'feature_level': plan.feature_level,
        }
        if plan.slug == 'proxy':
            resources['proxy'] = True
        entitlement = Entitlement.objects.create(
            name=plan.name,
            slug=plan.slug,
            resources=resources,
        )
        Organization.objects.filter(plan=plan).update(entitlement=entitlement)


def delete_entitlements(apps, schema_editor):
    Organization = apps.get_model("organization", "Organization")
    Entitlement = apps.get_model("organization", "Entitlement")
    Organization.objects.update(entitlement=None)
    Entitlement.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0028_auto_20200512_1208'),
    ]

    operations = [
        migrations.RunPython(entitlements, delete_entitlements),
    ]
