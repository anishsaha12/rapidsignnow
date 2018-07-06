# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer_profile', '0004_auto_20180515_1110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customerprofile',
            old_name='payment_method',
            new_name='primary_payment_method',
        ),
        migrations.RenameField(
            model_name='customerprofile',
            old_name='payment_profile_id',
            new_name='primary_payment_profile_id',
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='secondary_payment_method',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='secondary_payment_profile_id',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
