# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0009_remove_investigator_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='investigatorrates',
            name='default_in_area_payment_when_signature_not_obtained',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='investigatorrates',
            name='default_out_of_area_payment_when_signature_not_obtained',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='investigatorrates',
            name='mileage_compensation_rate',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='investigatorrates',
            name='mileage_threshold',
            field=models.FloatField(default=0.0),
        ),
    ]
