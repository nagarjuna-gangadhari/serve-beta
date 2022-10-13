from django.contrib import admin
from .models import *

class ApiSessionAdmin(admin.ModelAdmin):
    list_filter = ['user__username','session_key']
    list_display = ['user', 'session_key', 'status','expiry_time','created_on']
    ordering = ['id']


class StateAdmin(admin.ModelAdmin):
    list_filter = ['name','code']
    list_display = ['name', 'code', 'status','created_on']
    ordering = ['id']

class LanguageAdmin(admin.ModelAdmin):
    list_filter = ['name','code']
    list_display = ['name', 'code', 'status','created_on']
    ordering = ['id']

class PincodeAdmin(admin.ModelAdmin):
    search_fields = ['pincode','district','taluk','state__name']
    list_display = [ 'state_code', 'district','taluk','pincode','status']
    ordering = ['pincode']

admin.site.register(ApiSession, ApiSessionAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Language,LanguageAdmin)
admin.site.register(Pincode,PincodeAdmin)