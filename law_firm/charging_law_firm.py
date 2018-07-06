from case.models import Case
from law_firm.models import LawFirm
from transactions.models import Transaction
from invoice.models import Invoice
from invoice_line.models import InvoiceLine
from status_update.models import StatusUpdate
from django.core.mail import send_mail, EmailMessage
from io import BytesIO
import StringIO
import zipfile
import os
from datetime import timedelta, date
from dateutil import relativedelta
from django.utils import timezone
from django.conf import settings
import datetime

import random
from random import randint

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from customer_profile.models import CustomerProfile
from transactions.models import Transaction
from failed_transactions.models import FailedTransaction
from refunds.models import Refund

from django.db.models import Q, Count

import logging
from time import gmtime, strftime

PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]
styles = getSampleStyleSheet()
env = os.environ.get("ENV")

if env == "dev":
    host = "http://127.0.0.1:8000"
elif env == "staging":
    host = "http://staging.rapidsignnow.com"
elif env == "prod":
    host = "https://app.rapidsignnow.com"
    
def charge_law_firm_daily():

    # Create Log File for charging
    log_file_name = strftime("%d%m%Y%H%M%S", gmtime())
    charge_date = strftime("%d-%m-%Y %H:%M:%S", gmtime())
    print log_file_name
    logging.basicConfig(filename='./logs/'+log_file_name+'.log',level=logging.INFO)

    logging.info('Charging Law firms for date:'+ str(charge_date))
    logging.info('--------------------------------------------------------------------')

    # now = timezone.now()
    cases = Case.objects.filter(is_marked_for_payment=True).filter(
        approved_by_rsn=True).filter(has_law_firm_paid=False).filter(is_dispute_raised=False)
    law_firms = LawFirm.objects.filter(payment_plan="daily").filter(is_payment_profile_created = True)

    for law_firm in law_firms:
        amount_billed_to_law_firm = 0
        cases_by_law_firm_list = ""
        cases_by_law_firm = cases.filter(law_firm=law_firm)

        # Create transaction reference id and assign it to the cases:
        reference_id = create_reference_id()

        for case in cases_by_law_firm:
            
            case.reference_id = reference_id
            case.save()

            amount_billed_to_law_firm = amount_billed_to_law_firm + case.get_law_firm_price()
            cases_by_law_firm_list = cases_by_law_firm_list + str(case.pk) + ","
        
        print str(amount_billed_to_law_firm)
        print str(cases_by_law_firm_list)
        # Create a temporary transaction record in the failed txn table
        new_failed_transaction = FailedTransaction(law_firm=law_firm,reference_id=reference_id,cases=cases_by_law_firm_list,amount_charged=amount_billed_to_law_firm)
        new_failed_transaction.save()

        if cases_by_law_firm_list and amount_billed_to_law_firm is not 0:
            logging.info('Sending authorize a request to charge law firm')
            # perform charging these cases
            transaction_response = chargeCustomerProfile(law_firm, amount_billed_to_law_firm, reference_id)
            if transaction_response is not None:
                if transaction_response.transactionResponse.transId and transaction_response.transactionResponse.transId is not "0":
                    transaction_id = transaction_response.transactionResponse.transId
                    account_number = transaction_response.transactionResponse.accountNumber
                    new_transaction = Transaction(law_firm=law_firm, cases=cases_by_law_firm_list,
                                                amount_charged=amount_billed_to_law_firm, transaction_id=transaction_id,reference_id=reference_id)
                    new_transaction.save()
                    logging.info('--- Charged '+ str(law_firm.name) +' Successfully --- Transaction ID: '+ str(transaction_id) +' --- Reference ID: '+ str(reference_id) + ' --- Amount: $'+ str(amount_billed_to_law_firm) +' --- Cases Charged: ['+ str(cases_by_law_firm_list) +'] ---')
                    # send email to law firm email and all attornies with attached zipped invoice
                    buff = StringIO.StringIO()
                    archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

                    list_of_pdfs = []

                    for case_in_range in cases_by_law_firm:
                        file_like_object = StringIO.StringIO()
                        generate_the_invoice(file_like_object, law_firm, [case_in_range])
                        case_in_range.is_invoice_mailed = True
                        case_in_range.has_law_firm_paid = True
                        case_in_range.save()
                        archive.writestr('Invoice for ' + case_in_range.name +
                                        '.pdf', file_like_object.getvalue())
                    archive.close()
                    buff.flush()
                    ret_zip = buff.getvalue()
                    buff.close()
                    law_firm_email = law_firm.email_one
                    invoice_recipients = str(law_firm.invoice_recipients)
                    try:
                        if invoice_recipients is not "":
                            invoice_recipients = invoice_recipients.split(',')

                            logging.info('Sending Email to Law Firm and Invoice recipients')

                            email_body = 'Hi ' + law_firm.name + ',<br/><br/> An amount of $' + str(amount_billed_to_law_firm) + ' has been charged by RapidSignNow from '+ str(account_number) + '. <br><br> Please find the attached invoices which containes all the cases that were charged. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
                            message = EmailMessage('Invoice', email_body,
                                                'invoice@rapidsignnow.com', [law_firm_email],cc=invoice_recipients)
                            message.content_subtype = "html"
                            message.attach('Invoices.zip', ret_zip, 'application/zip')
                            message.send()
                        else:
                            logging.info('Sending Email to Law Firm')
                            email_body = 'Hi ' + law_firm.name + ',<br/><br/> An amount of $' + str(amount_billed_to_law_firm) + ' has been charged by RapidSignNow from '+ str(account_number) + '. <br><br> Please find the attached invoices which containes all the cases that were charged. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
                            message = EmailMessage('Invoice', email_body,
                                                'invoice@rapidsignnow.com', [law_firm_email])
                            message.content_subtype = "html"
                            message.attach('Invoices.zip', ret_zip, 'application/zip')
                            message.send()
                    except:
                        logging.info('Failed sending email to law firm')
                        print  "could not send email"

                    # Remove record for the reference id that is successful
                    new_failed_transaction.delete()

                else:
                    logging.info('Error Charging law firm')
                    if hasattr(transaction_response.transactionResponse, 'errors') == True:
                        print ('Error Code:  %s' % str(transaction_response.transactionResponse.errors.error[0].errorCode))
                        print ('Error message: %s' % transaction_response.transactionResponse.errors.error[0].errorText)
                        
                        error_code = str(transaction_response.transactionResponse.errors.error[0].errorCode)
                        error_text = transaction_response.transactionResponse.errors.error[0].errorText

                        logging.info('--- Error Charging '+ str(law_firm.name) +' --- Error Code: '+ str(error_code) + ' --- Error Message: '+ str(error_text) +' ---')

                        # Add the error code and error message to the failed transaction
                        new_failed_transaction.error_code = error_code
                        new_failed_transaction.error_text = error_text
                        new_failed_transaction.save()

                        logging.info('Saved failed transaction with failure reason')

                        csv_buffer = BytesIO()
                        generate_csv(csv_buffer, cases_by_law_firm)
                        csv = csv_buffer.getvalue()
                        csv_buffer.close()

                        logging.info('Sending Email to David regarding charging failure...')

                        # Send Email to David regarding the transaction failure
                        email_body = 'Hi David, <br> <br> This is to notify you that the cases that were to be charged for '+ law_firm.name +' was not charged due to the following error.<br><br> Error Code: '+ str(error_code) + '<br>Error Message: '+ error_text +'<br>Please check with the law firm to get this issue resolved.<br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
                        message = EmailMessage('Error charging Law Firm', email_body, 'error@rapidsignnow.com', [settings.INVOICE_HARDCODED_TO_EMAIL],cc=["varun.nair@42hertz.com","ankit.singh@42hertz.com"])
                        message.content_subtype = "html"
                        message.attach('All-Cases.csv', csv, 'text/csv')
                        message.send()

                        logging.info('Failure email sent successfully to david.')

                        print "Failed due to error"
            else:
                # Since failed transaction is already created do nothing
                logging.info('No transaction id recieved and failed. But transaction is logged in the failed transaction')
                print("Transaction id not received")
                # return "Failed - No Response"
        else:
            logging.info('No cases to be charged for this law firm')
            print "No cases to be charged"
    
    charging_reminder()
    logging.info('Sent charging reminder email to law firm')
    logging.info('--------------------------------------------------------------------')
    logging.info('---------------Charging Completed---------------')
    logging.info('--------------------------------------------------------------------')
    return "Success"

