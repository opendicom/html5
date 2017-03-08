from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from html5cda import models
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from urllib.parse import urlencode
from urllib.parse import quote
from datetime import datetime
import hashlib


@login_required(login_url='/html5dicom/login')
def editor(request, *args, **kwargs):
    html = ''
    modalidades = models.Estudio.objects.values('modalidad').annotate(Count('modalidad')) \
        .order_by('modalidad')
    studies_list = []
    for estudio in models.Estudio.objects.filter(modalidad=request.GET['Modality']):
        studies_list += [{
            'id': estudio.id,
            'description': estudio.code.displayname
        }]
    template_list = []
    for plantilla in models.Plantilla.objects.filter(
                    Q(estudio__modalidad=request.GET['Modality']) | Q(estudio__modalidad='ALL')):
        template_list += [{
            'id': plantilla.id,
            'description': plantilla.title
        }]
    if 'plantilla' in request.GET:
        # edicion de informe
        secciones = models.Seccion.objects.filter(plantilla=request.GET['plantilla']).order_by('ordinal')
        headscripts = models.IntermediateHeadScript.objects.filter(plantilla=request.GET['plantilla'])
        bodyscripts = models.IntermediateBodyScript.objects.filter(plantilla=request.GET['plantilla'])
        headers = models.IntermediatePlantillaHeader.objects.filter(plantilla=request.GET['plantilla'])
        footers = models.IntermediatePlantillaFooter.objects.filter(plantilla=request.GET['plantilla'])
        context_user = {'context': {'secciones': secciones,
                                    'headscripts': headscripts,
                                    'bodyscripts': bodyscripts,
                                    'headers': headers,
                                    'footers': footers
                                    }}
        html = render_to_string('html5cda/editor_template.html', context_user)
    else:
        # nuevo informe
        try:
            plantilla = models.Plantilla.objects.get(estudio__modalidad=request.GET['Modality'],
                                                     estudio__code__displayname=request.GET['StudyDescription'])
        except models.Plantilla.DoesNotExist:
            plantilla = models.Plantilla.objects.get(estudio__modalidad='ALL')
        secciones = models.Seccion.objects.filter(plantilla=plantilla).order_by('ordinal')
        headscripts = models.IntermediateHeadScript.objects.filter(plantilla=plantilla)
        bodyscripts = models.IntermediateBodyScript.objects.filter(plantilla=plantilla)
        headers = models.IntermediatePlantillaHeader.objects.filter(plantilla=plantilla)
        footers = models.IntermediatePlantillaFooter.objects.filter(plantilla=plantilla)
        context_user = {'context': {'secciones': secciones,
                                    'headscripts': headscripts,
                                    'bodyscripts': bodyscripts,
                                    'headers': headers,
                                    'footers': footers
                                    }}
        html = render_to_string('html5cda/editor_template.html', context_user)

    context_user = {'context': {
                                'html_plantilla': html,
                                'modalidades': modalidades,
                                'studies_list': studies_list,
                                'template_list': template_list}
                    }
    return render(request, template_name='html5cda/editor.html', context=context_user)


def viewport(request, *args, **kwargs):
    return render(request, template_name='html5cda/templates/viewport.html')


def studies_list(request, *args, **kwargs):
    studies_list = []
    for estudio in models.Estudio.objects.filter(modalidad=request.GET['modalidad']):
        studies_list += [{
            'id': estudio.id,
            'description': estudio.code.displayname
        }]
    data = {"studies_list": studies_list}
    return JsonResponse(data)


def template_list(request, *args, **kwargs):
    template_list = []
    for plantilla in models.Plantilla.objects.filter( Q(estudio=request.GET['estudio']) | Q(estudio__modalidad='ALL')):
        template_list += [{
            'id': plantilla.id,
            'description': plantilla.title
        }]
    data = {"template_list": template_list}
    return JsonResponse(data)


def get_template(request, *args, **kwargs):
    secciones = models.Seccion.objects.filter(plantilla=request.GET['template']).order_by('ordinal')
    headscripts = models.IntermediateHeadScript.objects.filter(plantilla=request.GET['template'])
    bodyscripts = models.IntermediateBodyScript.objects.filter(plantilla=request.GET['template'])
    headers = models.IntermediatePlantillaHeader.objects.filter(plantilla=request.GET['template'])
    footers = models.IntermediatePlantillaFooter.objects.filter(plantilla=request.GET['template'])
    context_user = {'context': {'secciones': secciones,
                                'headscripts': headscripts,
                                'bodyscripts': bodyscripts,
                                'headers': headers,
                                'footers': footers
                    }}
    html = render_to_string('html5cda/editor_template.html', context_user)
    return HttpResponse(html)


def get_save_template(request, *args, **kwargs):
    try:
        submit = models.Submit.objects.get(eiud=request.GET.get('study_uid'))
        return HttpResponse(submit.urlparamsenviado)
    except models.Submit.DoesNotExist:
        return HttpResponse('')


def save_template(request, *args, **kwargs):
    post_param = request.POST.dict()
    response_save = dict()
    if 'csrfmiddlewaretoken' in post_param: del post_param['csrfmiddlewaretoken']
    if 'usuario1' in post_param: del post_param['usuario1']
    if 'clave1' in post_param: del post_param['clave1']
    if request.POST.get("guardar"):
        submit, created = models.Submit.objects.update_or_create(
            plantilla=models.Plantilla.objects.get(id=request.POST.get('plantilla')),
            eaccnum=request.POST.get('AccessionNumber'),
            eaccoid=request.POST.get('accessionNumberOID'),
            urlparamsrecibido='',
            listoparaautenticacion='',
            eiud=request.POST.get('StudyIUID'),
        )
        submit.urlparamsenviado = urlencode(post_param, quote_via=quote)
        submit.save()
        response_save = {'message': 'Guardado Correctamente'}
    elif request.POST.get("firmar"):
        submit, submit_created = models.Submit.objects.update_or_create(
            plantilla=models.Plantilla.objects.get(id=request.POST.get('plantilla')),
            eaccnum=request.POST.get('AccessionNumber'),
            eaccoid=request.POST.get('accessionNumberOID'),
            urlparamsrecibido='',
            listoparaautenticacion='',
            eiud=request.POST.get('StudyIUID'),
        )
        submit.urlparamsenviado = urlencode(post_param, quote_via=quote)
        submit.save()
        firma, firma_created = models.Firma.objects.update_or_create(
            informe=submit,
            md5=hashlib.md5(urlencode(post_param, quote_via=quote).encode('utf-8')).hexdigest(),
            fecha=datetime.now()
        )

    elif request.POST.get("firmarAutenticar"):
        print('firmarAutenticar')
    elif request.POST.get("borrarPlantilla"):
        print('borrarPlantilla')
    elif request.POST.get("crearPlantilla"):
        print('crearPlantilla')
    return JsonResponse(response_save)
    #return JsonResponse({'error': 'prueba de error'})
    #return JsonResponse({'message': 'guardado correctamente'})
