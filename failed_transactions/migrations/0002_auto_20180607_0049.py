# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('failed_transactions', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='failedtransaction',
            old_name='is_transaction_successful',
            new_name='does_transaction_exist',
        ),
        migrations.AddField(
            model_name='failedtransaction',
            name='error_code',
            field=models.CharField(max_length=15, blank=True),
        ),
        migrations.AddField(
            model_name='failedtransaction',
            name='error_text',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
