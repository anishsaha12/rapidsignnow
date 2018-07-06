# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0015_lawfirm_payment_plan'),
        ('case', '0043_auto_20180625_0515'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference_id', models.CharField(max_length=10, blank=True)),
                ('transaction_id', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('refund_amount', models.CharField(max_length=20)),
                ('refund_discription', models.CharField(max_length=250, null=True, blank=True)),
                ('case', models.ForeignKey(to='case.Case')),
                ('law_firm', models.ForeignKey(to='law_firm.LawFirm')),
            ],
        ),
    ]
