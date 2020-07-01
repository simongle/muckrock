# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-10 10:07


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communication', '0001_initial'),
        ('foia', '0036_auto_20170929_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='foiacommunication',
            name='from_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_communications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='foiacommunication',
            name='to_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_communications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='foiarequest',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='foias', to='communication.Address'),
        ),
        migrations.AddField(
            model_name='foiarequest',
            name='cc_emails',
            field=models.ManyToManyField(related_name='cc_foias', to='communication.EmailAddress'),
        ),
        migrations.AddField(
            model_name='foiarequest',
            name='fax',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='foias', to='communication.PhoneNumber'),
        ),
        migrations.RenameField(
            model_name='foiarequest',
            old_name='email',
            new_name='old_email',
        ),
        migrations.AddField(
            model_name='foiarequest',
            name='email',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='foias', to='communication.EmailAddress'),
        ),
        migrations.AddField(
            model_name='rawemail',
            name='email',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='communication.EmailCommunication'),
        ),
        migrations.AlterField(
            model_name='rawemail',
            name='communication',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='foia.FOIACommunication'),
        ),
    ]
