# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_auto_20170813_1330'),
        ('case', '0024_case_status_mail'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='invoice_as_csv',
            field=models.ForeignKey(related_name='Invoce_as_csv', blank=True, to='invoice.Invoice', null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='invoice',
            field=models.ForeignKey(related_name='Invoce_as_pdf', blank=True, to='invoice.Invoice', null=True),
        ),
    ]
