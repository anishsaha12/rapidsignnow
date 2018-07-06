# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0044_case_refund_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='amount_billed_to_law_firm_override',
            field=models.FloatField(default=0.0),
        ),
    ]
