from rest_framework import viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from html5cda import models, serializers


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CodesystemViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Codesystem.objects.all()
    # filter_backends = (filters.DjangoFilterBackend,)
    # filter_fields = (,)
    serializer_class = serializers.CodesystemSerializer
    pagination_class = StandardResultsSetPagination


class ScriptelementViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Scriptelement.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.ScriptelementSerializer
    pagination_class = StandardResultsSetPagination


class HeaderViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Header.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.HeaderSerializer
    pagination_class = StandardResultsSetPagination


class FooterViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Footer.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.FooterSerializer
    pagination_class = StandardResultsSetPagination


class ArticlehtmlViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Articlehtml.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('titulo','descripcion',)
    serializer_class = serializers.ArticlehtmlSerializer
    pagination_class = StandardResultsSetPagination


class CodeViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Code.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.CodeSerializer
    pagination_class = StandardResultsSetPagination


class EstudioViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Estudio.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.EstudioSerializer
    pagination_class = StandardResultsSetPagination


class PlantillaViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Plantilla.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.PlantillaSerializer
    pagination_class = StandardResultsSetPagination


class PlantillagruposldapViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Plantillagruposldap.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.PlantillagruposldapSerializer
    pagination_class = StandardResultsSetPagination


class SeccionViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Seccion.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.SeccionSerializer
    pagination_class = StandardResultsSetPagination


class SelectoptionViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Selectoption.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.SelectoptionSerializer
    pagination_class = StandardResultsSetPagination


class EntryViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Entry.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.EntrySerializer
    pagination_class = StandardResultsSetPagination


class QualifierViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Qualifier.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.QualifierSerializer
    pagination_class = StandardResultsSetPagination


class ValueViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Value.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.ValueSerializer
    pagination_class = StandardResultsSetPagination


class AutenticadoViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Autenticado.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.AutenticadoSerializer
    pagination_class = StandardResultsSetPagination


class SecViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Sec.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SecSerializer
    pagination_class = StandardResultsSetPagination


class SubsecViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Subsec.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SubsecSerializer
    pagination_class = StandardResultsSetPagination


class SubsubsecViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Subsubsec.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SubsubsecSerializer
    pagination_class = StandardResultsSetPagination


class FirmaViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Firma.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.FirmaSerializer
    pagination_class = StandardResultsSetPagination


class SubmitViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Submit.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SubmitSerializer
    pagination_class = StandardResultsSetPagination
