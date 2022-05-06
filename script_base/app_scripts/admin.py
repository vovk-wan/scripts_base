from django.contrib import admin
from django.utils.translation import gettext as _
from app_scripts.models import Status, Client, Script, License


class StatusAdmin(admin.ModelAdmin):
    pass
    # list_display = ['id', 'name', 'description']


class ClientAdmin(admin.ModelAdmin):
    pass
    # list_display = ['id', 'name', 'description']


class ScriptAdmin(admin.ModelAdmin):
    pass
    # list_display = ['id', 'name', 'description']


class LicenseAdmin(admin.ModelAdmin):
    pass
    # list_display = ['id', 'name', 'description']


admin.site.register(Status, StatusAdmin)

admin.site.register(Client, ClientAdmin)

admin.site.register(Script, ScriptAdmin)

admin.site.register(License, LicenseAdmin)
