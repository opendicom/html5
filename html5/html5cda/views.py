from django.shortcuts import HttpResponse, render_to_response, render
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from html5cda import models, serializers
import json
import requests
import urllib


def index(request):
    return render_to_response('html5cda/index.html')


def report_editor(request, *args, **kwargs):
    context = {'study_iuid': kwargs['study_iuid']}
    return render(request, 'html5cda/editor.html', context)


def ajax_table_study(request, *args, **kwargs):
    params = {'offset': request.GET.get('start'),
              'limit': request.GET.get('length')
              }
    if request.GET.get('_00100020') != '':
        params.update({'00100020': request.GET.get('_00100020')})
    if request.GET.get('_00100010') != '':
        params.update({'00100010': request.GET.get('_00100010')})
    if request.GET.get('_00080020') != '':
        params.update({'00080020': request.GET.get('_00080020')})
    if request.GET.get('_00080061') != '':
        params.update({'00080061': request.GET.get('_00080061')})
    url = 'http://127.0.0.1:8081/html5cda/rest/studies'
    data_pacs = requests.get(url, params)
    data_table = []
    for item in data_pacs.json():
        if request.GET.get('search_status') == 'informed':
            if 'DOC' in value_of('00080061', item):
                data_table.append(add_item_table_study(item,
                                                       request.GET.get('sessionrest'),
                                                       request.GET.get('user_rest'),
                                                       request.GET.get('institution')))
        elif request.GET.get('search_status') == 'authenticate':
            print('authenticate')
        elif request.GET.get('search_status') == 'unauthenticated':
            if 'DOC' not in value_of('00080061', item):
                data_table.append(add_item_table_study(item,
                                                       request.GET.get('sessionrest'),
                                                       request.GET.get('user_rest'),
                                                       request.GET.get('institution')))
        else: # all
            data_table.append(add_item_table_study(item,
                                                   request.GET.get('sessionrest'),
                                                   request.GET.get('user_rest'),
                                                   request.GET.get('institution')))
    data = {"draw": request.GET.get('draw'),
             "recordsTotal": 1000,
             "recordsFiltered": 1000,
             "data": data_table}
    return HttpResponse(json.dumps(data))


def ajax_table_series(request, *args, **kwargs):
    params = {'offset': request.GET.get('start'),
              'limit': request.GET.get('length')
              }
    url = 'http://127.0.0.1:8081/html5cda/rest/studies/' + request.GET.get('studyuid') + '/series'
    datapacs = requests.get(url, params)
    datatable = []
    for item in datapacs.json():
        datatable.append(add_item_table_series(item,
                                               request.GET.get('sessionrest'),
                                               request.GET.get('user_rest'),
                                               request.GET.get('institution')))
    data = {"draw": request.GET.get('draw'),
            "recordsTotal": 100,
            "recordsFiltered": 100,
            "data": datatable}
    return HttpResponse(json.dumps(data))


