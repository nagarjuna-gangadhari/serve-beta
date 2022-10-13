from django.contrib import admin
from .models import *

class GuardianAdmin(admin.ModelAdmin):
    list_filter = ['full_name', 'mobile']
    search_fields = ['full_name','mobile']
    list_display = ['full_name', 'mobile', 'status','created_on','created_by']
    ordering = ['id']


class StudentGuardianRelationShipAdmin(admin.ModelAdmin):
    search_fields = ['guardian__full_name',"student__name"]
    list_display = ['student', 'guardian', 'relationship_type','is_primary_guardian','status','hasProvidedConsent','created_on','created_by']
    ordering = ['id']

class Student_School_EnrollmentAdmin(admin.ModelAdmin):
    search_fields = ["student__name"]
    list_display = ['student', 'digital_school', 'center','enrollment_status','enrolled_date','enrolled_by','created_on','created_by','start_date','end_date','payment_status']
    ordering = ['id']


class Student_Time_Table_Admin(admin.ModelAdmin):
    search_fields = ["student__name"]
    list_display = ['student', 'status','created_on','created_by']
    ordering = ['id']

class Student_Time_Table__SessionAdmin(admin.ModelAdmin):
    search_fields = ["timetable__id"]
    list_display = [ 'offering','topic','subtopic_ids','calDate','time_start','time_start','has_attended']
    ordering = ['id']

class Student_Study_Time_Preference_Admin(admin.ModelAdmin):
    search_fields = ["student__name"]
    list_display = ['student','day_of_the_week','time_start','time_end','status','created_on','created_by']
    ordering = ['id']

class Student_Content_View_Status_Admin(admin.ModelAdmin):
    search_fields = ["student__name"]
    list_display = ['student','content_detail','status','progress','number_of_times_viewed','has_understood','created_on','created_by']
    ordering = ['id']

class StudentDoubt_Admin(admin.ModelAdmin):
    search_fields = ["student__name"]
    list_display = ['student','subtopic','status','record_type','resource_type','text','resource_url','content_type','assigned_to','parent_thread']
    ordering = ['id']

class KycDetailsAdmin(admin.ModelAdmin):
    search_fields = ["student__name", "student__id"]
    list_display = ['student','doc_type','kyc_number','status']
    ordering = ['id']
class FLMClassTakenAdmin(admin.ModelAdmin):
    search_fields = ["offering__id", "teacher__id"]
    list_display = ('get_offering','teacher','comments','created_on','created_by')
    ordering = ['id']

    def get_offering(self, obj):
        return obj.offering.id 
    get_offering.short_description = 'Offering'
    get_offering.admin_order_field = 'offering'
    ordering = ['id']
class FLMClassAttendanceAdmin(admin.ModelAdmin):
    search_fields = ["flm_class__id", "offering__id"]
    list_display = ('flm_class','get_offering','get_student', 'status','created_on','created_by')
    ordering = ['id']

    def get_offering(self, obj):
        return obj.offering.id 
    get_offering.short_description = 'Offering'
    get_offering.admin_order_field = 'offering'

    def get_student(self, obj):
        return obj.student.id 
    get_student.short_description = 'Student'
    get_student.admin_order_field = 'student'
    
class Student_Promotion_HistoryAdmin(admin.ModelAdmin):
    search_fields = ["student__name","digital_school__name", 'center__name', 'center__id']
    list_display = ['student', 'from_grade', 'to_grade','promoted_by','promoted_on','created_by','created_on','updated_by','updated_on','ayfy','digital_school', 'center']
    ordering = ['id']

admin.site.register(Guardian, GuardianAdmin)
admin.site.register(Student_Guardian_Relation, StudentGuardianRelationShipAdmin)
admin.site.register(Student_School_Enrollment, Student_School_EnrollmentAdmin)
admin.site.register(Time_Table, Student_Time_Table_Admin)
admin.site.register(Time_Table_Session, Student_Time_Table__SessionAdmin)
admin.site.register(Content_View_Status, Student_Content_View_Status_Admin)
admin.site.register(Study_Time_Preference, Student_Study_Time_Preference_Admin)
admin.site.register(Doubt_Thread, StudentDoubt_Admin)
admin.site.register(KycDetails, KycDetailsAdmin)
admin.site.register(FLMClassTaken, FLMClassTakenAdmin)
admin.site.register(FLMClassAttendance, FLMClassAttendanceAdmin)
admin.site.register(Promotion_History, Student_Promotion_HistoryAdmin)
