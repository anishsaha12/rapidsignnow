# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0011_auto_20170704_0853'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='random_string',
            field=models.CharField(default='000000000000000000000000000000', max_length=30),
            preserve_default=False,
        ),
    ]
