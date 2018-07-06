from django.shortcuts import get_object_or_404, render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.utils.http import urlencode
from operator import __or__ as OR
from operator import __and__ as AND

from xhtml2pdf import pisa
from django.template.loader import get_template

import json
import itertools
import ast
import datetime
import random
import StringIO
import mimetypes 
import magic  
import urllib 
from twilio.rest import Client
from datetime import timedelta
from django.utils import timezone 

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *

from address.models import Address
from law_firm.models import LawFirm
from broker.models import Broker
from master_broker.models import MasterBroker
from investigator.models import Investigator
from case.models import Case
from document.models import Document
from attached_document.models import AttachedDocument
from status_update.models import StatusUpdate, CaseAcceptanceUpdate
from customer_profile.models import CustomerProfile

from law_firm.charging_law_firm import *
from random import randint

languages = ["English","Mandarin","Spanish","Hindi","Arabic","Portuguese","Bengali","Russian","Japanese","Punjabi",
             "German","Javanese","Wu","Shanghainese","Malay","Malaysian","Indonesian","Telugu","Vietnamese","Korean",
             "French","Marathi","Tamil","Urdu","Turkish","Italian","Yue","Cantonese","Thai","Gujarati","Jin",
             "Southern Min","Hokkien","Teochew","Persian","Polish","Pashto","Kannada","Xiang","Malayalam","Sundanese",
             "Hausa","Odia","Burmese","Hakka","Ukrainian","Bhojpuri","Tagalog","Yoruba","Maithili","Uzbek","Sindhi",
             "Amharic","Fula","Romanian","Oromo","Igbo","Azerbaijani","Awadhi","Gan Chinese","Cebuano","Dutch",
             "Kurdish","Serbo-Croatian","Malagasy","Saraiki","Nepali","Sinhalese","Chittagonian","Zhuang","Khmer",
             "Turkmen","Assamese","Madurese","Somali","Marwari","Magahi","Haryanvi","Hungarian","Chhattisgarhi",
             "Greek","Chewa","Deccan","Akan","Kazakh","Northern Min","disputed","discuss","Sylheti","Zulu","Czech",
             "Kinyarwanda","Dhundhari","Haitian Creole","Eastern Min","Fuzhounese","Ilocano","Quechua","Kirundi",
             "Swedish","Hmong","Shona","Uyghur","Hiligaynon/Ilonggo","Mossi","Xhosa","Belarusian","Balochi","Konkani"]

countries = ["United States of America","Afghanistan","Aland Islands","Albania","Algeria","American Samoa","Andorra",
             "Angola","Anguilla","Antarctica","Antigua and Barbuda","Argentina","Armenia","Aruba","Australia","Austria",
             "Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda",
             "Bhutan","Bolivia, Plurinational State of","Bonaire, Sint Eustatius and Saba","Bosnia and Herzegovina",
             "Botswana","Bouvet Island","Brazil","British Indian Ocean Territory","Brunei Darussalam","Bulgaria",
             "Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Cayman Islands",
             "Central African Republic","Chad","Chile","China","Christmas Island","Cocos (Keeling) Islands","Colombia",
             "Comoros","Congo","Congo, the Democratic Republic of the","Cook Islands","Costa Rica","Croatia","Cuba",
             "Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt",
             "El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Falkland Islands (Malvinas)",
             "Faroe Islands","Fiji","Finland","France","French Guiana","French Polynesia","French Southern Territories",
             "Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guadeloupe","Guam",
             "Guatemala","Guernsey","Guinea","Guinea-Bissau","Guyana","Haiti","Heard Island and McDonald Islands",
             "Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran, Islamic Republic of","Iraq","Ireland",
             "Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kiribati",
             "Korea, Democratic People's Republic of","Korea, Republic of","Kuwait","Kyrgyzstan",
             "Lao People's Democratic Republic","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein",
             "Lithuania","Luxembourg","Macao","Macedonia, the former Yugoslav Republic of","Madagascar","Malawi",
             "Malaysia","Maldives","Mali","Malta","Marshall Islands","Martinique","Mauritania","Mauritius","Mayotte",
             "Mexico","Micronesia, Federated States of","Moldova, Republic of","Monaco","Mongolia","Montenegro",
             "Montserrat","Morocco","Mozambique","Myanmar","Namibia","Nauru","Nepal","Netherlands","New Caledonia",
             "New Zealand","Nicaragua","Niger","Nigeria","Niue","Norfolk Island","Northern Mariana Islands","Norway",
             "Oman","Pakistan","Palau","Palestinian Territory, Occupied","Panama","Papua New Guinea","Paraguay","Peru",
             "Philippines","Pitcairn","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania",
             "Russian Federation","Rwanda","Saint Barthelemy","Saint Helena, Ascension and Tristan da Cunha",
             "Saint Kitts and Nevis","Saint Lucia","Saint Martin (French part)","Saint Pierre and Miquelon",
             "Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia","Senegal",
             "Serbia","Seychelles","Sierra Leone","Singapore","Sint Maarten (Dutch part)","Slovakia","Slovenia",
             "Solomon Islands","Somalia","South Africa","South Georgia and the South Sandwich Islands","South Sudan",
             "Spain","Sri Lanka","Sudan","Suriname","Svalbard and Jan Mayen","Swaziland","Sweden","Switzerland",
             "Syrian Arab Republic","Taiwan, Province of China","Tajikistan","Tanzania, United Republic of","Thailand",
             "Timor-Leste","Togo","Tokelau","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan",
             "Turks and Caicos Islands","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom",
             "United States Minor Outlying Islands","Uruguay","Uzbekistan","Vanuatu",
             "Venezuela, Bolivarian Republic of","Viet Nam","Virgin Islands, British","Virgin Islands, U.S.",
             "Wallis and Futuna","Western Sahara","Yemen","Zambia","Zimbabwe"]


twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def get_notifications(law_firm):

    unread_statuses = StatusUpdate.objects.filter(case__law_firm=law_firm).order_by('-timestamp')[:15]
    status_notifications = []
    unread_count = 0
    for status in unread_statuses:
        notification = dict()

        notification['status_id'] = status.pk
        notification['case_id'] = status.case.pk
        notification['case_name'] = status.case.name
        if status.updated_by:
            notification['updated_by'] = status.user.first_name + ' ' + status.user.last_name
        notification['status'] = status.status
        notification['timestamp'] = status.timestamp
        # notification['read'] = status.read_by_master_broker
        notification['type'] = 'status'

        # if not status.read_by_master_broker:
        #     unread_count += 1

        status_notifications.append(notification)

    
    unread_acceptances = CaseAcceptanceUpdate.objects.filter(case__law_firm=law_firm).order_by('-timestamp')[:15]
    acceptance_notifications = []

    for acceptance in unread_acceptances:
        notification = dict()

        notification['acceptance_id'] = acceptance.pk
        notification['case_id'] = acceptance.case.pk
        notification['case_name'] = acceptance.case.name
        notification['investigator'] = acceptance.investigator.user.first_name + ' ' + acceptance.investigator.user.last_name
        notification['is_accepted'] = acceptance.is_accepted
        notification['timestamp'] = acceptance.timestamp
        # notification['read'] = acceptance.read_by_master_broker
        notification['type'] = 'acceptance'

        # if not acceptance.read_by_master_broker:
        #     unread_count += 1

        acceptance_notifications.append(notification)

    notifications = status_notifications + acceptance_notifications
    # notifications = sorted(notifications, key=lambda notification: notification['timestamp'])
    notifications = notifications[:15]

    return {
        'entries': notifications,
        'unread': unread_count
    }



