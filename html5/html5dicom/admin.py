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
    list_display = ['name', 'user', 'institution', 'service', 'default', 'max_rows']
    raw_id_fields = ('user',)
    list_filter = ('name',)
    search_fields = ['user__username']


admin.site.register(models.Role, RoleAdmin)


class AlternateAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


admin.site.register(models.Alternate, AlternateAdmin)


class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')


admin.site.register(models.Setting, SettingAdmin)


class UserChangePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'changepassword', 'create_date', 'last_update')


admin.site.register(models.UserChangePassword, UserChangePasswordAdmin)


class UserViewerSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'viewer')


admin.site.register(models.UserViewerSettings, UserViewerSettingsAdmin)
