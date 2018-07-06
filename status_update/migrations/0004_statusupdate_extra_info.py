# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0003_auto_20170604_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='statusupdate',
            name='extra_info',
            field=models.TextField(default=b''),
        ),
    ]
