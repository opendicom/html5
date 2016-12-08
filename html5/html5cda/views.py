from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from html5cda import models


@login_required(login_url='/html5dicom/login')
def editor(request, *args, **kwargs):
    context_user = {'context': 'ok'}
    return render(request, template_name='html5cda/editor.html', context=context_user)


def editor(request, *args, **kwargs):
    context_user = {'context': 'ok'}
    return render(request, template_name='html5cda/editor.html', context=context_user)


def help(request, *args, **kwargs):
    context_user = {'context': 'ok'}
    return render(request, template_name='html5cda/templates/help.html', context=context_user)


def about(request, *args, **kwargs):
    context_user = {'context': 'ok'}
    return render(request, template_name='html5cda/templates/about.html', context=context_user)


def viewport(request, *args, **kwargs):
    context_user = {'context': 'ok'}
    return render(request, template_name='html5cda/templates/viewport.html', context=context_user)


def studyViewer(request, *args, **kwargs):
    context_user = {'context': 'ok'}
    return render(request, template_name='html5cda/templates/studyViewer.html', context=context_user)
