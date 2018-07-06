from django.db import models
from document.models import Document
from case.models import Case





class AttachedDocument(models.Model):

    case = models.ForeignKey(Case)
    document = models.ForeignKey(Document)
    created_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return '%s' % (self.case.name)
    
    
    