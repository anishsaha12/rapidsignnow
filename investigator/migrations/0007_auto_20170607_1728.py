# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_address_country'),
        ('investigator', '0006_auto_20170604_2135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investigator',
            name='phone_number_three',
        ),
        migrations.AddField(
            model_name='investigator',
            name='secondary_address',
            field=models.ForeignKey(related_name='secondary_address', blank=True, to='address.Address', null=True),
        ),
        migrations.AddField(
            model_name='investigator',
            name='secondary_language',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='investigator',
            name='tertiary_language',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='investigator',
            name='address',
            field=models.ForeignKey(related_name='address', to='address.Address'),
        ),
        migrations.AlterField(
            model_name='investigator',
            name='email_two',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='investigator',
            name='nickname',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='investigator',
            name='phone_number_two',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
