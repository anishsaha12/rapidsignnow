# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0033_auto_20180130_0050'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='date_of_signup',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
