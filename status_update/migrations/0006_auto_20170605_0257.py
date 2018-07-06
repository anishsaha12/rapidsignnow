# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status_update', '0005_caseacceptanceupdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statusupdate',
            name='extra_info',
            field=models.TextField(null=True, blank=True),
        ),
    ]
