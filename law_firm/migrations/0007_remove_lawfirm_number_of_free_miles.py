# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0006_auto_20170705_2251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lawfirm',
            name='number_of_free_miles',
        ),
    ]
