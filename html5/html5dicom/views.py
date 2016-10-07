from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
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
        organization = {}
        for role in models.Role.objects.filter(user=request.user.id).order_by('default'):
            if role.institution:
                if role.institution.organization.short_name in organization:
                    if role.institution.short_name in organization[role.institution.organization.short_name]['institution']:
                        organization[role.institution.organization.short_name]['institution'][role.institution.short_name].update(
                            {role.get_name_display(): {"service": []}}
                        )
                    else:
                        url_httpdicom_req = url_httpdicom + '/orgts/' + role.institution.organization.short_name
                        url_httpdicom_req += '/aets/' + role.institution.short_name
                        oid_inst = requests.get(url_httpdicom_req)
                        organization[role.institution.organization.short_name]['institution'].update(
                            {role.institution.short_name: {'aet': role.institution.short_name, 'oid':
                                oid_inst.json()[0], role.get_name_display(): {"service": []}}}
                        )
                else:
                    url_httpdicom_req = url_httpdicom + '/orgts/' + role.institution.organization.short_name
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
                            organization[role.service.institution.organization.short_name]['institution'][role.service.institution.short_name].update({role.get_name_display(): {"service": [role.service.name]}})
                    else:
                        url_httpdicom_req = url_httpdicom + '/orgts/' + role.service.institution.organization.short_name
                        url_httpdicom_req += '/aets/' + role.service.institution.short_name
                        oid_inst = requests.get(url_httpdicom_req)
                        organization[role.service.institution.organization.short_name]['institution'].update(
                            {role.service.institution.short_name: {'aet': role.service.institution.short_name, 'oid':
                                oid_inst.json()[0], role.get_name_display(): {"service": []}}}
                        )
                else:
                    url_httpdicom_req = url_httpdicom + '/orgts/' + role.service.institution.organization.short_name
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
                                            "service": [role.service.name]
                                        }
                                    }
                                }
                            }
                    })
        context_user = {'organization': organization, 'httpdicom': url_httpdicom}
        return render(request, template_name='html5dicom/main.html', context=context_user)
