# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0018_auto_20170813_1330'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='number_of_signatures_required',
        ),
    ]
