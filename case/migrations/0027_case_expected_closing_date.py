# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0026_auto_20171017_0534'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='expected_closing_date',
            field=models.DateTimeField(null=True),
        ),
    ]
