import traceback
import datetime
import urllib
import string
import random
import os

from django.db import models
#from django_facebook.models import FacebookProfileModel
from django.contrib.auth.models import User
from django.db.models import signals, ForeignKey
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.dispatch import receiver
from django.db.models import Q
from django.db import IntegrityError

import notification.models as notification

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend
from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends import google
from social_auth.signals import socialauth_registered
from django.template.defaultfilters import slugify
from partner.models import *
from webext.models import *
from genutilities.models import *

class Ayfy(models.Model):
    title = models.CharField(max_length=50)
    board = models.CharField(max_length=128,choices=(('APSB','APSB'),('TNSB','TNSB'),('DSERT','DSERT'),
                    ('NCERT','NCERT'),('MHSB','MHSB'),('WBSED','WBSED'), ('SCERT','SCERT'), ('OPEPA','OPEPA'),
                    ('UPMSP ','UPMSP '),('JACB','JACB'),('eVidyaloka ','eVidyaloka '),('BSEB','BSEB'),
                    ('UBSE','UBSE'),('GSEB','GSEB'),('JKBOSE','JKBOSE'),('CBSE','CBSE')), null=True, blank=True)
    start_date = models.DateTimeField(null=True,blank=True)
    end_date  =  models.DateTimeField(null=True,blank=True)
    types =  models.CharField(max_length=50,choices=(('Academic Year', 'Academic Year'), 
                    ('Financial Year', 'Financial Year')), default="Academic Year")
    is_current = models.BooleanField(default=True)
    def __unicode__(self):
        return  "%s - %s" %(self.title, self.board)
#-----------------------------------Calender-------------------------------#

class Calender(models.Model):
    name = models.CharField(max_length=128)
    board = models.CharField(max_length=128,choices=(('APSB','APSB'),('TNSB','TNSB'),('DSERT','DSERT'),
                    ('NCERT','NCERT'),('MHSB','MHSB'),('WBSED','WBSED'), ('SCERT','SCERT'), ('OPEPA','OPEPA'),
                    ('UPMSP ','UPMSP '),('JACB','JACB'), ('eVidyaloka ','eVidyaloka '),('BSEB','BSEB'),
                    ('UBSE','UBSE'),('GSEB','GSEB'),('JKBOSE','JKBOSE')))
    description = models.CharField(max_length=1024, blank=True, null=True)
    academic_year =  models.ForeignKey(Ayfy, limit_choices_to={'types': 'Academic Year'})
    def __unicode__(self):
        return  "%s" %(self.name)

class Holiday(models.Model):
    day = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=1024, blank=True, null=True )
    calender = models.ForeignKey(Calender)
    district=models.CharField(max_length=200,blank=True, null=True)
    center=models.CharField(max_length=200,blank=True, null=True)
    def __unicode__(self):
        return  "%s" %(self.day)

#----------------------------------End Calender----------------------------#


class Training(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(max_length=2048, null=True, blank=True)
    category = models.CharField(max_length=20,null=True,blank=True)
    url = models.CharField(max_length=1024,null=True,blank=True)
    content_type= models.CharField(max_length=256,choices=(('Html', 'Html'), ('Youtube Video', 'Youtube Video'),
                ('Pdf', 'Pdf')), default="Pdf")
    def __unicode__(self):
        return self.name

class TrainingStatus(models.Model):
    training = models.ForeignKey(Training)
    user = models.ForeignKey(User)
    date_completed = models.DateTimeField(null=True,blank=True)
    status = models.BooleanField()
    def __unicode__(self):
        value = ""
        if self.status ==1:
            value = "Completed"
        else:
            value = "Not Attended"
        return value


class Role(models.Model):
    name = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)
    type = models.CharField(max_length=30, blank=True)
    def __unicode__(self):
        return self.name

class CourseProvider(models.Model):
    name = models.CharField(max_length=1024, null=True, blank=True)
    type = models.CharField(max_length=256,choices=(('State', 'State'),
            ('centralboard','centralboard'), ('stateboard','stateboard'),
            ('evidyaloka','evidyaloka'), ('Other', 'Other')), default="State")
    code = models.CharField(max_length=1024, null=True, blank=True)
    language_code = models.CharField(max_length=1024, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, related_name='cp_created_by',blank=True)
    created_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='cp_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return self.name


class Course(models.Model):
    board_name = models.CharField(max_length=50,null=True, blank=True,db_index=True )
    subject = models.CharField(max_length=30,null=True, blank=True,db_index=True)
    grade = models.CharField(max_length=30,null=True, blank=False,db_index=True)
    type = models.CharField(max_length=30,null=True, blank=True,db_index=True)
    description = models.TextField(max_length=2048, null=True, blank=True)
    picture = models.FileField(upload_to='static/uploads/images', null=True, blank=True)
    status = models.CharField(max_length=50,choices=(('active', 'Active'), ('inactive', 'Inactive')),default="active")
    language = models.ForeignKey(Language, null=True, blank=True)
    availabilityType = models.CharField(max_length=50, choices=(('1', 'Web1.0 Only'), ('2', 'Mobile App only'),('3', 'All Platforms')), default="3")
    #age_group = models.CharField(max_length=30,null=True, blank=True)

    @property
    def topics():
        return Topics.objects.all()

    def get_topics(self):
        topics = self.topic_set.all()
        return ',<br/>'.join([unicode(t) for t in topics])

    get_topics.short_description = 'Topics'
    get_topics.allow_tags = True

    def __unicode__(self):
        # DONT CHANGE THIS FORMAT, PROVISIONALDEMAND SLOT DEPENDS ON IT (webext/views.py - def send_pd_booking_email)
        return "%s-%s-%s" % (self.board_name, self.subject, self.grade)

class Topic(models.Model):
    title = models.CharField(max_length=400)
    course_id = models.ForeignKey(Course,db_index=True)
    #chapter = models.CharField(max_length=50)
    url = models.CharField(max_length=1024, null=True, blank=True)
    num_sessions = models.IntegerField(default=1)
    status = models.CharField(max_length=256,choices=(('Not Started', 'Not Started'),
            ('In Progress', 'In Progress'), ('Partially Complete', 'Partially Complete'),
            ('Complete','Complete'), ('Inactive', 'Inactive')), default="Not Started")
    priority = models.IntegerField(default=0)
    def __unicode__(self):
        return self.title

class Attribute(models.Model):
    types = models.CharField(max_length=256,choices=(('TextBook', 'TextBook'), ('Lesson Plan', 'Lesson Plan'),
            ('Transliteration','Transliteration'),('Videos','Videos'), ('Pictures', 'Pictures'), 
            ('Activities', 'Activities'),('Worksheets','Worksheets'),('Assessments','Assessments'),
            ('PowerPoint','PowerPoint')))

    def __unicode__(self):
        return self.types

class TopicDetails(models.Model):
    topic = models.ForeignKey(Topic,db_index=True)
    attribute = models.ForeignKey(Attribute,db_index=True)
    url = models.CharField(max_length=1024, null=True, blank=True)
    types = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=256,choices=(('Not Started', 'Not Started'), ('Assigned', 'Assigned'),
            ('In Progress','In Progress'),('Draft','Draft'), ('In Review', 'In Review'), 
            ('Published', 'Published'), ('Inactive', 'Inactive')), default="Not Started")
    author = models.ForeignKey(User, null = True, blank=True,related_name="Author")
    last_updated_date = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(User, null = True, blank=True,related_name="Modified By")
    drafturl = models.CharField(max_length=2560, null=True, blank=True)

