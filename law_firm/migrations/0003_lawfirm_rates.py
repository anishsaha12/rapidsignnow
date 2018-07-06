# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0002_remove_lawfirm_rates'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawfirm',
            name='rates',
            field=models.ForeignKey(blank=True, to='law_firm.LawFirmRates', null=True),
        ),
    ]
