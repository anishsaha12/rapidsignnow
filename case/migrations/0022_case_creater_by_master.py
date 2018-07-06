# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_broker', '__first__'),
        ('case', '0021_auto_20170831_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='creater_by_master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='master_broker.MasterBroker', null=True),
        ),
    ]
