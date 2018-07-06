# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0004_auto_20170530_0943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lawfirm',
            name='phone_number_three',
        ),
        migrations.AlterField(
            model_name='lawfirm',
            name='email_two',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='lawfirm',
            name='number_of_free_miles',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='lawfirm',
            name='phone_number_two',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
