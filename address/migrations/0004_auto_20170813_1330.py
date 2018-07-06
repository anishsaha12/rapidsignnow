# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0003_address_gmaps_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 27, 153260, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 13, 13, 29, 29, 70786, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
