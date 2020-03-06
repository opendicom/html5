from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout, SESSION_KEY
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from html5dicom.models import Setting, UserChangePassword, UserViewerSettings, Role
from html5dicom.forms import UserViewerSettingsForm
import requests
import urllib


def user_login(request, *args, **kwargs):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_active:
                try:
                    ucp = UserChangePassword.objects.get(user=user)
                    changepassword=ucp.changepassword
                except UserChangePassword.DoesNotExist:
                    changepassword=False
                if changepassword:
                    return HttpResponseRedirect('/html5dicom/password')
                else:
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
        try:
            ucp = UserChangePassword.objects.get(user=request.user)
            changepassword = ucp.changepassword
        except UserChangePassword.DoesNotExist:
            changepassword = False
        if changepassword:
            return HttpResponseRedirect('/html5dicom/password')
        try:
            role_patient = Role.objects.get(user=request.user, name='pac')
            url_httpdicom_req = settings.HTTP_DICOM + '/custodians/titles/' + role_patient.institution.organization.short_name
            oid_org = requests.get(url_httpdicom_req)
            url_httpdicom_req += '/aets/' + role_patient.institution.short_name
            oid_inst = requests.get(url_httpdicom_req)
            try:
                config_toolbar = Setting.objects.get(key='toolbar_patient').value
            except Setting.DoesNotExist:
                config_toolbar = 'full'
            organization = {}
            organization.update({
                "patientID": request.user.username,
                "name": role_patient.institution.organization.short_name,
                "oid": oid_org.json()[0],
                "config_toolbar": config_toolbar,
                "institution": {
                    'name': role_patient.institution.short_name,
                    'aet': role_patient.institution.short_name,
                    'oid': oid_inst.json()[0]
                }
            })
            user_viewer = ''
            try:
                user_viewer = UserViewerSettings.objects.get(user=request.user).viewer
            except UserViewerSettings.DoesNotExist:
                user_viewer = ''
            context_user = {'organization': organization, 'httpdicom': request.META['HTTP_HOST'],
                            'user_viewer': user_viewer, 'navbar': 'patient'}
            return render(request, template_name='html5dicom/patient_main.html', context=context_user)
        except Role.DoesNotExist:
            pass

        organization = {}
        if Role.objects.filter(user=request.user.id).exclude(name__in=['res', 'pac']).count() < 1:
            logout(request)
            raise PermissionDenied
        for role in Role.objects.filter(user=request.user.id).exclude(name__in=['res', 'pac']):
            if role.service:
                default_organization = ''
                default_institution = ''
                default_role = ''
                default_service = ''
                if role.default_organization:
                    default_organization = role.service.institution.organization.short_name
                if role.default_institution:
                    default_institution = role.service.institution.short_name
                if role.default_role:
                    default_role = role.get_name_display()
                if role.default_service:
                    default_service = role.service.name
                if role.service.institution.organization.short_name in organization:
                    if organization['default_organization'] == '':
                        organization['default_organization'] = default_organization
                    if organization[role.service.institution.organization.short_name]['default_institution'] == '':
                        organization[role.service.institution.organization.short_name]['default_institution'] = default_institution
                    if role.service.institution.short_name in organization[role.service.institution.organization.short_name]['institution']:
                        if organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name]['default_role'] == '':
                            organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name]['default_role'] = default_role
                        if role.get_name_display() in organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name]:
                            if organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name][role.get_name_display()]['default_service'] == '':
                                organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name][role.get_name_display()]['default_service'] = default_service
                            if role.service.name not in organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name][role.get_name_display()]['service']:
                                organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name][role.get_name_display()]['service'].append(role.service.name)
                        else:
                            organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name].update(
                                {
                                    role.get_name_display(): {
                                        "max_rows": role.max_rows,
                                        "default_service": default_service,
                                        "service": [role.service.name]
                                    }
                                })
                    else:
                        url_httpdicom_req = settings.HTTP_DICOM + '/custodians/titles/' + role.service.institution.organization.short_name
                        url_httpdicom_req += '/aets/' + role.service.institution.short_name
                        oid_inst = requests.get(url_httpdicom_req)
                        organization[role.service.institution.organization.short_name]['institution'].update(
                            {
                                role.service.institution.short_name: {
                                    "aet": role.service.institution.short_name,
                                    "oid": oid_inst.json()[0],
                                    "default_role": default_role,
                                    role.get_name_display(): {
                                        "max_rows": role.max_rows,
                                        "default_service": default_service,
                                        "service": [role.service.name]
                                    }
                                }
                            }
                        )
                else:
                    url_httpdicom_req = settings.HTTP_DICOM + '/custodians/titles/' + role.service.institution.organization.short_name
                    oid_org = requests.get(url_httpdicom_req)
                    url_httpdicom_req += '/aets/' + role.service.institution.short_name
                    oid_inst = requests.get(url_httpdicom_req)
                    organization.update({
                        "default_organization": default_organization,
                        role.service.institution.organization.short_name:
                            {
                                "oid": oid_org.json()[0],
                                "name": role.service.institution.organization.short_name,
                                "default_institution": default_institution,
                                "institution": {
                                    role.service.institution.short_name: {
                                        "aet": role.service.institution.short_name,
                                        "oid": oid_inst.json()[0],
                                        "default_role": default_role,
                                        role.get_name_display(): {
                                            "max_rows": role.max_rows,
                                            "default_service": default_service,
                                            "service": [role.service.name]
                                        }
                                    }
                                }
                            }
                    })
        user_viewer = ''
        try:
            user_viewer = UserViewerSettings.objects.get(user=request.user).viewer
        except UserViewerSettings.DoesNotExist:
            user_viewer = ''
        context_user = {'organization': organization, 'httpdicom': request.META['HTTP_HOST'], 'user_viewer': user_viewer}
        return render(request, template_name='html5dicom/main.html', context=context_user)


