# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0004_auto_20170530_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_children',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='1.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_one_signature',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_for_children',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_for_one_signature',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='maximum_in_area_payment_for_any_number_of_signatures',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='maximum_out_of_area_payment_for_any_number_of_signatures',
            field=models.FloatField(default='0.0'),
        ),
    ]
