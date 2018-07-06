# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_auto_20170813_1330'),
        ('case', '0017_auto_20170813_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('case_created_at', models.DateTimeField()),
                ('is_signature_obtained', models.BooleanField(default=False)),
                ('did_investigator_travel', models.BooleanField(default=False)),
                ('number_of_adult_signatures_required', models.IntegerField(default=0)),
                ('number_of_child_signatures_required', models.IntegerField(default=0)),
                ('number_of_adult_signatures_obtained', models.IntegerField(default=0)),
                ('number_of_child_signatures_obtained', models.IntegerField(default=0)),
                ('case_name', models.CharField(max_length=300)),
                ('investigator_name', models.CharField(max_length=50)),
                ('case_type', models.CharField(default=b'', max_length=20)),
                ('case_type_description', models.CharField(default=b'', max_length=200)),
                ('client_name', models.CharField(max_length=50)),
                ('client_address', models.CharField(default=b'', max_length=300)),
                ('dol', models.DateTimeField(default=b'2017-01-01 00:00:00.000000')),
                ('case_closing_date', models.DateTimeField()),
                ('is_dol_provided', models.BooleanField(default=False)),
                ('locality', models.CharField(default=b'In Area', max_length=15)),
                ('adult_clients', models.CharField(default=b'', max_length=500)),
                ('child_clients', models.CharField(default=b'', max_length=500)),
                ('basic_fee_law_firm', models.FloatField()),
                ('no_of_free_miles_law_firm', models.FloatField()),
                ('mileage_rate_law_firm', models.FloatField()),
                ('additional_expenses_description', models.CharField(default=b'', max_length=500)),
                ('no_of_miles_travelled', models.FloatField(default=0.0)),
                ('minimum_payment_to_broker', models.FloatField(default=0.0)),
                ('minimum_payment_from_lawfirm', models.FloatField(default=0.0)),
                ('is_minimum_payment_made', models.BooleanField(default=False)),
                ('total_signature_fee_for_adults', models.FloatField(default=0.0)),
                ('total_signature_fee_for_children', models.FloatField(default=0.0)),
                ('total_signature_fee', models.FloatField(default=0.0)),
                ('travel_expenses', models.FloatField(default=0.0)),
                ('additional_expenses', models.FloatField(default=0.0)),
                ('total_amount_billed_to_law_firm', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('case', models.ForeignKey(to='case.Case', on_delete=django.db.models.deletion.PROTECT)),
                ('invoice', models.ForeignKey(to='invoice.Invoice')),
            ],
        ),
    ]
