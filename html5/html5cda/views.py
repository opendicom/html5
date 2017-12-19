from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from django.core.urlresolvers import reverse
from html5cda import models
from html5dicom.models import Institution
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
        if submit.listoparaautenticacion == 'SI':
            response_save_template = {'url_editor': request.build_absolute_uri(reverse('editor')) + '?' +
                                                    submit.urlparamsrecibido,
                                      'url_autentication': request.build_absolute_uri(reverse('authenticate_report')) +
                                                           '?report={}'.format(submit.id)}
        else:
            response_save_template = {'url_editor': request.build_absolute_uri(reverse('editor')) + '?' +
                                                    submit.urlparamsrecibido,
                                      'url_autentication': ''}
    except models.Submit.DoesNotExist:
        response_save_template = {'error': 'Report not save'}
    return JsonResponse(response_save_template)


def save_template(request, *args, **kwargs):
    post_param = request.POST.dict()
    response_save = dict()
    if 'csrfmiddlewaretoken' in post_param:
        del post_param['csrfmiddlewaretoken']
    if request.POST.get("guardar"):
        if saveTemplate(request, post_param) is True:
            response_save = {'message': 'Guardado Correctamente'}
        else:
            response_save = {'error': 'No fue posible realizar la operacion'}
    elif request.POST.get("firmar") or request.POST.get("firmarAutenticar"):
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
                    if saveTemplate(request, post_param) is True:
                        if signTemplate(request, post_param, user) is True:
                            if request.POST.get("firmarAutenticar"):
                                submit = models.Submit.objects.get(eiud=request.POST.get('StudyIUID'))
                                authenticate_report(submit, user)
                                response_save = {'message': 'Autenticado Correctamente'}
                            else:
                                response_save = {'message': 'Firmado Correctamente'}
                        else:
                            response_save = {'error': 'No fue posible realizar la operacion'}
                    else:
                        response_save = {'error': 'No fue posible realizar la operacion'}
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


def saveTemplate(request, post_param):
    if 'usuario' in post_param:
        del post_param['usuario']
    if 'clave' in post_param:
        del post_param['clave']
    if 'guardar' in post_param:
        del post_param['guardar']
    if 'firmar' in post_param:
        del post_param['firmar']

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
    return True


def signTemplate(request, post_param, user):
    institution = Institution.objects.get(oid=request.POST.get('custodianOID'))
    submit = models.Submit.objects.get(eiud=request.POST.get('StudyIUID'))
    firma, firma_created = models.Firma.objects.update_or_create(
        informe=submit,
        md5=hashlib.md5(urlencode(post_param, quote_via=quote).encode('utf-8')).hexdigest(),
        fecha=datetime.now(),
        user=user,
        iname=institution.name,
        ioid=institution.oid
    )
    firmas = models.Firma.objects.filter(informe=submit)
    plantilla = models.Plantilla.objects.get(id=request.POST.get('plantilla'))
    if firmas.count() == plantilla.cantidadfirmas:
        submit.listoparaautenticacion = 'SI'
    else:
        submit.listoparaautenticacion = 'NO'
    submit.save()
    return True


