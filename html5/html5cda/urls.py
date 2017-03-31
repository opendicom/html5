from django.conf.urls import url, include
from html5cda import views

urlpatterns = [
    url(r'^editor', views.editor, name='editor'),
    url(r'^templates/viewport', views.viewport, name='viewport'),
    url(r'^ajax/studies_list', views.studies_list, name='studies_list'),
    url(r'^ajax/template_list', views.template_list, name='template_list'),
    url(r'^ajax/get_template', views.get_template, name='get_template'),
    url(r'^save_template', views.save_template, name='save_template'),
    url(r'^get_save_template', views.get_save_template, name='get_save_template'),
    url(r'^authenticate_report', views.generate_authenticate_report, name='authenticate_report'),
]
