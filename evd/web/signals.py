from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from models import *

@receiver(post_save, sender=Session)
def set_active_teacher(sender, instance, **kwargs):
    #teacher_obj = Session.objects.filter(offering=instance.offering).order_by('-date_start')[0].teacher
    teacher_obj = instance.teacher
    instance.offering.active_teacher = teacher_obj
    instance.offering.save()
    userp = UserProfile.objects.get(user=teacher_obj)
    role_pref_obj = RolePreference.objects.filter(userprofile = userp, role_id__in=[1,2])
    if role_pref_obj:
        role_pref_obj = role_pref_obj[0]
        role_pref_obj.role_status = 'Active'
        role_pref_obj.save()
    return "success"
