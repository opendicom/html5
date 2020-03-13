from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout, SESSION_KEY
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from html5dicom.models import Setting, UserChangePassword, UserViewerSettings, Role, Institution
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
            role_patient = Role.objects.get(user=request.user, name='Paciente')
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
        if Role.objects.filter(user=request.user.id).exclude(name__in=['Rest', 'Paciente']).count() < 1:
            logout(request)
            raise PermissionDenied
        for role in Role.objects.filter(user=request.user.id).exclude(name__in=['Rest', 'Paciente']):
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


def data_tables_studies(request, *args, **kwargs):
    authorized = True
    if not request.user.is_authenticated():
        authorized = False
    try:
        institution = Institution.objects.get(short_name=request.GET['aet'])
    except Institution.DoesNotExist:
        authorized = False
    if authorized and not Role.objects.filter(Q(service__institution=institution) | Q(institution=institution), user=request.user, name=request.GET['role']).exists():
        authorized = False
    if not authorized:
        if request.is_ajax():
            error = {
                "draw": request.GET['draw'],
                "data": [],
                "recordsFiltered": 0,
                "recordsTotal": 0,
                "error": "No autorizado"
            }
            return JsonResponse(error)
        else:
            return HttpResponseRedirect('/html5dicom/login')
    data_tables = {
        "draw": request.GET['draw'],
        "start": request.GET['start'],
        "length": request.GET['length'],
        "username": request.user.username,
        "useroid": request.GET['useroid'],
        "session": request.session._session_key,
        "custodiantitle": request.GET['custodiantitle'],
        "aet": request.GET['aet'],
        "role": request.GET['role'],
        "max": request.GET['max'],
        "new": request.GET['new'],
        "_": request.GET['_'],
    }
    if 'date_start' in request.GET:
        if request.GET['date_start'] != '':
            data_tables['date_start'] = request.GET['date_start']
    if 'date_end' in request.GET:
        if request.GET['date_end'] != '':
            data_tables['date_end'] = request.GET['date_end']
    if 'cache' in request.GET:
        if request.GET['cache'] != '':
            data_tables['cache'] = request.GET['cache']
    if 'order[0][column]' in request.GET:
        data_tables['order'] = request.GET['order[0][column]']
    if 'order[0][dir]' in request.GET:
        data_tables['dir'] = request.GET['order[0][dir]'].lower()
    if request.GET['search[value]'] != '':
        data_tables['AccessionNumber'] = request.GET['search[value]']
    if request.GET['columns[3][search][value]'] != '':
        data_tables['PatientID'] = request.GET['columns[3][search][value]']
    if request.GET['columns[4][search][value]'] != '':
        data_tables['PatientName'] = request.GET['columns[4][search][value]']
    if request.GET['columns[6][search][value]'] != '':
        data_tables['Modalities'] = request.GET['columns[6][search][value]']
    if request.GET['columns[7][search][value]'] != '':
        data_tables['StudyDescription'] = request.GET['columns[7][search][value]']
    response_data_tables = requests.get(
        settings.HTTP_DICOM + '/datatables/studies?' + urllib.parse.urlencode(data_tables, quote_via=urllib.parse.quote))
    response = HttpResponse(response_data_tables.content,
                            status=response_data_tables.status_code,
                            content_type=response_data_tables.headers['Content-Type'])
    return response


def data_tables_series(request, *args, **kwargs):
    if not request.user.is_authenticated():
        if request.is_ajax():
            error = {
                "draw": request.GET['draw'],
                "data": [],
                "recordsFiltered": 0,
                "recordsTotal": 0,
                "error": "No autorizado"
            }
            return JsonResponse(error)
        else:
            return HttpResponseRedirect('/html5dicom/login')
    response_data_tables = requests.get(
        settings.HTTP_DICOM + '/datatables/series?' + urllib.parse.urlencode(request.GET, quote_via=urllib.parse.quote))
    response = HttpResponse(response_data_tables.content,
                            status=response_data_tables.status_code,
                            content_type=response_data_tables.headers['Content-Type'])
    return response


def data_tables_patient(request, *args, **kwargs):
    if not request.user.is_authenticated():
        if request.is_ajax():
            error = {
                "draw": request.GET['draw'],
                "data": [],
                "recordsFiltered": 0,
                "recordsTotal": 0,
                "error": "No autorizado"
            }
            return JsonResponse(error)
        else:
            return HttpResponseRedirect('/html5dicom/login')
    response_data_tables = requests.get(
        settings.HTTP_DICOM + '/datatables/patient?' + urllib.parse.urlencode(request.GET,
                                                                              quote_via=urllib.parse.quote))
    response = HttpResponse(response_data_tables.content,
                            status=response_data_tables.status_code,
                            content_type=response_data_tables.headers['Content-Type'])
    return response


