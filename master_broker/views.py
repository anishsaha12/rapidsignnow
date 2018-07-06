from django.shortcuts import get_object_or_404, render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseServerError
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from operator import __or__ as OR
from operator import __and__ as AND
from broker.tasks import scheduled_functions

from xhtml2pdf import pisa
from django.template.loader import get_template

import json
import itertools
import ast
import StringIO
import datetime
import random
import mimetypes 
import magic  
import urllib 
from twilio.rest import Client
from datetime import timedelta, date
from dateutil import relativedelta
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
from transactions.models import Transaction
from customer_profile.models import CustomerProfile

from law_firm.charging_law_firm import *
from decimal import *
from refunds.models import Refund

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

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def get_notifications(master_broker):

    unread_statuses = StatusUpdate.objects.order_by('-timestamp')[:15]
    status_notifications = []
    unread_count = 0
    for status in unread_statuses:
        notification = dict()

        notification['status_id'] = status.pk
        notification['case_id'] = status.case.pk
        notification['case_name'] = status.case.name
        if status.user == master_broker.user:
            notification['investigator'] = 'You'
        elif status.updated_by == 'MB':
            notification['investigator'] = status.user.first_name + ' ' + status.user.last_name
        elif status.updated_by == 'BR':
            notification['investigator'] = status.user.first_name + ' ' + status.user.last_name
        else:
            notification['investigator'] = status.case.investigator.user.first_name + ' ' + status.case.investigator.user.last_name
        notification['status'] = status.status
        notification['timestamp'] = status.timestamp
        notification['read'] = status.read_by_master_broker
        notification['type'] = 'status'

        if not status.read_by_master_broker:
            unread_count += 1

        status_notifications.append(notification)

    
    unread_acceptances = CaseAcceptanceUpdate.objects.filter().order_by('-timestamp')[:15]
    acceptance_notifications = []

    for acceptance in unread_acceptances:
        notification = dict()

        notification['acceptance_id'] = acceptance.pk
        notification['case_id'] = acceptance.case.pk
        notification['case_name'] = acceptance.case.name
        notification['investigator'] = acceptance.investigator.user.first_name + ' ' + acceptance.investigator.user.last_name
        notification['is_accepted'] = acceptance.is_accepted
        notification['timestamp'] = acceptance.timestamp
        notification['read'] = acceptance.read_by_master_broker
        notification['type'] = 'acceptance'

        if not acceptance.read_by_master_broker:
            unread_count += 1

        acceptance_notifications.append(notification)

    notifications = status_notifications + acceptance_notifications
    # notifications = sorted(notifications, key=lambda notification: notification['timestamp'])
    notifications = notifications[:15]

    return {
        'entries': notifications,
        'unread': unread_count
    }

def create_new_case(request):

    import requests
    import json

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['law_firms'] = LawFirm.objects.all().filter(is_active=True)
    all_investigators = Investigator.objects.all().filter(is_active=True)
    
    for investigator in all_investigators:
        try:
            investigator.languages = ast.literal_eval(investigator.languages)
        except:
            investigator.languages =['unknown']
            pass
    documents = Document.objects.filter(is_deleted=False)
    context['investigators'] = all_investigators
    context['languages'] = languages
    context['countries'] = countries
    context['documents'] = documents
    context['notifications'] = get_notifications(master_broker)

    if request.POST:
        if request.POST.get('context') == 'download-document':
            document_id = request.POST['document-id']
            response = download_doc(request,document_id)
            return response
        else:
            investigator = None

            try:
                investigator_id = request.POST['investigator']
                investigator = Investigator.objects.get(pk=investigator_id)
            except:
                pass

            law_firm_id = request.POST['law-firm']
            law_firm = LawFirm.objects.get(pk=law_firm_id)

            status = request.POST['status']

            street_one = request.POST['street-1']
            street_two = request.POST['street-2']
            city = request.POST['city']
            state = request.POST['state']
            if "zip-code" in request.POST and request.POST['zip-code']:
                zip_code = request.POST['zip-code']
            else:
                zip_code=''

            new_address = Address(street_one=street_one, street_two=street_two, city=city, state=state, zip_code=zip_code)
            new_address.save()
            
            coordinates = new_address.get_coordinates()
            
            if coordinates is not None:
                new_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                    str(coordinates['longitude'])
                new_address.save()

            name = request.POST['case-name']
            case_type = request.POST['case-type']
            case_type_description = ''

            if ('case-type' not in request.POST or type == ''):
                case_type='default'
            elif (case_type == 'Others'):
                case_type_description = request.POST['case-type-description']
            

            adult_clients = request.POST['adult-clients']
            print "POST Received Adult Clients: %s"%adult_clients
            child_clients = request.POST['child-clients']
            print "POST Received Child Clients: %s"%child_clients
            # number_of_signatures_required = request.POST['number-of-signatures-required']
            number_of_adult_signatures_required = int(request.POST['number-of-adult-signatures-required'])
            number_of_child_signatures_required = int(request.POST['number-of-child-signatures-required'])

            total_pages_in_attachment = None
            if 'total-pages-in-attachment' in request.POST:
                try:
                    total_pages_in_attachment = int(request.POST['total-pages-in-attachment'])
                except:
                    total_pages_in_attachment = None

            documents = None
            if 'documents' in request.FILES:
                documents = request.FILES['documents']

            basic_fee_law_firm = float(request.POST['basic-fee-for-case-law-firm'])
            no_of_free_miles_law_firm = float(request.POST['no-of-free-miles-law-firm'])
            mileage_rate_law_firm = float(request.POST['mileage-rate-law-firm'])

            basic_fee_investigator = float(request.POST['basic-fee-for-case-investigator'])
            no_of_free_miles_investigator = float(request.POST['no-of-free-miles-investigator'])
            mileage_rate_investigator = float(request.POST['mileage-rate-investigator'])

            locality = request.POST['locality']

            is_dol_provided = False
            if 'dol' in request.POST and request.POST['dol']:
                dol = request.POST['dol']
                dol_components = dol.split('/')
                dol = datetime.datetime(int(dol_components[2]), int(dol_components[0]), int(dol_components[1]))
                is_dol_provided = True
            else:
                dol = datetime.datetime(2017, 1, 1)
                is_dol_provided = False

            if 'edos' in request.POST and request.POST['edos']:
                edos = request.POST['edos']
                edos_components = edos.split('/')
                edos = datetime.datetime(int(edos_components[2]), int(edos_components[0]), int(edos_components[1]))
            else:
                edos = None   
                
            
            expected_payment = float(request.POST['expected-payment-for-case'])

            client_name = request.POST['client-name']
            client_mobile_phone = request.POST['mobile-phone']
            client_home_phone = request.POST['home-phone']
            if 'primary-email' in request.POST and  request.POST['primary-email'] :
                client_primary_email = request.POST['primary-email'] 
            else:
                client_primary_email = ''
            client_secondary_email = request.POST['secondary-email']
            client_language = request.POST['language']

            random_string = '%030x' % random.randrange(16**30)

            new_case = Case(investigator=investigator, law_firm=law_firm, status=status, client_address=new_address,
                            name=name, type=case_type, type_description=case_type_description, number_of_adult_signatures_required = number_of_adult_signatures_required,
                            number_of_child_signatures_required = number_of_child_signatures_required,
                            total_pages_in_attachment=total_pages_in_attachment, documents=documents,
                            expected_payment=expected_payment, client_name=client_name,
                            client_mobile_phone=client_mobile_phone, client_home_phone=client_home_phone,
                            client_primary_email=client_primary_email, client_secondary_email=client_secondary_email,
                            client_language=client_language, created_by_master=master_broker, adult_clients=adult_clients,
                            child_clients=child_clients, dol=dol,is_dol_provided=is_dol_provided,expected_closing_date=edos ,locality=locality, random_string=random_string,
                            basic_fee_law_firm=basic_fee_law_firm, no_of_free_miles_law_firm=no_of_free_miles_law_firm,
                            mileage_rate_law_firm=mileage_rate_law_firm, basic_fee_investigator=basic_fee_investigator,
                            no_of_free_miles_investigator=no_of_free_miles_investigator,
                            mileage_rate_investigator=mileage_rate_investigator)
            new_case.save()
            dos=timezone.localtime(timezone.now())
            new_case.date_of_signup = dos
            new_case.save()

            new_status_update = StatusUpdate(user=master_broker.user, status='Case opened', case=new_case)
            new_status_update.save()

            new_status_update = StatusUpdate(user=master_broker.user, status=status, case=new_case)
            new_status_update.save()

            if 'document' in request.POST:
                documents = request.POST.getlist('document')
                for document in documents:
                    attached_document = Document.objects.get(pk=document)
                    new_attached_document = AttachedDocument(case=new_case, document=attached_document)
                    new_attached_document.save()

            longUrl = 'http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' + str(new_case.pk) + '/?key=' + new_case.random_string
            if investigator is not None:
                post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
                params = json.dumps({'longUrl': longUrl})
                response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})
                shortened_url = longUrl
                try:
                    shortened_url =  response.json()['id']
                except:
                    pass
                
                phone_number = investigator.phone_number_one.replace('-', '').replace(' ', '')
                client_phone_number = new_case.client_mobile_phone.replace('-', '').replace(' ', '')
                print "%s:"%shortened_url
                print "%s:"%phone_number
                print "%s:"%client_phone_number
                print "%s:"%investigator.email_one
                print "%s:"%master_broker.user.first_name
                text_content = " Case assigned "
                subject = "CASE ASSIGNED"
                try:
                    if new_case.client_address.gmaps_link :
                        html_content = """<style>th,td{padding:5px;text-align:left}</style><div style="text-align:center;"><h1>CASE ASSIGNED</h1></div><div style="float:left;"><h3>Hi """+ new_case.investigator.user.first_name + """ """ + new_case.investigator.user.last_name + """ ,</h3></div><div style="float:left;"><h3> You have been assigned a new case by """+ master_broker.user.first_name + """ """+ master_broker.user.last_name +""". Please find the details below.</h3></div><div style="margin-top: 200px;text-align:center;"><table style="margin: 1em auto;"><tr><th>Case Id</th><td> """+ str(new_case.pk) + """</td></tr><tr><th>Case Name</th><td> """+ new_case.name +"""</td></tr><tr><th>Law Firm</th><td> """+ new_case.law_firm.name +"""</td></tr><tr><th>Client Name</th><td> """+ new_case.client_name +"""</td></tr><tr><th>Client Ph.no</th><td><a href="tel: """+client_phone_number+""" ">"""+ new_case.client_mobile_phone +"""</a></td></tr><tr><th>Client Address</th><td> <a href=" """+new_case.client_address.gmaps_link+""" ">"""+ new_case.client_address.simple_address() +"""</a></td></tr><tr><th>Map Link</th><td> <a href=" """+new_case.client_address.gmaps_link+""" ">"""+ new_case.client_address.gmaps_link +"""</a></td></tr></table><h4>Please Click <a href=" """+shortened_url+""" ">Here</a> to update status.</h4></div><div style="float:left;"><h4> Best Wishes,</h4><h4> Rapidsignnow Team</h4></div> </br></br> </br></br></br></br></br><div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div> """
                    else:
                        html_content = """<style>th,td{padding:5px;text-align:left}</style><div style="text-align:center;"><h1>CASE ASSIGNED</h1></div><div style="float:left;"><h3>Hi """+ new_case.investigator.user.first_name + """ """ + new_case.investigator.user.last_name + """ ,</h3></div><div style="float:left;"><h3> You have been assigned a new case by """+ master_broker.user.first_name + """ """+ master_broker.user.last_name +""". Please find the details below.</h3></div><div style="margin-top: 200px;text-align:center;"><table style="margin: 1em auto;"><tr><th>Case Id</th><td> """+ str(new_case.pk) + """</td></tr><tr><th>Case Name</th><td> """+ new_case.name +"""</td></tr><tr><th>Law Firm</th><td> """+ new_case.law_firm.name +"""</td></tr><tr><th>Client Name</th><td> """+ new_case.client_name +"""</td></tr><tr><th>Client Ph.no</th><td><a href="tel: """+client_phone_number+""" ">"""+ new_case.client_mobile_phone +"""</a></td></tr><tr><th>Client Address</th><td> """+ new_case.client_address.simple_address() +"""</td></tr></table><h4>Please Click <a href=" """+shortened_url+""" ">Here</a> to update status.</h4></div><div style="float:left;"><h4> Best Wishes,</h4><h4> Rapidsignnow Team</h4></div> </br></br> </br></br></br></br></br><div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>"""
                except:
                    print "html content is incorrect"
                
                try:
                    # if new_case.client_address.gmaps_link :
                    #     message = EmailMessage('Case Assigned', 'The case ' + new_case.name + ' has been assigned to you by ' + master_broker.user.first_name +
                    #         ' ' + master_broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. Visit the client at this address -> '+ new_address.gmaps_link,
                    #         'assign@rapidsignnow.com', [investigator.email_one])
                    # else:
                    #     message = EmailMessage('Case Assigned', 'The case ' + new_case.name + ' has been assigned to you by ' + master_broker.user.first_name +
                    #     ' ' + master_broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. Closest known address -> '+ new_case.client_address.simple_address() + '.',
                    #     'assign@rapidsignnow.com', [investigator.email_one])
                    message = EmailMultiAlternatives(subject, text_content, 'assign@rapidsignnow.com', [investigator.email_one])
                    message.attach_alternative(html_content, "text/html")
                    attached_documents = AttachedDocument.objects.filter(case=new_case)
                    for attached_document in attached_documents:
                        mime = magic.Magic(mime=True) 
                        output = "output" 
                        urllib.urlretrieve(attached_document.document.file.url, output)
                        mimes = mime.from_file(output)
                        ext = mimetypes.guess_all_extensions(mimes)[0] 
                        # os.rename(output, output+ext) # Rename file
                        pdf = attached_document.document.file.file.read()
                        name = attached_document.document.file_name
                        message.attach(name, pdf, mimes)
                    message.send()  
                except:
                    print "Coud not send email"
                    pass
                try:              
                    # message = twilio_client.api.account.messages.create(to=phone_number,
                    #                                     from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                    #                                     body='The case ' + new_case.name + ' has been assiged to you by ' + broker.user.first_name +
                    #     ' ' + broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. '+ new_address.gmaps_link)
                    if new_case.client_address.gmaps_link :
                        # message = twilio_client.api.account.messages.create(to=phone_number,
                        #                                     from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                        #                                     body='The case ' + new_case.name + ' has been assigned to you by ' + broker.user.first_name +
                        #     ' ' + broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. Address -> '+ new_case.client_address.gmaps_link )
                        message = twilio_client.api.account.messages.create(to=phone_number,from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,body="Case Assigned \nCase ID:" + str(new_case.pk) + "  \nCase Name: " + new_case.name + "\nLaw Firm: " + new_case.law_firm.name + "\nClient Name: " + new_case.client_name +  "\nClient Phone: " + new_case.client_mobile_phone + "\nClient Address: "+ new_case.client_address.simple_address() + "\nMap Link: "+ new_case.client_address.gmaps_link +"\n\n Please Click at " + shortened_url + " to update status.")
                    else:
                        # message = twilio_client.api.account.messages.create(to=phone_number,
                        #                                     from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                        #                                     body='The case ' + new_case.name + ' has been assigned to you by ' + broker.user.first_name +
                        #     ' ' + broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. Closest known address -> ' + new_case.client_address.simple_address()+'.')
                        message = twilio_client.api.account.messages.create(to=phone_number,from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,body="Case Assigned \nCase ID:" + str(new_case.pk) + "  \nCase Name: " + new_case.name + "\nLaw Firm: " + new_case.law_firm.name + "\nClient Name: " + new_case.client_name +  "\nClient Phone: " + new_case.client_mobile_phone + "\nClient Address: "+ new_case.client_address.simple_address() + "\n\n Please Click at " + shortened_url + " to update status.")
                except:
                    print "Could not send msg"
                    pass
            
            #scheduled_functions(new_case.pk)
            return HttpResponseRedirect('/master-broker/all-cases/')

    return render(request, 'master_broker/create_new_case.html', context)

