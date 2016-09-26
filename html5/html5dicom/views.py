from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from html5dicom import models


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
        institution_role_service = {}
        for role in models.Role.objects.filter(user=request.user.id):
            if role.institution is None:
                if role.service.institution in institution_role_service:
                    if role.get_name_display() in institution_role_service[role.service.institution]:
                        institution_role_service[role.service.institution][role.get_name_display()].append(role.service.name)
                    else:
                        institution_role_service[role.service.institution].update({role.get_name_display(): [role.service.name]})
                else:
                    institution_role_service.update({role.service.institution: {role.get_name_display(): [role.service.name]}})
            else:
                if role.institution in institution_role_service:
                    institution_role_service[role.institution].append({role.get_name_display(): []})
                else:
                    institution_role_service.update({role.institution: {role.get_name_display(): []}})
        context_user = {'roles': institution_role_service}
        return render(request, template_name='html5dicom/main.html', context=context_user)
