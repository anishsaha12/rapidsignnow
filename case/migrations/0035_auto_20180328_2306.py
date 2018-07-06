# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0034_case_date_of_signup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='date_of_signup',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 29, 6, 6, 54, 942100, tzinfo=utc), null=True, blank=True),
        ),
    ]
