# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='basic_fee',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='investigator_expenses',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='signature_fee',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='total_price',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='travel_expenses',
        ),
        migrations.AddField(
            model_name='invoice',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 43, 691436, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invoice',
            name='law_firm_address',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='law_firm_email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='law_firm_name',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='total_billed_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='invoice',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 56, 548432, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
