from django.conf.urls import url, include
from rest_framework import routers
from radiologo import views

router = routers.DefaultRouter()
router.register(r'codesystem', views.CodesystemViewSet)
router.register(r'scriptelement', views.ScriptelementViewSet)
router.register(r'header', views.HeaderViewSet)
router.register(r'footer', views.FooterViewSet)
router.register(r'articlehtml', views.ArticlehtmlViewSet)
router.register(r'code', views.CodeViewSet)
router.register(r'estudio', views.EstudioViewSet)
router.register(r'plantilla', views.PlantillaViewSet)
router.register(r'plantillagruposldap', views.PlantillagruposldapViewSet)
router.register(r'seccion', views.SeccionViewSet)
router.register(r'entry', views.EntryViewSet)
router.register(r'qualifier', views.QualifierViewSet)
router.register(r'value', views.ValueViewSet)
router.register(r'autenticado', views.AutenticadoViewSet)
router.register(r'sec', views.SecViewSet)
router.register(r'susbsec', views.SusbsecViewSet)
router.register(r'susbsubsec', views.SusbsubsecViewSet)
router.register(r'firma', views.FirmaViewSet)
router.register(r'submit', views.SubmitViewSet)
router.register(r'secentry', views.SecentryViewSet)
router.register(r'subsecentry', views.SubsecentryViewSet)
router.register(r'subsubsecentry', views.SubsubsecentryViewSet)

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^report_editor/(?P<study_iuid>[^/]+)$', views.report_editor, name='report_editor'),
    url(r'^xml/(?P<studyUID>[^/]+)/(?P<seriesUID>[^/]+)/(?P<objectUID>[^/]+)$', views.wado_xml, name='xml'),
    url(r'^rest/studies$', views.studies, name='studies'),
    url(r'^rest/studies/(?P<study_iuid>[^/]+)/series$', views.study_series, name='series'),
    url(r'^rest/studies/(?P<study_iuid>[^/]+)/series_description/(?P<series_description>[^/]+)$',
        views.instances_by_series_description, name='series_description'),
    url(r'^ajax_table_study$', views.ajax_table_study, name='ajax_table_study'),
    url(r'^ajax_table_series$', views.ajax_table_series, name='ajax_table_series'),
    url(r'^', include(router.urls)),
]
