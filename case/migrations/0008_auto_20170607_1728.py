# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0007_auto_20170604_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='client_home_phone',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='client_secondary_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
