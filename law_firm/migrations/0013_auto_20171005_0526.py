# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

def forwards(apps, schema_editor):

    LawFirm = apps.get_model('law_firm', 'LawFirm')
    User = apps.get_registered_model('auth','User')
    Group = apps.get_model("auth", "Group")
    my_group, created = Group.objects.get_or_create(name='LawFirm')
    content_type = ContentType.objects.get(app_label='law_firm', model='LawFirm')
    permission = Permission.objects.create(codename='can_view_law_firm',
                                       name='Can View Law Firm',
                                       content_type=content_type)
    my_group.permissions.add(permission.id)
    for law_firm in  LawFirm.objects.all():
        user = User.objects.get(username = law_firm.user.username)
        user.groups.add(my_group)
        user.save()
        law_firm.user = user
        law_firm.save()

        


def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0012_auto_20170922_0422'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
    ]
