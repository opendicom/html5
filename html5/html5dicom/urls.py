from django.conf.urls import url
from html5dicom import views

urlpatterns = [
    url(r'^$', views.user_login, name=''),
    url(r'^login', views.user_login, name='login'),
    url(r'^logout', views.user_logout, name='logout'),
    url(r'^main', views.main, name='main'),
]