# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0023_auto_20170912_0558'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='status_mail',
            field=models.BooleanField(default=False),
        ),
    ]
