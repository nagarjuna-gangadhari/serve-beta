from django.db import models
from web.models import *
from genutilities.models import *
from questionbank.models import *

# Create your models here.
from web.models import Ayfy, Student


class Guardian(models.Model):
    full_name = models.CharField(max_length=255, null=False, blank=False)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=255,choices=(('pending', 'Pending'),('active', 'Active'),('inactive', 'Inactive')), default="pending")
    address_line_1 = models.CharField(max_length=500, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    taluk = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    village = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='gu_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='gu_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    has_logged_in_once = models.BooleanField(default=False)
    first_logged_date = models.DateTimeField(null=True, blank=True)
    is_test_user = models.BooleanField(default=False)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=25,choices=(('1', 'DSM'), ('2', 'B2C'), ('3', 'Admin')),default="3")
    def __unicode__(self):
        return self.full_name

class Student_Guardian_Relation(models.Model):
    student = models.ForeignKey(Student, null=False)
    guardian = models.ForeignKey(Guardian, null=False)
    relationship_type = models.CharField(max_length=50,null=False,choices=(('mother','Mother'),('father','Father'),('guardian','Guardian')),default="guardian")
    is_primary_guardian = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    hasProvidedConsent = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, related_name='gu_su_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='gu_su_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Student Guardian Relation')
    def __unicode__(self):
        return self.relationship_type

