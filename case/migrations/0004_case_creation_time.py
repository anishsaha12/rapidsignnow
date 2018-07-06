# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0003_auto_20170531_1933'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 31, 14, 44, 59, 433000, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
