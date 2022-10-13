from django.contrib import admin
from web.models import *


class CourseAdmin(admin.ModelAdmin):
    list_filter = ('subject', 'board_name', 'grade','type', 'language')
    list_display = ['id', 'board_name', 'subject', 'grade', 'type','description','picture','get_topics', 'language']
    ordering = ['id']

class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description','type']
    ordering = ['id']

class UserProfileAdmin(admin.ModelAdmin):
    #list_filter = ('pref_roles', 'country', 'state', 'city', 'pref_subjects')
    search_fields = ["phone","skype_id"]
    list_filter = ('user', )
    list_display = ['user', 'skype_id', 'pref_medium', 'phone', 'roles', 'age' , 'time_zone', 'country', 'state', 'city', 'from_date', 'to_date', 'pref_days', 'pref_slots', 'pref_subjects','get_pref_offerings']
    ordering = ['id']

class StackTeacherAdmin(admin.ModelAdmin):
    list_display = ['offering','teacher','status']
    ordering = ['id']

class TopicAdmin(admin.ModelAdmin):
    list_filter = ('course_id',)
    list_display = ['title', 'course_id', 'url','status','priority']
    ordering = ['priority']

class CenterAdmin(admin.ModelAdmin):
    list_display = ['name', "language", 'state','district','village', 'admin','photo','description','status', 'funding_partner', 'delivery_partner', 'board','field_coordinator','delivery_coordinator','HM', 'program_type']
    ordering = ['id']

class StudentAdmin(admin.ModelAdmin):
    list_filter = ('center',)
    search_fields = ["name", "phone"]
    list_display = ['name', 'dob', 'center','gender','grade', 'phone', 'father_occupation', 'mother_occupation', 'strengths', 'weakness', 'observation','status','school_rollno',]
    ordering = ['id']

class SessionAdmin(admin.ModelAdmin):
    list_filter = ('offering',)
    list_display = ['date_start', 'date_end','offering', 'teacher', 'comments','cancel_reason','created_by','updated_by']
    ordering = ['id']

class OfferingAdmin(admin.ModelAdmin):
    list_filter = ('course', 'center')
    list_display = ['course', 'center', 'academic_year','start_date','end_date', 'get_planned_topics', 'get_actual_topics','status','language','course_type','created_date','updated_date','created_by','updated_by']
    ordering = ['id']

class SessionAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student','session','is_present']
    ordering = ['id']

class DonationAdmin(admin.ModelAdmin):
    list_display = ['donation_type', 'name', 'email', 'phone', 'reference', 'channel', 'status', 'duplicate', 'num_students', 'num_subjects', 'num_classrooms', 'num_centers', 'num_months', 'honorary_name', 'area_of_donation']
    ordering = ['id']

class TopicDetailsAdmin(admin.ModelAdmin):
    list_display = ['topic','attribute','url','drafturl','types','status','author','last_updated_date','updated_by']
    ordering = ['id']

class AttributeAdmin(admin.ModelAdmin):
    list_display = ['types']
    ordering = ['id']

class AyfyAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'board', 'start_date', 'end_date', 'types', 'is_current']
    ordering = ['id']

class TrainingAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'content_type', 'url']
    ordering = ['id']

class TrainingStatusAdmin(admin.ModelAdmin):
    list_display = ['training', 'user', 'status', 'date_completed']
    ordering = ['id']

class CalenderAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'description', 'academic_year']
    ordering = ['id']
    list_filter = ('board','academic_year')

class HolidayAdmin(admin.ModelAdmin):
    list_display = ['day', 'description', 'calender']
    ordering = ['id']

class SlotAdmin(admin.ModelAdmin):
    list_display = ['center_id', 'slot', 'user' ,'avail_from','select_offer']
    ordering = ['id']



class LRCategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name',]
    ordering = ['id']

class ScholasticAdmin(admin.ModelAdmin):
    list_display = ['id','total_marks', 'obtained_marks','learning_record','category']
    ordering = ['id']

class CoScholasticAdmin(admin.ModelAdmin):
    list_display = ['id','learning_record', 'pr_curious', 'pr_attentiveness', 'pr_self_confidence']
    ordering = ['id']

class ActivityAdmin(admin.ModelAdmin):
    list_display = ['id','learning_record', 'notes','grading']
    ordering = ['id']

class UniqueCAdmin(admin.ModelAdmin):
    list_display = ['id','learning_record','strengths','weaknesses']
    ordering = ['id']

class TermAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','start_date', 'end_date', 'status']
    ordering = ['id']

class DiagnosticAdmin(admin.ModelAdmin):
    list_filter = ('offering',)
    list_display = ['id', 'student', 'offering','grade','subject','date_created','aggregate_level', 'category']
    ordering = ['id']

class DiagParameterAdmin(admin.ModelAdmin):
    list_filter = ('subject',)
    list_display = ['id','subject', 'grade','param_code', 'name','level','total_marks','version' ]
    ordering = ['id']

class DiagDetailsAdmin(admin.ModelAdmin):
    list_display =  ['id', 'parameter', 'diagnostic', 'actual_marks']
    ordering = ['id']

class LearningRecordAdmin(admin.ModelAdmin):
    list_filter = ('category','created_by','offering')
    list_display = ['id', 'student', 'offering', 'category', 'date_created', 'created_by','attachment', 'remarks' ]
    ordering = ['id']

class  DemandslotAdmin(admin.ModelAdmin):
    list_filter = ('center','day','user')
    list_display = ['id', 'center', 'day', 'start_time', 'end_time', 'user','offering', 'status', 'date_booked']
    ordering = ['id']

class  ProvisionalDemandslotAdmin(admin.ModelAdmin):
    list_filter = ('center','day','user')
    list_display = ['id', 'center', 'day', 'start_time', 'end_time', 'user','offering', 'status', 'date_booked', 'user_pref']
    ordering = ['id']

class ProgressReportAdmin(admin.ModelAdmin):
    list_filter = ['generated_date']
    list_display = ['id','student','generated_date','report_card']
    ordering = ['id']


class OnboardingStepAdmin(admin.ModelAdmin):
    list_display = ['id','role','stepname','description','weightage', 'order', 'prerequisite', 'repeatable']
    ordering = ['id']

class RolePreferenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'userprofile', 'role', 'role_onboarding_status', 'role_outcome', 'hrs_contributed', 'role_status', 'updated_by', 'date_updated', 'notes']
    ordering = ['id']

class OnboardingStepStatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'role_preference', 'step','status', 'date_completed']
    ordering = ['id']

class SelfEvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'userp', 'role_preference','se_form', 'date_submited']
    ordering = ['id']

class EventRegistrationAdmin(admin.ModelAdmin):
    ordering = ['id']

class SelectionDiscussionSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'userp', 'tsd_panel_member', 'booked_date', 'start_time', 'end_time', 'status', 'outcome']
    ordering = ['id']

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment', 'dueDate', 'priority', 'reminderText', 'reminderUrl', 'subject', 'taskCreatedDate','taskFor','taskStatus','taskUpdatedDate','performedOn_userId','assignedTo','contactId','taskCreatedBy_userId','taskUpdatedBy_userId','autoGeneratedTask','taskUpdatedBy_userId','user_date_joined','taskType','task_other_status']
    ordering = ['id']
    
class SelectionDiscussionSlotHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'slot', 'userp', 'booked_date', 'released_date', 'status', 'reason_to_release']
    ordering = ['id']

class AwardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    ordering = ['id']

class AwardDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'offering', 'teacher', 'award', 'date_created', 'modified_date', 'modified_by', 'status']
    ordering = ['id']
    
class SettingAdmin(admin.ModelAdmin):
    list_display = ['id','name','duration']
    ordering = ['id']
    
class MailingListAdmin(admin.ModelAdmin):
    list_display = ['id','name','email_id','volunteer_id']
    ordering = ['id']
    
class UserActivityHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'username', 'name', 'activity_date_time', 'activity_name', 'last_login', 'activity_type','activity_type_id','created_date','updated_date','created_by','updated_by']
    ordering = ['id']
    
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ['id','activity_type']
    ordering = ['id']
    
class SystemTaskHistoryAdmin(admin.ModelAdmin):
    list_display = ['id','user_id','task_id','type']
    ordering = ['id']

class SchoolAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    ordering = ['id']

class PartnerAdmin(admin.ModelAdmin):
    list_display = ['contactperson', 'name', 'name_of_organization', 'email', 'phone', 'status']
    ordering = ['id']

class ReferenceChannelAdmin(admin.ModelAdmin):
    list_filter = ('partner',)
    list_display = ['name', 'partner']
    ordering = ['id']

class PartnertypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    ordering = ['id']
    
class SessionRatingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_rated', 'updated_date', 'question', 'no_of_stars', 'created_date', 'question_no', 'user_id', 'created_by', 'updated_by', 'session_id']
    ordering = ['id']
    
class TaskRejectedAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment', 'dueDate', 'priority', 'reminderText', 'reminderUrl', 'subject', 'taskCreatedDate','taskFor','taskStatus','performedOn_userId','assignedTo','contactId','taskCreatedBy_userId','autoGeneratedTask','user_date_joined','taskType','task_other_status']
    ordering = ['id']

class VolunteerProcessingAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'role', 'status', 'outcome' ,'last_outcome', 'created_by', 'modified_by', 'dt_added', 'dt_updated', 'last_updated', 'update_counter']
    ordering = ['id']
    
class SubTopicsAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'topic', 'created_date', 'updated_date','author_id','created_by','updated_by','status']

class MySchoolAdmin(admin.ModelAdmin):
    list_display = ['id','partner', 'school', 'status', 'added_by', 'added_on','updated_by','updated_on','remarks']

class DeliveryPartnerOrgDetailsAdmin(admin.ModelAdmin):
    list_display = ['id','partner', 'type_of_org', 'website_address', 'office_phone', 'authorized_signatory','date_of_reg','place_of_reg','reg_number','number','fcra_reg_number','fcra_acc_number','bank_name','ifsc_code','acc_holder_name','acc_number','type_of_acc','dt_added','dt_updated']

class RubaruRegistrationAdmin(admin.ModelAdmin):
        list_display = ['id','name', 'designation', 'email', 'organization', 'allergies','comment','created_date']
        
class VolOfMonthAdmin(admin.ModelAdmin):
    list_display = ['id','elected_user', 'category', 'writeup', 'month', 'year','status','added_by','added_on','updated_by','updated_on']

class OfferingTeacherMappingAdmin(admin.ModelAdmin):
    list_display = ['id','offering','teacher','demand_slot_id','booked_date','confirmation_date','assigned_date','dropped_date','dropped_reason','created_date','created_by','updated_date','updated_by']

class VideoAssignmentsAdmin(admin.ModelAdmin):
    list_display = ['board_name','grade','subject','topic','video_url','status','added_by','added_on','updated_by','updated_on']

class DigitalCenterStaffAdmin(admin.ModelAdmin):
    search_fields = ["user__username","digital_school__name"]
    list_display = ['id','user','center','digital_school','role','status','created_by','created_on','updated_by']

class DigitalSchoolAdmin(admin.ModelAdmin):
    search_fields = ["name","partner_owner__name"]
    list_display = ['name','partner_owner','status','address_line_1','street','taluk','district','state','pin_code']

class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['file_name','doc_type','source','doc_format','status','belongs_to_object','created_by','created_on','updated_by','updated_on']

class CourseProviderAdmin(admin.ModelAdmin):
    search_fields = ["name","type","code"]
    list_display = ['id','name','type','code','status','language_code']

class SystemSettingsAdmin(admin.ModelAdmin):
    search_fields = ["key","value"]
    list_display = ['key','value','status',"created_by","created_on"]

class CourseAttributesAdmin(admin.ModelAdmin):
    search_fields = ["course__subject","key","value"]
    list_display = ["course",'key','value','status',"created_by","created_on"]

class WorkstreamTypeAdmin(admin.ModelAdmin):
    search_fields = ["name","code"]
    list_display = ["name",'code','status',"created_by","created_on"]

class ContentTypeMasterAdmin(admin.ModelAdmin):
    search_fields = ["name","code"]
    list_display = ["name",'code','status',"created_by","created_on"]

class ContentHostMasterAdmin(admin.ModelAdmin):
    search_fields = ["name","code"]
    list_display = ["name",'code','status',"created_by","created_on"]

class MetaAttributeTypeAdmin(admin.ModelAdmin):
    search_fields = ["name","code"]
    list_display = ["name",'code','status',"workstream_type","created_by","created_on"]

class ContentAuthorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name",'user','status',"created_by","created_on"]

class ContentDetailAdmin(admin.ModelAdmin):
    search_fields = ["topic__title","subtopic__name","name","url"]
    list_display = ["get_topicId","get_subtopicId","topic",'subtopic','url','name','description','status',"workstream_type",'url_host',"content_type","author","priority","version","duration","is_primary","created_by","created_on","updated_by","updated_on"]

    def get_topicId(self, obj):
        return obj.topic.id
    get_topicId.short_description = 'Topic Id'

    def get_subtopicId(self, obj):
        return obj.subtopic.id
    get_subtopicId.short_description = 'Subtopic Id'

