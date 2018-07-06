# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('law_firm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investigator', '0001_initial'),
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Broker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number_one', models.CharField(max_length=20)),
                ('phone_number_two', models.CharField(max_length=20)),
                ('phone_number_three', models.CharField(max_length=20)),
                ('email_one', models.EmailField(max_length=254)),
                ('email_two', models.EmailField(max_length=254)),
                ('more_info', models.TextField()),
                ('rating', models.IntegerField(default=0)),
                ('photograph', models.ImageField(null=True, upload_to=b'/broker-photos/', blank=True)),
                ('active', models.BooleanField(default=True)),
                ('address', models.ForeignKey(to='address.Address')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BrokerInvestigatorLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('broker', models.ForeignKey(to='broker.Broker')),
                ('investigator', models.ForeignKey(to='investigator.Investigator')),
                ('investigator_rates', models.ForeignKey(to='investigator.InvestigatorRates')),
            ],
        ),
        migrations.CreateModel(
            name='BrokerLawFirmLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('broker', models.ForeignKey(to='broker.Broker')),
                ('law_firm', models.ForeignKey(to='law_firm.LawFirm')),
                ('law_firm_rates', models.ForeignKey(to='law_firm.LawFirmRates')),
            ],
        ),
    ]
