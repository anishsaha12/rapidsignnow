# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0031_auto_20180115_0240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='message_id',
            field=models.IntegerField(default=0),
        ),
    ]
