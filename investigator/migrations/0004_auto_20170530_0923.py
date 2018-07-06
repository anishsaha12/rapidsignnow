# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0003_investigator_rates'),
    ]

    operations = [
        migrations.AddField(
            model_name='investigator',
            name='more_info',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='investigator',
            name='photograph',
            field=models.ImageField(null=True, upload_to=b'investigator-photos', blank=True),
        ),
    ]
