from __future__ import absolute_import, unicode_literals
from celery import Celery, task
from celery import shared_task





from django.core.mail import send_mail, EmailMessage
# from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
from django.conf import settings


import json
import requests
import django
import os
import StringIO
import datetime
import random
from twilio.rest import Client
from case.models import Case

os.environ.setdefault('DJANGO_SETTINGS_MODULE','rapidsignnow.settings')
from django.conf import settings




@shared_task
def scheduled_functions(case_id):
    from datetime import timedelta, datetime
    now = datetime.utcnow()
    print (now)
    eta = now + timedelta(hours=1)
    # eta = now + timedelta(minutes = 1)
    counts = [1,2,3]
    for count in counts:
        eta = now + timedelta(hours=count)
        send_notifications_first.apply_async([case_id],eta=eta)

    eta = now + timedelta(hours = 6)
    send_notifications_second.apply_async([case_id],eta=eta)
    eta = now + timedelta(hours = 20)
    send_notifications_third.apply_async([case_id],eta=eta)
    eta = now + timedelta(hours = 48)
    send_notifications_third.apply_async([case_id],eta=eta)

@shared_task
def send_notifications_first(case_id):
    case = Case.objects.get(pk=case_id)
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    if timezone.now() - case.created_at >= timedelta(hours=1) and ( case.status == "Inactive" or case.status == "In progress" ) and case.message_id != 12:
        print "inside first function"
        phone_number = case.investigator.phone_number_one
        try:
            longUrl = 'http://app.rapidsignnow.com/investigator/case-details/' +str(case.pk) + '/?key=' + case.random_string
            post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
            params = json.dumps({'longUrl': longUrl})
            response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

            
            shortened_url = longUrl
            try:
                shortened_url =  response.json()['id']
            except:
                pass
        except: 
            pass
        try:
            message = twilio_client.api.account.messages.create(to=phone_number,from_=settings.TWILIO_NOTIFICATIONS_PHONE_NUMBER,body='Have you scheduled appointment with '+ case.client_name +' for case '+ str(case.pk) + '   yet?  Type "'+ str(case.pk) + ' <space> 1" for yes, "'+ str(case.pk) + ' <space> 0" for no. Please send message from your registered number. If you are facing issues texting go to ' + shortened_url)
            case.message_id = 1
            case.save()
            print "sent email/msg first %s"%case.name
        except:
            print "could not send email/msg"

        
@shared_task
def send_notifications_second(case_id):
    case = Case.objects.get(pk=case_id)
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    if timezone.now() - case.created_at >= timedelta(hours=6) and case.status != "Client cancelled" and case.status != "Signature obtained" and case.status != "Signature not obtained" and case.status != "Closed" :
        phone_number = case.investigator.phone_number_one
        print "inside second function"    
        try:
            longUrl = 'http://app.rapidsignnow.com/investigator/case-details/' +str(case.pk) + '/?key=' + case.random_string
            post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
            params = json.dumps({'longUrl': longUrl})
            response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

            
            shortened_url = longUrl
            try:
                shortened_url =  response.json()['id']
            except:
                pass
        except: 
            pass
        try:
            message = twilio_client.api.account.messages.create(to=phone_number,from_=settings.TWILIO_NOTIFICATIONS_PHONE_NUMBER,body='Were you able to obtain all signatures from ' + case.client_name + ' for case '+ str(case.pk) + '?  Type "'+ str(case.pk) + ' <space> 1" for yes, "'+ str(case.pk) + ' <space> 0" for no. Please send message from your registered number. If you are facing issues texting go to ' + shortened_url)
            case.message_id = 3
            case.save()
            print "sent email/msg second %s"%case.name
        except:
            print "could not send email/msg"
@shared_task
def send_notifications_third(case_id):
    case = Case.objects.get(pk=case_id)
    twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    if (timezone.now() - case.created_at >= timedelta(hours=20) or timezone.now() - case.created_at >= timedelta(hours=20)) and case.status != "Client cancelled" and case.status != "Signature obtained" and case.status != "Signature not obtained" and case.status != "Closed" :
        phone_number = case.investigator.phone_number_one
        print "inside third function"
        try:
            longUrl = 'http://app.rapidsignnow.com/investigator/case-details/' +str(case.pk) + '/?key=' + case.random_string
            post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB8fCmfS2jTZhUoznt-CrCqfvZUuxPZhmM'
            params = json.dumps({'longUrl': longUrl})
            response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

            
            shortened_url = longUrl
            try:
                shortened_url =  response.json()['id']
            except:
                pass
        except: 
            pass
        try:
            message = twilio_client.api.account.messages.create(to=phone_number,from_=settings.TWILIO_NOTIFICATIONS_PHONE_NUMBER,body='Were you able to obtain all signatures from ' + case.client_name + ' for case '+ str(case.pk) + '? Type "'+ str(case.pk) + ' <space> 1" for yes, "'+ str(case.pk) + ' <space> 0" for no and "'+ str(case.pk) + '<space> 2" for client cancelled. Please send message from your registered number. If you are facing issues texting go to ' + shortened_url)
            case.message_id = 4
            case.save()
            print "sent email/msg third %s"%case.name
        except:
            print "could not send email/msg"
