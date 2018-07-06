# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 37, 462437, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 39, 131602, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