def generate_authenticate_report(request, *args, **kwargs):
    submit = models.Submit.objects.get(id=request.GET.get('report'))
    xml_cda = authenticate_report(submit, request.user)
    return HttpResponse(xml_cda)


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
        efecha=datetime.strptime(values_submit['StudyDate'][0], '%Y%m%d'),
        eid='',
        erealizadoroid='',
        estudio=submit.plantilla.estudio,
        informetitulo='',
        informeuid=informeuid,
        custodianoid=values_submit['custodianOID'][0],
        valoracion='',
        solicituduid=''
    )
    xml_cda = '<?xml version="1.0" encoding="UTF-8"?>'
    xml_cda += '<ClinicalDocument xmlns="urn:hl7-org:v3">'
    xml_cda += '<realmCode code="UY"/>'
    xml_cda += '<typeId extension="POCD_HD000040" root="2.16.840.1.113883.1.3"/>'
    xml_cda += '<templateId root="{}"/>'.format(submit.plantilla.identifier)
    xml_cda += '<id root="{}"/>'.format(values_submit['StudyIUID'][0])

    xml_cda += '<code code="18748-4" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC" ' \
               'displayName="Diagnóstico imagenológico"/>'
    xml_cda += '<title>{}</title>'.format(values_submit['StudyDescription'][0])

    xml_cda += '<effectiveTime value="{}"/>'.format(datetime.now().strftime("%Y%m%d%H%M%S"))
    xml_cda += '<confidentialityCode code="N" codeSystem="2.16.840.1.113883.5.25" codeSystemName="HL7" ' \
               'displayName="normal"/>'
    xml_cda += '<languageCode code="{}"/>'.format(submit.plantilla.language)
    xml_cda += '<recordTarget>{}</recordTarget>'.format(autenticado.get_patientRole())
    signatures = models.Firma.objects.filter(informe=submit)
    for signature in signatures:
        xml_cda += signature.get_cda_format()
    institution = Institution.objects.get(oid=values_submit['custodianOID'][0])
    xml_cda += '<custodian><assignedCustodian><representedCustodianOrganization>'
    xml_cda += '<id root="{}"/>'.format(institution.oid)
    xml_cda += '<name>{}</name>'.format(institution.name)
    xml_cda += '</representedCustodianOrganization></assignedCustodian></custodian>'
    xml_cda += '<informationRecipient>'
    xml_cda += '<intendedRecipient classCode="ASSIGNED">'
    xml_cda += '<informationRecipient>'
    xml_cda += '<name>{}</name>'.format(institution.name)
    xml_cda += '</informationRecipient>'
    xml_cda += '</intendedRecipient>'
    xml_cda += '</informationRecipient>'
    xml_cda += '<inFulfillmentOf><order>'
    xml_cda += '<id root="{}" extension="{}"/>'.format(values_submit['accessionNumberOID'][0],
                                                       values_submit['AccessionNumber'][0])
    xml_cda += '</order></inFulfillmentOf>'
    xml_cda += '<documentationOf>'
    xml_cda += '<serviceEvent>'
    xml_cda += '<id root="{}"/>'.format(values_submit['StudyIUID'][0])
    xml_cda += '<code code="{}" codeSystem="{}"'.format(submit.plantilla.estudio.code.code,
                                                        submit.plantilla.estudio.code.codesystem.shortname)
    xml_cda += ' displayName="{}">'.format(submit.plantilla.estudio.code.displayname)
    xml_cda += '<translation code="{}" displayName=""/>'.format(submit.plantilla.estudio.modalidad)
    xml_cda += '</code>'
    xml_cda += '<effectiveTime>'
    xml_cda += '<low value="{}"/>'.format(values_submit['StudyDate'][0])
    xml_cda += '</effectiveTime>'
    xml_cda += '</serviceEvent>'
    xml_cda += '</documentationOf>'

    xml_cda += '<componentOf>'
    xml_cda += '<encompassingEncounter>'
    xml_cda += '<effectiveTime value="{}"/>'.format(values_submit['StudyDate'][0])
    xml_cda += '<encounterParticipant typeCode="ATND">'
    xml_cda += '<assignedEntity>'
    xml_cda += '<id extension="{}" root="{}"/>'.format(institution.name, institution.oid)
    xml_cda += '</assignedEntity>'
    xml_cda += '</encounterParticipant>'
    xml_cda += '</encompassingEncounter>'
    xml_cda += '</componentOf>'
    # parseo submit
    xml_cda += '<component><structuredBody>'
    sections = models.Section.objects.filter(plantilla=submit.plantilla)
    for section in sections:
        if values_submit['{}select'.format(section.idattribute)][0] != 'off':
            xml_cda += '<component><templateId root="{}"/>'.format(submit.plantilla.identifier)
            xml_cda += '<section>'
            xml_cda += '<templateId root="1.2.840.10008.9.2"/>'
            xml_cda += '<code codeSystem="{}" codeSystemName="{}"'.format(section.conceptcode.codesystem.oid,
                                                                          section.conceptcode.codesystem.shortname)
            xml_cda += ' code="{}" displayName="{}"/>'.format(section.conceptcode.code, section.conceptcode.displayname)
            xml_cda += '<title>{}</title>'.format(section.selecttitle)
            sec = models.Sec.objects.create(
                autenticado=autenticado,
                idsec=section.idattribute,
                seccode=section.conceptcode,
                title=section.selecttitle
            )
            if section.article is not None:
                if section.check_article_xhtml5 is not None:
                    text_section, entries_section = generate_text_observation(section, values_submit, sec=sec)
                    sec.text = text_section
                    xml_cda += text_section
                    xml_cda += entries_section
                    sec.save()
            else:
                subsections = section.get_all_sub_seccion()
                for subsection in subsections:
                    if values_submit['{}select'.format(subsection[0].idattribute)][0] != 'off':
                        xml_cda += '<component><templateId root="1.3.6.1.4.1.23650.7284777653.8482.1"/>'
                        xml_cda += '<section>'
                        xml_cda += '<templateId root="1.2.840.10008.9.2"/>'
                        xml_cda += '<code codeSystem="{}" codeSystemName="{}"'.format(
                            subsection[0].conceptcode.codesystem.oid,
                            subsection[0].conceptcode.codesystem.shortname)
                        xml_cda += ' code="{}" displayName="{}"/>'.format(subsection[0].conceptcode.code,
                                                                          subsection[0].conceptcode.displayname)
                        xml_cda += '<title>{}</title>'.format(subsection[0].selecttitle)
                        subsec = models.Subsec.objects.create(
                            idsubsec=subsection[0].idattribute,
                            subseccode=subsection[0].conceptcode,
                            title=subsection[0].selecttitle,
                            parent_sec=sec
                        )
                        if subsection[0].article is not None:
                            if subsection[0].article.check_xhtml5 is not None:
                                text_section, entries_section = generate_text_observation(subsection[0],
                                                                                          values_submit,
                                                                                          subsec=subsec)
                                subsec.text = text_section
                                xml_cda += text_section
                                xml_cda += entries_section
                                subsec.save()
                        else:
                            subsubsections = subsection[0].get_all_sub_seccion()
                            for subsubsection in subsubsections:
                                if values_submit['{}select'.format(subsubsection[0].idattribute)][0] != 'off':
                                    xml_cda += '<component><templateId root="1.3.6.1.4.1.23650.7284777653.8482.1"/>'
                                    xml_cda += '<section>'
                                    xml_cda += '<templateId root="1.2.840.10008.9.2"/>'
                                    xml_cda += '<code codeSystem="{}" codeSystemName="{}"'.format(
                                        subsubsection[0].conceptcode.codesystem.oid,
                                        subsubsection[0].conceptcode.codesystem.shortname)
                                    xml_cda += ' code="{}"'.format(subsubsection[0].conceptcode.code)
                                    xml_cda += ' displayName="{}"/>'.format(subsubsection[0].conceptcode.displayname)
                                    xml_cda += '<title>{}</title>'.format(subsubsection[0].selecttitle)
                                    subsubsec = models.Subsubsec.objects.create(
                                        idsubsubsec=subsubsection[0].idattribute,
                                        subsubseccode=subsubsection[0].conceptcode,
                                        title=subsubsection[0].selecttitle,
                                        parent_subsec=subsec
                                    )
                                    if subsubsection[0].article is not None:
                                        if subsubsection[0].article.check_xhtml5 is not None:
                                            text_section, entries_section = generate_text_observation(subsubsection[0],
                                                                                                      values_submit,
                                                                                                      subsubsec=subsubsec)
                                            subsubsec.text = text_section
                                            xml_cda += text_section
                                            xml_cda += entries_section
                                            subsubsec.save()
                                xml_cda += '</section></component>'
                        xml_cda += '</section></component>'
            xml_cda += '</section></component>'
    xml_cda += '</structuredBody></component>'
    xml_cda += '</ClinicalDocument>'
    submit.listoparaautenticacion = 'NO'
    submit.save()
    models.Firma.objects.filter(informe=submit).delete()
    return xml_cda


