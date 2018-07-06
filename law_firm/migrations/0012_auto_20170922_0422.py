# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import models, migrations
# from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def forwards(apps, schema_editor):

    LawFirm = apps.get_model('law_firm', 'LawFirm')
    User = apps.get_registered_model('auth','User')
    for law_firm in  LawFirm.objects.all():
        username = law_firm.email_one
        password = 'law_firm@123'
        user = User(username=username, password=make_password(password), email=username)
        user.save()
        law_firm.user = user
        # law_firm.user = authenticate(username=username, password=password)
        law_firm.save()


def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0011_lawfirm_user'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
    ]
