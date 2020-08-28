# Generated by Django 2.2.15 on 2020-08-28 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0054_auto_20200806_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='org_share',
            field=models.BooleanField(default=False, help_text='Let other members of my organization view my embargoed requests', verbose_name='Share with Organization'),
        ),
    ]
