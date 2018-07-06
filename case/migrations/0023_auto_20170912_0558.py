# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0022_case_creater_by_master'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='creater_by_master',
            new_name='created_by_master',
        ),
    ]
