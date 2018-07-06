from django.db import models
from address.models import Address
from law_firm.models import LawFirm


# class Invoice(models.Model):
#     basic_fee = models.FloatField(blank=True, null=True)
#     travel_expenses = models.FloatField(blank=True, null=True)
#     signature_fee = models.FloatField(blank=True, null=True)
#     investigator_expenses = models.FloatField(blank=True, null=True)
#     total_price = models.FloatField(blank=True, null=True)

class Invoice(models.Model):

    total_billed_amount = models.FloatField(default=0.0)

    is_deleted = models.BooleanField(default=False)
    
    # law_firm = models.ForeignKey(LawFirm)

    law_firm_name = models.CharField(max_length=300)
    law_firm_email = models.EmailField()
    law_firm_address = models.CharField(max_length=300)

    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
