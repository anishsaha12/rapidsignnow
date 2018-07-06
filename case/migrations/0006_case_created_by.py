# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0002_auto_20170530_0923'),
        ('case', '0005_auto_20170531_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='created_by',
            field=models.ForeignKey(default=1, to='broker.Broker'),
            preserve_default=False,
        ),
    ]
