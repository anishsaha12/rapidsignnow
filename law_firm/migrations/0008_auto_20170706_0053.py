# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0007_remove_lawfirm_number_of_free_miles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_when_signature_not_obtained',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_out_of_area_payment_when_signature_not_obtained',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='mileage_compensation_rate',
            field=models.FloatField(default='0.0'),
        ),
        migrations.AlterField(
            model_name='lawfirmrates',
            name='mileage_threshold',
            field=models.FloatField(default='0.0'),
        ),
    ]
