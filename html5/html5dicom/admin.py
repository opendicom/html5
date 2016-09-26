from django.contrib import admin
from html5dicom import models


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'oid', 'create_date', 'last_update']

admin.site.register(models.Institution, InstitutionAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'oid', 'institution', 'create_date', 'last_update']

admin.site.register(models.Service, ServiceAdmin)


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'institution', 'service', 'create_date', 'last_update']

admin.site.register(models.Role, RoleAdmin)


class AlternateAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']

admin.site.register(models.Alternate, AlternateAdmin)
