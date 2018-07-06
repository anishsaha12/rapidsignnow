from django.conf.urls import include, url
from django.contrib import admin
from law_firm import views

urlpatterns = [
    url(r'^all-cases/', views.all_cases),
    url(r'^case-details/(?P<case_id>[0-9]+)/', views.case_details),
    url(r'^show-investigator-details/', views.show_investigator_details),
    url(r'^my-profile/', views.my_profile),
    url(r'^change-password/', views.change_password),
    url(r'^manage-documents/', views.manage_documents),
    url(r'^dashboard', views.dashboard),
    url(r'^create-payment-profile',views.create_payment_profile),
    url(r'^cases-to-be-charged',views.cases_to_be_charged),
    url(r'^charged-cases/',views.charged_cases),
]
