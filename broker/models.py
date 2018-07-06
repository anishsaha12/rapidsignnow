from django.db import models
from django.contrib.auth.models import User
from address.models import Address
from law_firm.models import LawFirm, LawFirmRates
from investigator.models import Investigator, InvestigatorRates
from constance import config


class Broker(models.Model):
    user = models.OneToOneField(User)
    phone_number_one = models.CharField(max_length=20)
    phone_number_two = models.CharField(max_length=20, blank=True, null=True)

    email_one = models.EmailField()
    email_two = models.EmailField(blank=True, null=True)

    address = models.ForeignKey(Address)
    more_info = models.TextField()

    photograph = models.ImageField(blank=True, null=True, upload_to='broker-photos/')

    is_active = models.BooleanField(default=True)

    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BrokerLawFirmLink(models.Model):
    broker = models.ForeignKey(Broker)
    law_firm = models.ForeignKey(LawFirm)
    law_firm_rates = models.ForeignKey(LawFirmRates)


class BrokerInvestigatorLink(models.Model):
    broker = models.ForeignKey(Broker)
    investigator = models.ForeignKey(Investigator)
    investigator_rates = models.ForeignKey(InvestigatorRates)
