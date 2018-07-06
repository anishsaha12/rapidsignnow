# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0004_case_creation_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='clients',
            field=models.ManyToManyField(to='client.Client', blank=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='documents',
            field=models.FileField(null=True, upload_to=b'/case-files/', blank=True),
        ),
    ]
