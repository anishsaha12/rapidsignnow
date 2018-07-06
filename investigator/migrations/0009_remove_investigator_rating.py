# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0008_auto_20170607_1733'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investigator',
            name='rating',
        ),
    ]
