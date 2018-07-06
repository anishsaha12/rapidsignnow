# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

def forwards(apps, schema_editor):

    SystemAdmin = apps.get_model('system_admin', 'SystemAdmin')
    User = apps.get_registered_model('auth','User')
    Group = apps.get_model("auth", "Group")
    my_group, created = Group.objects.get_or_create(name='SystemAdmin')
    content_type = ContentType.objects.get(app_label='system_admin', model='SystemAdmin')
    permission = Permission.objects.create(codename='can_view_system_admin',
                                       name='Can View System Admin',
                                       content_type=content_type)
    my_group.permissions.add(permission.id)
    for system_admin in  SystemAdmin.objects.all():
        user = User.objects.get(username = system_admin.user.username)
        user.groups.add(my_group)
        user.save()
        system_admin.user = user
        system_admin.save()

        


def backwards(apps, schema_editor):
    pass
class Migration(migrations.Migration):

    dependencies = [
        ('system_admin', '0002_auto_20170813_1330'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
    ]
