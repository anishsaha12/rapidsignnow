from django.db import models
from law_firm.models import LawFirm
from case.models import Case
from django.utils import timezone

class Refund(models.Model):

    law_firm = models.ForeignKey(LawFirm)
    reference_id = models.CharField(max_length=10,blank=True)
    transaction_id = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    refund_amount = models.CharField(max_length=20)
    refund_discription = models.CharField(max_length=250,blank=True,null=True)
    case = models.ForeignKey(Case)

    def __str__(self):
        return '%s' % (self.law_firm.name)