from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from web.models import *
from genutilities.models import *
from student.models import *

# Create your models here.

class Alerts(models.Model):

    message         = models.TextField(blank=True)
    type            = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    status          = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    status_message  = models.TextField(blank=True, null=True)
    recipients      = models.TextField(blank=True, db_index=True)
    user            = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    dt_added        = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated      = models.DateTimeField(auto_now=True, null=True, blank=True)
    category        = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'Alerts'


class PushToken(models.Model):
    push_token =  models.CharField(max_length=1024,null=False)
    status = models.BooleanField(default=True)
    type = models.CharField(max_length=50, choices=(('guardian', 'guardian'),('others', 'others'),('authuser', 'authuser')), default="guardian")
    belongs_to_id =  models.IntegerField(default=-1,null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True, null=False)
    updated_on = models.DateTimeField(auto_now_add=True, null=False)
    device_type = models.CharField(max_length=50, choices=(('mobile', 'mobile'), ('web', 'web')), default="mobile")
    platform_type = models.CharField(max_length=50, choices=(('ios', 'ios'), ('android', 'android')), default="android")
    created_by = models.ForeignKey(User, null=True, related_name='put_created_by', blank=True)
    device = models.ForeignKey(UserDevice, null=True, related_name='put_user_device', blank=True)

    class Meta:
        verbose_name = ('Mobile Push Tokens')

    def __unicode__(self):
        return self.push_token

class PushNotificationHistory(models.Model):
    student = models.ForeignKey(Student, null = True, blank= True,related_name="pnh_student_id")
    guardian = models.ForeignKey(Guardian, null=True,blank= True)
    auth_user = models.ForeignKey(User, null=True, related_name='pnh_auth_user', blank=True)
    status = models.CharField(max_length=50, choices=(( '1','success'),('0','failed')), default="1")
    type = models.CharField(max_length=50, choices=(('guardian', 'guardian'),('others', 'others'),('authuser', 'authuser')), default="guardian")
    created_on = models.DateTimeField(auto_now_add=True, null=False)
    updated_on = models.DateTimeField(auto_now=True, null=False)
    push_token = models.ForeignKey(PushToken, null=False)
    created_by = models.ForeignKey(User, null=True, related_name='pnh_created_by', blank=True)
    payload = models.CharField(max_length=1024, null=True,blank= True)
    title = models.CharField(max_length=256, null=True,blank= True)
    body = models.CharField(max_length=256, null=True, blank=True)
    gcm_response = models.CharField(max_length=1024, null=True, blank=True)
    message_type = models.CharField(max_length=256, null=True, blank=True)
    class Meta:
        verbose_name = ('Push Notification History')

    def __unicode__(self):
        return self.type