def charge_law_firm_monthly():

    # Create Log File for charging
    log_file_name = strftime("%d%m%Y%H%M%S", gmtime())
    charge_date = strftime("%d-%m-%Y %H:%M:%S", gmtime())
    print log_file_name
    logging.basicConfig(filename='./logs/'+log_file_name+'.log',level=logging.INFO)

    logging.info('Charging Law firms for date:'+ str(charge_date))
    logging.info('--------------------------------------------------------------------')

    cases = Case.objects.filter(is_marked_for_payment=True).filter(
        approved_by_rsn=True).filter(has_law_firm_paid=False).filter(is_dispute_raised=False)

    law_firms = LawFirm.objects.filter(payment_plan="monthly").filter(is_payment_profile_created=True)

    for law_firm in law_firms:
        amount_billed_to_law_firm = 0
        cases_by_law_firm_list = ""
        cases_by_law_firm = cases.filter(law_firm=law_firm)

        # Create transaction reference id and assign it to the cases:
        reference_id = create_reference_id()

        for case in cases_by_law_firm:
            
            case.reference_id = reference_id
            case.save()

            amount_billed_to_law_firm = amount_billed_to_law_firm + case.get_law_firm_price()
            cases_by_law_firm_list = cases_by_law_firm_list + str(case.pk) + ","
        
        print str(amount_billed_to_law_firm)
        print str(cases_by_law_firm_list)
        # Create a temporary transaction record in the failed txn table
        new_failed_transaction = FailedTransaction(law_firm=law_firm,reference_id=reference_id,cases=cases_by_law_firm_list,amount_charged=amount_billed_to_law_firm)
        new_failed_transaction.save()

        if cases_by_law_firm_list and amount_billed_to_law_firm is not 0:
            logging.info('Sending authorize a request to charge law firm')
            # perform charging these cases
            transaction_response = chargeCustomerProfile(law_firm, amount_billed_to_law_firm, reference_id)
            if transaction_response is not None:
                if transaction_response.transactionResponse.transId and transaction_response.transactionResponse.transId is not "0":
                    transaction_id = transaction_response.transactionResponse.transId
                    account_number = transaction_response.transactionResponse.accountNumber

                    new_transaction = Transaction(law_firm=law_firm, cases=cases_by_law_firm_list,
                                                amount_charged=amount_billed_to_law_firm, transaction_id=transaction_id,reference_id=reference_id)
                    new_transaction.save()
                    logging.info('--- Charged '+ str(law_firm.name) +' Successfully --- Transaction ID: '+ str(transaction_id) +' --- Reference ID: '+ str(reference_id) + ' --- Amount: $'+ str(amount_billed_to_law_firm) +' --- Cases Charged: ['+ str(cases_by_law_firm_list) +'] ---')
                    # send email to law firm email and all attornies with attached zipped invoice
                    buff = StringIO.StringIO()
                    archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

                    list_of_pdfs = []

                    for case_in_range in cases_by_law_firm:
                        file_like_object = StringIO.StringIO()
                        generate_the_invoice(file_like_object, law_firm, [case_in_range])
                        case_in_range.is_invoice_mailed = True
                        case_in_range.has_law_firm_paid = True
                        case_in_range.save()
                        archive.writestr('Invoice for ' + case_in_range.name +
                                        '.pdf', file_like_object.getvalue())
                    archive.close()
                    buff.flush()
                    ret_zip = buff.getvalue()
                    buff.close()
                    law_firm_email = law_firm.email_one
                    invoice_recipients = str(law_firm.invoice_recipients)
                    try:
                        if invoice_recipients is "":
                            invoice_recipients = invoice_recipients.split(',')

                            logging.info('Sending Email to Law Firm and Invoice recipients')

                            email_body = 'Hi ' + law_firm.name + ',<br/><br/> An amount of $' + str(amount_billed_to_law_firm) + ' has been charged by RapidSignNow from '+ str(account_number) + '. <br><br> Please find the attached invoices which containes all the cases that were charged. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
                            message = EmailMessage('Invoice', email_body,
                                                'invoice@rapidsignnow.com', [law_firm_email],cc=invoice_recipients)
                            message.content_subtype = "html"
                            message.attach('Invoices.zip', ret_zip, 'application/zip')
                            message.send()
                        else:
                            logging.info('Sending Email to Law Firm')
                            email_body = 'Hi ' + law_firm.name + ',<br/><br/> An amount of $' + str(amount_billed_to_law_firm) + ' has been charged by RapidSignNow from '+ str(account_number) + '. <br><br> Please find the attached invoices which containes all the cases that were charged. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
                            message = EmailMessage('Invoice', email_body,
                                                'invoice@rapidsignnow.com', [law_firm_email])
                            message.content_subtype = "html"
                            message.attach('Invoices.zip', ret_zip, 'application/zip')
                            message.send()
                    except:
                        logging.info('Failed sending email to law firm')
                        print "could not send email"

                    # Remove record for the reference id that is successful
                    new_failed_transaction.delete()

                    charging_reminder()
                else:
                    logging.info('Error Charging law firm')
                    if hasattr(transaction_response.transactionResponse, 'errors') == True:
                        print ('Error Code:  %s' % str(transaction_response.transactionResponse.errors.error[0].errorCode))
                        print ('Error message: %s' % transaction_response.transactionResponse.errors.error[0].errorText)
                        
                        error_code = str(transaction_response.transactionResponse.errors.error[0].errorCode)
                        error_text = transaction_response.transactionResponse.errors.error[0].errorText

                        logging.info('--- Error Charging '+ str(law_firm.name) +' --- Error Code: '+ str(error_code) + ' --- Error Message: '+ str(error_text) +' ---')

                        # Add the error code and error message to the failed transaction
                        new_failed_transaction.error_code = error_code
                        new_failed_transaction.error_text = error_text
                        new_failed_transaction.save()

                        logging.info('Saved failed transaction with failure reason')

                        csv_buffer = BytesIO()
                        generate_csv(csv_buffer, cases_by_law_firm)
                        csv = csv_buffer.getvalue()
                        csv_buffer.close()

                        logging.info('Sending Email to David regarding charging failure...')

                        # Send Email to David regarding the transaction failure
                        email_body = 'Hi David, <br> <br> This is to notify you that the cases that were to be charged for '+ law_firm.name +' was not charged due to the following error.<br><br> Error Code: '+ str(error_code) + '<br>Error Message: '+ error_text +'<br>Please check with the law firm to get this issue resolved.<br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
                        message = EmailMessage('Error charging Law Firm', email_body, 'error@rapidsignnow.com', [settings.INVOICE_HARDCODED_TO_EMAIL],cc=["varun.nair@42hertz.com","ankit.singh@42hertz.com"])
                        message.content_subtype = "html"
                        message.attach('All-Cases.csv', csv, 'text/csv')
                        message.send()

                        logging.info('Failure email sent successfully to david.')
                        print "Failed due to error"

            else:
                # Since failed transaction is already created do nothing
                logging.info('No transaction id recieved and failed. But transaction is logged in the failed transaction')
                print("Transaction id not received")
                print "Failed - No Response"
        else:
            logging.info('No cases to be charged for this law firm')
            print "No cases to be charged"
            
    return "Success"

