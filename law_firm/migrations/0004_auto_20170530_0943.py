# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0003_lawfirm_rates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_for_children',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_for_one_signature',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_out_of_area_payment_for_children',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_out_of_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_out_of_area_payment_for_one_signature',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='maximum_in_area_payment_for_any_number_of_signatures',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='maximum_out_of_area_payment_for_any_number_of_signatures',
            field=models.FloatField(default='0.0'),
        ),
    ]
