# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0016_auto_20170710_1519'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='amount_paid_to_law_firm',
            new_name='amount_billed_to_law_firm',
        ),
        migrations.RenameField(
            model_name='case',
            old_name='creation_time',
            new_name='created_at',
        ),
        migrations.RemoveField(
            model_name='case',
            name='clients',
        ),
        migrations.AddField(
            model_name='case',
            name='additional_expenses_description',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='case',
            name='did_investigator_travel',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='investigator_bonus_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='case',
            name='investigator_bonus_reason',
            field=models.CharField(default=b'Not Provided', max_length=200),
        ),
        migrations.AddField(
            model_name='case',
            name='is_case_valid',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='case',
            name='is_dol_provided',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='is_minimum_payment_made',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='minimum_payment_from_lawfirm',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='case',
            name='minimum_payment_to_broker',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='case',
            name='number_of_adult_signatures_obtained',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='case',
            name='number_of_adult_signatures_required',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='case',
            name='number_of_child_signatures_obtained',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='case',
            name='number_of_child_signatures_required',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='case',
            name='pay_investigator_bonus',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='type_description',
            field=models.CharField(default=b'', max_length=200),
        ),
        migrations.AddField(
            model_name='case',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 35, 891547, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='case',
            name='client_address',
            field=models.ForeignKey(blank=True, to='address.Address', null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='broker.Broker', null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='dol',
            field=models.DateTimeField(default=b'2017-01-01 00:00:00.000000'),
        ),
        migrations.AlterField(
            model_name='case',
            name='expected_payment',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='case',
            name='investigator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='investigator.Investigator', null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='status',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='case',
            name='type',
            field=models.CharField(default=b'default', max_length=20),
        ),
    ]
