# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0041_case_reference_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='is_dispute_raised',
            field=models.BooleanField(default=False),
        ),
    ]
