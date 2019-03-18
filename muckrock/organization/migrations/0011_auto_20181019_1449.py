# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-10-19 18:49
from __future__ import unicode_literals

# Django
from django.db import migrations
from django.utils.text import slugify

# Standard Library
import uuid


def create_memberships(apps, schema_editor):
    Organization = apps.get_model('organization', 'Organization')
    Membership = apps.get_model('organization', 'Membership')
    for org in Organization.objects.all():
        Membership.objects.bulk_create([
            Membership(
                user=p.user,
                organization=org,
                active=True,
                admin=p.user == org.owner
            ) for p in org.members.all()
        ])
        if not Membership.objects.filter(
            user=org.owner, organization=org
        ).exists():
            Membership.objects.create(
                user=org.owner, organization=org, active=False, admin=True
            )


def delete_memberships(apps, schema_editor):
    Membership = apps.get_model('organization', 'Membership')
    Membership.objects.all().delete()


def generate_unqiue_slug(Organization, name):
    original_slug = slug = slugify(name)[:255]
    index = 1

    while True:
        if not Organization.objects.filter(slug=slug).exists():
            return slug

        index += 1

        tail_length = len(str(index)) + 1
        combined_length = len(original_slug) + tail_length
        if combined_length > 255:
            original_slug = original_slug[:255 - tail_length]

        slug = '{}-{}'.format(original_slug, index)


def create_individual_orgs(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Organization = apps.get_model('organization', 'Organization')
    Membership = apps.get_model('organization', 'Membership')
    Profile = apps.get_model('accounts', 'Profile')
    # make profiles for any users which dont have one
    # this shouldn't happen, but it does!
    for user in User.objects.filter(profile=None):
        Profile.objects.create(
            user=user,
            acct_type='basic',
            full_name=u'{} {}'.format(user.first_name, user.last_name),
            uuid=uuid.uuid4(),
        )
    for user in User.objects.all():
        if user.profile.acct_type == 'pro':
            org_type = 1  # pro
        else:
            org_type = 0  # free
        org = Organization.objects.create(
            name=user.username,
            slug=generate_unqiue_slug(Organization, user.username),
            uuid=user.profile.uuid,
            private=True,
            individual=True,
            org_type=org_type,
            owner=user,
            max_users=1,
            monthly_cost=0,
            _monthly_requests=0,
        )
        Membership.objects.create(
            user=user,
            organization=org,
            active=not user.organizations.filter(active=True).exists(),
            admin=True,
        )


def delete_individual_orgs(apps, schema_editor):
    Organization = apps.get_model('organization', 'Organization')
    Organization.objects.filter(individual=True).delete()


def inactive_orgs(apps, schema_editor):
    """Put inactive organizations onto the free plan"""
    Organization = apps.get_model('organization', 'Organization')
    Organization.objects.filter(active=False).update(org_type=0)


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0010_auto_20181022_1116'),
        ('accounts', '0047_auto_20181017_1646'),
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.RunPython(
            inactive_orgs,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            create_memberships,
            reverse_code=delete_memberships,
        ),
        migrations.RunPython(
            create_individual_orgs,
            reverse_code=delete_individual_orgs,
        ),
    ]
