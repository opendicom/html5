from django.conf.urls import url
from html5dicom import views

urlpatterns = [
    url(r'^$', views.user_login, name=''),
    url(r'^login', views.user_login, name='login'),
    url(r'^logout', views.user_logout, name='logout'),
    url(r'^main', views.main, name='main'),
    url(r'^weasis$', views.weasis, name='weasis'),
    url(r'^wado$', views.wado, name='wado'),
    url(r'^dcm.zip$', views.osirix, name='osirix'),
    url(r'^cornerstone$', views.cornerstone, name='cornerstone'),
    url(r'^password$', views.change_password, name='change_password'),
    url(r'^viewer_settings', views.viewer_settings, name='viewer_settings'),
    url(r'^datatables_studies', views.datatables_studies, name='datatables_studies'),
]
