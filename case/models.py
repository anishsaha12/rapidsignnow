from django.db import models
from client.models import Client
from law_firm.models import LawFirm
from broker.models import Broker
from master_broker.models import MasterBroker
# from status_update.models import StatusUpdate
from address.models import Address
from investigator.models import Investigator
from invoice.models import Invoice
from django.contrib.auth import get_user_model
from django.utils import timezone

import itertools

def get_sentinel_user():
    # get_user_model().objects.
    return get_user_model().objects.get_or_create(username='deleted')[0]

class Case(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=300)
    law_firm = models.ForeignKey(LawFirm)

    investigator = models.ForeignKey(Investigator, blank=True, null=True ,on_delete=models.SET_NULL)

    # clients = models.ManyToManyField(Client, blank=True)
    type = models.CharField(max_length=20,default='default')
    type_description = models.CharField(max_length=200,default='')
    
    # number_of_signatures_required = models.IntegerField()
    number_of_adult_signatures_required = models.IntegerField(default=0, null=True)
    number_of_child_signatures_required = models.IntegerField(default=0, null=True)
    number_of_adult_signatures_obtained = models.IntegerField(default=0, null=True)
    number_of_child_signatures_obtained = models.IntegerField(default=0, null=True)

    total_pages_in_attachment = models.IntegerField(blank=True, null=True)
    documents = models.FileField(upload_to='case-files/', blank=True, null=True)
    rating = models.IntegerField(default=1)
    dol = models.DateTimeField(default='2017-01-01 00:00:00.000000')
    is_dol_provided = models.BooleanField(default=False)
    closing_date = models.DateTimeField(blank=True, null=True)
    date_of_signup = models.DateTimeField(blank=True, null=True)
    expected_closing_date = models.DateTimeField(null=True)
    locality = models.CharField(max_length=15, default='In Area')
    is_investigator_paid = models.BooleanField(default=False)
    has_law_firm_paid = models.BooleanField(default=False)
    is_invoice_mailed = models.BooleanField(default=False)
    is_invoice_as_csv_mailed = models.BooleanField(default=False)

    investigator_bonus_amount = models.FloatField(default=0.0)
    investigator_bonus_reason = models.CharField(default='Not Provided',max_length=200)
    pay_investigator_bonus = models.BooleanField(default=False)
    status_mail = models.BooleanField(default=False)
    
    # these two fields decide how to bill the case
    # if is_signature_obtained == True
    #     proceed with normal signature obtained calculations
    # elif did_investigator_travel == True
    #     bill the default fee + travel expenses
    # else:
    #     case was cancelled by client, don't bill

    is_signature_obtained = models.BooleanField(default=False)
    did_investigator_travel = models.BooleanField(default=False)

    random_string = models.CharField(max_length=30)
    
    invoice = models.ForeignKey(Invoice, blank=True, null=True, related_name="Invoce_as_pdf")
    invoice_as_csv = models.ForeignKey(Invoice, blank=True, null=True, related_name="Invoce_as_csv")
    invoice_as_excel = models.ForeignKey(Invoice, blank=True, null=True, related_name="Invoce_as_excel")
    
    adult_clients = models.CharField(default="", max_length=500)
    child_clients = models.CharField(default="", max_length=500)

    created_by = models.ForeignKey(Broker, blank=True, null=True ,on_delete=models.SET_NULL)
    created_by_master = models.ForeignKey(MasterBroker, blank=True, null=True, on_delete=models.SET_NULL)

    basic_fee_law_firm = models.FloatField()
    no_of_free_miles_law_firm = models.FloatField()
    mileage_rate_law_firm = models.FloatField()

    basic_fee_investigator = models.FloatField()
    no_of_free_miles_investigator = models.FloatField()
    mileage_rate_investigator = models.FloatField()

    additional_expenses = models.FloatField(default=0.0)
    additional_expenses_description = models.CharField(default="", max_length=500)
    rsn_extra_expenses = models.FloatField(default=0.0)
    rsn_extra_expenses_description = models.CharField(default="", max_length=500)
    cancelled_by = models.CharField(default="", max_length=500)
    cancelled_reason_description = models.CharField(default="", max_length=500)
    no_of_miles_travelled = models.FloatField(default=0.0)
    amount_billed_to_law_firm = models.FloatField(default=0.0) #This should actually be amount_billed_to_law_firm
    amount_billed_to_law_firm_override = models.FloatField(default=0.0)
    amount_paid_to_investigator = models.FloatField(default=0.0)

    expected_payment = models.FloatField(default=0.0)

    minimum_payment_to_broker = models.FloatField(default=0.0)
    minimum_payment_from_lawfirm = models.FloatField(default=0.0)
    is_minimum_payment_made = models.BooleanField(default=False)

    is_case_valid = models.BooleanField(default=True)
    is_attention_required = models.BooleanField(default=False)
    is_marked_for_payment = models.BooleanField(default=False)
    approved_by_rsn = models.BooleanField(default=False)
    is_document_sent = models.BooleanField(default=False)
    is_document_received = models.BooleanField(default=False)

    client_name = models.CharField(max_length=50)
    client_mobile_phone = models.CharField(max_length=20)
    client_home_phone = models.CharField(max_length=20, blank=True, null=True)
    client_primary_email = models.EmailField()
    client_secondary_email = models.EmailField(blank=True, null=True)
    client_language = models.CharField(max_length=30)
    client_address = models.ForeignKey(Address,blank=True, null=True)
    
    message_id = models.IntegerField(default=0)
    status = models.CharField(max_length=30)

    reference_id = models.CharField(max_length=10,blank=True)
    is_dispute_raised = models.BooleanField(default=False)
    dispute_description = models.CharField(max_length=200,blank=True,null=True)
    
    refund_settlement = models.CharField(default="",max_length=30,blank=True,null=True)
    amount_refunded = models.FloatField(default=0.0,)
    refund_description = models.CharField(max_length=200,blank=True,null=True)
    
    def additional_expenses_text(self):

        if(self.additional_expenses > 0):

            pass

        # Need to fix this
        from status_update.models import StatusUpdate

        signature_obtained = StatusUpdate.objects.filter(status='Signature obtained').filter(case=self).order_by('-timestamp')
        signature_not_obtained = StatusUpdate.objects.filter(status='Signature not obtained').filter(case=self).order_by('-timestamp')

        info_container = None

        if signature_obtained.exists():
            info_container = signature_obtained[0]
        elif signature_not_obtained.exists():
            info_container = signature_not_obtained[0]
        else:
            return ''

        info_dict = info_container.extra_info + ""
        info_dict = info_dict.replace("{", "").replace("}", "").replace("\"", "").replace("'", "")

        if "," in info_dict:
            info_dict = info_dict.split(",")
            for item in info_dict:
                if "Out of pocket expenses" in item:
                    return item.split(":")[1].encode('utf8')
        else:
            if "Out of pocket expenses" in info_dict:
                return info_dict.split(":")[1].encode('utf8')

        return ''

    def no_of_miles_text(self):
        from status_update.models import StatusUpdate

        signature_obtained = StatusUpdate.objects.filter(status='Signature obtained').filter(case=self).order_by('-timestamp')
        signature_not_obtained = StatusUpdate.objects.filter(status='Signature not obtained').filter(case=self).order_by('-timestamp')

        info_container = None

        if signature_obtained.exists():
            info_container = signature_obtained[0]
        elif signature_not_obtained.exists():
            info_container = signature_not_obtained[0]
        else:
            return ''

        info_dict = info_container.extra_info + ""
        info_dict = info_dict.replace("{", "").replace("}", "").replace("\"", "").replace("'", "")

        if "," in info_dict:
            info_dict = info_dict.split(",")
            for item in info_dict:
                if "Mileage Description" in item:
                    return item.split(":")[1].encode('utf8')
        else:
            if "Mileage Description" in info_dict:
                return info_dict.split(":")[1].encode('utf8')

        return ''

    def difference_in_payment(self):
        return self.get_investigator_price() - self.expected_payment

    def profit(self):
        return self.get_law_firm_price() - self.get_investigator_price()

    def distance_to_client(self):
        if self.investigator is None:
            return ''

        return self.client_address.get_driving_distance_from_address(self.investigator.address.get_coordinates())
   
    def get_investigator_price(self):

        if self.is_investigator_paid:
            return self.amount_paid_to_investigator

        basic_fee_investigator = self.basic_fee_investigator
        mileage_rate_investigator = self.mileage_rate_investigator
        no_of_free_miles_investigator = self.no_of_free_miles_investigator
        no_of_miles_travelled = self.no_of_miles_travelled
        additional_expenses = self.additional_expenses

        number_of_adult_signatures_obtained = self.number_of_adult_signatures_obtained
        number_of_child_signatures_obtained = self.number_of_child_signatures_obtained

        travel_expenses = 0

        amount_paid_to_investigator = 0

        is_signature_obtained = False
        did_investigator_travel = False

        if no_of_miles_travelled > no_of_free_miles_investigator:
            travel_expenses = ((no_of_miles_travelled - no_of_free_miles_investigator) * mileage_rate_investigator)

        signature_prices = 0
        if self.investigator:
            investigator_rates = self.investigator.rates
            default_in_area_payment_for_one_signature = investigator_rates.default_in_area_payment_for_one_signature
            default_in_area_payment_for_each_additional_adult_signature = investigator_rates.default_in_area_payment_for_each_additional_adult_signature
            default_in_area_payment_for_children = investigator_rates.default_in_area_payment_for_children
            maximum_in_area_payment_for_any_number_of_signatures = investigator_rates.maximum_in_area_payment_for_any_number_of_signatures

            default_out_of_area_payment_for_one_signature = investigator_rates.default_out_of_area_payment_for_one_signature
            default_out_of_area_payment_for_each_additional_adult_signature = investigator_rates.default_out_of_area_payment_for_each_additional_adult_signature
            default_out_of_area_payment_for_children = investigator_rates.default_out_of_area_payment_for_children
            maximum_out_of_area_payment_for_any_number_of_signatures = investigator_rates.maximum_out_of_area_payment_for_any_number_of_signatures

              
            if self.is_signature_obtained:

                number_of_billed_adults = 0
                number_of_billed_children = 0
                total_signature_fee = 0
                total_signature_fee_for_adults = 0
                total_signature_fee_for_children = 0

                if no_of_miles_travelled > no_of_free_miles_investigator and int(no_of_miles_travelled) != 0:
                    travel_expenses = ((no_of_miles_travelled - no_of_free_miles_investigator) * mileage_rate_investigator)
                    print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_investigator),float(no_of_miles_travelled), float(mileage_rate_investigator),float(travel_expenses))
                
                if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained >0:
                    number_of_billed_adults = 1
                    number_of_billed_children = number_of_child_signatures_obtained - 1
                else:
                    number_of_billed_adults = number_of_adult_signatures_obtained
                    number_of_billed_children = number_of_child_signatures_obtained 


                if self.locality.lower() == 'in area':

                    total_signature_fee_for_adults = default_in_area_payment_for_one_signature

                    if number_of_billed_adults > 1:
                        total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_in_area_payment_for_each_additional_adult_signature
                    
                    if number_of_billed_children > 0:
                        total_signature_fee_for_children = number_of_billed_children * default_in_area_payment_for_children

                    
                    total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                    if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                        total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures
                    
                else:
                    # case out of area
                    total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature 
                    
                    if number_of_billed_adults  > 1:
                        total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_out_of_area_payment_for_each_additional_adult_signature
                    
                    total_signature_fee_for_children = number_of_billed_children * default_out_of_area_payment_for_children

                    
                    total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                    if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                        total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures
                
                amount_paid_to_investigator = total_signature_fee + travel_expenses + additional_expenses
                    
                
                
            elif self.did_investigator_travel:
                        
                if no_of_miles_travelled > no_of_free_miles_investigator and int(no_of_miles_travelled) != 0:
                    travel_expenses = ((no_of_miles_travelled - no_of_free_miles_investigator) * mileage_rate_investigator)
                    print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_investigator),float(no_of_miles_travelled), float(mileage_rate_investigator),float(travel_expenses))
                else:
                    print "Travel expenses is $0"

                amount_paid_to_investigator = basic_fee_investigator + travel_expenses + additional_expenses

                pass
            else:

                travel_expenses =  0
                total_signature_fee_for_adults = 0
                total_signature_fee_for_children = 0
                total_signature_fee = 0
                amount_paid_to_investigator = 0

        
        self.amount_paid_to_investigator = amount_paid_to_investigator
        self.save()
        return amount_paid_to_investigator

    def get_law_firm_price(self):

        # if self.amount_billed_to_law_firm != 0.0:
        #     return self.amount_billed_to_law_firm

        if self.invoice is not None:
            return self.invoice.total_billed_amount

        basic_fee = self.basic_fee_law_firm
        mileage_rate = self.mileage_rate_law_firm
        no_of_free_miles = self.no_of_free_miles_law_firm
        no_of_miles = self.no_of_miles_travelled
        additional_expenses = self.additional_expenses
        rsn_extra_expenses = self.rsn_extra_expenses
        travel_expenses = 0

        if no_of_miles > no_of_free_miles:
            travel_expenses = ((no_of_miles - no_of_free_miles) * mileage_rate)

        law_firm_rates = self.law_firm.rates


        default_in_area_payment_for_one_signature = law_firm_rates.default_in_area_payment_for_one_signature
        default_in_area_payment_for_each_additional_adult_signature = law_firm_rates.default_in_area_payment_for_each_additional_adult_signature
        default_in_area_payment_for_children = law_firm_rates.default_in_area_payment_for_children
        maximum_in_area_payment_for_any_number_of_signatures = law_firm_rates.maximum_in_area_payment_for_any_number_of_signatures

        default_out_of_area_payment_for_one_signature = law_firm_rates.default_out_of_area_payment_for_one_signature
        default_out_of_area_payment_for_each_additional_adult_signature = law_firm_rates.default_out_of_area_payment_for_each_additional_adult_signature
        default_out_of_area_payment_for_children = law_firm_rates.default_out_of_area_payment_for_children
        maximum_out_of_area_payment_for_any_number_of_signatures = law_firm_rates.maximum_out_of_area_payment_for_any_number_of_signatures

        basic_fee_law_firm = self.basic_fee_law_firm
        mileage_rate_law_firm = self.mileage_rate_law_firm
        no_of_free_miles_law_firm = self.no_of_free_miles_law_firm
        no_of_miles_travelled = self.no_of_miles_travelled
        additional_expenses = self.additional_expenses
        rsn_extra_expenses = self.rsn_extra_expenses

        number_of_adult_signatures_obtained = self.number_of_adult_signatures_obtained
        number_of_child_signatures_obtained = self.number_of_child_signatures_obtained

        travel_expenses = 0

        amount_billed_to_law_firm = 0

        if no_of_miles_travelled > no_of_free_miles_law_firm and int(no_of_miles_travelled) != 0:
            travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
        else:
            pass
            # print "Travel expenses is $0"


        signature_prices = 0
       
            
              
        if self.is_signature_obtained:

            number_of_billed_adults = 0
            number_of_billed_children = 0
            total_signature_fee = 0
            total_signature_fee_for_adults = 0
            total_signature_fee_for_children = 0


        
            if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained >0:
                number_of_billed_adults = 1
                number_of_billed_children = number_of_child_signatures_obtained - 1
            else:
                number_of_billed_adults = number_of_adult_signatures_obtained
                number_of_billed_children = number_of_child_signatures_obtained 


            if self.locality.lower() == 'in area':

                total_signature_fee_for_adults = default_in_area_payment_for_one_signature

                if number_of_billed_adults > 1:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_in_area_payment_for_each_additional_adult_signature
                
                if number_of_billed_children > 0:
                    total_signature_fee_for_children = number_of_billed_children * default_in_area_payment_for_children

                
                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children
                
                if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures
                
                
            else:
                # case out of area
                total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature 
                
                if number_of_billed_adults  > 1:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_out_of_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_out_of_area_payment_for_children

                
                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures
                

            
            amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses + rsn_extra_expenses
                
            
            
        elif self.did_investigator_travel:                    
            amount_billed_to_law_firm = basic_fee_law_firm + travel_expenses + additional_expenses + rsn_extra_expenses

            pass
        else:
            travel_expenses =  0
            total_signature_fee_for_adults = 0
            total_signature_fee_for_children = 0
            total_signature_fee = 0
            amount_billed_to_law_firm = 0
        
        self.amount_billed_to_law_firm = amount_billed_to_law_firm
        self.save()
        return amount_billed_to_law_firm
    
    def __str__(self):
        return '%s' % (self.name)

    def get_proposed_law_firm_price(self):
        
        law_firm_rates = self.law_firm.rates


        default_in_area_payment_for_one_signature = law_firm_rates.default_in_area_payment_for_one_signature
        default_in_area_payment_for_each_additional_adult_signature = law_firm_rates.default_in_area_payment_for_each_additional_adult_signature
        default_in_area_payment_for_children = law_firm_rates.default_in_area_payment_for_children
        maximum_in_area_payment_for_any_number_of_signatures = law_firm_rates.maximum_in_area_payment_for_any_number_of_signatures

        default_out_of_area_payment_for_one_signature = law_firm_rates.default_out_of_area_payment_for_one_signature
        default_out_of_area_payment_for_each_additional_adult_signature = law_firm_rates.default_out_of_area_payment_for_each_additional_adult_signature
        default_out_of_area_payment_for_children = law_firm_rates.default_out_of_area_payment_for_children
        maximum_out_of_area_payment_for_any_number_of_signatures = law_firm_rates.maximum_out_of_area_payment_for_any_number_of_signatures

        basic_fee_law_firm = self.basic_fee_law_firm
        mileage_rate_law_firm = self.mileage_rate_law_firm
        no_of_free_miles_law_firm = self.no_of_free_miles_law_firm
        no_of_miles_travelled = self.no_of_miles_travelled
        additional_expenses = self.additional_expenses
        rsn_extra_expenses = self.rsn_extra_expenses

        number_of_adult_signatures_obtained = self.number_of_adult_signatures_required
        number_of_child_signatures_obtained = self.number_of_child_signatures_required

        travel_expenses = 0

        amount_billed_to_law_firm = 0

        if no_of_miles_travelled > no_of_free_miles_law_firm and int(no_of_miles_travelled) != 0:
            travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
        else:
            pass
            # print "Travel expenses is $0"


        signature_prices = 0
       
            
              

        number_of_billed_adults = 0
        number_of_billed_children = 0
        total_signature_fee = 0
        total_signature_fee_for_adults = 0
        total_signature_fee_for_children = 0


    
        if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained >0:
            number_of_billed_adults = 1
            number_of_billed_children = number_of_child_signatures_obtained - 1
        else:
            number_of_billed_adults = number_of_adult_signatures_obtained
            number_of_billed_children = number_of_child_signatures_obtained 


        if self.locality.lower() == 'in area':

            total_signature_fee_for_adults = default_in_area_payment_for_one_signature

            if number_of_billed_adults > 1:
                total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_in_area_payment_for_each_additional_adult_signature
            
            if number_of_billed_children > 0:
                total_signature_fee_for_children = number_of_billed_children * default_in_area_payment_for_children

            
            total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children
            
            if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures
            
            
        else:
            # case out of area
            total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature 
            
            if number_of_billed_adults  > 1:
                total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_out_of_area_payment_for_each_additional_adult_signature
            
            total_signature_fee_for_children = number_of_billed_children * default_out_of_area_payment_for_children

            
            total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

            if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures
            

        
        amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses + rsn_extra_expenses
        print amount_billed_to_law_firm
        return amount_billed_to_law_firm

    def get_proposed_investigator_price(self):

        basic_fee_investigator = self.basic_fee_investigator
        mileage_rate_investigator = self.mileage_rate_investigator
        no_of_free_miles_investigator = self.no_of_free_miles_investigator
        no_of_miles_travelled = self.no_of_miles_travelled
        additional_expenses = self.additional_expenses

        number_of_adult_signatures_obtained = self.number_of_adult_signatures_required
        number_of_child_signatures_obtained = self.number_of_child_signatures_required

        travel_expenses = 0

        amount_paid_to_investigator = 0

        is_signature_obtained = False
        did_investigator_travel = False

        if no_of_miles_travelled > no_of_free_miles_investigator:
            travel_expenses = ((no_of_miles_travelled - no_of_free_miles_investigator) * mileage_rate_investigator)

        signature_prices = 0
        if self.investigator:
            investigator_rates = self.investigator.rates
            default_in_area_payment_for_one_signature = investigator_rates.default_in_area_payment_for_one_signature
            default_in_area_payment_for_each_additional_adult_signature = investigator_rates.default_in_area_payment_for_each_additional_adult_signature
            default_in_area_payment_for_children = investigator_rates.default_in_area_payment_for_children
            maximum_in_area_payment_for_any_number_of_signatures = investigator_rates.maximum_in_area_payment_for_any_number_of_signatures

            default_out_of_area_payment_for_one_signature = investigator_rates.default_out_of_area_payment_for_one_signature
            default_out_of_area_payment_for_each_additional_adult_signature = investigator_rates.default_out_of_area_payment_for_each_additional_adult_signature
            default_out_of_area_payment_for_children = investigator_rates.default_out_of_area_payment_for_children
            maximum_out_of_area_payment_for_any_number_of_signatures = investigator_rates.maximum_out_of_area_payment_for_any_number_of_signatures


            number_of_billed_adults = 0
            number_of_billed_children = 0
            total_signature_fee = 0
            total_signature_fee_for_adults = 0
            total_signature_fee_for_children = 0

            if no_of_miles_travelled > no_of_free_miles_investigator and int(no_of_miles_travelled) != 0:
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_investigator) * mileage_rate_investigator)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_investigator),float(no_of_miles_travelled), float(mileage_rate_investigator),float(travel_expenses))
            
            if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained >0:
                number_of_billed_adults = 1
                number_of_billed_children = number_of_child_signatures_obtained - 1
            else:
                number_of_billed_adults = number_of_adult_signatures_obtained
                number_of_billed_children = number_of_child_signatures_obtained 


            if self.locality.lower() == 'in area':

                total_signature_fee_for_adults = default_in_area_payment_for_one_signature

                if number_of_billed_adults > 1:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_in_area_payment_for_each_additional_adult_signature
                
                if number_of_billed_children > 0:
                    total_signature_fee_for_children = number_of_billed_children * default_in_area_payment_for_children

                
                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures
                
            else:
                # case out of area
                total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature 
                
                if number_of_billed_adults  > 1:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_out_of_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_out_of_area_payment_for_children

                
                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures
            
            amount_paid_to_investigator = total_signature_fee + travel_expenses + additional_expenses
                
        return amount_paid_to_investigator
    
    def get_case_final_status(self):

        if (self.is_signature_obtained):
            return "Signature obtained"
        elif (self.did_investigator_travel):
            return "Signature not obtained"
        else:
            return "Client cancelled"