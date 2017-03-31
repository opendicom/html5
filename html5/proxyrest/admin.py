from django.contrib import admin
from proxyrest import models


class SessionRestAdmin(admin.ModelAdmin):
    list_display = ['sessionid', 'start_date', 'expiration_date']

admin.site.register(models.SessionRest, SessionRestAdmin)
