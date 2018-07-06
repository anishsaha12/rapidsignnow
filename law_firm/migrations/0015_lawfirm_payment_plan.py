# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0014_lawfirm_is_payment_profile_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawfirm',
            name='payment_plan',
            field=models.CharField(default=b'', max_length=20),
        ),
    ]
