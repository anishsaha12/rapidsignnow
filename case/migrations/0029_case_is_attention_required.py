# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0028_case_invoice_as_excel'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='is_attention_required',
            field=models.BooleanField(default=False),
        ),
    ]
