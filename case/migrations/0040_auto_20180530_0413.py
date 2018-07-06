# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0039_auto_20180513_2250'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='is_chargable',
            new_name='approved_by_rsn',
        ),
    ]
