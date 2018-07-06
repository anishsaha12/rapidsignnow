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

from django.db.models import Q, Count
from law_firm.charging_law_firm import *
from master_broker.models import MasterBroker

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
        except:
            print "failed by exception"
    for failed_transaction_id in failed_transactions_list:
        try:
            failed_transaction = FailedTransaction.objects.get(pk=failed_transaction_id)
            failed_transaction.delete()
        except:
            print "failed transaction does not exist"

    charging_reminder()

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
                           'david@rapidlegalsign.com'])
    message.content_subtype = "html"
    message.attach('All-Cases.csv', csv, 'text/csv')
    message.send()
