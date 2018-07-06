from django.db import models
from address.models import Address


class Client(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    home_phone = models.CharField(max_length=20)

    email_one = models.EmailField()
    email_two = models.EmailField()

    language = models.CharField(max_length=30)
    address = models.ForeignKey(Address)

    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