class School(models.Model):
    name                    = models.CharField(max_length=250,db_index=True)
    district_details        = models.CharField(max_length=250, null = True, blank=True)
    typeofmgmt              = models.CharField(max_length=250, null = True, blank=True)
    headmaster_incharge     = models.CharField(max_length=250, null = True, blank=True)
    contact_details         = models.CharField(max_length=250, null = True, blank=True)
    beo_name                = models.CharField(max_length=250, null = True, blank=True)
    grades_inschool         = models.CharField(max_length=50, null = True, blank=True)
    noofchildren            = models.IntegerField(default=0)
    current_teacher         = models.CharField(max_length=250, null = True, blank=True)
    school_number           = models.CharField(max_length=50, blank=True)
    photo                   = models.FileField(upload_to='static/uploads/school', null=True, blank=True)
    location_map            = models.CharField(max_length=1024, null = True, blank=True)
    ledtv_available         = models.CharField(max_length=3, blank=True)
    cpu_and_others          = models.CharField(max_length=3, blank=True)
    speakers_available      = models.CharField(max_length=3, blank=True)
    web_camera              = models.CharField(max_length=3, blank=True)
    ups_avail               = models.CharField(max_length=3, blank=True)
    modem_avail             = models.CharField(max_length=3, blank=True)
    software_installed      = models.CharField(max_length=3, blank=True)
    created_by              = models.ForeignKey(User, null=True, related_name="school_createdby")
    modified_by             = models.CharField(max_length=250, null = True, blank=True)
    dt_added                = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated              = models.DateTimeField(auto_now=True, null=True, blank=True)
    ref_url                 = models.CharField(max_length=1024, null = True, blank=True)
    school_academic_year    = models.CharField(max_length=250, null = True, blank=True)
    school_code             = models.BigIntegerField(default=0,db_index=True)
    state                   = models.CharField(max_length=250, null = True, blank=True)
    block                   = models.CharField(max_length=250, null = True, blank=True)
    cluster                 = models.CharField(max_length=250, null = True, blank=True)
    village                 = models.CharField(max_length=250, null = True, blank=True)
    principal               = models.CharField(max_length=250, null = True, blank=True)
    location                = models.CharField(max_length=50,choices=(('Rural', 'Rural'), ('Urban', 'Urban')), default="Rural")
    pincode                 = models.IntegerField(default=0,db_index=True)
    school_category         = models.CharField(max_length=250, null = True, blank=True)
    lowest_class            = models.IntegerField(default=0)
    highest_class           = models.IntegerField(default=0)
    type_of_school          = models.CharField(max_length=50,choices=(('Co-educational', 'Co-educational'), ('Boys', 'Boys'),('Girls', 'Girls')), default="Co-educational")
    management              = models.CharField(max_length=250, null = True, blank=True)
    approachable_by_all_weather_road = models.CharField(max_length=30, null = True, blank=True)
    year_of_establishment   = models.IntegerField(default=0)
    year_of_recognition     = models.IntegerField(default=0)
    year_of_upgradation_p_to_up = models.IntegerField(default=0)
    special_school_for_cwsn = models.CharField(max_length=30, null = True, blank=True)
    shift_school            = models.CharField(max_length=30, null = True, blank=True)
    residential_school      = models.CharField(max_length=30, null = True, blank=True) 
    type_of_residential_school = models.CharField(max_length=100, null = True, blank=True) 
    pre_primary_section     = models.CharField(max_length=100, null = True, blank=True) 
    total_students_pre_primary = models.IntegerField(default=0)
    total_teachers_pre_primary = models.IntegerField(default=0)
    academic_inspections    = models.IntegerField(default=0)
    no_of_visits_by_crc_coordinator = models.IntegerField(default=0)
    no_of_visits_by_block_level_officer = models.IntegerField(default=0)
    school_development_grant_receipt = models.IntegerField(default=0)
    school_development_grant_expenditure = models.IntegerField(default=0)
    school_maintenance_grant_receipt = models.IntegerField(default=0)
    school_maintenance_grant_expenditure = models.IntegerField(default=0)
    regular_Teachers = models.IntegerField(default=0)
    contract_teachers = models.IntegerField(default=0)
    graduate_or_above       = models.IntegerField(default=0)
    teachers_male           = models.IntegerField(default=0)
    teachers_female         = models.IntegerField(default=0)
    teachers_aged_above     = models.IntegerField(default=0)
    head_master             = models.CharField(max_length=100, null = True, blank=True)
    trained_for_teaching_cwsn = models.IntegerField(default=0)
    trained_in_use_of_computer = models.IntegerField(default=0)
    part_time_instructor    = models.IntegerField(default=0)
    teachers_involved_in_non_teaching_assignments = models.IntegerField(default=0)
    avg_working_days_spent_on_Non_tch_assignments = models.IntegerField(default=0)
    teachers_with_professional_qualification = models.IntegerField(default=0)
    teachers_received_inservice_training = models.IntegerField(default=0)
    medium_one              = models.CharField(max_length=100, null = True, blank=True)
    medium_two              = models.CharField(max_length=100, null = True, blank=True)
    medium_three            = models.CharField(max_length=100, null = True, blank=True)
    status_of_school_building = models.CharField(max_length=100, null = True, blank=True)
    boundary_wall           = models.CharField(max_length=100, null = True, blank=True)
    classrooms_for_teaching = models.IntegerField(default=0)
    furniture_for_students  = models.CharField(max_length=100, null = True, blank=True)
    number_of_other_rooms   = models.IntegerField(default=0)
    classrooms_in_good_condition = models.IntegerField(default=0)
    classrooms_require_minor_repair = models.IntegerField(default=0)
    classrooms_require_major_repair = models.IntegerField(default=0)
    separate_room_for_HM    = models.CharField(max_length=30, null = True, blank=True)
    electricity_connection  = models.CharField(max_length=30, null = True, blank=True)
    boys_toilet_seats_total = models.IntegerField(default=0)
    boys_toilet_seats_functional = models.IntegerField(default=0)
    girls_toilet_seats_total = models.IntegerField(default=0)
    girls_toilet_seats_functional = models.IntegerField(default=0) 
    cwsn_friendly_toilet    = models.CharField(max_length=30, null = True, blank=True)
    drinking_water_facility = models.CharField(max_length=30, null = True, blank=True)
    drinking_water_functional = models.CharField(max_length=30, null = True, blank=True)
    library_facility        = models.CharField(max_length=30, null = True, blank=True)
    no_of_books_in_school_library = models.IntegerField(default=0) 
    computer_aided_learning_lab = models.CharField(max_length=30, null = True, blank=True)
    playground_facility     = models.CharField(max_length=30, null = True, blank=True)
    land_available_for_playground = models.CharField(max_length=30, null = True, blank=True)
    no_of_computers_available = models.IntegerField(default=0) 
    no_of_computers_functional = models.CharField(max_length=30, null = True, blank=True)
    medical_check           = models.CharField(max_length=30, null = True, blank=True)
    ramp_for_disabled_needed = models.CharField(max_length=30, null = True, blank=True)
    ramp_available          = models.CharField(max_length=30, null = True, blank=True)
    hand_rails_for_ramp     = models.CharField(max_length=30, null = True, blank=True)
    classroom_required_major_repair = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    teachers_with_prof_qualification = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    muslim_girls_to_muslim_enrolment = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    repeaters_to_total_enrolment = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    change_in_enrolment_over_previous_year = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    sc_girls_to_sc_enrolment = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    st_girls_to_st_enrolment = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    pupil_teacher_ratio     = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    student_classroom_ratio = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    girls_enrolment         = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    muslim_students         = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    sc_students             = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    st_students             = models.DecimalField( max_digits=11, decimal_places=2,default=0)
    obc_enrolment           = models.DecimalField( max_digits=11, decimal_places=2,default=0)

    def __unicode__(self):
        return self.name

class UserDocument(models.Model):
    file_name  = models.CharField(max_length=255, null=True, blank=True)
    url =  models.CharField(max_length=1024, null=False, blank=False)
    doc_type = models.CharField(max_length=50, choices=(('kyc', 'kyc'), ('consent', 'consent'),('school_logo', 'school_logo'),('school_banner', 'school_banner'),('others', 'others')), default="others")
    source = models.CharField(max_length=50, choices=(('s3', 's3'), ('gdrive', 'gdrive'),('others', 'others')), default="others")
    doc_format = models.CharField(max_length=50, choices=(('png', 'png'), ('pdf', 'pdf'),('jpg', 'jpg'),('others', 'others')), default="others")
    belongs_to =  models.IntegerField(default=-1,null=True, blank=True)
    status = models.BooleanField()
    belongs_to_object =  models.CharField(max_length=255, null=False, blank=False)
    created_by = models.ForeignKey(User, null=True, related_name='document_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='document_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

class DigitalSchool(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    partner_owner = models.ForeignKey(Partner, related_name="partner_id", null=False)
    school_type = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=255,choices=(('Pending', 'Pending'),('Active', 'Active'),('Inactive', 'Inactive')), default="Pending")
    description = models.CharField(max_length=500, null=True, blank=True)
    address_line_1 = models.CharField(max_length=500, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    taluk = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    village = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=100, null=True, blank=True)
    logo_url = models.CharField(max_length=1024, null=True, blank=True)
    logo_doc = models.ForeignKey(UserDocument, null=True)
    org_legal_document_id = models.IntegerField(default=-1)
    org_legal_registration_number = models.CharField(max_length=255, null=True, blank=True)
    statement_of_purpose = models.CharField(max_length=500, null=True, blank=True)
    course_provider = models.ForeignKey(CourseProvider, null=True,related_name='ds_course_provider')
    course_provider_code = models.CharField(max_length=1024, null=True, blank=True)
    banner_url = models.CharField(max_length=1024, null=True, blank=True)
    banner_doc = models.ForeignKey(UserDocument, null=True,related_name='banner_document')
    created_by = models.ForeignKey(User, null=True, related_name='ds_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='ds_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    approved_on = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, null=True, related_name='ds_approved_by')
    is_test_school = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Center(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    district = models.CharField(max_length=30, null=True, blank=True)
    village = models.CharField(max_length=30, null=True, blank=True)
    language = models.CharField(max_length=256,choices=(('Bengali', 'Bengali'), ('Gujarathi', 'Gujarathi'),
                    ('Hindi', 'Hindi'), ('Kannada', 'Kannada'), ('Malayalam', 'Malayalam'), ('Marathi', 'Marathi'),
                    ('Oriya', 'Oriya'), ('Punjabi', 'Punjabi'),('Tamil', 'Tamil'), ('Telugu', 'Telugu'), 
                    ('Urdu', 'Urdu')), default='Telugu')
    board = models.CharField(max_length=128,choices=(('APSB','APSB'),('TNSB','TNSB'),('DSERT','DSERT'),
                    ('NCERT','NCERT'),('MHSB','MHSB'),('WBSED','WBSED'), ('SCERT','SCERT'), ('OPEPA','OPEPA'),
                    ('UPMSP ','UPMSP '),('JACB ','JACB '), ('eVidyaloka ','eVidyaloka'),('BSEB','BSEB'), ('CBSE', 'CBSE'),
                    ('UBSE','UBSE'),('GSEB','GSEB'),('JKBOSE','JKBOSE')), null=True, blank=True)
    #block = models.CharField(max_length=30, null = True, blank=True)
    working_days = models.TextField(null=True, blank=True)
    working_slots = models.TextField(null=True, blank=True)
    admin = models.ForeignKey(User, null=True, blank=True)
    assistant = models.ForeignKey(User, null=True, blank=True, related_name='assistant_center')
    photo = models.FileField(upload_to='static/uploads/center', null=True, blank=True)
    description = models.TextField(max_length=2048, null=True, blank=True)
    classlocation = models.CharField(max_length=256, null=True, blank=True)
    grades = models.CharField(max_length=250, null=True, blank=True)
    subjectscovered = models.CharField(max_length=256, null=True, blank=True)
    noofchildren = models.IntegerField(default=0)
    status = models.CharField(max_length=256,choices=(('Planned', 'Planned'), ('Active', 'Active'), 
                ('Inactive', 'Inactive'),('Closed','Closed'), ('Provisional', 'Provisional')), default="Planned")
    launchdate = models.CharField(max_length=256, null=True, blank=True)
    donor_name = models.CharField(max_length=256, null=True, blank=True)
    skype_id = models.CharField(max_length=256, null=True, blank=True)
    location_map = models.CharField(max_length=1024, null=True, blank=True)
    ops_donor_name =  models.CharField(max_length=256, null=True, blank=True)
    # school  = models.ForeignKey(School, null=True)
    funding_partner = models.ForeignKey(Partner, related_name="funding_partner", null=True, blank=True)
    delivery_partner = models.ForeignKey(Partner, related_name="delivery_partner", null=True, blank=True)
    created_by  = models.ForeignKey(User, null=True, blank=True, related_name="center_createdby")
    modified_by = models.CharField(max_length=250, null=True, blank=True)
    dt_added   = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    field_coordinator = models.ForeignKey(User, null = True, blank=True ,related_name='field_coordinator_center')
    delivery_coordinator = models.ForeignKey(User, null = True, blank=True,related_name='delivery_coordinator_center')
    HM =  models.CharField(max_length=256, null = True, blank=True)
    partner_school = models.ForeignKey(MySchool, null=True, blank=True)
    orgunit_partner = models.ForeignKey(Partner, related_name="ogunit_partner", null=True, blank=True)
    digital_school = models.ForeignKey(DigitalSchool, related_name="ds_center_belongs_to", null=True, blank=True)
    digital_school_partner = models.ForeignKey(Partner, related_name="ds_center_partner", null=True, blank=True)
    program_type = models.IntegerField(null=True, blank=True, choices=((1,'Digital Classroom'), (2,'Digital School'), (3,'Sampoorna')), default=1)
    is_test = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=30)
    dob = models.DateTimeField(null=True, blank=True)
    center = models.ForeignKey(Center, null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    grade = models.CharField(max_length=50, null=True, blank=True)
    father_occupation = models.CharField(max_length=50,null=True, blank=True)
    mother_occupation = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True, default="")
    activation = models.BooleanField(default=False)
    strengths = models.TextField(max_length=2048, null=True, blank=True)
    weakness = models.TextField(max_length=2048, null=True, blank=True)
    observation = models.TextField(max_length=2048, null=True, blank=True)
    photo = models.FileField(upload_to='static/uploads/student', null=True, blank=True)
    status =  models.CharField(max_length=256,choices=(('Active', 'Active'), ('Alumni','Alumni')),default="Active")
    school_rollno = models.CharField(max_length=128, null=True, blank=True)
    created_by = models.ForeignKey(User,null=True,blank=True,related_name='student_created_by')
    updated_by = models.ForeignKey(User,null=True,blank=True,related_name='student_updated_by')
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    promoted_by = models.ForeignKey(User,null=True,blank=True,related_name='student_promoted_by')
    promoted_on = models.DateTimeField( null=True, blank=True)
    enrolled_by= models.ForeignKey(User,null=True,blank=True,related_name='student_enrolled_by')
    enrolled_on = models.DateTimeField( null=True, blank=True)
    previous_grade = models.CharField(max_length=50, null=True, blank=True)
    physical_school = models.CharField(max_length=500, null=True, blank=True)
    school_medium_lng = models.ForeignKey(Language, null=True, blank=True)
    profile_doc = models.ForeignKey(UserDocument, null=True, related_name='profile_pic_document')
    profile_pic_url = models.CharField(max_length=1024, null=True, blank=True)
    onboarding_status = models.CharField(max_length=256, choices=(('pending', 'Pending'), ('completed', 'Completed'), ('course not opted', 'Course not opted'),('schedule not opted', 'Schedule not opted')), default="pending")
    class_status = models.CharField(max_length=50, choices=(('1', 'Active'), ('2', 'Inactive'), ('3', 'Promoted ,Course not opted'),('4', 'schedule not opted ')), default="1")
    is_test_user = models.BooleanField(default=False)
    is_reached = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name

class Offering(models.Model):
    course = models.ForeignKey(Course,db_index=True)
    center = models.ForeignKey(Center,db_index=True)
    #language = models.CharField(max_length=50, null=True, blank=True)
    language = models.CharField(max_length=256,
            choices=(('Bengali', 'Bengali'), ('Gujarathi', 'Gujarathi'), ('Hindi', 'Hindi'), ('Kannada', 'Kannada'),
                    ('Malayalam', 'Malayalam'), ('Marathi', 'Marathi'), ('Oriya', 'Oriya'), ('Punjabi', 'Punjabi'),
                    ('Tamil', 'Tamil'), ('Telugu', 'Telugu'), ('Urdu', 'Urdu')), default='Telugu')
    academic_year =  models.ForeignKey(Ayfy, limit_choices_to={'types': 'Academic Year'}, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True,db_index=True)
    end_date = models.DateTimeField(null=True, blank=True,db_index=True)
    planned_topics = models.ManyToManyField(Topic, related_name="planned_topics", blank=False)
    actual_topics = models.ManyToManyField(Topic, related_name="actual_topics", blank=True)
    status = models.CharField(max_length=256,db_index=True, choices=(('running', 'running'), ('pending', 'pending'), 
                    ('completed', 'completed'), ('Provisional', 'Provisional')), blank=True,null=True)
    enrolled_students = models.ManyToManyField(Student)
    active_teacher = models.ForeignKey(User,null=True,blank=True)
    course_type = models.CharField(max_length=30,null=True, blank=True,db_index=True)
    picture = models.URLField(max_length=200, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='offering_created_by')
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='offering_updated_by')
    batch = models.IntegerField(null=True, blank=True)
    program_type = models.IntegerField(choices=((0, 'None'),(1,'Digital Classroom'),(2,'LFH'),(3,'Worksheets'),
                                                                (4,'Alumni'),(5,'Digital School')), default=0)
    
    @property
    def started_sessions(self):
        return Session.objects.filter(offering=self, status='started')

    @property
    def pending_sessions(self):
        return Session.objects.filter(offering=self, status='pending')

    def __unicode__(self):
        # DONT CHANGE THIS FORMAT, PROVISIONALDEMAND SLOT DEPENDS ON IT (webext/views.py - def send_pd_booking_email)
        return '%s/%s/%s' %(self.center, self.course, self.language)

    def get_planned_topics(self):
        return '<br/>'.join([unicode(t) for t in self.planned_topics.all()])
    get_planned_topics.short_description = 'Planned Topics'
    get_planned_topics.allow_tags = True

    def get_actual_topics(self):
        return '<br/>'.join([unicode(t) for t in self.actual_topics.all()])
    get_actual_topics.short_description = 'Actual Topics'
    get_actual_topics.allow_tags = True




