# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0002_statusupdate_read_by_broker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusupdate',
            name='status',
            field=models.CharField(max_length=30),
        ),
    ]
