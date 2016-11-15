from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.models import Session
from django.conf import settings
from html5dicom import models
import requests
import json


def user_login(request, *args, **kwargs):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/html5dicom/main')
            else:
                return render(request, template_name='html5dicom/login.html')
        else:
            return render(request, template_name='html5dicom/login.html')
                
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect('/html5dicom/main')
        else:
            return render(request, template_name='html5dicom/login.html')


@login_required(login_url='/html5dicom/login')
def user_logout(request, *args, **kwargs):
    logout(request)
    return HttpResponseRedirect('/html5dicom/login')


@login_required(login_url='/html5dicom/login')
def main(request, *args, **kwargs):
    if request.user.is_authenticated:
        url_httpdicom = models.Setting.objects.get(key='url_httpdicom').value
        url_httpdicom_ext = models.Setting.objects.get(key='url_httpdicom_ext').value
        organization = {}
        for role in models.Role.objects.filter(user=request.user.id).order_by('default'):
            if role.institution:
                if role.institution.organization.short_name in organization:
                    if role.institution.short_name in organization[role.institution.organization.short_name]['institution']:
                        organization[role.institution.organization.short_name]['institution'][role.institution.short_name].update(
                            {
                                role.get_name_display(): {
                                    'max_rows': role.max_rows,
                                    "service": []
                                }
                            }
                        )
                    else:
                        url_httpdicom_req = url_httpdicom + '/custodians/titles/' + role.institution.organization.short_name
                        url_httpdicom_req += '/aets/' + role.institution.short_name
                        oid_inst = requests.get(url_httpdicom_req)
                        organization[role.institution.organization.short_name]['institution'].update(
                            {
                                role.institution.short_name: {
                                    'aet': role.institution.short_name,
                                    'oid': oid_inst.json()[0],
                                    role.get_name_display(): {
                                        'max_rows': role.max_rows,
                                        "service": []
                                    }
                                }
                            }
                        )
                else:
                    url_httpdicom_req = url_httpdicom + '/custodians/titles/' + role.institution.organization.short_name
                    oid_org = requests.get(url_httpdicom_req)
                    url_httpdicom_req += '/aets/' + role.institution.short_name
                    oid_inst = requests.get(url_httpdicom_req)
                    organization.update({
                        role.institution.organization.short_name:
                            {
                                "oid": oid_org.json()[0],
                                "name": role.institution.organization.short_name,
                                "institution": {
                                    role.institution.short_name: {
                                        'aet': role.institution.short_name,
                                        'oid': oid_inst.json()[0],
                                        role.get_name_display(): {
                                            'max_rows': role.max_rows,
                                            "service": []
                                        }
                                    }
                                }
                            }
                    })
            else:
                if role.service.institution.organization.short_name in organization:
                    if role.service.institution.short_name in organization[role.service.institution.organization.short_name]['institution']:
                        if role.get_name_display() in organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name]:
                            if role.service.name not in organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name][role.get_name_display()]['service']:
                                organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name][role.get_name_display()]['service'].append(role.service.name)
                        else:
                            organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name].update(
                                {
                                    role.get_name_display(): {
                                        'max_rows': role.max_rows,
                                        "service": [role.service.name]
                                    }
                                })
                    else:
                        url_httpdicom_req = url_httpdicom + '/custodians/titles/' + role.service.institution.organization.short_name
                        url_httpdicom_req += '/aets/' + role.service.institution.short_name
                        oid_inst = requests.get(url_httpdicom_req)
                        organization[role.service.institution.organization.short_name]['institution'].update(
                            {
                                role.service.institution.short_name: {
                                    'aet': role.service.institution.short_name,
                                    'oid': oid_inst.json()[0],
                                    role.get_name_display(): {
                                        'max_rows': role.max_rows,
                                        "service": [role.service.name]
                                    }
                                }
                            }
                        )
                else:
                    url_httpdicom_req = url_httpdicom + '/custodians/titles/' + role.service.institution.organization.short_name
                    oid_org = requests.get(url_httpdicom_req)
                    url_httpdicom_req += '/aets/' + role.service.institution.short_name
                    oid_inst = requests.get(url_httpdicom_req)
                    organization.update({
                        role.service.institution.organization.short_name:
                            {
                                "oid": oid_org.json()[0],
                                "name": role.service.institution.organization.short_name,
                                "institution": {
                                    role.service.institution.short_name: {
                                        'aet': role.service.institution.short_name,
                                        'oid': oid_inst.json()[0],
                                        role.get_name_display(): {
                                            'max_rows': role.max_rows,
                                            "service": [role.service.name]
                                        }
                                    }
                                }
                            }
                    })
        context_user = {'organization': organization, 'httpdicom': url_httpdicom_ext}
        return render(request, template_name='html5dicom/main.html', context=context_user)