class Student_School_Enrollment(models.Model):
    student = models.ForeignKey(Student, null=False)
    digital_school = models.ForeignKey(DigitalSchool, null=False)
    center = models.ForeignKey(Center, null=True)
    enrollment_status = models.CharField(max_length=255,choices=(('pending', 'Pending'),('active', 'Active'),('inactive', 'Inactive')), default="pending")
    enrolled_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    enrolled_by = models.ForeignKey(User, null=True, related_name='gu_sc_enrolled_by')
    created_by = models.ForeignKey(User, null=True, related_name='gu_sc_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='gu_sc_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    start_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    payment_status = models.CharField(max_length=255,choices=(('pending', 'Pending'),('free', 'Free'),('paid', 'Paid')), default="free")
    class Meta:
        verbose_name = ('Student School Enrollment')
    def __unicode__(self):
        return self.enrollment_status

class Time_Table(models.Model):
    student = models.ForeignKey(Student, null=True, related_name="stt_student_id")
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive'),('pending', 'Pending')), default="pending")
    generation_status = models.CharField(max_length=50, choices=(('1', 'Completed'), ('2', 'Inactive'), ('3', 'Pending'), ('4', 'In Progress')),default="3")
    source = models.CharField(max_length=50, choices=(('system', 'System'), ('student', 'Student')), default="system")
    type = models.CharField(max_length=50, default="academic")
    created_by = models.ForeignKey(User, null=True, related_name='stt_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='stt_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    subject_to_be_processed = models.CharField(max_length=500,null=True, blank=True)
    generation_type = models.CharField(max_length=50, choices=(('1', 'fresh'), ('2', 'regeneration'), ('3', 'complete')), default="1")
    class Meta:
        verbose_name = ('Student Time Table')
    def __unicode__(self):
        return self.generation_status

class Time_Table_Session(models.Model):
    timetable = models.ForeignKey(Time_Table, null=True, related_name="sts_time_table")
    offering = models.ForeignKey(Offering, null=True, related_name="sts_offering")
    topic = models.ForeignKey(Topic, null=True, related_name="sts_topic")
    subtopic_ids =  models.CharField(max_length=1024, null=True, blank=True)
    session = models.ForeignKey(Session, null=True, related_name="sts_session")
    session_type = models.CharField(max_length=50, choices=(('1', 'VideoClass'), ('2', 'Live')), default="1")
    time_start = models.IntegerField(default=1,null=True, blank=True)
    time_end = models.IntegerField(default=1,null=True, blank=True)
    calDate = models.DateField(null=True, blank=True)
    day_of_the_week = models.IntegerField(default=1,null=True, blank=True)
    has_attended = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, related_name='sts_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='sts_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = ('Student Time Table Session')
    def __unicode__(self):
        return self.subtopic_ids


class Content_Rating(models.Model):
    rating = models.FloatField()
    student = models.ForeignKey(Student, null=False,related_name='scr_student_id')
    subtopic = models.ForeignKey(SubTopics, null=True,blank=True,related_name='scr_subtopic_id')
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive')), default="active")
    created_by = models.ForeignKey(User, null=True, related_name='scr_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='scr_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    session = models.ForeignKey(Time_Table_Session, null=True, blank=True, related_name='scr_table_sess_id')

    class Meta:
        verbose_name = ('Student Content Rating')

    def __unicode__(self):
        return self.rating

class Study_Time_Preference(models.Model):
    student = models.ForeignKey(Student, null=False,related_name='stp_student_id')
    day_of_the_week = models.CharField(max_length=50, choices=(('1', 'Monday'), ('2', 'Tuesday'),('3', 'Wednesday'),('4', 'Thursday'),('5', 'Friday'),('6', 'Saturday'),('7', 'Sunday')), default="1")
    time_start = models.IntegerField(default=0)
    time_end = models.IntegerField(default=0)
    start_time_min = models.IntegerField(default=0)
    end_time_min = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive')), default="active")
    slot_type = models.CharField(max_length=50, choices=(('predefined', 'Predefined'), ('custom', 'Custom')), default="predefined")
    created_by = models.ForeignKey(User, null=True, related_name='stp_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='stp_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Student Study Time Preference')

    def __unicode__(self):
        return self.student.name



class Content_View_Status(models.Model):
    content_detail = models.ForeignKey(ContentDetail, null=False,blank=True,related_name='svs_content_id')
    status = models.CharField(max_length=50, choices=(('1', 'Viewed'), ('2', 'Pending'), ('3', 'Inprogress')), default="1")
    progress = models.IntegerField(default=0)
    has_understood = models.BooleanField(default=False)
    number_of_times_viewed = models.IntegerField(default=1)
    student = models.ForeignKey(Student, null=False,blank=True,related_name='svs_student_id')
    subtopic = models.ForeignKey(SubTopics, null=True, blank=True, related_name="svs_sub_topic")
    offering = models.ForeignKey(Offering, null=True, related_name="cvs_offering",blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='svs_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='svs_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    session = models.ForeignKey(Time_Table_Session, null=True, blank=True, related_name='tts_table_sess_id')

    class Meta:
        verbose_name = ('Student Content View Status')

    def __unicode__(self):
        return self.student.name


class Doubt_Thread(models.Model):
    student = models.ForeignKey(Student, null=False,blank=True,related_name='dt_student_id')
    session = models.ForeignKey(Time_Table_Session, null=True, related_name="dt_time_table")
    offering = models.ForeignKey(Offering, null=True, related_name="dt_offering",blank=True)
    topic = models.ForeignKey(Topic, null=True, related_name="dt_topic",blank=True)
    subtopic = models.ForeignKey(SubTopics, null=True, related_name="dt_sub_topic",blank=True)
    parent_thread = models.ForeignKey('self', null=True, related_name="dt_doubt_id",blank=True)
    status = models.CharField(max_length=50, choices=(('1', 'Open'), ('2', 'Resolved'),('3', 'Responded')), default="1")
    record_type = models.CharField(max_length=50, choices=(('1', 'Asked Doubt'), ('2', 'Teacher Response')), default="1")
    resource_type = models.CharField(max_length=50, choices=(('1', 'Text'), ('2', 'Image'),('3', 'Video'),('4', 'Audio'),('5', 'Url')),default="2")
    text = models.CharField(max_length=500, null=True, blank=True)
    resource_url = models.CharField(max_length=500, null=True, blank=True)
    resource_doc = models.ForeignKey(UserDocument, null=True,related_name='dt_kyc_document')
    content_type = models.ForeignKey(ContentTypeMaster, null=True, related_name="dt_content_type_id")
    assigned_to = models.ForeignKey(User, null=True, related_name='dt_assigned_to', blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='dt_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='dt_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Student Doubts')

    def __unicode__(self):
        return self.student.name


class Content_Download_History(models.Model):
    student = models.ForeignKey(Student, null=False, blank=True, related_name='dh_student_id')
    download_status = models.CharField(max_length=50, choices=(('1', 'Initiated'), ('2', 'Completed')),default="2")
    file_status = models.CharField(max_length=50,choices=(('1', 'downloaded'), ('2', 'deleted')), default="1")
    session = models.ForeignKey(Time_Table_Session, null=True, related_name="dh_time_table")
    offering = models.ForeignKey(Offering, null=True, related_name="dh_offering", blank=True)
    content_detail = models.ForeignKey(ContentDetail, null=True, related_name="dh_content_detail", blank=True)
    topic = models.ForeignKey(Topic, null=True, related_name="dh_topic", blank=True)
    subtopic = models.ForeignKey(SubTopics, null=True, related_name="dh_sub_topic", blank=True)
    device = models.ForeignKey(UserDevice, null=True, related_name="dh_device", blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='dh_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='dh_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return self.student.name

    class Meta:
        verbose_name = ('Student Content Download History')


class FLMClassTaken(models.Model):
    teacher = models.ForeignKey(User, null=True, related_name='flm_class_teacher', blank=True)
    offering = models.ForeignKey(Offering, null=True, related_name="flm_class_offering", blank=True)
    topic = models.ForeignKey(Topic, null=True, related_name="flm_class_topic", blank=True)
    subtopic = models.ManyToManyField(SubTopics, null=True, related_name="flm_class_subtopic", blank=True)
    status = models.CharField(max_length=50, choices=(('1', 'Active'), ('2', 'Inactive')), default="1")
    startTime = models.DateTimeField( null=True, blank=True)
    endTime = models.DateTimeField( null=True, blank=True)
    comments = models.CharField(max_length=1024, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='flm_class_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='flm_class_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return str(self.offering)

    class Meta:
        verbose_name = ('FLM Class Taken')


class FLMClassAttendance(models.Model):
    flm_class = models.ForeignKey(FLMClassTaken, null=True, related_name='flm_class_taken_ref', blank=True)
    offering = models.ForeignKey(Offering, null=True, related_name="flm_class_attend_offering", blank=True)
    status = models.CharField(max_length=50, choices=(('1', 'Active'), ('2', 'Inactive')), default="1")
    student = models.ForeignKey(Student, null=False, blank=True, related_name='flm_class_attend_student_id')
    created_by = models.ForeignKey(User, null=True, related_name='flm_class_attend_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='flm_class_attend_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return self.student.name

    class Meta:
        verbose_name = ('FLM class attendance')

class KycDetails(models.Model):
    student = models.ForeignKey(Student, null=False, blank=True, related_name='skd_student_id')
    doc_type = models.CharField(max_length=50, choices=(('1', 'Aadhar Card'), ('2', 'Passport'),('3', 'Ration Card'), ('4', 'Others')),default="1")
    kyc_number = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=50, choices=(('1', 'Active'), ('2', 'Inactive')),default="1")
    created_by = models.ForeignKey(User, null=True, related_name='skd_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='skd_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return self.student.name

    class Meta:
        verbose_name = ('Student KYC Details')


class FlmContentViewStatus(models.Model):
    content_detail = models.ForeignKey(ContentDetail, null=True, blank=True, related_name='flm_user_content_id')
    status = models.CharField(max_length=50, choices=(('1', 'Viewed'), ('2', 'Pending'), ('3', 'Inprogress')),default="1")
    progress = models.IntegerField(default=0)
    number_of_times_viewed = models.IntegerField(default=1)
    offering = models.ForeignKey(Offering, null=True, related_name="flm_user_offering", blank=True)
    user = models.ForeignKey(User, null=True, related_name='flm_user_auth_user', blank=True)
    topic = models.ForeignKey(Topic, null=True, blank=True, related_name="flm_user_topic")
    subtopic = models.ForeignKey(SubTopics, null=True, blank=True, related_name="flm_user_sub_topic")
    offering = models.ForeignKey(Offering, null=True, related_name="flm_user_offering", blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='flm_user_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='flm_user_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = ('FLM_Content_View_Status')

    def __unicode__(self):
        return self.user.id


class Promotion_History(models.Model):
    student = models.ForeignKey(Student, null=False, blank=True, related_name='promotion_history_student')
    ayfy = models.ForeignKey(Ayfy, null=False, blank=True, related_name='promotion_history_ayfy')
    from_grade = models.IntegerField(default=0)
    to_grade = models.IntegerField(default=0)
    digital_school = models.ForeignKey(DigitalSchool, null=True, blank=True)
    center = models.ForeignKey(Center, null=True, blank=True)
    promoted_by = models.ForeignKey(User, null=True, related_name='promotion_history_promoted_by', blank=True)
    promoted_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='promotion_history_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='promotion_history_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Promotion History')

    def __unicode__(self):
        return self.student.name

class Quiz_History(models.Model):
    student = models.ForeignKey(Student, null=False, blank=True, related_name='quiz_history_student')
    content_detail = models.ForeignKey(ContentDetail, null=True, related_name="quizh_content_detail_id",blank=True)
    question_set = models.ForeignKey(Question_Set, null=True, related_name="quizh_question_set_id")
    offering = models.ForeignKey(Offering, blank=True, null=True)
    attempt = models.IntegerField(default=1)
    total_points = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    result = models.IntegerField(choices=((1, 'Passed'), (2, 'Failed')), default=1)
    created_by = models.ForeignKey(User, null=True, related_name='quiz_history_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='quiz_history_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return self.student.name

    class Meta:
        verbose_name = ('Quiz History')

class Quiz_History_Detail(models.Model):
    quiz_history = models.ForeignKey(Quiz_History, null=False, blank=True, related_name='quiz_history_detail_id')
    question = models.ForeignKey(Question, null=True, related_name="quizh_question_id")
    points_earned = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    result = models.IntegerField(choices=((1, 'Passed'), (2, 'Failed')), default=1)
    answer_given = models.CharField(max_length=1024, null=True)
    created_by = models.ForeignKey(User, null=True, related_name='quiz_history_detail_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='quiz_history_detail_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return self.question.text

    class Meta:
        verbose_name = ('Quiz History Detail')

    

class Flm_Content_Rating(models.Model):
    videoRating = models.FloatField()
    worksheetRating = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    reviewer = models.ForeignKey(User, null=False,related_name='flm_reviewer_id')
    offering = models.ForeignKey(Offering, null=True, blank=True, related_name='flm_offering_id')
    subtopic = models.ForeignKey(SubTopics, null=True,blank=True,related_name='flm_subtopic_id')
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive')), default="active")
    created_by = models.ForeignKey(User, null=True, related_name='flm_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='flm_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = ('Flm Content Rating')

    def __unicode__(self):
        return self.subtopic.id

