# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0010_auto_20170615_1220'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='mileage',
            new_name='no_of_free_miles',
        ),
        migrations.RemoveField(
            model_name='case',
            name='number_of_additional_adult_clients',
        ),
        migrations.RemoveField(
            model_name='case',
            name='number_of_additional_child_clients',
        ),
        migrations.AddField(
            model_name='case',
            name='additional_expenses',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='case',
            name='adult_clients',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='case',
            name='amount_paid_to_investigator',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='case',
            name='amount_paid_to_law_firm',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='case',
            name='child_clients',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='case',
            name='closing_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='case',
            name='dol',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 4, 3, 23, 59, 235000, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='invoice_generated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='is_investigator_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='locality',
            field=models.CharField(default=b'In Area', max_length=15),
        ),
        migrations.AddField(
            model_name='case',
            name='no_of_miles_travelled',
            field=models.FloatField(default=0.0),
        ),
    ]
