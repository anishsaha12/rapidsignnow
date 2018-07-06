# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0045_case_amount_billed_to_law_firm_override'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='refund_settlement',
            field=models.CharField(default=b'', max_length=30, null=True, blank=True),
        ),
    ]
