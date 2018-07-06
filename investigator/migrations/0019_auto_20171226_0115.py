# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0018_auto_20171208_0408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='15.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_in_area_payment_for_one_signature',
            field=models.FloatField(default='65.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_for_each_additional_adult_signature',
            field=models.FloatField(default='15.00'),
        ),
        migrations.AlterField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_for_one_signature',
            field=models.FloatField(default='65.00'),
        ),
    ]
