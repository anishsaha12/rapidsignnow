# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_address_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='gmaps_link',
            field=models.URLField(null=True, blank=True),
        ),
    ]
