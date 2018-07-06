# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0015_lawfirm_payment_plan'),
    ]

    operations = [
        migrations.CreateModel(
            name='FailedTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_id', models.CharField(max_length=10)),
                ('transaction_id', models.CharField(max_length=20, blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('transaction_status', models.CharField(max_length=50)),
                ('amount_charged', models.CharField(max_length=20)),
                ('cases', models.CharField(default=b'', max_length=20)),
                ('is_transaction_successful', models.BooleanField(default=False)),
                ('law_firm', models.ForeignKey(to='law_firm.LawFirm')),
            ],
        ),
    ]
