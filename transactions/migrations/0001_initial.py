# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0015_lawfirm_payment_plan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_id', models.CharField(max_length=20)),
                ('amount_charged', models.CharField(max_length=20)),
                ('cases', models.CharField(default=b'', max_length=20)),
                ('law_firm', models.ForeignKey(to='law_firm.LawFirm')),
            ],
        ),
    ]
