# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='transaction',
            name='reference_id',
            field=models.CharField(max_length=10, blank=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_status',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
