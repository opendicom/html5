from django.contrib import admin
from html5dicom import models


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'oid')

admin.site.register(models.Organization, OrganizationAdmin)


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'oid', 'create_date', 'last_update']

admin.site.register(models.Institution, InstitutionAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'oid', 'institution', 'create_date', 'last_update']

admin.site.register(models.Service, ServiceAdmin)


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'institution', 'service', 'default']
    list_filter = ('name',)
    search_fields = ['user__username']

admin.site.register(models.Role, RoleAdmin)


class AlternateAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']

admin.site.register(models.Alternate, AlternateAdmin)


class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')

admin.site.register(models.Setting, SettingAdmin)