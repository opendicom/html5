from django.conf.urls import url, include
from rest_framework import routers
from html5cda import views

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
router.register(r'subsec', views.SubsecViewSet)
router.register(r'subsubsec', views.SubsubsecViewSet)
router.register(r'firma', views.FirmaViewSet)
router.register(r'submit', views.SubmitViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
