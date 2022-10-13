from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from web.models import *
# from configs.models import AppreciationReason, Stickers

class UserWikividya(models.Model):
    user = models.ForeignKey(User,null=True, blank=True)
    user_password = models.TextField(max_length=2048, null=True, blank=True)
    wiki_username = models.CharField(max_length=1024, null=True, blank=True)
    token = models.TextField(blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=1024, null=True, blank=True)
    updated_by = models.CharField(max_length=1024, null=True, blank=True)
    
    
class TeachingSoftwareDetails(models.Model):
    software_name = models.CharField(max_length=1024, null=True, blank=True)
    software_link = models.CharField(max_length=1024, null=True, blank=True)
    created_by = models.ForeignKey(User,null=True,related_name='teaching_software_created_by')
    updated_by = models.ForeignKey(User,null=True,related_name='teaching_software_updated_by')
    created_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    
class StudentLog(models.Model):
    student = models.ForeignKey('web.Student', null = True, blank= True)
    current_school = models.CharField(max_length=50,null=True, blank=True)
    current_grade = models.CharField(max_length=50, null=True, blank=True)
    family_income = models.IntegerField(max_length=5, null=True )
    event_name = models.CharField(max_length=50,null=True, blank=True)
    notes_onperformance = models.TextField(max_length=2048, null=True, blank=True)
    event_description = models.TextField(max_length=2048, null=True, blank=True)
    achievments = models.TextField(max_length=2048, null=True, blank=True)

class SchoolViability(models.Model):
    school_code = models.CharField(max_length=50,null=True, blank=True) 
    school_name = models.CharField(max_length=50,null=True, blank=True)
    village_name = models.CharField(max_length=50,null=True, blank=True)
    distirict_name = models.CharField(max_length=50,null=True, blank=True)
    state = models.CharField(max_length=50,null=True, blank=True)
    headmaster_name = models.CharField(max_length=50,null=True, blank=True)
    no_of_teachers = models.IntegerField(max_length=5, null=True )
    no_of_students = models.IntegerField(max_length=5, null=True )
    servive_provider = models.CharField(max_length=50,null=True, blank=True)
    connection_type = models.CharField(max_length=50,null=True, blank=True)
    download_speed = models.CharField(max_length=50,null=True, blank=True)
    upload_speed = models.CharField(max_length=50,null=True, blank=True)
    date_of_entry = models.DateTimeField(null=True, blank=True)
    system_availability = models.CharField(max_length=50,null=True, blank=True)
    latitude = models.DecimalField( max_digits=5, decimal_places=2)
    longitude = models.DecimalField( max_digits=5, decimal_places=2)
    created_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


update_history_log_type_choices = (
    (1,'PartnerSchool'), # if PartnerSchool verification, then referred_table_id will have School ID
    (2,'Teacher'),
    (3,'Center'),
    (4,'Student')
)

class UpdateHistoryLog(models.Model):
    referred_table_id = models.IntegerField() # ID of the school or teacher or etc
    log_type = models.CharField(max_length=64, choices=update_history_log_type_choices)
    other_info = models.TextField(null=True,blank=True)  #Json meta info will be stored in the this table
    added_by = models.ForeignKey(User, null=True)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class Recognition(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    reason = models.ForeignKey('configs.AppreciationReason',null=True )
    sticker = models.ForeignKey('configs.Stickers', null=True)
    detailed_reason = models.CharField(max_length=2048, null=True, blank=True)
    offering = models.ForeignKey('web.Offering' , null=True)
    added_by = models.ForeignKey(User, null=True)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class VolOfMonth(models.Model):
    elected_user = models.ForeignKey(User,null=True, blank=True)
    category     = models.CharField(max_length=50,null=True, blank=True)
    writeup      = models.TextField(max_length=2048, null=True, blank=True)
    month        = models.IntegerField(max_length=5, null=True )
    year         = models.IntegerField(max_length=5, null=True )
    added_by     = models.ForeignKey(User, null = True, related_name = 'added_by')
    added_on     = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by   = models.ForeignKey(User, null = True, related_name = 'updated_by')
    updated_on   = models.DateTimeField(auto_now=True, null=True, blank=True)
    status       = models.CharField(max_length=50,choices=(('Nominated', 'Nominated'), ('Approved', 'Approved'), ('Not Approved', 'Not Approved')), default="Rural",null=True, blank=True)
    
    
class RubaruRegistration(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    designation = models.CharField(max_length=250,null=True, blank=True)
    email = models.CharField(max_length=50,null=True, blank=True,unique=True)
    organization = models.CharField(max_length=250,null=True, blank=True)
    allergies = models.CharField(max_length=250,null=True, blank=True)
    comment = models.CharField(max_length=250,null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'RubaruRegistraion'
    

class CountryStateCities(models.Model):
    custom_country_id = models.CharField(max_length=10, null=False, blank=False)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    country_name = models.CharField(max_length=100, null=False, blank=False)
    country_phonecode = models.CharField(max_length=10, null=True, blank=True)
    custom_state_id = models.CharField(max_length=10, null=False, blank=False)
    state_name = models.CharField(max_length=100, null=False, blank=False)
    custom_city_id = models.CharField(max_length=10, null=False, blank=False)
    city_name = models.CharField(max_length=100, null=False, blank=False)

    class Meta:
        db_table = 'CountryStateCities'

class CenterActivityType(models.Model):
    activity_type = models.CharField(max_length=100, null=False, unique=True)
    created_by = models.ForeignKey(User, null=True, related_name='CenterActivityType_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='CenterActivityType_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)    
    status = models.IntegerField(choices=((1, "Approved"), (2, "Not Approved")), default=1)
    is_active = models.BooleanField(default=True)

class CenterActivityTypeForm(models.Model):
    activity_type = models.ForeignKey('CenterActivityType', null=False, blank=False, on_delete=models.CASCADE)
    label = models.CharField(max_length=100, null=False, blank=False)
    type = models.CharField(max_length=100, null=False, blank=False)
    choices = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='CenterActivityTypeForm_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='CenterActivityTypeForm_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)    
    status = models.IntegerField(choices=((1, "Approved"), (2, "Not Approved")), default=1)
    is_active = models.BooleanField(default=True)

class CenterActivity(models.Model):
    center = models.ForeignKey('web.Center', null=True)
    user = models.ForeignKey(User, null=True)
    activity = models.ForeignKey(CenterActivityType, null=False)
    status = models.IntegerField(choices=((1, "Approved"), (2, "Not Approved")), default=1)
    comment = models.CharField(max_length=2048, null=True, blank=True) # Can contain images using s3 bucket
    activity_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='CenterActivities_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='CenterActivities_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)    
    values = models.TextField(null=False, blank=False) # dict of id to value
    is_active = models.BooleanField(default=True)

class CenterActivityImage(models.Model):
    activity = models.ForeignKey(CenterActivity, null=False, blank=False, on_delete=models.CASCADE)
    image = models.ForeignKey('web.UserDocument', null=False, blank=False, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=False, related_name='CenterActivityImages_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='CenterActivityImages_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)    
    status = models.IntegerField(choices=((1, "Approved"), (2, "Not Approved")), default=1)

