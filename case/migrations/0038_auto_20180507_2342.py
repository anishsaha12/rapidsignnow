# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0037_case_is_marked_for_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='has_law_firm_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='is_chargable',
            field=models.BooleanField(default=False),
        ),
    ]
