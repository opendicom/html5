from django.conf.urls import url
from proxyrest import views

urlpatterns = [
    url(r'^session/institution/(?P<institution>[^/]+)/user/(?P<user>[^/]+)/password/(?P<password>[^/]+)$',
        views.rest_login, name='login'),
    url(r'^session/(?P<session>[^/]+)/logout$', views.rest_logout, name='logout'),
    url(r'^session/(?P<session>[^/]+)/qido/', views.rest_qido, name='qido'),
    url(r'^session/(?P<session>[^/]+)/wado/', views.rest_wado, name='wado'),
    url(r'^study_web/(?P<session>[^/]+)/PatientID/(?P<patientID>[^/]+)', views.study_web, name='study_web'),
]
