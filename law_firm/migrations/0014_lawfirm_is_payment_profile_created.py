# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0013_auto_20171005_0526'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawfirm',
            name='is_payment_profile_created',
            field=models.BooleanField(default=False),
        ),
    ]