@login_required(login_url='/html5dicom/login')
def weasis(request, *args, **kwargs):
    jnlp_file = open(settings.STATIC_ROOT + 'html5dicom/weasis/weasis.jnlp', 'r')
    jnlp_text = jnlp_file.read()
    jnlp_file.close()
    base_url = request.META['wsgi.url_scheme']+'://'+request.META['HTTP_HOST']
    if request.GET['requestType'] == 'STUDY':
        manifiest = requests.get(settings.HTTP_DICOM + '/IHEInvokeImageDisplay?requestType=STUDY&studyUID=' + request.GET['study_uid'] + '&viewerType=IHE_BIR&diagnosticQuality=true&keyImagesOnly=false&custodianOID=' + request.GET['custodianOID'] + '&session=' + request.session.session_key + '&proxyURI=' + base_url + '/html5dicom/wado')
        jnlp_text = jnlp_text.replace('%@', manifiest.text)
    elif request.GET['requestType'] == 'SERIES':
        manifiest = requests.get(settings.HTTP_DICOM + '/IHEInvokeImageDisplay?requestType=SERIES&studyUID=' + request.GET['study_uid'] + '&seriesUID=' + request.GET['series_uid'] + '&viewerType=IHE_BIR&diagnosticQuality=true&keyImagesOnly=false&custodianOID=' + request.GET['custodianOID'] + '&session=' + request.session.session_key + '&proxyURI=' + base_url + '/html5dicom/wado')
        jnlp_text = jnlp_text.replace('%@', manifiest.text)
    jnlp_text = jnlp_text.replace('{IIDURL}', base_url +'/static/html5dicom')
    return HttpResponse(jnlp_text, content_type="application/x-java-jnlp-file")


def datatables_studies(request, *args, **kwargs):
    if not request.user.is_authenticated():
        if request.is_ajax():
            return HttpResponse(status=403, content="you are not logged in")
        else:
            return HttpResponseRedirect('/html5dicom/login')
    datatables = {
        "draw": request.GET['draw'],
        "start": request.GET['start'],
        "length": request.GET['length'],
        "username": request.GET['username'],
        "useroid": request.GET['useroid'],
        "session": request.GET['session'],
        "custodiantitle": request.GET['custodiantitle'],
        "aet": request.GET['aet'],
        "role": request.GET['role'],
        "max": request.GET['max'],
        "new": request.GET['new'],
        "_": request.GET['_'],
    }
    if 'date_start' in request.GET:
        datatables['date_start'] = request.GET['date_start']
    if 'date_end' in request.GET:
        datatables['date_end'] = request.GET['date_end']
    search = request.GET.get('search')
    if 'value' in search:
        datatables['AccessionNumber'] = search['value']
    columns = request.GET.get('columns')
    if request.GET['columns'][3]['search']['value']:
        datatables['PatientID'] = request.GET['columns'][3]['search']['value']
    if request.GET['columns'][4]['search']['value']:
        datatables['PatientName'] = ''
    if request.GET['columns'][6]['search']['value']:
        datatables['Modalities'] = ''
    if request.GET['columns'][7]['search']['value']:
        datatables['StudyDescription'] = ''
    response_datatables = requests.get(
        settings.HTTP_DICOM + '/datatables/studies?' + urllib.parse.urlencode(datatables, quote_via=urllib.parse.quote))
    response = HttpResponse(response_datatables.content,
                            status=response_datatables.status_code,
                            content_type=response_datatables.headers['Content-Type'])
    return response


