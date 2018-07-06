# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0038_auto_20180507_2342'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='is_document_received',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='case',
            name='is_document_sent',
            field=models.BooleanField(default=False),
        ),
    ]
