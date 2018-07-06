from django.db import models
from law_firm.models import LawFirm
from django.utils import timezone

class FailedTransaction(models.Model):

    law_firm = models.ForeignKey(LawFirm)
    reference_id = models.CharField(max_length=10)
    transaction_id = models.CharField(max_length=20,blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    transaction_status = models.CharField(max_length=50)
    amount_charged = models.CharField(max_length=20)
    cases = models.CharField(max_length=20,default="")
    does_transaction_exist = models.BooleanField(default=False)
    error_code = models.CharField(max_length=15,blank=True)
    error_text = models.CharField(max_length=200,blank=True)

    def __str__(self):
        return '%s' % (self.law_firm.name)
    
    
    