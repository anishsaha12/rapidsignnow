# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0019_auto_20180628_0537'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawfirm',
            name='is_customer_profile_created',
            field=models.BooleanField(default=False),
        ),
    ]
