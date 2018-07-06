# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0002_auto_20170530_0923'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='broker',
            name='phone_number_three',
        ),
        migrations.AlterField(
            model_name='broker',
            name='email_two',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='broker',
            name='phone_number_two',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
