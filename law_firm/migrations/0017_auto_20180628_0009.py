# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0016_lawfirm_invoice_recipients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawfirm',
            name='payment_plan',
            field=models.CharField(default=b'daily', max_length=20),
        ),
    ]
