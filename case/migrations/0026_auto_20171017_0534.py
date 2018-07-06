# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0025_auto_20171013_0156'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='is_invoice_as_csv_mailed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='is_invoice_mailed',
            field=models.BooleanField(default=False),
        ),
    ]
