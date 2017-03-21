from django.conf.urls import url
from proxyrest import views

urlpatterns = [
    url(r'^session/institution/(?P<institution>[^/]+)/user/(?P<user>[^/]+)/password/(?P<password>[^/]+)$',
        views.rest_login, name='login'),
    url(r'^session/(?P<session>[^/]+)/logout$', views.rest_logout, name='logout'),
    url(r'^session/(?P<session>[^/]+)/qido/', views.qido, name='qido'),
    url(r'^session/(?P<session>[^/]+)/wado/', views.wado, name='wado'),
]