def cornerstone(request, *args, **kwargs):
    if not request.user.is_authenticated():
        if request.is_ajax():
            return HttpResponse(status=403, content="you are not logged in")
        else:
            return HttpResponseRedirect('/html5dicom/login')
    base_url = request.META['wsgi.url_scheme'] + '://' + request.META['HTTP_HOST']
    if request.GET['requestType'] == 'STUDY':
        url_manifiest = settings.HTTP_DICOM + '/IHEInvokeImageDisplay?requestType=STUDY&studyUID=' + request.GET['study_uid'] + '&viewerType=cornerstone&diagnosticQuality=true&keyImagesOnly=false&custodianOID=' + request.GET['custodianOID'] + '&session=' + request.session.session_key + '&proxyURI=' + base_url + '/html5dicom/wado'
    elif request.GET['requestType'] == 'SERIES':
        url_manifiest = settings.HTTP_DICOM + '/IHEInvokeImageDisplay?requestType=SERIES&studyUID=' + request.GET['study_uid'] + '&seriesUID=' + request.GET['series_uid'] + '&viewerType=cornerstone&diagnosticQuality=true&keyImagesOnly=false&custodianOID=' + request.GET['custodianOID'] + '&session=' + request.session.session_key + '&proxyURI=' + base_url + '/html5dicom/wado'
    else:
        url_manifiest = ''
    manifiest = requests.get(url_manifiest)
    return HttpResponse(manifiest.text, content_type=manifiest.headers.get('content-type'))


def stream_response(url_zip):
    r = requests.get(url_zip, stream=True)
    for chunk in r.iter_content(512 * 1024):
        yield chunk


def osirix(request, *args, **kwargs):
    if 'session' in request.GET:
        try:
            session = Session.objects.get(session_key=request.GET['session'],
                                          expire_date__gt=timezone.now())
            session.get_decoded()[SESSION_KEY]
            if request.GET['requestType'] == 'STUDY':
                url_zip = settings.HTTP_DICOM + '/pacs/' + request.GET['custodianOID'] + '/dcm.zip?StudyInstanceUID=' + \
                          request.GET['study_uid']
                # Valida accession number
                #if request.GET['accession_no'] == '':
                #    url_zip = settings.HTTP_DICOM + '/pacs/' + request.GET['custodianOID'] + '/dcm.zip?StudyInstanceUID=' + request.GET['study_uid']
                #else:
                #    url_zip = settings.HTTP_DICOM + '/pacs/' + request.GET['custodianOID'] + '/dcm.zip?AccessionNumber=' + request.GET['accession_no']
                r = StreamingHttpResponse(stream_response(url_zip))
                r['Content-Type'] = "application/zip"
                r['Content-Disposition'] = "attachment; filename=dcm.zip"
                return r
            elif request.GET['requestType'] == 'SERIES':
                url_zip = settings.HTTP_DICOM + '/pacs/' + request.GET['custodianOID'] + '/dcm.zip?SeriesInstanceUID=' + \
                          request.GET['series_uid']
                r = StreamingHttpResponse(stream_response(url_zip))
                r['Content-Type'] = "application/zip"
                r['Content-Disposition'] = "attachment; filename=dcm.zip"
                return r
        except (Session.DoesNotExist, KeyError):
            raise PermissionDenied
    else:
        return HttpResponse('Error', status=400)


def wado(request, *args, **kwargs):
    if 'session' in request.GET:
        try:
            session = Session.objects.get(session_key=request.GET['session'],
                                          expire_date__gt=timezone.now())
            session.get_decoded()[SESSION_KEY]
            url_request = request.build_absolute_uri()
            url_wado = settings.OID_URL[request.GET['arcId']] + url_request[url_request.index("?"):]
            r = requests.get(url_wado)
            return HttpResponse(r.content, content_type=r.headers.get('content-type'))
        except (Session.DoesNotExist, KeyError):
            raise PermissionDenied
    else:
        return HttpResponse('Error', status=400)


@login_required(login_url='/html5dicom/login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            try:
                ucp = UserChangePassword.objects.get(user=user)
                ucp.changepassword=False
                ucp.save()
            except UserChangePassword.DoesNotExist:
                pass
            messages.success(request, 'Su contraseña fue actualizada correctamente!')
            return redirect('logout')
        else:
            messages.error(request, 'Favor revisar la informacion ingresada.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'html5dicom/change_password.html', {
        'form': form
    })


@login_required(login_url='/html5dicom/login')
def viewer_settings(request):
    try:
        userviewersettings = UserViewerSettings.objects.get(user=request.user)
    except UserViewerSettings.DoesNotExist:
        userviewersettings = UserViewerSettings.objects.create(user=request.user)
        userviewersettings.save()
    if request.method == 'POST':
        form = UserViewerSettingsForm(instance=userviewersettings, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada correctamente!')
        else:
            messages.error(request, 'Error al guardar')
    else:
        form = UserViewerSettingsForm(instance=userviewersettings)

    return render(request, 'html5dicom/viewer_settings.html', {
        'form': form
    })
