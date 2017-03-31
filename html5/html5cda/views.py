from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from django.core.urlresolvers import reverse
from html5cda import models
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.db.models import Q
from urllib.parse import urlencode, parse_qs
from urllib.parse import quote
from datetime import datetime
import hashlib
import uuid


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
    response_save_template = dict()
    try:
        submit = models.Submit.objects.get(eiud=request.GET.get('study_uid'))
        plantilla = models.Plantilla.objects.get(id=submit.plantilla.id)
        firmas = models.Firma.objects.filter(informe=submit)
        if firmas.count() == plantilla.cantidadfirmas:
            response_save_template = {'url_editor': submit.urlparamsenviado,
                                      'url_autentication': request.build_absolute_uri(reverse('authenticate_report')) + '?report={}'.format(submit.id)}
        else:
            response_save_template = {'url_editor': submit.urlparamsenviado, 'url_autentication': ''}
    except models.Submit.DoesNotExist:
        response_save_template = {'error': 'Report not save'}
    return JsonResponse(response_save_template)


def save_template(request, *args, **kwargs):
    post_param = request.POST.dict()
    response_save = dict()
    if 'csrfmiddlewaretoken' in post_param:
        del post_param['csrfmiddlewaretoken']
    if request.POST.get("guardar"):
        if 'usuario' in post_param:
            del post_param['usuario']
        if 'clave' in post_param:
            del post_param['clave']
        if 'guardar' in post_param:
            del post_param['guardar']
        submit, created = models.Submit.objects.update_or_create(
            plantilla=models.Plantilla.objects.get(id=request.POST.get('plantilla')),
            eiud=request.POST.get('StudyIUID'),
            eaccnum=request.POST.get('AccessionNumber'),
            eaccoid=request.POST.get('accessionNumberOID'),
        )
        submit.listoparaautenticacion = 'NO'
        submit.urlparamsenviado = request.build_absolute_uri(reverse('editor')) + '?' + \
                                  urlencode(post_param, quote_via=quote)
        submit.urlparamsrecibido = urlencode(post_param, quote_via=quote)
        submit.save()

        firmas = models.Firma.objects.filter(informe=submit)
        if firmas.count() > 0:
            models.Firma.objects.filter(informe=submit).delete()
        response_save = {'message': 'Guardado Correctamente'}
    elif request.POST.get("firmar"):
        username = ''
        password = ''
        if 'usuario' in post_param:
            username = request.POST.get('usuario')
        if 'clave' in post_param:
            password = request.POST.get('clave')
        if username != '' and password != '':
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    if 'usuario' in post_param:
                        del post_param['usuario']
                    if 'clave' in post_param:
                        del post_param['clave']
                    if 'firmar' in post_param:
                        del post_param['firmar']
                    plantilla = models.Plantilla.objects.get(id=request.POST.get('plantilla'))
                    submit, submit_created = models.Submit.objects.update_or_create(
                        plantilla=plantilla,
                        eiud=request.POST.get('StudyIUID'),
                        eaccnum=request.POST.get('AccessionNumber'),
                        eaccoid=request.POST.get('accessionNumberOID'),
                    )
                    submit.urlparamsenviado = request.build_absolute_uri(reverse('editor')) + '?' + \
                                              urlencode(post_param, quote_via=quote)
                    submit.urlparamsrecibido = urlencode(post_param, quote_via=quote)
                    submit.save()

                    firma, firma_created = models.Firma.objects.update_or_create(
                        informe=submit,
                        md5=hashlib.md5(urlencode(post_param, quote_via=quote).encode('utf-8')).hexdigest(),
                        fecha=datetime.now(),
                        udn=user.username,
                        uid='',
                        uoid='',
                        uname=user.get_full_name(),
                        iname='',
                        ioid=request.POST.get('custodianOID')
                    )
                    firmas = models.Firma.objects.filter(informe=submit)
                    if firmas.count() == plantilla.cantidadfirmas:
                        submit.listoparaautenticacion = 'SI'
                    else:
                        submit.listoparaautenticacion = 'NO'
                    submit.save()
                    response_save = {'message': 'Firmado Correctamente'}
                else:
                    response_save = {'error': 'Usuario valido, pero no esta activo'}
            else:
                response_save = {'error': 'Usuario no valido'}
        else:
            response_save = {'error': 'Debe ingresar usuario y contraseña'}

    elif request.POST.get("firmarAutenticar"):
        username = ''
        password = ''
        if 'usuario' in post_param:
            username = request.POST.get('usuario')
        if 'clave' in post_param:
            password = request.POST.get('clave')
        if username != '' and password != '':
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    if 'usuario' in post_param:
                        del post_param['usuario']
                    if 'clave' in post_param:
                        del post_param['clave']
                    if 'firmarAutenticar' in post_param:
                        del post_param['firmarAutenticar']
                    plantilla = models.Plantilla.objects.get(id=request.POST.get('plantilla'))
                    submit, submit_created = models.Submit.objects.update_or_create(
                        plantilla=plantilla,
                        eiud=request.POST.get('StudyIUID'),
                        eaccnum=request.POST.get('AccessionNumber'),
                        eaccoid=request.POST.get('accessionNumberOID'),
                    )
                    submit.urlparamsenviado = request.build_absolute_uri(reverse('editor')) + '?' + \
                                              urlencode(post_param, quote_via=quote)
                    submit.urlparamsrecibido = urlencode(post_param, quote_via=quote)
                    submit.save()

                    firma, firma_created = models.Firma.objects.update_or_create(
                        informe=submit,
                        md5=hashlib.md5(urlencode(post_param, quote_via=quote).encode('utf-8')).hexdigest(),
                        fecha=datetime.now(),
                        udn=user.username,
                        uid='',
                        uoid='',
                        uname=user.get_full_name(),
                        iname='',
                        ioid=request.POST.get('custodianOID')
                    )
                    firmas = models.Firma.objects.filter(informe=submit)
                    if firmas.count() == plantilla.cantidadfirmas:
                        submit.listoparaautenticacion = 'SI'
                    else:
                        submit.listoparaautenticacion = 'NO'
                    submit.save()
                    # llamar funcion autenticación
                    response_save = {'message': 'Firmado Correctamente'}
                else:
                    response_save = {'error': 'Usuario valido, pero no esta activo'}
            else:
                response_save = {'error': 'Usuario no valido'}
        else:
            response_save = {'error': 'Debe ingresar usuario y contraseña'}
    elif request.POST.get("borrarPlantilla"):
        print('borrarPlantilla')
    elif request.POST.get("crearPlantilla"):
        print('crearPlantilla')
    return JsonResponse(response_save)


