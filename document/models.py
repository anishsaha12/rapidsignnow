from django.db import models
from address.models import Address
from law_firm.models import LawFirm




class Document(models.Model):

    file_name = models.CharField(max_length=50)
    file = models.FileField()
    file_url = models.CharField(blank=True, null=True, max_length=300)
    law_firm = models.ForeignKey(LawFirm,blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now=True)
    version = models.FloatField(default=1.0)

    def __str__(self):
        return '%s' % (self.file_name)
    
    
    