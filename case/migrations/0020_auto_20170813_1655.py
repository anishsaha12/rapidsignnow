# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards(apps, schema_editor):
    Case = apps.get_model('case', 'Case')
    for case in  Case.objects.all():
        case.type = 'default'
        case.save()
    
def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('case', '0019_remove_case_number_of_signatures_required'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
        
    ]