#----------------------------------Demand Management----------------------------#


class Slot(models.Model):
    center_id = models.ForeignKey(Center)
    slot = models.CharField(max_length=50, null=True,blank=True)
    user = models.ForeignKey(User,null=True,blank=True)
    avail_from = models.DateTimeField(null=True,blank=True)
    select_offer = models.ForeignKey(Offering,null=True,blank=True)
    def __unicode__(self):
        return '%s ( %s )' %(self.center_id.name,self.slot)

class Demandslot(models.Model):
    center = models.ForeignKey(Center, null=True, blank=True)
    day = models.CharField(max_length=20, null=True, blank=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    offering = models.ForeignKey(Offering, blank=True, null=True)
    status = models.CharField(max_length=25, choices=(('Booked','Booked'), ('Allocated', 'Allocated'), 
                            ('Unallocated','Unallocated')), default='Unallocated')
    date_booked = models.DateTimeField(null=True,blank=True)
    type = models.IntegerField(choices=((1,'Common'), (2, 'Bounded')), default=1)
    created_by = models.ForeignKey(User, null=True, related_name='Demandslot_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='Demandslot_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    def __unicode__(self):
        return '%s :%s :%s :%s :%s :%s' %(self.day, self.start_time, self.end_time,self.offering,self.status,self.center)


class ProvisionalDemandslot(models.Model):
    center = models.ForeignKey(Center, null=True, blank=True)
    day = models.CharField(max_length=20, null=True, blank=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    offering = models.ForeignKey(Offering, blank=True, null=True)
    status = models.CharField(max_length=25, default='Unallocated')
    date_booked = models.DateTimeField(null=True, blank=True)
    user_pref = models.CharField(max_length=250, default="{}")

    def __unicode__(self):
        # DONT CHANGE THIS FORMAT, PROVISIONALDEMAND SLOT DEPENDS ON IT (webext/views.py - def send_pd_booking_email)
        return '%s|%s|%s|%s|%s|%s' % (
        self.day, self.start_time[:-3], self.end_time[:-3], self.offering, self.status, self.center)


#----------------------------------Demand Management----------------------------#


class ReferenceChannel(models.Model):
    name                    = models.CharField(max_length=100)
    partner                 = models.ForeignKey(Partner, null=True, related_name="partner_referencechannel")
    is_schooladmin             = models.IntegerField(default=0)
    dt_added                = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated              = models.DateTimeField(auto_now=True, null=True, blank=True)
    mail_status             = models.CharField(max_length=45, default='unmuted', null=True)

    def __unicode__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    skype_id = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    time_zone = models.CharField(max_length=20, blank=True)
    country         = models.CharField(max_length=30,  blank=True) #user current country
    state           = models.CharField(max_length=30,  blank=True) #user current state
    city            = models.CharField(max_length=30,  blank=True) #user current city
    secondary_email = models.CharField(max_length=75, blank=True)
    gender          = models.CharField(max_length=8, blank=True)
    age             = models.CharField(max_length=4, blank=True)
    profession      = models.CharField(max_length=80, blank=True)
    qualification = models.CharField(max_length=256, blank=True, null=True)
    from_date = models.DateTimeField(auto_now_add=True)
    to_date = models.DateTimeField(auto_now_add=True)
    pref_medium = models.CharField(max_length=30, blank=True)
    pref_roles = models.ManyToManyField(Role, related_name="user_pref_roles", blank=True)
    pref_offerings = models.ManyToManyField(Offering, blank=True)
    pref_days = models.TextField(blank=True)
    pref_slots = models.TextField(blank=True)
    pref_subjects = models.CharField(max_length=1024, blank=True)
    role = models.ManyToManyField(Role, related_name="user_profile_role", blank=True)
    pref_center = models.CharField(max_length=50, blank=True)
    picture = models.URLField(max_length=200, blank=True)
    code_conduct = models.BooleanField()
    computer = models.BooleanField()
    internet_connection = models.BooleanField()
    internet_speed = models.CharField(max_length=50, blank=True)
    webcam = models.BooleanField()
    headset = models.BooleanField()
    trainings_complete = models.BooleanField()
    review_resources = models.BooleanField()
    evd_rep = models.BooleanField()
    trail_class = models.BooleanField()
    self_eval = models.BooleanField()
    referred_user = models.ForeignKey(User,related_name="refered_user", null=True, blank=True)
    referer  = models.CharField(max_length=100,  blank=True)

    dicussion_outcome = models.CharField(max_length=30, choices=(('Not Scheduled', 'Not Scheduled'), ('Scheduled', 'Scheduled'),\
                            ('Recommended for Teaching', 'Recommended for Teaching'), ('Recommended for Alternate role', 'Recommended for Alternate role'),\
                            ('Recommended for Admin', 'Recommended for Admin'), ('Recommended for Content', 'Recommended for Content'),('Others', 'Others')),\
                            default='Not Scheduled')
    evd_rep_meet = models.BooleanField()

    hrs_contributed = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=25, choices=(('New', 'New'), ('Ready', 'Ready'), ('Active', 'Active'),\
                                            ('Dormant', 'Dormant'), ('Inactive', 'Inactive'),('Others','Others')), default='New')

    profile_complete_status = models.CharField(max_length=25, choices=(('Incomplete', 'Incomplete'), ('Started', 'Started'),\
                            ('Inprocess', 'Inprocess'), ('Selected', 'Selected'), ('Ready', 'Ready')), default = 'Incomplete')
    profile_completion_status = models.BooleanField()
    short_notes = models.CharField(max_length=3024, blank=True)
    remarks = models.CharField(max_length=3024, blank=True)
    purpose = models.TextField(blank=True)
    fbatwork_id = models.CharField(max_length=1024, blank=True)
    fb_member_token = models.TextField(blank=True)
    referencechannel = models.ForeignKey(ReferenceChannel, null=True, blank=True)
    old_reference_channel = models.CharField(max_length=64, choices=(('Internet Search', 'Internet Search'),\
                        ('Word of Mouth', 'Word of Mouth'), ('Facebook', 'Facebook'), ('WhatsApp', 'WhatsApp'), ('Emailer', 'Emailer'),
                        ('UN Volunteering', 'UN Volunteering'), ('Corporate HP', 'Corporate HP'),('Corporate - DST Services', 'Corporate - DST Services'),
                        ('Corporate - Microsoft', 'Corporate - Microsoft'), ('Corporate - FlipKart', 'Corporate - FlipKart'),
                        ('WealthRays', 'WealthRays'), ('Corporate - Apeejay Group', 'Corporate - Apeejay Group'),
                        ('L & T Infotech', 'L & T Infotech'),('Corporate - Mphasis','Corporate - Mphasis'),('Corporate - ANZ','Corporate - ANZ'),
                        ('Microsoft BLR', 'Microsoft BLR'),('Corporate - TE Connect', 'Corporate - TE Connect'),
                        ('Corporate - XLRI - Sigma', 'Corporate - XLRI - Sigma'),('Corporate - Mantra','Corporate - Mantra'),
                        ('Corporate - Brillio', 'Corporate - Brillio'),('corporate - Infosys', 'corporate - Infosys'),
                        ('Corporate - Avvaya', 'Corporate - Avvaya'),('Corporate - Quess', 'Corporate - Quess'),('Corporate - Cisco', 'Corporate - Cisco'),
                        ('Corporate - Enzen', 'Corporate - Enzen'),('Corporate - Joy of Reading', 'Corporate - Joy of Reading'),
                        ('Corporate - Aditya Birla Retail', 'Corporate - Aditya Birla Retail'),('Corporate - Cognizant - GGN', 'Corporate - Cognizant - GGN'),
                        ('Corporate - Cognizant - kolkata', 'Corporate - Cognizant - kolkata'),('Corporate - Cognizant - Mumbai', 'Corporate - Cognizant - Mumbai'),
                        ('Team-Everest', 'Team-Everest'),('Corporate - Cognizant - Pune', 'Corporate - Cognizant - Pune'),
                        #('Corporate - Cognizant HYD', 'Corporate - Cognizant HYD'), ('Online Community', 'Online Community')), default='Internet Search')
                        ('Corporate - Cognizant HYD', 'Corporate - Cognizant HYD'), ('Online Community', 'Online Community'), \
                        ('IBM Community', 'IBM Community')), default='Internet Search')
    unavailability_reason = models.CharField(max_length=64, choices=(('Interested, but not now','Interested, but not now'),\
                            ('Interested, but not clear on next steps', 'Interested, but not clear on next steps'), \
                            ('Interested, but Occupied with Professional commitments', 'Interested, but Occupied with Professional commitments'),\
                            ('Interested, but Occupied with Personal commitments', 'Interested, but Occupied with Personal commitments'),\
                            ('Interested, but only on Weekends', 'Interested, but only on Weekends'),\
                            ('Interested, but my preferred language is not Available', 'Interested, but my preferred language is not Available'),\
                            ('Interested, but in other volunteering opportunities', 'Interested, but on other volunteering opportunities')
                            ), default='Interested, but not now')
    organization_complete_status = models.CharField(max_length=25, choices=(('Incomplete', 'Incomplete'), ('Started', 'Started'),\
                            ('Inprocess', 'Inprocess'), ('Selected', 'Selected'), ('Ready', 'Ready')), default = 'Incomplete')
    usersettings_data = models.TextField(null=True,blank=True,max_length=2048) ### settings group type : all or none value will be stored here as a text formatted json.
    no_hrs_week = models.CharField(max_length=25, null=True, blank=True)
    languages_known = models.TextField(max_length=2048, null = True, blank = True)
    dob = models.DateField(null=True, blank=True)
    native_country = models.CharField(max_length=128, null=True, blank=True)
    native_state= models.CharField(max_length=128, null=True, blank=True)
    native_city= models.CharField(max_length=128, null=True, blank=True)
    current_job = models.CharField(max_length=128, null=True, blank=True)
    work_exp = models.CharField(max_length=25, null=True, blank=True)
    terms_and_conditions = models.BooleanField(default=False)
    reset_pasword = models.BooleanField(default=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    profile_pic_doc = models.ForeignKey(UserDocument, null=True, related_name='profile_document',blank=True)
    is_test_user = models.BooleanField(default=False)
    assistance = models.BooleanField(default=False)
    consent = models.IntegerField(choices=((1, 'Accept'), (2, 'Declined')), null=True, blank=True, default=2)
    
    def __unicode__(self):
        try:
            return self.user.username
        except:
            return "no"

    def get_pref_offerings(self):
        return '<br/>'.join([unicode(t) for t in self.pref_offerings.all()])
    get_pref_offerings.short_description = 'Prefered offering'
    get_pref_offerings.allow_tags = True

    @property
    def roles(self):
        assigned_roles = [ role.name for role in self.role.all() ]

        return ", ".join(assigned_roles)

    @property
    def prefered_roles(self):
        assigned_roles = [ role.name for role in self.pref_roles.all() ]

        return ", ".join(assigned_roles)

    def get_dict(self):
        dictionary = {}
        for field in self._meta.get_all_field_names():
            try:
                dictionary[field] = self.__getattribute__(field)
            except AttributeError:
                pass
        return dictionary

class Session(models.Model):
    offering = models.ForeignKey(Offering,db_index=True)
    date_start = models.DateTimeField(null=True, blank=True,db_index=True)
    date_end = models.DateTimeField(null=True, blank=True,db_index=True)
    teacher = models.ForeignKey(User, null=True, blank=True,db_index=True)
    #num_students = models.IntegerField(default=0)
    #topic_covered = models.ForeignKey(Topic, null=True))
    planned_topics = models.ManyToManyField(Topic, related_name="session_planned_topics")
    actual_topics = models.ManyToManyField(Topic, related_name="session_actual_topics", blank=True)
    #num_students_attended = models.IntegerField(default=0)
    #num_students_enrolled = models.IntegerField(default=0)
    status = models.CharField(max_length=256,null = True, blank=True,db_index=True, choices=(('waiting', 'waiting'), ('scheduled', 'scheduled'), ('completed', 'completed'), ('rescheduled', 'rescheduled'),('started','started'),('cancelled','cancelled'), ('Offline', 'Offline')), default="scheduled" )
    video_link = models.CharField(max_length=1024, null = True, blank=True,db_index=True)
    mode = models.CharField(max_length=50, null = True, blank=True,db_index=True)
    #aids_used = models.CharField(max_length=256, null=True, blank=True)
    #activity = models.CharField(max_length=50, null=True , blank=True)
    comments = models.TextField(max_length=2048, null = True, blank = True)
    cancel_reason = models.CharField(max_length=256,null = True, blank=True, choices=(('Internet Down School', 'Internet Down School'), ('Power Cut School', 'Power Cut School'), ('Unscheduled leave School', 'Unscheduled leave School'), ('Internet down Teacher', 'Internet Down Teacher'),('Power Cut Teacher','Power Cut Teacher'),('Last Minute Dropout Teacher','Last Minute Dropout Teacher'), ('Communication Issue','Communication Issue'), ('Others','Others'),('Teacher yet to be backfilled','Teacher yet to be backfilled')) , default= None)
    dt_added   = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    teachingSoftware = models.ForeignKey('webext.TeachingSoftwareDetails',null=True,related_name='teaching_Software')
    ts_link = models.CharField(max_length=1024, blank=True)
    vc_id = models.CharField(max_length=1024, blank=True, null=True)
    sub_topic = models.ForeignKey("SubTopics", null=True, blank=True,db_index=True) 
    created_by = models.ForeignKey(User,null=True,blank=True,related_name='session_created_by')
    updated_by = models.ForeignKey(User,null=True,blank=True,related_name='session_updated_by')
    used_lesson_plan = models.CharField(max_length=50,null=True, blank=True,
            choices=(('yes', 'yes'), ('no', 'no')))
    is_flm = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s :%s :%s' %(self.date_start, self.date_end, self.teacher)

class StackTeacher(models.Model):
    offering = models.ForeignKey(Offering, null=True, blank=True)
    teacher = models.ForeignKey(User, null=True, blank=True)
    status = models.CharField(max_length=256,null=True, blank=True,
            choices=(('accepted', 'accepted'), ('pending', 'pending'), ('rejected', 'rejected')))
class SessionAttendance(models.Model):
    student = models.ForeignKey(Student, null = True, blank= True)
    session = models.ForeignKey(Session, null = True, blank= True)
    is_present = models.CharField(max_length=256,null = True, blank=True,
                choices=(('yes', 'yes'), ('no', 'no'),))

class Donation(models.Model):

    address         = models.TextField(null=True, blank=True)
    address2        = models.TextField(null=True, blank=True)
    amount          = models.IntegerField(default=0)
    channel         = models.CharField(max_length=256, choices=(('Bangalore 10K Run', 'Bangalore 10K Run'), ('Facebook', 'Facebook'), ('Email', 'Email'), ('Word of Mouth', 'Word of Mouth'), ('Others', 'Others'), ("FlipKart", "FlipKart"), ("NAD", "NAD")), default="Others")
    city    = models.CharField(max_length=1024, blank=True)
    country    = models.CharField(max_length=1024, blank=True)
    comments        = models.TextField(null=True, blank=True)
    donation_type = models.CharField(max_length=256, null=True, blank=True,
                        choices=(("Sponsor a Child Education", "Sponsor a Child Education"), ('Adopt Digital Classroom', 'Adopt Digital Classroom'), ("General Contribution", "General Contribution"), ('Sponsor a Full Center', 'Sponsor a Full Center'), ('NAD', 'NAD')))
    email           = models.CharField(max_length=1024)
    name            = models.CharField(max_length=1024)
    last_name            = models.CharField(max_length=1024)
    num_centers     = models.CharField(max_length=1024, blank=True,)
    num_classrooms  = models.CharField(max_length=1024, blank=True)
    num_months      = models.CharField(max_length=1024, blank=True)
    num_students    = models.CharField(max_length=1024, blank=True)
    num_subjects    = models.CharField(max_length=1024, blank=True)
    pan_number      = models.CharField(null=True, blank=True, max_length=256)
    passport_number = models.CharField(max_length=1024, blank=True)
    payment_type    = models.CharField(max_length=256, choices=(('online', 'online'), ('cheque', 'cheque'), ('neft', 'neft')))
    phone           = models.CharField(max_length=1024)
    pincode         = models.CharField(max_length=20)
    reference       = models.CharField(max_length=1024, null=True, blank=True)
    receipt         = models.FileField(upload_to='static/uploads/donation_receipts', null=True, blank=True)
    resident        = models.CharField(max_length=1024, blank=True)
    state           = models.CharField(max_length=1024, blank=True)
    status = models.CharField(max_length=30, choices=(('pending', 'pending'), ('in progress', 'in progress'), ('completed', 'completed')), default="pending")
    mail_status = models.CharField(max_length=30, choices=(('pending', 'pending'), ('old data', 'old data'), ('success', 'success')), default="pending")
    user            = models.ForeignKey(User, null=True, blank=True)
    area_of_donation = models.CharField(max_length=1024, blank=True, null=True)
    honorary_name = models.CharField(max_length=1024, blank=True, null=True)
    duplicate = models.BooleanField()


    chequenumber            = models.CharField(max_length=1024, blank=True)
    chequedate              = models.CharField(max_length=1024, blank=True)
    chequebank              = models.CharField(max_length=1024, blank=True)
    checkdeposite_date      = models.CharField(max_length=1024, blank=True)
    cheque_credited_date    = models.CharField(max_length=1024, blank=True)
    neft_bank_name          = models.CharField(max_length=1024, blank=True)
    neft_transaction_id     = models.CharField(max_length=1024, blank=True)
    neft_transaction_date   = models.CharField(max_length=1024, blank=True)
    neft_credited_date      = models.CharField(max_length=1024, blank=True)
    online_msg              = models.CharField(max_length=1024, blank=True)
    online_resp_msg         = models.CharField(max_length=1024, blank=True)
    online_txn_status       = models.CharField(max_length=1024, blank=True, choices=(('started', 'started'), ('completed', 'completed')))
    recipent_url            = models.URLField(max_length=200, blank=True)
    donation_time           = models.DateTimeField(null=False, blank=False)
    transaction_key         = models.CharField(max_length=1024, blank=True)
    receipt_no              = models.CharField(max_length=1024, blank=True)
    batch_no                = models.CharField(max_length=1024, blank=True)
    reference_id            = models.ForeignKey(User,related_name="referrer",null = True, blank= True)
    financial_year          = models.ForeignKey(Ayfy, null= True, blank=True)
    is_deleted              = models.CharField(max_length=30, choices=(('yes', 'yes'), ('no', 'no')), default="no")
    upi_transaction_no      = models.CharField(max_length=1024, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            up = UserProfile.objects.create(user=instance)
            role = Role.objects.get(name='Teacher')
            up.pref_roles.add(role)
            up.save()
            admins = User.objects.filter(is_superuser=True)
            notification.send(admins, '_user_joined', {'user': instance})
        except Exception as e:
            print traceback.format_exc()

def facebook_extra_values(sender, user, response, details, **kwargs):
    print 'here at fb extra values', response
    if "id" in response:
        try:
            url = None
            if sender == FacebookBackend:
                url = "http://graph.facebook.com/%s/picture?type=large"  % response["id"]
            elif sender == google.GoogleOAuth2Backend and "picture" in response:
                url = response["picture"]
            print "***********URL**********", url
            if url:
                profile = UserProfile.objects.get(user=user)
                if not profile.picture or 'graph.facebook.com' in profile.picture:
                    profile.picture = url
                    profile.save()
        except Exception as e:
            print "got exception ", e.message

    return False

pre_update.connect(facebook_extra_values, sender=FacebookBackend)

#-------------------------Student Module-----------------------#


class Term(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField( max_length=30,  choices=(('Completed', 'Completed'), ('Running','Running'), ('Upcoming','Upcoming')),default='Upcoming' )

class LRCategory(models.Model):
    name = models.CharField(max_length=1024, blank = True)
    def __unicode__(self):
        return self.name


class LearningRecord(models.Model):
    student  = models.ForeignKey(Student)
    offering =  models.ForeignKey(Offering)
    category = models.ForeignKey(LRCategory)
    date_created =  models.DateTimeField(null=True, blank=True)
    created_by  = models.ForeignKey(User)
    attachment = models.FileField(blank=True, upload_to='static/uploads/assesments', null=True)
    remarks = models.CharField(max_length=2048, null=True, blank=True)
    def __unicode__(self):
        return  '%s | %s | %s | %s' %(self.student.name,self.offering, self.category, self.date_created)

class Scholastic(models.Model):
    learning_record = models.ForeignKey(LearningRecord, null=True, blank=True)
    total_marks = models.IntegerField(default=0)
    obtained_marks =  models.DecimalField( max_digits=5, decimal_places=2)
    category = models.CharField(max_length=50, choices=(('Quiz', 'Quiz'), ('Worksheet', 'Worksheet'), ('Sliptest', 'Sliptest'), ('Monthly test', 'Monthly test'), ('Term1', 'Term1'), ('Term2', 'Term2'), ('Term3', 'Term3'),('Baseline','Baseline'),('End_line','End_line')), default="Sliptest")
    is_present = models.CharField(max_length=128, null=True,blank=True, choices=(('Yes','Yes'),('No','No')),default="Yes")
    def __unicode__(self):
        return '%s | %s | %s' %(self.obtained_marks,self.total_marks,self.category)

class LFH_Scholatics(models.Model):
    offering_id = models.CharField(max_length=64, blank=True, null=True)
    student_id = models.CharField(max_length=64, blank=True, null=True)
    topic_id = models.CharField(max_length=128, blank=True, null=True)
    subject = models.CharField(max_length=128, blank=True, null=True)
    outcome = models.CharField(max_length=28, null=False,blank=False, choices=(('Correct','Correct'),('Incorrect','Incorrect')),default="Correct")
    is_present = models.CharField(max_length=128, null=False,blank=False, choices=(('Yes','Yes'),('No','No')),default="Yes")
    record_type = models.CharField(max_length=128, null=False,blank=False, choices=(('Baseline','Baseline'),('Endline','Endline')),default="Baseline")
    record_date = models.DateTimeField(null=False, blank=False)
    added_by = models.CharField(max_length=60, blank=True, null=True)
    added_on = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=60, blank=True, null=True)
    updated_on = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        return '%s | %s | %s | %s | %s | %s' %(self.topic_id, self.subject, self.outcome, self.is_present, self.record_type, self.record_date)
        
class CoScholastic(models.Model):
    learning_record = models.ForeignKey(LearningRecord, null=True, blank=True)
    pr_curious = models.CharField(max_length=126, null=True, blank=True )
    pr_attentiveness = models.CharField(max_length=126, null=True, blank=True)
    pr_self_confidence =  models.CharField(max_length=126, null=True, blank=True)
    lr_responsibility = models.CharField(max_length=126, null=True, blank=True)
    lr_supportiveness = models.CharField(max_length=126, null=True, blank=True)
    lr_initiativeness = models.CharField(max_length=126, null=True, blank=True)
    bh_positive_attitude = models.CharField(max_length=126, null=True, blank=True)
    bh_courteousness = models.CharField(max_length=126, null=True, blank=True)
    ee_widerperspective = models.CharField(max_length=126, null=True, blank=True)
    ee_emotional_connect = models.CharField(max_length=126, null=True, blank=True)
    ee_technology_exposure = models.CharField(max_length=126, null=True, blank=True)


class Activity(models.Model):
    learning_record = models.ForeignKey(LearningRecord, null=True, blank=True)
    notes = models.TextField(max_length=1024, null=True, blank=True)
    grading = models.CharField(max_length=126, null=True, blank=True)

class UniqueC(models.Model):
    learning_record = models.ForeignKey(LearningRecord, null=True, blank=True)
    strengths = models.TextField(max_length=1024)
    weaknesses = models.TextField(max_length=1024)


class Diagnostic(models.Model):
    student = models.ForeignKey(Student)
    offering = models.ForeignKey(Offering)
    grade = models.CharField(max_length=128, blank=True, null=True)
    subject = models.CharField(max_length=128, blank=True, null=True)
    date_created = models.DateTimeField(null=True, blank=True)
    aggregate_level =  models.CharField(max_length=20,blank=True, null=True)
    category = models.CharField(max_length=50, choices=(('Diagnostic1', 'Diagnostic1'), ('Diagnostic2', 'Diagnostic2')), blank=True, null=True)


class DiagParameter(models.Model):
    subject = models.CharField(max_length=126, blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)
    level = models.CharField(max_length=20,blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    param_code = models.CharField(max_length=50, blank=True,null=True)
    total_marks = models.IntegerField(default=0)
    version = models.CharField(max_length=20, blank=True,null=True)

class DiagDetails(models.Model):
    parameter = models.ForeignKey(DiagParameter)
    diagnostic = models.ForeignKey(Diagnostic)
    actual_marks = models.DecimalField(max_digits=3,decimal_places=2)





#-------------------------End Student Module-----------------------#

class ProgressReport(models.Model):
    student =  models.ForeignKey(Student)
    report_card =  models.FileField(upload_to='static/uploads/student_reports', null=True, blank=True)
    generated_date = models.DateTimeField(null=True, blank=True)

#------------------------Role wise Onboarding ---------------------#

class OnboardingStep(models.Model):
    role = models.ForeignKey(Role)
    stepname = models.CharField(max_length = 50, blank=True, null=True)
    description = models.CharField(max_length = 1024, blank=True, null=True)
    weightage = models.IntegerField( default = 0)
    order = models.IntegerField( default = 0 )
    prerequisite = models.ForeignKey('self', blank=True, null=True)
    repeatable = models.BooleanField()
    def __unicode__(self):
        return self.role.name +' '+self.stepname

class RolePreference(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    role = models.ForeignKey(Role)
    hrs_contributed = models.DecimalField( max_digits=10, decimal_places=2, null=True, blank=True)
    role_onboarding_status = models.IntegerField(max_length=10, default=0 )
    availability = models.BooleanField()
    follow_up_date = models.DateTimeField(null=True,blank=True)
    role_status = models.CharField(max_length=30, choices=(('New', 'New'),
                                                            ('Active', 'Active'),
                                                            ('Inactive', 'Inactive'),
                                                            ('Others', 'Others'),
                                                            ('Dormant','Dormant')), default="New")
    role_outcome = models.CharField(max_length=30, choices=(('Not Started', 'Not Started'),
                                                            ('Inprocess', 'Inprocess'),
                                                            ('Recommended', 'Recommended'),
                                                            ('Recommended for Alternate Role', 'Recommended for Alternate Role'),
                                                            ('Not Eligible','Not Eligible')), default="Not Started")
    recommended_date = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, blank=True)
    date_updated = models.DateTimeField(null=True,blank=True)
    notes = models.CharField(max_length=256, null=True, blank=True)
    dt_added   = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return str(self.userprofile.id) +' '+ self.role.name +' Preference'

    def update_status(self):
        complete_steps = self.onboardingstepstatus_set.all().filter(status=True)
        role_onboarding_status = sum(complete_steps.values_list('step__weightage',flat = True))
        self.role_onboarding_status = role_onboarding_status
        if role_onboarding_status > 0 and self.role_outcome == 'Not Started':
            self.role_outcome = 'Inprocess'
        self.save()


class OnboardingStepStatus(models.Model):
    role_preference = models.ForeignKey(RolePreference)
    step = models.ForeignKey(OnboardingStep)
    status = models.BooleanField()
    date_completed = models.DateTimeField(null=True,blank=True)

    def __unicode__(self):
        return str(self.status)

    def save(self, *args, **kwargs):
        super(OnboardingStepStatus, self).save(*args, **kwargs)
        self.role_preference.update_status()


class SelfEvaluation(models.Model):
    userp = models.ForeignKey(UserProfile)
    role_preference = models.ForeignKey(RolePreference)
    se_form = models.CharField(max_length=10240, null=True, blank=True)
    date_submited = models.DateTimeField(null=True,blank=True)

#------------------------End Role wise Onboarding ---------------------#

#------------------------SelectionDiscussion---------------------------#

class SelectionDiscussion(models.Model):
    userp = models.ForeignKey(UserProfile)
    event_id = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=25, null=True, blank=True)
    start_time = models.DateTimeField(null=True,blank=True)
    end_time = models.DateTimeField(null=True,blank=True)
    first_name = models.CharField(max_length=1024, null=True, blank=True)
    last_name = models.CharField(max_length=1024, null=True, blank=True)
    email = models.CharField(max_length=1024, null=True, blank=True)
    link_ref = models.CharField(max_length=1024, null=True, blank=True)
    updated_at = models.DateTimeField(null=True,blank=True)
    skype_id = models.CharField(max_length=1024, null=True, blank=True)
    nextSyncToken = models.CharField(max_length=1024, null=True, blank=True)
    channel_expiry = models.DateTimeField(null=True,blank=True)
    channel_id = models.CharField(max_length=1024, null=True, blank=True)
    resource_id = models.CharField(max_length=1024, null=True, blank=True)

class EventRegistration(models.Model):
    event_name = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=75, blank=True)
    email = models.CharField(max_length=75, blank=True)
    phone = models.CharField(max_length=75, blank=True)
    number_of_participants = models.CharField(max_length=3, blank=True)
    organisation = models.CharField(max_length=75, blank=True)
    referred_by = models.CharField(max_length=75, blank=True)

class SelectionDiscussionSlot(models.Model):
    userp = models.ForeignKey(UserProfile, null=True, blank=True)
    role = models.ForeignKey(Role, null=True, blank=True, default=None)
    tsd_panel_member = models.ForeignKey(UserProfile, null=True, blank=True, related_name="tsd_panel")
    publisher_role = models.ForeignKey(Role, null=True, blank=True, default=None,related_name="csd_panel")
    booked_date = models.DateTimeField(null=True,blank=True)
    start_time = models.DateTimeField(null=True,blank=True)
    end_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=(('Not Booked', 'Not Booked'),('Booked', 'Booked')), default="Not Booked")
    outcome = models.CharField(max_length=30, choices=(('Scheduled', 'Scheduled'),('Assigned', 'Assigned'),('Completed', 'Completed'), ('Cancelled', 'Cancelled')), default="Scheduled")

    # class Meta:
    #     unique_together = ('start_time', 'end_time','tsd_panel_member')

    def save(self, *args, **kwargs):
        # if not self.tsd_panel_member:
        #     if SelectionDiscussionSlot.objects.exclude(id=self.id).filter(start_time=self.start_time, end_time=self.end_time, tsd_panel_member__isnull=True).exists():
        #         raise ValueError("Duplicate Data With tsd_panel_member none")
        super(SelectionDiscussionSlot, self).save(*args, **kwargs)

class Task(models.Model):
    comment = models.CharField(max_length=3024, null=True, blank=True)
    dueDate = models.DateTimeField(null=True,blank=True)
    priority = models.CharField(max_length=1024, null=True, blank=True)
    reminderText = models.CharField(max_length=1024, null=True, blank=True)
    reminderUrl = models.CharField(max_length=1024, null=True, blank=True)
    subject = models.CharField(max_length=1024, null=True, blank=True)
    taskCreatedDate = models.DateTimeField(null=True,blank=True)
    taskFor = models.CharField(max_length=1024, null=True, blank=True)
    taskStatus = models.CharField(max_length=1024, null=True, blank=True)
    taskUpdatedDate = models.DateTimeField(null=True,blank=True)
    performedOn_userId = models.CharField(max_length=1024, null=True, blank=True)
    assignedTo = models.CharField(max_length=1024, null=True, blank=True)
    contactId = models.CharField(max_length=1024, null=True, blank=True)
    taskCreatedBy_userId = models.CharField(max_length=1024, null=True, blank=True)
    taskUpdatedBy_userId = models.CharField(max_length=1024, null=True, blank=True)
    autoGeneratedTask = models.CharField(max_length=1024, null=True, blank=True)
    taskUpdatedBy_userId = models.CharField(max_length=1024, null=True, blank=True)
    user_date_joined = models.DateTimeField(null=True, blank=True)
    performedOn_name=models.CharField(max_length=1024, null=True, blank=True)
    taskType=models.CharField(max_length=1024, null=True, blank=True)
    task_other_status = models.CharField(max_length=1024, null=True, blank=True)
    category = models.CharField(max_length=1024, null=True, blank=True)

class Meta:
    unique_together = ('start_time', 'end_time')

class SelectionDiscussionSlotHistory(models.Model):
    slot = models.ForeignKey(SelectionDiscussionSlot, null=True, blank=True)
    userp = models.ForeignKey(UserProfile, null=True, blank=True)
    booked_date = models.DateTimeField(null=True, blank=True)
    released_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=(('Released', 'Released'),('Booked', 'Booked'),('Admin Released', 'Admin Released')), default="Booked")
    reason_to_release = models.CharField(max_length=75, blank=True)

    def __unicode__(self):
        return '%s' %(self.id)

class Award(models.Model):
    name = models.CharField(max_length = 50, blank=True, null=True)
    description = models.CharField(max_length = 1024, blank=True, null=True)

    def __unicode__(self):
            return self.name

class AwardDetail(models.Model):
    student  = models.ForeignKey(Student, null=True, blank=True)
    offering = models.ForeignKey(Offering, null=True, blank=True)
    teacher  = models.ForeignKey(User, null=True, blank=True, related_name='teacher')
    award    = models.ForeignKey(Award, null=True, blank=True)
    nominate_reason = models.CharField(max_length = 1024, blank=True, null=True)
    date_created = models.DateTimeField(null=True,blank=True, auto_now_add=True)
    modified_date = models.DateTimeField(null=True,blank=True, auto_now=True)
    modified_by = models.ForeignKey(User, null=True, blank=True, related_name='modified_by')
    status = models.CharField(max_length=30, choices=(('Nominated', 'Nominated'),('Approved', 'Approved'),
                                                    ('Cancelled', 'Cancelled')))

    def __unicode__(self):
        return '%s - %s' %(self.student.name, self.award.name)
    
class Setting(models.Model):
    name=models.CharField(max_length=1024, null=True, blank=True)
    duration=models.CharField(max_length=1024, null=True, blank=True)
    
class MailingList(models.Model):
    name=models.CharField(max_length=1024, null=True, blank=True)
    email_id=models.CharField(max_length=1024, null=True, blank=True)
    volunteer_id=models.CharField(max_length=1024, null=True, blank=True)
    
class UserActivityHistory(models.Model):
    user_id = models.CharField(max_length=1024, null=True, blank=True)
    username = models.CharField(max_length=1024, null=True, blank=True)
    name = models.CharField(max_length=1024, null=True, blank=True)
    activity_date_time = models.DateTimeField(null=True, blank=True)
    activity_name = models.CharField(max_length=1024, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    activity_type = models.CharField(max_length=1024, null=True, blank=True)
    activity_type_id = models.CharField(max_length=1024, null=True, blank=True)
    created_date = models.CharField(max_length=1024, null=True, blank=True)
    updated_date = models.CharField(max_length=1024, null=True, blank=True)
    created_by = models.CharField(max_length=1024, null=True, blank=True)
    updated_by = models.CharField(max_length=1024, null=True, blank=True)
    
class ActivityType(models.Model):
    activity_type = models.CharField(max_length=1024, null=True, blank=True)
    
class SystemTaskHistory(models.Model):
    user_id = models.CharField(max_length=1024, null=True, blank=True)
    task_id = models.CharField(max_length=1024, null=True, blank=True)
    type = models.CharField(max_length=1024, null=True, blank=True)
    
class SessionRatings(models.Model):
    is_rated = models.BooleanField(default=False)
    updated_date = models.DateTimeField(null=True, blank=True)
    question = models.CharField(max_length=50,null=False)
    no_of_stars = models.IntegerField(max_length=5,null=True)
    created_date = models.DateTimeField(null=True, blank=True)
    question_no = models.IntegerField(max_length=10,null=False)
    user_id = models.ForeignKey(User,null=True,related_name='sr_user_id')
    created_by = models.ForeignKey(User,null=True,related_name='sr_created_by')
    updated_by = models.ForeignKey(User,null=True,related_name='sr_updated_by')
    session_id = models.ForeignKey(Session,null=True,related_name='sr_session_id')
    
class TaskRejected(models.Model):
    comment = models.CharField(max_length=3024, null=True, blank=True)
    dueDate = models.DateTimeField(null=True,blank=True)
    priority = models.CharField(max_length=1024, null=True, blank=True)
    reminderText = models.CharField(max_length=1024, null=True, blank=True)
    reminderUrl = models.CharField(max_length=1024, null=True, blank=True)
    subject = models.CharField(max_length=1024, null=True, blank=True)
    taskCreatedDate = models.DateTimeField(null=True,blank=True)
    taskFor = models.CharField(max_length=1024, null=True, blank=True)
    taskStatus = models.CharField(max_length=1024, null=True, blank=True)
    performedOn_userId = models.CharField(max_length=1024, null=True, blank=True)
    assignedTo = models.CharField(max_length=1024, null=True, blank=True)
    contactId = models.CharField(max_length=1024, null=True, blank=True)
    taskCreatedBy_userId = models.CharField(max_length=1024, null=True, blank=True)
    autoGeneratedTask = models.CharField(max_length=1024, null=True, blank=True)
    user_date_joined = models.DateTimeField(null=True, blank=True)
    performedOn_name=models.CharField(max_length=1024, null=True, blank=True)
    taskType=models.CharField(max_length=1024, null=True, blank=True)
    task_other_status = models.CharField(max_length=1024, null=True, blank=True)
    category = models.CharField(max_length=1024, null=True, blank=True)
    
class VolunteerProcessing(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    role = models.ForeignKey(Role, null=True, blank=True)
    status = models.CharField(max_length=25, choices=(('To be Processed', 'To be Processed'), ('Progressing', 'Progressing'),\
                                                    ('Not Progressing', 'Not Progressing'), ('Processed', 'Processed')), default='To be Processed')
    outcome = models.CharField(max_length=25, choices=(('Not Started', 'Not Started'), ('Onboard Complete', 'Onboard Complete'),\
                                                    ('Not Interested', 'Not Interested'), ('UnSubscribe', 'UnSubscribe'),\
                                                    ('Not Available', 'Not Available'), ('Not Reachable', 'Not Reachable'),\
                                                    ('No Response', 'No Response')), default='Not Started')
    last_outcome = models.CharField(max_length=25, null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    update_counter = models.IntegerField(default=0, editable=False)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='vp_created_by')
    modified_by = models.ForeignKey(User, null = True, blank=True, related_name='vp_modified_by')
    dt_added    = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated  = models.DateTimeField(auto_now=True, null=True, blank=True)

@receiver(pre_save, sender=RolePreference)
def change_vp_status(sender, instance, **kwargs):
    try:
        user = instance.userprofile.user
        role = instance.role
        print(role)
        vp_obj, created = VolunteerProcessing.objects.get_or_create(user=user,role=role)

        role_pref_obj = RolePreference.objects.get(pk=instance.pk)
        old_role_outcome = role_pref_obj.role_outcome
        new_role_outcome = instance.role_outcome
        old_onboard_status = role_pref_obj.role_onboarding_status
        new_onboard_status = instance.role_onboarding_status

        if old_role_outcome != new_role_outcome:
            vp_obj.last_outcome = vp_obj.outcome
            vp_obj.update_counter += 1
            if old_role_outcome == "Inprocess":
                vp_obj.status = "Processed"
                vp_obj.outcome = "Onboard Complete"
            
            if old_role_outcome == "Not Started" and new_role_outcome == "Inprocess":
                vp_obj.status = "Progressing"

        if old_onboard_status != new_onboard_status:
            vp_obj.update_counter += 1
            vp_obj.status = "Progressing"

        vp_obj.save()

        return "success"
    except Exception as e:
        print traceback.format_exc()
        return "error"
    
class SubTopics(models.Model):
    name = models.CharField(max_length=400,null=True, blank=True)
    topic = models.ForeignKey(Topic,null=True,related_name='topic')
    created_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50,default="Not Started")
    type = models.CharField(max_length=50, choices=(('1', 'Subchapter'), ('2', 'quiz')),default=1)
    author_id = models.ForeignKey(User, null = True, blank=True,related_name="Author_id")
    created_by = models.ForeignKey(User, null = True, blank=True,related_name="created_user")
    updated_by = models.ForeignKey(User, null = True, blank=True,related_name="updated_user")
    reviewer = models.ForeignKey(User, null = True, blank=True,related_name="Reviewer_id")

    def __unicode__(self):
        return self.name

class OfferingTeacherMapping(models.Model):
    offering=models.ForeignKey(Offering)
    teacher=models.ForeignKey(User,related_name="offr_map_teacher_id")
    demand_slot_id=models.CharField(max_length=128,null=True)
    booked_date=models.DateTimeField(null=True)
    confirmation_date=models.DateTimeField(null=True)
    assigned_date=models.DateTimeField(null=True)
    dropped_date=models.DateTimeField(null=True)
    dropped_reason=models.CharField(max_length=1024, null=True)
    created_date=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.ForeignKey(User,null=True,related_name="offr_map_created_by")
    updated_date=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.ForeignKey(User,null=True,related_name="offr_map_updated_by")
    dropped_category=models.CharField(max_length=400, null=True)
class Course_combination_recommendation(models.Model):
    center = models.CharField(max_length=50,null=True, blank=True)
    board = models.CharField(max_length=50,null=True, blank=True)
    grade = models.CharField(max_length=50,null=True, blank=True)
    subject = models.CharField(max_length=50,null=True, blank=True)
    added_by = models.CharField(max_length=50,null=True, blank=True)


class Teachers(models.Model):
    user = models.ForeignKey(User, null=True)
    first_name = models.CharField(max_length=65, null=False)
    last_name = models.CharField(max_length=65, null=False)
    email = models.CharField(max_length=300, null=False)
    phone = models.CharField(max_length=50, null=False)
    added_by_id = models.CharField(max_length=65, null=False)
    added_by = models.CharField(max_length=128, null=True)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.CharField(max_length=128, null=True)
    updated_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class VideoAssignments(models.Model):
    board_name = models.CharField(max_length=300, null=False)
    grade = models.CharField(max_length=11, null=False)
    subject = models.CharField(max_length=300, null=False)
    topic = models.CharField(max_length=300, null=False)
    sub_topic = models.CharField(max_length=300, null=False)
    video_url = models.CharField(max_length=1024, null=False)
    status = models.CharField(max_length=64,choices=(('Submitted','Submitted'),('Under Review','Under Review'),('Approved','Approved'), ('Not Approved', 'Not Approved')),default='Submitted')
    added_by = models.ForeignKey(User, null=True, related_name='video_assignments_added_by')
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='video_assignments_updated_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)


class Offering_enrolled_students(models.Model):
    offering = models.CharField(max_length=11, db_index=True, null=False)
    student_id = models.CharField(max_length=11, null=False)
    # assignment_status = models.CharField(max_length=10,choices=(('0','0'),('1', '1')),default='0')

class Student_Upload_Assignments(models.Model):
    assignment_id = models.CharField(max_length=65, db_index=True, null=False)
    student_id = models.CharField(max_length=65, db_index=True, null=False)
    file_path = models.CharField(max_length=200, db_index=True, null=False)
    file_name = models.CharField(max_length=200, db_index=True, null=False)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    file_type = models.CharField(max_length=128,choices=(('file','file'),('img','img')), null=True, blank=True)


class DropTeacherReason(models.Model):
    category = models.CharField(max_length=300, null=False)
    reason = models.CharField(max_length=300, null=False)

class Homeworks(models.Model):
    student_id = models.CharField(max_length=65, null=False, blank=False)
    offering_id = models.CharField(max_length=65, null=False, blank=False)
    session_id = models.CharField(max_length=65, null=False, blank=False)
    topic_id = models.CharField(max_length=65, db_index=True, null=False)
    topic_comment = models.CharField(max_length=1024, blank=False, null=False)
    assignment_type = models.CharField(max_length=40, blank=False, null=False)
    assignment_details = models.CharField(max_length=1024, blank=False, null=False)
    status = models.CharField(max_length=40, choices=(('Assigned', 'Assigned'), ('Submitted', 'Submitted'), ('Reviewed', 'Reviewed'), ('Resubmit', 'Resubmit'), ('Completed', 'Completed')), default='Assigned')
    remarks = models.CharField(max_length=1024, null=True, blank=True)
    file_path = models.CharField(max_length=200, db_index=True, null=False)
    file_name = models.CharField(max_length=200, db_index=True, null=False)
    assignment_no = models.IntegerField(default=1)
    added_by = models.ForeignKey(User, null=True, related_name='assignments_added_by')
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='assignments_updated_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_submission_date = models.DateTimeField(null=True, blank=True)
    
class Homeworksdetails(models.Model):
    homework = models.ForeignKey(Homeworks, null=False, related_name='homeworks')
    student_id = models.CharField(max_length=65, null=False, blank=False)
    file_path = models.CharField(max_length=200, null=False, blank=False)
    file_name = models.CharField(max_length=200, null=False, blank=False)
    file_type = models.CharField(max_length=65, null=False, blank=False)
    added_on = models.DateTimeField(auto_now=True, null=True, blank=True)

class DigitalCenterStaff(models.Model):
    user = models.ForeignKey(User, related_name="user_id", null=False)
    center = models.ForeignKey(Center, related_name="center_id", null=True)
    digital_school = models.ForeignKey(DigitalSchool, related_name="digital_school_id", null=False)
    role = models.ForeignKey(Role, related_name="role_id", null=False)
    status = models.CharField(max_length=50, choices=(('Active', 'Active'), ('Inactive', 'Inactive')), default="Active")
    created_by = models.ForeignKey(User, null=True, related_name='dss_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='dss_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)


class DigitalPartnerCoursePreference(models.Model):
    digital_school = models.ForeignKey(DigitalSchool, related_name="dspcp_partner_course_pref", null=False)
    course = models.ForeignKey(Course, related_name="ds_partner_course_id", null=False)
    max_student_per_section = models.IntegerField(default=25)
    status = models.BooleanField()
    created_by = models.ForeignKey(User, null=True, related_name='dspcp_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='dspcp_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

class SystemSettings(models.Model):
    key = models.CharField(max_length=1024, null=False, blank=False)
    value = models.CharField(max_length=2048, null=True, blank=True)
    status = models.BooleanField()
    created_by = models.ForeignKey(User, null=True, related_name='ss_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='ss_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = ('System Settings')

    def __unicode__(self):
        return self.key


class CourseAttribute(models.Model):
    key = models.CharField(max_length=256, null=False, blank=False)
    value = models.CharField(max_length=500, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, related_name='ca_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='ca_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    course = models.ForeignKey(Course, related_name="ca_course_id", null=True)
    class Meta:
        verbose_name = ('Coure Attribute')

    def __unicode__(self):
        return self.key

class WorkStreamType(models.Model):
    name = models.CharField(max_length=256, null=True, blank=False)
    code = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive')), default="active")
    created_by = models.ForeignKey(User, null=True, related_name='wst_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='wst_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = ('Workstream Type')

    def __unicode__(self):
        return self.name

class ContentTypeMaster(models.Model):
    name = models.CharField(max_length=256, null=True, blank=False)
    code = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive')), default="active")
    created_by = models.ForeignKey(User, null=True, related_name='ctm_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='ctm_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    format = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = ('Content Type Master')

    def __unicode__(self):
        return self.name

class ContentHostMaster(models.Model):
    name = models.CharField(max_length=256, null=True, blank=False)
    code = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive')), default="active")
    created_by = models.ForeignKey(User, null=True, related_name='chm_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='chm_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    class Meta:
        verbose_name = ('Content Host Master')

    def __unicode__(self):
        return self.name

class ContentMetaAttributeType(models.Model):
    name = models.CharField(max_length=256, null=True, blank=False)
    code = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive')), default="active")
    workstream_type = models.ForeignKey(WorkStreamType,null=True,related_name="mat_workstream_type")
    created_by = models.ForeignKey(User, null=True, related_name='mat_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='mat_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Meta Attribute Type')

    def __unicode__(self):
        return self.name

class ContentAuthor(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    user = models.ForeignKey(User,null=True,related_name="ca_author_user", blank=True)
    status = models.CharField(max_length=50, choices=(('active', 'Active'), ('inactive', 'Inactive')), default="active")
    created_by = models.ForeignKey(User, null=True, related_name='car_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='car_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Content Author')

    def __unicode__(self):
        return self.name

class ContentDetail(models.Model):
    topic = models.ForeignKey(Topic, null=True, related_name='cd_topic_id')
    subtopic = models.ForeignKey(SubTopics,null=True,related_name="cd_sub_topic_id")
    name = models.CharField(max_length=256, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    url = models.CharField(max_length=2048, null=True, blank=True)
    url_host = models.ForeignKey(ContentHostMaster, null=True, related_name="cd_host_master_id")
    content_type = models.ForeignKey(ContentTypeMaster,null=True,related_name="cd_content_type_id")
    workstream_type = models.ForeignKey(WorkStreamType, null=True, related_name="cd_workstream_type_id")
    author = models.ForeignKey(ContentAuthor, null=True, related_name="cd_content_author_id")
    status = models.CharField(max_length=50, choices=(('approved', 'Approved'),('unapproved', 'Unapproved'), ('inactive', 'Inactive')), default="unapproved")
    priority = models.IntegerField(default=1)
    version = models.IntegerField(default=1)
    duration = models.IntegerField(default=0)
    is_primary = models.BooleanField()
    created_by = models.ForeignKey(User, null=True, related_name='cd_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='cd_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Content Detail')

    def __unicode__(self):
        return self.name

class ContentMetaAttribute(models.Model):
    key = models.CharField(max_length=256, null=True, blank=False)
    value = models.CharField(max_length=500, null=True, blank=False)
    status = models.BooleanField(default=True)
    content_detail = models.ForeignKey(ContentDetail,null=True,related_name="cma_content_detail_d")
    meta_attribute_type = models.ForeignKey(ContentMetaAttributeType, null=True, related_name="cma_meta_attribute_id")
    created_by = models.ForeignKey(User, null=True, related_name='cma_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='cma_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Content Meta Attribute')

    def __unicode__(self):
        return self.key


class DigitalSchool_Location_Preference(models.Model):
    digital_school = models.ForeignKey(DigitalSchool, related_name="dlp_digital_school_id", null=False)
    state = models.ForeignKey(State, null=True, related_name='dlp_state',blank=True)
    pincode = models.ForeignKey(Pincode, null=True, related_name='dlp_pincode', blank=True)
    state_code = models.CharField(max_length=256, null=True, blank=False)
    pincode_key = models.CharField(max_length=256, null=True, blank=False)
    status = models.CharField(max_length=50, choices=(('Active', 'active'), ('Inactive', 'inactive')), default="active")
    created_by = models.ForeignKey(User, null=True, related_name='dlp_created_by',blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='dlp_updated_by',blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    sel_type = models.CharField(max_length=50, choices=(('1', 'All'), ('2', 'custom')), default="2")
    class Meta:
        verbose_name = ('DigitalSchool Location Preference')

    def __unicode__(self):
        return self.pincode_key


class TvBroadCast(models.Model):
    state = models.CharField(max_length=256, null=False, blank=False)
    student_class = models.CharField(max_length=256, null=False, blank=False)
    subject = models.CharField(max_length=256, null=False, blank=False)
    chapter_name = models.CharField(max_length=256, null=False, blank=False)
    date = models.DateTimeField(null=True, blank=True)
    chanel = models.TextField(max_length=1000, null=False, blank=False)



class UserDevice(models.Model):
    deviceId =  models.CharField(max_length=1024,null=False)
    status = models.BooleanField(default=True)
    user_type = models.CharField(max_length=50, choices=(('guardian', 'guardian'),('others', 'others'),('authuser', 'authuser')), default="guardian")
    belongs_to_id =  models.IntegerField(default=-1,null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True, null=False)
    updated_on = models.DateTimeField(auto_now=True, null=False)
    device_type = models.CharField(max_length=50, choices=(('mobile', 'mobile'), ('web', 'web')), default="mobile")
    created_by = models.ForeignKey(User, null=True, related_name='usd_created_by', blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='usd_updated_by', blank=True)
    os_type = models.CharField(max_length=50, choices=(('ios', 'ios'), ('android', 'android')), default="android")
    is_test = models.BooleanField(default=True)

    class Meta:
        verbose_name = ('User Devices')

    def __unicode__(self):
        return self.belongs_to + " "+self.type


class Faq(BaseModel):

    """To store charset having bytes>3 : change column charset
        example:    ALTER TABLE `evldb`.`web_faq` 
                    CHANGE COLUMN `question` `question` TEXT CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' NOT NULL ,
                    CHANGE COLUMN `answer` `answer` TEXT CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' NOT NULL ;

    Returns:
        str: question
    """

    category = models.CharField(max_length=1024)
    question = models.TextField(null=False, blank=False)
    answer = models.TextField(null=False, blank=False)
    language = models.ForeignKey(Language , null=False,blank=False, related_name="faq_language_id")
    parent_faq = models.ForeignKey('self', null=True,blank=True, related_name="faq_parent_id")
    status = models.BooleanField(default=True)


    def __unicode__(self):
        if self.language.name !='English' or self.parent_faq:
            # return  '%s - %s' % (self.language, self.parent_faq.question)
            return '---------------------DO NOT SELECT' 

        return '%s - %s' % (self.category, self.question)


class FLTeacher_Content_View_Status(BaseModel):
    content_detail = models.ForeignKey(ContentDetail, null=True, blank=True, related_name='fsvs_content_id')
    status = models.CharField(max_length=50, choices=(('1', 'Viewed'), ('2', 'Pending'), ('3', 'Inprogress')),default="1")
    progress = models.IntegerField(default=0)
    number_of_times_viewed = models.IntegerField(default=1)
    offering = models.ForeignKey(Offering, null=True, related_name="fsvs_offering", blank=True)
    user = models.ForeignKey(User, null=True, related_name='fsvs_auth_user', blank=True)
    topic = models.ForeignKey(Topic, null=True, blank=True, related_name="fsvs_topic")
    subtopic = models.ForeignKey(SubTopics, null=True, blank=True, related_name="fsvs_sub_topic")
    offering = models.ForeignKey(Offering, null=True, related_name="fcvs_offering", blank=True)

    class Meta:
        verbose_name = ('FLTeacher_Content_View_Status')

    def __unicode__(self):
        return self.user.first_name
    
class AlertUser(BaseModel):
    role = models.ForeignKey(Role, null=True, blank=True, unique=True, related_name='AlertUsersRoles')
    user = models.ManyToManyField(User, null=True, blank=True)
    is_active = models.BooleanField(default=True)


class Content_Demand(BaseModel):
    topic = models.ForeignKey(Topic, null=True, blank=True, related_name="content_demand_topic")
    subtopic = models.ForeignKey(SubTopics, null=True, blank=True, related_name="content_demand_subtopic")
    workstream = models.ForeignKey(WorkStreamType, null=True, blank=True, related_name="content_demand_workstream")
    content_type = models.ForeignKey(ContentTypeMaster, null=True, blank=True, related_name="content_demand_content_type")
    status = models.IntegerField(choices=((1,'Not Started'), (2,'Booked'), (3,'Assigned'), (4,'Submitted'), (5,'In Review'), (6,'Approved'), (7,'Resubmit'), (8,'Published'), (9,'Inactive')), default=1)
    author = models.ForeignKey(User, null=True, blank=True, related_name="content_demand_author")
    reviewer = models.ForeignKey(User, null=True, blank=True, related_name="content_demand_reviewer")
    url = models.CharField(max_length=1024, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    comment = models.CharField(max_length=1024, null = True, blank=True)


    def __unicode__(self):
        return str(self.subtopic.id)
    

class Content_Demand_Review_Checklist(BaseModel):
    workstream = models.ForeignKey(WorkStreamType, null=True, blank=True)
    checklist = models.CharField(max_length=1024, null=True, blank=True)


class Content_Demand_Checklist_Comments(BaseModel):
    content_demand = models.ForeignKey(Content_Demand, null=True, blank=True, related_name='checklist_content_demand')
    checklist = models.ForeignKey(Content_Demand_Review_Checklist, null=True, blank=True, related_name='checklist_checks')
    answers = models.BooleanField(default=True)
    comments = models.CharField(max_length=1024, null=True, blank=True)


class Offering_Enrolled_Students_History(BaseModel):
    offering = models.ForeignKey(Offering, null=True, blank=True)
    student = models.ForeignKey(Student, null=True, blank=True)
    assignment_status = models.IntegerField(choices=((1, 'Endolled'), (2, 'De-Enrolled')), default=1)