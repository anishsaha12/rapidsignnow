# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0009_auto_20170706_1651'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lawfirm',
            old_name='active',
            new_name='is_active',
        ),
        migrations.AddField(
            model_name='lawfirm',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 58, 219394, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lawfirm',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 59, 820195, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lawfirmrates',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 30, 1, 327919, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lawfirmrates',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 30, 2, 634048, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_for_children',
            field=models.FloatField(default='25.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='75.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_for_one_signature',
            field=models.FloatField(default='149.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_when_signature_not_obtained',
            field=models.FloatField(default='90.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_out_of_area_payment_for_children',
            field=models.FloatField(default='25.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_out_of_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='75.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_out_of_area_payment_for_one_signature',
            field=models.FloatField(default='195.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_out_of_area_payment_when_signature_not_obtained',
            field=models.FloatField(default='90.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='maximum_in_area_payment_for_any_number_of_signatures',
            field=models.FloatField(default='300.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='maximum_out_of_area_payment_for_any_number_of_signatures',
            field=models.FloatField(default='300.00'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='mileage_compensation_rate',
            field=models.FloatField(default='.5'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='mileage_threshold',
            field=models.FloatField(default='75.00'),
        ),
    ]
