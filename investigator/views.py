from django.shortcuts import get_object_or_404, render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from operator import __or__ as OR
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt


from xhtml2pdf import pisa
from django.template.loader import get_template

import ast
import json
import requests
import StringIO
import datetime
import random
import mimetypes 
import magic  
import urllib
from datetime import timedelta
from django.utils import timezone 
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from investigator.models import Investigator
from status_update.models import StatusUpdate, CaseAcceptanceUpdate
from case.models import Case
from attached_document.models import AttachedDocument
from document.models import Document
from law_firm.models import LawFirm
from broker.models import Broker
from master_broker.models import MasterBroker

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
@login_required(login_url='/')
@permission_required('investigator.can_view_investigator',raise_exception=True)
def change_password(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
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
                print "Password successfully changed"
                return JsonResponse({'success':"true"})
            else:
                print "Password check failed"
                context["error"] = "Your current password is incorrect"
                return JsonResponse({'success':"false"})
        else:
            print "fields are bad "
            return JsonResponse({'success':"false"})

    print "Not a post request"    
    return render(request, 'investigator/change_password.html', context)



def get_notifications(investigator):

    unread_statuses = StatusUpdate.objects.filter(case__investigator=investigator).order_by('-timestamp')[:15]
    status_notifications = []
    unread = 0

    for status in unread_statuses:
        notification = dict()

        notification['status_id'] = status.pk
        notification['case_id'] = status.case.pk
        notification['case_name'] = status.case.name
        if status.updated_by == 'MB':
            notification['broker'] = status.user.first_name + ' ' + status.user.last_name
        elif status.updated_by == 'BR':
            notification['broker'] = status.user.first_name + ' ' + status.user.last_name
        else:
            notification['broker'] = 'You'
        notification['status'] = status.status
        notification['timestamp'] = status.timestamp
        notification['read'] = status.read_by_investigator
        notification['type'] = 'status'

        if not status.read_by_investigator:
            unread += 1

        status_notifications.append(notification)

    notifications = status_notifications

    return {
        'entries': notifications,
        'unread': unread
    }

@login_required(login_url='/')
@permission_required('investigator.can_view_investigator',raise_exception=True)
def assigned_cases(request):

    # if not request.user.is_authenticated():
    #     return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    law_firms = []

    if len(Case.objects.filter(investigator=investigator, status='Inactive')) > 1:
        context['pending_cases'] = Case.objects.filter(investigator=investigator, status='Inactive')[0:2]
        law_firms.append(context['pending_cases'][0].law_firm)
        law_firms.append(context['pending_cases'][1].law_firm)
    elif Case.objects.filter(investigator=investigator, status='Inactive').exists():
        context['pending_cases'] = [Case.objects.filter(investigator=investigator, status='Inactive')[0]]
        law_firms.append(context['pending_cases'][0].law_firm)

    if Case.objects.filter(investigator=investigator).exclude(status='Inactive').exclude(status='Closed').exists():
        context['working_case'] = Case.objects.filter(investigator=investigator).exclude(status='Inactive').exclude(status='Closed')[0]
    
    
    attached_documents = AttachedDocument.objects.all()
    context['attached_documents'] = attached_documents
    context['law_firms'] = law_firms
    context['notifications'] = get_notifications(investigator)

    if request.POST.get('context') == 'download-document':
        document_id = request.POST['document-id']
        response = download_doc(request,document_id)
        return response

    return render(request, 'investigator/assigned_cases.html', context)

@login_required(login_url='/')
@permission_required('investigator.can_view_investigator',raise_exception=True)
def closed_cases(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['closed_cases'] = Case.objects.filter(investigator=investigator, status='Closed')
    context['notifications'] = get_notifications(investigator)

    return render(request, 'investigator/closed_cases.html', context)

@login_required(login_url='/')
@permission_required('investigator.can_view_investigator',raise_exception=True)
def all_cases(request):
    import datetime
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['cases'] = []

    cases = None
    # cases = Case.objects.filter().order_by('-pk')
    # print (cases)
    cases = Case.objects.filter(investigator = investigator)
    law_firms = LawFirm.objects.all()

    # paginator = Paginator(cases, 15) # Show 25 contacts per page

    # page = request.GET.get('page')
    # try:
    #     cases = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     cases = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     cases = paginator.page(paginator.num_pages)
    # for case in cases:
    #     case.final_status =  get_case_final_status(case)
    #     case.amount_billed_to_law_firm = case.get_law_firm_price()
        # if not case.status_mail: 
        #     status = list(StatusUpdate.objects.filter(case=case).order_by("-created_at"))[0]
        #     if status.user == master_broker.user:
        #         status_mail(case,request)
    
    # context['cases'] = cases
    
    brokers = Broker.objects.all()
    master_brokers = MasterBroker.objects.all()
    
    
    context['brokers'] = brokers
    context['master_brokers'] = master_brokers
    context['notifications'] = get_notifications(investigator)

    context['law_firms'] = law_firms
    cases_by_broker = []
    cases_by_master_broker = []


    if (request.method == 'GET') or ((request.method == 'POST') and ('context' in request.POST) and (request.POST['context'] == 'remove-filters')):
        # If filters were removed
        cases = Case.objects.filter(investigator = investigator).order_by('-pk')
    elif ((request.method == 'POST') and ('context' in request.POST) and (request.POST['context'] == 'apply-filters')):
        
        # If we have any filters applied
        if 'from' in request.POST and request.POST['from'] != '':
            from_date = request.POST.get('from')
            from_components = from_date.split('/')
            from_date = datetime.datetime(int(from_components[2]), int(from_components[0]), int(from_components[1]))
            cases = cases.filter(created_at__gte=from_date)

            context['from'] = request.POST['from']
            context['is_filter_applied'] = 1
            
        

        if 'to' in request.POST and request.POST['to'] != '':
            to_date = request.POST.get('to')
            to_components = to_date.split('/')
            to_date = datetime.datetime(int(to_components[2]), int(to_components[0]), int(to_components[1]))
            cases = cases.filter(created_at__lt=to_date)
            context['to'] = request.POST['to']
            context['is_filter_applied'] = 1


        if 'law-firm' in request.POST and request.POST['law-firm'] != '':
            law_firm_id = request.POST['law-firm']
            law_firm = LawFirm.objects.get(pk=int(law_firm_id))
            print "The selected_lawfirm is "
            print law_firm_id
            context['selected_firm_id'] = law_firm_id
            cases = cases.filter(law_firm = law_firm)
            context['selected_firm'] = law_firm_id
            context['is_filter_applied'] = 1
        

        if 'status' in request.POST and request.POST['status'] != '':
            status = request.POST['status']
            cases = cases.filter(status = status)
            context['selected_status'] = request.POST['status']
            context['is_filter_applied'] = 1

        q_array = []
        
        if 'broker' in request.POST and request.POST['broker'] != '':
            broker_id = request.POST['broker']
            broker = Broker.objects.get(pk=broker_id)
            # cases_by_broker = cases.filter(created_by = broker)

            q_array.append(Q(created_by = broker))

            # cases = cases.filter(created_by = broker)
            # case_by_broker = cases
            context['selected_broker'] = broker_id
            context['is_filter_applied'] = 1   

        if 'master-broker' in request.POST and request.POST['master-broker'] !='':  
            master_broker_id = request.POST['master-broker']
            master_broker = MasterBroker.objects.get(pk=master_broker_id)

            context['selected_master_broker'] = master_broker_id
            cases_by_master_broker = cases.filter(created_by_master = master_broker)
            q_array.append(Q(created_by_master = master_broker))

            
            context['is_filter_applied'] = 1   
        
        
        if len(q_array):
            cases = cases.filter(reduce(OR, q_array))  

        if 'marked-case' in request.POST and request.POST['marked-case'] != '':
                cases = cases.filter(is_attention_required = True)
                context['is_marked_case'] = 1
                context['is_filter_applied'] = 1
                # context['next_page_url'] += 'marked-case=on&'

        # cases = cases.order_by('-pk')
        # for case in cases:
        #     print (case.name)
    for case in cases:
        case.final_status =  get_case_final_status(case)
        case.amount_paid_to_investigator = case.get_investigator_price()

    q_array_status = []
    for case in cases:
        status_updates = StatusUpdate.objects.filter(case = case).order_by('-timestamp')[0:1]
        for status in status_updates:
            q_array_status.append(Q(pk = status.pk))
    try:
        context['status_updates'] = StatusUpdate.objects.filter(reduce(OR, q_array_status))
    except:
        print "No case"
        
    context['cases'] = cases
    return render(request, 'investigator/all_cases.html', context)
def case_details(request, case_id):

    try:
        case_instance = Case.objects.get(pk=case_id)
    except:
        raise Http404

    investigator = None

    if case_instance.investigator is not None and request.GET and 'key' in request.GET:
        key = request.GET['key']
        if key != case_instance.random_string:
            return HttpResponseRedirect('/')

        investigator = case_instance.investigator
        investigator.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, investigator.user)

    elif request.user.is_authenticated():

        try:
            investigator = Investigator.objects.get(user=request.user)
        except:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')

    if case_instance.investigator.id != investigator.id:
        raise SuspiciousOperation("Invalid request; You do not have access to this case")
    attached_documents = AttachedDocument.objects.filter(case = case_instance)
    context = dict()
    context['case'] = case_instance
    context['amount_paid_to_investigator'] = case_instance.get_investigator_price()
    context['law_firms'] = [case_instance.law_firm]
    context['countries'] = countries
    context['status_updates'] = StatusUpdate.objects.filter(case=case_instance).order_by('-timestamp')
    context['notifications'] = get_notifications(investigator)
    context['attached_documents'] = attached_documents
    client_mobile_phone = case_instance.client_mobile_phone.replace('-', '').replace(' ', '')
    context['client_mobile_phone'] = client_mobile_phone
    client_home_phone = case_instance.client_home_phone.replace('-', '').replace(' ', '')
    context['client_home_phone'] = client_home_phone
    # Disable status updation by investigator if case is closed
    if(str(case_instance.status).lower() == 'closed' ):
        context['is_case_closed'] = True
    else:
        context['is_case_closed'] = False
    if case_instance.is_investigator_paid:
        context['is_case_closed'] = True
    
    if (str(case_instance.status).lower() == 'duplicate delete') :
        context['is_case_closed'] = True

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

    return render(request, 'investigator/case_details.html', context)

@login_required(login_url='/')
@permission_required('investigator.can_view_investigator',raise_exception=True)
def case_details_closed(request, case_id):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    try:
        case_instance = Case.objects.get(pk=case_id)
    except:
        raise Http404

    context = dict()
    context['case'] = case_instance
    context['law_firms'] = [case_instance.law_firm]
    context['countries'] = countries
    context['status_updates'] = StatusUpdate.objects.filter(case=case_instance).order_by('-timestamp')
    # print context['status_updates']
    context['notifications'] = get_notifications(investigator)
    attached_documents = AttachedDocument.objects.filter(case = case_instance)
    context['attached_documents'] = attached_documents
    client_mobile_phone = case_instance.client_mobile_phone.replace('-', '').replace(' ', '')
    context['client_mobile_phone'] = client_mobile_phone
    client_home_phone = case_instance.client_home_phone.replace('-', '').replace(' ', '')
    context['client_home_phone'] = client_home_phone

    return render(request, 'investigator/case_details_closed.html', context)


def change_status(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
        
    except:
        return HttpResponseRedirect('/')

    
    if not request.POST or 'new_status' not in request.POST or 'case_id' not in request.POST:
        raise SuspiciousOperation('The request did not contain eiter a status or the case id')


    if request.POST['new_status'] == '' or request.POST['case_id'] == '':
        raise SuspiciousOperation('The request did not contain eiter a status or the case id')


    case = None
    case_id = request.POST['case_id']

    try:
        case = Case.objects.get(pk=case_id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


    status = request.POST['new_status']
    
    possible_statuses = ['inactive','in progress','called and texted','client contacted','client meeting set','client rescheduled','client cancelled','signature obtained','signature not obtained']

    if not status.lower() in possible_statuses:
        raise SuspiciousOperation('Not an allowed status')

    extra_info = None
    json_payload = None
    additional_expenses_description = ''
    
    if 'extra_info' in request.POST and request.POST['extra_info']:
        extra_info = request.POST['extra_info']

        if len(extra_info) == 0:
            extra_info = None

    case.status = status

    if status.lower() == 'client cancel':
        case.is_signature_obtained = False
        case.did_investigator_travel = False
        case.number_of_adult_signatures_obtained = 0
        case.number_of_child_signatures_obtained = 0
        if extra_info:
            try:
                json_payload = json.loads(extra_info)
                print json_payload
            
            except:
                raise SuspiciousOperation("Could not parse JSON payload")
                pass

            if "Cancelled by" in json_payload and "Cancellation reason" in json_payload:
                case.cancelled_by =json_payload["Cancelled by"]
                print case.cancelled_by

                case.cancelled_reason_description = json_payload["Cancellation reason"]
                print case.cancelled_reason_description
                case.save()
                
            else:
                raise ValueError('could not find Cancellation reason in Status update')
        
    
    if status.lower() == 'signature obtained':
        case.is_signature_obtained = True
        case.did_investigator_travel = True
        if extra_info:
            try:
                json_payload = json.loads(extra_info)
            except:
                raise SuspiciousOperation("Status update requires a Mileage description, Out of pocket expenses, More Info, no_of_adult_signatures_obtained and no_of_child_signatures_obtained")
                pass    

                

            if "Mileage Description" in json_payload:
                case.no_of_miles_travelled = float(json_payload["Mileage Description"])
            else:
                raise ValueError('could not find Mileage description in Status update')

            if "Out of pocket expenses" in json_payload :
                if float(json_payload["Out of pocket expenses"]) > 0.0:
                    case.additional_expenses = float(json_payload["Out of pocket expenses"])
                    if "More Info" in json_payload and json_payload['More Info']:
                        case.additional_expenses_description = json_payload["More Info"]
                    else:
                        raise ValueError('could not find More Info in Status update')
            else:
                raise ValueError('could not find Mileage description in Status update')

            if "no_of_adult_signatures_obtained" in json_payload:
                case.number_of_adult_signatures_obtained = int(json_payload["no_of_adult_signatures_obtained"])
            else:
                raise ValueError('could not find no_of_adult_signatures_obtained in Status update')
            

            if "no_of_child_signatures_obtained" in json_payload:
                case.number_of_child_signatures_obtained = int(json_payload["no_of_child_signatures_obtained"])
            else:
                raise ValueError('could not find no_of_child_signatures_obtained in Status update')
                            
            if "adult_client_names" in json_payload:
                case.adult_clients = json_payload["adult_client_names"]
            else:
                raise ValueError('cound not find adult_clients in Status update') 
            print case.adult_clients

            if "child_client_names" in json_payload:
                case.child_clients = json_payload["child_client_names"]
            else:
                raise ValueError('cound not find adult_clients in Status update')        
        else:
            raise SuspiciousOperation("Status update requires extra_info")

                     

    if status.lower() == 'signature not obtained':
        case.is_signature_obtained = False
        case.did_investigator_travel = True
        case.number_of_adult_signatures_obtained = 0
        case.number_of_child_signatures_obtained = 0
        if extra_info:
            try:
                json_payload = json.loads(extra_info)
            except:
                raise SuspiciousOperation("Could not parse JSON payload")
                pass
            if "Out of pocket expenses" in json_payload :
                if float(json_payload["Out of pocket expenses"]) > 0.0:
                    case.additional_expenses = float(json_payload["Out of pocket expenses"])
                    if "More Info" in json_payload and json_payload['More Info']:
                        case.additional_expenses_description = json_payload["More Info"]
                    else:
                        raise ValueError('could not find More Info in Status update')
            else:
                raise ValueError('could not find Mileage description in Status update')

            if "Mileage Description" in json_payload:
                case.no_of_miles_travelled = float(json_payload["Mileage Description"])
            else:
                raise ValueError('could not find Mileage description in Status update')

                
           
        else:
            raise SuspiciousOperation("Status update requires extra_info")


    
        
    case.save()

    new_status_update = StatusUpdate(user=investigator.user, status=status, case=case, read_by_broker=False,read_by_master_broker=False,
                                     extra_info=extra_info, updated_by='IN')
    new_status_update.save()

    status_mail(case,request)
    return HttpResponse('')

def status_mail(case,request):
    import json
    import requests

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if case.created_by :
        longUrl = 'http://' + request.META['HTTP_HOST'] + '/broker/case-details/' +str(case.pk) + '/?key=' + case.random_string
        post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
        params = json.dumps({'longUrl': longUrl})
        response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

    
        shortened_url = longUrl
        try:
            shortened_url =  response.json()['id']
        except:
            pass

        

        broker = case.created_by
        print "%s"%broker.user.first_name
        print "%s"%broker.email_one
        print "%s"%broker.phone_number_one
        print "%s"%case.name
        print "%s"%case.status
        phone_number = broker.phone_number_one.replace('-', '').replace(' ', '')

        try:
            msg =  EmailMessage('Status Changed', 'Hi '+ broker.user.first_name +',<br><br> The status of ' + case.name + ' has been changed to ' + case.status +' by ' + investigator.user.first_name +
            ' ' + investigator.user.last_name + '. Please visit <a href= "http://' + request.META['HTTP_HOST'] + '/broker/case-details/' +
              str(case.pk) + '/?key=' + case.random_string + '">http://' + request.META['HTTP_HOST'] + '/broker/case-details/' +
              str(case.pk) + '/?key=' + case.random_string + '</a> and view the details. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>',
            'status@rapidsignnow.com', [broker.email_one])
            msg.content_subtype = "html"
            msg.send()
        except:
            pass
        try:    
            message = twilio_client.api.account.messages.create(to=phone_number,
                                                from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                                                body='The status of ' + case.name + ' has been changed to ' + case.status +' by ' + investigator.user.first_name +
                ' ' + investigator.user.last_name + '. Please visit ' + shortened_url + ' and view the details. ')
            case.status_mail = True 
            case.save()
        except:
            pass

    elif case.created_by_master:
        longUrl = 'http://' + request.META['HTTP_HOST'] + '/master-broker/case-details/' +str(case.pk) + '/?key=' + case.random_string
        post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
        params = json.dumps({'longUrl': longUrl})
        response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

    
        shortened_url = longUrl
        try:
            shortened_url =  response.json()['id']
        except:
            pass

        master_broker = case.created_by_master   
        phone_number = master_broker.phone_number_one.replace('-', '').replace(' ', '')

        try:
            msg =  EmailMessage('Status Changed', 'Hi '+ master_broker.user.first_name +',<br><br> The status of ' + case.name + ' has been changed to ' + case.status +' by ' + investigator.user.first_name +
            ' ' + investigator.user.last_name + '. Please visit <a href= "http://' + request.META['HTTP_HOST'] + '/master-broker/case-details/' +
              str(case.pk) + '/?key=' + case.random_string + '">http://' + request.META['HTTP_HOST'] + '/master-broker/case-details/' +
              str(case.pk) + '/?key=' + case.random_string + '</a> and view the details. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>',
            'status@rapidsignnow.com', [master_broker.email_one])
            msg.content_subtype = "html"
            msg.send()
        except:
            pass      
        try:
            message = twilio_client.api.account.messages.create(to=phone_number,
                                             from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                                             body='The status of ' + case.name + ' has been changed to ' + case.status +' by ' + investigator.user.first_name +
              ' ' + investigator.user.last_name + '. Please visit ' + shortened_url + ' and view the details. ')
            case.status_mail = True 
            case.save()
        except:
            pass
            
def accept_case(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'case_id' not in request.POST:
        return HttpResponseRedirect('/')

    case_id = request.POST['case_id']
    case = Case.objects.get(pk=case_id)

    case.status = 'In progress'
    case.save()

    new_status_update = StatusUpdate(user=investigator.user, status='In progress', case=case, read_by_broker=False)
    new_status_update.save()
    
    new_case_acceptance = CaseAcceptanceUpdate(investigator=investigator, case=case, is_accepted=True,
                                               read_by_broker=False,read_by_master_broker=False)
    new_case_acceptance.save()

    return HttpResponse('')


def decline_case(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'case_id' not in request.POST:
        return HttpResponseRedirect('/')

    case_id = request.POST['case_id']
    case = Case.objects.get(pk=case_id)

    case.investigator = None
    case.save()
    
    new_case_acceptance = CaseAcceptanceUpdate(investigator=investigator, case=case, is_accepted=False,
                                               read_by_broker=False, read_by_master_broker=False)
    new_case_acceptance.save()

    return HttpResponse('')

@login_required(login_url='/')
@permission_required('investigator.can_view_investigator',raise_exception=True)
def my_profile(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['investigator'] = investigator
    try:
        context['languages'] = ast.literal_eval(investigator.languages)
    except:
        pass
    
    context['notifications'] = get_notifications(investigator)

    return render(request, 'investigator/my_profile.html', context)


def mark_as_read(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')
    
    if not request.GET:
        return HttpResponse('')
    
    request_id = request.GET['id']
    request_type = request.GET['type']
    
    if request_type == 'status':
        status_update_instance = StatusUpdate.objects.get(pk=request_id)
        status_update_instance.read_by_investigator = True
        status_update_instance.save()
    
    
    return HttpResponse('')

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

def mark_case(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'case_id' not in request.POST:
        return HttpResponseRedirect('/')

    case_id = request.POST['case_id']
    case = Case.objects.get(pk=case_id)

    if request.POST['mark'] == "mark":
        if case.status == "Closed":
            raise SuspiciousOperation("Invalid request; Cannot mark case as case is closed")
        else:
            case.is_attention_required = True
            case.save()
            import json
            import requests

            if case.created_by :
                longUrl = 'http://' + request.META['HTTP_HOST'] + '/broker/case-details/' +str(case.pk) + '/?key=' + case.random_string
                post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
                params = json.dumps({'longUrl': longUrl})
                response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

                
                shortened_url = longUrl
                try:
                    shortened_url =  response.json()['id']
                except:
                    pass

                
                
                broker = case.created_by
                # print "%s"%investigator.user.first_name
                # print "%s"%investigator.email_one
                # print "%s"%investigator.phone_number_one
                # print "%s"%case.name
                # print "%s"%case.status
                phone_number = broker.phone_number_one.replace('-', '').replace(' ', '')
                
                try:
                    send_mail('Attention Required !', '' + investigator.user.first_name + ' ' + investigator.user.last_name + ' has marked the case ' + case.name +' as attention required which was created by '+ case.created_by.user.first_name +' ' +case.created_by.user.last_name  + '. Please visit http://' + request.META['HTTP_HOST'] + '/broker/case-details/' +
                        str(case.pk) + '/?key=' + case.random_string + ' and view the details. ',
                        'assign@rapidsignnow.com', [broker.email_one],fail_silently=False,)
                except:
                    pass
                
                try:
                    message = twilio_client.api.account.messages.create(to=phone_number,
                                                        from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                                                        body='' + investigator.user.first_name + ' ' + investigator.user.last_name + ' has marked the case ' + case.name +' as attention required which was created by '+ case.created_by.user.first_name +' ' +case.created_by.user.last_name  + '. Please visit' + shortened_url + ' and view the details. ')
                except:
                    pass
                print "case marked"
            
            elif case.created_by_master:
                longUrl = 'http://' + request.META['HTTP_HOST'] + '/master-broker/case-details/' +str(case.pk) + '/?key=' + case.random_string
                post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
                params = json.dumps({'longUrl': longUrl})
                response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

                
                shortened_url = longUrl
                try:
                    shortened_url =  response.json()['id']
                except:
                    pass

                
                
                master_broker = case.created_by_master
                # print "%s"%investigator.user.first_name
                # print "%s"%investigator.email_one
                # print "%s"%investigator.phone_number_one
                # print "%s"%case.name
                # print "%s"%case.status
                phone_number = master_broker.phone_number_one.replace('-', '').replace(' ', '')
                
                try:
                    send_mail('Attention Required !', '' + investigator.user.first_name + ' ' + investigator.user.last_name + ' has marked the case ' + case.name +' as attention required which was created by '+ case.created_by_master.user.first_name +' ' +case.created_by_master.user.last_name  + '. Please visit http://' + request.META['HTTP_HOST'] + '/broker/case-details/' +
                        str(case.pk) + '/?key=' + case.random_string + ' and view the details. ',
                        'assign@rapidsignnow.com', [master_broker.email_one],fail_silently=False,)
                except:
                    pass
                
                try:
                    message = twilio_client.api.account.messages.create(to=phone_number,
                                                        from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                                                        body='' + investigator.user.first_name + ' ' + investigator.user.last_name + ' has marked the case ' + case.name +' as attention required which was created by '+ case.created_by_master.user.first_name +' ' +case.created_by_master.user.last_name  + '. Please visit' + shortened_url + ' and view the details. ')
                except:
                    pass
                print "case marked"
    elif request.POST['mark'] == "unmark":
        case.is_attention_required = False
        case.save()
        print "case unmarked"




    return HttpResponse('')

@csrf_exempt
def handle_incoming_message(request):
    
    try:
        message_sid = request.POST.get('MessageSid', '')
        body = request.POST.get('Body','')
        print (body)
        from_number = request.POST.get('From', '')
        # to_number = request.POST.get('To', '')
        body_part = body.split(" ",1)
        case_id = ""
        for temp in body_part:
            case_id  = temp
            break
        case_instance = Case.objects.get(pk = case_id)
        body = body.replace(case_id + " ","")
        print case_instance.name
        print body
        
        print str(request.META['HTTP_HOST'])

        longUrl = 'http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +str(case_instance.pk) + '/?key=' + str(case_instance.random_string)
        print longUrl
        post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
        params = json.dumps({'longUrl': longUrl})
        response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

    
        shortened_url = longUrl
        try:
            shortened_url =  response.json()['id']
        except:
            pass


        # shortened_url = 'http://staging.rapidsignnow.com/investigator/case-details/' +str(case_instance.pk) + "/"
    except:
        print "Not a message"

    
    
    
    message = ""
    try:
        country_code = from_number[0:2]
        first = from_number[2:5]
        second = from_number[5:8]
        third = from_number[8:12]
        phone_number = str(country_code) + " " + str(first) + "-" +str(second)+ "-" + str(third)
        print phone_number
        investigator = Investigator.objects.get(phone_number_one = phone_number)
        print investigator.user.first_name


        if case_instance.investigator == investigator:
        
            if case_instance.message_id == 1:
                if "1" in body :
                    message = "What time Today? Type " + str(case_instance.pk) + "<space> <Time>"
                    case_instance.message_id = 11
                    case_instance.save()
                elif "0" in body :
                    message = "Can you please give a short answer as to when the appointment will be scheduled? Type "  + str(case_instance.pk) + " <space> <message>"
                    case_instance.message_id = 10
                    case_instance.save()
            elif case_instance.message_id == 10:
                status = case_instance.status
                if status == "Inactive":
                    case_instance.status = "In progress"
                    case_instance.save()
                    extra_info = '{"More info":"'+ body + '"}'
                    new_status_update = StatusUpdate(user=investigator.user, status=case_instance.status, case=case_instance, read_by_broker=False,read_by_master_broker=False,
                                            extra_info=extra_info, updated_by='IN')
                    new_status_update.save()

                else:
                    status = "In progress"
                    case_status = StatusUpdate.objects.filter(case = case_instance).filter(status = status).order_by('-timestamp')[0:1]
                    progress_status = None
                    for status_update in case_status:
                        progress_status = StatusUpdate.objects.get(pk = status_update.pk)
                    progress_status.extra_info = '{"More info":"'+ body + '"}'
                    progress_status.save()

                case_instance.message_id = 12
                case_instance.save()
                message = "Thanks for the response"    
            elif case_instance.message_id == 11:
                if case_instance.status == "Inactive" or case_instance.status == "In progress" or case_instance.status == "Called and texted" or case_instance.status == "Client contacted":
                    case_instance.status = "Client meeting set"
                    case_instance.message_id = 12
                    case_instance.save()
                    extra_info = '{"More info":"'+ body + '"}'
                    new_status_update = StatusUpdate(user=investigator.user, status=case_instance.status, case=case_instance, read_by_broker=False,read_by_master_broker=False,
                                            extra_info=extra_info, updated_by='IN')
                    new_status_update.save()
                else:
                    status = "Client meeting set"
                    status = "In progress"
                    case_status = StatusUpdate.objects.filter(case = case_instance).filter(status = status).order_by('-timestamp')[0:1]
                    progress_status = None
                    for status_update in case_status:
                        progress_status = StatusUpdate.objects.get(pk = status_update.pk)
                    progress_status.extra_info = '{"More info":"'+ body + '"}'
                    progress_status.save()
                    case_instance.message_id = 12
                    case_instance.save()

                message = "Thanks for the response"    
            elif case_instance.message_id == 3:
                if "1" in body:
                    message = "Great, please click HERE " + shortened_url +"  and select signature obtained status so we can get you paid ASAP. Note - Do not share this link to anyone."
                elif "0" in body:
                    message = "Please Click HERE " + shortened_url +" to update current status on case. Note - Do not share this link to anyone."
            elif case_instance.message_id == 4:
                if "1" in body:
                    message = "Great, please click HERE " + shortened_url +" and select signature obtained status so we can get you paid ASAP. Note - Do not share this link to anyone."
                elif "0" in body:
                    message = "Please Click HERE  " + shortened_url +" to update current status on case. Note - Do not share this link to anyone."
                elif "2" in body:
                    message = "Please Click HERE " + shortened_url +" to update current status to client cancalled on case. Note - Do not share this link to anyone."
        else:
            message = "Thanks for the response but you are not assigned to this case."
    except:    
        message = "Thanks for the response but this either is an unregistered number or an invalid message."
    
    try:
        print message
        # print from_number
        response = twilio_client.api.account.messages.create(to=from_number,
                                             from_=settings.TWILIO_NOTIFICATIONS_PHONE_NUMBER,
                                             body = message)
        case_instance.save()
    except:
        print "No number or body"
        return render(request, '404.html')
    return HttpResponse('')



def dashboard(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        investigator = Investigator.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['notifications'] = get_notifications(investigator)

    # in_progress = 
    total_cases  = Case.objects.filter(investigator=investigator).filter(~Q(status= "Duplicate delete"))
    if not total_cases:
        context["no_data"] = True

        # Investigaror ranking
        investigators = Investigator.objects.all()
        # sorted_results = sorted(investigators, key= lambda t: t.cases_in_month(), reverse=True)
        # investigators = sorted_results[0:10]
        investigators_for_top_table = []
        cases_assigned_to_investigator_for_top_table = []
        cases_with_signature_percent_for_top_table = []
        for investigator_instance in investigators:
            cases_assigned_to_investigator = Case.objects.filter(investigator=investigator_instance).filter(~Q(status= "Duplicate delete")).filter(created_at__gt=(timezone.now() - timedelta(days=30)))
            cases_with_signature_obtained = cases_assigned_to_investigator.filter(is_signature_obtained = True)
            cases_assigned_to_investigator_for_top_table.append(len(cases_assigned_to_investigator))
            if len(cases_assigned_to_investigator) != 0 and len(cases_with_signature_obtained) != 0:
                percent_signature_obtained = round(float(len(cases_with_signature_obtained)*100 / len(cases_assigned_to_investigator)),2)
                cases_with_signature_percent_for_top_table.append(percent_signature_obtained)
                investigators_for_top_table.append(investigator_instance)
            else:
                percent_signature_obtained = 0
                cases_with_signature_percent_for_top_table.append(percent_signature_obtained)
                investigators_for_top_table.append(investigator_instance)
        
        investigator_data = zip(investigators_for_top_table,cases_assigned_to_investigator_for_top_table,cases_with_signature_percent_for_top_table)
        investigator_data.sort(key = lambda t: t[1],reverse=True)
        context["investigators_data"] = investigator_data[0:10]

        count = 0
        users_rank = 0
        users_cases = 0
        users_percent = 0
        is_user_in_top_ten = False
        for investigator_instance,cases_assigned_to_investigator_for_top_table,cases_with_signature_percent_for_top_table in investigator_data:
            count = count + 1
            if investigator_instance == investigator :
                users_rank = count
                users_cases = cases_assigned_to_investigator_for_top_table
                users_percent = cases_with_signature_percent_for_top_table

        for investigator_instance,cases_assigned_to_investigator_for_top_table,cases_with_signature_percent_for_top_table in investigator_data[0:10]:
            if investigator_instance == investigator :
                is_user_in_top_ten = True


        # context["investigators"] = investigators
        context["user_rank"] = users_rank
        context["user_cases"] = users_cases
        context["user_percent_signature_obtained"] = users_percent
        context["is_user_in_top_ten"] = is_user_in_top_ten
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

        investigators = Investigator.objects.all()
        # sorted_results = sorted(investigators, key= lambda t: t.cases_in_month(), reverse=True)
        # investigators = sorted_results[0:10]
        investigators_for_top_table = []
        cases_assigned_to_investigator_for_top_table = []
        cases_with_signature_percent_for_top_table = []
        for investigator_instance in investigators:
            cases_assigned_to_investigator = Case.objects.filter(investigator=investigator_instance).filter(~Q(status= "Duplicate delete")).filter(created_at__gt=(timezone.now() - timedelta(days=30)))
            cases_with_signature_obtained = cases_assigned_to_investigator.filter(is_signature_obtained = True)
            cases_assigned_to_investigator_for_top_table.append(len(cases_assigned_to_investigator))
            if len(cases_assigned_to_investigator) != 0 and len(cases_with_signature_obtained) != 0:
                percent_signature_obtained = round(float(len(cases_with_signature_obtained)*100 / len(cases_assigned_to_investigator)),2)
                cases_with_signature_percent_for_top_table.append(percent_signature_obtained)
                investigators_for_top_table.append(investigator_instance)
            else:
                percent_signature_obtained = 0
                cases_with_signature_percent_for_top_table.append(percent_signature_obtained)
                investigators_for_top_table.append(investigator_instance)
        
        investigator_data = zip(investigators_for_top_table,cases_assigned_to_investigator_for_top_table,cases_with_signature_percent_for_top_table)
        investigator_data.sort(key = lambda t: t[1],reverse=True)
        context["investigators_data"] = investigator_data[0:10]

        count = 0
        users_rank = 0
        users_cases = 0
        users_percent = 0
        is_user_in_top_ten = False
        for investigator_instance,cases_assigned_to_investigator_for_top_table,cases_with_signature_percent_for_top_table in investigator_data:
            count = count + 1
            if investigator_instance == investigator :
                users_rank = count
                users_cases = cases_assigned_to_investigator_for_top_table
                users_percent = cases_with_signature_percent_for_top_table

        for investigator_instance,cases_assigned_to_investigator_for_top_table,cases_with_signature_percent_for_top_table in investigator_data[0:10]:
            if investigator_instance == investigator :
                is_user_in_top_ten = True


        # context["investigators"] = investigators
        context["user_rank"] = users_rank
        context["user_cases"] = users_cases
        context["user_percent_signature_obtained"] = users_percent
        context["is_user_in_top_ten"] = is_user_in_top_ten


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

        brokers = Broker.objects.all()
        context['brokers'] = brokers

        profit_per_month = []
        profit_per_week = []
        profit_per_day = []
        profit_per_day_for_broker = []
        dates = []
        months = []
        weeks = []
        broker_ids = []
        data_for_broker = []
        date = timezone.localtime(timezone.now()).date() - timedelta(days=31)
        
        for day in range(0, 32):
            profit = 0
            current_date = date + timedelta(days=day)
            next_date = date + timedelta(days=day + 1)
            cases_on_current_date = total_cases.filter(closing_date__gte = current_date).filter(closing_date__lt = next_date).filter(status = "Closed")
            for case in cases_on_current_date:
                profit = profit + case.amount_paid_to_investigator
            profit_per_day.append(profit)
            dates.append(current_date)
        context['total_revenue_graph_daily'] = zip(dates, profit_per_day)

        date = timezone.localtime(timezone.now()).date()
        date = date.replace(day=1)
        month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        no_of_months =  range(0,12)
        month_names = ['January','February','March','April','May','June','July','August','September','October','November','December']
        for index in range(1,7):
            profit = 0
            first_day_of_month = date
            print first_day_of_month
            month = date.month
            print month-1
            days = month_days[no_of_months[month-1]]
            print days
            last_day_of_month = date.replace(day=days)
            print last_day_of_month
            cases_on_current_date = total_cases.filter(closing_date__gte = first_day_of_month).filter(closing_date__lt = last_day_of_month).filter(status = "Closed")
            for case in cases_on_current_date:
                profit = profit + case.amount_paid_to_investigator
            print profit
            profit_per_month.append(profit)
            months.append(first_day_of_month)
            date = date - timedelta(days=month_days[no_of_months[month-2]])
        context['total_revenue_graph_monthly'] = zip(months, profit_per_month)
        

    return render(request, 'investigator/dashboard.html',context)