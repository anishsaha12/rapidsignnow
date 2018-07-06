# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0030_case_message_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='message_id',
            field=models.IntegerField(default=1),
        ),
    ]
