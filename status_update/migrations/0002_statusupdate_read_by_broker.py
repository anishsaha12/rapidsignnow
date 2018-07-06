# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='statusupdate',
            name='read_by_broker',
            field=models.BooleanField(default=True),
        ),
    ]
