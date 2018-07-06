from django.db import models
from invoice.models import Invoice
from case.models import Case
from address.models import Address
from law_firm.models import LawFirm

# Create your models here.
class InvoiceLine(models.Model):

    #New in InvoiceLine

    #fk references
    case = models.ForeignKey(Case, on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    case_created_at = models.DateTimeField()
    #decide case calculations business logic based on this
    is_signature_obtained = models.BooleanField(default=False)
    did_investigator_travel = models.BooleanField(default=False)


    #snapshot fields from case

    number_of_adult_signatures_required = models.IntegerField(default=0)
    number_of_child_signatures_required = models.IntegerField(default=0)

    number_of_adult_signatures_obtained = models.IntegerField(default=0)
    number_of_child_signatures_obtained = models.IntegerField(default=0)

    case_name = models.CharField(max_length=300)    
    investigator_name = models.CharField(max_length=50)
    case_type = models.CharField(max_length=20,default='')
    case_type_description = models.CharField(max_length=200,default='')

    client_name = models.CharField(max_length=50)
    client_address = models.CharField(max_length = 300,default='')
    
    dol = models.DateTimeField(default='2017-01-01 00:00:00.000000')
    case_closing_date = models.DateTimeField()
    date_of_signup = models.DateTimeField(blank=True, null=True)

    is_dol_provided = models.BooleanField(default=False)

    locality = models.CharField(max_length=15, default='In Area')

    adult_clients = models.CharField(default="", max_length=500)
    child_clients = models.CharField(default="", max_length=500)

    basic_fee_law_firm = models.FloatField()
    no_of_free_miles_law_firm = models.FloatField()
    mileage_rate_law_firm = models.FloatField()

    additional_expenses = models.FloatField(default=0.0)
    additional_expenses_description = models.CharField(default="", max_length=500)
    rsn_extra_expenses = models.FloatField(default=0.0)
    rsn_extra_expenses_description = models.CharField(default="", max_length=500)
    no_of_miles_travelled = models.FloatField(default=0.0)
    cancelled_by = models.CharField(default="", max_length=500)
    cancelled_reason_description = models.CharField(default="", max_length=500)
    
    minimum_payment_to_broker = models.FloatField(default=0.0)
    minimum_payment_from_lawfirm = models.FloatField(default=0.0)
    is_minimum_payment_made = models.BooleanField(default=False)

    # Calculated fields

    # Fees
    ## signature  to be mentioned on the invoice pdf
    total_signature_fee_for_adults = models.FloatField(default=0.0)
    total_signature_fee_for_children = models.FloatField(default=0.0)
    total_signature_fee = models.FloatField(default=0.0)

    ## Other fee
    travel_expenses = models.FloatField(default=0.0)
    additional_expenses = models.FloatField(default=0.0)

    total_amount_billed_to_law_firm = models.FloatField(default=0.0) #This should actually be amount_billed_to_law_firm

    
    #meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def get_total_amount_billed_to_law_firm(self):

        #This returns the total amount to be billed to the law firm

        if self.total_amount_billed_to_law_firm > 0:
            return  self.total_amount_billed_to_law_firm 
        if self.did_investigator_travel :
            if self.is_signature_obtained :
                # proceed with normal calculations

                total_amount_billed_to_law_firm = (  self.total_signature_fee_for_adults 
                                                        + self.total_signature_fee_for_children 
                                                        + self.travel_expenses 
                                                        + self.additional_expenses
                                                        + self.rsn_extra_expenses)
                                                    
                return total_amount_billed_to_law_firm
            else:
                # bill them basic fee

                total_amount_billed_to_law_firm = (  self.basic_fee_law_firm
                                                        + self.travel_expenses 
                                                        + self.additional_expenses
                                                        + self.rsn_extra_expenses)
                                                    
                return total_amount_billed_to_law_firm

        else :
            # Make total fee as $0

            return 0
