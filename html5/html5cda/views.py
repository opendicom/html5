from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from html5cda import models
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string


@login_required(login_url='/html5dicom/login')
def editor(request, *args, **kwargs):
    modalidades = models.Estudio.objects.values('modalidad').annotate(Count('modalidad'))
    context_user = {'context': {'study': 'study',
                                'modalidades': modalidades }
                    }
    return render(request, template_name='html5cda/editor.html', context=context_user)


def viewport(request, *args, **kwargs):
    context_user = {'context': 'ok'}
    return render(request, template_name='html5cda/templates/viewport.html', context=context_user)


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
    for plantilla in models.Plantilla.objects.filter(estudio=request.GET['estudio']):
        template_list += [{
            'id': plantilla.id,
            'description': plantilla.title
        }]
    data = {"template_list": template_list}
    return JsonResponse(data)


def get_template(request, *args, **kwargs):
    secciones = models.Seccion.objects.filter(plantilla=request.GET['template']).order_by('ordinal')
    headscripts = models.IntermediateHeadScript.objects.filter(plantilla=request.GET['template'])
    bodyscripts = models.IntermediateBodyScript.objects.filter(plantilla=request.GET['template'])
    context_user = {'context': {'secciones': secciones,
                                'headscripts': headscripts,
                                'bodyscripts': bodyscripts
                    }}
    html = render_to_string('html5cda/editor_template.html', context_user)
    return HttpResponse(html)


def save_template(request, *args, **kwargs):
    print(request.POST)
    print(args)
    print(kwargs)
    return HttpResponse('ok')

