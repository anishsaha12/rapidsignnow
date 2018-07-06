# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0003_auto_20170607_1728'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='broker',
            name='rating',
        ),
    ]
