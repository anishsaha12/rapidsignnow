# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0009_case_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='number_of_additional_adult_clients',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='case',
            name='number_of_additional_child_clients',
            field=models.IntegerField(default=0),
        ),
    ]
