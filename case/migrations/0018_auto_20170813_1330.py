# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards(apps, schema_editor):

    Case = apps.get_model('case', 'Case')
    for case in  Case.objects.all():
        number_of_signatures_required = case.number_of_signatures_required

        number_of_adult_signatures_required = 0 
        number_of_child_signatures_required = 0
        number_of_adult_signatures_obtained = 0
        number_of_child_signatures_obtained = 0

        if case.adult_clients is not None and len(str(case.adult_clients)) > 1:    
            number_of_adult_signatures_required = len(case.adult_clients.split(','))
        
        if case.child_clients is not None and len(str(case.child_clients)) > 1:
            number_of_child_signatures_required = len(case.child_clients.split(','))

        if number_of_signatures_required > (number_of_adult_signatures_required + number_of_child_signatures_required):
            number_of_adult_signatures_required = number_of_signatures_required - number_of_child_signatures_required
        
        
        if case.is_signature_obtained == True:
            number_of_adult_signatures_obtained = number_of_adult_signatures_required
            number_of_child_signatures_obtained = number_of_child_signatures_obtained

        case.number_of_adult_signatures_required = number_of_adult_signatures_required
        case.number_of_child_signatures_required = number_of_child_signatures_required
        case.number_of_adult_signatures_obtained = number_of_adult_signatures_obtained
        case.number_of_child_signatures_obtained = number_of_child_signatures_obtained

        case.is_dol_provided = True
        case.did_investigator_travel = True

        case.save()


def backwards(apps, schema_editor):
    Case = apps.get_model('case', 'Case')
    for case in  Case.objects.all():
        case.number_of_signatures_required = case.number_of_adult_signatures_required + case.number_of_child_signatures_required
        case.save()


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0017_auto_20170813_1330'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
    ]
