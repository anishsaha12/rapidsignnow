# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0005_auto_20170530_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigator',
            name='photograph',
            field=models.ImageField(null=True, upload_to=b'investigator-photos/', blank=True),
        ),
    ]
