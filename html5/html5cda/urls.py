from django.conf.urls import url, include
from html5cda import views

urlpatterns = [
    url(r'^editor', views.editor, name='editor'),
]