def generate_text_observation(section, values_submit, sec=None, subsec=None, subsubsec=None):
    text_cda = '<text>'
    entries_cda = ''
    textareas = re.findall("<textarea name='(.+?)'>", section.article.xhtml5)
    for textarea in textareas:
        textarea_value = values_submit['{}'.format(textarea)][0]
        str_replace = re.compile('<p>')
        textarea_value = str_replace.sub('<paragraph>', textarea_value)
        str_replace = re.compile('</p>')
        textarea_value = str_replace.sub('</paragraph>', textarea_value)
        str_replace = re.compile('<strong>')
        textarea_value = str_replace.sub('<content styleCode="Bold">', textarea_value)
        str_replace = re.compile('</strong>')
        textarea_value = str_replace.sub('</content>', textarea_value)
        str_replace = re.compile('<em>')
        textarea_value = str_replace.sub('<content styleCode="Italics">', textarea_value)
        str_replace = re.compile('</em>')
        textarea_value = str_replace.sub('</content>', textarea_value)
        str_replace = re.compile('<u>')
        textarea_value = str_replace.sub('<content styleCode="Underline">', textarea_value)
        str_replace = re.compile('</u>')
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
            observation.save()
            if label.xsitype == 'CR':
                option_selectd = models.Option.objects.get(id=values_submit['{}.{}'.format(section.idattribute,
                                                                                           label.id)][0])
                observation.option = option_selectd
                observation.save()
                text_cda += label.get_cda_select(observation=observation)
                entries_cda = observation.get_cda_format_select()
            else:
                valueattribute = models.Valueattribute.objects.create(
                    observation=observation,
                    name='value',
                    content=values_submit['{}.{}'.format(section.idattribute, label.id)][0]
                )
                text_cda += label.get_cda_input(input=values_submit['{}.{}'.format(section.idattribute, label.id)][0],
                                                observation=observation)
                entries_cda = observation.get_cda_format_input()
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
                        observation.save()
                        text_cda += col.label.get_cda_label(observation=observation)
                    elif col.code1 is not None:
                        observation.code1 = col.code1
                        observation.save()
                        text_cda += col.code1.get_cda_format(observation=observation)
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
                    try:
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
                                        option_selectd = models.Option.objects.get(id=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0])
                                        observation.option = option_selectd
                                        observation.save()
                                        text_cda += cell.label.get_cda_select(observation=observation, caption=False)
                                        entries_cda += observation.get_cda_format_select()
                                    else:
                                        valueattribute = models.Valueattribute.objects.create(
                                            observation=observation,
                                            name='value',
                                            content=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0]
                                        )
                                        text_cda += cell.label.get_cda_input(
                                            input=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0],
                                            observation=observation,
                                            caption=False)
                                        entries_cda += observation.get_cda_format_input()
                                else:
                                    if cell.label.xsitype == 'CR':
                                        option_selectd = models.Option.objects.get(id=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0])
                                        observation.option = option_selectd
                                        observation.save()
                                        text_cda += cell.label.get_cda_select(observation=observation)
                                        entries_cda += observation.get_cda_format_select()
                                    else:
                                        valueattribute = models.Valueattribute.objects.create(
                                            observation=observation,
                                            name='value',
                                            content=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0]
                                        )
                                        text_cda += cell.label.get_cda_input(
                                            input=values_submit['{}.{}'.format(section.idattribute, cell.label.id)][0],
                                            observation=observation)
                                        entries_cda += observation.get_cda_format_input()
                            elif cell.code1 is not None:
                                observation.code1 = cell.code1
                                observation.save()
                                text_cda += cell.code1.get_cda_format(observation=observation)
                                entries_cda += observation.get_cda_fomat_code1()
                    except models.Cell.DoesNotExist:
                        print('Missing cell config')
                    text_cda += '</td>'
                text_cda += '</tr>'
            text_cda += '</tbody></table>'
    text_cda += '</text>'
    return text_cda, entries_cda
