# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0006_case_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='documents',
            field=models.FileField(null=True, upload_to=b'case-files/', blank=True),
        ),
    ]
