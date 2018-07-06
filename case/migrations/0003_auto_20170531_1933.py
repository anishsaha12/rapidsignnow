# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
        ('case', '0002_auto_20170530_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='bonus',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='client_address',
            field=models.ForeignKey(default=1, to='address.Address'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='client_home_phone',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='client_language',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='client_mobile_phone',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='client_name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='client_primary_email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='client_secondary_email',
            field=models.EmailField(default='', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='expected_payment',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='case',
            name='name',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
    ]
