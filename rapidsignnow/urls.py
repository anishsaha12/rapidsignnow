from django.conf.urls import include, url
from django.contrib import admin
from rapidsignnow import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'rapidsignnow.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^administrator/', include('system_admin.urls')),
    url(r'^investigator/', include('investigator.urls')),
    url(r'^broker/', include('broker.urls')),
    url(r'^master-broker/', include('master_broker.urls')),
    url(r'^law-firm/', include('law_firm.urls')),    
    url(r'^check-username/', views.check_username),
    url(r'^$', views.app_login),
    url(r'^logout/', views.app_logout)
]
