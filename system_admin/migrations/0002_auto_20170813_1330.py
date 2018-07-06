# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('system_admin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemadmin',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 30, 10, 74875, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='systemadmin',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='systemadmin',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 30, 11, 610047, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
