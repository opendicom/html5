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
import re


@login_required(login_url='/html5dicom/login')
def editor(request, *args, **kwargs):
    modality_filter = ''
    if 'modalidad' in request.GET:
        modality_filter = request.GET['modalidad']
    else:
        modality_filter = request.GET['Modality']
    html = ''
    modalidades = models.Estudio.objects.values('modalidad').annotate(Count('modalidad')) \
        .order_by('modalidad')
    studies_list = []
    for estudio in models.Estudio.objects.filter(modalidad=modality_filter):
        studies_list += [{
            'id': estudio.id,
            'description': estudio.code.displayname
        }]
    template_list = []
    for plantilla in models.Plantilla.objects.filter(
                    Q(estudio__modalidad=modality_filter) | Q(estudio__modalidad='ALL')):
        template_list += [{
            'id': plantilla.id,
            'description': plantilla.title
        }]
    if 'plantilla' in request.GET:
        # edicion de informe
        secciones = models.Section.objects.filter(plantilla=request.GET['plantilla']).order_by('ordinal')
        headscripts = models.IntermediateHeadScript.objects.filter(plantilla=request.GET['plantilla'])
        bodyscripts = models.IntermediateBodyScript.objects.filter(plantilla=request.GET['plantilla'])
        headers = models.IntermediatePlantillaHeader.objects.filter(plantilla=request.GET['plantilla'])
        footers = models.IntermediatePlantillaFooter.objects.filter(plantilla=request.GET['plantilla'])
        context_user = {'context': {'sections': secciones,
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
        secciones = models.Section.objects.filter(plantilla=plantilla).order_by('ordinal')
        headscripts = models.IntermediateHeadScript.objects.filter(plantilla=plantilla)
        bodyscripts = models.IntermediateBodyScript.objects.filter(plantilla=plantilla)
        headers = models.IntermediatePlantillaHeader.objects.filter(plantilla=plantilla)
        footers = models.IntermediatePlantillaFooter.objects.filter(plantilla=plantilla)
        context_user = {'context': {'sections': secciones,
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
    secciones = models.Section.objects.filter(plantilla=request.GET['template']).order_by('ordinal')
    headscripts = models.IntermediateHeadScript.objects.filter(plantilla=request.GET['template'])
    bodyscripts = models.IntermediateBodyScript.objects.filter(plantilla=request.GET['template'])
    headers = models.IntermediatePlantillaHeader.objects.filter(plantilla=request.GET['template'])
    footers = models.IntermediatePlantillaFooter.objects.filter(plantilla=request.GET['template'])
    context_user = {'context': {'sections': secciones,
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
            eiud=request.POST.get('StudyIUID')
        )
        submit.plantilla = models.Plantilla.objects.get(id=request.POST.get('plantilla'))
        submit.eaccnum = request.POST.get('AccessionNumber')
        submit.eaccoid = request.POST.get('accessionNumberOID')
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
                        eiud=request.POST.get('StudyIUID')
                    )
                    submit.plantilla = plantilla
                    submit.eaccnum = request.POST.get('AccessionNumber')
                    submit.eaccoid = request.POST.get('accessionNumberOID')
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
                        eiud=request.POST.get('StudyIUID'),
                    )
                    submit.plantilla = plantilla
                    submit.eaccnum = request.POST.get('AccessionNumber')
                    submit.eaccoid = request.POST.get('accessionNumberOID')
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
    sections = models.Section.objects.filter(plantilla=submit.plantilla)
    for section in sections:
        if values_submit['{}select'.format(section.idattribute)][0] != 'off':
            sec = models.Sec.objects.create(
                autenticado=autenticado,
                idsec=section.idattribute,
                seccode=section.conceptcode,
                title=section.selecttitle
            )
            if section.article is not None:
                if section.check_article_xhtml5 is not None:
                    sec.text = generate_text_observation(section, values_submit, sec=sec)
                    sec.save()
            else:
                subsections = section.get_all_sub_seccion()
                for subsection in subsections:
                    print(subsection[0])
                    print('subsection {} {}'.format(subsection[0].id, subsection[0].idattribute))
                    subsec = models.Subsec.objects.create(
                        idsubsec=subsection[0].idattribute,
                        subseccode=subsection[0].conceptcode,
                        title=subsection[0].selecttitle,
                        parent_sec=sec
                    )
                    if subsection[0].article is not None:
                        if subsection[0].article.check_xhtml5 is not None:
                            subsec.text = generate_text_observation(subsection[0], values_submit, subsec=subsec)
                            subsec.save()
                    else:
                        subsubsections = subsection[0].get_all_sub_seccion()
                        for subsubsection in subsubsections:
                            subsubsec = models.Subsubsec.objects.create(
                                idsubsubsec=subsubsection[0].idattribute,
                                subsubseccode=subsubsection[0].conceptcode,
                                title=subsubsection[0].selecttitle,
                                parent_subsec=subsec
                            )
                            if subsubsection[0].article is not None:
                                if subsubsection[0].article.check_xhtml5 is not None:
                                    subsubsec.text = generate_text_observation(subsubsection[0], values_submit, subsubsec=subsubsec)
                                    subsubsec.save()
    return


def generate_text_observation(section, values_submit, sec=None, subsec=None, subsubsec=None):
    text_cda = '<text>'
    textareas = re.findall("<textarea name='(.+?)'>", section.article.xhtml5)
    for textarea in textareas:
        textarea_value = values_submit['{}'.format(textarea)][0]
        str_replace = re.compile('%3Cp%3E')
        textarea_value = str_replace.sub('<paragraph>', textarea_value)
        str_replace = re.compile('%3C%2Fp%3E')
        textarea_value = str_replace.sub('</paragraph>', textarea_value)
        str_replace = re.compile('%3Cstrong%3E')
        textarea_value = str_replace.sub('<content styleCode="Bold">', textarea_value)
        str_replace = re.compile('%3C%2Fstrong%3E')
        textarea_value = str_replace.sub('</content>', textarea_value)
        str_replace = re.compile('%3Cem%3E')
        textarea_value = str_replace.sub('<content styleCode="Italics">', textarea_value)
        str_replace = re.compile('%3C%2Fem%3E')
        textarea_value = str_replace.sub('</content>', textarea_value)
        str_replace = re.compile('%3Cu%3E')
        textarea_value = str_replace.sub('<content styleCode="Underline">', textarea_value)
        str_replace = re.compile('%3C%2Fu%3E')
        textarea_value = str_replace.sub('</content>', textarea_value)
        text_cda += textarea_value


    hrefs = re.findall('<a href="(.+?)"/>', section.article.xhtml5)
    for href in hrefs:
        if 'label' in href:
            label = models.Label.objects.get(id=href.split('/')[-1])
            observation = models.Observation.objects.create(label=label)
            if sec is not None:
                observation.sec = sec
            elif subsec is not None:
                observation.subsec = subsec
            elif subsubsec is not None:
                observation.subsubsec = subsubsec
            if label.xsitype == 'CR':
                observation.option = values_submit['{}.{}'.format(section.idattribute, label.id)][0]
                text_cda += label.get_cda_select(option=values_submit['{}.{}'.format(section.idattribute, label.id)][0],
                                                 observation=observation)
            else:
                valueattribute = models.Valueattribute.objects.create(
                    observation=observation,
                    name='value',
                    content=values_submit['{}.{}'.format(section.idattribute, label.id)][0]
                )
                text_cda += label.get_cda_input(input=values_submit['{}.{}'.format(section.idattribute, label.id)][0],
                                                observation=observation)
            observation.save()
        elif 'table' in href:
            table = models.Table.objects.get(id=href.split('/')[-1])
            cols = models.Col.objects.filter(table=table).order_by('number')
            text_cda += '<table><thead><tr><th></th>'
            for col in cols:
                text_cda += '<td>'
                if col.label is None and col.code1 is None:
                    text_cda += col.get_content_cda()
                else:
                    observation = models.Observation.objects.create(table=table, col=col)
                    if sec is not None:
                        observation.sec = sec
                    elif subsec is not None:
                        observation.subsec = subsec
                    elif subsubsec is not None:
                        observation.subsubsec = subsubsec

                    if col.label is not None:
                        observation.label = col.label
                        text_cda += col.label.get_cda_label(observation=observation)
                    elif col.code1 is not None:
                        observation.code1 = col.code1
                        text_cda += col.code1.get_cda_format(observation=observation)
                    observation.save()
                text_cda += '</td>'
            text_cda += '</tr></thead><tbody>'
            rows = models.Row.objects.filter(table=table).order_by('number')
            for row in rows:
                text_cda += '<tr><th>'
                if row.label is None and row.code1 is None:
                    text_cda += row.get_content_cda()
                else:
                    observation = models.Observation.objects.create(table=table, row=row)
                    if sec is not None:
                        observation.sec = sec
                    elif subsec is not None:
                        observation.subsec = subsec
                    elif subsubsec is not None:
                        observation.subsubsec = subsubsec

                    if row.label is not None:
                        observation.label = row.label
                        text_cda += row.label.get_cda_label(observation=observation)
                    elif row.code1 is not None:
                        observation.code1 = row.code1
                        text_cda += row.code1.get_cda_format(observation=observation)
                    observation.save()
                text_cda += '</th>'
                for col in cols:
                    text_cda += '<td>'
                    #try:
                    cell = models.Cell.objects.get(row=row, col=col)
                    if cell.label is None and cell.code1 is None:
                        text_cda += cell.get_content_cda()
                    else:
                        observation = models.Observation.objects.create(table=table, row=row, col=col)
                        if sec is not None:
                            observation.sec = sec
                        elif subsec is not None:
                            observation.subsec = subsec
                        elif subsubsec is not None:
                            observation.subsubsec = subsubsec

                        if cell.label is not None:
                            observation.label = cell.label
                            observation.save()
                            if row.label is not None or col.label is not None:
                                if cell.label.xsitype == 'CR':
                                    text_cda += cell.label.get_cda_select(
                                        option=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0],
                                        observation=observation,
                                        caption=False)
                                else:
                                    text_cda += cell.label.get_cda_input(
                                        input=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0],
                                        observation=observation,
                                        caption=False)
                            else:
                                if cell.label.xsitype == 'CR':
                                    text_cda += cell.label.get_cda_select(
                                        option=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0],
                                        observation=observation)
                                else:
                                    text_cda += cell.label.get_cda_input(
                                        input=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0],
                                        observation=observation)
                        elif cell.code1 is not None:
                            observation.code1 = cell.code1
                            observation.save()
                            text_cda += cell.code1.get_cda_format(observation=observation)
                    #except:
                    #    print('Missing cell config')
                    text_cda += '</td>'
                text_cda += '</tr>'
            text_cda += '</tbody></table>'
    text_cda += '</text>'
    return text_cda
