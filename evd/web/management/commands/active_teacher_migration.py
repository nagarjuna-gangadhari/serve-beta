from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('error.log', 'w+') as err:
            acive_teacher_list = []
            teacher_userp_obj = RolePreference.objects.filter(role_outcome='Recommended',role_id=1).values_list('userprofile_id',flat=True)
            offering_list = Offering.objects.values_list('id',flat=True)
            for offer in offering_list:
                sessions_list = Session.objects.filter(offering_id=offer).values_list('teacher_id',flat=True).order_by('-id')
                
                if sessions_list:
                    acive_teacher_list.append(sessions_list[0])
                    offer_obj = Offering.objects.filter(id=offer).all()[0]
                    offer_obj.active_teacher_id = sessions_list[0]
                    offer_obj.save()
            for teacher in teacher_userp_obj:
                role_pref_obj = RolePreference.objects.filter(role_id=1,userprofile_id=teacher).all()[0]
                if teacher in acive_teacher_list:
                    print acive_teacher_list
                    role_pref_obj.role_status = 'Active'
                    role_pref_obj.save()
                elif role_pref_obj.role_status != 'New':
                    role_pref_obj.role_status = 'Inactive'
                    role_pref_obj.save()
            success_count = 0
        return "success"
