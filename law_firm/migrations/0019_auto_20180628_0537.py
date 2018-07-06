# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import models, migrations

def forwards(apps, schema_editor):

    LawFirm = apps.get_model('law_firm', 'LawFirm')
    for law_firm in  LawFirm.objects.all():
        law_firm.payment_plan = 'daily'
        law_firm.save()


def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0018_auto_20180628_0533'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
    ]