def generate_the_invoice(output, law_firm, cases):

    if len(cases) < 1:
        raise ValueError('Cases cannot be zero for invoicing')

    for case in cases:
        if case.invoice is not None:
            print_invoice_as_pdf(output, case.invoice, law_firm)
            return

    entire_invoice_total = 0

    law_firm_rates = law_firm.rates

    default_in_area_payment_for_one_signature = law_firm_rates.default_in_area_payment_for_one_signature
    default_in_area_payment_for_each_additional_adult_signature = law_firm_rates.default_in_area_payment_for_each_additional_adult_signature
    default_in_area_payment_for_children = law_firm_rates.default_in_area_payment_for_children
    maximum_in_area_payment_for_any_number_of_signatures = law_firm_rates.maximum_in_area_payment_for_any_number_of_signatures

    default_out_of_area_payment_for_one_signature = law_firm_rates.default_out_of_area_payment_for_one_signature
    default_out_of_area_payment_for_each_additional_adult_signature = law_firm_rates.default_out_of_area_payment_for_each_additional_adult_signature
    default_out_of_area_payment_for_children = law_firm_rates.default_out_of_area_payment_for_children
    maximum_out_of_area_payment_for_any_number_of_signatures = law_firm_rates.maximum_out_of_area_payment_for_any_number_of_signatures

    invoice = Invoice()
    invoice.law_firm_name = law_firm.name
    invoice.law_firm_address = law_firm.address.simple_address()
    invoice.law_firm_email = law_firm.email_one
    invoice_lines = []

    invoice.save()
    print "Newly created Invoice ID: %d" % invoice.id

    for case in cases:

        case.invoice = invoice
        case.save()

        print "Invoice for case no: %d" % case.id

        # create new invoice line
        invoice_line = InvoiceLine()

        # FK assignments
        invoice_line.invoice = invoice
        invoice_line.case = case

        number_of_adult_signatures_required = 0
        number_of_child_signatures_required = 0
        number_of_adult_signatures_obtained = 0
        number_of_child_signatures_obtained = 0

        is_signature_obtained = False
        did_investigator_travel = False

        case_name = case.name
        case_created_at = case.created_at
        date_of_signup = case.date_of_signup

        investigator_name = case.investigator.user.first_name + \
            ' ' + case.investigator.user.last_name
        client_name = case.client_name
        client_address = case.client_address.simple_address()

        dol = case.dol
        case_closing_date = case.closing_date
        is_dol_provided = case.is_dol_provided
        locality = case.locality
        additional_expenses_description = case.additional_expenses_description
        rsn_extra_expenses = case.rsn_extra_expenses
        rsn_extra_expenses_info = case.rsn_extra_expenses_description

        adult_clients = case.adult_clients
        child_clients = case.child_clients

        basic_fee_law_firm = case.basic_fee_law_firm
        no_of_free_miles_law_firm = case.no_of_free_miles_law_firm
        mileage_rate_law_firm = case.mileage_rate_law_firm
        cancelled_by = case.cancelled_by
        print "cancelled_by:%s" % case.cancelled_by
        cancelled_reason_description = case.cancelled_reason_description
        additional_expenses = case.additional_expenses
        no_of_miles_travelled = case.no_of_miles_travelled

        # Need to calculate these

        travel_expenses = 0
        total_signature_fee_for_adults = 0
        total_signature_fee_for_children = 0
        total_signature_fee = 0
        total_amount_billed_to_law_firm = 0

        if case.is_signature_obtained:

            number_of_adult_signatures_required = case.number_of_adult_signatures_required
            number_of_child_signatures_required = case.number_of_child_signatures_required
            number_of_adult_signatures_obtained = case.number_of_adult_signatures_obtained
            number_of_child_signatures_obtained = case.number_of_child_signatures_obtained
            is_signature_obtained = True
            did_investigator_travel = True

            number_of_billed_adults = 0
            number_of_billed_children = 0

            if no_of_miles_travelled > no_of_free_miles_law_firm and int(no_of_miles_travelled) != 0:
                travel_expenses = (
                    (no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f" % (float(
                    no_of_free_miles_law_firm), float(no_of_miles_travelled), float(mileage_rate_law_firm), float(travel_expenses))

            if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained > 0:
                number_of_billed_adults = 1
                number_of_billed_children = number_of_child_signatures_obtained - 1
            else:
                number_of_billed_adults = number_of_adult_signatures_obtained
                number_of_billed_children = number_of_child_signatures_obtained

            if locality.lower() == 'in area':

                total_signature_fee_for_adults = default_in_area_payment_for_one_signature
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * \
                        default_in_area_payment_for_each_additional_adult_signature

                total_signature_fee_for_children = number_of_billed_children * \
                    default_in_area_payment_for_children

                total_signature_fee = total_signature_fee_for_adults + \
                    total_signature_fee_for_children

                if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + \
                    travel_expenses + additional_expenses + rsn_extra_expenses

            else:
                # case out of area
                total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature

                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * \
                        default_out_of_area_payment_for_each_additional_adult_signature

                total_signature_fee_for_children = number_of_billed_children * \
                    default_out_of_area_payment_for_children

                total_signature_fee = total_signature_fee_for_adults + \
                    total_signature_fee_for_children

                if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + \
                    travel_expenses + additional_expenses + rsn_extra_expenses

        elif case.did_investigator_travel:

            number_of_adult_signatures_required = case.number_of_adult_signatures_required
            number_of_child_signatures_required = case.number_of_child_signatures_required
            number_of_adult_signatures_obtained = 0
            number_of_child_signatures_obtained = 0

            is_signature_obtained = False
            did_investigator_travel = True

            if no_of_miles_travelled > no_of_free_miles_law_firm and int(no_of_miles_travelled) != 0:
                travel_expenses = (
                    (no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f" % (float(
                    no_of_free_miles_law_firm), float(no_of_miles_travelled), float(mileage_rate_law_firm), float(travel_expenses))
            else:
                print "Travel expenses is $0"

            total_amount_billed_to_law_firm = basic_fee_law_firm + \
                travel_expenses + additional_expenses + rsn_extra_expenses

            pass
        else:

            travel_expense = 0
            total_signature_fee_for_adults = 0
            total_signature_fee_for_children = 0
            total_signature_fee = 0
            total_amount_billed_to_law_firm = 0

            pass

        # Just in case someone enters a negative value
        if total_signature_fee_for_children < 0:
            total_signature_fee_for_children = 0
        if total_signature_fee_for_adults < 0:
            total_signature_fee_for_adults = 0
        if travel_expenses < 0:
            travel_expenses = 0
        if additional_expenses < 0:
            additional_expenses = 0
        if no_of_miles_travelled < 0:
            no_of_miles_travelled = 0

        invoice_line.number_of_adult_signatures_required = number_of_adult_signatures_required
        invoice_line.number_of_child_signatures_required = number_of_child_signatures_required
        invoice_line.number_of_adult_signatures_obtained = number_of_adult_signatures_obtained
        invoice_line.number_of_child_signatures_obtained = number_of_child_signatures_obtained

        # other static assignments

        invoice_line.basic_fee_law_firm = basic_fee_law_firm
        invoice_line.no_of_free_miles_law_firm = no_of_free_miles_law_firm
        invoice_line.mileage_rate_law_firm = mileage_rate_law_firm

        invoice_line.case_name = case_name

        invoice_line.investigator_name = investigator_name
        invoice_line.client_name = client_name
        invoice_line.client_address = client_address

        invoice_line.case_created_at = case_created_at
        invoice_line.dol = dol
        invoice_line.is_dol_provided = is_dol_provided
        invoice_line.case_closing_date = case_closing_date
        invoice_line.date_of_signup = date_of_signup
        invoice_line.locality = locality

        invoice_line.adult_clients = adult_clients
        invoice_line.child_clients = child_clients
        invoice_line.cancelled_by = cancelled_by
        invoice_line.cancelled_reason_description = cancelled_reason_description
        invoice_line.is_signature_obtained = is_signature_obtained
        invoice_line.did_investigator_travel = did_investigator_travel

        invoice_line.additional_expenses = additional_expenses
        invoice_line.rsn_extra_expenses = rsn_extra_expenses
        invoice_line.no_of_miles_travelled = no_of_miles_travelled

        invoice_line.travel_expenses = travel_expenses
        invoice_line.total_signature_fee_for_adults = total_signature_fee_for_adults
        invoice_line.total_signature_fee_for_children = total_signature_fee_for_children
        invoice_line.total_signature_fee = total_signature_fee
        invoice_line.total_amount_billed_to_law_firm = total_amount_billed_to_law_firm
        invoice_line.additional_expenses_description = additional_expenses_description
        invoice_line.rsn_extra_expenses_description = rsn_extra_expenses_info
        print "is_signature_obtained: %r" % is_signature_obtained
        print "did_investigator_travel: %r" % did_investigator_travel
        print "travel_expense: %f" % travel_expenses
        print "additional_expenses: %f" % additional_expenses
        print "rsn_extra_expenses: %f" % rsn_extra_expenses
        print "total_signature_fee_for_adults: %f" % total_signature_fee_for_adults
        print "total_signature_fee_for_children: %f" % total_signature_fee_for_children
        print "total_signature_fee: %f" % total_signature_fee
        print "total_amount_billed_to_law_firm: %f" % total_amount_billed_to_law_firm
        print "Cancelled_by:%s" % cancelled_by

        # Save the invoice_line
        invoice_line.save()

        # add the case total to the invoice total
        entire_invoice_total += total_amount_billed_to_law_firm

        invoice_lines.append(invoice_line)

    invoice.total_billed_amount = entire_invoice_total
    invoice.save()
    print_invoice_as_pdf(output, invoice, law_firm)

