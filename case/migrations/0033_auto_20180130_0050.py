# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0032_auto_20180115_0242'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='rsn_extra_expenses',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='case',
            name='rsn_extra_expenses_description',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]
