from django.contrib import admin
from html5cda import models


class EstudioAdmin(admin.ModelAdmin):
    list_display = ['id', 'modalidad', 'code']
    search_fields = ['modalidad']
    raw_id_fields = ('code',)

admin.site.register(models.Estudio, EstudioAdmin)


class CodesystemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'oid']
    search_fields = ['name', 'oid']

admin.site.register(models.Codesystem, CodesystemAdmin)


class CodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'codesystem', 'code', 'displayname']
    search_fields = ['name', 'oid']
    list_select_related = True # para busacar la fk en listbox
    #raw_id_fields = ('codesystem',) # para buscar la fk en popup de busaueda
    list_filter = ('codesystem',) # habilita los filtros al costado derecho
    #list_filter = (('codesystem', admin.RelatedOnlyFieldListFilter),) #muestra solo los que tengan relacion

admin.site.register(models.Code, CodeAdmin)


class ArticlehtmlAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'descripcion', 'html']
    search_fields = ['titulo', 'descripcion']

admin.site.register(models.Articlehtml, ArticlehtmlAdmin)


class SeccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'templateuidroot', 'ordinal']
    search_fields = ['ordinal']

admin.site.register(models.Seccion, SeccionAdmin)


admin.site.register(models.Header)
admin.site.register(models.Footer)
admin.site.register(models.Scriptelement)

class IntermediatePlantillaHeaderInline(admin.TabularInline):
    model = models.IntermediatePlantillaHeader
    extra = 1

class IntermediatePlantillaFooterInline(admin.TabularInline):
    model = models.IntermediatePlantillaFooter
    extra = 1

class IntermediateHeadScriptInline(admin.TabularInline):
    model = models.IntermediateHeadScript
    extra = 1

class IntermediateBodyScriptInline(admin.TabularInline):
    model = models.IntermediateBodyScript
    extra = 1

class PlantillaAdmin(admin.ModelAdmin):
    model = models.Plantilla
    inlines = (IntermediatePlantillaHeaderInline, IntermediatePlantillaFooterInline,
               IntermediateHeadScriptInline, IntermediateBodyScriptInline)
admin.site.register(models.Plantilla, PlantillaAdmin)