def print_invoice_as_pdf(output, invoice, law_firm):

    invoice_number = invoice.id
    invoice_lines = InvoiceLine.objects.filter(
        invoice=invoice).order_by('case_created_at')

    light_peacock_green = '#dbf2f9'
    dark_peacock_green = '#166a83'

    doc = SimpleDocTemplate(output)
    story = []
    style = styles["Normal"]

    table_data = [[[Paragraph('Rapid Sign Now', ParagraphStyle('heading', fontSize=15, textColor=dark_peacock_green)), Spacer(1, 0.3*inch)],
                   [Paragraph('INVOICE', ParagraphStyle('heading', fontSize=13, textColor=light_peacock_green, alignment=TA_RIGHT)), Spacer(1, 0.3*inch)]]]

    table_data.append([Paragraph('8 Corporate park suite 300 <br /> Irvine, CA 92606 <br /> customerservice@rapidsignnow.com <br /> www.rapidsignnow.com <br /> P: 310-892-2043',  # <br /> F: 123-555-0124',
                                 ParagraphStyle('address', fontSize=7, textColor=dark_peacock_green, leading=12)),
                       Paragraph('Invoice No.:' + str(invoice_number) + '<br /> Invoice Date: ' + datetime.datetime.now().strftime('%m-%d-%y')
                                 + ' <br /> Due Date: ' + \
                                 (datetime.datetime.now(
                                 ) + datetime.timedelta(days=10)).strftime('%m-%d-%y'),
                                 ParagraphStyle('meta', fontSize=7, textColor=light_peacock_green, leading=12))])

    table_data.append([Paragraph('<b>BILL TO:</b> ' + law_firm.name + '<br />' + law_firm.address.simple_address(),
                                 ParagraphStyle('address', fontSize=7, textColor='#000000', leading=12)), ''])

    table_data.append([Paragraph('<b>Case Details</b>', ParagraphStyle('table-header', fontSize=13, textColor=light_peacock_green, alignment=TA_CENTER)),
                       Paragraph('<b>Amount</b>', ParagraphStyle('table-header', fontSize=13, textColor=light_peacock_green, alignment=TA_CENTER))])

    case_style = ParagraphStyle(
        'case-details', fontSize=8, textColor='#000000')
    law_firm_style = ParagraphStyle(
        'law-firm-details', fontSize=8, textColor='#000000')
    price_style = ParagraphStyle(
        'case-details', fontSize=8, textColor='#000000', alignment=TA_CENTER)

    for invoice_line in invoice_lines:

        case_final_status = ''
        case_cancelled_by = ''
        case_status_additional_info = 'N.A'
        if invoice_line.is_signature_obtained:
            if invoice_line.number_of_adult_signatures_required <= invoice_line.number_of_adult_signatures_obtained and invoice_line.number_of_child_signatures_required <= invoice_line.number_of_child_signatures_obtained:
                case_final_status = 'Signature Obtained'
            else:
                case_final_status = 'Signatures Partially obtained'
        elif invoice_line.did_investigator_travel:
            case_final_status = 'Signature Not Obtained'
        else:
            case_final_status = 'Client Cancelled'
            case_cancelled_by = invoice_line.cancelled_by
            if invoice_line.cancelled_reason_description:
                case_status_additional_info = invoice_line.cancelled_reason_description

        if invoice_line.is_signature_obtained:
            signature_fee = Paragraph(
                'Signature fees: $' + str(invoice_line.total_signature_fee), price_style)
        else:
            signature_fee = Paragraph(
                'Basic fee: $' + str(invoice_line.basic_fee_law_firm), price_style)

        if invoice_line.is_dol_provided:
            try:
                dol_value = invoice_line.dol.strftime('%m-%d-%y')
            except:
                dol_value = str(invoice_line.dol.day) + "-" + \
                    str(invoice_line.dol.month) + \
                    "-" + str(invoice_line.dol.year)
        else:
            dol_value = 'Not Provided'

        # if invoice_line.is_signature_obtained:
        #     is_signature_obtained = 'Yes'
        # else:
        #     is_signature_obtained = 'No'
        additional_expenses_description = 'N.A'
        if invoice_line.additional_expenses_description != '':
            if invoice_line.rsn_extra_expenses_description != '':
                additional_expenses_description = invoice_line.additional_expenses_description + \
                    " and " + invoice_line.rsn_extra_expenses_description
            else:
                additional_expenses_description = invoice_line.additional_expenses_description
        elif invoice_line.rsn_extra_expenses_description != '':
            additional_expenses_description = invoice_line.rsn_extra_expenses_description

        travel_expenses_line = None
        additional_expenses_line = None

        if case_final_status.lower() == 'client cancelled':
            travel_expenses_line = Paragraph(
                'Travel expenses: N.A', price_style)
            additional_expenses_line = Paragraph(
                'Additional expenses: N.A', price_style)
            signature_fee = Paragraph('Signature fee: N.A', price_style)
            case_final_status = case_cancelled_by
        else:
            travel_expenses_line = Paragraph(
                'Travel expenses: $' + str(invoice_line.travel_expenses), price_style)
            additional_expenses = invoice_line.additional_expenses + \
                invoice_line.rsn_extra_expenses
            additional_expenses_line = Paragraph(
                'Additional expenses: $' + str(additional_expenses), price_style)

        if invoice_line.date_of_signup is not None:
            date_of_signup = invoice_line.date_of_signup
        else:
            date_of_signup = invoice_line.case_created_at

        table_data.append([
            [
                [Paragraph('<b>Case name: </b>' +
                           invoice_line.case_name, case_style)],
                [Paragraph(
                    '<b>Investigator: </b>' + invoice_line.investigator_name, case_style)],
                [Paragraph(
                    '<b>Location: </b>' + invoice_line.client_address, case_style)],
                [Paragraph('<b>DOL: </b>' +
                           dol_value, case_style)],
                [Paragraph(
                    '<b>Date of Sign Up: </b>' + date_of_signup.strftime('%m-%d-%y'), case_style)],
                [Paragraph('<b>Locality: </b>' +
                           invoice_line.locality, case_style)],
                [Paragraph(
                    '<b>No. of miles: </b>' + str(invoice_line.no_of_miles_travelled), case_style)],
                [Paragraph(
                    '<b>Mileage rate: </b>' + str(invoice_line.mileage_rate_law_firm), case_style)],
                [Paragraph('<b>Adult clients: </b>' +
                           invoice_line.adult_clients, case_style)],
                [Paragraph('<b>Child clients: </b>' +
                           invoice_line.child_clients, case_style)],
                [Paragraph('<b>Additional expenses desc: </b>' +
                           additional_expenses_description, case_style)],
                [Paragraph('<b>Final Status: </b>' +
                           case_final_status, case_style)],
                [Paragraph(
                    '<b>Status additional info : </b>' + case_status_additional_info, case_style)],
            ],
            [
                [signature_fee],
                [travel_expenses_line],
                [additional_expenses_line],
                [Paragraph(
                    'Total price: $' + str(invoice_line.total_amount_billed_to_law_firm), price_style)]
            ]
        ])

        table_data.append([Paragraph('', style),
                           Paragraph('', style)])
        table_data.append([Paragraph('<b>Total: </b>', style),
                           Paragraph('$' + str(invoice.total_billed_amount), style)])
        table_data.append([Paragraph('<br/><br/>', style),
                           Paragraph('', style)])
        law_firm_rates = law_firm.rates

        adult_clients_full = invoice_line.adult_clients
        adult_clients = adult_clients_full.split(',')
        child_clients_full = invoice_line.child_clients
        child_clients = child_clients_full.split(',')
        if invoice_line.is_signature_obtained:
            table_data.append([
                [
                    [Paragraph(
                        '<br/><br/><br/><b>Clients Signed </b>', style)],
                ],
                [
                    [Paragraph('<br/><br/><br/><b>Cost </b>', style)]
                ]
            ])
            if(invoice_line.locality == 'In Area'):
                signature_fee_for_adult_clients = law_firm_rates.default_in_area_payment_for_one_signature + \
                    ((invoice_line.number_of_adult_signatures_obtained - 1) *
                     law_firm_rates.default_in_area_payment_for_each_additional_adult_signature)
                signature_fee_for_child_clients = law_firm_rates.default_in_area_payment_for_children * \
                    invoice_line.number_of_child_signatures_obtained

                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                            [
                                [Paragraph(
                                    '<br/>'+str(adult_client), law_firm_style)],
                            ],
                            [
                                [Paragraph(
                                    '<b><br/>_______________</b>', law_firm_style)],
                            ]

                        ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                            [
                                [Paragraph(
                                    '<br/>'+str(child_client), law_firm_style)],
                            ],
                            [
                                [Paragraph(
                                    '<b><br/>_______________</b>', law_firm_style)],
                            ]

                        ])
            else:

                signature_fee_for_adult_clients = law_firm_rates.default_out_of_area_payment_for_one_signature + \
                    ((invoice_line.number_of_adult_signatures_obtained - 1) *
                     law_firm_rates.default_out_of_area_payment_for_each_additional_adult_signature)
                signature_fee_for_child_clients = law_firm_rates.default_out_of_area_payment_for_children * \
                    invoice_line.number_of_child_signatures_obtained
                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                            [
                                [Paragraph(
                                    '<br/>'+str(adult_client), law_firm_style)],
                            ],
                            [
                                [Paragraph(
                                    '<b><br/>_______________</b>', law_firm_style)],
                            ]

                        ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                            [
                                [Paragraph(
                                    '<br/>'+str(child_client), law_firm_style)],
                            ],
                            [
                                [Paragraph(
                                    '<b><br/>_______________</b>', law_firm_style)],
                            ]

                        ])

        elif (case_final_status == 'Signature Not Obtained'):
            table_data.append([
                [
                    [Paragraph('<br/><br/><br/><b>Clients</b>', style)],
                ],
                [
                    [Paragraph('<br/><br/><br/><b>Cost </b>', style)]
                ]
            ])
            if(invoice_line.locality == 'In Area'):

                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                            [
                                [Paragraph(
                                    '<br/>'+str(adult_client), law_firm_style)],
                            ],
                            [
                                [Paragraph(
                                    '<b><br/>_______________</b>', law_firm_style)],
                            ]

                        ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                            [
                                [Paragraph(
                                    '<br/>'+str(child_client), law_firm_style)],
                            ],
                            [
                                [Paragraph(
                                    '<b><br/>_______________</b>', law_firm_style)],
                            ]

                        ])
            else:

                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                            [
                                [Paragraph(
                                    '<br/>'+str(adult_client), law_firm_style)],
                            ],
                            [
                                [Paragraph(
                                    '<b><br/>_______________</b>', law_firm_style)],
                            ]

                        ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                            [
                                [Paragraph(
                                    '<br/>'+str(child_client), law_firm_style)],
                            ],
                            [
                                [Paragraph(
                                    '<b><br/>_______________</b>', law_firm_style)],
                            ]

                        ])

        else:
            table_data.append([
                [[Paragraph('<br/><br/><br/><b>Detailed Invoice</b>', style)],
                 [Paragraph(
                     '<b><br/>Basic Fee =</b> $ 0', law_firm_style)],
                 [Paragraph(
                     '<b>Miles travelled =</b> 0', law_firm_style)],
                 [Paragraph(
                     '<b>Travel Expenses =</b> $ 0', law_firm_style)],
                 [Paragraph(
                     '<b>Additional expenses =</b> $ 0', law_firm_style)],
                 [Paragraph(
                     '<b>RSN Extra expenses =</b> $ 0', law_firm_style)],
                 [Paragraph(
                     '<b>Total Price =</b> $ 0', law_firm_style)],
                 [Paragraph('<br/><br/>', style)]
                 ],
                [
                    [Paragraph('', style)],
                    [Paragraph('', style)]
                ]
            ])

    table_content = Table(table_data)
    table_content.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 1), light_peacock_green),
        ('BACKGROUND', (1, 0), (1, 1), dark_peacock_green),
        ('BACKGROUND', (0, 3), (1, 3), dark_peacock_green),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))

    for loop in range(0, len(invoice_lines)):
        table_index = loop + 4
        if table_index % 2 != 0:
            table_content.setStyle(TableStyle([
                ('BACKGROUND', (0, table_index),
                 (1, table_index), light_peacock_green)
            ]))

    rates_style = ParagraphStyle(
        'case-details', fontSize=10, textColor='#000000')

    story.append(table_content)
    doc.build(story, onFirstPage=my_first_page, onLaterPages=my_later_pages)

    pass

