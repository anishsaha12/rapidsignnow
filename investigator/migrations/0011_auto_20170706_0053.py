# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0010_auto_20170705_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_when_signature_not_obtained',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_when_signature_not_obtained',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='mileage_compensation_rate',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='mileage_threshold',
            field=models.FloatField(default='0.0'),
        ),
    ]
