# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0011_auto_20170706_0053'),
    ]

    operations = [
        migrations.RenameField(
            model_name='investigator',
            old_name='active',
            new_name='is_active',
        ),
        migrations.AddField(
            model_name='investigator',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 40, 778109, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='investigator',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 42, 223151, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_children',
            field=models.FloatField(default='15.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='30.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_one_signature',
            field=models.FloatField(default='80.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_when_signature_not_obtained',
            field=models.FloatField(default='60.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_for_children',
            field=models.FloatField(default='15.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='30.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_for_one_signature',
            field=models.FloatField(default='80.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_when_signature_not_obtained',
            field=models.FloatField(default='60.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='maximum_in_area_payment_for_any_number_of_signatures',
            field=models.FloatField(default='180.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='maximum_out_of_area_payment_for_any_number_of_signatures',
            field=models.FloatField(default='180.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='mileage_compensation_rate',
            field=models.FloatField(default='.5'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='mileage_threshold',
            field=models.FloatField(default='75.0'),
        ),
    ]