def send_reminder_for_approval():

    all_cases = Case.objects.filter(is_marked_for_payment=True).filter(
        approved_by_rsn=True).filter(has_law_firm_paid=False)
    csv_buffer = BytesIO()
    generate_csv(csv_buffer, all_cases)
    csv = csv_buffer.getvalue()
    csv_buffer.close()
    case_ids = []

    for case in all_cases:
        case_ids.append(case.pk)

    email_body = 'Hi David, <br> <br> This is to remind you to approve the cases that were send for approval. Please approve all the cases on <a href="' + host + '/master-broker/cases-to-be-approved/">case to be approved</a> and also check all cases approved on <a href="' + host + '/master-broker/pending-receivables">pending receivables</a> . Please NOTE all the cases on pending receivables would be charged midnight today. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
    message = EmailMessage('Reminder for confirmation', email_body, 'reminder@rapidsignnow.com', [
                           'varun.nair@42hertz.com', 'ankit.singh@42hertz.com'])
    message.content_subtype = "html"
    message.attach('All-Cases.csv', csv, 'text/csv')
    message.send()

def generate_csv(output, all_cases):

    import csv
    import datetime
    writer = csv.writer(output)

    writer.writerow(['Date', 'Date Of Loss', 'Date of Signup', 'Law firm' 'Case name',
                     'Location', 'Status', 'Broker', 'Investigator', ' Amount Billed to Law Firm'])

    try:
        count = 0
        for case in all_cases:
            count = count + 1
            created_at = case.created_at.strftime('%m/%d/%y')

            dol = case.dol.strftime('%m/%d/%y')
            if case.closing_date:
                closing_date = case.closing_date.strftime('%m/%d/%y')
            else:
                closing_date = "Not yet closed"
            investigator_name = case.investigator.user.first_name + \
                ' ' + case.investigator.user.last_name

            if case.created_by:
                broker_name = case.created_by.user.first_name + \
                    ' ' + case.created_by.user.last_name
            elif case.created_by_master:
                broker_name = case.created_by_master.user.first_name + \
                    ' ' + case.created_by_master.user.last_name

            writer.writerow([created_at, dol, closing_date, case.law_firm.name, case.name, case.client_address,
                             case.status, broker_name, investigator_name, case.amount_billed_to_law_firm])
    except:
        print "could not write"
    print count
    return output

