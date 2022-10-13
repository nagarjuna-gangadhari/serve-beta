from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class ApiSession(models.Model):
    user = models.ForeignKey(User, null=True, db_index=True)
    session_key = models.CharField(max_length=500, null=False)
    expiry_time = models.DateTimeField(null=False)
    status = models.BooleanField()
    type = models.CharField(max_length=50, choices=(
        ('guardian', 'guardian'), ('others', 'others')), default="others")
    belongs_to = models.IntegerField(default=-1, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        verbose_name = ('Mobile user session')

    def __unicode__(self):
        return self.session_key


class State(models.Model):
    name = models.CharField(max_length=100, null=False)
    code = models.CharField(max_length=255, null=False)
    status = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=False)

    def __unicode__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=255, null=False)
    code = models.CharField(max_length=255, null=False)
    status = models.BooleanField()
    created_on = models.DateTimeField(auto_now_add=True, null=False)

    def __unicode__(self):
        return self.name


class Pincode(models.Model):
    pincode = models.CharField(max_length=256, null=True, blank=False)
    district = models.CharField(max_length=500, null=True, blank=False)
    taluk = models.CharField(max_length=500, null=True, blank=False)
    state = models.ForeignKey(
        State, null=True, related_name='pincode_state', blank=True)
    state_code = models.CharField(max_length=256, null=True, blank=False)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, null=True, related_name='pincode_created_by', blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(
        User, null=True, related_name='pincode_updated_by', blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = ('Pincode')

    def __unicode__(self):
        return self.pincode


class UserOtp(models.Model):
    mobile = models.CharField(max_length=100, null=False)
    otp = models.CharField(max_length=25, null=False)
    expiry_time = models.DateTimeField(null=False)
    status = models.BooleanField(default=True)
    type = models.CharField(max_length=50, choices=(
        ('guardian', 'guardian'), ('user', 'user'), ('others', 'others')), default="others")
    belongs_to = models.IntegerField(default=-1, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        verbose_name = ('User Otp')

    def __unicode__(self):
        return self.mobile + " " + self.otp


class BaseModel(models.Model):
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='%(class)s_created_by')
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='%(class)s_updated_by')
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
        
     


