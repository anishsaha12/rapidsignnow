# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0011_auto_20170913_0539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caseacceptanceupdate',
            name='updated_by',
            field=models.CharField(default=b'', max_length=2),
        ),
    ]
