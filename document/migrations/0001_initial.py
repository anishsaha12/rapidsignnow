# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0013_auto_20171005_0526'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_name', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to=b'')),
                ('file_url', models.CharField(max_length=300, null=True, blank=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('uploaded_at', models.DateTimeField(auto_now=True)),
                ('law_firm', models.ForeignKey(blank=True, to='law_firm.LawFirm', null=True)),
            ],
        ),
    ]
