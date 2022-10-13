from django.db import models
from django.utils import timezone
from web.models import *
from django.contrib.auth.models import User


class SettingsGroup(models.Model):
    '''Master Settings Group information will be stored here'''
    group_name = models.CharField(max_length=128)
    group_title = models.CharField(max_length=128)
    group_description = models.CharField(max_length=1024,null=True)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(User, null=True, related_name='settings_group_added_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='settings_group_updated_by')

    def __unicode__(self):
        return self.group_name

class SettingsGroupItems(models.Model):
    settings_group = models.ForeignKey(SettingsGroup,null=True)
    input_type = models.CharField(max_length=128)
    input_sub_type = models.CharField(max_length=128, null=True)
    input_name = models.CharField(max_length=128)
    input_label = models.CharField(max_length=128)
    input_order = models.CharField(max_length=128, null=True)
    input_rule = models.CharField(max_length=512,null=True)
    input_values = models.CharField(max_length=512)
    default_value = models.CharField(max_length=128, null=True)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(User, null=True, related_name='settings_grp_items_added_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='settings_grp_items_updated_by')


class RoleDefaultSettings(models.Model):
    role = models.ForeignKey(Role,null=True)
    settings_grp_items = models.ForeignKey(SettingsGroupItems,null=True)
    name = models.CharField(max_length=128)
    values = models.CharField(max_length=512)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(User, null=True, related_name='role_settings_added_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='role_settings_updated_by')
    is_removed = models.BooleanField(default=False)


class UserSettings(models.Model):
    user = models.ForeignKey(User,null=True)
    settings_grp_items = models.ForeignKey(SettingsGroupItems, null=True)
    name = models.CharField(max_length=128)
    values = models.CharField(max_length=512)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(User, null=True, related_name='user_settings_added_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='user_settings_updated_by')
    is_removed = models.BooleanField(default=False)


class AppreciationReason(models.Model):
    reason_type = models.CharField(choices=(('appreciation','Appreciation'),('others','Others')),max_length=32,null=True)
    for_whom = models.CharField(choices=(('volunteer','Volunteer'),('student','Student')),max_length=32,null=True)
    reason = models.CharField(max_length=128)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(User, null=True, related_name='appreciation_reason_added_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='appreciation_reason_updated_by')

    def __unicode__(self):
        return self.reason


class Stickers(models.Model):
    sticker_type = models.CharField(choices=(('appreciation', 'Appreciation'), ('others', 'Others')), max_length=32,null=True)
    for_whom = models.CharField(choices=(('volunteer', 'Volunteer'), ('student', 'Student')), max_length=32, null=True)
    sticker_name = models.CharField(max_length=128)
    sticker_path = models.FileField(upload_to='static/uploads/stickers', null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    added_by = models.ForeignKey(User, null=True, related_name='sticker_added_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='sticker_updated_by')

    def __unicode__(self):
        return self.sticker_name


class DemandShareShortUrl(models.Model):
    filtered_data = models.TextField(max_length=2048)
    unique_url_path = models.CharField(max_length=256)
    added_by = models.ForeignKey(User, related_name="share_url_added_by")
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Certificate(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    center = models.ForeignKey(Center, null=True, blank=True)
    sessions = models.IntegerField(null=True, blank=True)
    ay = models.ForeignKey(Ayfy, null=True, blank=True)
    is_alerted = models.BooleanField(default=0)
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, related_name='certificate_added_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='certificate_updated_by')

    def __unicode__(self):
        return str(self.user.id)
