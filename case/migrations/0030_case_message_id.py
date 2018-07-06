# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0029_case_is_attention_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='message_id',
            field=models.IntegerField(default=1, max_length=10),
        ),
    ]
