# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0036_auto_20180328_2349'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='is_marked_for_payment',
            field=models.BooleanField(default=False),
        ),
    ]
