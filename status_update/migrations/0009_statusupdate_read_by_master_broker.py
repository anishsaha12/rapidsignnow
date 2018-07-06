# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0008_auto_20170813_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='statusupdate',
            name='read_by_master_broker',
            field=models.BooleanField(default=True),
        ),
    ]