def show_investigator_details(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'investigator_id' not in request.POST:
        return HttpResponseRedirect('/')

    investigator_id = request.POST['investigator_id']
    investigator = Investigator.objects.get(pk=investigator_id)

    context = dict()
    context['investigator'] = investigator
    phone_number = investigator.phone_number_one.replace('-', '').replace(' ', '')
    context['phone_number'] = phone_number
    try:
        context['languages'] = ast.literal_eval(investigator.languages)
    except:
        pass
    
    
    context['notifications'] = get_notifications(law_firm)

    return render(request, 'law_firm/investigator_snippet.html', context)

@login_required(login_url='/')
@permission_required('law_firm.can_view_law_firm',raise_exception=True)
def all_cases(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['cases'] = []


    cases = Case.objects.filter(law_firm=law_firm).order_by('-pk')


    for case in cases:
        case.final_status =  get_case_final_status(case)
        case.amount_billed_to_law_firm = case.get_law_firm_price()
          
    context['cases'] = cases
    q_array_status = []
    for case in cases:
        status_updates = StatusUpdate.objects.filter(case = case).order_by('-timestamp')[0:1]
        for status in status_updates:
            q_array_status.append(Q(pk = status.pk))
    try:
        context['status_updates'] = StatusUpdate.objects.filter(reduce(OR, q_array_status))
    except:
        print "No case"
    
   
    all_investigators = Investigator.objects.all()
    for investigator in all_investigators:
        investigator.languages = ast.literal_eval(investigator.languages)

    context['investigators'] = all_investigators
    context['notifications'] = get_notifications(law_firm)

    if request.POST and 'context' in request.POST and request.POST['context'] == 'generate-csv':
        response = HttpResponse(content_type='text/csv')    
        response['Content-Disposition'] = 'attachment; filename="All-cases.csv"'
        response = generate_csv(response,cases,law_firm)
        return response
    elif request.POST and 'context' in request.POST and request.POST['context'] == 'document-received':
        try:
            case_id = request.POST['case_id']
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_document_received = True
            case_instance.save()
        except:
            print "not marked" 
        
        return HttpResponse('')

    elif request.POST and 'context' in request.POST and request.POST['context'] == 'document-not-received':
        try:
            case_id = request.POST['case_id']
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_document_received = False
            case_instance.save()
        except:
            print "not unmarked"

        return HttpResponse('')

    return render(request, 'law_firm/all_cases.html', context)


@login_required(login_url='/')
@permission_required('law_firm.can_view_law_firm',raise_exception=True)
def case_details(request, case_id):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    try:
        case_instance = Case.objects.get(pk=case_id)
    except:
        raise Http404

    
    # if case_instance.created_by.id != broker.id:
    #             raise SuspiciousOperation("Invalid request; You do not have access to this case")
    broker = Broker.objects.all()
    attached_documents = AttachedDocument.objects.filter(case = case_instance)
    context = dict()
    context['broker'] = broker
    context['case'] = case_instance
    context['amount_paid_to_investigator'] = case_instance.get_investigator_price()
    context['amount_billed_to_law_firm'] = case_instance.get_law_firm_price()
    context['law_firms'] = LawFirm.objects.all()
    context['countries'] = countries
    context['editable'] = case_instance.invoice is None and not case_instance.is_investigator_paid
    context['attached_documents'] = attached_documents
    context['case_result'] = get_case_final_status(case_instance)

    context['notifications'] = get_notifications(law_firm)
    client_mobile_phone = case_instance.client_mobile_phone.replace('-', '').replace(' ', '')
    context['client_mobile_phone'] = client_mobile_phone
    client_home_phone = case_instance.client_home_phone.replace('-', '').replace(' ', '')
    context['client_home_phone'] = client_home_phone

    context['status_updates'] = StatusUpdate.objects.filter(case=case_instance).order_by('-timestamp')

    if request.POST.get('context') == 'view-document':
        context = dict()
        context['pagesize'] = 'A4'
        template = get_template('document.html')
        result = StringIO.StringIO()
        document_id = request.POST.get('document-id')
        document_instance = Document.objects.get(pk = document_id)
        mime = magic.Magic(mime=True) 
        buffer = "output" 
        urllib.urlretrieve(document_instance.file.url, buffer)
        mimes = mime.from_file(buffer)
        output = download_doc(request,document_id)
        result = output
        document = result.getvalue()
        # print (result)
        html = template.render(context)
        pdf = pisa.pisaDocument(
            StringIO.StringIO(html.encode("ISO-8859-1")), 
            dest=result, link_callback=fetch_resources)
        
        if not pdf.err:
            return HttpResponse(document, content_type=mimes)
        return HttpResponse("Error: <pre>%s</pre>" % escape(html))    
    if request.POST.get('context') == 'download-document':
        document_id = request.POST['document-id']
        response = download_doc(request,document_id)
        return response


    return render(request, 'law_firm/case_details.html', context)

@login_required(login_url='/')
@permission_required('law_firm.can_view_law_firm',raise_exception=True)
def my_profile(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['law_firm'] = law_firm
    
    context['notifications'] = get_notifications(law_firm)

    return render(request, 'law_firm/my_profile.html', context)

@login_required(login_url='/')
@permission_required('law_firm.can_view_law_firm',raise_exception=True)
def change_password(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()

    if request.POST:
        
        old_password = request.POST["old_password"]
        new_password = request.POST["new_password"]
        new_password_confirm = request.POST["new_password_confirm"]


        if( (old_password is not None) and  (new_password is not None) and (new_password_confirm is not None) and (new_password == new_password_confirm)):

            if (request.user.check_password(old_password)):
                print "Password check successful"
                request.user.set_password(new_password)
                request.user.save()
                return JsonResponse({'success':"true"})


            else:
                print "Password check failed"
                context["error"] = "Your current password is incorrect"
                return JsonResponse({'success':"false"})
        else:
            return JsonResponse({'success':"false"})


    context['notifications'] = get_notifications(law_firm)
    return render(request, 'law_firm/change_password.html', context)

def get_case_final_status(case):
    case_result = None

    if (case.is_signature_obtained):
        return "Signature obtained"
    elif (case.did_investigator_travel):
        return "Signature not obtained"
    else:
        return "Client cancelled"

def download_doc(request,file_id):
    
    document = Document.objects.get(id = file_id)        
    
    mime = magic.Magic(mime=True) 
    output = "output" 
    urllib.urlretrieve(document.file.url, output)
    mimes = mime.from_file(output)
    ext = mimetypes.guess_all_extensions(mimes)[0] 
    # os.rename(output, output+ext) # Rename file
    # pdf = d.file.file.read()
    
    
    # law_firm_email = 'ankit.singh@42hertz.com'
    # email_body = 'Find attached the invoice'
    # message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
    # message.attach('Attachment'+ext, pdf, mimes)
    # message.send()
    
    response = HttpResponse(document.file, content_type=mimes)
    response['Content-Disposition'] = 'attachment; filename=%s' % document.file_name

    return response

def fetch_resources(uri, rel):
    path = join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return path

def manage_documents(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['notifications'] = get_notifications(law_firm)
    documents = Document.objects.filter(law_firm = law_firm)
    context['documents']  = documents

    context['documents_count']  = len(documents)

    # if request.POST:
    #     if 'context' in request.POST and request.POST.get('context') == 'documents':
    #         files = request.FILES.getlist('document')
    #         print (files)
    #         for file in files:
    #             fs = FileSystemStorage()
    #             file_name = fs.save(file.name, file)
    #             uploaded_file_url = fs.url(file_name)
    #             new_document = Document(file_name=file_name, file = file, file_url=uploaded_file_url, law_firm = new_law_firm_instance )
    #             new_document.save()

    if request.POST:
        if request.POST.get('context') == 'view-document':
            context = dict()
            context['pagesize'] = 'A4'
            template = get_template('document.html')
            result = StringIO.StringIO()
            document_id = request.POST.get('document-id')
            document_instance = Document.objects.get(pk = document_id)
            mime = magic.Magic(mime=True) 
            buffer = "output" 
            urllib.urlretrieve(document_instance.file.url, buffer)
            mimes = mime.from_file(buffer)
            output = download_doc(request,document_id)
            result = output
            document = result.getvalue()
            # print (result)
            html = template.render(context)
            pdf = pisa.pisaDocument(
                StringIO.StringIO(html.encode("ISO-8859-1")), 
                dest=result, link_callback=fetch_resources)
            
            if not pdf.err:
                return HttpResponse(document, content_type=mimes)
            return HttpResponse("Error: <pre>%s</pre>" % escape(html))    
        
        elif request.POST.get('context') == 'download-document':
            document_id = request.POST['document-id']
            response = download_doc(request,document_id)
            return response

    return render(request, 'law_firm/manage_documents.html', context)


def delete_document(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'document_id' not in request.POST:
        return HttpResponseRedirect('/')

    document_id = request.POST['document_id']
    document_instance = Document.objects.get(pk=document_id)

    attached_documents = AttachedDocument.objects.filter(document = document_instance)
    if attached_documents:
        raise SuspiciousOperation("Invalid request; Cannot delete document as the document is attached to a case")
    
    if document_instance:
        document_instance.law_firm = None

    document_instance.is_deleted = True
    document_instance.save()
    

    return HttpResponse('')

def generate_csv(output,all_cases,law_firm):

    import csv
    import datetime
    writer = csv.writer(output)
    writer.writerow(['LAW FIRM:', law_firm.name])
    writer.writerow(['',law_firm.address.simple_address()])
    writer.writerow(['',law_firm.phone_number_one])
    writer.writerow([''])
    writer.writerow(['Date','Date Of Loss','Date of Signup' , 'Case name','Location','Status', 'Broker', 'Investigator' ])

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
            investigator_name = case.investigator.user.first_name + ' ' + case.investigator.user.last_name
            
            if case.created_by:
                broker_name = case.created_by.user.first_name + ' ' + case.created_by.user.last_name
            elif case.created_by_master:
                broker_name = case.created_by_master.user.first_name + ' ' + case.created_by_master.user.last_name

            writer.writerow([created_at,dol,closing_date,case.name,case.client_address,case.status, broker_name, investigator_name ])
    except:
        print "could not write"
    print count
    return output

def dashboard(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['notifications'] = get_notifications(law_firm)
    
    # in_progress = 
    total_cases  = Case.objects.filter(law_firm = law_firm).filter(~Q(status= "Duplicate delete"))
    if not total_cases:
        context["no_data"] = True
    else:
        total_cases_count  = total_cases.count()
        client_cancelled = total_cases.filter(Q(status = "Closed") | Q(status = "Client cancelled") ).filter(Q(is_signature_obtained = False) & Q(did_investigator_travel = False))
        client_cancelled_count = client_cancelled.count()
        client_cancelled_percent = float(client_cancelled_count * 100 ) / total_cases_count
        signature_obtained = total_cases.filter(is_signature_obtained = True)
        signature_obtained_count = signature_obtained.count()
        signature_obtained_percent = float(signature_obtained_count * 100 ) /total_cases_count
        signature_not_obtained = total_cases.filter(Q(is_signature_obtained = False) & Q(did_investigator_travel = True))
        signature_not_obtained_count = signature_not_obtained.count()
        signature_not_obtained_percent = float(signature_not_obtained_count * 100) / total_cases_count
        others = round(100 - client_cancelled_percent - signature_not_obtained_percent - signature_obtained_percent,2) 
        context['others'] = others
        print round(100 - client_cancelled_percent - signature_not_obtained_percent - signature_obtained_percent) 
        context['client_cancelled'] = round(client_cancelled_percent,2)
        print client_cancelled_percent
        context['total_cases_count'] = total_cases_count
        context['signature_obtained'] = round(signature_obtained_percent,2)
        context['signature_not_obtained'] = round(signature_not_obtained_percent,2)

        case_status_closed = total_cases.filter(status = "Closed")
        case_status_client_cancelled = total_cases.filter(status = "Client cancelled")
        total_cases_for_case_status_donut  = total_cases.count() - case_status_closed.count() - case_status_client_cancelled.count()
        case_status_inactive = total_cases.filter(status = "Inactive")
        case_status_in_progress = total_cases.filter(status = "In progress")
        case_status_called_and_texted = total_cases.filter(status = "Called and texted")
        case_status_client_contacted  = total_cases.filter(status = "Client contacted")
        case_status_client_meeting_set  = total_cases.filter(status = "Client meeting set")
        case_status_client_rescheduled = total_cases.filter(status = "Client rescheduled")
        case_signature_obtained  = total_cases.filter(status = "Signature obtained")
        case_status_signature_not_obtained  = total_cases.filter(status = "Signature not obtained")

        context['total_cases_for_case_status_donut'] = total_cases_for_case_status_donut
        if total_cases_for_case_status_donut is not 0:
            if case_status_inactive.count() == 0:
                context['case_status_inactive'] = 0
            else:
                context['case_status_inactive']  = round( (float(case_status_inactive.count() * 100) / total_cases_for_case_status_donut) ,2)
            if case_status_in_progress.count() == 0:
                context['case_status_in_progress'] = 0
            else:
                context['case_status_in_progress']  = round( (float(case_status_in_progress.count() * 100) / total_cases_for_case_status_donut) ,2)
            
            if case_status_called_and_texted.count() == 0:
                context['case_status_called_and_texted'] = 0
            else:
                context['case_status_called_and_texted']  = round( (float(case_status_called_and_texted.count() * 100) / total_cases_for_case_status_donut) ,2)
            
            if case_status_client_contacted.count() == 0:
                context['case_status_client_contacted'] = 0
            else:
                context['case_status_client_contacted']  = round( (float(case_status_client_contacted.count() * 100) / total_cases_for_case_status_donut) ,2)
            
            if case_status_client_meeting_set.count() == 0:
                context['case_status_client_meeting_set'] = 0
            else:
                context['case_status_client_meeting_set']  = round( (float(case_status_client_meeting_set.count() * 100) / total_cases_for_case_status_donut) ,2)
            
            if case_status_client_rescheduled.count() == 0:
                context['case_status_client_rescheduled'] = 0
            else:
                context['case_status_client_rescheduled']  = round( (float(case_status_client_rescheduled.count() * 100) / total_cases_for_case_status_donut) ,2)
            # context['case_status_client_cancelled']  = round( (float(case_status_client_cancelled.count() * 100) / total_cases_for_case_status_donut) ,2)
            
            if case_signature_obtained.count() == 0:
                context['case_signature_obtained'] = 0
            else:
                context['case_signature_obtained']  = round( (float(case_signature_obtained.count() * 100) / total_cases_for_case_status_donut) ,2)
            
            if case_status_signature_not_obtained.count() == 0:
                context['case_status_signature_not_obtained'] = 0
            else:
                context['case_status_signature_not_obtained']  = round( (float(case_status_signature_not_obtained.count() * 100) / total_cases_for_case_status_donut) ,2)
            # context['case_status_closed']  = round( (case_status_closed.count() * 100 / total_cases_count) ,2)

        payment_paid_and_closed = total_cases.filter(is_investigator_paid = True)
        payment_invoice_generated_but_not_paid = total_cases.filter(Q(is_investigator_paid = False) & ~Q(invoice = None))
        payment_invoice_sent_but_not_paid = total_cases.filter(Q(is_investigator_paid = False) & Q(invoice = None) & (Q(is_invoice_mailed = True)|Q(is_invoice_as_csv_mailed = True)))
        payment_closed_but_no_invoice = total_cases.filter(Q(is_investigator_paid = False) & Q(invoice = None) & Q(is_invoice_mailed = False) & Q(is_invoice_as_csv_mailed = False) & Q(status = "Closed") )
        payment_in_progress = total_cases.filter(Q(is_investigator_paid = False) & Q(invoice = None) & Q(is_invoice_mailed = False) & Q(is_invoice_as_csv_mailed = False) & ~Q(status = "Closed") )
        context["payment_paid_and_closed"] = round( (float(payment_paid_and_closed.count() * 100) / total_cases.count()) ,2)
        context["payment_invoice_generated_but_not_paid"] = round( (float(payment_invoice_generated_but_not_paid.count() * 100) / total_cases.count()) ,2)
        context["payment_invoice_sent_but_not_paid"] = round( (float(payment_invoice_sent_but_not_paid.count() * 100) / total_cases.count()) ,2)
        context["payment_closed_but_no_invoice"] = round( (float(payment_closed_but_no_invoice.count() * 100) / total_cases.count()) ,2)
        context["payment_in_progress"] = round( (float(payment_in_progress.count() * 100) / total_cases.count()) ,2)


        cases_added = []
        cases_closed = []
        dates = []
        date = timezone.localtime(timezone.now()).date() - timedelta(days=31)
        
        for day in range(0, 32):
            current_date = date + timedelta(days=day)
            next_date = date + timedelta(days=day + 1)
            cases_on_current_date = total_cases.filter(created_at__gte = current_date).filter(created_at__lt = next_date)
            cases_added.append(cases_on_current_date.count())
            dates.append(current_date)
        
        date = timezone.localtime(timezone.now()).date() - timedelta(days=31)
        for day in range(0, 32):
            current_date = date + timedelta(days=day)
            next_date = date + timedelta(days=day + 1)
            cases_closed_on_current_date = total_cases.filter(closing_date__gte = current_date).filter(closing_date__lt = next_date)
            cases_closed.append(cases_closed_on_current_date.count())
        
        # context['cases_added_closed'] = zip(dates, cases_added, cases_closed)
        context['cases_added'] = zip(dates, cases_added)
        context['cases_closed'] = zip(dates, cases_closed )
        

    return render(request, 'law_firm/dashboard.html',context)

def create_payment_profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')
    context = dict()
    customer_profile = None
    context["secondary_payment_method"] = ""
    context["primary_payment_method"] = ""
    if law_firm.is_customer_profile_created:
        context["payment_type_selected"] = "automatic"
        try:
            customer_profile = CustomerProfile.objects.get(law_firm = law_firm)
        except:
            print "No customer profile found"
        
        context["customer_profile"] = customer_profile
        context["secondary_payment_method"] = ""
        context["primary_payment_method"] = ""

        customer_profile_id = str(customer_profile.auth_customer_profile_id)
        if law_firm.is_payment_profile_created:
            if (customer_profile.primary_payment_method == "credit-card"):
                primary_payment_profile_id = str(customer_profile.primary_payment_profile_id)
                #get customer credit card profile
                customerCreditCardNumber,customerCreditCardExpiration = get_customer_profile_credit_card(customer_profile_id,primary_payment_profile_id)
                print (customerCreditCardExpiration)
                print (customerCreditCardNumber)
                customerCreditCardExpiration = [str(customerCreditCardExpiration)[i:i+2] for i in range(0, len(str(customerCreditCardExpiration)), 2)]
                customerCreditCardNumber = [str(customerCreditCardNumber)[i:i+4] for i in range(0, len(str(customerCreditCardNumber)), 4)]
                print (customerCreditCardNumber)
                customerCreditCardNumberIndex1 = customerCreditCardNumber[0]
                customerCreditCardNumberIndex2 = customerCreditCardNumber[1]
                context["primary_payment_method"] = customer_profile.primary_payment_method
                context['credit_card_number'] = "XXXX-XXXX-" + customerCreditCardNumberIndex1 + "-" + customerCreditCardNumberIndex2
                context['expiration_month'] = customerCreditCardExpiration[0]
                context['expiration_year'] = "XX" + customerCreditCardExpiration[1]
            
            if customer_profile.secondary_payment_method == "bank-account":
                secondary_payment_profile_id = str(customer_profile.secondary_payment_profile_id)
                customerAccountNumber,customerBankRoutingNumber,customerNameOnAccount,customerBankAccountType = get_customer_profile_ACH(customer_profile_id,secondary_payment_profile_id)
                context["secondary_payment_method"] = customer_profile.secondary_payment_method
                context['account_type'] = customerBankAccountType
                context['account_number'] = customerAccountNumber
                context['routing_number'] = customerBankRoutingNumber
                context['name_in_bank_account'] = customerNameOnAccount

    else:    
        context["payment_type_selected"] = "non-selected"

    context["law_firm"]  = law_firm
    if request.POST:
        if "context" in request.POST and request.POST["context"] == "create-new-customer-profile":
            # create new porfile
            customer_name = request.POST["name"]
            customer_email = request.POST["email"]
              
            # Checking the payment type
            if "payment-type-context" in request.POST and request.POST["payment-type-context"]  == "automatic":
                
                # if automatic
                payment_type = request.POST["payment-type"]
                # law_firm.payment_type = payment_type
                # law_firm.save()
                
                #Checking payment by
                if "payment-by-context" in request.POST and request.POST["payment-by-context"]  == "credit-card":
                    
                    # if credit card
                    payment_by = request.POST["payment-by"]
                    invoice_recipients = request.POST["alternative-emails-credit-card"]
                    customer_credit_card_number = request.POST["card-number"]
                    customer_credit_card_number = customer_credit_card_number.replace("-","")
                    customer_credit_card_expiration_month = request.POST["expiration-month"]
                    customer_credit_card_expiration_year = request.POST["expiration-year"]
                    customer_credit_card_expiration = customer_credit_card_expiration_year +"-"+ customer_credit_card_expiration_month

                    # Check if a customer profile exists for this law firm
                    if customer_profile is None:
                        try:
                            customerProfileResponse = createCustomerProfile(customer_name,customer_email)
                        except Exception as ex:
                            print ex
                            return Exception ("Error creating customer profile")
                        if customerProfileResponse.messages.resultCode=="Ok":
                            auth_customer_profile_id = customerProfileResponse.customerProfileId
                            new_customer_profile = CustomerProfile(law_firm=law_firm,auth_customer_profile_id=auth_customer_profile_id)
                            new_customer_profile.save()

                            law_firm.is_customer_profile_created = True
                            law_firm.save()
                            # Create a credit card payment profile
                            try:
                                createCreditCardResponse = createCreditCardProfile(auth_customer_profile_id,customer_credit_card_number,customer_credit_card_expiration)
                            except Exception as ex:
                                print ex
                                return Exception ("Error creating payment profile")
                            if createCreditCardResponse.messages.resultCode=="Ok":
                                new_customer_profile.primary_payment_profile_id = createCreditCardResponse.customerPaymentProfileId
                                new_customer_profile.primary_payment_method = "credit-card"
                                new_customer_profile.save()
                                law_firm.is_payment_profile_created = True
                                law_firm.invoice_recipients = invoice_recipients
                                law_firm.save()
                                return HttpResponseRedirect('/law-firm/create-payment-profile/')
                            else:
                                context['error'] = createCreditCardResponse.messages.message[0]['text'].text
                                return render(request,'law_firm/create_payment_profile.html',context)
                        else:
                            context['error'] = customerProfileResponse.messages.message[0]['text'].text
                            return render(request,'law_firm/create_payment_profile.html',context)
                    else:
                        auth_customer_profile_id = customer_profile.auth_customer_profile_id
                        try:
                            # Create a credit card payment profile
                            createCreditCardResponse = createCreditCardProfile(auth_customer_profile_id,customer_credit_card_number,customer_credit_card_expiration)
                        except Exception as ex:
                            print ex
                            return Exception ("Error creating payment profile")
                        if createCreditCardResponse.messages.resultCode=="Ok":
                            customer_profile.primary_payment_profile_id = createCreditCardResponse.customerPaymentProfileId
                            customer_profile.primary_payment_method = "credit-card"
                            customer_profile.save()
                            law_firm.is_payment_profile_created = True
                            law_firm.invoice_recipients = invoice_recipients
                            law_firm.save()
                            return HttpResponseRedirect('/law-firm/create-payment-profile/')
                        else:
                            context['error'] = createCreditCardResponse.messages.message[0]['text'].text
                            return render(request,'law_firm/create_payment_profile.html',context)
                else:
                    
                    # if bank account
                    payment_by = request.POST["payment-by"]
                    invoice_recipients = request.POST["alternative-emails-bank-account"]
                    customer_bank_account_type = request.POST["account_type"]
                    customer_bank_account_number = request.POST["account-number"]
                    customer_bank_account_routing_number = request.POST["routing-number"]
                    customer_bank_account_name = request.POST["name-in-bank-account"]

                    # Check if a customer profile exists for this law firm
                    if customer_profile is None:
                        try:
                            customerProfileResponse = createCustomerProfile(customer_name,customer_email)
                        except Exception as ex:
                            print ex
                            return Exception ("Error creating customer profile")
                        if customerProfileResponse.messages.resultCode=="Ok":
                            auth_customer_profile_id = customerProfileResponse.customerProfileId
                            new_customer_profile = CustomerProfile(law_firm=law_firm,auth_customer_profile_id=auth_customer_profile_id)
                            new_customer_profile.save()

                            law_firm.is_customer_profile_created = True
                            law_firm.save()
                            # Create a ACH payment profile
                            try:
                                createACHResponse = createACHProfile(auth_customer_profile_id,customer_bank_account_type,customer_bank_account_number,customer_bank_account_routing_number,customer_bank_account_name)
                            except Exception as ex:
                                print ex
                                return Exception ("Error creating payment profile")
                            if createACHResponse.messages.resultCode=="Ok":
                                new_customer_profile.secondary_payment_profile_id = createACHResponse.customerPaymentProfileId
                                new_customer_profile.secondary_payment_method = "bank-account"
                                new_customer_profile.save()
                                law_firm.is_payment_profile_created = True
                                law_firm.invoice_recipients = invoice_recipients
                                law_firm.save()
                                return HttpResponseRedirect('/law-firm/create-payment-profile/')
                            else:
                                context['error'] = createACHResponse.messages.message[0]['text'].text
                                return render(request,'law_firm/create_payment_profile.html',context)
                        else:
                            context['error'] = customerProfileResponse.messages.message[0]['text'].text
                            return render(request,'law_firm/create_payment_profile.html',context)
                    else:
                        auth_customer_profile_id = customer_profile.auth_customer_profile_id
                        # Create a ACH payment profile
                        try:
                            createACHResponse = createACHProfile(auth_customer_profile_id,customer_bank_account_type,customer_bank_account_number,customer_bank_account_routing_number,customer_bank_account_name)
                        except Exception as ex:
                            print ex
                            raise Exception("Error creating payment profile")
                        if createACHResponse.messages.resultCode=="Ok":
                            customer_profile.secondary_payment_profile_id = createACHResponse.customerPaymentProfileId
                            customer_profile.secondary_payment_method = "bank-account"
                            customer_profile.save()
                            law_firm.is_payment_profile_created = True
                            law_firm.invoice_recipients = invoice_recipients
                            law_firm.save()
                            return HttpResponseRedirect('/law-firm/create-payment-profile/')
                        else:
                            context['error'] = createACHResponse.messages.message[0]['text'].text
                            return render(request,'law_firm/create_payment_profile.html',context)            
            else:
                
                # if manual
                payment_type = "manual"
        
        elif "context" in request.POST and request.POST["context"] == "edit-customer-profile":
            
            print("edit")

            # if editing details 
            customer_name = request.POST["name"]
            customer_email = request.POST["email"]
            
            # Checking the payment type
            if "payment-type-context" in request.POST and request.POST["payment-type-context"]  == "automatic":
                print "automatic"
                # if automatic
                payment_type = request.POST["payment-type"]
                law_firm.payment_type = payment_type
                law_firm.save()
                
                #Checking payment by
                if "payment-by-context" in request.POST and request.POST["payment-by-context"]  == "credit-card":
                    print "credit"
                    # if credit card
                    invoice_recipients = request.POST["alternative-emails-credit-card"]
                    law_firm.invoice_recipients = invoice_recipients
                    law_firm.save()
                    payment_by = request.POST["payment-by"]
                    customer_credit_card_number = request.POST["card-number"]
                    customer_credit_card_number = customer_credit_card_number.replace("-","")
                    customer_credit_card_expiration_month = request.POST["expiration-month"]
                    customer_credit_card_expiration_year = request.POST["expiration-year"]
                    customer_credit_card_expiration = customer_credit_card_expiration_year +"-"+ customer_credit_card_expiration_month
                    
                    try:
                        #Create credit card payment profile
                        UpdateResponse = updateCreditCardProfile(customer_profile.auth_customer_profile_id,customer_profile.primary_payment_profile_id,customer_credit_card_number,customer_credit_card_expiration)
                    except Exception as ex:
                        print ex
                        return Exception ("Error updating credit card")
                    #Check response status
                    if UpdateResponse.messages.resultCode == "Ok":
                        print "Here"
                        #Delete old payment profile
                        customer_profile = CustomerProfile.objects.get(law_firm=law_firm)
                        try:
                            deleteResponse = deletePaymentProfile(customer_profile.auth_customer_profile_id,customer_profile.primary_payment_profile_id)
                        except Exception as ex:
                            print ex
                            return Exception ("Error deleting existing payment profile")
                        if deleteResponse.messages.resultCode == "Ok":
                            print "Deleted"
                            auth_customer_profile_id = UpdateResponse.customerProfileId
                            payment_profile_id = UpdateResponse.customerPaymentProfileId
                            customer_profile.auth_customer_profile_id = UpdateResponse.customerProfileId
                            customer_profile.primary_payment_profile_id = UpdateResponse.customerPaymentProfileId
                            customer_profile.primary_payment_method = payment_by
                            customer_profile.save()
                            print "Updated Credit Card"
                            return HttpResponseRedirect('/law-firm/create-payment-profile/')
                        else:
                            # If the old payment profile was not deleted then still update the payment profile id with new id
                            auth_customer_profile_id = UpdateResponse.customerProfileId
                            payment_profile_id = UpdateResponse.customerPaymentProfileId
                            customer_profile.auth_customer_profile_id = UpdateResponse.customerProfileId
                            customer_profile.primary_payment_profile_id = UpdateResponse.customerPaymentProfileId
                            customer_profile.primary_payment_method = payment_by
                            customer_profile.save()
                            print "Updated Credit Card but not deleted the old one"
                            return HttpResponseRedirect('/law-firm/create-payment-profile/')
                    else:
                        print ("Error Updating CC")
                        context['error'] = UpdateResponse.messages.message[0]['text'].text
                        return render(request,'law_firm/create_payment_profile.html',context)
                else:
                    # if bank account
                    
                    invoice_recipients = request.POST["alternative-emails-bank-account"]
                    law_firm.invoice_recipients = invoice_recipients
                    law_firm.save()
                    payment_by = request.POST["payment-by"]
                    customer_bank_account_type = request.POST["account_type"]
                    customer_bank_account_number = request.POST["account-number"]
                    customer_bank_account_routing_number = request.POST["routing-number"]
                    name_in_bank_account = request.POST["name-in-bank-account"]
                    
                    #Create ACH payment profile
                    try:
                        updateResponse = updateACHProfile(customer_profile.auth_customer_profile_id,customer_profile.secondary_payment_profile_id,customer_bank_account_type,customer_bank_account_number,customer_bank_account_routing_number,name_in_bank_account)
                    except Exception as ex:
                        print ex
                        return Exception ("Error updating bank account")
                    print updateResponse
                    # Check response status
                    if updateResponse.messages.resultCode == "Ok":
                        #Delete customer payment profile
                        try:
                            deleteResponse = deletePaymentProfile(customer_profile.auth_customer_profile_id,customer_profile.secondary_payment_profile_id)
                        except Exception as ex:
                            print ex
                            return Exception ("Error deleting existing payment profile")
                        if deleteResponse.messages.resultCode == "Ok":
                            print "Here"
                            auth_customer_profile_id = updateResponse.customerProfileId
                            payment_profile_id = updateResponse.customerPaymentProfileId
                            customer_profile.auth_customer_profile_id = auth_customer_profile_id
                            customer_profile.secondary_payment_profile_id = payment_profile_id
                            customer_profile.secondary_payment_method = payment_by
                            customer_profile.save()
                            print "Updated ACH"
                            return HttpResponseRedirect('/law-firm/create-payment-profile/')
                        else:
                            print "Payment profile not deleted"
                            auth_customer_profile_id = updateResponse.customerProfileId
                            payment_profile_id = updateResponse.customerPaymentProfileId
                            customer_profile.auth_customer_profile_id = auth_customer_profile_id
                            customer_profile.secondary_payment_profile_id = payment_profile_id
                            customer_profile.secondary_payment_method = payment_by
                            customer_profile.save()
                            print "Updated ACH"
                            return HttpResponseRedirect('/law-firm/create-payment-profile/')
                    else:
                        print ("Error Updating ACH")
                        context['error'] = updateResponse.messages.message[0]['text'].text
                        return render(request,'law_firm/create_payment_profile.html',context)
            else:
                
                # if manual
                payment_type = request.POST["payment-type"]
    return render(request, 'law_firm/create_payment_profile.html', context)

def cases_to_be_charged(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    cases = Case.objects.filter(law_firm=law_firm).filter(is_marked_for_payment = True ).filter(has_law_firm_paid = False).filter(is_dispute_raised = False)
    context['cases'] = cases

    if request.POST and 'context' in request.POST and request.POST['context'] == "single-dispute":

        if 'case_id' in request.POST and request.POST['case_id'] != "":
            case_id = request.POST['case_id']
            dispute_description = request.POST['dispute-reason']
            case = Case.objects.get(pk=case_id)
            case.is_dispute_raised = True
            case.dispute_description = dispute_description
            case.save()
            send_email_on_dispute(request,case,law_firm)
            
            print dispute_description
            print case_id
            print "-- Single dispute raised --" 

    elif request.POST and 'context' in request.POST and request.POST['context'] == "combined-dispute":
        print "--Combined dispute raised --"
        if 'case_ids' in request.POST and request.POST['case_ids'] != "":
            try:
                case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
                dispute_description = request.POST['dispute-reason']
                print dispute_description
            except:
                print "No value for case_ids or case_ids not found in request.POST"

            for case_id in case_ids:
                print case_id
                case = Case.objects.get(pk=case_id)
                case.is_dispute_raised = True
                case.dispute_description = dispute_description
                case.save()
            send_email_combined_on_dispute(request,case_ids,law_firm)



    return render(request, 'law_firm/cases_to_be_charged.html', context)

# def charge_law_firm(request):
#     if not request.user.is_authenticated():
#         return HttpResponseRedirect('/')

#     try:
#         law_firm = LawFirm.objects.get(user=request.user)
#     except:
#         return HttpResponseRedirect('/')
#     response = charge_law_firm_daily()
#     return HttpResponse(response)

def charged_cases(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        law_firm = LawFirm.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()    
    cases = Case.objects.filter(law_firm=law_firm).filter(has_law_firm_paid=True)
    context['cases'] = cases

    if request.POST and 'context' in request.POST and request.POST['context'] == "single-dispute":

        if 'case_id' in request.POST and request.POST['case_id'] != "":
            case_id = request.POST['case_id']
            dispute_description = request.POST['dispute-reason']
            case = Case.objects.get(pk=case_id)
            case.is_dispute_raised = True
            case.dispute_description = dispute_description
            case.save()
            send_email_on_dispute(request,case,law_firm)
            print case_id
            
            print dispute_description
            print "-- Single dispute raised --" 
    elif request.POST and 'context' in request.POST and request.POST['context'] == "combined-dispute":
        print "--Combined dispute raised --"
        if 'case_ids' in request.POST and request.POST['case_ids'] != "":
            try:
                case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
            except:
                print "No value for case_ids or case_ids not found in request.POST"
                
            dispute_description = request.POST['dispute-reason']
            print dispute_description
            for case_id in case_ids:
                print case_id
                case = Case.objects.get(pk=case_id)
                case.is_dispute_raised = True
                case.dispute_description = dispute_description
                case.save()
            send_email_combined_on_dispute(request,case_ids,law_firm)

    return render(request,'law_firm/charged_cases.html',context)


def send_email_on_dispute(request,case,law_firm):
    import json
    import requests

    longUrl = 'http://' + request.META['HTTP_HOST'] + '/master-broker/pending-receivables/'
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
    params = json.dumps({'longUrl': longUrl})
    response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

    
    shortened_url = longUrl
    try:
        shortened_url =  response.json()['id']
    except:
        pass

    
    email = settings.INVOICE_HARDCODED_TO_EMAIL
    
    try:
        msg =  EmailMessage('Dispute Raised', 'Hi David,<br><br>' + law_firm.name + ' has raised dispute for the cases - ' + case.name +'. Please visit <a href= "http://' + request.META['HTTP_HOST'] + '/master-broker/pending-receivables/">pending receivables</a> and view the details. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>',
            'dispute@rapidsignnow.com', [email])
        msg.content_subtype = "html"
        msg.send()
    except:
        pass

def send_email_combined_on_dispute(request,case_ids,law_firm):
    import json
    import requests

    longUrl = 'http://' + request.META['HTTP_HOST'] + '/master-broker/pending-receivables/'
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
    params = json.dumps({'longUrl': longUrl})
    response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

    
    shortened_url = longUrl
    try:
        shortened_url =  response.json()['id']
    except:
        pass

    case_names = ""
    for case_id in case_ids:
        case = Case.objects.get(pk=case_id)
        case_names = case_names + case.name + ", "
    case_names = case_names[:-2]
    
    email = settings.INVOICE_HARDCODED_TO_EMAIL
    
    try:
        msg =  EmailMessage('Dispute Raised', 'Hi David,<br><br>' + law_firm.name + ' has raised dispute for the cases - ' + case_names +'. Please visit <a href= "http://' + request.META['HTTP_HOST'] + '/master-broker/pending-receivables/">pending receivables</a> and view the details. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>',
            'dispute@rapidsignnow.com', [email])
        msg.content_subtype = "html"
        msg.send()
    except:
        pass