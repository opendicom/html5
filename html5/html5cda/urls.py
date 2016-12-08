from django.conf.urls import url, include
from html5cda import views

urlpatterns = [
    url(r'^editor', views.editor, name='editor'),
    url(r'^templates/help', views.help, name='help'),
    url(r'^templates/about', views.about, name='about'),
    url(r'^templates/viewport', views.viewport, name='viewport'),
    url(r'^templates/studyViewer', views.studyViewer, name='studyViewer'),
]
