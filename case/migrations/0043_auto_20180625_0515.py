# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0042_case_is_dispute_raised'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='amount_refunded',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='case',
            name='refund_settlement',
            field=models.CharField(default=None, max_length=30),
        ),
    ]
