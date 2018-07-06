from django.conf.urls import include, url
from django.contrib import admin
from investigator import views

urlpatterns = [
    url(r'^assigned-cases/', views.assigned_cases),
    url(r'^closed-cases/', views.closed_cases),
    url(r'^case-details/(?P<case_id>[0-9]+)/', views.case_details),
    url(r'^case-details-closed/(?P<case_id>[0-9]+)/', views.case_details_closed),
    url(r'^change-status/', views.change_status),
    url(r'^accept-case/', views.accept_case),
    url(r'^decline-case/', views.decline_case),
    url(r'^my-profile/', views.my_profile),
    url(r'^mark-as-read/', views.mark_as_read),
    url(r'^change-password/', views.change_password),
    url(r'^all-cases/', views.all_cases),
    url(r'^mark-case', views.mark_case),
    url(r'^incoming-message', views.handle_incoming_message),
    url(r'^dashboard', views.dashboard),

]
