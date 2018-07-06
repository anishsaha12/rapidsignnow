from django.db import models
from django.contrib.auth.models import User
from address.models import Address
from constance import config
from datetime import timedelta
from django.utils import timezone
import ast


class InvestigatorRates(models.Model):
    default_in_area_payment_for_one_signature = models.FloatField(
        default=config.DEFAULT_IN_AREA_PAYMENT_FOR_ONE_SIGNATURE_INVESTIGATOR)
    default_in_area_payment_for_each_additional_adult_signature = models.FloatField(
        default=config.DEFAULT_IN_AREA_PAYMENT_FOR_EACH_ADDITIONAL_ADULT_SIGNATURE_INVESTIGATOR)
    default_in_area_payment_for_children = models.FloatField(
        default=config.DEFAULT_IN_AREA_PAYMENT_FOR_CHILDREN_INVESTIGATOR)
    maximum_in_area_payment_for_any_number_of_signatures = models.FloatField(
        default=config.MAXIMUM_IN_AREA_PAYMENT_FOR_ANY_NUMBER_OF_SIGNATURES_INVESTIGATOR)
    default_in_area_payment_when_signature_not_obtained = models.FloatField(
        default=config.DEFAULT_IN_AREA_PAYMENT_WHEN_SIGNATURE_NOT_OBTAINED_INVESTIGATOR)

    default_out_of_area_payment_for_one_signature = models.FloatField(
        default=config.DEFAULT_OUT_OF_AREA_PAYMENT_FOR_ONE_SIGNATURE_INVESTIGATOR)
    default_out_of_area_payment_for_each_additional_adult_signature = models.FloatField(
        default=config.DEFAULT_OUT_OF_AREA_PAYMENT_FOR_EACH_ADDITIONAL_ADULT_SIGNATURE_INVESTIGATOR)
    default_out_of_area_payment_for_children = models.FloatField(
        default=config.DEFAULT_OUT_OF_AREA_PAYMENT_FOR_CHILDREN_INVESTIGATOR)
    maximum_out_of_area_payment_for_any_number_of_signatures = models.FloatField(
        default=config.MAXIMUM_OUT_OF_AREA_PAYMENT_FOR_ANY_NUMBER_OF_SIGNATURES_INVESTIGATOR)
    default_out_of_area_payment_when_signature_not_obtained = models.FloatField(
        default=config.DEFAULT_OUT_OF_AREA_PAYMENT_WHEN_SIGNATURE_NOT_OBTAINED_INVESTIGATOR)

    mileage_compensation_rate = models.FloatField(default=config.MILEAGE_COMPENSATION_RATE_INVESTIGATOR)
    mileage_threshold = models.FloatField(default=config.MILEAGE_THRESHOLD_INVESTIGATOR)


class Investigator(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    languages = models.CharField(max_length=150, default="[\"English\"]")

    phone_number_one = models.CharField(max_length=20)
    phone_number_two = models.CharField(max_length=20, blank=True, null=True)

    email_one = models.EmailField()
    email_two = models.EmailField(blank=True, null=True)

    address = models.ForeignKey(Address, related_name='address')
    secondary_address = models.ForeignKey(Address, related_name='secondary_address', blank=True, null=True)
    more_info = models.TextField()

    photograph = models.ImageField(blank=True, null=True, upload_to='investigator-photos/')

    is_active = models.BooleanField(default=True)
    rates = models.ForeignKey(InvestigatorRates, blank=True, null=True)

    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return '%s' % (self.email_one)

    def cases_in_month(self):
        from case.models import Case
        from datetime import timedelta
        from django.utils import timezone

        return len(Case.objects.filter(investigator=self, status='Closed').filter(created_at__gt=(timezone.now() - timedelta(days=30))))

    def cases_in_lifetime(self):
        from case.models import Case

        return len(Case.objects.filter(investigator=self, status='Closed'))

    def rating(self):
        from case.models import Case

        ratings = []
        all_cases = Case.objects.filter(investigator=self, status='Closed')

        for case in all_cases:
            ratings.append(case.rating)
            
        if len(all_cases) == 0:
            return 0

        return sum(ratings)/len(ratings)

    def languages_array(self):
        try:
            return ast.literal_eval(self.languages)
        except:
            return "Unknown"