# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
        ('investigator', '0001_initial'),
        ('law_firm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=20)),
                ('number_of_signatures_required', models.IntegerField()),
                ('total_pages_in_attachment', models.IntegerField()),
                ('documents', models.FileField(upload_to=b'/case-files/')),
                ('status', models.CharField(max_length=20)),
                ('clients', models.ManyToManyField(to='client.Client')),
                ('investigator', models.ForeignKey(blank=True, to='investigator.Investigator', null=True)),
                ('law_firm', models.ForeignKey(to='law_firm.LawFirm')),
            ],
        ),
    ]