def study_token_weasis(request, *args, **kwargs):
    if 'session' in request.GET:
        try:
            session = Session.objects.get(session_key=request.GET['session'],
                                          expire_date__gt=timezone.now())
            session.get_decoded()[SESSION_KEY]
            base_url = request.META['wsgi.url_scheme'] + '://' + request.META['HTTP_HOST']
            study_token = {
                "session": request.GET['session'],
                "institution": request.GET['institutionOID'],
                "proxyURI": base_url + '/html5dicom/wado',
                "accessType": 'weasis.xml',
            }
            # cache
            if 'cache' in request.GET:
                study_token['cache'] = request.GET['cache']
            # StudyInstanceUID
            if 'StudyInstanceUID' in request.GET:
                study_token['StudyInstanceUID'] = request.GET['StudyInstanceUID']
            # SeriesInstanceUID
            if 'SeriesInstanceUID' in request.GET:
                study_token['SeriesInstanceUID'] = request.GET['SeriesInstanceUID']
            response_study_token = requests.get(
                settings.HTTP_DICOM + '/studyToken?' + urllib.parse.urlencode(study_token, quote_via=urllib.parse.quote))
            response = HttpResponse(response_study_token.content, content_type='application/x-gzip')
            response['Content-Length'] = str(len(response_study_token.content))
            return response
        except (Session.DoesNotExist, KeyError):
            raise PermissionDenied
    else:
        return HttpResponse('Error', status=400)


def study_token_cornerstone(request, *args, **kwargs):
    if 'session' in request.GET:
        try:
            session = Session.objects.get(session_key=request.GET['session'],
                                          expire_date__gt=timezone.now())
            session.get_decoded()[SESSION_KEY]
            base_url = request.META['wsgi.url_scheme'] + '://' + request.META['HTTP_HOST']
            study_token = {
                "session": request.GET['session'],
                "institution": request.GET['institutionOID'],
                "proxyURI": base_url + '/html5dicom/wado',
                "accessType": 'cornerstone.json',
            }
            # cache
            if 'cache' in request.GET:
                study_token['cache'] = request.GET['cache']
            # StudyInstanceUID
            if 'StudyInstanceUID' in request.GET:
                study_token['StudyInstanceUID'] = request.GET['StudyInstanceUID']
            # SeriesInstanceUID
            if 'SeriesInstanceUID' in request.GET:
                study_token['SeriesInstanceUID'] = request.GET['SeriesInstanceUID']
            response_study_token = requests.get(
                settings.HTTP_DICOM + '/studyToken?' + urllib.parse.urlencode(study_token,
                                                                              quote_via=urllib.parse.quote))
            response = HttpResponse(response_study_token.content,
                                    status=response_study_token.status_code,
                                    content_type=response_study_token.headers['Content-Type'])
            return response
        except (Session.DoesNotExist, KeyError):
            raise PermissionDenied
    else:
        return HttpResponse('Error', status=400)


def study_token_zip(request, *args, **kwargs):
    if 'session' in request.GET:
        try:
            session = Session.objects.get(session_key=request.GET['session'],
                                          expire_date__gt=timezone.now())
            session.get_decoded()[SESSION_KEY]
            base_url = request.META['wsgi.url_scheme'] + '://' + request.META['HTTP_HOST']
            study_token = {
                "session": request.GET['session'],
                "institution": request.GET['institutionOID'],
                "proxyURI": base_url + '/html5dicom/wado',
                "accessType": 'dicom.zip',
            }
            # cache
            if 'cache' in request.GET:
                study_token['cache'] = request.GET['cache']
            # StudyInstanceUID
            if 'StudyInstanceUID' in request.GET:
                study_token['StudyInstanceUID'] = request.GET['StudyInstanceUID']
            # SeriesInstanceUID
            if 'SeriesInstanceUID' in request.GET:
                study_token['SeriesInstanceUID'] = request.GET['SeriesInstanceUID']
            url_zip = settings.HTTP_DICOM + '/studyToken?' + urllib.parse.urlencode(study_token,
                                                                                    quote_via=urllib.parse.quote)
            r = StreamingHttpResponse(stream_response(url_zip))
            r['Content-Type'] = "application/zip"
            r['Content-Disposition'] = "attachment; filename=dcm.zip"
            return r
        except (Session.DoesNotExist, KeyError):
            raise PermissionDenied
    else:
        return HttpResponse('Error', status=400)


def cornerstone(request, *args, **kwargs):
    return render(request,
                  template_name='html5dicom/redirect_cornerstone.html',
                  context={'url_manifiest': request.build_absolute_uri(
                      reverse('study_token_cornerstone') + '?' + urllib.parse.urlencode(request.GET))})


def stream_response(url_zip):
    r = requests.get(url_zip, stream=True)
    for chunk in r.iter_content(512 * 1024):
        yield chunk


def wado(request, *args, **kwargs):
    if 'session' in request.GET:
        try:
            session = Session.objects.get(session_key=request.GET['session'],
                                          expire_date__gt=timezone.now())
            session.get_decoded()[SESSION_KEY]
            url_request = request.build_absolute_uri()
            url_wado = settings.OID_URL[request.GET['arcId']]['wadouri'] + url_request[url_request.index("?"):]
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
