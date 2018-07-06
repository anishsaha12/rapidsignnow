from django.shortcuts import get_object_or_404, render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User
from django.utils import timezone

from system_admin.models import SystemAdmin
from law_firm.models import LawFirm
from broker.models import Broker
from master_broker.models import MasterBroker
from investigator.models import Investigator

import json


def app_login(request):
    
    if request.POST:
        
        username = request.POST['username']
        password = request.POST['password']

        try:
            logged_in_user = authenticate(username=username, password=password)
        except:
            context = dict()
            context['error'] = 'The user could not be logged in'
            return render(request, 'login.html', context)

        if logged_in_user is None:
            context = dict()
            context['error'] = 'The user could not be logged in'
            return render(request, 'login.html', context)

        
        if not logged_in_user.is_active:
            context = dict()
            context['error'] = 'The user account has been suspended'
            return render(request, 'login.html', context)

        
        if SystemAdmin.objects.filter(user=logged_in_user).exists():
            login(request, logged_in_user)
            return HttpResponseRedirect('/administrator/law-firms/')
        elif LawFirm.objects.filter(user=logged_in_user).exists():
            login(request, logged_in_user)
            return HttpResponseRedirect('/law-firm/all-cases/')
        elif Broker.objects.filter(user=logged_in_user).exists():
            print('Broker exists')
            login(request, logged_in_user)
            return HttpResponseRedirect('/broker/create-new-case/')
        elif MasterBroker.objects.filter(user=logged_in_user).exists():
            login(request, logged_in_user)
            return HttpResponseRedirect('/master-broker/create-new-case/')
        elif Investigator.objects.filter(user=logged_in_user).exists():
            login(request, logged_in_user)
            return HttpResponseRedirect('/investigator/assigned-cases/')
        else:
            context = dict()
            context['error'] = 'This user is not registered for this platform'
            return render(request, 'login.html', context)
    
    return render(request, 'login.html')

def app_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def check_username(request):
    if not request.GET:
        return HttpResponse('')
    
    username = request.GET['email-1']
    response = None
    if User.objects.filter(username=username).exists():
        response = 'false'
    else:
        response = 'true'
    
    return HttpResponse(response)
    