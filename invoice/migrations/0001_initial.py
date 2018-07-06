# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('basic_fee', models.FloatField(null=True, blank=True)),
                ('travel_expenses', models.FloatField(null=True, blank=True)),
                ('signature_fee', models.FloatField(null=True, blank=True)),
                ('investigator_expenses', models.FloatField(null=True, blank=True)),
                ('total_price', models.FloatField(null=True, blank=True)),
            ],
        ),
    ]
