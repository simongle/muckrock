# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-02-21 21:44


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0024_auto_20190213_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='monthly_requests',
            field=models.IntegerField(default=0, help_text=b'How many recurring monthly requests are left for this month - these do not roll over and are just reset to `requests_per_month` on `date_update`'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='number_requests',
            field=models.IntegerField(default=0, help_text=b'How many individually purchased requests this organization has - these never expire and are unaffected by the monthly roll over'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='requests_per_month',
            field=models.IntegerField(default=0, help_text=b'How many monthly requests this organization gets each month'),
        ),
    ]
