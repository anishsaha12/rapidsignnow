# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0015_lawfirm_payment_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawfirm',
            name='invoice_recipients',
            field=models.CharField(default=b'', max_length=500, null=True, blank=True),
        ),
    ]
