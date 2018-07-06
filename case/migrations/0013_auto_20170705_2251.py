# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0012_case_random_string'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='basic_fee',
            new_name='basic_fee_investigator',
        ),
        migrations.RenameField(
            model_name='case',
            old_name='mileage_rate',
            new_name='basic_fee_law_firm',
        ),
        migrations.RenameField(
            model_name='case',
            old_name='no_of_free_miles',
            new_name='mileage_rate_investigator',
        ),
        migrations.AddField(
            model_name='case',
            name='is_signature_obtained',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='mileage_rate_law_firm',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='no_of_free_miles_investigator',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='no_of_free_miles_law_firm',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
