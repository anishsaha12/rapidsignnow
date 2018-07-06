# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0002_remove_investigator_rates'),
    ]

    operations = [
        migrations.AddField(
            model_name='investigator',
            name='rates',
            field=models.ForeignKey(blank=True, to='investigator.InvestigatorRates', null=True),
        ),
    ]
