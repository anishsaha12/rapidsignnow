# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0007_auto_20170607_1728'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investigator',
            name='language',
        ),
        migrations.RemoveField(
            model_name='investigator',
            name='secondary_language',
        ),
        migrations.RemoveField(
            model_name='investigator',
            name='tertiary_language',
        ),
        migrations.AddField(
            model_name='investigator',
            name='languages',
            field=models.CharField(default=b'["English"]', max_length=150),
        ),
    ]
