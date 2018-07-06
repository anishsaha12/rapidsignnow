# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0006_auto_20170605_0257'),
    ]

    operations = [
        migrations.AddField(
            model_name='caseacceptanceupdate',
            name='updated_by',
            field=models.CharField(default=b'BR', max_length=2),
        ),
        migrations.AddField(
            model_name='statusupdate',
            name='read_by_investigator',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='statusupdate',
            name='updated_by',
            field=models.CharField(default=b'BR', max_length=2),
        ),
    ]
