from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from html5cda import models


@login_required(login_url='/html5dicom/login')
def editor(request, *args, **kwargs):
    context_user = {'context': 'ok'}
    return render(request, template_name='html5cda/editor.html', context=context_user)
