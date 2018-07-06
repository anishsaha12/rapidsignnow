# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('mobile', models.CharField(max_length=20)),
                ('home_phone', models.CharField(max_length=20)),
                ('email_one', models.EmailField(max_length=254)),
                ('email_two', models.EmailField(max_length=254)),
                ('language', models.CharField(max_length=30)),
                ('address', models.ForeignKey(to='address.Address')),
            ],
        ),
    ]
