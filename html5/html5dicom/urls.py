from django.conf.urls import url
from html5dicom import views

urlpatterns = [
    url(r'^$', views.user_login, name=''),
    url(r'^login', views.user_login, name='login'),
    url(r'^logout', views.user_logout, name='logout'),
    url(r'^main', views.main, name='main'),
    url(r'^wado$', views.wado, name='wado'),
    url(r'^password$', views.change_password, name='change_password'),
    url(r'^viewer_settings', views.viewer_settings, name='viewer_settings'),
    url(r'^data_tables_studies$', views.data_tables_studies, name='data_tables_studies'),
    url(r'^data_tables_series$', views.data_tables_series, name='data_tables_series'),
    url(r'^data_tables_patient$', views.data_tables_patient, name='data_tables_patient'),
    url(r'^study_token_weasis$', views.study_token_weasis, name='study_token_weasis'),
    url(r'^study_token_cornerstone$', views.study_token_cornerstone, name='study_token_cornerstone'),
    url(r'^cornerstone', views.cornerstone, name='cornerstone'),
    url(r'^study_token_zip$', views.study_token_zip, name='study_token_zip'),
    url(r'^show_cda$', views.show_cda, name='show_cda'),    
]
