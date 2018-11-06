from django.conf.urls import url, include
from django.contrib import admin
from html5dicom import views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Proxy Dicom Web')

urlpatterns = [
    url(r'^$', views.user_login),
    url(r'^html5dicom/', include('html5dicom.urls')),
    url(r'^html5cda/', include('html5cda.urls')),
    url(r'^proxydcmweb/', include('proxyrest.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/$', schema_view)
]
