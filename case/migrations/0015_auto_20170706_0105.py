# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0014_remove_case_bonus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='total_pages_in_attachment',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
