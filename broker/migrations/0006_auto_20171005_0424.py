# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

def forwards(apps, schema_editor):

    Broker = apps.get_model('broker', 'Broker')
    User = apps.get_registered_model('auth','User')
    Group = apps.get_model("auth", "Group")
    my_group, created = Group.objects.get_or_create(name='Broker')
    content_type = ContentType.objects.get(app_label='broker', model='Broker')
    permission = Permission.objects.create(codename='can_view_broker',
                                       name='Can View Broker',
                                       content_type=content_type)
    my_group.permissions.add(permission.id)
    for broker in  Broker.objects.all():
        user = User.objects.get(username = broker.user.username)
        user.groups.add(my_group)
        user.save()
        broker.user = user
        broker.save()

        


def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0005_auto_20170813_1330'),
    ]

    operations = [
        migrations.RunPython(forwards,backwards),
    ]
