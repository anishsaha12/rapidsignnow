from django.conf.urls import include, url
from django.contrib import admin
from broker import views

urlpatterns = [
    url(r'^create-new-case/', views.create_new_case),
    url(r'^all-cases/', views.all_cases),
    url(r'^case-details/(?P<case_id>[0-9]+)/', views.case_details),
    url(r'^show-investigator-details/', views.show_investigator_details),
    url(r'^change-status/', views.change_status),
    url(r'^assign-investigator/', views.assign_investigator),
    url(r'^my-profile/', views.my_profile),
    url(r'^mark-as-read/', views.mark_as_read),
    url(r'^get-investigator-rates/', views.get_investigator_rates),
    url(r'^get-law-firm-rates/', views.get_law_firm_rates),
    url(r'^change-password/', views.change_password),
    url(r'^all-notifications/', views.get_all_notifications),
    url(r'^delete-document', views.delete_document),
    url(r'^mark-case', views.mark_case),
    url(r'^dashboard', views.dashboard),
]