def show_investigator_details(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
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
    
    
    context['notifications'] = get_notifications(master_broker)

    return render(request, 'master_broker/investigator_snippet.html', context)

def all_cases(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['cases'] = []

    cases = []
    
    # print (cases)
    # cases = Case.objects.all()
    law_firms = LawFirm.objects.all()

    
    all_investigators = Investigator.objects.all()
    # for investigator in all_investigators:
    #     investigator.languages = ast.literal_eval(investigator.languages)

    context['investigators'] = all_investigators
    context['notifications'] = get_notifications(master_broker)

    context['law_firms'] = law_firms
    cases_by_broker = []
    cases_by_master_broker = []
    context['next_page_url'] = ''
    no_of_cases = 50


    if request.is_ajax() and 'context' in request.POST and request.POST['context'] == 'pay':

        #Mark case as paid to investigator
        try:
            case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                .replace(' ', '').split(',')
        except:
            return HttpResponseRedirect('/')

        all_cases_in_range = []

        for case_id in case_ids:
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_investigator_paid = True
            case_instance.amount_paid_to_investigator = case_instance.get_investigator_price()
            case_instance.save()
            all_cases_in_range.append(case_instance)

        return HttpResponse('')
    elif request.is_ajax() and 'context' in request.POST and request.POST['context'] == 'unpay':
        #Mark case as unpaid to investigator
        try:
            case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                .replace(' ', '').split(',')
        except:
            return HttpResponseRedirect('/')

        all_cases_in_range = []

        for case_id in case_ids:
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_investigator_paid = False
            case_instance.save()
            all_cases_in_range.append(case_instance)

        return HttpResponse('')
    
    elif request.POST and 'context' in request.POST and request.POST['context'] == 'document-sent':
        try:
            case_id = request.POST['case_id']
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_document_sent = True
            case_instance.save()
        except:
            print "not marked" 
        
        return HttpResponse('')

    elif request.POST and 'context' in request.POST and request.POST['context'] == 'document-not-sent':
        try:
            case_id = request.POST['case_id']
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_document_sent = False
            case_instance.save()
        except:
            print "not unmarked"
            
        return HttpResponse('')
        
    elif 'context' in request.POST and request.POST['context'] == 'mark-for-documents-sent':
        try:
            case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                .replace(' ', '').split(',')
        except:
            return HttpResponseRedirect('/')

        all_cases_in_range = []

        for case_id in case_ids:
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_document_sent = True
            case_instance.save()
            all_cases_in_range.append(case_instance)

        return HttpResponse('')
    elif 'context' in request.POST and request.POST['context'] == 'mark-for-documents-not-sent':
        try:
            case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                .replace(' ', '').split(',')
        except:
            return HttpResponseRedirect('/')

        all_cases_in_range = []

        for case_id in case_ids:
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_document_sent = False
            case_instance.save()
            all_cases_in_range.append(case_instance)

        return HttpResponse('')
    elif 'context' in request.POST and request.POST['context'] == 'mark-for-payment':
        try:
            case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                .replace(' ', '').split(',')
        except:
            return HttpResponseRedirect('/')

        all_cases_in_range = []

        for case_id in case_ids:
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_marked_for_payment = True
            case_instance.amount_refunded = 0.0
            case_instance.refund_settlement = ""
            case_instance.refund_description = ""
            case_instance.save()
            all_cases_in_range.append(case_instance)

        return HttpResponse('')
    elif 'context' in request.POST and request.POST['context'] == 'unmark-for-payment':
        try:
            case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                .replace(' ', '').split(',')
        except:
            return HttpResponseRedirect('/')

        all_cases_in_range = []

        for case_id in case_ids:
            case_instance = Case.objects.get(pk=case_id)
            case_instance.is_marked_for_payment = False
            case_instance.approved_by_rsn = False
            case_instance.save()
            all_cases_in_range.append(case_instance)

        return HttpResponse('')

    if (request.method == 'GET'):
        # If filters were removed
        cases = Case.objects.all().order_by('-pk')
        if 'filtering' in  request.GET and request.GET['filtering'] == 'on':
                
            context['next_page_url'] = 'filtering=on&'
            if 'from' in request.GET and request.GET['from'] != '':
                from_date = request.GET.get('from')
                from_components = from_date.split('/')
                context['next_page_url'] += 'from='+str(from_date)+'&'
                from_date = datetime.datetime(int(from_components[2]), int(from_components[0]), int(from_components[1]))
                cases = cases.filter(created_at__gte=from_date)

                context['from'] = request.GET['from']
                context['is_filter_applied'] = 1
                
            
            if 'to' in request.GET and request.GET['to'] != '':
                to_date = request.GET.get('to')
                to_components = to_date.split('/')
                context['next_page_url'] += 'to='+str(to_date)+'&'
                to_date = datetime.datetime(int(to_components[2]), int(to_components[0]), int(to_components[1]))
                cases = cases.filter(created_at__lt=to_date)
                context['to'] = request.GET['to']
                context['is_filter_applied'] = 1
                
            if 'law-firm' in request.GET and request.GET['law-firm'] != '':
                law_firm_id = request.GET['law-firm']
                law_firm = LawFirm.objects.get(pk=int(law_firm_id))
                print "The selected_lawfirm is "
                print law_firm_id
                context['selected_firm_id'] = law_firm_id
                cases = cases.filter(law_firm = law_firm)
                context['selected_firm'] = law_firm_id
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'law-firm='+law_firm_id+'&'
            

            if 'investigator' in request.GET and request.GET['investigator'] != '':
                investigator_id = request.GET['investigator']
                investigator = Investigator.objects.get(pk=investigator_id)
                # context['selected_investigator_id'] = investigator_id
                cases = cases.filter(investigator = investigator)
                context['selected_investigator'] = investigator_id
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'investigator='+investigator_id+'&'
                

            if 'status' in request.GET and request.GET['status'] != '':
                status = request.GET['status']
                cases = cases.filter(status = status)
                context['selected_status'] = request.GET['status']
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'status='+status+'&'

            q_array = []
            
            if 'broker' in request.GET and request.GET['broker'] != '':
                broker_id = request.GET['broker']
                broker = Broker.objects.get(pk=broker_id)
                # cases_by_broker = cases.filter(created_by = broker)

                q_array.append(Q(created_by = broker))

                # cases = cases.filter(created_by = broker)
                # case_by_broker = cases
                context['selected_broker'] = broker_id
                context['is_filter_applied'] = 1   
                context['next_page_url'] += 'broker='+broker_id+'&'

            if 'master-broker' in request.GET and request.GET['master-broker'] !='':  
                master_broker_id = request.GET['master-broker']
                master_broker = MasterBroker.objects.get(pk=master_broker_id)

                context['selected_master_broker'] = master_broker_id
                cases_by_master_broker = cases.filter(created_by_master = master_broker)
                q_array.append(Q(created_by_master = master_broker))
                context['is_filter_applied'] = 1   
                context['next_page_url'] += 'master-broker='+master_broker_id+'&'
            
            if len(q_array):
                cases = cases.filter(reduce(OR, q_array))  


            if 'marked-case' in request.GET and request.GET['marked-case'] != '':
                cases = cases.filter(is_attention_required = True)
                context['is_marked_case'] = 1
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'marked-case=on&'
                
            if 'no-of-cases' in request.GET and request.GET['no-of-cases'] != '':
                # context['no-of-cases'] = request.GET['no-of-cases']
                no_of_cases = request.GET['no-of-cases']
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'no-of-cases='+ no_of_cases +'&'

            if 'search' in request.GET and request.GET['search'] != '' :
                search = request.GET['search']
                context['search'] = search
                q_array = []
                q_array = []
                q_array_investigator= []
                q_array_broker= []
                q_array_master_broker= []
                q_array_name = []
                q_array_law_firm = []
                search_url = ''

                q_array_name.append(Q(name__icontains = search))
                q_array_law_firm.append(Q(law_firm__name__icontains = search))

                for search in search.split():
                    q_array.append(Q(name__icontains = search))
                    q_array.append(Q(law_firm__name__icontains = search))
                    q_array.append(Q(created_by__user__first_name__icontains = search))
                    q_array.append(Q(created_by__user__last_name__icontains = search))
                    q_array.append(Q(created_by_master__user__first_name__icontains = search))
                    q_array.append(Q(created_by_master__user__last_name__icontains = search))
                    q_array.append(Q(investigator__user__first_name__icontains = search))
                    q_array.append(Q(investigator__user__last_name__icontains = search))
                    q_array.append(Q(client_address__street_one__icontains = search))
                    q_array.append(Q(client_address__street_two__icontains = search))
                    q_array.append(Q(client_address__city__icontains = search))
                    q_array.append(Q(client_address__state__icontains = search))
                    q_array.append(Q(client_address__country__icontains = search))
                    search_url += search + '+' 
                
                context['next_page_url'] += 'search='+search_url+'&'
                
                search = request.GET['search']
                for search_first in search.split():
                    for search_last in search.split():
                        if search_first != search_last:
                            if len(cases.filter(investigator__user__first_name__icontains = search_first).filter(investigator__user__last_name__icontains = search_last)):
                                q_array_investigator.append(Q(investigator__user__first_name__icontains = search_first))
                                q_array_investigator.append(Q(investigator__user__last_name__icontains = search_last))
                
                for search_first in search.split():
                    for search_last in search.split():
                        if search_first != search_last:
                            if len(cases.filter(created_by__user__first_name__icontains = search_first).filter(created_by__user__last_name__icontains = search_last)):
                                q_array_broker.append(Q(created_by__user__first_name__icontains = search_first))
                                q_array_broker.append(Q(created_by__user__last_name__icontains = search_last))
                
                for search_first in search.split():
                    for search_last in search.split():
                        if search_first != search_last:
                            if len(cases.filter(created_by_master__user__first_name__icontains = search_first).filter(created_by_master__user__last_name__icontains = search_last)):
                                q_array_master_broker.append(Q(created_by_master__user__first_name__icontains = search_first))
                                q_array_master_broker.append(Q(created_by_master__user__last_name__icontains = search_last))
                
                cases_1=[]
                cases_2=[]
                cases_3=[]
                cases_4=[]
                cases_5 =[]
                cases_6 = []
                cases_combined = []
                if len(q_array_name):
                    cases_1 = cases.filter(reduce(OR, q_array_name))
                if len(q_array_law_firm):
                    cases_2 = cases.filter(reduce(OR, q_array_law_firm))
                if len(q_array_investigator):
                    cases_3 = cases.filter(reduce(AND, q_array_investigator))
                    # searched_cases.append(cases_1)
                if len(q_array_broker):
                    cases_4 = cases.filter(reduce(AND, q_array_broker))  
                if len(q_array_master_broker):
                    cases_5 = cases.filter(reduce(AND, q_array_master_broker))  
                
                if len(q_array):
                    cases_6 = cases.filter(reduce(OR, q_array))  
                
                
                

                if len(cases_3) and len(cases_4) and len(cases_5):
                    cases = reduce(OR,(cases_1,cases_2,cases_3,cases_4,cases_5,cases_6))
                elif len(cases_3):
                    if len(cases_4):
                        cases = reduce(OR,(cases_1,cases_2,cases_3,cases_4,cases_6))
                    elif len(cases_5):
                        cases = reduce(OR,(cases_1,cases_2,cases_3,cases_5,cases_6))
                    else:
                        cases = reduce(OR,(cases_1,cases_2,cases_3,cases_6))
                elif len(cases_4):
                    if len(cases_5):
                        cases = reduce(OR,(cases_1,cases_2,cases_4,cases_5,cases_6))
                    else:
                        cases = reduce(OR,(cases_1,cases_2,cases_4,cases_6))
                elif len(cases_5):
                    cases = reduce(OR,(cases_1,cases_2,cases_5,cases_6))
                else:
                    cases = reduce(OR,(cases_1,cases_2,cases_6))

        
    elif request.method == 'POST' and 'context' in request.POST and (request.POST['context'] == 'remove-filters' or request.POST['context'] == 'clear-search'):
        cases = Case.objects.all().order_by('-pk')

    # for case in cases:
    #     case.final_status =  get_case_final_status(case)
    #     case.amount_billed_to_law_firm = case.get_law_firm_price()
    
    if no_of_cases != 'All':
        paginator = Paginator(cases, no_of_cases) # Show case per page

        page = request.GET.get('page')
        try:
            cases = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            cases = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            cases = paginator.page(paginator.num_pages)
    elif no_of_cases == 'All' :
        paginator = Paginator(cases, 1000) # Show 25 contacts per page

        page = request.GET.get('page')
        try:
            cases = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            cases = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            cases = paginator.page(paginator.num_pages)
        
    context['no_of_cases'] = no_of_cases    
    print (no_of_cases)
    print len(cases)    
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

    return render(request, 'master_broker/all_cases.html', context)

def assign_investigator(request):
    import json
    import requests

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'investigator_id' not in request.POST or 'case_id' not in request.POST:
        return HttpResponseRedirect('/')

    investigator_id = request.POST['investigator_id']
    investigator = Investigator.objects.get(pk=investigator_id)

    if not investigator.is_active:
        return SuspiciousOperation("Invalid request; Cannot assign an Investigator who is suspended")

    case_id = request.POST['case_id']
    case = Case.objects.get(pk=case_id)

    if case.is_investigator_paid:
        raise SuspiciousOperation("Invalid request; Cannot change status of case which is marked as Paid")
    elif case.invoice:
        raise SuspiciousOperation("Invalid request; Cannot edit case details if an active invoice is associated")

    longUrl = 'http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +str(case.pk) + '/?key=' + case.random_string
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
    params = json.dumps({'longUrl': longUrl})
    response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

    
    shortened_url = longUrl
    try:
        shortened_url =  response.json()['id']
    except:
        pass
    print"%s:"% shortened_url
    

    case.investigator = investigator
    case.save()
    
    phone_number = investigator.phone_number_one.replace('-', '').replace(' ', '')
    print (case.name)
    print "%s:"% phone_number
    print "%s"% master_broker.user.first_name
    print "%s:"% investigator.email_one

    client_phone_number = case.client_mobile_phone.replace('-', '').replace(' ', '')
    print "%s:"%shortened_url
    print "%s:"%phone_number
    print "%s:"%client_phone_number
    print "%s:"%investigator.email_one
    print "%s:"%master_broker.user.first_name
    text_content = " Case assigned "
    subject = "CASE ASSIGNED"
    try:
        if case.client_address.gmaps_link :
            html_content = """<style>th,td{padding:5px;text-align:left}</style><div style="text-align:center;"><h1>CASE ASSIGNED</h1></div><div style="float:left;"><h3>Hi """+ case.investigator.user.first_name + """ """ + case.investigator.user.last_name + """ ,</h3></div><div style="float:left;"><h3> You have been assigned a new case by """+ master_broker.user.first_name + """ """+ master_broker.user.last_name +""". Please find the details below.</h3></div><div style="margin-top: 200px;text-align:center;"><table style="margin: 1em auto;"><tr><th>Case Id</th><td> """+ str(case.pk) + """</td></tr><tr><th>Case Name</th><td> """+ case.name +"""</td></tr><tr><th>Law Firm</th><td> """+ case.law_firm.name +"""</td></tr><tr><th>Client Name</th><td> """+ case.client_name +"""</td></tr><tr><th>Client Ph.no</th><td><a href="tel: """+client_phone_number+""" ">"""+ case.client_mobile_phone +"""</a></td></tr><tr><th>Client Address</th><td> <a href=" """+case.client_address.gmaps_link+""" ">"""+ case.client_address.simple_address() +"""</a></td></tr><tr><th>Map Link</th><td> <a href=" """+case.client_address.gmaps_link+""" ">"""+ case.client_address.gmaps_link +"""</a></td></tr></table><h4>Please Click <a href=" """+shortened_url+""" ">Here</a> to update status.</h4></div><div style="float:left;"><h4> Best Wishes,</h4><h4> Rapidsignnow Team</h4></div></br></br> </br></br></br></br></br><div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>"""
        else:
            html_content = """<style>th,td{padding:5px;text-align:left}</style><div style="text-align:center;"><h1>CASE ASSIGNED</h1></div><div style="float:left;"><h3>Hi """+ case.investigator.user.first_name + """ """ + case.investigator.user.last_name + """ ,</h3></div><div style="float:left;"><h3> You have been assigned a new case by """+ master_broker.user.first_name + """ """+ master_broker.user.last_name +""". Please find the details below.</h3></div><div style="margin-top: 200px;text-align:center;"><table style="margin: 1em auto;"><tr><th>Case Id</th><td> """+ str(case.pk) + """</td></tr><tr><th>Case Name</th><td> """+ case.name +"""</td></tr><tr><th>Law Firm</th><td> """+ case.law_firm.name +"""</td></tr><tr><th>Client Name</th><td> """+ case.client_name +"""</td></tr><tr><th>Client Ph.no</th><td><a href="tel: """+client_phone_number+""" ">"""+ case.client_mobile_phone +"""</a></td></tr><tr><th>Client Address</th><td> """+ case.client_address.simple_address() +"""</td></tr></table><h4>Please Click <a href=" """+shortened_url+""" ">Here</a> to update status.</h4></div><div style="float:left;"><h4> Best Wishes,</h4><h4> Rapidsignnow Team</h4></div></br></br> </br></br></br></br></br><div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div> """
    except:
        print "html content is incorrect"
    
    try:
        # if new_case.client_address.gmaps_link :
        #     message = EmailMessage('Case Assigned', 'The case ' + new_case.name + ' has been assigned to you by ' + master_broker.user.first_name +
        #         ' ' + master_broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. Visit the client at this address -> '+ new_address.gmaps_link,
        #         'assign@rapidsignnow.com', [investigator.email_one])
        # else:
        #     message = EmailMessage('Case Assigned', 'The case ' + new_case.name + ' has been assigned to you by ' + master_broker.user.first_name +
        #     ' ' + master_broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. Closest known address -> '+ new_case.client_address.simple_address() + '.',
        #     'assign@rapidsignnow.com', [investigator.email_one])
        message = EmailMultiAlternatives(subject, text_content, 'assign@rapidsignnow.com', [investigator.email_one])
        message.attach_alternative(html_content, "text/html")
        attached_documents = AttachedDocument.objects.filter(case=case)
        for attached_document in attached_documents:
            mime = magic.Magic(mime=True) 
            output = "output" 
            urllib.urlretrieve(attached_document.document.file.url, output)
            mimes = mime.from_file(output)
            ext = mimetypes.guess_all_extensions(mimes)[0] 
            # os.rename(output, output+ext) # Rename file
            pdf = attached_document.document.file.file.read()
            name = attached_document.document.file_name
            message.attach(name, pdf, mimes)
        message.send()
    except Exception as e:
        print "could not send mail"
        print (e)
        
    try:
        if case.client_address.gmaps_link is not None :
            # message = twilio_client.api.account.messages.create(to=phone_number,
            #                                     from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
            #                                     body='The case ' + case.name + ' has been assigned to you by ' + master_broker.user.first_name +
            #     ' ' + master_broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. Address -> '+ case.client_address.gmaps_link)
            message = twilio_client.api.account.messages.create(to=phone_number,from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,body="Case Assigned \nCase ID:" + str(case.pk) + "\nCase Name: " + case.name + "\nLaw Firm: " + case.law_firm.name + "\nClient Name: " + case.client_name +  "\nClient Phone: " + case.client_mobile_phone + "\nClientAddress: "+ case.client_address.simple_address() + "\nMap Link: "+ case.client_address.gmaps_link +"\n\n Please Click at " + shortened_url + " to update status.")
        else:
            # message = twilio_client.api.account.messages.create(to=phone_number,
            #                                     from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
            #                                     body='The case ' + case.name + ' has been assigned to you by ' + master_broker.user.first_name +
            #     ' ' + master_broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. Closest known address -> '+ case.client_address.simple_address())
            message = twilio_client.api.account.messages.create(to=phone_number,from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,body="Case Assigned \nCase ID:" + str(case.pk) + "\nCase Name: " + case.name + "\nLaw Firm: " + case.law_firm.name + "\nClient Name: " + case.client_name +  "\nClient Phone: " + case.client_mobile_phone + "\nClientAddress: "+ case.client_address.simple_address() + "\n\n Please Click at " + shortened_url + " to update status.")
    except Exception as e:
        print "could not send msg"
    
    return HttpResponse('')

def change_status(request):

    import datetime

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'new_status' not in request.POST or 'case_id' not in request.POST:
        return HttpResponseRedirect('/')

    status = request.POST['new_status']
    if status is None:
        return HttpResponseRedirect('/')

    possible_statuses = ['inactive','in progress','called and texted','client contacted','client meeting set','client rescheduled','client cancelled','duplicate delete','signature obtained','signature not obtained', 'closed']

    if not status.lower() in possible_statuses:
        raise SuspiciousOperation('Not an allowed status')

    extra_info = None
    
    if 'extra_info' in request.POST:
        extra_info = request.POST['extra_info']

        if len(extra_info) == 0:
            extra_info = None


    case_id = request.POST['case_id']
    case = Case.objects.get(pk=case_id)

    if case.is_investigator_paid:
        raise SuspiciousOperation("Invalid request; Cannot change status of case which is marked as Paid")
    elif case.invoice is not None:
        raise SuspiciousOperation("Invalid request; Cannot edit case details if an active invoice is associated")


    case.status = status

    additional_expenses_description = ''
    json_payload = None

    
    if status.lower() == 'client cancelled':
        case.is_signature_obtained = False
        case.did_investigator_travel = False
        case.number_of_adult_signatures_obtained = 0
        case.number_of_child_signatures_obtained = 0
        case.no_of_miles_travelled = 0
        case.additional_expenses = 0
        case.additional_expenses_description=''
        
        if extra_info:
            try:
                json_payload = json.loads(extra_info)
                print json_payload
            
            except:
                raise SuspiciousOperation("Could not parse JSON payload")
                pass

            if "Cancelled by" in json_payload and "Cancellation reason" in json_payload:
                case.cancelled_by =str(json_payload["Cancelled by"]).encode("utf-8")
                print ":%s"%case.cancelled_by

                case.cancelled_reason_description = str(json_payload["Cancellation reason"]).encode("utf-8")
                print ":%s"%case.cancelled_reason_description   
                case.save()             
            else:
                raise ValueError('could not find Cancellation reason in Status update')

    
    if status.lower() == 'signature obtained':  
        if extra_info:
            try:
                json_payload = json.loads(extra_info)
                print json_payload
            
            except:
                raise SuspiciousOperation("Could not parse JSON payload")
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
                case.adult_clients = str(json_payload["adult_client_names"]).encode("utf-8")
            else:
                raise ValueError('cound not find adult_clients in Status update') 
            print case.adult_clients

            if "child_client_names" in json_payload:
                case.child_clients = str(json_payload["child_client_names"]).encode("utf-8")
            else:
                raise ValueError('cound not find adult_clients in Status update')        
            
                    
        else:
            raise SuspiciousOperation("Status update requires extra_info")
        case.is_signature_obtained = True
        case.did_investigator_travel = True
    

    if status.lower() == 'signature not obtained':
        
        if extra_info:
            try:
                json_payload = json.loads(extra_info)
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

                    
            except:
                raise SuspiciousOperation("Status update requires a Mileage description, Out of pocket expenses and More Info")
                pass
        else:
            raise SuspiciousOperation("Status update requires extra_info")
        case.is_signature_obtained = False
        case.did_investigator_travel = True
        case.number_of_adult_signatures_obtained = 0
        case.number_of_child_signatures_obtained = 0

 

    

    if status.lower() == 'closed':
        # info_dict = extra_info + ""
        # info_dict = info_dict.replace("{", "").replace("}", "").replace("\"", "").replace("'", "")

        rating = None
        additional_expenses = None
        additional_expenses_description = None
        number_of_miles = None
        rsn_extra_expenses = None
        rsn_extra_expenses_info = None

        # if "," in info_dict:
        #     info_dict = info_dict.split(",")

        #     for pair in info_dict:
        #         if "Rating" in pair:
        #             rating = pair
        #         elif "Additional Expenses" in pair:
        #             additional_expenses = pair
        #         elif "Number of Miles" in pair:
        #             number_of_miles = pair

        # rating = int(rating.split(":")[1])
        try:
            json_payload = json.loads(extra_info)
            if "More Info" in json_payload:
                additional_expenses_description = json_payload["More Info"]
        except:
            raise SuspiciousOperation("Invalid request; extra_info must be provided when updating status")
        

        if case.did_investigator_travel:
            if not "Mileage Description" in json_payload or not "Out of pocket expenses" in json_payload or not "More Info" in json_payload :
                raise SuspiciousOperation("Status update request must contain all required parameters")
            elif float(json_payload["Out of pocket expenses"]) > 0.0 and len(json_payload["More Info"]) == 0:
                raise SuspiciousOperation("More Info should be provided for the additional expense")
            else:
                additional_expenses = float(json_payload["Out of pocket expenses"])
                number_of_miles = float(json_payload["Mileage Description"])
                additional_expenses_description = str(json_payload["More Info"])
                rsn_extra_expenses = json_payload["RSN extra expenses"]
                rsn_extra_expenses_info = json_payload["RSN extra expenses info"]

                case.additional_expenses = additional_expenses
                case.no_of_miles_travelled = number_of_miles
                case.additional_expenses_description = additional_expenses_description
                case.rsn_extra_expenses = rsn_extra_expenses
                case.rsn_extra_expenses_description = rsn_extra_expenses_info
        
        if 'Rating' in json_payload:
            rating = int(json_payload["Rating"])
            case.rating = rating

        # additional_expenses = float(additional_expenses.split(":")[1])
        # number_of_miles = float(number_of_miles.split(":")[1])

        case.closing_date = datetime.datetime.now()

        import itertools
        important_updates = []
        all_updates = StatusUpdate.objects.filter(case=case)
        signature_obtained = all_updates.filter(status='Signature obtained').order_by("-timestamp")
        signature_not_obtained = all_updates.filter(status='Signature not obtained').order_by("-timestamp")
        client_cancelled = all_updates.filter(status='Client cancelled').order_by("-timestamp")
        important_updates = list(itertools.chain(client_cancelled, signature_obtained, signature_not_obtained))

        if len(important_updates) > 0:
            important_updates.sort(key=lambda d: d.timestamp, reverse=True)
            important_status_update = important_updates[0].status
            print "The important status is %s"%important_status_update
            if important_status_update == 'Signature obtained':
                
                case.is_signature_obtained = True
                case.did_investigator_travel = True
                
                pass
            elif important_status_update == 'Signature not obtained':
                case.is_signature_obtained = False
                case.did_investigator_travel = True
                case.no_of_adult_signatures_obtained = 0
                case.no_of_child_signatures_obtained = 0
                
                pass
            elif important_status_update == 'Client cancelled':
                case.is_signature_obtained = False
                case.did_investigator_travel = False
                case.no_of_adult_signatures_obtained = 0
                case.no_of_child_signatures_obtained = 0
                

                case.no_of_miles_travelled = 0.0
                case.additional_expenses = 0.0
                case.additional_expenses_description=''
                case.rsn_extra_expenses = 0.0
                case.rsn_extra_expenses_description = ''
                
                pass

    case.status_mail = False
    case.save()
    print "case successfully saved"
    if case.created_by:
            new_status_update = StatusUpdate(user=master_broker.user, status=status, case=case, extra_info=extra_info,
                                        read_by_investigator=False, read_by_broker=False, read_by_master_broker=False, updated_by='MB')
            new_status_update.save()
    else:
            new_status_update = StatusUpdate(user=master_broker.user, status=status, case=case, extra_info=extra_info,
                                        read_by_investigator=False, read_by_master_broker=False, updated_by='MB')
            new_status_update.save()
    print "status_update successfully saved"

    status_mail(case,request)

    return HttpResponse('')

def status_mail(case,request):
    import json
    import requests

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    longUrl = 'http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +str(case.pk) + '/?key=' + case.random_string
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
    params = json.dumps({'longUrl': longUrl})
    response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

    
    shortened_url = longUrl
    try:
        shortened_url =  response.json()['id']
    except Exception as ex:
        print str(ex)

        pass
        

    

    investigator = case.investigator
    # print "%s"%investigator.user.first_name
    # print "%s"%investigator.email_one
    # print "%s"%investigator.phone_number_one
    # print "%s"%case.name
    # print "%s"%case.status
    phone_number = investigator.phone_number_one.replace('-', '').replace(' ', '')

    try:
        msg =  EmailMessage('Status Changed', 'Hi '+ investigator.user.first_name +',<br><br> The status of ' + case.name + ' has been changed to ' + case.status +' by ' + master_broker.user.first_name +
            ' ' + master_broker.user.last_name + '. Please visit <a href= "http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +
              str(case.pk) + '/?key=' + case.random_string + '">http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +
              str(case.pk) + '/?key=' + case.random_string + '</a> and view the details. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>',
            'status@rapidsignnow.com', [investigator.email_one])
        msg.content_subtype = "html"
        msg.send()
    except:
        print "Coud not send"
        pass
    try:    
        message = twilio_client.api.account.messages.create(to=phone_number,
                                             from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                                             body='The status of ' + case.name + ' has been changed to ' + case.status +' by ' + master_broker.user.first_name +
              ' ' + master_broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. ')
        case.status_mail = True 
        case.save()
    except Exception as ex:
        print ex
        pass

    if case.created_by:
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
        phone_number = broker.phone_number_one.replace('-', '').replace(' ', '')
        try:
            # send_mail('Status Changed', 'The status of ' + case.name + ' has been changed to ' + case.status +' by ' + master_broker.user.first_name +
            #   ' ' + master_broker.user.last_name + '. Please visit http://' + request.META['HTTP_HOST'] + '/broker/case-details/' +
            #   str(case.pk) + '/?key=' + case.random_string + ' and view the details. ',
            #   'assign@rapidsignnow.com', [broker.email_one],fail_silently=False,)

            msg =  EmailMessage('Status Changed', 'Hi '+ broker.user.first_name +',<br><br> The status of ' + case.name + ' has been changed to ' + case.status +' by ' + master_broker.user.first_name +
                ' ' + master_broker.user.last_name + '. Please visit <a href= "http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +
                str(case.pk) + '/?key=' + case.random_string + '">http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +
                str(case.pk) + '/?key=' + case.random_string + '</a> and view the details. <br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>',
                'status@rapidsignnow.com', [broker.email_one])
            msg.content_subtype = "html"
            msg.send()
        except:
            print "could not send email"
        
        try:
            message = twilio_client.api.account.messages.create(to=phone_number,
                                             from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                                             body='The status of ' + case.name + ' has been changed to ' + case.status +' by ' + master_broker.user.first_name +
              ' ' + master_broker.user.last_name + '. Please visit ' + shortened_url + ' and view the details. ')
            case.status_mail = True 
            case.save()
        except:
            pass

def case_details(request, case_id):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    try:
        case_instance = Case.objects.get(pk=case_id)
    except:
        raise Http404

    
    # if case_instance.created_by.id != broker.id:
    #             raise SuspiciousOperation("Invalid request; You do not have access to this case")
    broker = Broker.objects.all()
    context = dict()
    context['broker'] = broker
    context['case'] = case_instance
    context['amount_paid_to_investigator'] = case_instance.get_investigator_price()
    context['amount_billed_to_law_firm'] = case_instance.get_law_firm_price()
    context['law_firms'] = LawFirm.objects.all()
    context['countries'] = countries
    context['editable'] = case_instance.invoice is None and not case_instance.is_investigator_paid and case_instance.invoice_as_csv is None and case_instance.invoice_as_excel is None
    context['all_documents'] = Document.objects.all()
    client_mobile_phone = case_instance.client_mobile_phone.replace('-', '').replace(' ', '')
    context['client_mobile_phone'] = client_mobile_phone
    client_home_phone = case_instance.client_home_phone.replace('-', '').replace(' ', '')
    context['client_home_phone'] = client_home_phone
    

    context['case_result'] = get_case_final_status(case_instance)

    context['notifications'] = get_notifications(master_broker)

    context['status_updates'] = StatusUpdate.objects.filter(case=case_instance).order_by('-timestamp')
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

        elif request.POST['context'] == 'update-case-details':

            if case_instance.is_investigator_paid:
                raise SuspiciousOperation("Invalid request; Cannot edit case details after case is marked as Paid")
            elif case_instance.invoice:
                raise SuspiciousOperation("Invalid request; Cannot edit case details if an active invoice is associated")

            print "Updating case: %s"%str(case_id)
            # law_firm_id = request.POST['law-firm']
            # law_firm = LawFirm.objects.get(pk=law_firm_id)

            street_one = request.POST['street-1']
            street_two = request.POST['street-2']
            city = request.POST['city']
            state = request.POST['state']
            zip_code = request.POST['zip-code']

            case_instance.client_address.street_one = street_one
            case_instance.client_address.street_two = street_two
            case_instance.client_address.city = city
            case_instance.client_address.state = state
            case_instance.client_address.zip_code = zip_code

            case_instance.client_address.save()
        
            coordinates = case_instance.client_address.get_coordinates()

            if coordinates is not None:
                case_instance.client_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                       str(coordinates['longitude'])
                case_instance.client_address.save()

            name = request.POST['case-name']
            case_type = request.POST['case-type']
            case_type_description = ''

            if ('case-type' not in request.POST or type == ''):
                case_type='default'
            elif (case_type == 'Others'):
                case_type_description = request.POST['case-type-description']
            
            basic_fee_law_firm = request.POST['basic-fee-for-case-law-firm']
            no_of_free_miles_law_firm = request.POST['no-of-free-miles-law-firm']
            mileage_rate_law_firm = request.POST['mileage-rate-law-firm']

            basic_fee_investigator = request.POST['basic-fee-for-case-investigator']
            no_of_free_miles_investigator = request.POST['no-of-free-miles-investigator']
            mileage_rate_investigator = request.POST['mileage-rate-investigator']
            if 'dol' in request.POST and request.POST['dol']:
                dol = request.POST['dol']
                dol_components = dol.split('/')
                dol = datetime.datetime(int(dol_components[2]), int(dol_components[0]), int(dol_components[1]))
                case_instance.is_dol_provided = True
            else:
                dol = datetime.datetime(2017, 1, 1)
                case_instance.is_dol_provided = False

            if 'closing-date' in request.POST and request.POST['closing-date']:
                doc = request.POST['closing-date']
                doc_components = doc.split('/')
                doc = datetime.datetime(int(doc_components[2]), int(doc_components[0]), int(doc_components[1]))
                case_instance.closing_date = doc
            # else:
            #     dos = None
            #     case_instance.closing_date = dos

            if 'edos' in request.POST and request.POST['edos']:
                edos = request.POST['edos']
                edos_components = edos.split('/')
                edos = datetime.datetime(int(edos_components[2]), int(edos_components[0]), int(edos_components[1]))
                case_instance.expected_closing_date = edos
            else:
                edos = None
                case_instance.expected_closing_date = edos
            
            if 'dos' in request.POST and request.POST['dos']:
                dos = request.POST['dos']
                dos_components = dos.split('/')
                dos = datetime.datetime(int(dos_components[2]), int(dos_components[0]), int(dos_components[1]))
                case_instance.date_of_signup = dos
            else:
                dos = case.created_at
                case_instance.date_of_signup = dos

            
            locality = request.POST['locality']

            adult_clients = request.POST['adult-clients']
            child_clients = request.POST['child-clients']

            no_of_miles_travelled = None
            if 'no-of-miles-travelled' in request.POST:
                no_of_miles_travelled = float(request.POST['no-of-miles-travelled'])

            additional_expenses = None
            if 'additional-expenses' in request.POST:
                additional_expenses = float(request.POST['additional-expenses'])
            
            rsn_extra_expenses = None
            if 'rsn-extra-expenses' in request.POST:
                rsn_extra_expenses = float(request.POST['rsn-extra-expenses'])

            expected_payment = request.POST['expected-payment-for-case']

            client_name = request.POST['client-name']
            client_mobile_phone = request.POST['mobile-phone']
            client_home_phone = request.POST['home-phone']
            client_primary_email = request.POST['primary-email']
            client_secondary_email = request.POST['secondary-email']
            client_language = request.POST['language']

            number_of_adult_signatures_required = int(request.POST['number-of-adult-signatures-required'])
            number_of_child_signatures_required = int(request.POST['number-of-child-signatures-required'])

            number_of_adult_signatures_obtained = int(request.POST['number-of-adult-signatures-obtained'])
            number_of_child_signatures_obtained = int(request.POST['number-of-child-signatures-obtained'])



            # case_instance.law_firm = law_firm
            case_instance.name = name
            case_instance.type = case_type
            case_instance.type_description = case_type_description

            case_instance.basic_fee_law_firm = basic_fee_law_firm
            case_instance.no_of_free_miles_law_firm = no_of_free_miles_law_firm
            case_instance.mileage_rate_law_firm = mileage_rate_law_firm

            if not case_instance.is_investigator_paid:
                case_instance.basic_fee_investigator = basic_fee_investigator
                case_instance.no_of_free_miles_investigator = no_of_free_miles_investigator
                case_instance.mileage_rate_investigator = mileage_rate_investigator

            case_instance.dol = dol
            case_instance.locality = locality

            if no_of_miles_travelled:
                case_instance.no_of_miles_travelled = no_of_miles_travelled

            if additional_expenses:
                case_instance.additional_expenses = additional_expenses

            if rsn_extra_expenses:
                case_instance.rsn_extra_expenses = rsn_extra_expenses
            
            case_instance.expected_payment = expected_payment
            case_instance.adult_clients = adult_clients
            
            case_instance.child_clients = child_clients

            case_instance.client_name = client_name
            case_instance.client_mobile_phone = client_mobile_phone
            case_instance.client_home_phone = client_home_phone
            case_instance.client_primary_email = client_primary_email
            case_instance.client_secondary_email = client_secondary_email
            case_instance.client_language = client_language

            case_instance.number_of_adult_signatures_required = number_of_adult_signatures_required
            case_instance.number_of_child_signatures_required = number_of_child_signatures_required

            case_instance.number_of_adult_signatures_obtained = number_of_adult_signatures_obtained
            case_instance.number_of_child_signatures_obtained = number_of_child_signatures_obtained

            if 'document' in request.POST:
                documents = request.POST.getlist('document')
                for document in documents:
                    if AttachedDocument.objects.filter(document=document).filter(case=case_instance):     
                        print "Already attached to this case"
                    else:   
                        attached_document = Document.objects.get(pk=document)
                        new_attached_document = AttachedDocument(case=case_instance, document=attached_document)
                        new_attached_document.save()
            case_instance.save()
            
            
            context['updated'] = True
        else:
            pass

    attached_documents = AttachedDocument.objects.filter(case = case_instance)
    context['attached_documents'] = attached_documents
    documents  = Document.objects.filter(law_firm=case_instance.law_firm)

    flag = 0
    documents_available = []
    for document in documents:
        flag = 0
        for attached_document in attached_documents:
            if document.pk == attached_document.document.pk:
                flag = 1
        if flag == 0:
            documents_available.append(document)
    context['documents'] = documents_available
    client_mobile_phone = case_instance.client_mobile_phone.replace('-', '').replace(' ', '')
    context['client_mobile_phone'] = client_mobile_phone
    client_home_phone = case_instance.client_home_phone.replace('-', '').replace(' ', '')
    context['client_home_phone'] = client_home_phone
    return render(request, 'master_broker/case_details.html', context)

def my_profile(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['master_broker'] = master_broker
    
    context['notifications'] = get_notifications(master_broker)

    return render(request, 'master_broker/my_profile.html', context)

def get_investigator_rates(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or not request.is_ajax() or 'id' not in request.POST:
        return HttpResponseRedirect('/')

    investigator_id = request.POST['id']
    investigator = Investigator.objects.get(pk=investigator_id)

    context = dict()

    context['basic_in_area'] = investigator.rates.default_in_area_payment_when_signature_not_obtained
    context['basic_out_of_area'] = investigator.rates.default_out_of_area_payment_when_signature_not_obtained
    context['free_miles'] = investigator.rates.mileage_threshold
    context['mileage_rate'] = investigator.rates.mileage_compensation_rate

    return JsonResponse(context)

def get_law_firm_rates(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or not request.is_ajax() or 'id' not in request.POST:
        return HttpResponseRedirect('/')

    law_firm_id = request.POST['id']
    law_firm = LawFirm.objects.get(pk=law_firm_id)

    context = dict()

    context['basic_in_area'] = law_firm.rates.default_in_area_payment_when_signature_not_obtained
    context['basic_out_of_area'] = law_firm.rates.default_out_of_area_payment_when_signature_not_obtained
    context['free_miles'] = law_firm.rates.mileage_threshold
    context['mileage_rate'] = law_firm.rates.mileage_compensation_rate

    return JsonResponse(context)

def mark_as_read(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')
    
    if not request.GET:
        return HttpResponse('')
    
    request_id = request.GET['id']
    request_type = request.GET['type']
    
    if request_type == 'status':
        status_update_instance = StatusUpdate.objects.get(pk=request_id)
        status_update_instance.read_by_master_broker = True
        status_update_instance.save()
    elif request_type == 'acceptance':
        acceptance_instance = CaseAcceptanceUpdate.objects.get(pk=request_id)
        acceptance_instance.read_by_master_broker = True
        acceptance_instance.save()
    
    return HttpResponse('')

def change_password(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
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


    context['notifications'] = get_notifications(master_broker)
    return render(request, 'master_broker/change_password.html', context)

def get_all_notifications(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')
    
    context = dict()

    unread_statuses = StatusUpdate.objects.filter().order_by('-timestamp')
    status_notifications = []
    unread_count = 0

    for status in unread_statuses:
        notification = dict()

        notification['status_id'] = status.pk
        notification['case_id'] = status.case.pk
        notification['case_name'] = status.case.name
        if status.user == master_broker:
            notification['investigator'] = 'You'
        elif status.updated_by == 'MB':
            notification['investigator'] = status.user.first_name + ' ' + status.user.last_name
        elif status.updated_by == 'BR':
            notification['investigator'] = status.user.first_name + ' ' + status.user.last_name
        else:
            notification['investigator'] = status.case.investigator.user.first_name + ' ' + status.case.investigator.user.last_name
        notification['status'] = status.status
        notification['timestamp'] = status.timestamp
        notification['read'] = status.read_by_broker
        notification['type'] = 'status'

        if not status.read_by_master_broker:
            unread_count += 1

        status_notifications.append(notification)

    
    unread_acceptances = CaseAcceptanceUpdate.objects.filter().order_by('-timestamp')
    acceptance_notifications = []

    for acceptance in unread_acceptances:
        notification = dict()

        notification['acceptance_id'] = acceptance.pk
        notification['case_id'] = acceptance.case.pk
        notification['case_name'] = acceptance.case.name
        notification['investigator'] = acceptance.investigator.user.first_name + ' ' + acceptance.investigator.user.last_name
        notification['is_accepted'] = acceptance.is_accepted
        notification['timestamp'] = acceptance.timestamp
        notification['read'] = acceptance.read_by_master_broker
        notification['type'] = 'acceptance'

        if not acceptance.read_by_master_broker:
            unread_count += 1

        acceptance_notifications.append(notification)

    notifications = status_notifications + acceptance_notifications
    notifications = sorted(notifications, key=lambda notification: notification['timestamp'])
    context['notifications'] = reversed(notifications)
    context['unread_count'] = unread_count

    return render(request, 'master_broker/all_notifications.html', context)

def get_case_final_status(case):
    case_result = None

    if (case.is_signature_obtained):
        return "Signature obtained"
    elif (case.did_investigator_travel):
        return "Signature not obtained"
    else:
        return "Client cancelled"

def delete_document(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'attached_document_id' not in request.POST:
        return HttpResponseRedirect('/')

    attached_document_id = request.POST['attached_document_id']
    attached_document_instance = AttachedDocument.objects.get(pk=attached_document_id)
    
    attached_document_instance.delete()
    

    return HttpResponse('')

def download_doc(request,file_id):
    
    d = Document.objects.get(id = file_id)        
    
    mime = magic.Magic(mime=True) 
    output = "output" 
    urllib.urlretrieve(d.file.url, output)
    mimes = mime.from_file(output)
    ext = mimetypes.guess_all_extensions(mimes)[0] 
    # os.rename(output, output+ext) # Rename file
    # pdf = d.file.file.read()
    
    
    # law_firm_email = 'ankit.singh@42hertz.com'
    # email_body = 'Find attached the invoice'
    # message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
    # message.attach('Attachment'+ext, pdf, mimes)
    # message.send()
    
    response = HttpResponse(d.file, content_type=mimes)
    response['Content-Disposition'] = 'attachment; filename=%s' % d.file_name

    return response

def fetch_resources(uri, rel):
    path = join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return path

def mark_case(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
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

            longUrl = 'http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +str(case.pk) + '/?key=' + case.random_string
            post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
            params = json.dumps({'longUrl': longUrl})
            response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

            
            shortened_url = longUrl
            try:
                shortened_url =  response.json()['id']
            except:
                pass

            

            investigator = case.investigator
            # print "%s"%investigator.user.first_name
            # print "%s"%investigator.email_one
            # print "%s"%investigator.phone_number_one
            # print "%s"%case.name
            # print "%s"%case.status
            phone_number = investigator.phone_number_one.replace('-', '').replace(' ', '')
            
            try:
                send_mail('Attention Required !', '' + master_broker.user.first_name + ' ' + master_broker.user.last_name + ' has marked the case ' + case.name +' as attention required which was assigned to '+ case.investigator.user.first_name +' ' +case.investigator.user.last_name  + '. Please visit http://' + request.META['HTTP_HOST'] + '/investigator/case-details/' +
                    str(case.pk) + '/?key=' + case.random_string + ' and view the details. ',
                    'assign@rapidsignnow.com', [investigator.email_one],fail_silently=False,)
            except:
                pass
            
            try:
                message = twilio_client.api.account.messages.create(to=phone_number,
                                                    from_=settings.TWILIO_OUTGOING_PHONE_NUMBER,
                                                    body='' + master_broker.user.first_name + ' ' + master_broker.user.last_name + ' has marked the case ' + case.name +' as attention required which was assigned to '+ case.investigator.user.first_name +' ' +case.investigator.user.last_name  + '. Please visit' + shortened_url + ' and view the details. ')
            except:
                pass
            print "case marked"
    elif request.POST['mark'] == "unmark":
        case.is_attention_required = False
        case.save()
        print "case unmarked"




    return HttpResponse('')

def dashboard(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['notifications'] = get_notifications(master_broker)

    # in_progress = 
    total_cases  = Case.objects.filter(~Q(status= "Duplicate delete"))
    total_cases_count  = total_cases.count()
    client_cancelled = total_cases.filter(Q(status = "Closed") | Q(status = "Client cancelled") ).filter(Q(is_signature_obtained = False) & Q(did_investigator_travel = False))
    client_cancelled_count = client_cancelled.count()
    client_cancelled_percent = float(client_cancelled_count * 100 ) / total_cases_count
    signature_obtained = Case.objects.filter(is_signature_obtained = True)
    signature_obtained_count = signature_obtained.count()
    signature_obtained_percent = float(signature_obtained_count * 100 ) /total_cases_count
    signature_not_obtained = Case.objects.filter(Q(is_signature_obtained = False) & Q(did_investigator_travel = True))
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
    context['case_status_inactive']  = round( (float(case_status_inactive.count() * 100) / total_cases_for_case_status_donut) ,2)
    context['case_status_in_progress']  = round( (float(case_status_in_progress.count() * 100) / total_cases_for_case_status_donut) ,2)
    context['case_status_called_and_texted']  = round( (float(case_status_called_and_texted.count() * 100) / total_cases_for_case_status_donut) ,2)
    context['case_status_client_contacted']  = round( (float(case_status_client_contacted.count() * 100) / total_cases_for_case_status_donut) ,2)
    context['case_status_client_meeting_set']  = round( (float(case_status_client_meeting_set.count() * 100) / total_cases_for_case_status_donut) ,2)
    context['case_status_client_rescheduled']  = round( (float(case_status_client_rescheduled.count() * 100) / total_cases_for_case_status_donut) ,2)
    # context['case_status_client_cancelled']  = round( (float(case_status_client_cancelled.count() * 100) / total_cases_for_case_status_donut) ,2)
    context['case_signature_obtained']  = round( (float(case_signature_obtained.count() * 100) / total_cases_for_case_status_donut) ,2)
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

    #for invetigator table
    investigators = Investigator.objects.all()
    # sorted_results = sorted(investigators, key= lambda t: t.cases_in_month(), reverse=True)
    # investigators = sorted_results[0:10]
    investigators_for_top_table = []
    cases_assigned_to_investigator_for_top_table = []
    cases_with_signature_percent_for_top_table = []
    for investigator in investigators:
        cases_assigned_to_investigator = Case.objects.filter(investigator=investigator).filter(~Q(status= "Duplicate delete")).filter(created_at__gt=(timezone.now() - timedelta(days=30)))
        cases_with_signature_obtained = cases_assigned_to_investigator.filter(is_signature_obtained = True)
        cases_assigned_to_investigator_for_top_table.append(len(cases_assigned_to_investigator))
        if len(cases_assigned_to_investigator) != 0 and len(cases_with_signature_obtained) != 0:
            percent_signature_obtained = round(float(len(cases_with_signature_obtained)*100 / len(cases_assigned_to_investigator)),2)
            cases_with_signature_percent_for_top_table.append(percent_signature_obtained)
            investigators_for_top_table.append(investigator)
        else:
            percent_signature_obtained = 0
            cases_with_signature_percent_for_top_table.append(percent_signature_obtained)
            investigators_for_top_table.append(investigator)
    
    investigator_data = zip(investigators_for_top_table,cases_assigned_to_investigator_for_top_table,cases_with_signature_percent_for_top_table)
    investigator_data.sort(key = lambda t: t[1],reverse=True)
    context["investigators_data"] = investigator_data[0:10]


    #cases added and closed graph
    cases_added_list = []
    cases_closed_list = []
    monthly_revenue_list = [] 
    monthly_proposed_revenue_list = []
    daily_revenue_list = [] 
    daily_proposed_revenue_list = []
    broker_revenue_list = []
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
    cases_added_list = zip(dates, cases_added)
    cases_closed_list = zip(dates, cases_closed)

    brokers = Broker.objects.all()
    context['brokers'] = brokers

    #revenue for RSN graph
    profit_per_month = []
    proposed_profit_per_month = []
    profit_per_day = []
    proposed_profit_per_day = []
    profit_per_day_for_broker = []
    dates = []
    months = []
    weeks = []
    broker_ids = []
    data_for_broker = []
    date = timezone.localtime(timezone.now()).date() - timedelta(days=31)
    # daily revenue for RSN graph
    for day in range(0, 32):
        profit = 0
        profit_including_client_cancelled = 0
        current_date = date + timedelta(days=day)
        next_date = date + timedelta(days=day + 1)
        cases_on_current_date = total_cases.filter(created_at__gte = current_date).filter(created_at__lt = next_date).filter(status = "Closed")
        for case in cases_on_current_date:
            profit = profit + case.amount_billed_to_law_firm - case.amount_paid_to_investigator
        cases_on_current_date_including_client_cancelled = total_cases.filter(created_at__gte = current_date).filter(created_at__lt = next_date).filter(status = "Client cancelled")
        for case in cases_on_current_date_including_client_cancelled:
            profit_including_client_cancelled = profit_including_client_cancelled  + case.get_proposed_law_firm_price()  - case.get_proposed_investigator_price()
        profit_per_day.append(profit)
        proposed_profit_per_day.append(profit_including_client_cancelled+profit)
        dates.append(current_date)

    
    daily_revenue_list = zip(dates, profit_per_day)
    daily_proposed_revenue_list = zip(dates,proposed_profit_per_day)


    # monthly revenue for RSN graph
    date = timezone.localtime(timezone.now()).date()
    date = date.replace(day=1)
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    no_of_months =  range(0,12)
    month_names = ['January','February','March','April','May','June','July','August','September','October','November','December']
    for index in range(1,7):
        profit = 0
        profit_including_client_cancelled = 0
        first_day_of_month = date
        month = date.month
        days = month_days[no_of_months[month-1]]
        last_day_of_month = date.replace(day=days)
        cases_on_current_date = total_cases.filter(created_at__gte = first_day_of_month).filter(created_at__lt = last_day_of_month).filter(status = "Closed")
        for case in cases_on_current_date:
            profit = profit + case.amount_billed_to_law_firm - case.amount_paid_to_investigator
        cases_on_current_date_including_client_cancelled = total_cases.filter(created_at__gt = first_day_of_month).filter(created_at__lt = last_day_of_month).filter(status = "Client cancelled")
        for case in cases_on_current_date_including_client_cancelled:
            profit_including_client_cancelled = profit_including_client_cancelled  + case.get_proposed_law_firm_price()  - case.get_proposed_investigator_price()
        proposed_profit_per_month.append(profit_including_client_cancelled+profit)
        profit_per_month.append(profit)
        months.append(first_day_of_month)
        date = date - timedelta(days=month_days[no_of_months[month-2]])
    # context['total_revenue_graph_monthly'] = zip(months, profit_per_month)
    # context['total_proposed_revenue_graph_monthly'] = zip(months, proposed_profit_per_month)
    monthly_revenue_list = zip(months, profit_per_month)
    monthly_proposed_revenue_list = zip(months, proposed_profit_per_month)
    #broker revenue graph
    for broker in brokers:
        zippped_data = []
        dates = []
        profit_per_day_for_broker = []
        date = timezone.localtime(timezone.now()).date() - timedelta(days=31)
        for day in range(0, 32):
            profit = 0
            current_date = date + timedelta(days=day)
            next_date = date + timedelta(days=day + 1)
            cases_on_current_date = total_cases.filter(created_by = broker).filter(created_at__gte = current_date).filter(created_at__lt = next_date).filter(status = "Closed")
            for case in cases_on_current_date:
                profit = profit + case.amount_billed_to_law_firm - case.amount_paid_to_investigator
            profit_per_day_for_broker.append(profit)
            dates.append(current_date)
        zipped_data = zip(dates,profit_per_day_for_broker)
        data_for_broker.append(zipped_data)
    
    broker_revenue_list = data_for_broker
        
    context["broker"] = brokers
    context["brokers_count"] = brokers.count()
    
    #USA map graph
    states_array = []
    cases_in_state = []
    for short_form, state_name in states.iteritems():
        cases = total_cases.filter(Q(client_address__state = state_name)|Q(client_address__state = short_form))
        states_array.append(state_name)
        cases_in_state.append(cases.count)
    
    zipped_data_for_map_graph = zip(states_array,cases_in_state)
    context["states"] = states_array
    context["map_data"] = zipped_data_for_map_graph

    #broker table data
    broker_for_percentage_of_cases_closed = []
    percentage_of_cases_closed_for_broker = []
    broker_no_of_cases_added = []
    broker_no_of_cases_closed = []
    for broker in brokers:
        no_of_cases_added = 0
        no_of_cases_closed = 0
        date = timezone.localtime(timezone.now()).date() - timedelta(days=31)
        cases_on_current_date = total_cases.filter(created_by = broker).filter(created_at__gte = date)
        cases_on_current_date_closed = cases_on_current_date.filter(status = "Closed")
        no_of_cases_added = cases_on_current_date.count()
        no_of_cases_closed = cases_on_current_date_closed.count()
        if no_of_cases_added != 0 and no_of_cases_closed != 0:
            closing_percent = round(float(no_of_cases_closed * 100) / no_of_cases_added , 2)
            percentage_of_cases_closed_for_broker.append(closing_percent)
            broker_for_percentage_of_cases_closed.append(broker)
            broker_no_of_cases_added.append(no_of_cases_added)
            broker_no_of_cases_closed.append(no_of_cases_closed)

        else:
            closing_percent = 0
            percentage_of_cases_closed_for_broker.append(closing_percent)
            broker_for_percentage_of_cases_closed.append(broker)
            broker_no_of_cases_added.append(no_of_cases_added)
            broker_no_of_cases_closed.append(no_of_cases_closed)
    
    broker_closing_percent_data = zip(broker_for_percentage_of_cases_closed,broker_no_of_cases_added,broker_no_of_cases_closed,percentage_of_cases_closed_for_broker)
    broker_closing_percent_data.sort(key = lambda t: t[3],reverse=True)
    
    context["broker_closing_percent_data"] = broker_closing_percent_data
    if request.POST:
        if 'from' in request.POST and request.POST['from'] != '':
            from_date = request.POST['from']
            from_components = from_date.split('/')
            from_date = datetime.datetime(int(from_components[2]), int(from_components[0]), int(from_components[1]))

            context['from'] = request.POST['from']
                
            
        if 'to' in request.POST and request.POST['to'] != '':
            to_date = request.POST['to']
            to_components = to_date.split('/')
            to_date = datetime.datetime(int(to_components[2]), int(to_components[0]), int(to_components[1]))
            context['to'] = request.POST['to']


            
        if 'context' in request.POST and request.POST['context'] == 'cases-added-closed':
            print "inside"
            dates = []
            cases_added = []
            cases_closed = []
            date = from_date
            date_range = to_date - from_date
            date_range = date_range.days
            for day in range(0,date_range+1):
                current_date = date + timedelta(days=day)
                next_date = date + timedelta(days=day + 1)
                cases_on_current_date = total_cases.filter(created_at__gte = current_date).filter(created_at__lt = next_date)
                cases_added.append(cases_on_current_date.count())
                dates.append(current_date.date())
            cases_added_list = zip(dates,cases_added)

            
            
            for day in range(0,date_range+1):
                current_date = date + timedelta(days=day)
                next_date = date + timedelta(days=day + 1)
                cases_closed_on_current_date = total_cases.filter(closing_date__gte = current_date).filter(closing_date__lt = next_date)
                cases_closed.append(cases_closed_on_current_date.count())
            cases_closed_list = zip(dates,cases_closed)
            context["range_for"] = "cases-added-closed"

        elif 'context' in request.POST and request.POST['context'] == 'rsn-revenue':
            profit_per_month = []
            proposed_profit_per_month = []
            profit_per_day = []
            proposed_profit_per_day = []
            profit_per_day_for_broker = []
            dates = []
            months = []
            weeks = []

            date = from_date
            date_range = to_date - from_date
            date_range = date_range.days
            for day in range(0, date_range+1):
                profit = 0
                profit_including_client_cancelled = 0
                current_date = date + timedelta(days=day)
                next_date = date + timedelta(days=day + 1)
                cases_on_current_date = total_cases.filter(created_at__gte = current_date).filter(created_at__lt = next_date).filter(status = "Closed")
                for case in cases_on_current_date:
                    profit = profit + case.amount_billed_to_law_firm - case.amount_paid_to_investigator
                cases_on_current_date_including_client_cancelled = total_cases.filter(created_at__gte = current_date).filter(created_at__lt = next_date).filter(status = "Client cancelled")
                for case in cases_on_current_date_including_client_cancelled:
                    profit_including_client_cancelled = profit_including_client_cancelled  + case.get_proposed_law_firm_price()  - case.get_proposed_investigator_price()
                profit_per_day.append(profit)
                proposed_profit_per_day.append(profit_including_client_cancelled+profit)
                dates.append(current_date.date())

            
            # context['total_revenue_graph_daily'] = zip(dates, profit_per_day)
            # context['total_proposed_revenue_graph_daily'] = zip(dates,proposed_profit_per_day)
            daily_revenue_list = zip(dates, profit_per_day)
            daily_proposed_revenue_list = zip(dates,proposed_profit_per_day)
            

            # monthly revenue for RSN graph
            date = to_date
            # month_range = relativedelta.relativedelta(to_date, from_date)
            
            month_range = (to_date.year - from_date.year)*12  + (to_date.month - from_date.month)
            month_range = month_range + 1
            date = date.replace(day=1)
            month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            no_of_months =  range(0,12)
            month_names = ['January','February','March','April','May','June','July','August','September','October','November','December']
            for index in range(1,month_range+1):
                profit = 0
                profit_including_client_cancelled = 0
                first_day_of_month = date
                month = date.month
                days = month_days[no_of_months[month-1]]
                last_day_of_month = date.replace(day=days)
                cases_on_current_date = total_cases.filter(created_at__gte = first_day_of_month).filter(created_at__lt = last_day_of_month).filter(status = "Closed")
                for case in cases_on_current_date:
                    profit = profit + case.amount_billed_to_law_firm - case.amount_paid_to_investigator
                cases_on_current_date_including_client_cancelled = total_cases.filter(created_at__gt = first_day_of_month).filter(created_at__lt = last_day_of_month).filter(status = "Client cancelled")
                for case in cases_on_current_date_including_client_cancelled:
                    profit_including_client_cancelled = profit_including_client_cancelled  + case.get_proposed_law_firm_price()  - case.get_proposed_investigator_price()
                proposed_profit_per_month.append(profit_including_client_cancelled+profit)
                profit_per_month.append(profit)
                months.append(first_day_of_month.date())
                date = date - timedelta(days=month_days[no_of_months[month-2]])
            # context['total_revenue_graph_monthly'] = zip(months, profit_per_month)
            # context['total_proposed_revenue_graph_monthly'] = zip(months, proposed_profit_per_month)
            monthly_revenue_list = zip(months, profit_per_month)
            monthly_proposed_revenue_list = zip(months, proposed_profit_per_month)

            context["range_for"] = "rsn-revenue"

        elif 'context' in request.POST and request.POST['context'] == 'broker-revenue':

            broker_ids = []
            data_for_broker = []
            brokers = Broker.objects.all()
            for broker in brokers:
                zippped_data = []
                dates = []
                profit_per_day_for_broker = []
                date = from_date
                date_range = to_date - from_date
                date_range = date_range.days
                for day in range(0, date_range + 1):
                    profit = 0
                    current_date = date + timedelta(days=day)
                    next_date = date + timedelta(days=day + 1)
                    cases_on_current_date = total_cases.filter(created_by = broker).filter(created_at__gte = current_date).filter(created_at__lt = next_date).filter(status = "Closed")
                    for case in cases_on_current_date:
                        profit = profit + case.amount_billed_to_law_firm - case.amount_paid_to_investigator
                    profit_per_day_for_broker.append(profit)
                    dates.append(current_date.date())
                zipped_data = zip(dates,profit_per_day_for_broker)
                data_for_broker.append(zipped_data)
            
            broker_revenue_list = data_for_broker
            context["range_for"] = "broker-revenue"
                
    context["broker_revenue"] = broker_revenue_list
    context['total_revenue_graph_monthly'] = monthly_revenue_list
    context['total_proposed_revenue_graph_monthly'] = monthly_proposed_revenue_list
    context['cases_added'] = cases_added_list
    context['cases_closed'] = cases_closed_list
    context['total_revenue_graph_daily'] =     daily_revenue_list
    context['total_proposed_revenue_graph_daily'] = daily_proposed_revenue_list
    
    return render(request, 'master_broker/dashboard.html',context)

def pending_receivables(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['cases'] = []

    cases = Case.objects.filter(is_marked_for_payment = True).filter(approved_by_rsn = True).filter(has_law_firm_paid=False).order_by('-pk')
    
    law_firms = LawFirm.objects.all()
    
    brokers = Broker.objects.all()
    master_brokers = MasterBroker.objects.all()
    
    
    all_investigators = Investigator.objects.all()

    context['investigators'] = all_investigators
    context['brokers'] = brokers
    context['master_brokers'] = master_brokers
    context['notifications'] = get_notifications(master_broker)

    context['law_firms'] = law_firms
    cases_by_broker = []
    cases_by_master_broker = []
    context['next_page_url'] = ''
    no_of_cases = 50


    if request.POST and 'context' in request.POST and request.POST['context'] == "raise-single-dispute":

        if 'case_id' in request.POST and request.POST['case_id'] != "":
            case_id = request.POST['case_id']
            dispute_description = request.POST['dispute-reason']
            case = Case.objects.get(pk=case_id)
            case.is_dispute_raised = True
            case.dispute_description = dispute_description
            case.save()
            print case_id
            print dispute_description
            print "-- Single dispute raised --" 

    elif request.POST and 'context' in request.POST and request.POST['context'] == "resolve-single-dispute":
        if 'case_id' in request.POST and request.POST['case_id'] != "":
            case_id = request.POST['case_id']
            case = Case.objects.get(pk=case_id)
            case.is_dispute_raised = False
            case.dispute_description = ''
            case.save()
            print case_id
            print "-- Single dispute resolved --" 

    elif request.POST and 'context' in request.POST and request.POST['context'] == "raise-combined-dispute":
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

    elif request.POST and 'context' in request.POST and request.POST['context'] == "resolve-combined-dispute":
        print "--Combined dispute resolved --"
        if 'case_ids' in request.POST and request.POST['case_ids'] != "":
            try:
                case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
            except:
                print "No value for case_ids or case_ids not found in request.POST"

            for case_id in case_ids:
                print case_id
                case = Case.objects.get(pk=case_id)
                case.is_dispute_raised = False
                case.dispute_description = ''
                case.save()

    if (request.method == 'GET'):
        # If filters were removed
        cases = Case.objects.filter(is_marked_for_payment = True).filter(approved_by_rsn = True).filter(has_law_firm_paid=False).order_by('-pk')
        if 'filtering' in  request.GET and request.GET['filtering'] == 'on':
                
            context['next_page_url'] = 'filtering=on&'
            if 'from' in request.GET and request.GET['from'] != '':
                from_date = request.GET.get('from')
                from_components = from_date.split('/')
                context['next_page_url'] += 'from='+str(from_date)+'&'
                from_date = datetime.datetime(int(from_components[2]), int(from_components[0]), int(from_components[1]))
                cases = cases.filter(created_at__gte=from_date)

                context['from'] = request.GET['from']
                context['is_filter_applied'] = 1
                
            
            if 'to' in request.GET and request.GET['to'] != '':
                to_date = request.GET.get('to')
                to_components = to_date.split('/')
                context['next_page_url'] += 'to='+str(to_date)+'&'
                to_date = datetime.datetime(int(to_components[2]), int(to_components[0]), int(to_components[1]))
                cases = cases.filter(created_at__lt=to_date)
                context['to'] = request.GET['to']
                context['is_filter_applied'] = 1
                
            if 'law-firm' in request.GET and request.GET['law-firm'] != '':
                law_firm_id = request.GET['law-firm']
                law_firm = LawFirm.objects.get(pk=int(law_firm_id))
                print "The selected_lawfirm is "
                print law_firm_id
                context['selected_firm_id'] = law_firm_id
                cases = cases.filter(law_firm = law_firm)
                context['selected_firm'] = law_firm_id
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'law-firm='+law_firm_id+'&'
            

            if 'investigator' in request.GET and request.GET['investigator'] != '':
                investigator_id = request.GET['investigator']
                investigator = Investigator.objects.get(pk=investigator_id)
                # context['selected_investigator_id'] = investigator_id
                cases = cases.filter(investigator = investigator)
                context['selected_investigator'] = investigator_id
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'investigator='+investigator_id+'&'
                

            if 'status' in request.GET and request.GET['status'] != '':
                status = request.GET['status']
                if status == "Signature obtained":
                    cases = cases.filter(is_signature_obtained = True)
                    context['selected_status'] = request.GET['status']
                    context['is_filter_applied'] = 1
                    context['next_page_url'] += 'status='+status+'&'
                else:
                    cases = cases.filter(is_signature_obtained = False)
                    context['selected_status'] = request.GET['status']
                    context['is_filter_applied'] = 1
                    context['next_page_url'] += 'status='+status+'&'

            q_array = []
            
            if 'broker' in request.GET and request.GET['broker'] != '':
                broker_id = request.GET['broker']
                broker = Broker.objects.get(pk=broker_id)
                # cases_by_broker = cases.filter(created_by = broker)

                q_array.append(Q(created_by = broker))

                # cases = cases.filter(created_by = broker)
                # case_by_broker = cases
                context['selected_broker'] = broker_id
                context['is_filter_applied'] = 1   
                context['next_page_url'] += 'broker='+broker_id+'&'

            if 'master-broker' in request.GET and request.GET['master-broker'] !='':  
                master_broker_id = request.GET['master-broker']
                master_broker = MasterBroker.objects.get(pk=master_broker_id)

                context['selected_master_broker'] = master_broker_id
                cases_by_master_broker = cases.filter(created_by_master = master_broker)
                q_array.append(Q(created_by_master = master_broker))
                context['is_filter_applied'] = 1   
                context['next_page_url'] += 'master-broker='+master_broker_id+'&'
            
            if len(q_array):
                cases = cases.filter(reduce(OR, q_array))  

        
    elif request.method == 'POST' and 'context' in request.POST and (request.POST['context'] == 'remove-filters' or request.POST['context'] == 'clear-search'):
        cases = Case.objects.filter(is_marked_for_payment = True).filter(approved_by_rsn = True).filter(has_law_firm_paid=False).order_by('-pk')
    
    # if no_of_cases != 'All':
    #     paginator = Paginator(cases, no_of_cases) # Show 25 contacts per page

    #     page = request.GET.get('page')
    #     try:
    #         cases = paginator.page(page)
    #     except PageNotAnInteger:
    #         # If page is not an integer, deliver first page.
    #         cases = paginator.page(1)
    #     except EmptyPage:
    #         # If page is out of range (e.g. 9999), deliver last page of results.
    #         cases = paginator.page(paginator.num_pages)
    # elif no_of_cases == 'All' :
    #     paginator = Paginator(cases, 1000) # Show 25 contacts per page

    #     page = request.GET.get('page')
    #     try:
    #         cases = paginator.page(page)
    #     except PageNotAnInteger:
    #         # If page is not an integer, deliver first page.
    #         cases = paginator.page(1)
    #     except EmptyPage:
    #         # If page is out of range (e.g. 9999), deliver last page of results.
    #         cases = paginator.page(paginator.num_pages)
    cases = Case.objects.filter(is_marked_for_payment = True).filter(approved_by_rsn = True).filter(has_law_firm_paid=False).order_by('-pk')
    context['no_of_cases'] = no_of_cases    
    print (no_of_cases)
    print len(cases)    
    context['cases'] = cases

    return render(request, 'master_broker/pending_receivables.html', context)

def collected_payments(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['cases'] = []

    cases = Case.objects.filter(has_law_firm_paid=True).order_by('-pk')
    
    # print (cases)
    # cases = Case.objects.all()
    law_firms = LawFirm.objects.all()

    
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
    
    
    all_investigators = Investigator.objects.all()
    for investigator in all_investigators:
        investigator.languages = ast.literal_eval(investigator.languages)

    context['investigators'] = all_investigators
    context['brokers'] = brokers
    context['master_brokers'] = master_brokers
    context['notifications'] = get_notifications(master_broker)

    context['law_firms'] = law_firms
    cases_by_broker = []
    cases_by_master_broker = []
    context['next_page_url'] = ''
    no_of_cases = 50


    if request.POST and 'context' in request.POST and request.POST['context'] == "raise-single-dispute":

        if 'case_id' in request.POST and request.POST['case_id'] != "":
            case_id = request.POST['case_id']
            dispute_description = request.POST['dispute-reason']
            case = Case.objects.get(pk=case_id)
            case.is_dispute_raised = True
            case.dispute_description = dispute_description
            case.save()
            print dispute_description
            print case_id
            print "-- Single dispute raised --" 


    if (request.method == 'GET'):
        # If filters were removed
        cases = Case.objects.filter(has_law_firm_paid=True).order_by('-pk')
        if 'filtering' in  request.GET and request.GET['filtering'] == 'on':
                
            context['next_page_url'] = 'filtering=on&'
            if 'from' in request.GET and request.GET['from'] != '':
                from_date = request.GET.get('from')
                from_components = from_date.split('/')
                context['next_page_url'] += 'from='+str(from_date)+'&'
                from_date = datetime.datetime(int(from_components[2]), int(from_components[0]), int(from_components[1]))
                cases = cases.filter(created_at__gte=from_date)

                context['from'] = request.GET['from']
                context['is_filter_applied'] = 1
                
            
            if 'to' in request.GET and request.GET['to'] != '':
                to_date = request.GET.get('to')
                to_components = to_date.split('/')
                context['next_page_url'] += 'to='+str(to_date)+'&'
                to_date = datetime.datetime(int(to_components[2]), int(to_components[0]), int(to_components[1]))
                cases = cases.filter(created_at__lt=to_date)
                context['to'] = request.GET['to']
                context['is_filter_applied'] = 1
                
            if 'law-firm' in request.GET and request.GET['law-firm'] != '':
                law_firm_id = request.GET['law-firm']
                law_firm = LawFirm.objects.get(pk=int(law_firm_id))
                print "The selected_lawfirm is "
                print law_firm_id
                context['selected_firm_id'] = law_firm_id
                cases = cases.filter(law_firm = law_firm)
                context['selected_firm'] = law_firm_id
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'law-firm='+law_firm_id+'&'
            

            if 'investigator' in request.GET and request.GET['investigator'] != '':
                investigator_id = request.GET['investigator']
                investigator = Investigator.objects.get(pk=investigator_id)
                # context['selected_investigator_id'] = investigator_id
                cases = cases.filter(investigator = investigator)
                context['selected_investigator'] = investigator_id
                context['is_filter_applied'] = 1
                context['next_page_url'] += 'investigator='+investigator_id+'&'
                

            if 'status' in request.GET and request.GET['status'] != '':
                status = request.GET['status']
                if status == "Signature obtained":
                    cases = cases.filter(is_signature_obtained = True)
                    context['selected_status'] = request.GET['status']
                    context['is_filter_applied'] = 1
                    context['next_page_url'] += 'status='+status+'&'
                else:
                    cases = cases.filter(is_signature_obtained = False)
                    context['selected_status'] = request.GET['status']
                    context['is_filter_applied'] = 1
                    context['next_page_url'] += 'status='+status+'&'

            q_array = []
            
            if 'broker' in request.GET and request.GET['broker'] != '':
                broker_id = request.GET['broker']
                broker = Broker.objects.get(pk=broker_id)
                # cases_by_broker = cases.filter(created_by = broker)

                q_array.append(Q(created_by = broker))

                # cases = cases.filter(created_by = broker)
                # case_by_broker = cases
                context['selected_broker'] = broker_id
                context['is_filter_applied'] = 1   
                context['next_page_url'] += 'broker='+broker_id+'&'

            if 'master-broker' in request.GET and request.GET['master-broker'] !='':  
                master_broker_id = request.GET['master-broker']
                master_broker = MasterBroker.objects.get(pk=master_broker_id)

                context['selected_master_broker'] = master_broker_id
                cases_by_master_broker = cases.filter(created_by_master = master_broker)
                q_array.append(Q(created_by_master = master_broker))
                context['is_filter_applied'] = 1   
                context['next_page_url'] += 'master-broker='+master_broker_id+'&'
            
            if len(q_array):
                cases = cases.filter(reduce(OR, q_array))  

        
    elif request.method == 'POST' and 'context' in request.POST and (request.POST['context'] == 'remove-filters' or request.POST['context'] == 'clear-search'):
        cases = Case.objects.filter(is_marked_for_payment=True).order_by('-pk')

    for case in cases:
        case.final_status =  get_case_final_status(case)
        case.amount_billed_to_law_firm = case.get_law_firm_price()
    
    # if no_of_cases != 'All':
    #     paginator = Paginator(cases, no_of_cases) # Show 25 contacts per page

    #     page = request.GET.get('page')
    #     try:
    #         cases = paginator.page(page)
    #     except PageNotAnInteger:
    #         # If page is not an integer, deliver first page.
    #         cases = paginator.page(1)
    #     except EmptyPage:
    #         # If page is out of range (e.g. 9999), deliver last page of results.
    #         cases = paginator.page(paginator.num_pages)
    # elif no_of_cases == 'All' :
    #     paginator = Paginator(cases, 1000) # Show 25 contacts per page

    #     page = request.GET.get('page')
    #     try:
    #         cases = paginator.page(page)
    #     except PageNotAnInteger:
    #         # If page is not an integer, deliver first page.
    #         cases = paginator.page(1)
    #     except EmptyPage:
    #         # If page is out of range (e.g. 9999), deliver last page of results.
    #         cases = paginator.page(paginator.num_pages)
    cases = Case.objects.filter(has_law_firm_paid=True).order_by('-pk')
    context['no_of_cases'] = no_of_cases    
    print (no_of_cases)
    print len(cases)    
    context['cases'] = cases

    return render(request, 'master_broker/collected_payments.html', context)

def cases_to_be_approved(request):
    print "In here"

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        master_broker = MasterBroker.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    date = timezone.localtime(timezone.now()).date() - timedelta(days=1)
    cases = Case.objects.filter(is_marked_for_payment = True).filter(approved_by_rsn = False).filter(has_law_firm_paid=False).filter(closing_date__lt = date)
    context['cases'] = cases

    if request.POST and 'context' in request.POST and request.POST['context'] == "single-approve":
        print "In here"

        if 'case_id' in request.POST and request.POST['case_id'] != "":
            case_id = request.POST['case_id']
            case = Case.objects.get(pk=case_id)
            case.approved_by_rsn = True
            case.save()
            print case_id
            print "-- Single approve --" 
    elif request.POST and 'context' in request.POST and request.POST['context'] == "single-disapprove":

        if 'case_id' in request.POST and request.POST['case_id'] != "":
            case_id = request.POST['case_id']
            case = Case.objects.get(pk=case_id)
            print case_id
            case.approved_by_rsn = False
            case.is_marked_for_payment = False
            case.save()
            print "-- Single disapprove --" 
    elif request.POST and 'context' in request.POST and request.POST['context'] == "combined-approve":
        print "--Combined approve --"
        if 'case_ids' in request.POST and request.POST['case_ids'] != "":
            try:
                case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
            except:
                print "No value for case_ids or case_ids not found in request.POST"

            for case_id in case_ids:
                print case_id
                case = Case.objects.get(pk=case_id)
                case.approved_by_rsn = True
                case.save()
    elif request.POST and 'context' in request.POST and request.POST['context'] == "combined-disapprove":
        print "--Combined disapprove --"
        if 'case_ids' in request.POST and request.POST['case_ids'] != "":
            try:
                case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
            except:
                print "No value for case_ids or case_ids not found in request.POST"

            for case_id in case_ids:
                print case_id
                case = Case.objects.get(pk=case_id)
                case.approved_by_rsn = False
                case.is_marked_for_payment = False
                case.save()

    cases = Case.objects.filter(is_marked_for_payment = True).filter(approved_by_rsn = False).filter(has_law_firm_paid=False).filter(closing_date__lt = date)
    context['cases'] = cases

    return render(request, 'master_broker/cases_to_be_approved.html', context)

def refund_case(request):

    case_id = request.POST["case_id"]
    refund_amount = request.POST["refund_amount"]
    refund_description = request.POST["refund_description"]
    case = Case.objects.get(pk=case_id)
    reference_id = case.reference_id

    law_firm = case.law_firm
    law_firm_email = law_firm.email_one
    refund_recipients = law_firm.invoice_recipients
    refund_recipients = refund_recipients.split(",")

    customer_profile = CustomerProfile.objects.get(law_firm=law_firm)
    # Resolve the case without a refund operation
    if refund_amount == "0":
        case.is_dispute_raised = False
        case.refund_description = refund_description
        case.save()
        return HttpResponse('')

    elif (case.amount_refunded + float(refund_amount) > case.amount_billed_to_law_firm):
        return Exception("Refund amount is exceeding amount billed to law firm for this case")

    else:
        try:
            transaction_instance = Transaction.objects.get(reference_id=reference_id)
            transaction_id =  transaction_instance.transaction_id
            print "Found transaction id"
            #Get transaction status from authorize
            try:
                print "here"
                transaction_status_response = get_transaction_status(transaction_id)
                if transaction_status_response.transaction is not None:
                    if transaction_status_response.transaction and transaction_status_response.transaction.transactionStatus == "settledSuccessfully":
                        print "Success found refundable amount"
                        print transaction_status_response.transaction.transactionStatus
                        
                        # Create Refund Object with a unique reference id
                        refund_ref_id = create_refund_reference_id()
                        new_refund_transaction = Refund(law_firm=law_firm,reference_id=refund_ref_id,refund_amount=refund_amount,case=case)
                        new_refund_transaction.save()

                        # Perform Refund based on payment type.
                        if 'bankAccount' in dir(transaction_status_response.transaction.payment) and transaction_status_response is not None:
                            customer_bank_account_number, customer_bank_account_routing_number, customer_bank_account_name, customer_bank_account_type = get_customer_profile_ACH(customer_profile.auth_customer_profile_id, customer_profile.secondary_payment_profile_id)
                            response = refund_ACH_transaction(transaction_id, customer_bank_account_type,customer_bank_account_routing_number,customer_bank_account_number,customer_bank_account_name,refund_amount,refund_ref_id)
                            if response is not None:
                                if response.messages.resultCode == "Ok":
                                    if hasattr(response.transactionResponse, 'messages') == True:
                                        new_refund_transaction.transaction_id = response.transactionResponse.transId
                                        new_refund_transaction.save()

                                        case.is_dispute_raised = False
                                        case.amount_refunded = case.amount_refunded + float(refund_amount)
                                        case.refund_description = refund_description
                                        case.save()

                                        # Check if the case is being completely refunded if so mark the case as unpaid and remove the previous transaction reference id
                                        if float(refund_amount) == case.amount_billed_to_law_firm:
                                            case.refund_settlement = "Full Refund"
                                            case.reference_id = ""
                                            case.has_law_firm_paid = False
                                            case.is_marked_for_payment = False
                                            case.approved_by_rsn = False
                                            case.save()
                                        else:
                                            case.refund_settlement = "Partial Refund"
                                            case.save()

                                        # Check if amount refunded has matched the amount billed to law firm and perform the necessary field updates
                                        if case.amount_refunded == case.amount_billed_to_law_firm:
                                            case.refund_settlement = "Full Refund"
                                            case.reference_id = ""
                                            case.has_law_firm_paid = False
                                            case.is_marked_for_payment = False
                                            case.approved_by_rsn = False
                                            case.save()

                                        #Send email confirmation to law firm and David
                                        email_body = 'Hi ' + law_firm.name + ',<br><br>Refund for the case '+ str(case.name) +'( case id:'+ str(case.pk) +' ) for an amount of $' + str(refund_amount) + ' has been initiated by RapidSignNow for the account number '+ str(customer_bank_account_number) + '. <br><br> <b>Reason for refund amount:</b> '+ str(refund_description) +'<br><br>Please allow few days for this amount to reflect in your account.<br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
                                        message = EmailMessage('Refund Initiated', email_body,
                                                'refund@rapidsignnow.com', [law_firm_email],cc=refund_recipients,bcc=[settings.INVOICE_HARDCODED_TO_EMAIL])
                                        message.content_subtype = "html"
                                        message.send()

                                    else:
                                        print ('Failed Transaction.')
                                        if hasattr(response.transactionResponse, 'errors') == True:
                                            print ('Error Code:  %s' % str(response.transactionResponse.errors.error[0].errorCode))
                                            print ('Error message: %s' % response.transactionResponse.errors.error[0].errorText)

                                            new_refund_transaction.delete()
                                            # If a duplicate transaction was placed inform the master broker
                                            if response.transactionResponse.errors.error[0].errorCode == "11":
                                                return HttpResponseServerError("A refund with same amount already submitted for the same transaction. Please try again after sometime")
                                else:
                                    print ('Failed Transaction.')
                                    if hasattr(response, 'transactionResponse') == True and hasattr(response.transactionResponse, 'errors') == True:
                                        print ('Error Code: %s' % str(response.transactionResponse.errors.error[0].errorCode))
                                        print ('Error message: %s' % response.transactionResponse.errors.error[0].errorText)

                                        new_refund_transaction.delete()
                                        # If a duplicate transaction was placed inform the master broker
                                        if response.transactionResponse.errors.error[0].errorCode == "11":
                                            return HttpResponseServerError("A refund with same amount already submitted for the same transaction. Please try again after sometime")
                                    else:
                                        print ('Error Code: %s' % response.messages.message[0]['code'].text)
                                        print ('Error message: %s' % response.messages.message[0]['text'].text)

                                        new_refund_transaction.delete()
                                        # If a duplicate transaction was placed inform the master broker
                                        if response.messages.message[0]['code'].text == "11":
                                            return HttpResponseServerError("A refund with same amount already submitted for the same transaction. Please try again after sometime")
                            else:
                                print ('Null Response.')
                                new_refund_transaction.delete()
                                # Handle null response in front end
                        else:
                            print "credit card refund start"
                            creditCardNumber, creditCardExpiry = get_customer_profile_credit_card(customer_profile.auth_customer_profile_id, customer_profile.primary_payment_profile_id)
                            response = refund_credit_card(transaction_id, creditCardNumber , creditCardExpiry, refund_amount, refund_ref_id)
                            if response is not None:
                                if response.messages.resultCode == "Ok":
                                    if hasattr(response.transactionResponse, 'messages') == True:
                                        new_refund_transaction.transaction_id = response.transactionResponse.transId
                                        new_refund_transaction.save()

                                        case.is_dispute_raised = False
                                        case.amount_refunded = case.amount_refunded + float(refund_amount)
                                        case.refund_description = refund_description
                                        case.save()

                                        # Check if the case is being completely refunded if so mark the case as unpaid and remove the previous transaction reference id
                                        if float(refund_amount) == case.amount_billed_to_law_firm:
                                            case.refund_settlement = "Full Refund"
                                            case.reference_id = ""
                                            case.has_law_firm_paid = False
                                            case.is_marked_for_payment = False
                                            case.approved_by_rsn = False
                                            case.save()
                                        else:
                                            case.refund_settlement = "Partial Refund"
                                            case.save()

                                        # Check if amount refunded has matched the amount billed to law firm and perform the necessary field updates
                                        if case.amount_refunded == case.amount_billed_to_law_firm:
                                            case.refund_settlement = "Full Refund"
                                            case.reference_id = ""
                                            case.has_law_firm_paid = False
                                            case.is_marked_for_payment = False
                                            case.approved_by_rsn = False
                                            case.save()

                                        #Send email confirmation to law firm and David
                                        email_body = 'Hi ' + law_firm.name + ',<br><br>Refund for the case '+ str(case.name) +'( case id:'+ str(case.pk) +' ) for an amount of $' + str(refund_amount) + ' has been initiated by RapidSignNow for the credit card '+ str(creditCardNumber) + '. <br><br> <b>Reason for refund amount:</b> '+ str(refund_description) +'<br><br>Please allow few days for this amount to reflect in your account.<br><br> Thanks,<br> RSN Team <br><br> <div style="font-family: monospace;"><h7>These emails are automatically generated. If you need immediate assistance or have questions please give Rapid Sign Now a call at <a href="tel:+13108922043">310-892-2043</a> or email us at <a href="mailto:david@rapidlegalsign.com">david@rapidlegalsign.com</a></h7></div>'
                                        message = EmailMessage('Refund Initiated', email_body,
                                                'refund@rapidsignnow.com', [law_firm_email],cc=refund_recipients,bcc=[settings.INVOICE_HARDCODED_TO_EMAIL])
                                        message.content_subtype = "html"
                                        message.send()
                                    else:
                                        print ('Failed Transaction.')
                                        if hasattr(response.transactionResponse, 'errors') == True:
                                            print ('Error Code:  %s' % str(response.transactionResponse.errors.error[0].errorCode))
                                            print ('Error message: %s' % response.transactionResponse.errors.error[0].errorText)

                                            new_refund_transaction.delete()
                                            # If a duplicate transaction was placed inform the master broker
                                            if response.transactionResponse.errors.error[0].errorCode == "11":
                                                return HttpResponseServerError("A refund with same amount already submitted for the same transaction. Please try again after sometime")
                                else:
                                    print ('Failed Transaction.')
                                    if hasattr(response, 'transactionResponse') == True and hasattr(response.transactionResponse, 'errors') == True:
                                        print ('Error Code: %s' % str(response.transactionResponse.errors.error[0].errorCode))
                                        print ('Error message: %s' % response.transactionResponse.errors.error[0].errorText)
                                        new_refund_transaction.delete()
                                        # If a duplicate transaction was placed inform the master broker
                                        if response.transactionResponse.errors.error[0].errorCode == "11":
                                            return HttpResponseServerError("A refund with same amount already submitted for the same transaction. Please try again after sometime")
                                    else:
                                        print ('Error Code: %s' % response.messages.message[0]['code'].text)
                                        print ('Error message: %s' % response.messages.message[0]['text'].text)

                                        new_refund_transaction.delete()
                                        # If a duplicate transaction was placed inform the master broker
                                        if response.messages.message[0]['code'].text == "11":
                                            return HttpResponseServerError("A refund with same amount already submitted for the same transaction. Please try again after sometime")
                            else:
                                print ('Null Response.')
                                new_refund_transaction.delete()
                                # Handle null response in front end
                    else:
                        print "Amount not yet settled"
                        # raise Exception("Transaction has not yet been settled. Please try again after sometime.")
                        return HttpResponseServerError("Transaction has not yet been settled. Please try again after sometime.")
                else:
                    print "None Returned"
                    return HttpResponseServerError("Could not process. Please try again after some time")
            except Exception as ex:
                print ex
                print "No response from authorize"
                new_refund_transaction.delete()
                return HttpResponseServerError("Error occured while fetching transaction status. Please try again after sometime.")
        except:
            print "No transaction with reference id"

    return HttpResponse('')
# Refund an exisiting settled credit card transaction
def refund_credit_card(transaction_id, card_number, card_expiration, refund_amount, ref_id):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = str(card_number)
    creditCard.expirationDate = str(card_expiration)

    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard

    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "refundTransaction"
    transactionrequest.amount = Decimal (refund_amount)
    #set refTransId to transId of a settled transaction
    transactionrequest.refTransId = transaction_id
    transactionrequest.payment = payment


    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = str(ref_id)

    createtransactionrequest.transactionRequest = transactionrequest
    createtransactioncontroller = createTransactionController(createtransactionrequest)
    createtransactioncontroller.setenvironment(constants.PRODUCTION)
    createtransactioncontroller.execute()

    response = createtransactioncontroller.getresponse()

    if response is not None:
        if response.messages.resultCode == "Ok":
            if hasattr(response.transactionResponse, 'messages') == True:
                print ('Successfully created transaction with Transaction ID: %s' % response.transactionResponse.transId)
                print ('Transaction Response Code: %s' % response.transactionResponse.responseCode)
                print ('Message Code: %s' % response.transactionResponse.messages.message[0].code)
                print ('Description: %s' % response.transactionResponse.messages.message[0].description)
            else:
                print ('Failed Transaction.')
                if hasattr(response.transactionResponse, 'errors') == True:
                    print ('Error Code:  %s' % str(response.transactionResponse.errors.error[0].errorCode))
                    print ('Error message: %s' % response.transactionResponse.errors.error[0].errorText)
        else:
            print ('Failed Transaction.')
            if hasattr(response, 'transactionResponse') == True and hasattr(response.transactionResponse, 'errors') == True:
                print ('Error Code: %s' % str(response.transactionResponse.errors.error[0].errorCode))
                print ('Error message: %s' % response.transactionResponse.errors.error[0].errorText)
            else:
                print ('Error Code: %s' % response.messages.message[0]['code'].text)
                print ('Error message: %s' % response.messages.message[0]['text'].text)
    else:
        print ('Null Response.')

    return response

# Refund an existing settled ACH Transaction
def refund_ACH_transaction(transaction_id, customer_bank_account_type, customer_bank_account_routing_number, customer_bank_account_number, customer_bank_account_name, amount, ref_id):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    # Create the payment data for a bank account
    bankAccount = apicontractsv1.bankAccountType()
    accountType = apicontractsv1.bankAccountTypeEnum
    if (customer_bank_account_type == "checking"):
        bankAccount.accountType = accountType.checking
    else:
        bankAccount.accountType = accountType.savings

    bankAccount.routingNumber = customer_bank_account_routing_number
    bankAccount.accountNumber = customer_bank_account_number
    bankAccount.nameOnAccount = customer_bank_account_name

    payment = apicontractsv1.paymentType()
    payment.bankAccount = bankAccount

    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "refundTransaction"
    transactionrequest.amount = Decimal (amount)
    #set refTransId to transId of a settled transaction
    transactionrequest.refTransId = str(transaction_id)
    transactionrequest.payment = payment


    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    # Refund invoice number. Can be used to get details in case refund never returned a response.
    createtransactionrequest.refId = str(ref_id)

    createtransactionrequest.transactionRequest = transactionrequest
    createtransactioncontroller = createTransactionController(createtransactionrequest)
    createtransactioncontroller.setenvironment(constants.PRODUCTION)
    createtransactioncontroller.execute()

    response = createtransactioncontroller.getresponse()

    if response is not None:
        if response.messages.resultCode == "Ok":
            if hasattr(response.transactionResponse, 'messages') == True:
                print ('Successfully created transaction with Transaction ID: %s' % response.transactionResponse.transId)
                print ('Transaction Response Code: %s' % response.transactionResponse.responseCode)
                print ('Message Code: %s' % response.transactionResponse.messages.message[0].code)
                print ('Description: %s' % response.transactionResponse.messages.message[0].description)
            else:
                print ('Failed Transaction.')
                if hasattr(response.transactionResponse, 'errors') == True:
                    print ('Error Code:  %s' % str(response.transactionResponse.errors.error[0].errorCode))
                    print ('Error message: %s' % response.transactionResponse.errors.error[0].errorText)
        else:
            print ('Failed Transaction.')
            if hasattr(response, 'transactionResponse') == True and hasattr(response.transactionResponse, 'errors') == True:
                print ('Error Code: %s' % str(response.transactionResponse.errors.error[0].errorCode))
                print ('Error message: %s' % response.transactionResponse.errors.error[0].errorText)
            else:
                print ('Error Code: %s' % response.messages.message[0]['code'].text)
                print ('Error message: %s' % response.messages.message[0]['text'].text)
    else:
        print ('Null Response.')

    return response

def get_transaction_status(transaction_id):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = settings.AUTHORIZE_LOGIN_ID
    merchantAuth.transactionKey = settings.AUTHORIZE_TRANSACTION_KEY

    transactionDetailsRequest = apicontractsv1.getTransactionDetailsRequest()
    transactionDetailsRequest.merchantAuthentication = merchantAuth
    transactionDetailsRequest.transId = str(transaction_id)

    transactionDetailsController = getTransactionDetailsController(transactionDetailsRequest)
    transactionDetailsController.setenvironment(constants.PRODUCTION)
    transactionDetailsController.execute()

    transactionDetailsResponse = transactionDetailsController.getresponse()

    if transactionDetailsResponse is not None:
        if transactionDetailsResponse.messages.resultCode == apicontractsv1.messageTypeEnum.Ok:
            print('Successfully got transaction details!')

            print('Transaction Id : %s' % transactionDetailsResponse.transaction.transId)
            print('Transaction Type : %s' % transactionDetailsResponse.transaction.transactionType)
            print('Transaction Status : %s' % transactionDetailsResponse.transaction.transactionStatus)
            print('Auth Amount : %s' % transactionDetailsResponse.transaction.authAmount)
            print('Settle Amount : %s' % transactionDetailsResponse.transaction.settleAmount)
            if hasattr(transactionDetailsResponse.transaction, 'tax') == True:
                print('Tax : %s' % transactionDetailsResponse.transaction.tax.amount)
            if hasattr(transactionDetailsResponse.transaction, 'profile'):
                print('Customer Profile Id : %s' % transactionDetailsResponse.transaction.profile.customerProfileId)

            if transactionDetailsResponse.messages is not None:
                print('Message Code : %s' % transactionDetailsResponse.messages.message[0]['code'].text)
                print('Message Text : %s' % transactionDetailsResponse.messages.message[0]['text'].text)
        else:
            if transactionDetailsResponse.messages is not None:
                print('Failed to get transaction details.\nCode:%s \nText:%s' % (transactionDetailsResponse.messages.message[0]['code'].text,transactionDetailsResponse.messages.message[0]['text'].text))

    return transactionDetailsResponse
