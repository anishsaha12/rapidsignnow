# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0007_auto_20170604_2135'),
        ('investigator', '0006_auto_20170604_2135'),
        ('status_update', '0004_statusupdate_extra_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseAcceptanceUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_accepted', models.BooleanField(default=True)),
                ('read_by_broker', models.BooleanField(default=True)),
                ('case', models.ForeignKey(to='case.Case')),
                ('investigator', models.ForeignKey(to='investigator.Investigator')),
            ],
        ),
    ]