class ContentMetaAttributeAdmin(admin.ModelAdmin):
    search_fields = ["content_detail__name", "key", "value"]
    list_display = ["content_detail","key", 'value', 'status', "meta_attribute_type","created_by", "created_on"]


class TttinfoAdmin(admin.ModelAdmin):
    search_fields = ['subject', 'chapter_name']
    list_display = ['state', 'student_class', 'subject', 'chapter_name', 'date', 'chanel']
    ordering = ['-date']
    list_filter = ('date', 'chanel','student_class','subject','state' )


class FaqAdmin(admin.ModelAdmin):
    search_fields = ['question']
    list_display = ['category', 'question', 'answer', 'parent_faq', 'language', 'status']
    ordering = ['category']
    list_filter = ('category','language')

    class Media:
        js = ('web/admin/faqadminform.js',)

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        if obj.created_by:
            obj.updated_by = request.user
        obj.save()
        
class AlertUsersAdmin(admin.ModelAdmin):
    search_fields = ['role__name', 'user__first_name', 'user__first_name']
    list_display = ['role', 'is_active', 'created_by']
    list_filter = ('role', 'is_active')

class OfferingEnrolledStudentsHistoryAdmin(admin.ModelAdmin):
    search_fields = ['offering__id', 'student__id']
    list_display = ['offering', 'student', 'assignment_status', 'created_by', 'updated_by', "created_on", "updated_on"]
    list_filter = ('assignment_status', 'offering__id')
class CenterActivityTypeFormInline(admin.TabularInline):
    model = CenterActivityTypeForm
    #fields = ('activity_type', 'label', 'type')
    raw_id_fields = ('created_by', 'updated_by')
    readonly_fields = ('created_by', 'created_on', 'updated_by', 'updated_on')


class CenterActivityTypesAdmin(admin.ModelAdmin):
    search_fields = ['activity_type']
    raw_id_fields = ('created_by', 'updated_by')
    list_display = ['activity_type', "created_by", "created_on", "updated_by", "updated_on"]
    readonly_fields = ('created_by', 'created_on', 'updated_by', 'updated_on')
    #list_filter = ('role', 'is_active')
    inlines = [
        CenterActivityTypeFormInline,
    ]

    def save_formset(self, request, form, formset, change):
        try:
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            for obj in instances:
                if obj.created_by:
                    obj.updated_by = request.user
                    obj.updated_on = datetime.datetime.now()
                else:
                    obj.created_by = request.user
                    obj.created_on = datetime.datetime.now()

                obj.save()
            formset.save_m2m()
        except Exception as exc:
            print("Error", exc)

    def save_model(self, request, obj, form, change):
        try:
            if change:
                obj.updated_by = request.user
                obj.updated_on = datetime.datetime.now()
            else:
                obj.created_by = request.user
                obj.created_on = datetime.datetime.now()
            obj.save()
        except Exception as exc:
            print("Error", exc)

class CenterActivityAdmin(admin.ModelAdmin):
    search_fields = ['center', "get_activity"]
    list_display = ['center', "user", "get_activity", "comment", "created_by", "created_on", "updated_by", "updated_on"]
    raw_id_fields = ('created_by', 'updated_by', 'user')
    readonly_fields = ('created_by', 'created_on', 'updated_by', 'updated_on')

    def get_activity(self, obj):
        return obj.activity.activity_type
    get_activity.short_description = 'Activity'  #Renames column head
    get_activity.admin_order_field  = 'activity'  #Allows column order sorting

    def save_formset(self, request, form, formset, change):
        try:
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            for obj in instances:
                if obj.created_by:
                    obj.updated_by = request.user
                    obj.updated_on = datetime.datetime.now()
                else:
                    obj.created_by = request.user
                    obj.created_on = datetime.datetime.now()

                obj.save()
            formset.save_m2m()
        except Exception as exc:
            print("Error", exc)

    def save_model(self, request, obj, form, change):
        try:
            if change:
                obj.updated_by = request.user
                obj.updated_on = datetime.datetime.now()
            else:
                obj.created_by = request.user
                obj.created_on = datetime.datetime.now()
            obj.save()
        except Exception as exc:
            print("Error", exc)


class Content_DemandAdmin(admin.ModelAdmin):
    search_fields = ['topic__id', 'subtopic__id']
    list_display = ['topic', 'subtopic', 'workstream', 'content_type', 'status', "created_on", "reviewer", 'url', 'due_date', 'comment']
    list_filter = ('workstream', 'content_type')


