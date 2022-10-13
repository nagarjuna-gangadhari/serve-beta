from django.contrib import admin
from .models import *

class CertificateAdmin(admin.ModelAdmin):
    search_fields = ["user__id", "ay__name"]
    list_display = ('user', 'center', 'sessions', 'ay',  'created_on', 'created_by')
    ordering = ['id']



admin.site.register(Certificate, CertificateAdmin)