@api_view(['GET'])
def studies(request, *args, **kwargs):
    params_qido = dict(request.query_params)
    #params_qido['00080080'] = kwargs['institution']
    params_qido['includefield'] = 'all'
    if 'offset' in params_qido and 'limit' in params_qido:
        qido_url = models.Configuracion.objects.get(key='qidourl')
        pacs_resp = requests.get(qido_url.value + 'studies', params_qido)
        try:
            resp = pacs_resp.json()
            return Response(resp, status=status.HTTP_200_OK)
        except:
            return Response('', status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def study_series(request, *args, **kwargs):
    params_qido = dict(request.query_params)
    params_qido['0020000D'] = kwargs['study_iuid']
    params_qido['orderby'] = 'SeriesNumber'
    params_qido['includefield'] = 'all'
    if 'offset' in params_qido and 'limit' in params_qido:
        qidourl = models.Configuracion.objects.get(key='qidourl')
        pacs_resp = requests.get(qidourl.value + 'series', params_qido)
        try:
            resp = pacs_resp.json()
            return Response(resp, status=status.HTTP_200_OK)
        except:
            return Response('', status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def instances_by_series_description(request, *args, **kwargs):
    params_qido = dict(request.query_params)
    params_qido['0020000D'] = kwargs['study_iuid']
    params_qido['0008103E'] = kwargs['series_description']
    params_qido['orderby'] = '-00400244,-00400245'
    params_qido['includefield'] = 'all'
    if 'offset' in params_qido and 'limit' in params_qido:
        qidourl = models.Configuracion.objects.get(key='qidourl')
        pacs_resp = requests.get(qidourl.value + 'instances', params_qido)
        try:
            resp = pacs_resp.json()
            return Response(resp, status=status.HTTP_200_OK)
        except:
            return Response('', status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)


def add_item_table_study(item, session_rest, user_rest, institution_rest):
    row = []
    # show series
    row.append('<a href=# onClick="series(\'' + value_of('0020000D', item) + '\',\'' + pn_of('00100010', item) +
               '\',\'' + value_of('00081030', item) + '\')"><img title="Ver series" border=0 src=/static/html5cda' +
               '/img/ver_series.png></a>')
    # report
    if 'DOC' in value_of('00080061', item):
        uid_report = get_uid_series(value_of('0020000D', item),
                                    session_rest,
                                    user_rest,
                                    institution_rest,
                                    'SignedClinicalDocument')
        row.append('<a href=# onClick="view_xml(\'' + uid_report['studyUID'] + '\',\'' + uid_report['seriesUID'] +
                   '\',\'' + uid_report['objectUID'] + '\')"><img title="Ver informe" border=0 src=/static/html5cda/' +
                   'img/ver_cda.png></a>')
    else:
        row.append('<a href=# onClick="report(\'' + value_of('0020000D', item) + '\')"><img title="Informe" border=0 ' +
                   'src=/static/html5cda/img/informe.png></a>')
    # download or weasis
    row.append('<a href=/weasis-pacs-connector/viewer?studyUID=' + value_of('0020000D', item) + '><img ' + \
               'title="Descargar estudio" border=0 src=/static/html5cda/img/ver_imagenes.png></a>')
    # patient id
    row.append(value_of('00100020', item))
    # patient name
    row.append(pn_of('00100010', item))
    # informer
    row.append(pn_of('00081060', item))
    # modalities
    row.append(value_of('00080061', item))
    # study description
    row.append(value_of('00081030', item))
    # date time study
    row.append(date_of('00080020', item) + ' ' + time_of('00080030', item))
    return row


def add_item_table_series(item, session_rest, user_rest, institution_rest):
    row = []
    # series description
    row.append(value_of('0008103E', item))
    # part
    row.append(value_of('00180015', item))
    # number series
    row.append(value_of('00200011', item))
    # station name
    row.append(value_of('00081010', item))
    # series date time
    row.append(date_of('00400244', item) + ' ' + time_of('00400245', item))
    # view request  0008,0060 OT
    if 'OT' in value_of('00080060', item):
        uid_report = get_uid_series(value_of('0020000D', item),
                                    session_rest,
                                    user_rest,
                                    institution_rest,
                                    'solicitud')
        row.append('<a href=# onClick="view_xml(\'' + uid_report['studyUID'] + '\',\'' + uid_report['seriesUID'] +
                   '\',\'' + uid_report['objectUID'] + '\')"><img title="Ver solicitud" border=0 src=/static/html5cda/' +
                   'img/ver_solicitud.png></a>')
    else:
        row.append('')
    # weasis
    # row.append('<a href=/weasis-pacs-connector/viewer?studyUID=' + value_of('0020000D', item) + '&seriesUID=' +
    #           value_of('0020000E', item) + '><img title="Descargar serie" border=0 src=/static/html5cda/img/' +
    #           'ver_imagenes.png></a>')
    return row


def wado_xml(request, *args, **kwargs):

    wado_url = models.Configuracion.objects.get(key='wadourl')
    url_xml = wado_url.value + 'studyUID=' + kwargs['studyUID'] + '&seriesUID=' + kwargs['seriesUID'] + \
              '&objectUID=' + kwargs['objectUID'] + '&contentType=text/xml'
    content = urllib.request.urlopen(url_xml).read()
    content = content.decode('utf-8')
    content = content.replace('\x00', '')
    response = HttpResponse(content, content_type="text/xml")
    return response


def get_uid_series(study_uid, session_rest, user_rest, institution_rest, series_description):
    params = {'offset': 0,
              'limit': 10
              }
    url = 'http://127.0.0.1:8081/html5cda/rest/studies/' + study_uid + '/series_description/' + series_description
    instances = requests.get(url, params)
    try:
        resp = {}
        for item in instances.json():
            resp.update({'studyUID': value_of('0020000D', item),
                         'seriesUID': value_of('0020000E', item),
                         'objectUID': value_of('00080018', item)})
            break
        return resp
    except:
        return ''


def value_of(key, item):
    if key in item:
        if 'Value' in item[key]:
            return item[key]['Value'][0]
        else:
            return ''
    else:
        return ''


def pn_of(key, item):
    if key in item:
        if 'Value' in item[key]:
            if 'Alphabetic' in item[key]['Value'][0]:
                return item[key]['Value'][0]['Alphabetic']
            else:
                return ''
        else:
            return ''
    else:
        return ''


def date_of(key, item):
    if key in item:
        if 'Value' in item[key]:
            return format_date(item[key]['Value'][0])
        else:
            return ''
    else:
        return ''


def time_of(key, item):
    if key in item:
        if 'Value' in item[key]:
            return format_time(item[key]['Value'][0])
        else:
            return ''
    else:
        return ''


def format_date(value):
    return value[:4] + '-' + value[4:6] + '-' + value[6:8]


def format_time(value):
    return value[:2] + ':' + value[2:4] + ':' + value[4:6]


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


class HeadscriptViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Headscript.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.HeadscriptSerializer
    pagination_class = StandardResultsSetPagination


class BodyscriptViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Bodyscript.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.BodyscriptSerializer
    pagination_class = StandardResultsSetPagination


class PlantillaheaderViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Plantillaheader.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.PlantillaheaderSerializer
    pagination_class = StandardResultsSetPagination


class PlantillafooterViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Plantillafooter.objects.all()
    #filter_backends = (filters.DjangoFilterBackend,)
    #filter_fields = (,)
    serializer_class = serializers.PlantillafooterSerializer
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


class SusbsecViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Susbsec.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SusbsecSerializer
    pagination_class = StandardResultsSetPagination


class SusbsubsecViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Susbsubsec.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SusbsubsecSerializer
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


class SecentryViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Secentry.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SecentrySerializer
    pagination_class = StandardResultsSetPagination


class SubsecentryViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Subsecentry.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SubsecentrySerializer
    pagination_class = StandardResultsSetPagination


class SubsubsecentryViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    queryset = models.Subsubsecentry.objects.all()
    #filter_backends = (filters.DjangoFilterBackend)
    #filter_fields = ()
    serializer_class = serializers.SubsubsecentrySerializer
    pagination_class = StandardResultsSetPagination
