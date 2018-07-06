# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broker',
            name='photograph',
            field=models.ImageField(null=True, upload_to=b'broker-photos/', blank=True),
        ),
    ]
