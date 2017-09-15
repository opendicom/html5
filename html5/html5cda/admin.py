from django.contrib import admin
from html5cda import models


class EstudioAdmin(admin.ModelAdmin):
    list_display = ['id', 'modalidad', 'code']
    search_fields = ['modalidad']
    raw_id_fields = ('code',)

admin.site.register(models.Estudio, EstudioAdmin)


class CodesystemAdmin(admin.ModelAdmin):
    list_display = ['id', 'shortname', 'oid']
    search_fields = ['shortname', 'oid']

admin.site.register(models.Codesystem, CodesystemAdmin)


class Code1Inline(admin.TabularInline):
    model = models.Code1
    extra = 1


class CodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'codesystem', 'code', 'displayname']
    search_fields = ['name', 'oid']
    list_select_related = True # para busacar la fk en listbox
    #raw_id_fields = ('codesystem',) # para buscar la fk en popup de busaueda
    list_filter = ('codesystem',) # habilita los filtros al costado derecho
    #list_filter = (('codesystem', admin.RelatedOnlyFieldListFilter),) #muestra solo los que tengan relacion
    inlines = (Code1Inline,)

admin.site.register(models.Code, CodeAdmin)


class Code2Inline(admin.TabularInline):
    model = models.Code2
    extra = 1


class Code1Admin(admin.ModelAdmin):
    inlines = (Code2Inline, )

admin.site.register(models.Code1, Code1Admin)


class Code3Inline(admin.TabularInline):
    model = models.Code3
    extra = 1


class Code2Admin(admin.ModelAdmin):
    inlines = (Code3Inline, )

admin.site.register(models.Code2, Code2Admin)


class ArticlehtmlAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'descripcion']
    search_fields = ['titulo', 'descripcion']

admin.site.register(models.Articlehtml, ArticlehtmlAdmin)


class ItemInline(admin.TabularInline):
    model = models.Item
    extra = 1


class ListAdmin(admin.ModelAdmin):
    inlines = (ItemInline, )

admin.site.register(models.List, ListAdmin)


class SelectOptionInline(admin.TabularInline):
    model = models.Selectoption
    extra = 1


class SectionAdmin(admin.ModelAdmin):
    list_display = ['idattribute', 'ordinal','plantilla']
    search_fields = ['idattribute', 'plantilla']
    list_filter = ('plantilla',)
    inlines = (SelectOptionInline,)

admin.site.register(models.Section, SectionAdmin)


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
