# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice_line', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceline',
            name='cancelled_by',
            field=models.CharField(default=b'', max_length=500),
        ),
        migrations.AddField(
            model_name='invoiceline',
            name='cancelled_reason_description',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]
