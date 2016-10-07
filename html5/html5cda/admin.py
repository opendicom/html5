from django.contrib import admin
from html5cda import models


class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    search_fields = ['key']

admin.site.register(models.Configuracion, ConfiguracionAdmin)


class EstudioAdmin(admin.ModelAdmin):
    list_display = ['id', 'modalidad', 'fkcode']
    search_fields = ['modalidad']
    raw_id_fields = ('fkcode',)

admin.site.register(models.Estudio, EstudioAdmin)


class CodesystemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'oid']
    search_fields = ['name', 'oid']

admin.site.register(models.Codesystem, CodesystemAdmin)


class CodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'fkcodesystem', 'code', 'displayname']
    search_fields = ['name', 'oid']
    list_select_related = True # para busacar la fk en listbox
    #raw_id_fields = ('fkcodesystem',) # para buscar la fk en popup de busaueda
    list_filter = ('fkcodesystem',) # habilita los filtros al costado derecho
    #list_filter = (('fkcodesystem', admin.RelatedOnlyFieldListFilter),) #muestra solo los que tengan relacion

admin.site.register(models.Code, CodeAdmin)


class ArticlehtmlAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'descripcion', 'html']
    search_fields = ['titulo', 'descripcion']

admin.site.register(models.Articlehtml, ArticlehtmlAdmin)


class SeccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'templateuidroot', 'ordinal']
    search_fields = ['ordinal']

admin.site.register(models.Seccion, SeccionAdmin)
