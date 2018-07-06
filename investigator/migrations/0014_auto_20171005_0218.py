# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

def forwards(apps, schema_editor):

    Investigator = apps.get_model('investigator', 'Investigator')
    User = apps.get_registered_model('auth','User')
    Group = apps.get_model("auth", "Group")
    my_group, created = Group.objects.get_or_create(name='Investigator')
    content_type = ContentType.objects.get(app_label='investigator', model='Investigator')
    permission = Permission.objects.create(codename='can_view_investigator',
                                       name='Can View Investigator',
                                       content_type=content_type)
    my_group.permissions.add(permission.id)
    for investigator in  Investigator.objects.all():
        user = User.objects.get(username = investigator.user.username)
        user.groups.add(my_group)
        user.save()
        investigator.user = user
        investigator.save()

        


def backwards(apps, schema_editor):
    pass
class Migration(migrations.Migration):

    dependencies = [
        ('investigator', '0013_auto_20170911_0930'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
    ]
