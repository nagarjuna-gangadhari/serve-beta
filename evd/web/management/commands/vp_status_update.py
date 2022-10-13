from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('vp_status_update.log', 'w+') as err:
            err.write("in \n")
            today = datetime.datetime.utcnow()+ datetime.timedelta(days=0, hours=5, minutes=30)
            vp_interval = Setting.objects.get(name="Volunteer Processing").duration
            vp_objs = VolunteerProcessing.objects.all()
            for vp_obj in vp_objs:
                try:
                    role_pref_obj = RolePreference.object.get(userprofile=vp_obj.user.userprofile, role=vp_obj.role)
                    #latest_date = role_pref_obj.date_updated
                    if role_pref_obj.outcome == "Not Started":
                        latest_date = role_pref_obj.dt_updated
                    else:
                        latest_step = OnboardingStepStatus.objects.filter(role_preference=role_pref_obj).order_by('-date_completed')[0]
                        latest_date = latest_step.date_completed
                    if not latest_date:
                        latest_date = vp_obj.user.last_login

                    if latest_date + datetime.timedelta(days=vp_interval, hours=5, minutes=30) > today:
                        vp_obj.status = 'Not Progressing'
                        vp_obj.save()

                        err.write(str(vp_obj.id) + "--" + str(vp_obj.user.id) + "--" + str(vp_obj.role.id) + "\n\n")
                except:
                    pass

        return "success"
