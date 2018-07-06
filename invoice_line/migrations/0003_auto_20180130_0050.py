# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice_line', '0002_auto_20170831_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceline',
            name='rsn_extra_expenses',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='invoiceline',
            name='rsn_extra_expenses_description',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]
