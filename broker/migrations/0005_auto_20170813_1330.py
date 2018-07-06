# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0004_remove_broker_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='broker',
            old_name='active',
            new_name='is_active',
        ),
        migrations.AddField(
            model_name='broker',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 30, 873740, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='broker',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 32, 931743, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
