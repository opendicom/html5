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
import base64
import requests
from django.contrib.auth.models import User


@login_required(login_url='/html5dicom/login')
def editor(request, *args, **kwargs):
    modality_filter = ''
    estudio_filter = ''
    if 'modalidad' in request.GET:
        modality_filter = request.GET['modalidad']
    else:
        modality_filter = request.GET['Modality']
    if 'estudio' in request.GET:
        estudio_filter = request.GET['estudio']
    else:
        estudio_filter = 0
    html = ''
    modalidades = models.Estudio.objects.values('modalidad').annotate(Count('modalidad')) \
        .order_by('modalidad')
    studies_list = []
    for estudio in models.Estudio.objects.filter(modalidad=modality_filter):
        if estudio_filter == 0 and estudio.code.displayname == request.GET['StudyDescription']:
            estudio_filter = estudio.id
        studies_list += [{
            'id': estudio.id,
            'description': estudio.code.displayname
        }]
    if estudio_filter == 0 and len(studies_list) > 0:
        estudio_filter = studies_list[0]['id']
    template_list = []
    plantillas = models.Plantilla.objects.filter(Q(estudio=estudio_filter) | Q(estudio=None))
    for p in plantillas:
        template_list += [{
            'plantilla_id': '{}.-'.format(p.id),
            'template_id': '',
            'description': p.title
        }]

    template = models.Template.objects.filter(estudio=estudio_filter, user=request.user)
    if len(template) > 0:
        for t in template:
            template_list += [{
                'plantilla_id': '{}.{}'.format(t.plantilla_id, t.id),
                'template_id': t.id,
                'description': t.titulo
            }]
    signature_list = []
    try:
        submit = models.Submit.objects.get(eiud=request.GET.get('StudyIUID'))
        if submit.listoparaautenticacion == 'SI':
            signatures = models.Firma.objects.filter(informe_id=submit.id)
            count_signature = 1
            for signature in signatures:
                signature_list += [{
                    'count_signature': count_signature,
                    'date_signature': signature.fecha,
                    'user_signature': signature.user.get_full_name
                }]
                count_signature = count_signature + 1
    except models.Submit.DoesNotExist:
        signature_list = []

    if 'plantilla' in request.GET:
        # edicion de informe
        plantilla, template = request.GET['plantilla'].split('.')
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
    else:
        # nuevo informe
        try:
            plantilla = models.Plantilla.objects.get(estudio__modalidad=request.GET['Modality'],
                                                     estudio__code__displayname=request.GET['StudyDescription'])
        except models.Plantilla.DoesNotExist:
            plantilla = models.Plantilla.objects.get(estudio=None, title='Texto Libre')
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
                                'signature_list': signature_list,
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
    plantillas = models.Plantilla.objects.filter(Q(estudio=request.GET['estudio']) | Q(estudio=None))
    for p in plantillas:
        template_list += [{
            'plantilla_id': '{}.-'.format(p.id),
            'template_id': '',
            'description': p.title
        }]
    template = models.Template.objects.filter(estudio=request.GET['estudio'], user=request.user)
    if len(template) > 0:
        for t in template:
            template_list += [{
                'plantilla_id': '{}.{}'.format(t.plantilla_id, t.id),
                'template_id': t.id,
                'description': t.titulo
            }]
    data = {"template_list": template_list}
    return JsonResponse(data)


