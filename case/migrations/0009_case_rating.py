# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0008_auto_20170607_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='rating',
            field=models.IntegerField(default=1),
        ),
    ]
