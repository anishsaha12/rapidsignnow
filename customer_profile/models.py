from django.db import models
from document.models import Document
from law_firm.models import LawFirm

class CustomerProfile(models.Model):

    law_firm = models.ForeignKey(LawFirm)
    auth_customer_profile_id = models.CharField(max_length = 20)

    # As per client request added Primary and Secondary payment methods
    primary_payment_profile_id = models.CharField(max_length=20,blank=True,null=True)
    primary_payment_method = models.CharField(max_length=20,blank=True,null=True)

    secondary_payment_profile_id = models.CharField(max_length=20,blank=True,null=True)
    secondary_payment_method = models.CharField(max_length=20,blank=True,null=True)


    def __str__(self):
        return '%s' % (self.law_firm.name)
    
    
    