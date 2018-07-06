# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LawFirm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('phone_number_one', models.CharField(max_length=20)),
                ('phone_number_two', models.CharField(max_length=20)),
                ('phone_number_three', models.CharField(max_length=20)),
                ('email_one', models.EmailField(max_length=254)),
                ('email_two', models.EmailField(max_length=254)),
                ('number_of_free_miles', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('address', models.ForeignKey(to='address.Address')),
            ],
        ),
        migrations.CreateModel(
            name='LawFirmRates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('default_in_area_payment_for_one_signature', models.FloatField(default=0.0)),
                ('default_in_area_payment_for_each_additional_adult_signature', models.FloatField(default=0.0)),
                ('default_in_area_payment_for_children', models.FloatField(default=0.0)),
                ('maximum_in_area_payment_for_any_number_of_signatures', models.FloatField(default=0.0)),
                ('default_out_of_area_payment_for_one_signature', models.FloatField(default=0.0)),
                ('default_out_of_area_payment_for_each_additional_adult_signature', models.FloatField(default=0.0)),
                ('default_out_of_area_payment_for_children', models.FloatField(default=0.0)),
                ('maximum_out_of_area_payment_for_any_number_of_signatures', models.FloatField(default=0.0)),
            ],
        ),
        migrations.AddField(
            model_name='lawfirm',
            name='rates',
            field=models.ForeignKey(blank=True, to='law_firm.LawFirmRates', null=True),
        ),
    ]
