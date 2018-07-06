# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial'),
        ('case', '0015_auto_20170706_0105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='invoice_generated',
        ),
        migrations.AddField(
            model_name='case',
            name='invoice',
            field=models.ForeignKey(blank=True, to='invoice.Invoice', null=True),
        ),
    ]