def charging_reminder():

    all_cases = Case.objects.filter(is_marked_for_payment=True).filter(has_law_firm_paid=False).filter(is_dispute_raised=False)
    law_firms = LawFirm.objects.filter(payment_plan='daily').filter(is_payment_profile_created=True)
    for law_firm in law_firms:

        cases_by_law_firm = all_cases.filter(law_firm=law_firm)

        if cases_by_law_firm:
            buff = StringIO.StringIO()
            archive = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)

            list_of_pdfs = []

            for case_in_range in cases_by_law_firm:
                file_like_object = StringIO.StringIO()
                generate_the_invoice(
                    file_like_object, law_firm, [case_in_range])
                case_in_range.is_invoice_mailed = True
                case_in_range.save()
                archive.writestr(
                    'Invoice for ' + case_in_range.name + '.pdf', file_like_object.getvalue())
            archive.close()
            buff.flush()
            ret_zip = buff.getvalue()
            buff.close()

            email_body = 'Hi ' + law_firm.name + ', <br> <br> This is to remind you that the cases in the attached zip file will be charged at midnight today. Please check all the cases and the amount billed. Go on <a href="' + host + '/law-firm/cases-to-be-charged"> cases to be charged </a>to raise a dispute if you have any .<br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
            message = EmailMessage('Reminder: Case to be charged today ',
                                   email_body, 'reminder@rapidsignnow.com', [law_firm.email_one])
            message.content_subtype = "html"
            message.attach('Invoices.zip', ret_zip, 'application/zip')
            message.send()

def confirm_charging_cases():

    try:
        case_ids = request.POST['case-ids']
    except:
        return HttpResponse('success:false')

    all_cases_in_range = []

    for case_id in case_ids:
        case_instance = Case.objects.get(pk=case_id)
        case_instance.approved_by_rsn = True
        case_instance.save()

    return HttpResponse('success:false')

def chargeCustomerProfile(law_firm, amount_charged, reference_id):

    customer_profile = CustomerProfile.objects.get(law_firm=law_firm)
    customer_profile_id = customer_profile.auth_customer_profile_id
    primary_payment_profile_id = customer_profile.primary_payment_profile_id
    secondary_payment_profile_id = customer_profile.secondary_payment_profile_id

    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    # Profile to charge
    profileToCharge = apicontractsv1.customerProfilePaymentType()
    profileToCharge.customerProfileId = customer_profile_id
    profileToCharge.paymentProfile = apicontractsv1.paymentProfile()
    profileToCharge.paymentProfile.paymentProfileId = primary_payment_profile_id

    # Create order information
    orderInfo = apicontractsv1.orderType()
    orderInfo.invoiceNumber = str(reference_id)
    orderInfo.description = str(law_firm.name) + " has been charged "+ str(amount_charged)

    # Create transaction request
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = amount_charged
    transactionrequest.profile = profileToCharge
    transactionrequest.order = orderInfo

    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = "MerchantID-0001"

    createtransactionrequest.transactionRequest = transactionrequest
    createtransactioncontroller = createTransactionController(
        createtransactionrequest)
    createtransactioncontroller.setenvironment(constants.PRODUCTION)
    createtransactioncontroller.execute()

    response = createtransactioncontroller.getresponse()

    if response is not None:
        if response.messages.resultCode == "Ok":
            if hasattr(response.transactionResponse, 'messages') == True:
                print ('Successfully created transaction with Transaction ID: %s' %
                       response.transactionResponse.transId)
                print ('Transaction Response Code: %s' %
                       response.transactionResponse.responseCode)
                print ('Message Code: %s' %
                       response.transactionResponse.messages.message[0].code)
                print ('Description: %s' %
                       response.transactionResponse.messages.message[0].description)
                print (response)
                return response
            else:
                # Re try with secondary payment profile
                
                merchantAuth = apicontractsv1.merchantAuthenticationType()
                merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
                merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

                # Profile to charge
                profileToCharge = apicontractsv1.customerProfilePaymentType()
                profileToCharge.customerProfileId = customer_profile_id
                profileToCharge.paymentProfile = apicontractsv1.paymentProfile()
                profileToCharge.paymentProfile.paymentProfileId = secondary_payment_profile_id

                # Create order information
                orderInfo = apicontractsv1.orderType()
                orderInfo.invoiceNumber = str(reference_id)
                orderInfo.description = str(law_firm.name) + " has been charged "+ str(amount_charged)

                # Create transaction request
                transactionrequest = apicontractsv1.transactionRequestType()
                transactionrequest.transactionType = "authCaptureTransaction"
                transactionrequest.amount = amount_charged
                transactionrequest.profile = profileToCharge
                transactionrequest.order = orderInfo

                createtransactionrequest = apicontractsv1.createTransactionRequest()
                createtransactionrequest.merchantAuthentication = merchantAuth
                createtransactionrequest.refId = "MerchantID-0001"

                createtransactionrequest.transactionRequest = transactionrequest
                createtransactioncontroller = createTransactionController(
                    createtransactionrequest)
                createtransactioncontroller.setenvironment(constants.PRODUCTION)
                createtransactioncontroller.execute()

                response = createtransactioncontroller.getresponse()

                if response is not None:
                    if response.messages.resultCode == "Ok":
                        if hasattr(response.transactionResponse, 'messages') == True:
                            print ('Successfully created transaction with Transaction ID: %s' %
                                response.transactionResponse.transId)
                            print ('Transaction Response Code: %s' %
                                response.transactionResponse.responseCode)
                            print ('Message Code: %s' %
                                response.transactionResponse.messages.message[0].code)
                            print ('Description: %s' %
                                response.transactionResponse.messages.message[0].description)
                            print (response)
                            return response
                        else:
                            print ('Failed Transactions.')
                            if hasattr(response.transactionResponse, 'errors') == True:
                                print ('Error Code:  %s' % str(
                                    response.transactionResponse.errors.error[0].errorCode))
                                print ('Error message: %s' %
                                    response.transactionResponse.errors.error[0].errorText)
                                return response
                            else:
                                print ('Error Code: %s' %
                                    response.messages.message[0]['code'].text)
                                print ('Error message: %s' %
                                    response.messages.message[0]['text'].text)
                                return response
                    else:
                        print ('Failed Transaction.')
                        if hasattr(response, 'transactionResponse') == True and hasattr(response.transactionResponse, 'errors') == True:
                            print ('Error Code: %s' % str(
                                response.transactionResponse.errors.error[0].errorCode))
                            print ('Error message: %s' %
                                response.transactionResponse.errors.error[0].errorText)
                            return response
                        else:
                            print ('Error Code: %s' %
                                response.messages.message[0]['code'].text)
                            print ('Error message: %s' %
                                response.messages.message[0]['text'].text)
                            return response
                else:
                    print ('Null Response.')
                    return response
        else:
            # Re try with secondary payment profile
                
            merchantAuth = apicontractsv1.merchantAuthenticationType()
            merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
            merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

            # Profile to charge
            profileToCharge = apicontractsv1.customerProfilePaymentType()
            profileToCharge.customerProfileId = customer_profile_id
            profileToCharge.paymentProfile = apicontractsv1.paymentProfile()
            profileToCharge.paymentProfile.paymentProfileId = secondary_payment_profile_id

            # Create order information
            orderInfo = apicontractsv1.orderType()
            orderInfo.invoiceNumber = str(reference_id)
            orderInfo.description = str(law_firm.name) + " has been charged "+ str(amount_charged)

            # Create transaction request
            transactionrequest = apicontractsv1.transactionRequestType()
            transactionrequest.transactionType = "authCaptureTransaction"
            transactionrequest.amount = amount_charged
            transactionrequest.profile = profileToCharge
            transactionrequest.order = orderInfo

            createtransactionrequest = apicontractsv1.createTransactionRequest()
            createtransactionrequest.merchantAuthentication = merchantAuth
            createtransactionrequest.refId = "MerchantID-0001"

            createtransactionrequest.transactionRequest = transactionrequest
            createtransactioncontroller = createTransactionController(
                createtransactionrequest)
            createtransactioncontroller.setenvironment(constants.PRODUCTION)
            createtransactioncontroller.execute()

            response = createtransactioncontroller.getresponse()

            if response is not None:
                if response.messages.resultCode == "Ok":
                    if hasattr(response.transactionResponse, 'messages') == True:
                        print ('Successfully created transaction with Transaction ID: %s' %
                            response.transactionResponse.transId)
                        print ('Transaction Response Code: %s' %
                            response.transactionResponse.responseCode)
                        print ('Message Code: %s' %
                            response.transactionResponse.messages.message[0].code)
                        print ('Description: %s' %
                            response.transactionResponse.messages.message[0].description)
                        print (response)
                        return response
                    else:
                        print ('Failed Transactions.')
                        if hasattr(response.transactionResponse, 'errors') == True:
                            print ('Error Code:  %s' % str(
                                response.transactionResponse.errors.error[0].errorCode))
                            print ('Error message: %s' %
                                response.transactionResponse.errors.error[0].errorText)
                            return response
                        else:
                            print ('Error Code: %s' %
                                response.messages.message[0]['code'].text)
                            print ('Error message: %s' %
                                response.messages.message[0]['text'].text)
                            return response
                else:
                    print ('Failed Transaction.')
                    if hasattr(response, 'transactionResponse') == True and hasattr(response.transactionResponse, 'errors') == True:
                        print ('Error Code: %s' % str(
                            response.transactionResponse.errors.error[0].errorCode))
                        print ('Error message: %s' %
                            response.transactionResponse.errors.error[0].errorText)
                        return response
                    else:
                        print ('Error Code: %s' %
                            response.messages.message[0]['code'].text)
                        print ('Error message: %s' %
                            response.messages.message[0]['text'].text)
                        return response
            else:
                print ('Null Response.')
                return response
    else:
        print ('Null Response.')
        return response