admin.site.register(CourseAttribute, CourseAttributesAdmin)
admin.site.register(WorkStreamType, WorkstreamTypeAdmin)
admin.site.register(ContentTypeMaster, ContentTypeMasterAdmin)
admin.site.register(ContentHostMaster, ContentHostMasterAdmin)
admin.site.register(ContentMetaAttributeType, MetaAttributeTypeAdmin)
admin.site.register(ContentAuthor, ContentAuthorAdmin)
admin.site.register(ContentDetail, ContentDetailAdmin)
admin.site.register(ContentMetaAttribute, ContentMetaAttributeAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Center, CenterAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Offering, OfferingAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(StackTeacher, StackTeacherAdmin)
admin.site.register(SessionAttendance, SessionAttendanceAdmin)
admin.site.register(Donation, DonationAdmin)
admin.site.register(TopicDetails, TopicDetailsAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Ayfy, AyfyAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(TrainingStatus, TrainingStatusAdmin)
admin.site.register(Calender, CalenderAdmin)
admin.site.register(Holiday, HolidayAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(LRCategory, LRCategoryAdmin)
admin.site.register(Scholastic, ScholasticAdmin)
admin.site.register(CoScholastic, CoScholasticAdmin)
admin.site.register(Activity,ActivityAdmin)
admin.site.register(UniqueC, UniqueCAdmin)
admin.site.register(Term,TermAdmin )
admin.site.register(Diagnostic, DiagnosticAdmin)
admin.site.register(DiagParameter, DiagParameterAdmin)
admin.site.register(DiagDetails, DiagDetailsAdmin)
admin.site.register(LearningRecord, LearningRecordAdmin)
admin.site.register(Demandslot, DemandslotAdmin)
admin.site.register(ProvisionalDemandslot, ProvisionalDemandslotAdmin)
admin.site.register(ProgressReport, ProgressReportAdmin)

admin.site.register(OnboardingStep, OnboardingStepAdmin)
admin.site.register(OnboardingStepStatus, OnboardingStepStatusAdmin)
admin.site.register(RolePreference, RolePreferenceAdmin)
admin.site.register(SelfEvaluation, SelfEvaluationAdmin)

admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(SelectionDiscussionSlot, SelectionDiscussionSlotAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(SelectionDiscussionSlotHistory, SelectionDiscussionSlotHistoryAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(AwardDetail, AwardDetailAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(MailingList, MailingListAdmin)
admin.site.register(UserActivityHistory, UserActivityHistoryAdmin)
admin.site.register(ActivityType, ActivityTypeAdmin)
admin.site.register(SystemTaskHistory, SystemTaskHistoryAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(ReferenceChannel, ReferenceChannelAdmin)
admin.site.register(Partnertype, PartnertypeAdmin)
admin.site.register(SessionRatings, SessionRatingsAdmin)
admin.site.register(TaskRejected, TaskRejectedAdmin)
admin.site.register(VolunteerProcessing, VolunteerProcessingAdmin)
admin.site.register(SubTopics, SubTopicsAdmin)
admin.site.register(MySchool, MySchoolAdmin)
admin.site.register(DeliveryPartnerOrgDetails, DeliveryPartnerOrgDetailsAdmin)
admin.site.register(RubaruRegistration,RubaruRegistrationAdmin)
admin.site.register(VolOfMonth,VolOfMonthAdmin)
admin.site.register(OfferingTeacherMapping,OfferingTeacherMappingAdmin)
admin.site.register(VideoAssignments,VideoAssignmentsAdmin)
admin.site.register(DigitalCenterStaff,DigitalCenterStaffAdmin)
admin.site.register(DigitalSchool, DigitalSchoolAdmin)
admin.site.register(UserDocument, UserDocumentAdmin)
admin.site.register(CourseProvider, CourseProviderAdmin)
admin.site.register(SystemSettings, SystemSettingsAdmin)
admin.site.register(Offering_enrolled_students)
admin.site.register(TvBroadCast, TttinfoAdmin)
admin.site.register(Faq, FaqAdmin)
admin.site.register(AlertUser, AlertUsersAdmin)
admin.site.register(Offering_Enrolled_Students_History, OfferingEnrolledStudentsHistoryAdmin)
admin.site.register(Content_Demand, Content_DemandAdmin)
admin.site.register(CenterActivityType, CenterActivityTypesAdmin)
admin.site.register(CenterActivity, CenterActivityAdmin)

