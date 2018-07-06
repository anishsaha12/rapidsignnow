from django.db import models
from law_firm.models import LawFirm
from django.utils import timezone

class Transaction(models.Model):

    law_firm = models.ForeignKey(LawFirm)
    reference_id = models.CharField(max_length=10,blank=True)
    transaction_id = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    transaction_status = models.CharField(max_length=50,blank=True)
    amount_charged = models.CharField(max_length=20)
    cases = models.CharField(max_length=20,default="")

    def __str__(self):
        return '%s' % (self.law_firm.name)
    
    
    