def my_first_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % (doc.page,))
    canvas.restoreState()

def my_later_pages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % (doc.page,))
    canvas.restoreState()

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def create_reference_id():
    is_unique = False
    while not is_unique:
        reference_id = random_with_N_digits(10)
        try:
            transactions = Transaction.objects.get(reference_id=reference_id)
            failed_transactions = FailedTransaction.objects.get(reference_id=reference_id)
            if not transactions and not failed_transactions:
                is_unique = True
        except:
            print "REFID Unique"
            is_unique = True
    return reference_id

def create_refund_reference_id():
    is_unique = False
    while not is_unique:
        reference_id = random_with_N_digits(10)
        try:
            refund = Refund.objects.get(reference_id=reference_id)
        except:
            print "REFID Unique"
            is_unique = True
    return reference_id

def check_failed_transactions():
    # First check for all failed transactions list cases is the transaction successful or not.
    failed_transactions = FailedTransaction.objects.filter(does_transaction_exist = False)
    # Holds all the transactions which isn't registered at authorize and will be removed from the failed transaction table 
    failed_transactions_list = []
    for failed_transaction in failed_transactions:
        law_firm = failed_transaction.law_firm
        customer_profile = CustomerProfile.objects.get(law_firm=law_firm)
        try:
            transaction_list = get_customer_profile_transaction_list(customer_profile.auth_customer_profile_id)
            if transaction_list is not None:
                data = transaction_list.transactions.transaction
                # print failed_transaction.reference_id
                for transaction in data:
                    print transaction.invoiceNumber
                    
                    if str(failed_transaction.reference_id) == str(transaction.invoiceNumber) and (str(transaction.transactionStatus) == "settledSuccessfully" or str(transaction.transactionStatus) == "capturedPendingSettlement"):
                        transaction_id = str(transaction.transId)
                        new_transaction = Transaction(law_firm=failed_transaction.law_firm, cases=failed_transaction.cases,reference_id=failed_transaction.reference_id,transaction_status=str(transaction.transactionStatus),amount_charged=failed_transaction.amount_charged,transaction_id=transaction_id)
                        new_transaction.save()
                        failed_transaction.does_transaction_exist = True
                        failed_transaction.save()

                        case_ids = failed_transaction.cases.split(",")
                        case_ids = case_ids[:-1]
                        print case_ids
                        for case_id in case_ids:
                            try:
                                case = Case.objects.get(pk=case_id)
                                case.has_law_firm_paid = True
                                case.save()
                            except:
                                print "case_id is wrong"
                        
                        print("Settled Successfully....")
                    else:
                        failed_transactions_list.append(failed_transaction.pk)
                        print("Not a successful transaction or invoice number doesnt exist")
                    
            else:
                print "failed no txns"
        except Exception as ex:
            print ex
            return Exception ("Failed fetching transactions")
    for failed_transaction_id in failed_transactions_list:
        try:
            failed_transaction = FailedTransaction.objects.get(pk=failed_transaction_id)
            failed_transaction.delete()
        except Exception as ex:
            print ex

def get_customer_profile_transaction_list(customerProfileId):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    # set paging and offset parameters
    paging = apicontractsv1.Paging()
    # Paging limit can be up to 1000 for this request
    paging.limit = 5
    paging.offset = 1

    transactionListForCustomerRequest = apicontractsv1.getTransactionListForCustomerRequest()
    transactionListForCustomerRequest.merchantAuthentication = merchantAuth
    transactionListForCustomerRequest.customerProfileId = customerProfileId
    transactionListForCustomerRequest.paging = paging

    transactionListForCustomerController = getTransactionListForCustomerController(transactionListForCustomerRequest)
    transactionListForCustomerController.setenvironment(constants.PRODUCTION)
    transactionListForCustomerController.execute()

    transactionListForCustomerResponse = transactionListForCustomerController.getresponse()
    
    if transactionListForCustomerResponse is not None:
        if transactionListForCustomerResponse.messages.resultCode == apicontractsv1.messageTypeEnum.Ok:
            print('Successfully got transaction list!')

            for transaction in transactionListForCustomerResponse.transactions.transaction:
                print('Transaction Id : %s' % transaction.transId)
                print('Transaction Status : %s' % transaction.transactionStatus)
                print('Amount Type : %s' % transaction.accountType)
                print('Settle Amount : %s' % transaction.settleAmount)
                print('----------------------------------------------------')

            if transactionListForCustomerResponse.messages is not None:
                print('Message Code : %s' % transactionListForCustomerResponse.messages.message[0]['code'].text)
                print('Message Text : %s' % transactionListForCustomerResponse.messages.message[0]['text'].text)
        else:
            if transactionListForCustomerResponse.messages is not None:
                print('Failed to get transaction list.\nCode:%s \nText:%s' % (transactionListForCustomerResponse.messages.message[0]['code'].text,transactionListForCustomerResponse.messages.message[0]['text'].text))

    return transactionListForCustomerResponse       

# Create a custormer profile with payement type as credit card
def createCreditCardProfile(customer_profile_id,card_number,expiration):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = card_number
    creditCard.expirationDate = expiration

    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard

    profile = apicontractsv1.customerPaymentProfileType()
    profile.payment = payment

    createCustomerPaymentProfile = apicontractsv1.createCustomerPaymentProfileRequest()
    createCustomerPaymentProfile.merchantAuthentication = merchantAuth
    createCustomerPaymentProfile.paymentProfile = profile
    print("customerProfileId in create_customer_payment_profile. customerProfileId = %s" %customer_profile_id)
    createCustomerPaymentProfile.customerProfileId = str(customer_profile_id)

    controller = createCustomerPaymentProfileController(createCustomerPaymentProfile)
    controller.setenvironment(constants.PRODUCTION)
    controller.execute()

    response = controller.getresponse()

    if (response.messages.resultCode=="Ok"):
        print("Successfully created a customer payment profile with id: %s" % response.customerPaymentProfileId)
    else:
        print("Failed to create customer payment profile %s" % response.messages.message[0]['text'].text)

    return response


def createACHProfile(customer_profile_id,account_type,accountNumber,routingNumber,nameOnAccount):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    # Create the payment data for a bank account
    bankAccount = apicontractsv1.bankAccountType()
    accountType = apicontractsv1.bankAccountTypeEnum
    if (account_type == "checking"):
        bankAccount.accountType = accountType.checking
    elif (account_type == "savings"):
        bankAccount.accountType = accountType.savings
    else:
        bankAccount.accountType = accountType.businessChecking
    print bankAccount.accountType
    bankAccount.routingNumber = routingNumber
    bankAccount.accountNumber = accountNumber
    bankAccount.nameOnAccount = nameOnAccount

    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.bankAccount = bankAccount

    profile = apicontractsv1.customerPaymentProfileType()
    profile.payment = payment

    createCustomerPaymentProfile = apicontractsv1.createCustomerPaymentProfileRequest()
    createCustomerPaymentProfile.merchantAuthentication = merchantAuth
    createCustomerPaymentProfile.paymentProfile = profile
    print("customerProfileId in create_customer_payment_profile. customerProfileId = %s" %customer_profile_id)
    createCustomerPaymentProfile.customerProfileId = str(customer_profile_id)
    
    controller = createCustomerPaymentProfileController(createCustomerPaymentProfile)
    controller.setenvironment(constants.PRODUCTION)
    controller.execute()

    response = controller.getresponse()

    if (response.messages.resultCode == "Ok"):
        print("Successfully created a customer payment profile with id: %s" 
            %response.customerPaymentProfileId)
    else:
        print("Failed to create customer payment profile %s" 
            %response.messages.message[0]['text'].text)

    return response

