from django.conf.urls import url
from accounts import views

urlpatterns = [
    url(r'api/user$', views.UserCreate.as_view(), name='account-create'),
]
