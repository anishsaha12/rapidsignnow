# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0009_statusupdate_read_by_master_broker'),
    ]

    operations = [
        migrations.AddField(
            model_name='caseacceptanceupdate',
            name='read_by_master_broker',
            field=models.BooleanField(default=True),
        ),
    ]
