from django.db import models
from django.contrib.auth.models import User

from investigator.models import Investigator
from case.models import Case


class StatusUpdate(models.Model):
    status = models.CharField(max_length=40)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    case = models.ForeignKey(Case)
    read_by_broker = models.BooleanField(default=True)
    read_by_master_broker = models.BooleanField(default=True)
    read_by_investigator = models.BooleanField(default=True)
    extra_info = models.TextField(blank=True, null=True)
    updated_by = models.CharField(max_length=2, default='')

    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CaseAcceptanceUpdate(models.Model):
    investigator = models.ForeignKey(Investigator)
    timestamp = models.DateTimeField(auto_now_add=True)
    case = models.ForeignKey(Case)
    is_accepted = models.BooleanField(default=True)
    read_by_broker = models.BooleanField(default=True)
    read_by_master_broker = models.BooleanField(default=True)
    updated_by = models.CharField(max_length=2, default='')

    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
