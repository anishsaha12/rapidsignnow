# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_auto_20170813_1330'),
        ('case', '0027_case_expected_closing_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='invoice_as_excel',
            field=models.ForeignKey(related_name='Invoce_as_excel', blank=True, to='invoice.Invoice', null=True),
        ),
    ]
