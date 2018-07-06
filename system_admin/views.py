from django.shortcuts import render

from django.shortcuts import get_object_or_404, render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404,JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.db.models import Q

from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.decorators import login_required, permission_required

from xhtml2pdf import pisa
from django.template.loader import get_template

from rapidsignnow.settings import CONSTANCE_CONFIG_FIELDSETS
from rapidsignnow.settings import INVOICE_HARDCODED_TO_EMAIL
from constance import config
from io import BytesIO
import datetime
import StringIO
import zipfile
import itertools
import xlsxwriter
import boto
import os
import requests
import mimetypes 
import magic  
import urllib 
import numpy
from boto.s3.key import Key
from datetime import timedelta
from django.utils import timezone
from dateutil import relativedelta


from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]
styles = getSampleStyleSheet()

from system_admin.models import SystemAdmin
from law_firm.models import LawFirm, LawFirmRates
from broker.models import Broker
from master_broker.models import MasterBroker
from investigator.models import Investigator, InvestigatorRates
from address.models import Address
from case.models import Case
from document.models import Document
from attached_document.models import AttachedDocument
from invoice.models import Invoice
from invoice_line.models import InvoiceLine
from status_update.models import StatusUpdate


all_languages = ["English","Mandarin","Spanish","Hindi","Arabic","Portuguese","Bengali","Russian","Japanese","Punjabi",
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



@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def law_firms(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['law_firms'] = []
    law_firms = LawFirm.objects.all().order_by('-pk')

    phone_numbers = []
    for law_firm in law_firms:
        phone_number = law_firm.phone_number_one.replace('-', '').replace(' ', '')
        phone_numbers.append(phone_number)
    context['data'] = zip(law_firms, phone_numbers)
    
    # paginator = Paginator(law_firms, 15) # Show 25 contacts per page

    # page = request.GET.get('page')
    # try:
    #     law_firms = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     law_firms = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     law_firms = paginator.page(paginator.num_pages)
    
    context['law_firms']= law_firms
    

    return render(request, 'system_admin/law_firms.html', context)

@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def profile(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
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


    

  

    return render(request, 'system_admin/profile.html', context)


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def new_law_firm(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if request.POST:

        username = request.POST['email-1']
        password = request.POST['password']
        first_name = request.POST['name']
        
        try:
            user = User.objects.create_user(username=username, password=password, email=username, first_name = first_name )
            created_user = authenticate(username=username, password=password)
            permission = Permission.objects.get(name='Can View Law Firm')
            user.user_permissions.add(permission)
        except:
            context = dict()
            context['error'] = 'A user with this username already exists'
            return render(request, 'system_admin/new_law_firm.html', context)

    if request.POST:
        referring_law_firm = None

        if 'referring_law_firm' in request.POST:
            try:
                referring_law_firm_id = request.POST['referring-law-firm']
                referring_law_firm = LawFirm.objects.get(referring_law_firm_id)
            except:
                return HttpResponseRedirect('/administrator/new-law-firm/')

        street_one = request.POST['street-1']
        
        street_two = None
        if 'street-2' in request.POST:
            street_two = request.POST['street-2']
        
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip-code']
        country = request.POST['country']

        new_address = Address(street_one=street_one, street_two=street_two, city=city, state=state, zip_code=zip_code,
                              country=country)
        new_address.save()
        
        coordinates = new_address.get_coordinates()
        
        if coordinates is not None:
            new_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                   str(coordinates['longitude']) + 'z?hl=en'
            new_address.save()

        name = request.POST['name']
        phone_number_one = request.POST['phone-1']
        phone_number_two = None

        if 'phone-2' in request.POST:
            phone_number_two = request.POST['phone-2']

        email_one = request.POST['email-1']

        email_two = None
        if 'email-2' in request.POST:
            email_two = request.POST['email-2']
        
        payment_plan = None
        if 'payment-plan' in request.POST:
            payment_plan = request.POST['payment-plan']

        new_law_firm_instance = LawFirm(user=created_user,name=name, phone_number_one=phone_number_one, phone_number_two=phone_number_two,
                                        email_one=email_one, email_two=email_two, address=new_address, payment_plan=payment_plan)
        new_law_firm_instance.save()

        law_firm_rates_keys = [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm In Area options']] + \
                         [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm Out of Area options']] + \
                        [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm miscellaneous options']]

        law_firm_rates = dict()

        for rate_key in law_firm_rates_keys:
            law_firm_rates[rate_key] = float(request.POST[rate_key.lower().replace('_', '-')])

        new_law_firm_rates = LawFirmRates()
        new_law_firm_rates.save()

        for rate_key in law_firm_rates_keys:
            setattr(new_law_firm_rates, rate_key.lower()[0:len(rate_key) - len('_LAW_FIRM')], law_firm_rates[rate_key])

        new_law_firm_rates.save()

        new_law_firm_instance.rates = new_law_firm_rates
        new_law_firm_instance.save()

        
        if request.method == 'POST' and 'document' in request.FILES and request.FILES['document']:
            files = request.FILES.getlist('document')
            document_names = request.POST.getlist('document-name')
            for file,document_name in zip(files,document_names):
                fs = FileSystemStorage()
                filename, file_extension = os.path.splitext(file.name)
                file_name = str(document_name) + str(file_extension)
                file.name = str(new_law_firm_instance.name) + "-" + str(document_name) + str(file_extension)
                uploaded_file_url = fs.url(file.name)
                new_document = Document(file_name=file_name, file = file, file_url=uploaded_file_url, law_firm = new_law_firm_instance )
                new_document.save()
        return HttpResponseRedirect('/administrator/law-firms/?created=True')
    context = dict()
    context['law_firms'] = LawFirm.objects.all()
    context['countries'] = countries
    return render(request, 'system_admin/new_law_firm.html', context)

@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def law_firm(request, law_firm_id):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    try:
        law_firm_instance = LawFirm.objects.get(pk=law_firm_id)
    except:
        raise Http404

    documents = Document.objects.filter(law_firm = law_firm_instance)    
    context = dict()
    context['law_firm'] = law_firm_instance
    context['law_firm_rates'] = law_firm_instance.rates
    context['countries'] = countries

    phone_number_one = law_firm_instance.phone_number_one.replace('-', '').replace(' ', '')
    phone_number_two = law_firm_instance.phone_number_two.replace('-', '').replace(' ', '')
    context['phone_number_one'] = phone_number_one
    context['phone_number_two'] = phone_number_two
    if request.POST:
        if request.is_ajax() and request.POST:
            if request.POST['context'] == 'suspend':
                law_firm_instance.is_active = False
                law_firm_instance.user.is_active = False
                law_firm_instance.user.save()
                law_firm_instance.save()              
                return HttpResponse('')
            elif request.POST['context'] == 'resume':
                law_firm_instance.is_active = True
                law_firm_instance.user.is_active = True
                law_firm_instance.user.save()
                law_firm_instance.save()               
                return HttpResponse('')
            elif request.POST['context'] == 'delete':
                # rates_instance = law_firm_instance.rates
                # law_firm_instance.rates = None
                # rates_instance.delete()
                # law_firm_instance.address.delete()
                law_firm_instance.is_active = False
                law_firm_instance.user.is_active = False
                law_firm_instance.user.save()
                law_firm_instance.save()

                return HttpResponse('')
            else:
                return HttpResponse('')
        elif request.POST.get('context') == 'view-document':
            context = dict()
            context['pagesize'] = 'A4'
            template = get_template('system_admin/invoice.html')
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


        elif request.POST.get('context') == 'edit-document':
            if request.method == 'POST' or request.FILES.get('document'):
                document_id = request.POST.get('document-id')
                document_instance = Document.objects.get(pk=document_id)
                changes = 0
                try:
                    if request.FILES.get('new-document'):
                        file = request.FILES.get('new-document')
                        document_instance.file = file
                        changes = 1
                        if request.POST.get('new-document-name'):
                            document_name = request.POST.get('new-document-name')
                            fs = FileSystemStorage()
                            filename, file_extension = os.path.splitext(document_instance.file.name)
                            file_name = str(document_name) + str(file_extension)
                            document_instance.file.name = str(law_firm_instance.name) + "-" + str(document_name) + str(file_extension)
                            document_instance.file_name = file_name
                            uploaded_file_url = fs.url(document_instance.file.name)
                            document_instance.file_url = uploaded_file_url
                            changes= 1
                    
                    elif request.POST.get('new-document-name'):
                        document_name = request.POST.get('new-document-name')
                        filename, file_extension = os.path.splitext(document_instance.file.name)
                        file_name = str(document_name) + str(file_extension)
                        document_instance.file_name = file_name
                        changes= 1
                    
                    if changes != 0:
                        document_instance.version = float(document_instance.version) + 0.1
                        document_instance.save()
                except:
                    print "Could not Update Document "
        elif request.POST.get('context') == 'download-document':
                document_id = request.POST['document-id']
                response = download_doc(request,document_id)
                return response            
        else:

            street_one = request.POST['street-1']
            
            street_two = None
            if 'street-2' in request.POST:
                street_two = request.POST['street-2']
            
            city = request.POST['city']
            state = request.POST['state']
            zip_code = request.POST['zip-code']
            country = request.POST['country']

            law_firm_instance.address.street_one = street_one
            law_firm_instance.address.street_two = street_two
            law_firm_instance.address.city = city
            law_firm_instance.address.state = state
            law_firm_instance.address.country = country
            law_firm_instance.address.zip_code = zip_code
            law_firm_instance.address.save()
            
            coordinates = law_firm_instance.address.get_coordinates()
            
            if coordinates is not None:
                law_firm_instance.address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                    str(coordinates['longitude']) + 'z?hl=en'
                law_firm_instance.address.save()

            name = request.POST['name']
            phone_number_one = request.POST['phone-1']

            phone_number_two = None
            if 'phone-2' in request.POST:
                phone_number_two = request.POST['phone-2']

            email_one = request.POST['email-1']

            email_two = None
            if 'email-2' in request.POST:
                email_two = request.POST['email-2']
            
            payment_plan = None
            if 'payment-plan' in request.POST:
                payment_plan = request.POST['payment-plan']
            number_of_free_miles = None
            try:
                if 'number-of-free-miles' in request.POST:
                    number_of_free_miles = int(request.POST['number-of-free-miles'])
            except:
                number_of_free_miles = None

            law_firm_instance.name = name
            law_firm_instance.phone_number_one = phone_number_one
            law_firm_instance.phone_number_two = phone_number_two
            law_firm_instance.email_one = email_one
            law_firm_instance.email_two = email_two
            law_firm_instance.payment_plan = payment_plan
            law_firm_instance.number_of_free_miles = number_of_free_miles

            law_firm_instance.save()

            law_firm_rates_keys = [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm In Area options']] + \
                            [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm Out of Area options']] + \
                            [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm miscellaneous options']]

            law_firm_rates = dict()

            for rate_key in law_firm_rates_keys:
                law_firm_rates[rate_key] = float(request.POST[rate_key.lower().replace('_', '-')])

            law_firm_rates_instance = None
            if law_firm_instance.rates is not None:
                law_firm_rates_instance = law_firm_instance.rates
            else:
                law_firm_rates_instance = LawFirmRates()
                law_firm_rates_instance.save()
                context['law_firm_rates'] = law_firm_rates_instance

            for rate_key in law_firm_rates_keys:
                setattr(law_firm_rates_instance, rate_key.lower()[0:len(rate_key) - len('_LAW_FIRM')], law_firm_rates[rate_key])

                law_firm_rates_instance.save()

            law_firm_instance.rates = law_firm_rates_instance
            law_firm_instance.save()

            if request.method == 'POST' and request.FILES.getlist('document'):
                files = request.FILES.getlist('document')
                document_names = request.POST.getlist('document-name')
                for file,document_name in zip(files,document_names):
                    fs = FileSystemStorage()
                    # file_name = fs.save(file.name, file)
                    filename, file_extension = os.path.splitext(file.name)
                    file_name = str(document_name) + str(file_extension)
                    file.name = str(law_firm_instance.name) + "-" + str(document_name) + str(file_extension)
                    uploaded_file_url = fs.url(file.name)
                    new_document = Document(file_name=file_name, file = file, file_url=uploaded_file_url, law_firm = law_firm_instance )
                    new_document.save()
        


    
    documents = Document.objects.filter(law_firm = law_firm_instance)
    attached_documents = []
    for document in documents:
        attached_cases = AttachedDocument.objects.filter(document = document)
        for attached_case in attached_cases:
            attached_documents.append(attached_case)
    context['attached_documents'] = attached_documents
    context['documents'] = documents
    phone_number_one = law_firm_instance.phone_number_one.replace('-', '').replace(' ', '')
    phone_number_two = law_firm_instance.phone_number_two.replace('-', '').replace(' ', '')
    context['phone_number_one'] = phone_number_one
    context['phone_number_two'] = phone_number_two
    return render(request, 'system_admin/law_firm_details.html', context)


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def brokers(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['brokers'] = []
    brokers = Broker.objects.all().order_by('-pk')
    phone_numbers = []
    for broker in brokers:
        phone_number = broker.phone_number_one.replace('-', '').replace(' ', '')
        phone_numbers.append(phone_number)
    context['data'] = zip(brokers, phone_numbers)
    
    # paginator = Paginator(brokers, 15) # Show 25 contacts per page

    # page = request.GET.get('page')
    # try:
    #     brokers = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     brokers = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     brokers = paginator.page(paginator.num_pages)
    
    context['brokers']= brokers
    return render(request, 'system_admin/brokers.html', context)


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def new_broker(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if request.POST:

        username = request.POST['email-1']
        password = request.POST['password']
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']

        try:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            created_user = authenticate(username=username, password=password)
            permission = Permission.objects.get(name='Can View Broker')
            user.user_permissions.add(permission)
        except:
            context = dict()
            context['error'] = 'A user with this username already exists'
            return render(request, 'system_admin/new_broker.html', context)

        street_one = request.POST['street-1']
        
        street_two = None
        if 'street-2' in request.POST:
            street_two = request.POST['street-2']
        
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip-code']
        country = request.POST['country']

        new_address = Address(street_one=street_one, street_two=street_two, city=city, state=state, zip_code=zip_code,
                              country=country)
        new_address.save()
        
        coordinates = new_address.get_coordinates()
        
        if coordinates is not None:
            new_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                   str(coordinates['longitude']) + 'z?hl=en'
            new_address.save()

        phone_number_one = request.POST['phone-1']

        phone_number_two = None
        if 'phone-2' in request.POST:
            phone_number_two = request.POST['phone-2']

        email_one = request.POST['email-1']

        email_two = None
        if 'email-2' in request.POST:
            email_two = request.POST['email-2']

        more_info = None
        if 'more-info' in request.POST:
            more_info = request.POST['more-info']

        photograph = None

        if request.FILES and 'photograph' in request.FILES:
            photograph = request.FILES['photograph']

        new_broker_instance = Broker(user=created_user, address=new_address, phone_number_one=phone_number_one,
                            phone_number_two=phone_number_two, email_one=email_one, email_two=email_two,
                            more_info=more_info, photograph=photograph)
        new_broker_instance.save()

        return HttpResponseRedirect('/administrator/brokers/?created=True')

    context = dict()
    context['countries'] = countries

    return render(request, 'system_admin/new_broker.html', context)


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def broker(request, broker_id):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    try:
        broker_instance = Broker.objects.get(pk=broker_id)
    except:
        raise Http404

    context = dict()
    context['broker'] = broker_instance
    context['countries'] = countries
    phone_number_one = broker_instance.phone_number_one.replace('-', '').replace(' ', '')
    phone_number_two = broker_instance.phone_number_two.replace('-', '').replace(' ', '')
    context['phone_number_one'] = phone_number_one
    context['phone_number_two'] = phone_number_two

    if request.is_ajax() and request.POST and 'context' in request.POST:
        if request.POST['context'] == 'suspend':
            #broker can still login
            broker_instance.is_active = False
            broker_instance.user.is_active = False
            broker_instance.user.save()
            broker_instance.save()
            return HttpResponse('')
        elif request.POST['context'] == 'resume':
            broker_instance.is_active = True
            broker_instance.user.is_active = True
            broker_instance.user.save()
            broker_instance.save()
            return HttpResponse('')
        elif request.POST['context'] == 'delete':

            # restrict login (soft delete)
            user_instance = broker_instance.user
            user_instance.is_active = False
            user_instance.save()
            return HttpResponse('')
            
            
        else:
            return HttpResponse('')

    if request.POST:
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']

        broker_instance.user.first_name = first_name
        broker_instance.user.last_name = last_name
        broker_instance.user.save()

        street_one = request.POST['street-1']
        
        street_two = None
        if 'street-2' in request.POST:
            street_two = request.POST['street-2']
        
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip-code']
        country = request.POST['country']

        broker_instance.address.street_one = street_one
        broker_instance.address.street_two = street_two
        broker_instance.address.city = city
        broker_instance.address.state = state
        broker_instance.address.country = country
        broker_instance.address.zip_code = zip_code
        broker_instance.address.save()
        
        coordinates = broker_instance.address.get_coordinates()
        
        if coordinates is not None:
            broker_instance.address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                   str(coordinates['longitude'])
            broker_instance.address.save()

        phone_number_one = request.POST['phone-1']

        phone_number_two = None
        if 'phone-2' in request.POST:
            phone_number_two = request.POST['phone-2']

        email_one = request.POST['email-1']

        email_two = None
        if 'email-2' in request.POST:
            email_two = request.POST['email-2']

        more_info = None
        if 'more-info' in request.POST:
            more_info = request.POST['more-info']
        photograph = None

        if request.FILES and 'photograph' in request.FILES:
            photograph = request.FILES['photograph']
            broker_instance.photograph = photograph

        broker_instance.phone_number_one = phone_number_one
        broker_instance.phone_number_two = phone_number_two

        broker_instance.email_one = email_one
        broker_instance.email_two = email_two

        broker_instance.more_info = more_info

        broker_instance.save()

    phone_number_one = broker_instance.phone_number_one.replace('-', '').replace(' ', '')
    phone_number_two = broker_instance.phone_number_two.replace('-', '').replace(' ', '')
    context['phone_number_one'] = phone_number_one
    context['phone_number_two'] = phone_number_two
    return render(request, 'system_admin/broker_details.html', context)


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def master_brokers(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')


    context = dict()
    context['master_brokers'] = []
    master_brokers = MasterBroker.objects.all().order_by('-pk')
    
    # paginator = Paginator(master_brokers, 15) # Show 25 contacts per page

    # page = request.GET.get('page')
    # try:
    #     master_brokers = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     master_brokers = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     master_brokers = paginator.page(paginator.num_pages)
    
    context['master_brokers'] = master_brokers
    return render(request, 'system_admin/master_brokers.html', context)

@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def new_master_broker(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)

    except:
        return HttpResponseRedirect('/')

    if request.POST:

        username = request.POST['email-1']
        password = request.POST['password']
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']

        try:
            User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            created_user = authenticate(username=username, password=password)
        except:
            context = dict()
            context['error'] = 'A user with this username already exists'
            return render(request, 'system_admin/new_master_broker.html', context)

        street_one = request.POST['street-1']
        
        street_two = None
        if 'street-2' in request.POST:
            street_two = request.POST['street-2']
        
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip-code']
        country = request.POST['country']

        new_address = Address(street_one=street_one, street_two=street_two, city=city, state=state, zip_code=zip_code,
                              country=country)
        new_address.save()
        
        coordinates = new_address.get_coordinates()
        
        if coordinates is not None:
            new_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                   str(coordinates['longitude']) + 'z?hl=en'
            new_address.save()

        phone_number_one = request.POST['phone-1']

        phone_number_two = None
        if 'phone-2' in request.POST:
            phone_number_two = request.POST['phone-2']

        email_one = request.POST['email-1']

        email_two = None
        if 'email-2' in request.POST:
            email_two = request.POST['email-2']

        more_info = None
        if 'more-info' in request.POST:
            more_info = request.POST['more-info']

        photograph = None

        if request.FILES and 'photograph' in request.FILES:
            photograph = request.FILES['photograph']

        new_master_broker_instance = MasterBroker(user=created_user, address=new_address, phone_number_one=phone_number_one,
                            phone_number_two=phone_number_two, email_one=email_one, email_two=email_two,
                            more_info=more_info, photograph=photograph)
        new_master_broker_instance.save()

        return HttpResponseRedirect('/administrator/master-brokers/?created=True')

    context = dict()
    context['countries'] = countries

    return render(request, 'system_admin/new_master_broker.html', context)

@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def master_broker(request,master_broker_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    try:
        master_broker_instance = MasterBroker.objects.get(pk=master_broker_id)
    except:
        raise Http404

    context = dict()
    context['master_broker'] = master_broker_instance
    context['countries'] = countries

    if request.is_ajax() and request.POST and 'context' in request.POST:
        if request.POST['context'] == 'suspend':
            #broker can still login
            master_broker_instance.is_active = False
            master_broker_instance.user.is_active = False
            master_broker_instance.user.save()
            master_broker_instance.save()
            return HttpResponse('')
        elif request.POST['context'] == 'resume':
            master_broker_instance.is_active = True
            master_broker_instance.user.is_active = True
            master_broker_instance.user.save()
            master_broker_instance.save()
            return HttpResponse('')
        elif request.POST['context'] == 'delete':

            # restrict login (soft delete)
            user_instance = master_broker_instance.user
            user_instance.is_active = False
            user_instance.save()
            return HttpResponse('')
            
            
        else:
            return HttpResponse('')

    if request.POST:
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']

        master_broker_instance.user.first_name = first_name
        master_broker_instance.user.last_name = last_name
        master_broker_instance.user.save()

        street_one = request.POST['street-1']
        
        street_two = None
        if 'street-2' in request.POST:
            street_two = request.POST['street-2']
        
        city = request.POST['city']
        state = request.POST['state']
        zip_code = request.POST['zip-code']
        country = request.POST['country']

        master_broker_instance.address.street_one = street_one
        master_broker_instance.address.street_two = street_two
        master_broker_instance.address.city = city
        master_broker_instance.address.state = state
        master_broker_instance.address.country = country
        master_broker_instance.address.zip_code = zip_code
        master_broker_instance.address.save()
        
        coordinates = master_broker_instance.address.get_coordinates()
        
        if coordinates is not None:
            master_broker_instance.address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                   str(coordinates['longitude'])
            master_broker_instance.address.save()

        phone_number_one = request.POST['phone-1']

        phone_number_two = None
        if 'phone-2' in request.POST:
            phone_number_two = request.POST['phone-2']

        email_one = request.POST['email-1']

        email_two = None
        if 'email-2' in request.POST:
            email_two = request.POST['email-2']

        more_info = None
        if 'more-info' in request.POST:
            more_info = request.POST['more-info']
        photograph = None

        if request.FILES and 'photograph' in request.FILES:
            photograph = request.FILES['photograph']
            master_broker_instance.photograph = photograph

        master_broker_instance.phone_number_one = phone_number_one
        master_broker_instance.phone_number_two = phone_number_two

        master_broker_instance.email_one = email_one
        master_broker_instance.email_two = email_two

        master_broker_instance.more_info = more_info

        master_broker_instance.save()

    return render(request, 'system_admin/master_broker_details.html', context)

@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def investigators(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['investigators'] =[] 
    investigators = Investigator.objects.all().order_by('-pk')
    
    phone_numbers = []
    for investigator in investigators:
        phone_number = investigator.phone_number_one.replace('-', '').replace(' ', '')
        phone_numbers.append(phone_number)
    context['data'] = zip(investigators, phone_numbers)
    # paginator = Paginator(investigators, 15) # Show 25 contacts per page

    # page = request.GET.get('page')
    # try:
    #     investigators = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     investigators = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     investigators = paginator.page(paginator.num_pages)
    
    context['investigators']= investigators

    return render(request, 'system_admin/investigators.html', context)


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def new_investigator(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()
    context['languages'] = all_languages
    context['countries'] = countries

    if request.POST:

        username = request.POST['email-1']
        password = request.POST['password']
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']

        try:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            created_user = authenticate(username=username, password=password)
            permission = Permission.objects.get(name='Can View Investigator')
            user.user_permissions.add(permission)
        except:
            context['error'] = 'A user with this username already exists'
            return render(request, 'system_admin/new_investigator.html', context)

        street_one = request.POST['street-1']
        
        street_two = None
        if 'street-2' in request.POST:
            street_two = request.POST['street-2']
        
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        zip_code = request.POST['zip-code']

        new_address = Address(street_one=street_one, street_two=street_two, city=city, state=state, zip_code=zip_code,
                              country=country)
        new_address.save()
        
        coordinates = new_address.get_coordinates()
        
        if coordinates is not None:
            new_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                   str(coordinates['longitude'])
            new_address.save()

        new_secondary_address = None

        try:
            street_one = request.POST['secondary-street-1']
        
            street_two = None
            if 'street-2' in request.POST:
                street_two = request.POST['secondary-street-2']

            city = request.POST['secondary-city']
            state = request.POST['secondary-state']
            country = request.POST['secondary-country']
            zip_code = request.POST['secondary-zip-code']

            new_secondary_address = Address(street_one=street_one, street_two=street_two, city=city, state=state, zip_code=zip_code,
                                  country=country)
            new_secondary_address.save()
        
            coordinates = new_secondary_address.get_coordinates()

            if coordinates is not None:
                new_secondary_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                       str(coordinates['longitude'])
                new_secondary_address.save()
        except:
            new_secondary_address = None

        nickname = request.POST['nickname']
        languages = repr([str(ele) for ele in request.POST.getlist('languages')])

        phone_number_one = request.POST['phone-1']

        phone_number_two = None
        if 'phone-2' in request.POST:
            phone_number_two = request.POST['phone-2']

        email_one = request.POST['email-1']

        email_two = None
        if 'email-2' in request.POST:
            email_two = request.POST['email-2']

        more_info = None
        if 'more-info' in request.POST:
            more_info = request.POST['more-info']

        photograph = None

        if request.FILES and 'photograph' in request.FILES:
            photograph = request.FILES['photograph']

        new_investigator_instance = Investigator(user=created_user, address=new_address, nickname=nickname,
                                languages=languages, phone_number_one=phone_number_one, phone_number_two=phone_number_two,
                                email_one=email_one, email_two=email_two, more_info=more_info, photograph=photograph,
                                secondary_address=new_secondary_address)
        new_investigator_instance.save()

        investigator_rates_keys = [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator In Area options']] + \
                         [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator Out of Area options']] + \
                        [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator miscellaneous options']]

        investigator_rates = dict()

        for rate_key in investigator_rates_keys:
            investigator_rates[rate_key] = float(request.POST[rate_key.lower().replace('_', '-')])

        new_investigator_rates = InvestigatorRates()
        new_investigator_rates.save()

        for rate_key in investigator_rates_keys:
            setattr(new_investigator_rates, rate_key.lower()[0:len(rate_key) - len('_INVESTIGATOR')],
                    investigator_rates[rate_key])

            new_investigator_rates.save()

        new_investigator_instance.rates = new_investigator_rates
        new_investigator_instance.save()

        return HttpResponseRedirect('/administrator/investigators/?created=True')

    return render(request, 'system_admin/new_investigator.html', context)


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def investigator(request, investigator_id):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    try:
        investigator_instance = Investigator.objects.get(pk=investigator_id)
    except:
        raise Http404

    context = dict()
    context['investigator'] = investigator_instance
    context['investigator_rates'] = investigator_instance.rates
    context['languages'] = all_languages
    context['countries'] = countries

    phone_number_one = investigator_instance.phone_number_one.replace('-', '').replace(' ', '')
    phone_number_two = investigator_instance.phone_number_two.replace('-', '').replace(' ', '')
    context['phone_number_one'] = phone_number_one
    context['phone_number_two'] = phone_number_two

    if request.is_ajax() and request.POST and 'context' in request.POST:
        if request.POST['context'] == 'suspend':
            investigator_instance.is_active = False
            investigator_instance.user.is_active = False
            investigator_instance.user.save()
            investigator_instance.save()
            return HttpResponse('')
        elif request.POST['context'] == 'resume':
            investigator_instance.is_active = True
            investigator_instance.user.is_active = True
            investigator_instance.user.save()
            investigator_instance.save()
            return HttpResponse('')


        elif request.POST['context'] == 'delete':
            user_instance = investigator_instance.user

            for case in Case.objects.filter(investigator=investigator_instance).exclude(status='Closed'):
                case.investigator = None
                case.save()

            user_instance.is_active = False
            user_instance.save()
            return HttpResponse('')
        else:
            return HttpResponse('')

    if request.POST:
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']

        investigator_instance.user.first_name = first_name
        investigator_instance.user.last_name = last_name
        investigator_instance.user.save()

        street_one = request.POST['street-1']
        
        street_two = None
        if 'street-2' in request.POST:
            street_two = request.POST['street-2']
        
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        zip_code = request.POST['zip-code']

        investigator_instance.address.street_one = street_one
        investigator_instance.address.street_two = street_two
        investigator_instance.address.city = city
        investigator_instance.address.state = state
        investigator_instance.address.country = country
        investigator_instance.address.zip_code = zip_code
        investigator_instance.address.save()
        
        coordinates = investigator_instance.address.get_coordinates()
        
        if coordinates is not None:
            investigator_instance.address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                   str(coordinates['longitude'])
            investigator_instance.address.save()

        new_secondary_address = None

        try:
            street_one = request.POST['secondary-street-1']
        
            street_two = None
            if 'street-2' in request.POST:
                street_two = request.POST['secondary-street-2']

            city = request.POST['secondary-city']
            state = request.POST['secondary-state']
            country = request.POST['secondary-country']
            zip_code = request.POST['secondary-zip-code']

            if investigator_instance.secondary_address:
                investigator_instance.secondary_address.street_one = street_one
                investigator_instance.secondary_address.street_two = street_two
                investigator_instance.secondary_address.city = city
                investigator_instance.secondary_address.state = state
                investigator_instance.secondary_address.country = country
                investigator_instance.secondary_address.zip_code = zip_code
                investigator_instance.secondary_address.save()
        
                coordinates = investigator_instance.secondary_address.get_coordinates()

                if coordinates is not None:
                    investigator_instance.secondary_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                           str(coordinates['longitude'])
                    investigator_instance.secondary_address.save()
            else:
                new_secondary_address = Address(street_one=street_one, street_two=street_two, city=city, state=state, zip_code=zip_code,
                                      country=country)
                new_secondary_address.save()
        
                coordinates = investigator_instance.secondary_address.get_coordinates()

                if coordinates is not None:
                    investigator_instance.secondary_address.gmaps_link = 'https://www.google.com/maps/place/' + str(coordinates['latitude']) + ',' + \
                           str(coordinates['longitude'])
                    investigator_instance.secondary_address.save()

                investigator_instance.secondary_address = new_secondary_address
                investigator_instance.save()
        except:
            pass

        nickname = request.POST['nickname']
        languages = repr([str(ele) for ele in request.POST.getlist('languages')])

        phone_number_one = request.POST['phone-1']

        phone_number_two = None
        if 'phone-2' in request.POST:
            phone_number_two = request.POST['phone-2']

        email_one = request.POST['email-1']

        email_two = None
        if 'email-2' in request.POST:
            email_two = request.POST['email-2']

        more_info = None
        if 'more-info' in request.POST:
            more_info = request.POST['more-info']
        photograph = None

        if request.FILES and 'photograph' in request.FILES:
            photograph = request.FILES['photograph']
            investigator_instance.photograph = photograph

        investigator_instance.nickname = nickname
        investigator_instance.languages = languages

        investigator_instance.phone_number_one = phone_number_one
        investigator_instance.phone_number_two = phone_number_two

        investigator_instance.email_one = email_one
        investigator_instance.email_two = email_two

        investigator_instance.more_info = more_info

        investigator_instance.save()

        investigator_rates_keys = [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator In Area options']] + \
                         [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator Out of Area options']] + \
                        [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator miscellaneous options']]

        investigator_rates = dict()

        for rate_key in investigator_rates_keys:
            investigator_rates[rate_key] = float(request.POST[rate_key.lower().replace('_', '-')])

        investigator_rates_instance = None
        if investigator_instance.rates is not None:
            investigator_rates_instance = investigator_instance.rates
        else:
            investigator_rates_instance = InvestigatorRates()
            investigator_rates_instance.save()
            context['investigator_rates'] = investigator_rates_instance

        for rate_key in investigator_rates_keys:
            setattr(investigator_rates_instance, rate_key.lower()[0:len(rate_key) - len('_INVESTIGATOR')], investigator_rates[rate_key])

            investigator_rates_instance.save()

        investigator_instance.rates = investigator_rates_instance
        investigator_instance.save()
        
    phone_number_one = investigator_instance.phone_number_one.replace('-', '').replace(' ', '')
    phone_number_two = investigator_instance.phone_number_two.replace('-', '').replace(' ', '')
    context['phone_number_one'] = phone_number_one
    context['phone_number_two'] = phone_number_two
    return render(request, 'system_admin/investigator_details.html', context)


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def rates(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if request.POST:
        rates_keys = [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm In Area options']] + \
                     [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm Out of Area options']] + \
                     [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Law firm miscellaneous options']] + \
                     [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator In Area options']] + \
                     [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator Out of Area options']] + \
                     [rate for rate in CONSTANCE_CONFIG_FIELDSETS['Investigator miscellaneous options']]

        for rate_key in rates_keys:
            setattr(config, rate_key, request.POST[rate_key.lower().replace('_', '-')])

    return render(request, 'system_admin/rates.html')


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def delete_case_invoice(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'case_id' not in request.POST:
        return HttpResponseRedirect('/')

    case_id = request.POST['case_id']
    case_instance = Case.objects.get(pk=case_id)
    invoice_to_be_deleted = case_instance.invoice
    
    if invoice_to_be_deleted:
        
        invoice_lines = InvoiceLine.objects.filter(invoice = invoice_to_be_deleted)

        all_cases_containing_same_invoice = Case.objects.filter(invoice = invoice_to_be_deleted)

        for case in all_cases_containing_same_invoice:
            case.invoice = None
            case.total_amount_billed_to_law_firm = 0
            case.save()


    # print invoice_lines

    # case_instance.invoice.id
    # case_instance.invoice.delete()
    invoice_to_be_deleted.is_deleted = True
    invoice_to_be_deleted.save()
    # case_instance.invoice = None
    # case_instance.save()

    return HttpResponse('')

@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def delete_case_invoice_as_csv(request):
    
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'case_id' not in request.POST:
        return HttpResponseRedirect('/')

    case_id = request.POST['case_id']
    case_instance = Case.objects.get(pk=case_id)
    invoice_to_be_deleted = case_instance.invoice_as_csv
    print "hello"
    if invoice_to_be_deleted:
        
        invoice_lines = InvoiceLine.objects.filter(invoice = invoice_to_be_deleted)

        all_cases_containing_same_invoice = Case.objects.filter(invoice_as_csv = invoice_to_be_deleted)

        for case in all_cases_containing_same_invoice:
            case.invoice_as_csv = None
            case.total_amount_billed_to_law_firm = 0
            case.save()
        
        

    # print invoice_lines

    # case_instance.invoice.id
    # case_instance.invoice.delete()
    invoice_to_be_deleted.is_deleted = True
    invoice_to_be_deleted.save()
    # case_instance.invoice = None
    # case_instance.save()

    return HttpResponse('')


@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def delete_case_invoice_as_excel(request):
    
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'case_id' not in request.POST:
        return HttpResponseRedirect('/')

    case_id = request.POST['case_id']
    case_instance = Case.objects.get(pk=case_id)
    invoice_to_be_deleted = case_instance.invoice_as_excel
    print "hello"
    if invoice_to_be_deleted:
        
        invoice_lines = InvoiceLine.objects.filter(invoice = invoice_to_be_deleted)

        all_cases_containing_same_invoice = Case.objects.filter(invoice_as_excel = invoice_to_be_deleted)

        for case in all_cases_containing_same_invoice:
            case.invoice_as_excel = None
            case.total_amount_billed_to_law_firm = 0
            case.save()
        
        

    # print invoice_lines

    # case_instance.invoice.id
    # case_instance.invoice.delete()
    invoice_to_be_deleted.is_deleted = True
    invoice_to_be_deleted.save()
    # case_instance.invoice = None
    # case_instance.save()

    return HttpResponse('')

@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def delete_document(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'document_id' not in request.POST:
        return HttpResponseRedirect('/')

    try:
        document_id = request.POST['document_id']
        document_instance = Document.objects.get(pk=document_id)
        law_firm_id = request.POST['law_firm_id']
    except:
        print "No document_id or law firm"

    try:
        attached_documents = AttachedDocument.objects.filter(document = document_instance)
        # if attached_documents:
        #     raise SuspiciousOperation("Invalid request; Cannot delete document as the document is attached to a case")
        for attached_document in attached_documents:
            attached_document.delete()

        if document_instance:
            document_instance.law_firm = None

        document_instance.is_deleted = True
        document_instance.save()
    except:
        print "Error: Attached document not found and not deleted"

    # return HttpResponse('')
    return HttpResponseRedirect('/administrator/law-firm/'+ law_firm_id +'/')
@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def generate_report(request):

    import datetime
    import csv

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')
    
    if request.POST:
        
        if request.is_ajax() and 'context' in request.POST and request.POST['context'] == 'update-table':
            # Handle table update
            case_id = request.POST['case-id']

            case_instance = Case.objects.get(pk=case_id)

            case_instance.no_of_miles_travelled = float(request.POST['number-of-miles-travelled'])
            case_instance.no_of_free_miles_law_firm = float(request.POST['number-of-free-miles'])
            case_instance.basic_fee_law_firm = float(request.POST['basic-fee'])
            case_instance.mileage_rate_law_firm = float(request.POST['mileage-rate'])
            case_instance.additional_expenses = float(request.POST['additional-expenses'])

            case_instance.save()

            return HttpResponse('')
        elif request.is_ajax() and 'context' in request.POST and request.POST['context'] == 'pay':

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
        elif 'context' in request.POST and request.POST['context'] == 'download-csv-selected-cases':
            # generate CSV for only specific cases
            try:
                case_ids = request.POST['case_ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
            except:
                return HttpResponseRedirect('/')

            all_cases_in_range = []
            
            for case_id in case_ids:
                try:
                    case_instance = Case.objects.get(pk=case_id)
                    all_cases_in_range.append(case_instance)
                except :
                    context = dict()
                    context['error'] = 'An error occurred while generating payment report'
                    return render(request, 'system_admin/generate_report.html',context)
                    pass
            response = HttpResponse(content_type='text/csv')
            
            response['Content-Disposition'] = 'attachment; filename="Payment Report.csv"'

            writer = csv.writer(response)
            writer.writerow(['Case Name', 'Investigator name','Adult Cients','Child Clients', 'Location of client', 'No. of miles travelled',
                             'No. of free miles', 'Basic fee', 
                            #  'No. of signatures',
                              'Mileage rate',
                             'Additional expenses','Additional Expenses description', 'Expected payment', 'Amount paid to law firm', 'Difference',
                             'Amount paid to investigator', 'Profit', 'Payment status'])

            for case in all_cases_in_range:
                investigator_name = case.investigator.user.first_name + ' ' + case.investigator.user.last_name
                investigator_payment = 'PENDING'

                if case.is_investigator_paid:
                    investigator_payment = 'PAID'

                writer.writerow([case.name, investigator_name, case.adult_clients, case.child_clients,case.client_address.simple_address(), case.no_of_miles_travelled,
                                 case.no_of_free_miles_investigator, case.basic_fee_investigator,
                                #   case.number_of_signatures_required,
                                 case.mileage_rate_investigator, case.additional_expenses,
                                 case.additional_expenses_description, case.expected_payment, case.get_law_firm_price(),
                                 case.difference_in_payment(), case.get_investigator_price(), case.profit(), investigator_payment])

            return response
            

            return HttpResponse('')
        
        elif 'from' in request.POST and 'to' in request.POST and 'law-firm' in request.POST:
            try:
                
                from_date = request.POST.get('from')
                to_date = request.POST.get('to')
            
                from_components = from_date.split('/')
                from_date = datetime.datetime(int(from_components[2]), int(from_components[0]), int(from_components[1]))

                to_components = to_date.split('/')
                to_date = datetime.datetime(int(to_components[2]), int(to_components[0]), int(to_components[1]))

                if request.POST['law-firm'] == 'All Firms':
                    law_firm = 'All Firms'
                else:
                    law_firm_id = request.POST['law-firm']
                    law_firm = LawFirm.objects.get(pk=law_firm_id)     
            except:
                return HttpResponseRedirect('/administrator/generate-report/')
            if law_firm != 'All Firms' :    
                all_cases_in_range = Case.objects.filter(created_at__gte=from_date)\
                    .filter(created_at__lt=to_date)\
                    .filter(law_firm = law_firm)\
                    .filter(status='Closed')
            else:
                all_cases_in_range = Case.objects.filter(created_at__gte=from_date)\
                    .filter(created_at__lt=to_date)\
                    .filter(status='Closed')
                
            context = dict()
            context['cases'] = all_cases_in_range
            context['from'] = request.POST['from']
            context['to'] = request.POST['to']
            # context['law_firms'] = LawFirm.objects.all()
            # context['selected_firm'] = law_firm
            print "before download-csv context"

            
            
            # for case in all_cases_in_range:
            #     print(case.name)
            context['law_firms'] = LawFirm.objects.all()
            context['selected_firm'] = law_firm
            return render(request, 'system_admin/generate_report.html', context)
        elif 'context' in request.POST and request.POST['context'] == 'download-csv':
            # try:
                # print "in context download-csv"
            from_date = request.POST.get('from')
            to_date = request.POST.get('to')
        
            from_components = from_date.split('/')
            from_date = datetime.datetime(int(from_components[2]), int(from_components[0]), int(from_components[1]))

            to_components = to_date.split('/')
            to_date = datetime.datetime(int(to_components[2]), int(to_components[0]), int(to_components[1]))

            if request.POST.get('law_firm') == 'All Firms':
                law_firm = 'All Firms'
            else:
                law_firm_id = request.POST.get('law_firm')
                print (law_firm_id)
                law_firm = LawFirm.objects.get(pk=law_firm_id)     
            # except:
            #     return HttpResponseRedirect('/administrator/generate-report/')
            if law_firm != 'All Firms' :    
                all_cases_in_range = Case.objects.filter(created_at__gte=from_date)\
                    .filter(created_at__lt=to_date)\
                    .filter(law_firm = law_firm)\
                    .filter(status='Closed')
            else:
                all_cases_in_range = Case.objects.filter(created_at__gte=from_date)\
                    .filter(created_at__lt=to_date)\
                    .filter(status='Closed')

            print "passes download-csv context"
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Payment Report on '+str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))+'.csv"'

            writer = csv.writer(response)
            writer.writerow(['Case Name', 'Investigator name','Adult Clients','Child Clients', 'Location of client', 'No. of miles travelled',
                            'No. of free miles', 'Basic fee', 
                            # 'No. of signatures', 
                            'Mileage rate','Additional expenses','Additional Expenses description', 'Expected payment', 'Amount paid to law firm', 'Difference',
                            'Amount paid to investigator', 'Profit', 'Payment status'])

            for case in all_cases_in_range:
                investigator_name = case.investigator.user.first_name + ' ' + case.investigator.user.last_name
                investigator_payment = 'PENDING'

                if case.is_investigator_paid:
                    investigator_payment = 'PAID'

                writer.writerow([case.name, investigator_name, case.adult_clients, case.child_clients ,case.client_address.simple_address(), case.no_of_miles_travelled,
                                case.no_of_free_miles_investigator, case.basic_fee_investigator, 
                                # case.number_of_signatures_required,
                                case.mileage_rate_investigator, case.additional_expenses,
                                case.additional_expenses_description,
                                case.expected_payment, case.get_law_firm_price(),
                                case.difference_in_payment(), case.get_investigator_price(), case.profit(), investigator_payment])
            return response
            context = dict()
            context = dict()
            context['cases'] = all_cases_in_range
            context['from'] = request.POST['from']
            context['to'] = request.POST['to']
            context['law_firms'] = LawFirm.objects.all()
            context['selected_firm'] = law_firm
            return render(request, 'system_admin/generate_report.html', context)
            
    context = dict()
    context['law_firms'] = LawFirm.objects.all()        
    return render(request, 'system_admin/generate_report.html',context)


# @login_required(login_url='/')
# @permission_required('system_admin.can_view_system_admin',raise_exception=True)
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



@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def case_details(request, case_id):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    try:
        case_instance = Case.objects.get(pk=case_id)
    except:
        raise Http404

    context = dict()
    context['broker'] = broker
    context['case'] = case_instance
    context['law_firms'] = LawFirm.objects.all()
    context['countries'] = countries
    context['editable'] = case_instance.invoice is None and not case_instance.is_investigator_paid and case_instance.invoice_as_csv is None and case_instance.invoice_as_excel is None
    context['amount_paid_to_investigator'] = case_instance.get_investigator_price()
    context['amount_billed_to_law_firm'] = case_instance.get_law_firm_price()
    context['all_documents'] = Document.objects.all()
    client_mobile_phone = case_instance.client_mobile_phone.replace('-', '').replace(' ', '')
    context['client_mobile_phone'] = client_mobile_phone
    client_home_phone = case_instance.client_home_phone.replace('-', '').replace(' ', '')
    context['client_home_phone'] = client_home_phone
    

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

            # if 'documents' in request.FILES:
            #     uploaded_documents = request.FILES['documents']
            #     case_instance.documents = uploaded_documents

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

        elif request.is_ajax() and request.POST['context'] == 'pay':
            case_instance.is_investigator_paid = True
            case_instance.amount_paid_to_investigator = case_instance.get_investigator_price()
            case_instance.save()
            return HttpResponse('')

        elif request.is_ajax() and request.POST['context'] == 'unpay':
            case_instance.is_investigator_paid = False
            case_instance.save()
            return HttpResponse('')
    
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
    return render(request, 'system_admin/case_details.html', context)


# Complete rewrite of invoicing
@login_required(login_url='/')
@permission_required('system_admin.can_view_system_admin',raise_exception=True)
def generate_invoice_with_invoice_lines(request):

    import datetime

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if request.POST:
        law_firm_id = request.POST.get('law-firm')
        law_firm = LawFirm.objects.get(pk=law_firm_id)
        
        from_date = request.POST.get('from')
        to_date = request.POST.get('to')

        try:

            from_components = from_date.split('/')
            from_date = datetime.datetime(int(from_components[2]), int(from_components[0]), int(from_components[1]))

            to_components = to_date.split('/')
            to_date = datetime.datetime(int(to_components[2]), int(to_components[0]), int(to_components[1]))

        except:
            return HttpResponseRedirect('/administrator/generate-invoice/')

        all_cases_in_range = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date)\
            .filter(created_at__lte=to_date).filter(status='Closed')

        if request.POST.get('context') == 'list-cases':

            context = dict()
            context['law_firms'] = LawFirm.objects.all()
            context['selected_firm'] = law_firm
            law_firm_emails = []
            if law_firm.email_one:
                law_firm_emails.append(law_firm.email_one)
            if law_firm.email_two:
                law_firm_emails.append(law_firm.email_two)
            context['law_firm_emails'] = law_firm_emails
            context['cases'] = all_cases_in_range
            context['from'] = request.POST['from']
            context['to'] = request.POST['to']

            return render(request, 'system_admin/generate_invoice.html', context)
        
        elif request.POST.get('context') == 'print-aggregate-invoice':
            try:
                case_ids = request.POST['case-ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
            except:
                return HttpResponseRedirect('/')

            all_cases_in_range = []

            for case_id in case_ids:
                case_instance = Case.objects.get(pk=case_id)
                if case_instance.status.lower() != 'closed':
                    print "Invalid request; Invoice cannot be generated for cases which have not yet been closed. Case ID: %d"%case_instance.id
                    raise SuspiciousOperation("Invalid request; Invoice cannot be generated for cases which have not yet been closed. Case ID: %d"%case_instance.id)
                all_cases_in_range.append(case_instance)

            if request.POST['invoice-sending'] == 'download':

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

                generate_the_aggregate_invoice(response, law_firm, all_cases_in_range)

                return response

            elif request.POST['invoice-sending'] == 'mail':
                pdf_buffer = BytesIO()
                generate_the_aggregate_invoice(pdf_buffer, law_firm, all_cases_in_range)
                
                for case in all_cases_in_range:
                    case.is_invoice_mailed = True
                    case.save()

                pdf = pdf_buffer.getvalue()
                pdf_buffer.close()
                law_firm_email = request.POST.get('email')
                email_body = 'Find the attached invoice'
                message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
                message.attach('Invoice.pdf', pdf, 'application/pdf')
                message.send()

                context = dict()
                context['law_firms'] = LawFirm.objects.all()
                context['selected_firm'] = law_firm
                context['cases'] = all_cases_in_range
                context['from'] = request.POST['from']
                context['to'] = request.POST['to']
                law_firm_emails = []
                if law_firm.email_one:
                    law_firm_emails.append(law_firm.email_one)
                if law_firm.email_two:
                    law_firm_emails.append(law_firm.email_two)
                context['law_firm_emails'] = law_firm_emails

                return render(request, 'system_admin/generate_invoice.html', context)

        elif request.POST.get('context') == 'print-bulk-invoice':
            try:
                case_ids = request.POST['case-ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
            except:
                return HttpResponseRedirect('/')

            all_cases_in_range = []

            for case_id in case_ids:
                case_instance = Case.objects.get(pk=case_id)
                all_cases_in_range.append(case_instance)
            # ret_zip = None
            if request.POST['invoice-sending'] == 'download':
                response = HttpResponse(content_type='application/zip')
                response['Content-Disposition'] = 'filename=all_invoices.zip'

                buff = StringIO.StringIO()
                archive = zipfile.ZipFile(buff, 'w' ,zipfile.ZIP_DEFLATED)

                list_of_pdfs = []

                for case_in_range in all_cases_in_range:
                    file_like_object = StringIO.StringIO()
                    generate_the_invoice(file_like_object, law_firm, [case_in_range])

                    archive.writestr('Invoice for ' + case_in_range.name + '.pdf', file_like_object.getvalue())
                archive.close()
                buff.flush()
                ret_zip = buff.getvalue()
                buff.close()
                response.write(ret_zip)
                
                if request.POST['download'] == 'true':
                    return response
                else:
                    context = dict()
                    context['law_firms'] = LawFirm.objects.all()
                    context['selected_firm'] = law_firm
                    context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                    context['from'] = request.POST['from']
                    context['to'] = request.POST['to']
                    law_firm_emails = []
                    if law_firm.email_one:
                        law_firm_emails.append(law_firm.email_one)
                    if law_firm.email_two:
                        law_firm_emails.append(law_firm.email_two)
                    context['law_firm_emails'] = law_firm_emails

                    return render(request, 'system_admin/generate_invoice.html', context)

            elif request.POST['invoice-sending'] == 'mail':
                buff = StringIO.StringIO()
                archive = zipfile.ZipFile(buff, 'w' ,zipfile.ZIP_DEFLATED)

                list_of_pdfs = []

                for case_in_range in all_cases_in_range:
                    file_like_object = StringIO.StringIO()
                    generate_the_invoice(file_like_object, law_firm, [case_in_range])
                    case_in_range.is_invoice_mailed = True
                    case_in_range.save()
                    archive.writestr('Invoice for ' + case_in_range.name + '.pdf', file_like_object.getvalue())
                archive.close()
                buff.flush()
                ret_zip = buff.getvalue()
                buff.close()
                law_firm_email = request.POST.get('email')

                email_body = 'Find the attached invoice'
                message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
                message.attach('all_invoices.zip', ret_zip, 'application/zip')
                message.send()

                context = dict()
                context['law_firms'] = LawFirm.objects.all()
                context['selected_firm'] = law_firm
                context['cases'] = all_cases_in_range
                context['from'] = request.POST['from']
                context['to'] = request.POST['to']
                law_firm_emails = []
                if law_firm.email_one:
                    law_firm_emails.append(law_firm.email_one)
                if law_firm.email_two:
                    law_firm_emails.append(law_firm.email_two)
                context['law_firm_emails'] = law_firm_emails

                return render(request, 'system_admin/generate_invoice.html', context)
        
        elif request.POST.get('context') == 'print-single-invoice':
            case_instance = None
            try:
                case_id = request.POST['case-id']
                case_instance = Case.objects.get(pk=case_id)

            except:
                return HttpResponseRedirect('/')

            all_cases_in_range = [case_instance]

            if request.POST['invoice-sending'] == 'download':

                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="Invoice - '+ case_instance.name +'.pdf"'

                generate_the_invoice(response, law_firm, all_cases_in_range)
                print (response)
                if request.POST['download'] == 'true':
                    return response
                else:
                    context = dict()
                    context['law_firms'] = LawFirm.objects.all()
                    context['selected_firm'] = law_firm
                    context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                    context['from'] = request.POST['from']
                    context['to'] = request.POST['to']
                    law_firm_emails = []
                    if law_firm.email_one:
                        law_firm_emails.append(law_firm.email_one)
                    if law_firm.email_two:
                        law_firm_emails.append(law_firm.email_two)
                    context['law_firm_emails'] = law_firm_emails

                    return render(request, 'system_admin/generate_invoice.html', context)
            elif request.POST['invoice-sending'] == 'mail':
                pdf_buffer = BytesIO()
                generate_the_invoice(pdf_buffer, law_firm, all_cases_in_range)
                for case in all_cases_in_range:
                    case.is_invoice_mailed = True
                    case.save()
                pdf = pdf_buffer.getvalue()
                pdf_buffer.close()

                email_body = 'Find the attached invoice'
                law_firm_email = request.POST.get('email')
                # Hardcoding David's Email
                # message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm.email_one])
                message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
                message.attach('Invoice.pdf', pdf, 'application/pdf')
                message.send()

                context = dict()
                context['law_firms'] = LawFirm.objects.all()
                context['selected_firm'] = law_firm
                context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                context['from'] = request.POST['from']
                context['to'] = request.POST['to']
                law_firm_emails = []
                if law_firm.email_one:
                    law_firm_emails.append(law_firm.email_one)
                if law_firm.email_two:
                    law_firm_emails.append(law_firm.email_two)
                context['law_firm_emails'] = law_firm_emails
                return render(request, 'system_admin/generate_invoice.html', context)
            elif request.POST['invoice-sending'] == 'print':
                context = dict()
                context['pagesize'] = 'A4'
                template = get_template('system_admin/invoice.html')
                result = StringIO.StringIO()
                generate_the_invoice(result, law_firm, all_cases_in_range)
                invoice_pdf = result.getvalue()
                context['cases'] = all_cases_in_range
                html = template.render(context)
                pdf = pisa.pisaDocument(
                    StringIO.StringIO(html.encode("ISO-8859-1")), 
                    dest=result, link_callback=fetch_resources)
                if not pdf.err:
                    return HttpResponse(invoice_pdf, content_type='application/pdf')
                return HttpResponse("Error: <pre>%s</pre>" % escape(html))

        elif request.POST.get('context') == 'print-combined-invoice-as-csv':
            
            case_ids = []
            case_instance = None
            try:
                case_ids = request.POST['case-ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
                print (case_ids)
            except:
                return HttpResponseRedirect('/')
                # pass

            all_cases_in_range = []
            
            for case_id in case_ids:
                try:
                    case_instance = Case.objects.get(pk=case_id)
                    all_cases_in_range.append(case_instance)
                except :
                    context = dict()
                    context['error'] = 'An error occurred while generating payment report'
                    return render(request, 'system_admin/generate_report.html',context)
                    pass
            
            

            if request.POST['invoice-sending'] == 'download':

                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Combined-invoice.csv"'
                
                response = generate_bulk_invoice_as_csv(response, law_firm, all_cases_in_range)
                # print "hello"
                if request.POST['download'] == 'true':
                    # print "true"
                    return response
                else:
                    context = dict()
                    context['law_firms'] = LawFirm.objects.all()
                    context['selected_firm'] = law_firm
                    context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                    context['from'] = request.POST['from']
                    context['to'] = request.POST['to']
                    law_firm_emails = []
                    if law_firm.email_one:
                        law_firm_emails.append(law_firm.email_one)
                    if law_firm.email_two:
                        law_firm_emails.append(law_firm.email_two)
                    context['law_firm_emails'] = law_firm_emails

                    return render(request, 'system_admin/generate_invoice.html', context)
            elif request.POST['invoice-sending'] == 'mail':
                csv_buffer = BytesIO()
                generate_bulk_invoice_as_csv(csv_buffer, law_firm, all_cases_in_range)
                
                for case in all_cases_in_range:
                    case.is_invoice_as_csv_mailed = True
                    case.save()

                csv = csv_buffer.getvalue()
                csv_buffer.close()
                law_firm_email = request.POST.get('email')

                email_body = 'Find the attached invoice as csv'
                # Hardcoding David's Email
                # message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm.email_one])
                message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
                message.attach('Invoice.csv', csv, 'text/csv')
                message.send()

                context = dict()
                context['law_firms'] = LawFirm.objects.all()
                context['selected_firm'] = law_firm
                context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                context['from'] = request.POST['from']
                context['to'] = request.POST['to'] 
                law_firm_emails = []
                if law_firm.email_one:
                    law_firm_emails.append(law_firm.email_one)
                if law_firm.email_two:
                    law_firm_emails.append(law_firm.email_two)
                context['law_firm_emails'] = law_firm_emails       

                return render(request, 'system_admin/generate_invoice.html', context)

        elif request.POST.get('context') == 'print-single-invoice-csv':
            case_instance = None
            try:
                case_id = request.POST['case-id']
                case_instance = Case.objects.get(pk=case_id)

            except:
                return HttpResponseRedirect('/')

            all_cases_in_range = [case_instance]

            if request.POST['invoice-sending'] == 'download':

                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="Invoice - '+ case_instance.name +'.csv"'
                
                generate_the_invoice_as_csv(response, law_firm, all_cases_in_range)
                # print "hello"
                if request.POST['download'] == 'true':
                    print "true"
                    return response
                else:
                    context = dict()
                    context['law_firms'] = LawFirm.objects.all()
                    context['selected_firm'] = law_firm
                    context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                    context['from'] = request.POST['from']
                    context['to'] = request.POST['to']
                    law_firm_emails = []
                    if law_firm.email_one:
                        law_firm_emails.append(law_firm.email_one)
                    if law_firm.email_two:
                        law_firm_emails.append(law_firm.email_two)
                    context['law_firm_emails'] = law_firm_emails

                    return render(request, 'system_admin/generate_invoice.html', context)
            elif request.POST['invoice-sending'] == 'mail':
                csv_buffer = BytesIO()
                generate_the_invoice_as_csv(csv_buffer, law_firm, all_cases_in_range)
                print "hello"
                for case in all_cases_in_range:
                    print"in loop"
                    case.is_invoice_as_csv_mailed = True
                    case.save()
                    print (case.is_invoice_as_csv_mailed)
                    case_name = case.name
                
                csv = csv_buffer.getvalue()
                csv_buffer.close()
                # law_firm_email = law_firm.email_one
                law_firm_email = request.POST.get('email')
                print str(law_firm_email)
                email_body = 'Find the attached invoice as csv'
                # Hardcoding David's Email
                # message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm.email_one])
                message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
                message.attach('Invoice.csv', csv, 'text/csv')
                message.send()

                context = dict()
                context['law_firms'] = LawFirm.objects.all()
                context['selected_firm'] = law_firm
                context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                context['from'] = request.POST['from']
                context['to'] = request.POST['to']        
                law_firm_emails = []
                if law_firm.email_one:
                    law_firm_emails.append(law_firm.email_one)
                if law_firm.email_two:
                    law_firm_emails.append(law_firm.email_two)
                context['law_firm_emails'] = law_firm_emails

                return render(request, 'system_admin/generate_invoice.html', context)
        
        elif request.POST.get('context') == 'print-single-invoice-excel':
            case_instance = None
            try:
                case_id = request.POST['case-id']
                case_instance = Case.objects.get(pk=case_id)

            except:
                return HttpResponseRedirect('/')

            all_cases_in_range = [case_instance]

            if request.POST['invoice-sending'] == 'download':

                # response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                # response['Content-Disposition'] = 'attachment; filename="Invoice - '+ case_instance.name +'.xlsx"'
                
                # response = generate_the_invoice_as_excel(response, law_firm, all_cases_in_range)
                
                output = StringIO.StringIO()
                output = generate_the_invoice_as_excel(output, law_firm, all_cases_in_range)
                output.seek(0)
                response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response['Content-Disposition'] = 'attachment; filename="Invoice- '+ case_instance.name +'.xlsx"'
                # return response


                # print "hello"
                if request.POST['download'] == 'true':
                    print "true"
                    return response
                else:
                    context = dict()
                    context['law_firms'] = LawFirm.objects.all()
                    context['selected_firm'] = law_firm
                    context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                    context['from'] = request.POST['from']
                    context['to'] = request.POST['to']
                    law_firm_emails = []
                    if law_firm.email_one:
                        law_firm_emails.append(law_firm.email_one)
                    if law_firm.email_two:
                        law_firm_emails.append(law_firm.email_two)
                    context['law_firm_emails'] = law_firm_emails

                    return render(request, 'system_admin/generate_invoice.html', context)
            elif request.POST['invoice-sending'] == 'mail':
                excel_buffer = StringIO.StringIO()
                generate_the_invoice_as_excel(excel_buffer, law_firm, all_cases_in_range)
                print "excel"
                excel = excel_buffer.getvalue()
                excel_buffer.close()
                # law_firm_email = law_firm.email_one
                law_firm_email = request.POST.get('email')
                print str(law_firm_email)
                email_body = 'Find the attached invoice as excel'
                # Hardcoding David's Email
                # message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm.email_one])
                message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
                message.attach('Invoice.xlsx', excel, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                message.send()
                for case in all_cases_in_range:
                    print"in loop"
                    case.is_invoice_as_csv_mailed = True
                    case.save()

                context = dict()
                context['law_firms'] = LawFirm.objects.all()
                context['selected_firm'] = law_firm
                context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                context['from'] = request.POST['from']
                context['to'] = request.POST['to']        
                law_firm_emails = []
                if law_firm.email_one:
                    law_firm_emails.append(law_firm.email_one)
                if law_firm.email_two:
                    law_firm_emails.append(law_firm.email_two)
                context['law_firm_emails'] = law_firm_emails

                return render(request, 'system_admin/generate_invoice.html', context)
        
        elif request.POST.get('context') == 'print-combined-invoice-as-excel':
            
            case_ids = []
            case_instance = None
            try:
                case_ids = request.POST['case-ids'].replace('"', '').replace("'", '').replace('[', '').replace(']', '')\
                    .replace(' ', '').split(',')
                print (case_ids)
            except:
                return HttpResponseRedirect('/')
                # pass

            all_cases_in_range = []
            
            for case_id in case_ids:
                try:
                    case_instance = Case.objects.get(pk=case_id)
                    all_cases_in_range.append(case_instance)
                except :
                    context = dict()
                    context['error'] = 'An error occurred while generating payment report'
                    return render(request, 'system_admin/generate_report.html',context)
                    pass
            
            

            if request.POST['invoice-sending'] == 'download':

                output = StringIO.StringIO()
                output = generate_bulk_invoice_as_excel(output, law_firm, all_cases_in_range)
                output.seek(0)
                response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response['Content-Disposition'] = "attachment; filename=Combined-invoice.xlsx"
                
                if request.POST['download'] == 'true':
                    return response
                else:
                    context = dict()
                    context['law_firms'] = LawFirm.objects.all()
                    context['selected_firm'] = law_firm
                    context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                    context['from'] = request.POST['from']
                    context['to'] = request.POST['to']
                    law_firm_emails = []
                    if law_firm.email_one:
                        law_firm_emails.append(law_firm.email_one)
                    if law_firm.email_two:
                        law_firm_emails.append(law_firm.email_two)
                    context['law_firm_emails'] = law_firm_emails

                    return render(request, 'system_admin/generate_invoice.html', context)
            elif request.POST['invoice-sending'] == 'mail':
                excel_buffer = StringIO.StringIO()
                generate_bulk_invoice_as_excel(excel_buffer, law_firm, all_cases_in_range)
                
                # for case in all_cases_in_range:
                #     case.is_invoice_as_excel_mailed = True

                excel = excel_buffer.getvalue()
                excel_buffer.close()
                law_firm_email = request.POST.get('email')

                email_body = 'Find the attached invoice as excel'
                # Hardcoding David's Email
                # message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm.email_one])
                message = EmailMessage('Invoice', email_body, 'invoice@rapidsignnow.com', [law_firm_email])
                message.attach('Combined-Invoice.xlsx', excel, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                message.send()
                for case in all_cases_in_range:
                    print"in loop"
                    case.is_invoice_as_csv_mailed = True
                    case.save()

                context = dict()
                context['law_firms'] = LawFirm.objects.all()
                context['selected_firm'] = law_firm
                context['cases'] = Case.objects.filter(law_firm=law_firm).filter(created_at__gte=from_date).filter(created_at__lt=to_date).filter(status='Closed')
                context['from'] = request.POST['from']
                context['to'] = request.POST['to'] 
                law_firm_emails = []
                if law_firm.email_one:
                    law_firm_emails.append(law_firm.email_one)
                if law_firm.email_two:
                    law_firm_emails.append(law_firm.email_two)
                context['law_firm_emails'] = law_firm_emails       

                return render(request, 'system_admin/generate_invoice.html', context)


    context = dict()
    context['law_firms'] = LawFirm.objects.all()

    return render(request, 'system_admin/generate_invoice.html', context)

def generate_the_invoice(output, law_firm, cases):

    if len(cases) < 1:
        raise ValueError('Cases cannot be zero for invoicing')

    for case in cases:
        if case.invoice is not None:
            print_invoice_as_pdf(output,case.invoice, law_firm)
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
    print "Newly created Invoice ID: %d"%invoice.id

    for case in cases:

        case.invoice = invoice
        case.save()

        print "Invoice for case no: %d"%case.id

        #create new invoice line
        invoice_line = InvoiceLine()

        #FK assignments
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

        investigator_name = case.investigator.user.first_name + ' '+ case.investigator.user.last_name
        client_name = case.client_name
        client_address = case.client_address.simple_address()

        dol = case.dol
        case_closing_date = case.closing_date
        is_dol_provided = case.is_dol_provided
        locality = case.locality
        additional_expenses_description = case.additional_expenses_description
        rsn_extra_expenses = case.rsn_extra_expenses
        rsn_extra_expenses_info =  case.rsn_extra_expenses_description

        adult_clients = case.adult_clients
        child_clients = case.child_clients

        basic_fee_law_firm = case.basic_fee_law_firm
        no_of_free_miles_law_firm = case.no_of_free_miles_law_firm
        mileage_rate_law_firm = case.mileage_rate_law_firm
        cancelled_by = case.cancelled_by
        print "cancelled_by:%s"%case.cancelled_by
        cancelled_reason_description = case.cancelled_reason_description
        additional_expenses = case.additional_expenses
        no_of_miles_travelled = case.no_of_miles_travelled

        #Need to calculate these

        travel_expenses =  0
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
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_law_firm),float(no_of_miles_travelled), float(mileage_rate_law_firm),float(travel_expenses))
            
            if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained >0:
                number_of_billed_adults = 1
                number_of_billed_children = number_of_child_signatures_obtained - 1
            else:
                number_of_billed_adults = number_of_adult_signatures_obtained
                number_of_billed_children = number_of_child_signatures_obtained 


            if locality.lower() == 'in area':

                total_signature_fee_for_adults = default_in_area_payment_for_one_signature
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_in_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_in_area_payment_for_children

                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children
            
                if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses + rsn_extra_expenses

                
            

                
            else:
                # case out of area
                total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature 
                
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_out_of_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_out_of_area_payment_for_children

                
                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses + rsn_extra_expenses
            
            
        elif case.did_investigator_travel:
            
            number_of_adult_signatures_required = case.number_of_adult_signatures_required
            number_of_child_signatures_required = case.number_of_child_signatures_required
            number_of_adult_signatures_obtained = 0
            number_of_child_signatures_obtained = 0


            is_signature_obtained = False
            did_investigator_travel = True

            if no_of_miles_travelled > no_of_free_miles_law_firm and int(no_of_miles_travelled) != 0:
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_law_firm),float(no_of_miles_travelled), float(mileage_rate_law_firm),float(travel_expenses))
            else:
                print "Travel expenses is $0"

            total_amount_billed_to_law_firm = basic_fee_law_firm + travel_expenses + additional_expenses + rsn_extra_expenses

            pass
        else:
            
            travel_expense =  0
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
        if travel_expenses< 0:
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

        invoice_line.travel_expenses =  travel_expenses
        invoice_line.total_signature_fee_for_adults = total_signature_fee_for_adults
        invoice_line.total_signature_fee_for_children = total_signature_fee_for_children
        invoice_line.total_signature_fee = total_signature_fee
        invoice_line.total_amount_billed_to_law_firm = total_amount_billed_to_law_firm
        invoice_line.additional_expenses_description = additional_expenses_description
        invoice_line.rsn_extra_expenses_description = rsn_extra_expenses_info
        print "is_signature_obtained: %r" %is_signature_obtained
        print "did_investigator_travel: %r"%did_investigator_travel
        print "travel_expense: %f"%travel_expenses
        print "additional_expenses: %f"%additional_expenses
        print "rsn_extra_expenses: %f"%rsn_extra_expenses
        print "total_signature_fee_for_adults: %f"%total_signature_fee_for_adults
        print "total_signature_fee_for_children: %f"%total_signature_fee_for_children
        print "total_signature_fee: %f"%total_signature_fee
        print "total_amount_billed_to_law_firm: %f"%total_amount_billed_to_law_firm
        print "Cancelled_by:%s"%cancelled_by

        #Save the invoice_line
        invoice_line.save()

        #add the case total to the invoice total
        entire_invoice_total += total_amount_billed_to_law_firm

        invoice_lines.append(invoice_line)
    
    
    invoice.total_billed_amount = entire_invoice_total
    invoice.save()
    print_invoice_as_pdf(output,invoice, law_firm)

def generate_the_aggregate_invoice(output, law_firm, cases):

    if len(cases) < 1:
        raise ValueError('Cases cannot be zero for invoicing')

    # for case in cases:
    #     if case.invoice is not None:
    #         case.invoice = None
    #         case.total_amount_billed_to_law_firm = 0
    #         case.save()

    
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
    print "Newly created Invoice ID: %d"%invoice.id

    for case in cases:

        # case.invoice = invoice
        case.save()

        print "Invoice for case no: %d"%case.id

        #create new invoice line
        invoice_line = InvoiceLine()

        #FK assignments
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

        investigator_name = case.investigator.user.first_name + ' '+ case.investigator.user.last_name
        client_name = case.client_name
        client_address = case.client_address.simple_address()

        dol = case.dol
        case_closing_date = case.closing_date
        is_dol_provided = case.is_dol_provided
        locality = case.locality
        additional_expenses_description = case.additional_expenses_description
        date_of_signup = case.date_of_signup

        adult_clients = case.adult_clients
        child_clients = case.child_clients

        basic_fee_law_firm = case.basic_fee_law_firm
        no_of_free_miles_law_firm = case.no_of_free_miles_law_firm
        mileage_rate_law_firm = case.mileage_rate_law_firm
        cancelled_by = case.cancelled_by
        print "cancelled_by:%s"%case.cancelled_by
        cancelled_reason_description = case.cancelled_reason_description
        additional_expenses = case.additional_expenses
        no_of_miles_travelled = case.no_of_miles_travelled
        rsn_extra_expenses = case.rsn_extra_expenses
        rsn_extra_expenses_info =  case.rsn_extra_expenses_description

        #Need to calculate these

        travel_expenses =  0
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
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_law_firm),float(no_of_miles_travelled), float(mileage_rate_law_firm),float(travel_expenses))
            
            if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained >0:
                number_of_billed_adults = 1
                number_of_billed_children = number_of_child_signatures_obtained - 1
            else:
                number_of_billed_adults = number_of_adult_signatures_obtained
                number_of_billed_children = number_of_child_signatures_obtained 


            if locality.lower() == 'in area':

                total_signature_fee_for_adults = default_in_area_payment_for_one_signature
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_in_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_in_area_payment_for_children

                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children
            
                if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses + rsn_extra_expenses

                
            

                
            else:
                # case out of area
                total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature 
                
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_out_of_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_out_of_area_payment_for_children

                
                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses + rsn_extra_expenses
            
            
        elif case.did_investigator_travel:
            
            number_of_adult_signatures_required = case.number_of_adult_signatures_required
            number_of_child_signatures_required = case.number_of_child_signatures_required
            number_of_adult_signatures_obtained = 0
            number_of_child_signatures_obtained = 0


            is_signature_obtained = False
            did_investigator_travel = True

            if no_of_miles_travelled > no_of_free_miles_law_firm and int(no_of_miles_travelled) != 0:
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_law_firm),float(no_of_miles_travelled), float(mileage_rate_law_firm),float(travel_expenses))
            else:
                print "Travel expenses is $0"

            total_amount_billed_to_law_firm = basic_fee_law_firm + travel_expenses + additional_expenses + rsn_extra_expenses

            pass
        else:
            
            travel_expense =  0
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
        if travel_expenses< 0:
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
        invoice_line.rsn_extra_expenses = rsn_extra_expenses

        invoice_line.additional_expenses = additional_expenses
        invoice_line.no_of_miles_travelled = no_of_miles_travelled

        invoice_line.travel_expenses =  travel_expenses
        invoice_line.total_signature_fee_for_adults = total_signature_fee_for_adults
        invoice_line.total_signature_fee_for_children = total_signature_fee_for_children
        invoice_line.total_signature_fee = total_signature_fee
        invoice_line.total_amount_billed_to_law_firm = total_amount_billed_to_law_firm
        invoice_line.additional_expenses_description = additional_expenses_description
        invoice_line.rsn_extra_expenses_description = rsn_extra_expenses_info
        print "is_signature_obtained: %r" %is_signature_obtained
        print "did_investigator_travel: %r"%did_investigator_travel
        print "travel_expense: %f"%travel_expenses
        print "additional_expenses: %f"%additional_expenses
        print "total_signature_fee_for_adults: %f"%total_signature_fee_for_adults
        print "total_signature_fee_for_children: %f"%total_signature_fee_for_children
        print "total_signature_fee: %f"%total_signature_fee
        print "total_amount_billed_to_law_firm: %f"%total_amount_billed_to_law_firm
        print "Cancelled_by:%s"%cancelled_by

        #Save the invoice_line
        invoice_line.save()

        #add the case total to the invoice total
        entire_invoice_total += total_amount_billed_to_law_firm

        invoice_lines.append(invoice_line)
    
    
    invoice.total_billed_amount = entire_invoice_total
    invoice.save()
    print_aggregate_invoice_as_pdf(output,invoice, law_firm)
def generate_the_invoice_as_csv(output, law_firm, cases):

    if len(cases) < 1:
        raise ValueError('Cases cannot be zero for invoicing')

    for case in cases:
        if case.invoice_as_csv is not None:
            print_invoice_as_csv(output,case.invoice_as_csv, law_firm)
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


    invoice_as_csv = Invoice()
    invoice_as_csv.law_firm_name = law_firm.name
    invoice_as_csv.law_firm_address = law_firm.address.simple_address()
    invoice_as_csv.law_firm_email = law_firm.email_one
    invoice_lines = []

    invoice_as_csv.save()
    print "Newly created Invoice ID: %d"%invoice_as_csv.id

    for case in cases:

        case.invoice_as_csv = invoice_as_csv
        case.save()

        print "Invoice for case no: %d"%case.id

        #create new invoice line
        invoice_line = InvoiceLine()

        #FK assignments
        invoice_line.invoice = invoice_as_csv
        invoice_line.case = case

    

        number_of_adult_signatures_required = 0
        number_of_child_signatures_required = 0
        number_of_adult_signatures_obtained = 0
        number_of_child_signatures_obtained = 0

        is_signature_obtained = False
        did_investigator_travel = False

        case_name = case.name
        case_created_at = case.created_at

        investigator_name = case.investigator.user.first_name + ' '+ case.investigator.user.last_name
        client_name = case.client_name
        client_address = case.client_address.simple_address()

        dol = case.dol
        case_closing_date = case.closing_date
        is_dol_provided = case.is_dol_provided
        locality = case.locality
        additional_expenses_description = case.additional_expenses_description
        date_of_signup = case.date_of_signup

        adult_clients = case.adult_clients
        child_clients = case.child_clients

        basic_fee_law_firm = case.basic_fee_law_firm
        no_of_free_miles_law_firm = case.no_of_free_miles_law_firm
        mileage_rate_law_firm = case.mileage_rate_law_firm
        cancelled_by = case.cancelled_by
        print "cancelled_by:%s"%case.cancelled_by
        cancelled_reason_description = case.cancelled_reason_description
        additional_expenses = case.additional_expenses
        no_of_miles_travelled = case.no_of_miles_travelled

        #Need to calculate these

        travel_expenses =  0
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
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_law_firm),float(no_of_miles_travelled), float(mileage_rate_law_firm),float(travel_expenses))
            
            if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained >0:
                number_of_billed_adults = 1
                number_of_billed_children = number_of_child_signatures_obtained - 1
            else:
                number_of_billed_adults = number_of_adult_signatures_obtained
                number_of_billed_children = number_of_child_signatures_obtained 


            if locality.lower() == 'in area':

                total_signature_fee_for_adults = default_in_area_payment_for_one_signature
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_in_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_in_area_payment_for_children

                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children
            
                if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses

                
            

                
            else:
                # case out of area
                total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature 
                
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_out_of_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_out_of_area_payment_for_children

                
                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses
            
            
        elif case.did_investigator_travel:
            
            number_of_adult_signatures_required = case.number_of_adult_signatures_required
            number_of_child_signatures_required = case.number_of_child_signatures_required
            number_of_adult_signatures_obtained = 0
            number_of_child_signatures_obtained = 0


            is_signature_obtained = False
            did_investigator_travel = True

            if no_of_miles_travelled > no_of_free_miles_law_firm and int(no_of_miles_travelled) != 0:
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_law_firm),float(no_of_miles_travelled), float(mileage_rate_law_firm),float(travel_expenses))
            else:
                print "Travel expenses is $0"

            total_amount_billed_to_law_firm = basic_fee_law_firm + travel_expenses + additional_expenses

            pass
        else:
            
            travel_expense =  0
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
        if travel_expenses< 0:
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
        invoice_line.no_of_miles_travelled = no_of_miles_travelled

        invoice_line.travel_expenses =  travel_expenses
        invoice_line.total_signature_fee_for_adults = total_signature_fee_for_adults
        invoice_line.total_signature_fee_for_children = total_signature_fee_for_children
        invoice_line.total_signature_fee = total_signature_fee
        invoice_line.total_amount_billed_to_law_firm = total_amount_billed_to_law_firm
        invoice_line.additional_expenses_description = additional_expenses_description

        print "is_signature_obtained: %r" %is_signature_obtained
        print "did_investigator_travel: %r"%did_investigator_travel
        print "travel_expense: %f"%travel_expenses
        print "additional_expenses: %f"%additional_expenses
        print "total_signature_fee_for_adults: %f"%total_signature_fee_for_adults
        print "total_signature_fee_for_children: %f"%total_signature_fee_for_children
        print "total_signature_fee: %f"%total_signature_fee
        print "total_amount_billed_to_law_firm: %f"%total_amount_billed_to_law_firm
        print "Cancelled_by:%s"%cancelled_by

        #Save the invoice_line
        invoice_line.save()

        #add the case total to the invoice total
        entire_invoice_total += total_amount_billed_to_law_firm

        invoice_lines.append(invoice_line)
    
    
    invoice_as_csv.total_billed_amount = entire_invoice_total
    invoice_as_csv.save()
    print_invoice_as_csv(output,invoice_as_csv, law_firm)
    
def print_invoice_as_pdf(output,invoice, law_firm):
    
    invoice_number = invoice.id
    invoice_lines = InvoiceLine.objects.filter(invoice=invoice).order_by('case_created_at')
    
    
    light_peacock_green = '#dbf2f9'
    dark_peacock_green = '#166a83'

    doc = SimpleDocTemplate(output)
    story = []
    style = styles["Normal"]
    
    table_data = [[[Paragraph('Rapid Sign Now', ParagraphStyle('heading', fontSize=15, textColor=dark_peacock_green)), Spacer(1,0.3*inch)],
                   [Paragraph('INVOICE', ParagraphStyle('heading', fontSize=13, textColor=light_peacock_green, alignment=TA_RIGHT)), Spacer(1,0.3*inch)]]]

    table_data.append([Paragraph('8 Corporate park suite 300 <br /> Irvine, CA 92606 <br /> customerservice@rapidsignnow.com <br /> www.rapidsignnow.com <br /> P: 310-892-2043',# <br /> F: 123-555-0124',
                                 ParagraphStyle('address', fontSize=7, textColor=dark_peacock_green, leading=12)),
                       Paragraph('Invoice No.:' + str(invoice_number) + '<br /> Invoice Date: ' + datetime.datetime.now().strftime('%m-%d-%y')
                                 + ' <br /> Due Date: ' + (datetime.datetime.now() + datetime.timedelta(days=10)).strftime('%m-%d-%y'),
                                 ParagraphStyle('meta', fontSize=7, textColor=light_peacock_green, leading=12))])

    table_data.append([Paragraph('<b>BILL TO:</b> ' + law_firm.name + '<br />' + law_firm.address.simple_address(), ParagraphStyle('address', fontSize=7, textColor='#000000', leading=12)), ''])

    table_data.append([Paragraph('<b>Case Details</b>', ParagraphStyle('table-header', fontSize=13, textColor=light_peacock_green, alignment=TA_CENTER )),
                       Paragraph('<b>Amount</b>', ParagraphStyle('table-header', fontSize=13, textColor=light_peacock_green, alignment=TA_CENTER ))])

    case_style = ParagraphStyle('case-details', fontSize=8, textColor='#000000')
    law_firm_style = ParagraphStyle('law-firm-details', fontSize=8, textColor='#000000')
    price_style = ParagraphStyle('case-details', fontSize=8, textColor='#000000', alignment=TA_CENTER)

    
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
            signature_fee = Paragraph('Signature fees: $' + str(invoice_line.total_signature_fee), price_style)
        else:
            signature_fee = Paragraph('Basic fee: $' + str(invoice_line.basic_fee_law_firm), price_style)
        
        if invoice_line.is_dol_provided:
            try:
                dol_value = invoice_line.dol.strftime('%m-%d-%y')
            except:
                dol_value = str(invoice_line.dol.day) + "-" + str(invoice_line.dol.month) + "-" + str(invoice_line.dol.year)
        else:
            dol_value = 'Not Provided'

        # if invoice_line.is_signature_obtained:
        #     is_signature_obtained = 'Yes'
        # else:
        #     is_signature_obtained = 'No'
        additional_expenses_description = 'N.A'
        if invoice_line.additional_expenses_description != '':
            if invoice_line.rsn_extra_expenses_description != '':
                additional_expenses_description = invoice_line.additional_expenses_description + " and " + invoice_line.rsn_extra_expenses_description
            else:
                additional_expenses_description = invoice_line.additional_expenses_description
        elif invoice_line.rsn_extra_expenses_description != '':
            additional_expenses_description = invoice_line.rsn_extra_expenses_description

        travel_expenses_line = None
        additional_expenses_line = None

        if case_final_status.lower() == 'client cancelled':
            travel_expenses_line = Paragraph('Travel expenses: N.A', price_style)
            additional_expenses_line = Paragraph('Additional expenses: N.A', price_style)
            signature_fee = Paragraph('Signature fee: N.A' , price_style)
            case_final_status = case_cancelled_by
        else:
            travel_expenses_line = Paragraph('Travel expenses: $' + str(invoice_line.travel_expenses), price_style)
            additional_expenses = invoice_line.additional_expenses + invoice_line.rsn_extra_expenses
            additional_expenses_line = Paragraph('Additional expenses: $' + str(additional_expenses), price_style)

        if invoice_line.date_of_signup is not None:
            date_of_signup = invoice_line.date_of_signup
        else:
            date_of_signup = invoice_line.case_created_at

        table_data.append([
                            [
                                [Paragraph('<b>Case name: </b>' + invoice_line.case_name, case_style)],
                                [Paragraph('<b>Investigator: </b>' + invoice_line.investigator_name, case_style)],
                                [Paragraph('<b>Location: </b>' + invoice_line.client_address, case_style)],
                                [Paragraph('<b>DOL: </b>' + dol_value, case_style)],
                                [Paragraph('<b>Date of Sign Up: </b>' + date_of_signup.strftime('%m-%d-%y'), case_style)],
                                [Paragraph('<b>Locality: </b>' + invoice_line.locality, case_style)],
                                [Paragraph('<b>No. of miles: </b>' + str(invoice_line.no_of_miles_travelled), case_style)],
                                [Paragraph('<b>Mileage rate: </b>' + str(invoice_line.mileage_rate_law_firm), case_style)],
                                [Paragraph('<b>Adult clients: </b>' + invoice_line.adult_clients, case_style)],
                                [Paragraph('<b>Child clients: </b>' + invoice_line.child_clients, case_style)],
                                [Paragraph('<b>Additional expenses desc: </b>' + additional_expenses_description, case_style)],
                                [Paragraph('<b>Final Status: </b>' + case_final_status, case_style)],
                                [Paragraph('<b>Status additional info : </b>' + case_status_additional_info, case_style)],
                            ],
                            [
                                [signature_fee],
                                [travel_expenses_line],
                                [additional_expenses_line],
                                [Paragraph('Total price: $' + str(invoice_line.total_amount_billed_to_law_firm), price_style)]
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
                            [Paragraph('<br/><br/><br/><b>Clients Signed </b>', style)],
                        ],
                        [
                            [Paragraph('<br/><br/><br/><b>Cost </b>', style)]
                        ]
                        ])
            if(invoice_line.locality == 'In Area'):
                signature_fee_for_adult_clients = law_firm_rates.default_in_area_payment_for_one_signature + ((invoice_line.number_of_adult_signatures_obtained - 1) * law_firm_rates.default_in_area_payment_for_each_additional_adult_signature)
                signature_fee_for_child_clients = law_firm_rates.default_in_area_payment_for_children * invoice_line.number_of_child_signatures_obtained     
                
                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(adult_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(child_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
            else:

                signature_fee_for_adult_clients = law_firm_rates.default_out_of_area_payment_for_one_signature + ((invoice_line.number_of_adult_signatures_obtained - 1) * law_firm_rates.default_out_of_area_payment_for_each_additional_adult_signature)
                signature_fee_for_child_clients = law_firm_rates.default_out_of_area_payment_for_children * invoice_line.number_of_child_signatures_obtained     
                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(adult_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(child_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
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
                                                    [Paragraph('<br/>'+str(adult_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(child_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
            else:

                
                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(adult_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(child_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])

        else:
            table_data.append([
                                    [   [Paragraph('<br/><br/><br/><b>Detailed Invoice</b>',style)],
                                        [Paragraph('<b><br/>Basic Fee =</b> $ 0', law_firm_style)],
                                        [Paragraph('<b>Miles travelled =</b> 0',law_firm_style)],
                                        [Paragraph('<b>Travel Expenses =</b> $ 0',law_firm_style)],
                                        [Paragraph('<b>Additional expenses =</b> $ 0',law_firm_style)],
                                        [Paragraph('<b>RSN Extra expenses =</b> $ 0',law_firm_style)],
                                        [Paragraph('<b>Total Price =</b> $ 0',law_firm_style)],
                                        [Paragraph('<br/><br/>',style)]
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
        ('VALIGN',(0,0),(-1,-1),'TOP')
    ]))

    for loop in range(0, len(invoice_lines)):
        table_index = loop + 4
        if table_index % 2 != 0:
            table_content.setStyle(TableStyle([
                ('BACKGROUND', (0, table_index), (1, table_index), light_peacock_green)
            ]))

    rates_style = ParagraphStyle('case-details', fontSize=10, textColor='#000000')

    story.append(table_content)
    doc.build(story, onFirstPage=my_first_page, onLaterPages=my_later_pages)


    pass


# End Complete rewrite of invoicing
def print_aggregate_invoice_as_pdf(output,invoice, law_firm):
    
    invoice_number = invoice.id
    invoice_lines = InvoiceLine.objects.filter(invoice=invoice).order_by('case_created_at')
    
    
    light_peacock_green = '#dbf2f9'
    dark_peacock_green = '#166a83'

    doc = SimpleDocTemplate(output)
    story = []
    style = styles["Normal"]
    
    table_data = [[[Paragraph('Rapid Sign Now', ParagraphStyle('heading', fontSize=15, textColor=dark_peacock_green)), Spacer(1,0.3*inch)],
                   [Paragraph('INVOICE', ParagraphStyle('heading', fontSize=13, textColor=light_peacock_green, alignment=TA_RIGHT)), Spacer(1,0.3*inch)]]]

    table_data.append([Paragraph('8 Corporate park suite 300 <br /> Irvine, CA 92606 <br /> customerservice@rapidsignnow.com <br /> www.rapidsignnow.com <br /> P: 310-892-2043',# <br /> F: 123-555-0124',
                                 ParagraphStyle('address', fontSize=7, textColor=dark_peacock_green, leading=12)),
                       Paragraph('Invoice No.:' + str(invoice_number) + '<br /> Invoice Date: ' + datetime.datetime.now().strftime('%m-%d-%y')
                                 + ' <br /> Due Date: ' + (datetime.datetime.now() + datetime.timedelta(days=10)).strftime('%m-%d-%y'),
                                 ParagraphStyle('meta', fontSize=7, textColor=light_peacock_green, leading=12))])

    table_data.append([Paragraph('<b>BILL TO:</b> ' + law_firm.name + '<br />' + law_firm.address.simple_address(), ParagraphStyle('address', fontSize=7, textColor='#000000', leading=12)), ''])

    table_data.append([Paragraph('<b>Case Details</b>', ParagraphStyle('table-header', fontSize=13, textColor=light_peacock_green, alignment=TA_CENTER )),
                       Paragraph('<b>Amount</b>', ParagraphStyle('table-header', fontSize=13, textColor=light_peacock_green, alignment=TA_CENTER ))])

    case_style = ParagraphStyle('case-details', fontSize=8, textColor='#000000')
    law_firm_style = ParagraphStyle('law-firm-details', fontSize=8, textColor='#000000')
    price_style = ParagraphStyle('case-details', fontSize=8, textColor='#000000', alignment=TA_CENTER)

    
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
            signature_fee = Paragraph('Signature fees: $' + str(invoice_line.total_signature_fee), price_style)
        else:
            signature_fee = Paragraph('Basic fee: $' + str(invoice_line.basic_fee_law_firm), price_style)
        
        if invoice_line.is_dol_provided:
            try:
                dol_value = invoice_line.dol.strftime('%m-%d-%y')
            except:
                dol_value = str(invoice_line.dol.day) + "-" + str(invoice_line.dol.month) + "-" + str(invoice_line.dol.year)
        else:
            dol_value = 'Not Provided'

        # if invoice_line.is_signature_obtained:
        #     is_signature_obtained = 'Yes'
        # else:
        #     is_signature_obtained = 'No'
        additional_expenses_description = 'N.A'
        if invoice_line.additional_expenses_description != '':
            if invoice_line.rsn_extra_expenses_description != '':
                additional_expenses_description = invoice_line.additional_expenses_description + " and " + invoice_line.rsn_extra_expenses_description
            else:
                additional_expenses_description = invoice_line.additional_expenses_description
        elif invoice_line.rsn_extra_expenses_description != '':
            additional_expenses_description = invoice_line.rsn_extra_expenses_description
        travel_expenses_line = None
        additional_expenses_line = None
        rsn_extra_expenses = None

        if case_final_status.lower() == 'client cancelled':
            travel_expenses_line = Paragraph('Travel expenses: N.A', price_style)
            additional_expenses_line = Paragraph('Additional expenses: N.A', price_style)
            signature_fee = Paragraph('Signature fee: N.A' , price_style)
            case_final_status = case_cancelled_by
        else:
            travel_expenses_line = Paragraph('Travel expenses: $' + str(invoice_line.travel_expenses), price_style)
            additional_expenses = invoice_line.additional_expenses + invoice_line.rsn_extra_expenses
            print str(additional_expenses)
            additional_expenses_line = Paragraph('Additional expenses: $' + str(additional_expenses), price_style)

        if invoice_line.date_of_signup is not None:
            date_of_signup = invoice_line.date_of_signup
        else:
            date_of_signup = invoice_line.case_created_at


        table_data.append([
                            [
                                [Paragraph('<b>Case name: </b>' + invoice_line.case_name, case_style)],
                                [Paragraph('<b>Investigator: </b>' + invoice_line.investigator_name, case_style)],
                                [Paragraph('<b>Location: </b>' + invoice_line.client_address, case_style)],
                                [Paragraph('<b>DOL: </b>' + dol_value, case_style)],
                                [Paragraph('<b>Date of Sign Up: </b>' + date_of_signup.strftime('%m-%d-%y'), case_style)],
                                [Paragraph('<b>Locality: </b>' + invoice_line.locality, case_style)],
                                [Paragraph('<b>No. of miles: </b>' + str(invoice_line.no_of_miles_travelled), case_style)],
                                [Paragraph('<b>Mileage rate: </b>' + str(invoice_line.mileage_rate_law_firm), case_style)],
                                [Paragraph('<b>Adult clients: </b>' + invoice_line.adult_clients, case_style)],
                                [Paragraph('<b>Child clients: </b>' + invoice_line.child_clients, case_style)],
                                [Paragraph('<b>Additional expenses desc: </b>' + additional_expenses_description, case_style)],
                                [Paragraph('<b>Final Status: </b>' + case_final_status, case_style)],
                                [Paragraph('<b>Status additional info : </b>' + case_status_additional_info, case_style)],
                            ],
                            [
                                [signature_fee],
                                [travel_expenses_line],
                                [additional_expenses_line],
                                [Paragraph('Total price: $' + str(invoice_line.total_amount_billed_to_law_firm), price_style)]
                            ]
                        ])


        
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
                            [Paragraph('<br/><br/><br/><b>Clients Signed </b>', style)],
                        ],
                        [
                            [Paragraph('<br/><br/><br/><b>Cost </b>', style)]
                        ]
                        ])
            if(invoice_line.locality == 'In Area'):
                signature_fee_for_adult_clients = law_firm_rates.default_in_area_payment_for_one_signature + ((invoice_line.number_of_adult_signatures_obtained - 1) * law_firm_rates.default_in_area_payment_for_each_additional_adult_signature)
                signature_fee_for_child_clients = law_firm_rates.default_in_area_payment_for_children * invoice_line.number_of_child_signatures_obtained     
                
                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(adult_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(child_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
            else:

                signature_fee_for_adult_clients = law_firm_rates.default_out_of_area_payment_for_one_signature + ((invoice_line.number_of_adult_signatures_obtained - 1) * law_firm_rates.default_out_of_area_payment_for_each_additional_adult_signature)
                signature_fee_for_child_clients = law_firm_rates.default_out_of_area_payment_for_children * invoice_line.number_of_child_signatures_obtained     
                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(adult_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(child_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
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
                                                    [Paragraph('<br/>'+str(adult_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(child_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
            else:

                
                if invoice_line.adult_clients:
                    for adult_client in adult_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(adult_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])
                if invoice_line.child_clients:
                    for child_client in child_clients:

                        table_data.append([
                                                [ 
                                                    [Paragraph('<br/>'+str(child_client),law_firm_style)],  
                                                ],
                                                [
                                                    [Paragraph('<b><br/>_______________</b>',law_firm_style)],
                                                ]

                                            ])

        else:
            table_data.append([
                                    [   [Paragraph('<br/><br/><br/><b>Detailed Invoice</b>',style)],
                                        [Paragraph('<b><br/>Basic Fee =</b> $ 0', law_firm_style)],
                                        [Paragraph('<b>Miles travelled =</b> 0',law_firm_style)],
                                        [Paragraph('<b>Travel Expenses =</b> $ 0',law_firm_style)],
                                        [Paragraph('<b>Additional expenses =</b> $ 0',law_firm_style)],
                                        [Paragraph('<b>RSN Extra expenses =</b> $ 0',law_firm_style)],
                                        [Paragraph('<b>Total Price =</b> $ 0',law_firm_style)],
                                        [Paragraph('<br/><br/>',style)]
                                    ],
                                    [
                                        [Paragraph('', style)],
                                        [Paragraph('', style)]     
                                    ]
                                ])
        table_data.append([Paragraph('<br/><br/>', law_firm_style),
                        Paragraph('<br/><br/>', law_firm_style)])
        

    
    table_data.append([Paragraph('<b><br/> Total: </b>', style),
                        Paragraph('<br/>$' + str(invoice.total_billed_amount), style)])

    table_content = Table(table_data)
    table_content.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 1), light_peacock_green),
        ('BACKGROUND', (1, 0), (1, 1), dark_peacock_green),
        ('BACKGROUND', (0, 3), (1, 3), dark_peacock_green),
        ('VALIGN',(0,0),(-1,-1),'TOP')
    ]))

    for loop in range(0, len(invoice_lines)):
        table_index = loop + 7
       
        if table_index % 3 != 0:
            table_content.setStyle(TableStyle([
                ('BACKGROUND', (0, table_index), (1, table_index), light_peacock_green)
            ]))

    rates_style = ParagraphStyle('case-details', fontSize=10, textColor='#000000')

    story.append(table_content)
    doc.build(story, onFirstPage=my_first_page, onLaterPages=my_later_pages)


    pass
def print_invoice_as_csv(output,invoice, law_firm):
    import csv

    invoice_number = invoice.id
    invoice_lines = InvoiceLine.objects.filter(invoice=invoice).order_by('case_created_at')
    law_firm_rates = law_firm.rates
    
    
    
    print "hello"
    for invoice_line in invoice_lines:
        
        case_final_status = ''
        case_cancelled_by = ''
        case_status_additional_info = 'N.A'
        if invoice_line.is_signature_obtained:
            if invoice_line.number_of_adult_signatures_required <= invoice_line.number_of_adult_signatures_obtained and invoice_line.number_of_child_signatures_required <= invoice_line.number_of_child_signatures_obtained:
                case_final_status = 'Signature Obtained'
                # print str(case_final_status)
            else:
                case_final_status = 'Signatures Partially obtained'
                # print (case_final_status)
        elif invoice_line.did_investigator_travel:
            case_final_status = 'Signature Not Obtained'
        else:
            case_final_status = 'Client Cancelled'
            case_cancelled_by = invoice_line.cancelled_by
            if invoice_line.cancelled_reason_description:
                case_status_additional_info = invoice_line.cancelled_reason_description
                
        all_cases_in_range = []
        for invoice_line in invoice_lines:
            try:
                case_instance = Case.objects.get(pk=invoice_line.case.pk)
                all_cases_in_range.append(case_instance)
            except :
                context = dict()
                context['error'] = 'An error occurred while generating payment report'
                # return render(request, 'system_admin/generate_invoice.html',context)
                pass
            
            writer = csv.writer(output)
            writer.writerow(['BILL TO:', law_firm.name])
            writer.writerow(['',law_firm.address.simple_address()])
            writer.writerow(['',law_firm.phone_number_one])
            writer.writerow([''])
            writer.writerow(['Date of Signup','Date of Loss','Case Name',' Adult Clients','Child Clients','Address','Milaege','Total','Investigator'])
            print "writing"
            for case in all_cases_in_range:

                if case.date_of_signup is not None:
                    date_of_signup = case.date_of_signup
                else:
                    date_of_signup =  case.created_at

                investigator_name = case.investigator.user.first_name + ' ' + case.investigator.user.last_name
                total_payout = '$'+ str(case.get_law_firm_price()) 
                if case.locality == 'In Area':
                    writer.writerow([date_of_signup, case.dol, case.name, case.adult_clients, case.child_clients,case.client_address.simple_address(), case.no_of_miles_travelled,
                                    total_payout,
                                    investigator_name])
                else:
                    writer.writerow([date_of_signup, case.dol, case.name, case.adult_clients, case.child_clients,case.client_address.simple_address(), case.no_of_miles_travelled,
                                    total_payout,
                                    investigator_name])

                print "In loop for case"
                print (output)
            return output


    
    pass

def generate_bulk_invoice_as_csv(output,law_firm,all_cases_in_range):
    import csv
    law_firm_rates = law_firm.rates
    writer = csv.writer(output)
    writer.writerow(['BILL TO:', law_firm.name])
    writer.writerow(['',law_firm.address.simple_address()])
    writer.writerow(['',law_firm.phone_number_one])
    writer.writerow([''])
    writer.writerow(['Date of Signup','Date of Loss','Case Name',' Adult Clients','Child Clients','Address','Milaege','Total','Investigator'])
    print "writing"
    total = 0
    for case in all_cases_in_range:
        investigator_name = case.investigator.user.first_name + ' ' + case.investigator.user.last_name
        total_payout = '$ '+ str(case.get_law_firm_price())
        total_law_firm_payout = case.get_law_firm_price()
        total = total + total_law_firm_payout
        if case.date_of_signup is not None:
            date_of_signup = case.date_of_signup
        else:
            date_of_signup =  case.created_at
        
        if case.locality == 'In Area':
            writer.writerow([date_of_signup, case.dol, case.name, case.adult_clients, case.child_clients,case.client_address.simple_address(), case.no_of_miles_travelled,
                            total_payout,
                            investigator_name])
        else:
            writer.writerow([date_of_signup, case.dol, case.name, case.adult_clients, case.child_clients,case.client_address.simple_address(), case.no_of_miles_travelled,
                            total_payout,
                            investigator_name])
    total = '$ ' + str(total)
    writer.writerow([''])
    writer.writerow(['','','','','','','Total',total])
    return output
    

def fetch_resources(uri, rel):
    path = join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    return path

def generate_the_invoice_as_excel(output, law_firm, cases):

    if len(cases) < 1:
        raise ValueError('Cases cannot be zero for invoicing')

    for case in cases:
        if case.invoice_as_excel is not None:
            output = print_invoice_as_excel(output,case.invoice_as_excel, law_firm)
            return output

    
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


    invoice_as_excel = Invoice()
    invoice_as_excel.law_firm_name = law_firm.name
    invoice_as_excel.law_firm_address = law_firm.address.simple_address()
    invoice_as_excel.law_firm_email = law_firm.email_one
    invoice_lines = []

    invoice_as_excel.save()
    print "Newly created Invoice ID: %d"%invoice_as_excel.id

    for case in cases:

        case.invoice_as_excel = invoice_as_excel
        case.save()

        print "Invoice for case no: %d"%case.id

        #create new invoice line
        invoice_line = InvoiceLine()

        #FK assignments
        invoice_line.invoice = invoice_as_excel
        invoice_line.case = case

    

        number_of_adult_signatures_required = 0
        number_of_child_signatures_required = 0
        number_of_adult_signatures_obtained = 0
        number_of_child_signatures_obtained = 0

        is_signature_obtained = False
        did_investigator_travel = False

        case_name = case.name
        case_created_at = case.created_at

        investigator_name = case.investigator.user.first_name + ' '+ case.investigator.user.last_name
        client_name = case.client_name
        client_address = case.client_address.simple_address()

        dol = case.dol
        case_closing_date = case.closing_date
        is_dol_provided = case.is_dol_provided
        locality = case.locality
        additional_expenses_description = case.additional_expenses_description
        date_of_signup = case.date_of_signup

        adult_clients = case.adult_clients
        child_clients = case.child_clients

        basic_fee_law_firm = case.basic_fee_law_firm
        no_of_free_miles_law_firm = case.no_of_free_miles_law_firm
        mileage_rate_law_firm = case.mileage_rate_law_firm
        cancelled_by = case.cancelled_by
        print "cancelled_by:%s"%case.cancelled_by
        cancelled_reason_description = case.cancelled_reason_description
        additional_expenses = case.additional_expenses
        no_of_miles_travelled = case.no_of_miles_travelled

        #Need to calculate these

        travel_expenses =  0
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
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_law_firm),float(no_of_miles_travelled), float(mileage_rate_law_firm),float(travel_expenses))
            
            if number_of_adult_signatures_obtained < 1 and number_of_child_signatures_obtained >0:
                number_of_billed_adults = 1
                number_of_billed_children = number_of_child_signatures_obtained - 1
            else:
                number_of_billed_adults = number_of_adult_signatures_obtained
                number_of_billed_children = number_of_child_signatures_obtained 


            if locality.lower() == 'in area':

                total_signature_fee_for_adults = default_in_area_payment_for_one_signature
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_in_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_in_area_payment_for_children

                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children
            
                if total_signature_fee > maximum_in_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_in_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses

                
            

                
            else:
                # case out of area
                total_signature_fee_for_adults = default_out_of_area_payment_for_one_signature 
                
                if (number_of_billed_adults - 1) > 0:
                    total_signature_fee_for_adults += (number_of_billed_adults - 1) * default_out_of_area_payment_for_each_additional_adult_signature
                
                total_signature_fee_for_children = number_of_billed_children * default_out_of_area_payment_for_children

                
                total_signature_fee = total_signature_fee_for_adults + total_signature_fee_for_children

                if total_signature_fee > maximum_out_of_area_payment_for_any_number_of_signatures:
                    total_signature_fee = maximum_out_of_area_payment_for_any_number_of_signatures

                total_amount_billed_to_law_firm = total_signature_fee + travel_expenses + additional_expenses
            
            
        elif case.did_investigator_travel:
            
            number_of_adult_signatures_required = case.number_of_adult_signatures_required
            number_of_child_signatures_required = case.number_of_child_signatures_required
            number_of_adult_signatures_obtained = 0
            number_of_child_signatures_obtained = 0


            is_signature_obtained = False
            did_investigator_travel = True

            if no_of_miles_travelled > no_of_free_miles_law_firm and int(no_of_miles_travelled) != 0:
                travel_expenses = ((no_of_miles_travelled - no_of_free_miles_law_firm) * mileage_rate_law_firm)
                print "Travel expenses:( %f free miles - %f miles travelled) * $%f per mile = $%f"%(float(no_of_free_miles_law_firm),float(no_of_miles_travelled), float(mileage_rate_law_firm),float(travel_expenses))
            else:
                print "Travel expenses is $0"

            total_amount_billed_to_law_firm = basic_fee_law_firm + travel_expenses + additional_expenses

            pass
        else:
            
            travel_expense =  0
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
        if travel_expenses< 0:
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
        invoice_line.no_of_miles_travelled = no_of_miles_travelled

        invoice_line.travel_expenses =  travel_expenses
        invoice_line.total_signature_fee_for_adults = total_signature_fee_for_adults
        invoice_line.total_signature_fee_for_children = total_signature_fee_for_children
        invoice_line.total_signature_fee = total_signature_fee
        invoice_line.total_amount_billed_to_law_firm = total_amount_billed_to_law_firm
        invoice_line.additional_expenses_description = additional_expenses_description

        print "is_signature_obtained: %r" %is_signature_obtained
        print "did_investigator_travel: %r"%did_investigator_travel
        print "travel_expense: %f"%travel_expenses
        print "additional_expenses: %f"%additional_expenses
        print "total_signature_fee_for_adults: %f"%total_signature_fee_for_adults
        print "total_signature_fee_for_children: %f"%total_signature_fee_for_children
        print "total_signature_fee: %f"%total_signature_fee
        print "total_amount_billed_to_law_firm: %f"%total_amount_billed_to_law_firm
        print "Cancelled_by:%s"%cancelled_by

        #Save the invoice_line
        invoice_line.save()

        #add the case total to the invoice total
        entire_invoice_total += total_amount_billed_to_law_firm

        invoice_lines.append(invoice_line)
    
    
    invoice_as_excel.total_billed_amount = entire_invoice_total
    invoice_as_excel.save()
    output = print_invoice_as_excel(output,invoice_as_excel, law_firm)
    return output

def print_invoice_as_excel(output,invoice, law_firm):
    import xlsxwriter
    import datetime

    invoice_number = invoice.id
    invoice_lines = InvoiceLine.objects.filter(invoice=invoice).order_by('case_created_at')
    law_firm_rates = law_firm.rates

    workbook = xlsxwriter.Workbook(output, {'remove_timezone': True})
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    money = workbook.add_format({'num_format': '$#,##0'})
    wrap = workbook.add_format()
    wrap.set_text_wrap()
    date_format = workbook.add_format({'num_format': 'm/d/yyyy'})
    bold_align = workbook.add_format({'bold':True,'align':'justify'})
    num = workbook.add_format()
    num.set_num_format('0.00')
    data = []
    
    
    
    print "hello"
    for invoice_line in invoice_lines:
        
        case_final_status = ''
        case_cancelled_by = ''
        case_status_additional_info = 'N.A'
        if invoice_line.is_signature_obtained:
            if invoice_line.number_of_adult_signatures_required <= invoice_line.number_of_adult_signatures_obtained and invoice_line.number_of_child_signatures_required <= invoice_line.number_of_child_signatures_obtained:
                case_final_status = 'Signature Obtained'
                # print str(case_final_status)
            else:
                case_final_status = 'Signatures Partially obtained'
                # print (case_final_status)
        elif invoice_line.did_investigator_travel:
            case_final_status = 'Signature Not Obtained'
        else:
            case_final_status = 'Client Cancelled'
            case_cancelled_by = invoice_line.cancelled_by
            if invoice_line.cancelled_reason_description:
                case_status_additional_info = invoice_line.cancelled_reason_description
                
        all_cases_in_range = []
        for invoice_line in invoice_lines:
            try:
                case_instance = Case.objects.get(pk=invoice_line.case.pk)
                all_cases_in_range.append(case_instance)
            except :
                context = dict()
                context['error'] = 'An error occurred while generating invoice'
                pass
            
            
            
            worksheet.write('A1','BILL TO:', bold)
            worksheet.write('B1',law_firm.name, bold)
            worksheet.write('B2',law_firm.address.simple_address(),bold)
            worksheet.write('B3',law_firm.phone_number_one,bold)
            worksheet.write('A5','Date Of Signup',bold_align)
            worksheet.write('B5','Date Of Loss',bold_align)
            worksheet.write('C5','Case Name',bold_align)
            worksheet.write('D5','Adult Clients',bold_align)
            worksheet.write('E5','Child Clients',bold_align)
            worksheet.write('F5','Address',bold_align)
            worksheet.write('G5','No of Miles',bold_align)
            worksheet.write('H5','Total',bold_align)
            worksheet.write('I5','Investigator',bold_align)
            worksheet.set_column('A:I', 12)

            
            count = 0
            
            
            for case in all_cases_in_range:
                if case.date_of_signup is not None:
                    date_of_signup = case.date_of_signup
                else:
                    date_of_signup =  case.created_at
                
                investigator_name = case.investigator.user.first_name + ' ' + case.investigator.user.last_name
                total_payout = case.get_law_firm_price()
                if case.locality == 'In Area':
                    data.append([date_of_signup, case.dol, case.name, case.adult_clients, case.child_clients,case.client_address.simple_address().decode('latin-1'), case.no_of_miles_travelled,total_payout,investigator_name])
                    count = count + 1
                else:
                    data.append([date_of_signup, case.dol, case.name, case.adult_clients, case.child_clients,case.client_address.simple_address(), case.no_of_miles_travelled,total_payout,investigator_name])
                    count = count + 1
                
                print "printing"
            row = 5
            col = 0
            for dos, dol, name, adult_clients, child_clients, client_address, miles, total, investigator in (data):
                
                worksheet.write_datetime(row, col, dos, date_format )
                worksheet.write_datetime(row, col + 1, dol, date_format )
                worksheet.write_string(row, col + 2, name, wrap)
                worksheet.write_string(row, col + 3, adult_clients, wrap)
                worksheet.write_string(row, col + 4, child_clients, wrap)
                worksheet.write_string(row, col + 5, client_address, wrap)
                worksheet.write_number(row, col + 6, miles, num)
                worksheet.write_number(row, col + 7, total, money)
                worksheet.write_string(row, col + 8, investigator, wrap)
                row += 1


    workbook.close()
    return output


    
    pass

def generate_bulk_invoice_as_excel(output,law_firm,all_cases_in_range):

    import csv

    workbook = xlsxwriter.Workbook(output, {'remove_timezone': True})
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    money = workbook.add_format({'num_format': '$#,##0'})
    wrap = workbook.add_format()
    wrap.set_text_wrap()
    date_format = workbook.add_format({'num_format': 'm/d/yyyy'})
    bold_align = workbook.add_format({'bold':True,'align':'justify'})
    num = workbook.add_format()
    num.set_num_format('0.00')
    data = [] 




    worksheet.write('A1','BILL TO:', bold)
    worksheet.write('B1',law_firm.name, bold)
    worksheet.write('B2',law_firm.address.simple_address(),bold)
    worksheet.write('B3',law_firm.phone_number_one,bold)
    worksheet.write('A5','Date Of Signup',bold_align)
    worksheet.write('B5','Date Of Loss',bold_align)
    worksheet.write('C5','Case Name',bold_align)
    worksheet.write('D5','Adult Clients',bold_align)
    worksheet.write('E5','Child Clients',bold_align)
    worksheet.write('F5','Address',bold_align)
    worksheet.write('G5','No of Miles',bold_align)
    worksheet.write('H5','Total',bold_align)
    worksheet.write('I5','Investigator',bold_align)
    worksheet.set_column('A:I', 12)

    row = 5
    col = 0        
    total_bulk = 0 
    
    
    for case in all_cases_in_range:
        if case.date_of_signup is not None:
            date_of_signup = case.date_of_signup
        else:
            date_of_signup =  case.created_at
        investigator_name = case.investigator.user.first_name + ' ' + case.investigator.user.last_name
        total_payout = case.get_law_firm_price()
        total_bulk = total_bulk + total_payout
        # print case.name
        # print case.client_address.simple_address().decode('latin-1')

        if case.locality == 'In Area':
            data.append([date_of_signup, case.dol, case.name, case.adult_clients, case.child_clients,case.client_address.simple_address().decode('latin-1'), case.no_of_miles_travelled,total_payout,investigator_name])
        else:
            data.append([date_of_signup, case.dol, case.name, case.adult_clients, case.child_clients,case.client_address.simple_address().decode('latin-1'), case.no_of_miles_travelled,total_payout,investigator_name])
            
        print "printing"
        
    for dos, dol, name, adult_clients, child_clients, client_address, miles, total, investigator in (data):
        
        worksheet.write_datetime(row, col, dos, date_format )
        worksheet.write_datetime(row, col + 1, dol, date_format )
        worksheet.write_string(row, col + 2, name, wrap)
        worksheet.write_string(row, col + 3, adult_clients, wrap)
        worksheet.write_string(row, col + 4, child_clients, wrap)
        worksheet.write_string(row, col + 5, client_address, wrap)
        worksheet.write_number(row, col + 6, miles, num)
        worksheet.write_number(row, col + 7, total, money)
        worksheet.write_string(row, col + 8, investigator, wrap)
        row += 1

    worksheet.write(row + 2, col+6,'Total',bold)
    worksheet.write(row+2,col+7,total_bulk,money)
    workbook.close()
    return output
    

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
    response['Content-Disposition'] = 'attachment; filename=%s' % document.file.name

    return response

def delete_attached_document(request):

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    if not request.POST or 'attached_document_id' not in request.POST:
        return HttpResponseRedirect('/')

    attached_document_id = request.POST['attached_document_id']
    attached_document_instance = AttachedDocument.objects.get(pk=attached_document_id)
    
    attached_document_instance.delete()
    

    return HttpResponse('')

def dashboard(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    try:
        system_admin = SystemAdmin.objects.get(user=request.user)
    except:
        return HttpResponseRedirect('/')

    context = dict()

    # in_progress = 
    total_cases  = Case.objects.filter(~Q(status="Duplicate delete"))
    total_cases_count  = total_cases.count()
    # client_cancelled = Case.objects.filter(status = "Closed").filter(Q(is_signature_obtained = False) & Q(did_investigator_travel = False))
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
    #<me
    broker_avg_closing_time_seconds = []
    #me>
    for broker in brokers:
        no_of_cases_added = 0
        no_of_cases_closed = 0
        date = timezone.localtime(timezone.now()).date() - timedelta(days=31)
        cases_on_current_date = total_cases.filter(created_by = broker).filter(created_at__gte = date)
        cases_on_current_date_closed = cases_on_current_date.filter(status = "Closed")
        no_of_cases_added = cases_on_current_date.count()
        no_of_cases_closed = cases_on_current_date_closed.count()
        #<me
        closed_cases_created_date = cases_on_current_date_closed.values_list('created_at', flat=True)
        closed_cases_closing_date = cases_on_current_date_closed.values_list('closing_date', flat=True)
        avg_closing_time=0
        for i in range(0,no_of_cases_closed):
            avg_closing_time += (closed_cases_closing_date[i]-closed_cases_created_date[i]).seconds
        if avg_closing_time!=0:
            avg_closing_time= avg_closing_time*1.0/no_of_cases_closed
        broker_avg_closing_time_seconds.append(avg_closing_time)
        #me>
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
    
    broker_closing_percent_data = zip(broker_for_percentage_of_cases_closed,broker_no_of_cases_added,broker_no_of_cases_closed,percentage_of_cases_closed_for_broker,broker_avg_closing_time_seconds)

    #<me    
    mean_cases_added = sum(broker_no_of_cases_added)*1.0/len(broker_no_of_cases_added)
    max_cases_added = max(broker_no_of_cases_added)*1.0
    max_closing_time = max(broker_avg_closing_time_seconds)

    def normalized_rate(broker_row):
        closing_time = broker_row[4]
        percent_cases_closed = broker_row[3]
        no_cases_closed = broker_row[2]
        
        if percent_cases_closed==0:
            return -9999
        else:
            no_case_weight = numpy.log(no_cases_closed*max_cases_added/mean_cases_added)
            closing_time_weight = numpy.log(max_closing_time/closing_time)+1
            return no_case_weight*closing_time_weight*percent_cases_closed
    
    broker_closing_percent_data.sort(key = (lambda t: normalized_rate(t)),reverse=True)
    #me>
    
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
            # month_range = month_range.months
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
    
    return render(request, 'system_admin/dashboard.html',context)