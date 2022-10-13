from django.db import models

# Create your models here.

class FcmKey(models.Model):
    user_id = models.CharField(max_length=50, null=True, blank=True)
    fcm_key = models.TextField(blank=True)

class StudentFcmKey(models.Model):
    student_id = models.CharField(max_length=50, null=True, blank=True)
    fcm_key = models.TextField(blank=True)   
    device_id =  models.TextField(blank=True)   

