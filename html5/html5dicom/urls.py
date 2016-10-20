from django.conf.urls import url
from html5dicom import views

urlpatterns = [
    url(r'^$', views.user_login, name=''),
    url(r'^login', views.user_login, name='login'),
    url(r'^logout', views.user_logout, name='logout'),
    url(r'^main', views.main, name='main'),
    url(r'^weasis', views.weasis, name='weasis'),
    url(r'^wado', views.wado, name='wado'),
    url(r'^osirix', views.osirix, name='osirix'),
    url(r'^osirixmd', views.osirixmd, name='osirixmd'),
    url(r'^cornerstone', views.cornerstone, name='cornerstone'),
]