def get_template(request, *args, **kwargs):
    plantilla_id, template_id = request.GET['template'].split('.')
    secciones = models.Section.objects.filter(plantilla=plantilla_id).order_by('ordinal')
    headscripts = models.IntermediateHeadScript.objects.filter(plantilla=plantilla_id)
    bodyscripts = models.IntermediateBodyScript.objects.filter(plantilla=plantilla_id)
    headers = models.IntermediatePlantillaHeader.objects.filter(plantilla=plantilla_id)
    footers = models.IntermediatePlantillaFooter.objects.filter(plantilla=plantilla_id)
    if template_id == '-':
        template = None
    else:
        template = models.Template.objects.filter(id=template_id)
    context_user = {'context': {'sections': secciones,
                                'headscripts': headscripts,
                                'bodyscripts': bodyscripts,
                                'headers': headers,
                                'footers': footers,
                                'template': template
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


def save_template_user(request, *args, **kwargs):
    post_param = request.POST.dict()
    # Clean post_param
    if 'csrfmiddlewaretoken' in post_param:
        del post_param['csrfmiddlewaretoken']
    if 'PatientIDIssuer' in post_param:
        del post_param['PatientIDIssuer']
    if 'PatientID' in post_param:
        del post_param['PatientID']
    if 'PatientBirthDate' in post_param:
        del post_param['PatientBirthDate']
    if 'PatientSex' in post_param:
        del post_param['PatientSex']
    if 'PatientName' in post_param:
        del post_param['PatientName']
    if 'StudyIUID' in post_param:
        del post_param['StudyIUID']
    if 'accessionNumberOID' in post_param:
        del post_param['accessionNumberOID']
    if 'custodianOID' in post_param:
        del post_param['custodianOID']
    if 'AccessionNumber' in post_param:
        del post_param['AccessionNumber']
    if 'StudyDate' in post_param:
        del post_param['StudyDate']
    if 'Modality' in post_param:
        del post_param['Modality']
    if 'StudyDescription' in post_param:
        del post_param['StudyDescription']
    if 'templateID' in post_param:
        del post_param['templateID']
    if 'modalidad' in post_param:
        del post_param['modalidad']
    if 'estudio' in post_param:
        del post_param['estudio']
    if 'title' in post_param:
        del post_param['title']
    if 'plantilla' in post_param:
        del post_param['plantilla']

    plantilla, template = request.POST.get('plantilla').split('.')
    template, template_created = models.Template.objects.update_or_create(
        modalidad=request.POST.get('modalidad'),
        estudio_id=request.POST.get('estudio'),
        plantilla=models.Plantilla.objects.get(id=plantilla),
        user=request.user,
        titulo=request.POST.get('title')
    )
    template.urlparams = urlencode(post_param, quote_via=quote)
    template.save()
    response_save = dict()
    response_save = {'message': 'Guardado correctamente'}
    return JsonResponse(response_save)


def delete_template_user(request, *args, **kwargs):
    print('delete template id {}'.format(request.POST.get('template')))
    models.Template.objects.filter(id=request.POST.get('template')).delete()
    response_save = dict()
    response_save = {'message': 'Borrado correctamente'}
    return JsonResponse(response_save)


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
                        sign, listoautenticacion = signTemplate(request, post_param, user)
                        if sign is True:
                            if request.POST.get("firmarAutenticar"):
                                if listoautenticacion == 'SI':
                                    submit = models.Submit.objects.get(eiud=request.POST.get('StudyIUID'))
                                    xml_cda = authenticate_report(submit, user)
                                    response_save = {'message': 'Autenticado Correctamente', 'xml': base64.b64encode(bytes(xml_cda, 'utf-8')).decode("utf-8")}
                                else:
                                    response_save = {'error': 'Firmado Correctamente, faltan firmas para poder realizar autenticacion!'}
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
    plantilla, template = request.POST.get('plantilla').split('.')
    submit.plantilla = models.Plantilla.objects.get(id=plantilla)
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
    plantilla, template = request.POST.get('plantilla').split('.')
    plantilla = models.Plantilla.objects.get(id=plantilla)
    if firmas.count() == plantilla.cantidadfirmas:
        submit.listoparaautenticacion = 'SI'
    else:
        submit.listoparaautenticacion = 'NO'
    submit.save()
    return True, submit.listoparaautenticacion


def generate_authenticate_report(request, *args, **kwargs):
    submit = models.Submit.objects.get(id=request.GET.get('report'))
    xml_cda = authenticate_report(submit, request.user)
    return HttpResponse(xml_cda, content_type='text/xml')


def authenticate_report(submit, user):
    # registra datos tabla autenticado
    informeuid = '2.25.{}'.format(int(str(uuid.uuid4()).replace('-', ''), 16))
    values_submit = parse_qs(submit.urlparamsrecibido)
    if 'estudio' in values_submit:
        estudio = models.Estudio.objects.get(id=values_submit['estudio'][0])

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
        estudio=estudio,
        informetitulo='',
        informeuid=informeuid,
        custodianoid=values_submit['custodianOID'][0],
        valoracion='',
        solicituduid=''
    )
    xml_cda = '<ClinicalDocument xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
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
    xml_cda += '<code code="{}" codeSystem="{}"'.format(estudio.code.code,
                                                        estudio.code.codesystem.shortname)
    xml_cda += ' displayName="{}">'.format(estudio.code.displayname)
    xml_cda += '<translation code="{}" displayName=""/>'.format(estudio.modalidad)
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

    xml_preffix = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="#Transform"?><!DOCTYPE document [<!ATTLIST xsl:stylesheet id ID #REQUIRED>]>'
    xml_preffix += '<dscd'
    xml_preffix += ' xmlns:cda="urn:hl7-org:v3"'
    xml_preffix += ' xmlns:sdtc="urn:hl7-org:sdtc"'
    xml_preffix += ' xmlns:scd="urn:salud.uy/2014/signed-clinical-document"'
    xml_preffix += ' ><SignedClinicalDocument'
    xml_preffix += ' xmlns="urn:salud.uy/2014/signed-clinical-document"'
    xml_preffix += ' >'

    xml_suffix = '</SignedClinicalDocument> '
    xml_suffix += '<xsl:stylesheet '
    xml_suffix += 'id="Transform" '
    xml_suffix += 'version="1.0" '
    xml_suffix += 'xmlns:xsl="http://www.w3.org/1999/XSL/Transform" '
    xml_suffix += 'xmlns:cda="urn:hl7-org:v3" '
    xml_suffix += 'xmlns:scd="urn:salud.uy/2014/signed-clinical-document" '
    xml_suffix += 'xmlns:sdtc="urn:hl7-org:sdtc" '
    xml_suffix += 'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
    xml_suffix += 'xmlns="http://www.w3.org/1999/xhtml" '
    xml_suffix += '> '
    xml_suffix += '<xsl:variable name="cda" select="dscd/scd:SignedClinicalDocument/cda:ClinicalDocument"/> '
    xml_suffix += '<xsl:template match="/"> '
    xml_suffix += '<html> '
    xml_suffix += '<head> '
    xml_suffix += '<title> '
    xml_suffix += '<xsl:value-of select="$cda/cda:title/text()"/> '
    xml_suffix += '</title> '
    xml_suffix += '<style type="text/css"> '
    xml_suffix += 'body { '
    xml_suffix += 'color: #003366; '
    xml_suffix += 'background-color: #FFFFFF; '
    xml_suffix += 'font-family: Verdana, Tahoma, sans-serif; '
    xml_suffix += 'font-size: 13px; '
    xml_suffix += '} '
    xml_suffix += 'pre { '
    xml_suffix += 'font-family: Verdana, Tahoma, '
    xml_suffix += 'sans-serif; '
    xml_suffix += '} '
    xml_suffix += 'h2 { '
    xml_suffix += 'font-size: 17pt; '
    xml_suffix += 'font-weight: bold; '
    xml_suffix += 'text-align: center; '
    xml_suffix += '} '
    xml_suffix += 'h3 { '
    xml_suffix += 'font-size: 14pt; '
    xml_suffix += 'font-weight: bold; '
    xml_suffix += 'margin-bottom: 0; '
    xml_suffix += 'padding-bottom: '
    xml_suffix += '0; '
    xml_suffix += '} '
    xml_suffix += 'table { '
    xml_suffix += 'width: 768px; '
    xml_suffix += '} '
    xml_suffix += 'dt { '
    xml_suffix += 'float: left; '
    xml_suffix += 'clear: left; '
    xml_suffix += 'width: 200px; '
    xml_suffix += 'text-align: left; '
    xml_suffix += 'font-weight: bold; '
    xml_suffix += 'color: green; '
    xml_suffix += '} '
    xml_suffix += 'dt:after '
    xml_suffix += '{ '
    xml_suffix += 'content: ":"; '
    xml_suffix += '} '
    xml_suffix += 'dd { '
    xml_suffix += 'margin: 0 0 0 210px; '
    xml_suffix += 'padding: 0 0 0.5em 0; '
    xml_suffix += '} '
    xml_suffix += 'section '
    xml_suffix += '{ '
    xml_suffix += 'margin: 0 0 0 0; '
    xml_suffix += 'padding: 0 0 0 0; '
    xml_suffix += '} '
    xml_suffix += 'p { '
    xml_suffix += 'margin: 0 0 0 0; '
    xml_suffix += 'padding: 0 0 0 '
    xml_suffix += '0; text-align: justify;'
    xml_suffix += '}</style> '
    xml_suffix += '</head> '
    xml_suffix += '<body> '
    xml_suffix += '<h2> '
    xml_suffix += '<img> '
    xml_suffix += '<xsl:attribute name="src"> '
    xml_suffix += '<xsl:value-of select="/dscd/cita/iRealizadora/@logoData"/> '
    xml_suffix += '</xsl:attribute> '
    xml_suffix += '</img> '
    xml_suffix += '<xsl:text> </xsl:text> '
    xml_suffix += '<xsl:value-of select="/dscd/cita/iRealizadora/@nombre"/> '
    xml_suffix += '<xsl:text>Informe imagenológico</xsl:text> '
    xml_suffix += '</h2> '
    xml_suffix += '<hr/> '
    xml_suffix += '<table> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Paciente: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:call-template name="getPersonName"> '
    xml_suffix += '<xsl:with-param name="personName" '
    xml_suffix += 'select="$cda/cda:recordTarget/cda:patientRole/cda:patient"/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '<xsl:text> </xsl:text> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Identificación del Paciente: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:call-template name="getExtension"> '
    xml_suffix += '<xsl:with-param name="oidPersona" '
    xml_suffix += 'select="$cda/cda:recordTarget/cda:patientRole/cda:id/@extension" '
    xml_suffix += '/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Fecha de Nacimiento: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:variable name="B" '
    xml_suffix += 'select="$cda/cda:recordTarget/cda:patientRole/cda:patient/cda:birthTime/@value"/> '
    xml_suffix += '<xsl:variable name="S" '
    xml_suffix += 'select="$cda/cda:componentOf/cda:encompassingEncounter/cda:effectiveTime/@value"/> '
    xml_suffix += '<xsl:call-template name="formatDate"> '
    xml_suffix += '<xsl:with-param name="date" select="$B"/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '<xsl:text> (</xsl:text> '
    xml_suffix += '<xsl:variable name="BY" select="substring($B, 1, 4)"/> '
    xml_suffix += '<xsl:variable name="SY" select="substring($S, 1, 4)"/> '
    xml_suffix += '<xsl:variable name="Y" select="$SY - $BY"/> '
    xml_suffix += '<xsl:variable name="BM" select="substring($B, 5, 2)"/> '
    xml_suffix += '<xsl:variable name="SM" select="substring($S, 5, 2)"/> '
    xml_suffix += '<xsl:variable name="M" select="$SM - $BM"/> '
    xml_suffix += '<xsl:variable name="YM" select="($Y * 12) + $M"/> '
    xml_suffix += '<xsl:choose> '
    xml_suffix += '<xsl:when test="$YM > 24"> '
    xml_suffix += '<xsl:value-of select="$Y"/> '
    xml_suffix += '<xsl:text> años</xsl:text> '
    xml_suffix += '</xsl:when> '
    xml_suffix += '<xsl:when test="$YM > 2"> '
    xml_suffix += '<xsl:value-of select="$YM"/> '
    xml_suffix += '<xsl:text> meses</xsl:text> '
    xml_suffix += '</xsl:when> '
    xml_suffix += '<xsl:otherwise> '
    xml_suffix += '<xsl:text>menos de 3 meses</xsl:text> '
    xml_suffix += '</xsl:otherwise> '
    xml_suffix += '</xsl:choose> '
    xml_suffix += '<xsl:text>)</xsl:text> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Sexo: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of '
    xml_suffix += 'select="$cda/cda:recordTarget/cda:patientRole/cda:patient/cda:administrativeGenderCode/@displayName" '
    xml_suffix += '/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Departamento: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of '
    xml_suffix += 'select="normalize-space($cda/cda:recordTarget/cda:patientRole/cda:addr/cda:state/text())" '
    xml_suffix += '/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Ciudad: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of '
    xml_suffix += 'select="normalize-space($cda/cda:recordTarget/cda:patientRole/cda:addr/cda:city/text())" '
    xml_suffix += '/> '
    xml_suffix += '</b> '
    xml_suffix += '<xsl:if '
    xml_suffix += 'test="$cda/cda:recordTarget/cda:patientRole/cda:addr/cda:additionalLocator/text() != \'\'"> '
    xml_suffix += '<xsl:text> (</xsl:text> '
    xml_suffix += '<xsl:value-of '
    xml_suffix += 'select="normalize-space($cda/cda:recordTarget/cda:patientRole/cda:addr/cda:additionalLocator/text())"/> '
    xml_suffix += '<xsl:text>)</xsl:text> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<br/> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<br/> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Institución solicitante: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of select="/dscd/cita/iSolicitante/@nombre"/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Médico solicitante: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of select="/dscd/cita/pSolicitante/@nombre"/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<br/> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<br/> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Fecha estudio: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:call-template name="formatDate"> '
    xml_suffix += '<xsl:with-param name="date" '
    xml_suffix += 'select="$cda/cda:componentOf/cda:encompassingEncounter/cda:effectiveTime/@value" '
    xml_suffix += '/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Servicio: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of '
    xml_suffix += 'select="substring-after(\'$cda/cda:componentOf/cda:encompassingEncounter/cda:encounterParticipant/cda:assignedEntity/cda:id/@extension\',\'^\')" '
    xml_suffix += '/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Estudio: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of '
    xml_suffix += 'select="$cda/cda:documentationOf/cda:serviceEvent/cda:code/@displayName" '
    xml_suffix += '/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Número acceso: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of '
    xml_suffix += 'select = "$cda/cda:component/cda:structuredBody/cda:component/cda:section/cda:component/cda:section/cda:entry/cda:act/cda:code/cda:qualifier/cda:value/cda:originalText/text()" '
    xml_suffix += '/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '<tr> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Prioridad: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of select="/dscd/cita/@prioridad"/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '<td> '
    xml_suffix += '<xsl:text>Origen: </xsl:text> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:value-of select="/dscd/cita/@internacion"/> '
    xml_suffix += '</b> '
    xml_suffix += '</td> '
    xml_suffix += '</tr> '
    xml_suffix += '</table> '
    xml_suffix += '<hr/> '
    xml_suffix += '<xsl:apply-templates select="$cda/cda:component[1]/cda:structuredBody[1]/cda:component/cda:section"/> '
    xml_suffix += '<p> '
    xml_suffix += '<br/> '
    xml_suffix += '</p> '
    xml_suffix += '<p> '
    xml_suffix += '<br/> '
    xml_suffix += '</p> '
    xml_suffix += '<p> '
    xml_suffix += '<xsl:call-template name="formatDate"> '
    xml_suffix += '<xsl:with-param name="date" select="$cda/cda:effectiveTime/@value"/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '<xsl:call-template name="formatTime"> '
    xml_suffix += '<xsl:with-param name="date" select="$cda/cda:effectiveTime/@value"/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '<xsl:text> firmado por Médico</xsl:text> '
    xml_suffix += '<xsl:variable name="cdaProfesional1" '
    xml_suffix += 'select="$cda/cda:author[1]/cda:assignedAuthor/cda:assignedPerson"/> '
    xml_suffix += '<xsl:if test="$cdaProfesional1"> '
    xml_suffix += '<xsl:call-template name="getPersonName"> '
    xml_suffix += '<xsl:with-param name="personName" select="$cdaProfesional1"/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '<xsl:variable name="cdaProfesional1org" '
    xml_suffix += 'select="$cda/cda:author[1]/cda:assignedAuthor/cda:representedOrganization/cda:name/text()"/> '
    xml_suffix += '<xsl:if test="$cdaProfesional1org != \'\'"> '
    xml_suffix += '<xsl:text>, </xsl:text> '
    xml_suffix += '<xsl:value-of select="$cdaProfesional1org"/> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '<xsl:variable name="cdaProfesional2" '
    xml_suffix += 'select="$cda/cda:ClinicalDocument/cda:author[2]/cda:assignedAuthor/cda:assignedPerson"/> '
    xml_suffix += '<xsl:if test="$cdaProfesional2"> '
    xml_suffix += '<xsl:text> | </xsl:text> '
    xml_suffix += '<xsl:call-template name="getPersonName"> '
    xml_suffix += '<xsl:with-param name="personName" select="$cdaProfesional2"/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '<xsl:variable name="cdaProfesional2org" '
    xml_suffix += 'select="$cda/cda:author[2]/cda:assignedAuthor/cda:representedOrganization/cda:name/text()"/> '
    xml_suffix += '<xsl:if test="$cdaProfesional2org != \'\'"> '
    xml_suffix += '<xsl:text>, </xsl:text> '
    xml_suffix += '<xsl:value-of select="$cdaProfesional2org"/> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '<xsl:variable name="cdaProfesional3" '
    xml_suffix += 'select="$cda/cda:author[3]/cda:assignedAuthor/cda:assignedPerson"/> '
    xml_suffix += '<xsl:if test="$cdaProfesional3"> '
    xml_suffix += '<xsl:text> | </xsl:text> '
    xml_suffix += '<xsl:call-template name="getPersonName"> '
    xml_suffix += '<xsl:with-param name="personName" select="$cdaProfesional3"/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '<xsl:variable name="cdaProfesional3org" '
    xml_suffix += 'select="$cda/cda:author[3]/cda:assignedAuthor/cda:representedOrganization/cda:name/text()"/> '
    xml_suffix += '<xsl:if test="$cdaProfesional3org != \'\'"> '
    xml_suffix += '<xsl:text>, </xsl:text> '
    xml_suffix += '<xsl:value-of select="$cdaProfesional3org"/> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</p> '
    xml_suffix += '<hr/> '
    xml_suffix += '<p> '
    xml_suffix += '<xsl:value-of select="/dscd/sdtc:signatureTEXT/sdtc:thumbnail/text()"/> '
    xml_suffix += '</p> '
    xml_suffix += '</body> '
    xml_suffix += '</html> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template name="getPersonName"> '
    xml_suffix += '<xsl:param name="personName"/> '
    xml_suffix += '<xsl:for-each select="$personName/cda:name/*"> '
    xml_suffix += '<xsl:text> </xsl:text> '
    xml_suffix += '<xsl:value-of select="."/> '
    xml_suffix += '</xsl:for-each> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template name="getExtension"> '
    xml_suffix += '<xsl:param name="oidPersona"/> '
    xml_suffix += '<xsl:choose> '
    xml_suffix += '<xsl:when test="contains($oidPersona, \'.\')"> '
    xml_suffix += '<xsl:call-template name="getExtension"> '
    xml_suffix += '<xsl:with-param name="oidPersona" select="substring-after($oidPersona, \'.\')"/> '
    xml_suffix += '</xsl:call-template> '
    xml_suffix += '</xsl:when> '
    xml_suffix += '<xsl:otherwise> '
    xml_suffix += '<xsl:value-of select="$oidPersona"/> '
    xml_suffix += '</xsl:otherwise> '
    xml_suffix += '</xsl:choose> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template name="formatDate"> '
    xml_suffix += '<xsl:param name="date"/> '
    xml_suffix += '<xsl:if test="$date != \'\'"> '
    xml_suffix += '<xsl:value-of select="substring($date, 1, 4)"/> '
    xml_suffix += '<xsl:text>-</xsl:text> '
    xml_suffix += '<xsl:value-of select="substring($date, 5, 2)"/> '
    xml_suffix += '<xsl:text>-</xsl:text> '
    xml_suffix += '<xsl:value-of select="substring($date, 7, 2)"/> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template name="formatTime"> '
    xml_suffix += '<xsl:param name="date"/> '
    xml_suffix += '<xsl:if test="$date != \'\'"> '
    xml_suffix += '<xsl:text>T</xsl:text> '
    xml_suffix += '<xsl:value-of select="substring($date, 9, 2)"/> '
    xml_suffix += '<xsl:text>:</xsl:text> '
    xml_suffix += '<xsl:value-of select="substring($date, 11, 2)"/> '
    xml_suffix += '<xsl:text>:</xsl:text> '
    xml_suffix += '<xsl:value-of select="substring($date, 13, 2)"/> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template match="cda:section"> '
    xml_suffix += '<xsl:if test="1=1"> '
    xml_suffix += '<h3> '
    xml_suffix += '<xsl:value-of select="cda:title/text()"/> '
    xml_suffix += '</h3> '
    xml_suffix += '<section> '
    xml_suffix += '<xsl:apply-templates select="cda:entry" mode="pre"/> '
    xml_suffix += '<xsl:apply-templates select="cda:text"/> '
    xml_suffix += '<xsl:apply-templates select="cda:component/cda:section"/> '
    xml_suffix += '<xsl:apply-templates select="cda:entry" mode="post"/> '
    xml_suffix += '</section> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template match="cda:text"> '
    xml_suffix += '<xsl:apply-templates select="*"/> '
    xml_suffix += '</xsl:template> '
    xml_suffix += ' '
    xml_suffix += '<xsl:template match="cda:linkHtml"> '
    xml_suffix += '<xsl:element name="a"> '
    xml_suffix += '<xsl:attribute name="href"><xsl:value-of select="@href"/></xsl:attribute> '
    xml_suffix += '<xsl:value-of select="text()"/> '
    xml_suffix += '</xsl:element> '
    xml_suffix += '</xsl:template> '
    xml_suffix += ' '
    xml_suffix += '<xsl:template match="cda:table"> '
    xml_suffix += '<table border="1"> '
    xml_suffix += '<xsl:apply-templates select="*"/> '
    xml_suffix += '</table> '
    xml_suffix += '</xsl:template> '
    xml_suffix += ' '
    xml_suffix += '<xsl:template match="cda:thead"> '
    xml_suffix += '<thead border="1"> '
    xml_suffix += '<xsl:apply-templates select="*"/> '
    xml_suffix += '</thead> '
    xml_suffix += '</xsl:template> '
    xml_suffix += ' '
    xml_suffix += '<xsl:template match="cda:tbody"> '
    xml_suffix += '<tbody border="1"> '
    xml_suffix += '<xsl:apply-templates select="*"/> '
    xml_suffix += '</tbody> '
    xml_suffix += '</xsl:template> '
    xml_suffix += ' '
    xml_suffix += '<xsl:template match="cda:tr"> '
    xml_suffix += '<tr border="1"> '
    xml_suffix += '<xsl:apply-templates select="*"/> '
    xml_suffix += '</tr> '
    xml_suffix += '</xsl:template> '
    xml_suffix += ' '
    xml_suffix += '<xsl:template match="cda:th"> '
    xml_suffix += '<th border="1"> '
    xml_suffix += '<xsl:apply-templates select="*"/> '
    xml_suffix += '</th> '
    xml_suffix += '</xsl:template> '
    xml_suffix += ' '
    xml_suffix += '<xsl:template match="cda:td"> '
    xml_suffix += '<td border="1"> '
    xml_suffix += '<xsl:apply-templates select="*"/> '
    xml_suffix += '</td> '
    xml_suffix += '</xsl:template> '
    xml_suffix += ' '
    xml_suffix += ' '
    xml_suffix += '<xsl:template match="cda:br"> '
    xml_suffix += '<br/> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template match="cda:paragraph"> '
    xml_suffix += '<p> '
    xml_suffix += '<xsl:apply-templates select="cda:content | text() | cda:br"/> '
    xml_suffix += '</p> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template match="text()"> '
    xml_suffix += '<xsl:value-of select="."/> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template match="cda:content"> '
    xml_suffix += '<xsl:choose> '
    xml_suffix += '<xsl:when test="@styleCode = \'Italics\'"> '
    xml_suffix += '<i> '
    xml_suffix += '<xsl:apply-templates select="cda:content | text() | cda:br"/> '
    xml_suffix += '</i> '
    xml_suffix += '</xsl:when> '
    xml_suffix += '<xsl:when test="@styleCode = \'Bold\'"> '
    xml_suffix += '<b> '
    xml_suffix += '<xsl:apply-templates select="cda:content | text() | cda:br"/> '
    xml_suffix += '</b> '
    xml_suffix += '</xsl:when> '
    xml_suffix += '</xsl:choose> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template match="cda:entry" mode="pre"> '
    xml_suffix += '<xsl:if '
    xml_suffix += 'test="contains(\' 129716005 129717001 129718006 129719003 111351 111352 111353 \', concat(\' \', cda:observation/cda:code/@code, \'  \'))"> '
    xml_suffix += '<xsl:value-of select="cda:observation/cda:code/@displayName"/> '
    xml_suffix += '<br/> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '<xsl:template match="cda:entry" mode="post"> '
    xml_suffix += '<xsl:if '
    xml_suffix += 'test="not(contains(\' 129716005 129717001 129718006 129719003 111351 111352 111353 \', concat(\' \',cda:observation/cda:code/@ code, \' \')))"> '
    xml_suffix += '<xsl:choose> '
    xml_suffix += '<xsl:when test="cda:observation/cda:value/cda:qualifier"> '
    xml_suffix += '<xsl:value-of select="cda:observation/cda:value/cda:qualifier/@displayName"/> '
    xml_suffix += '<br/> '
    xml_suffix += '</xsl:when> '
    xml_suffix += '<xsl:when test="cda:observation/cda:value"> '
    xml_suffix += '<xsl:value-of select="cda:observation/cda:value/@displayName"/> '
    xml_suffix += '<br/> '
    xml_suffix += '</xsl:when> '
    xml_suffix += '<xsl:otherwise> '
    xml_suffix += '<xsl:value-of select="cda:observation/cda:code/@displayName"/> '
    xml_suffix += '<br/> '
    xml_suffix += '</xsl:otherwise> '
    xml_suffix += '</xsl:choose> '
    xml_suffix += '</xsl:if> '
    xml_suffix += '</xsl:template> '
    xml_suffix += '</xsl:stylesheet> '
    xml_suffix += '</dscd> '

    xml_cda = xml_preffix + xml_cda + xml_suffix
    xml_cda_base64 = base64.b64encode(bytes(xml_cda, 'utf-8'))
    seriesuid = '2.25.{}'.format(int(str(uuid.uuid4()).replace('-', ''), 16))
    xml_dcm = '<?xml version="1.0" encoding="UTF-8"?>'
    xml_dcm += '<NativeDicomModel xml-space="preserved">'
    xml_dcm += '<DicomAttribute keyword="FileMetaInformationVersion" tag="00020001" vr="OB"><InlineBinary>AAE=</InlineBinary></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="MediaStorageSOPClassUID" tag="00020002" vr="UI"><Value number="1">1.2.840.10008.5.1.4.1.1.104.2</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="MediaStorageSOPInstanceUID" tag="00020003" vr="UI"><Value number="1">{}</Value></DicomAttribute>'.format(
        informeuid)
    xml_dcm += '<DicomAttribute keyword="TransferSyntaxUID" tag="00020010" vr="UI"><Value number="1">1.2.840.10008.1.2</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="ImplementationClassUID" tag="00020012" vr="UI"><Value number="1">2.16.858.0.2.9.62.0.1.0.217215590012</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="ImplementationVersionName" tag="00020013" vr="SH"><Value number="1">JESROS OPENDICOM</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="SpecificCharacterSet" tag="00080005" vr="CS"><Value number="1">ISO_IR 100</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="SOPClassUID" tag="00080016" vr="UI"><Value number="1">1.2.840.10008.5.1.4.1.1.104.2</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="SOPInstanceUID" tag="00080018" vr="UI"><Value number="1">{}</Value></DicomAttribute>'.format(
        informeuid)
    xml_dcm += '<DicomAttribute keyword="TimezoneOffsetFromUTC" tag="00080201" vr="SH"><Value number="1">-0300</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="PatientName" tag="00100010" vr="PN"><PersonName number="1"><Alphabetic><FamilyName>{}</FamilyName></Alphabetic></PersonName></DicomAttribute>'.format(
        values_submit['PatientName'][0])
    xml_dcm += '<DicomAttribute keyword="PatientID" tag="00100020" vr="LO"><Value number="1">{}</Value></DicomAttribute>'.format(
        values_submit['PatientID'][0])
    xml_dcm += '<DicomAttribute keyword="IssuerOfPatientID" tag="00100021" vr="LO"><Value number="1">{}</Value></DicomAttribute>'.format(
        values_submit['PatientIDIssuer'][0])
    xml_dcm += '<DicomAttribute keyword="PatientBirthDate" tag="00100030" vr="DA"><Value number="1">{}</Value></DicomAttribute>'.format(
        values_submit['PatientBirthDate'][0])
    xml_dcm += '<DicomAttribute keyword="PatientSex" tag="00100040" vr="CS"><Value number="1">{}</Value></DicomAttribute>'.format(
        values_submit['PatientSex'][0])
    xml_dcm += '<DicomAttribute keyword="StudyInstanceUID" tag="0020000D" vr="UI"><Value number="1">{}</Value></DicomAttribute>'.format(
        values_submit['StudyIUID'][0])
    xml_dcm += '<DicomAttribute keyword="Modality" tag="00080060" vr="CS"><Value number="1">DOC</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="SeriesInstanceUID" tag="0020000E" vr="UI"><Value number="1">{}</Value></DicomAttribute>'.format(
        seriesuid)
    xml_dcm += '<DicomAttribute keyword="SeriesNumber" tag="00200011" vr="IS"><Value number="1">-16</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="SeriesDescription" tag="0008103E" vr="LO"><Value number="1">ClinicalDocument</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="SeriesDate" tag="00080021" vr="DA"><Value number="1">{}</Value></DicomAttribute>'.format(
        datetime.now().strftime("%Y%m%d"))
    xml_dcm += '<DicomAttribute keyword="SeriesTime" tag="00080031" vr="TM"><Value number="1">{}</Value></DicomAttribute>'.format(
        datetime.now().strftime("%H%M%S"))
    xml_dcm += '<DicomAttribute keyword="PerformedProcedureStepStartDate" tag="00400244" vr="DA"><Value number="1">{}</Value></DicomAttribute>'.format(
        datetime.now().strftime("%Y%m%d"))
    xml_dcm += '<DicomAttribute keyword="PerformedProcedureStepStartTime" tag="00400245" vr="TM"><Value number="1">{}</Value></DicomAttribute>'.format(
        datetime.now().strftime("%H%M%S"))
    xml_dcm += '<DicomAttribute keyword="Manufacturer" tag="00080070" vr="LO"><Value number="1">opendicom (Jesros SA)</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="InstitutionAddress" tag="00080081" vr="ST"><Value number="1">Agesic, Torre Ejecutiva Torre Sur, Liniers 1324, Montevideo, Uruguay</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="SoftwareVersions" tag="00181020" vr="LO"><Value number="1">2.0</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="ConversionType" tag="00080064" vr="CS"><Value number="1">WSD</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="InstanceNumber" tag="00200013" vr="IS"><Value number="1">1</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="ContentDate" tag="00080023" vr="DA"><Value number="1">{}</Value></DicomAttribute>'.format(
        datetime.now().strftime("%Y%m%d"))
    xml_dcm += '<DicomAttribute keyword="ContentTime" tag="00080033" vr="TM"><Value number="1">{}</Value></DicomAttribute>'.format(
        datetime.now().strftime("%H%M%S"))
    xml_dcm += '<DicomAttribute keyword="AcquisitionDateTime" tag="0008002A" vr="DT"><Value number="1">{}{}</Value></DicomAttribute>'.format(
        datetime.now().strftime("%Y%m%d"), datetime.now().strftime("%H%M%S"))
    xml_dcm += '<DicomAttribute keyword="BurnedInAnnotation" tag="00280301" vr="CS"><Value number="1">YES</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="DocumentTitle" tag="00420010" vr="ST"><Value number="1">INFORME IMAGENOLOGIGO</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="HL7InstanceIdentifier" tag="0040E001" vr="ST"><Value number="1">{}</Value></DicomAttribute>'.format(
        autenticado.id)
    xml_dcm += '<DicomAttribute keyword="MIMETypeOfEncapsulatedDocument" tag="00420012" vr="LO"><Value number="1">text/xml</Value></DicomAttribute>'
    xml_dcm += '<DicomAttribute keyword="EncapsulatedDocument" tag="00420011" vr="OB"><InlineBinary>{}</InlineBinary></DicomAttribute>'.format(
        xml_cda_base64.decode("utf-8"))
    xml_dcm += '</NativeDicomModel>'

    submit.listoparaautenticacion = 'NO'
    submit.save()
    models.Firma.objects.filter(informe=submit).delete()
    url = 'http://127.0.0.1:8080/dcm4chee-arc/aets/{}/rs/studies'.format(institution.short_name)
    headers = {'Content-Type': 'multipart/related;type=application/dicom+xml; boundary=myboundary;'}
    data = '\r\n--myboundary\r\nContent-Type: application/dicom+xml; transfer-syntax=1.2.840.10008.1.2.1\r\n\r\n{}\r\n--myboundary--'.format(
        xml_dcm)
    requests.post(url, headers=headers, data=data.encode('utf-8'))
    requests.get(url + '?0020000D=' + values_submit['StudyIUID'][0])
    # Active user patient
    User.objects.filter(username=values_submit['PatientID'][0]).update(is_active=True)
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
