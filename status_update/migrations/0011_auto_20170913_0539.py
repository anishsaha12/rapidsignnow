# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0010_caseacceptanceupdate_read_by_master_broker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusupdate',
            name='updated_by',
            field=models.CharField(default=b'', max_length=2),
        ),
    ]
