from django.conf.urls import include, url
from django.contrib import admin
from system_admin import views

urlpatterns = [

    url(r'^profile/', views.profile),
    

    url(r'^law-firms/', views.law_firms),
    url(r'^law-firm/(?P<law_firm_id>[0-9]+)/', views.law_firm),
    url(r'^download/(?P<file_id>[0-9]+)/', views.download_doc),

    url(r'^investigators/', views.investigators),
    url(r'^investigator/(?P<investigator_id>[0-9]+)/', views.investigator),

    url(r'^brokers/', views.brokers),
    url(r'^broker/(?P<broker_id>[0-9]+)/', views.broker),

    url(r'^master-brokers/', views.master_brokers),
    url(r'^master-broker/(?P<master_broker_id>[0-9]+)/', views.master_broker),

    url(r'^new-law-firm/', views.new_law_firm),
    url(r'^new-investigator/', views.new_investigator),
    url(r'^new-broker/', views.new_broker),
    url(r'^new-master-broker/', views.new_master_broker),

    url(r'^case-details/(?P<case_id>[0-9]+)/', views.case_details),
    
    # url(r'^generate-invoice/', views.generate_invoice),
    url(r'^generate-invoice/', views.generate_invoice_with_invoice_lines),

    url(r'^generate-report/', views.generate_report),
    url(r'^rates/', views.rates),
    url(r'^delete-case-invoice-as-excel', views.delete_case_invoice_as_excel),
    url(r'^delete-case-invoice-as-csv', views.delete_case_invoice_as_csv),
    url(r'^delete-case-invoice', views.delete_case_invoice),
    url(r'^delete-document', views.delete_document),
    url(r'^delete-attached-document', views.delete_attached_document),
    url(r'^dashboard', views.dashboard),
]
