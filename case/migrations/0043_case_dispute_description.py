# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0043_auto_20180625_0515'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='dispute_description',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
