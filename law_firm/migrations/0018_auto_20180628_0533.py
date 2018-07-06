# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0017_auto_20180628_0009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawfirm',
            name='payment_plan',
            field=models.CharField(default=b'dialy', max_length=20),
        ),
    ]
