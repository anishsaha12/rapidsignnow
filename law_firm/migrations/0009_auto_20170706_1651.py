# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0008_auto_20170706_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawfirmrates',
            name='default_in_area_payment_for_one_signature',
            field=models.FloatField(default='3'),
        ),
    ]
