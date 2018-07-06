# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Investigator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nickname', models.CharField(max_length=50)),
                ('language', models.CharField(max_length=30)),
                ('phone_number_one', models.CharField(max_length=20)),
                ('phone_number_two', models.CharField(max_length=20)),
                ('phone_number_three', models.CharField(max_length=20)),
                ('email_one', models.EmailField(max_length=254)),
                ('email_two', models.EmailField(max_length=254)),
                ('rating', models.IntegerField(default=0)),
                ('photograph', models.ImageField(null=True, upload_to=b'/investigator-photos', blank=True)),
                ('active', models.BooleanField(default=True)),
                ('address', models.ForeignKey(to='address.Address')),
            ],
        ),
        migrations.CreateModel(
            name='InvestigatorRates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('default_in_area_payment_for_one_signature', models.FloatField(default=0.0)),
                ('default_in_area_payment_for_each_additional_adult_signature', models.FloatField(default=0.0)),
                ('default_in_area_payment_for_children', models.FloatField(default=0.0)),
                ('maximum_in_area_payment_for_any_number_of_signatures', models.FloatField(default=0.0)),
                ('default_out_of_area_payment_for_one_signature', models.FloatField(default=0.0)),
                ('default_out_of_area_payment_for_each_additional_adult_signature', models.FloatField(default=0.0)),
                ('default_out_of_area_payment_for_children', models.FloatField(default=0.0)),
                ('maximum_out_of_area_payment_for_any_number_of_signatures', models.FloatField(default=0.0)),
            ],
        ),
        migrations.AddField(
            model_name='investigator',
            name='rates',
            field=models.ForeignKey(blank=True, to='investigator.InvestigatorRates', null=True),
        ),
        migrations.AddField(
            model_name='investigator',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