def generate_authenticate_report(request, *args, **kwargs):
    submit = models.Submit.objects.get(id=request.GET.get('report'))
    authenticate_report(submit, request.user)
    return HttpResponse('autenticado ok')


def authenticate_report(submit, user):
    # registra datos tabla autenticado
    informeuid = '2.25.{}'.format(int(str(uuid.uuid4()).replace('-', ''), 16))
    values_submit = parse_qs(submit.urlparamsrecibido)
    autenticado = models.Autenticado.objects.create(
        plantilla=submit.plantilla,
        eiud=submit.eiud,
        eaccnum=submit.eaccnum,
        eaccoid=submit.eaccoid,
        urlparams=submit.urlparamsrecibido,
        activo='SI',
        pnombre=values_submit['PatientName'][0],
        pid=values_submit['PatientID'][0],
        poid=values_submit['PatientIDIssuer'][0],
        psexo=values_submit['PatientSex'][0],
        pnacimiento=values_submit['PatientBirthDate'][0],
        pbarrio='',
        pciudad='',
        pregion='',
        ppais='',
        efecha=datetime.strptime(values_submit['StudyDate'][0],'%Y%m%d'),
        eid='',
        erealizadoroid='',
        estudio=submit.plantilla.estudio,
        informetitulo='',
        informeuid=informeuid,
        custodianoid=values_submit['custodianOID'][0],
        valoracion='',
        solicituduid=''
    )
    # parseo submit
    secciones = models.Seccion.objects.filter(plantilla=submit.plantilla)
    print(secciones.query)
    for seccion in secciones:
        sec = models.Sec.objects.create(
            autenticado=autenticado,
            templateuid=seccion.templateuidroot,
            idsec=seccion.idseccion,
            seccode=seccion.code,
            title=seccion.selecttitle
        )
        if seccion.articlehtml is not None:
            sec.text = values_submit['{}textarea'.format(seccion.idseccion)][0]
            sec.save()
        else:
            subsecciones = seccion.get_all_sub_seccion()
            for subseccion in subsecciones:
                subsec = models.Subsec.objects.create(
                    templateuid=subseccion.templateuidroot,
                    idsubsec=subseccion.idseccion,
                    subseccode=subseccion.code,
                    title=subseccion.selecttitle,
                    parent_sec=sec.id
                )
                if subseccion.articlehtml is not None:
                    subsec.text = values_submit['{}textarea'.format(subseccion.idseccion)][0]
                    subsec.save()
                else:
                    subsubsecciones = subseccion.get_all_sub_seccion()
                    for subsubseccion in subsubsecciones:
                        subsubsec = models.Subsubsec.objects.create(
                            templateuid=subsubseccion.templateuidroot,
                            idsubsubsec=subsubseccion.idseccion,
                            subsubseccode=subsubseccion.code,
                            title=subsubseccion.selecttitle,
                            parent_subsec=subsec.id,
                            text = values_submit['{}textarea'.format(subsubsecciones.idseccion)][0]
                        )
    return