@login_required(login_url='/html5dicom/login')
def weasis(request, *args, **kwargs):
    url_httpdicom = models.Setting.objects.get(key='url_httpdicom').value
    jnlp_file = open(settings.STATIC_ROOT + 'html5dicom/weasis/weasis.jnlp', 'r')
    jnlp_text = jnlp_file.read()
    jnlp_file.close()
    base_url = request.META['wsgi.url_scheme']+'://'+request.META['HTTP_HOST']
    if request.GET['requestType'] == 'STUDY':
        manifiest = requests.get(url_httpdicom + '/IHEInvokeImageDisplay?requestType=STUDY&studyUID=' + request.GET['study_uid'] + '&viewerType=IHE_BIR&diagnosticQuality=true&keyImagesOnly=false&custodianOID=' + request.GET['custodianOID'] + '&session=' + request.session.session_key + '&proxyURI=' + base_url + '/html5dicom/wado')
        jnlp_text = jnlp_text.replace('%@', manifiest.text)
    elif request.GET['requestType'] == 'SERIES':
        manifiest = requests.get(url_httpdicom + '/IHEInvokeImageDisplay?requestType=SERIES&studyUID=' + request.GET['study_uid'] + '&seriesUID=' + request.GET['series_uid'] + '&viewerType=IHE_BIR&diagnosticQuality=true&keyImagesOnly=false&custodianOID=' + request.GET['custodianOID'] + '&session=' + request.session.session_key + '&proxyURI=' + base_url + '/html5dicom/wado')
        jnlp_text = jnlp_text.replace('%@', manifiest.text)
    jnlp_text = jnlp_text.replace('{IIDURL}', base_url +'/static/html5dicom')
    return HttpResponse(jnlp_text, content_type="application/x-java-jnlp-file")


def osirix(request, *args, **kwargs):
    if 'session' in request.GET:
        try:
            session = Session.objects.get(session_key=request.GET['session'])
            session.get_decoded()[SESSION_KEY]
            url_httpdicom = models.Setting.objects.get(key='url_httpdicom').value
            if request.GET['requestType'] == 'STUDY':
                url_zip = url_httpdicom + '/pacs/' + request.GET['custodianOID'] + '/dcm.zip?StudyInstanceUID=' + \
                          request.GET['study_uid']
                # Valida accession number
                #if request.GET['accession_no'] == '':
                #    url_zip = url_httpdicom + '/pacs/' + request.GET['custodianOID'] + '/dcm.zip?StudyInstanceUID=' + request.GET['study_uid']
                #else:
                #    url_zip = url_httpdicom + '/pacs/' + request.GET['custodianOID'] + '/dcm.zip?AccessionNumber=' + request.GET['accession_no']
                r = requests.get(url_zip)
                return HttpResponse(r.content, content_type=r.headers.get('content-type'))
            elif request.GET['requestType'] == 'SERIES':
                url_zip = url_httpdicom + '/pacs/' + request.GET['custodianOID'] + '/dcm.zip?SeriesInstanceUID=' + \
                          request.GET['series_uid']
                r = requests.get(url_zip)
                return HttpResponse(r.content, content_type=r.headers.get('content-type'))
        except (Session.DoesNotExist, KeyError):
            raise PermissionDenied
    else:
        return HttpResponse('Error', status=400)


def cornerstone(request, *args, **kwargs):
    url_httpdicom = models.Setting.objects.get(key='url_httpdicom').value
    base_url = request.META['wsgi.url_scheme']+'://'+request.META['HTTP_HOST']
    if request.GET['requestType'] == 'STUDY':
        url_manifiest = url_httpdicom + '/IHEInvokeImageDisplay?requestType=STUDY&studyUID=' + request.GET['study_uid'] + '&viewerType=cornerstone&diagnosticQuality=true&keyImagesOnly=false&custodianOID=' + request.GET['custodianOID'] + '&session=' + request.session.session_key + '&proxyURI=' + base_url + '/html5dicom/wado'
    elif request.GET['requestType'] == 'SERIES':
        url_manifiest = url_httpdicom + '/IHEInvokeImageDisplay?requestType=SERIES&studyUID=' + request.GET['study_uid'] + '&seriesUID=' + request.GET['series_uid'] + '&viewerType=cornerstone&diagnosticQuality=true&keyImagesOnly=false&custodianOID=' + request.GET['custodianOID'] + '&session=' + request.session.session_key + '&proxyURI=' + base_url + '/html5dicom/wado'
    else:
        url_manifiest = ''
    manifiest = requests.get(url_manifiest)
    return HttpResponse(manifiest.text, content_type=manifiest.headers.get('content-type'))


def wado(request, *args, **kwargs):
    if 'session' in request.GET:
        try:
            session = Session.objects.get(session_key=request.GET['session'])
            session.get_decoded()[SESSION_KEY]
            url_httpdicom = models.Setting.objects.get(key='url_httpdicom').value
            url_request = request.build_absolute_uri()
            url_wado = url_httpdicom + url_request[url_request.index("?"):]
            r = requests.get(url_wado)
            return HttpResponse(r.content, content_type=r.headers.get('content-type'))
        except (Session.DoesNotExist, KeyError):
            raise PermissionDenied
    else:
        return HttpResponse('Error', status=400)
