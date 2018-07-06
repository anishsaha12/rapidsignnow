from django.db import models
from address.models import Address
from constance import config
from django.contrib.auth.models import User

class LawFirmRates(models.Model):
    default_in_area_payment_for_one_signature = models.FloatField(
        default=config.DEFAULT_IN_AREA_PAYMENT_FOR_ONE_SIGNATURE_LAW_FIRM)
    default_in_area_payment_for_each_additional_adult_signature = models.FloatField(
        default=config.DEFAULT_IN_AREA_PAYMENT_FOR_EACH_ADDITIONAL_ADULT_SIGNATURE_LAW_FIRM)
    default_in_area_payment_for_children = models.FloatField(
        default=config.DEFAULT_IN_AREA_PAYMENT_FOR_CHILDREN_LAW_FIRM)
    maximum_in_area_payment_for_any_number_of_signatures = models.FloatField(
        default=config.MAXIMUM_IN_AREA_PAYMENT_FOR_ANY_NUMBER_OF_SIGNATURES_LAW_FIRM)
    default_in_area_payment_when_signature_not_obtained = models.FloatField(
        default=config.DEFAULT_IN_AREA_PAYMENT_WHEN_SIGNATURE_NOT_OBTAINED_LAW_FIRM)

    default_out_of_area_payment_for_one_signature = models.FloatField(
        default=config.DEFAULT_OUT_OF_AREA_PAYMENT_FOR_ONE_SIGNATURE_LAW_FIRM)
    default_out_of_area_payment_for_each_additional_adult_signature = models.FloatField(
        default=config.DEFAULT_OUT_OF_AREA_PAYMENT_FOR_EACH_ADDITIONAL_ADULT_SIGNATURE_LAW_FIRM)
    default_out_of_area_payment_for_children = models.FloatField(
        default=config.DEFAULT_OUT_OF_AREA_PAYMENT_FOR_CHILDREN_LAW_FIRM)
    maximum_out_of_area_payment_for_any_number_of_signatures = models.FloatField(
        default=config.MAXIMUM_OUT_OF_AREA_PAYMENT_FOR_ANY_NUMBER_OF_SIGNATURES_LAW_FIRM)
    default_out_of_area_payment_when_signature_not_obtained = models.FloatField(
        default=config.DEFAULT_OUT_OF_AREA_PAYMENT_WHEN_SIGNATURE_NOT_OBTAINED_LAW_FIRM)

    mileage_compensation_rate = models.FloatField(default=config.MILEAGE_COMPENSATION_RATE_LAW_FIRM)
    mileage_threshold = models.FloatField(default=config.MILEAGE_THRESHOLD_LAW_FIRM)

    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LawFirm(models.Model):
    user = models.ForeignKey(User, null=True)
    name = models.CharField(max_length=200)

    phone_number_one = models.CharField(max_length=20)
    phone_number_two = models.CharField(max_length=20, blank=True, null=True)

    email_one = models.EmailField()
    email_two = models.EmailField(blank=True, null=True)

    address = models.ForeignKey(Address)

    is_active = models.BooleanField(default=True)
    rates = models.ForeignKey(LawFirmRates, blank=True, null=True)

    #Payment selected
    is_customer_profile_created = models.BooleanField(default=False)
    is_payment_profile_created = models.BooleanField(default=False)
    payment_plan =  models.CharField(default="dialy",max_length=20)
    invoice_recipients = models.CharField(max_length=500,default="",null=True,blank=True)
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_emails_as_array(self):
        emails = []
        if self.email_one:
            emails.append(self.email_one)
        if self.email_two:
            emails.append(self.email_two)
        return emails


    def __str__(self):
        return '%s' % (self.name)