def updateCreditCardProfile(customer_profile_id,customer_payment_profile_id,card_number,expiration):

    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = card_number
    creditCard.expirationDate = expiration

    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard

    profile = apicontractsv1.customerPaymentProfileType() 
    profile.payment = payment

    createCustomerPaymentProfile = apicontractsv1.createCustomerPaymentProfileRequest()
    createCustomerPaymentProfile.merchantAuthentication = merchantAuth
    createCustomerPaymentProfile.paymentProfile = profile
    print("customerProfileId in create_customer_payment_profile. customerProfileId = %s" %customer_profile_id)
    createCustomerPaymentProfile.customerProfileId = str(customer_profile_id)

    controller = createCustomerPaymentProfileController(createCustomerPaymentProfile)
    controller.setenvironment(constants.PRODUCTION)
    controller.execute()

    response = controller.getresponse()

    if (response.messages.resultCode=="Ok"):
        print("Successfully created a customer payment profile with id: %s" % response.customerPaymentProfileId)
    else:
        print("Failed to create customer payment profile %s" % response.messages.message[0]['text'].text)

    return response


def updateACHProfile(customer_profile_id,customer_payment_profile_id,customer_bank_account_type,customer_bank_account_number,customer_bank_account_routing_number,customer_bank_account_name):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    # Create the payment data for a bank account
    bankAccount = apicontractsv1.bankAccountType()
    accountType = apicontractsv1.bankAccountTypeEnum
    if (customer_bank_account_type == "checking"):
        bankAccount.accountType = accountType.checking
    elif (customer_bank_account_type == "savings"):
        bankAccount.accountType = accountType.savings
    else:
        bankAccount.accountType = accountType.businessChecking
    print bankAccount.accountType
    bankAccount.routingNumber = customer_bank_account_routing_number
    bankAccount.accountNumber = customer_bank_account_number
    bankAccount.nameOnAccount = customer_bank_account_name

    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.bankAccount = bankAccount

    profile = apicontractsv1.customerPaymentProfileType()
    profile.payment = payment

    createCustomerPaymentProfile = apicontractsv1.createCustomerPaymentProfileRequest()
    createCustomerPaymentProfile.merchantAuthentication = merchantAuth
    createCustomerPaymentProfile.paymentProfile = profile

    print("customerProfileId in create_customer_payment_profile. customerProfileId = %s" %customer_profile_id)
    createCustomerPaymentProfile.customerProfileId = str(customer_profile_id)
    
    controller = createCustomerPaymentProfileController(createCustomerPaymentProfile)
    controller.setenvironment(constants.PRODUCTION)
    controller.execute()

    response = controller.getresponse()

    if (response.messages.resultCode=="Ok"):
        print("Successfully created a customer payment profile with id: %s" % response.customerPaymentProfileId)
    else:
        print("Failed to create customer payment profile %s" % response.messages.message[0]['text'].text)

    return response

def deletePaymentProfile(customer_profile_id,customer_payment_profile_id):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    deleteCustomerPaymentProfile = apicontractsv1.deleteCustomerPaymentProfileRequest()
    deleteCustomerPaymentProfile.merchantAuthentication = merchantAuth
    deleteCustomerPaymentProfile.customerProfileId = customer_profile_id
    deleteCustomerPaymentProfile.customerPaymentProfileId = customer_payment_profile_id

    controller = deleteCustomerPaymentProfileController(deleteCustomerPaymentProfile)
    controller.setenvironment(constants.PRODUCTION)
    controller.execute()

    response = controller.getresponse()

    if (response.messages.resultCode=="Ok"):
        print("Successfully deleted customer payment profile with customer profile id %s" % deleteCustomerPaymentProfile.customerProfileId)
    else:
        print(response.messages.message[0]['text'].text)
        print("Failed to delete customer paymnet profile with customer profile id %s" % deleteCustomerPaymentProfile.customerProfileId)

    return response

#get customer credit card profile
def get_customer_profile_credit_card(customerProfileid,customerPaymentProfileId):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    getCustomerPaymentProfile = apicontractsv1.getCustomerPaymentProfileRequest()
    getCustomerPaymentProfile.merchantAuthentication = merchantAuth
    getCustomerPaymentProfile.customerProfileId = str(customerProfileid)
    getCustomerPaymentProfile.customerPaymentProfileId = str(customerPaymentProfileId)

    controller = getCustomerPaymentProfileController(getCustomerPaymentProfile)
    controller.setenvironment(constants.PRODUCTION)
    controller.execute()

    response = controller.getresponse()

    if (response.messages.resultCode=="Ok"):
        print("Successfully retrieved a payment profile with profile id %s and customer id %s" % (getCustomerPaymentProfile.customerProfileId, getCustomerPaymentProfile.customerProfileId))
        if hasattr(response.paymentProfile.payment, "creditCard") == True:
            print ("Credit Card Recieved")
            credit_card_number = response.paymentProfile.payment.creditCard.cardNumber
            expiration = response.paymentProfile.payment.creditCard.expirationDate
        else:
            print ("No credit card found")
    else:
        print ("Error couldn't fetch payment profile")
    
    return credit_card_number,expiration

# Get customer ACH Profile details
def get_customer_profile_ACH(customerProfileid,customerPaymentProfileId):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    getCustomerPaymentProfile = apicontractsv1.getCustomerPaymentProfileRequest()
    getCustomerPaymentProfile.merchantAuthentication = merchantAuth
    getCustomerPaymentProfile.customerProfileId = str(customerProfileid)
    getCustomerPaymentProfile.customerPaymentProfileId = str(customerPaymentProfileId)

    controller = getCustomerPaymentProfileController(getCustomerPaymentProfile)
    controller.setenvironment(constants.PRODUCTION)
    controller.execute()

    response = controller.getresponse()

    if (response.messages.resultCode=="Ok"):
        print("Successfully retrieved a payment profile with profile id %s and customer id %s" % (getCustomerPaymentProfile.customerProfileId, getCustomerPaymentProfile.customerProfileId))
        if hasattr(response.paymentProfile.payment, "bankAccount") == True:
            print ("Bank Account Recieved")
            customerAccountNumber = response.paymentProfile.payment.bankAccount.accountNumber
            customerBankRoutingNumber = response.paymentProfile.payment.bankAccount.routingNumber
            customerNameOnAccount = response.paymentProfile.payment.bankAccount.nameOnAccount
            customerBankAccountType = response.paymentProfile.payment.bankAccount.accountType
        else:
            print ("No Bank Account Found")
    else:
        print ("Error couldn't fetch payment profile")
    
    return customerAccountNumber,customerBankRoutingNumber,customerNameOnAccount,customerBankAccountType
# Create New Customer Profile
def createCustomerProfile(payment_profile_name,payment_profile_email):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    # Split Payment Profile Name to initials for merchantCustomerId
    profile_name = payment_profile_name.split(" ")
    merchantCustomerId = ""
    for initial in profile_name:
        merchantCustomerId = merchantCustomerId + str(initial[0])
    
    createCustomerProfile = apicontractsv1.createCustomerProfileRequest()
    createCustomerProfile.merchantAuthentication = merchantAuth
    createCustomerProfile.profile = apicontractsv1.customerProfileType(
        merchantCustomerId + str(random.randint(0, 10000)), payment_profile_name, payment_profile_email)

    controller = createCustomerProfileController(createCustomerProfile)
    controller.setenvironment(constants.PRODUCTION)
    controller.execute()

    response = controller.getresponse()

    if (response.messages.resultCode=="Ok"):
        print("Successfully created a customer profile with id: %s" % response.customerProfileId)
    else:
        print("Failed to create customer payment profile %s" % response.messages.message[0]['text'].text)

    return response