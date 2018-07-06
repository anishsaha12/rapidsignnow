# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0001_initial'),
        ('case', '0028_case_invoice_as_excel'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachedDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('case', models.ForeignKey(to='case.Case')),
                ('document', models.ForeignKey(to='document.Document')),
            ],
        ),
    ]
