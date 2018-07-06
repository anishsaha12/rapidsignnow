from django.db import models
from django.contrib.auth.models import User


class SystemAdmin(models.Model):
    user = models.OneToOneField(User)
    is_active = models.BooleanField(default=True)
    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
