from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('error.log', 'w+') as err:
            users = User.objects.filter(userprofile__pref_roles__name = 'Content Developer', userprofile__profile_completion_status=True)
            for user in users:
                try:
                    userp = user.userprofile
                    self.create_onboardings(userp, err)
                    print 'Successfully Updated user with ID : %s \n' %str(user.id)

                except ObjectDoesNotExist:
                    print 'Requested User has no userprofile'
                    print user.id
                    err.write('Error processing user_id'+str(userp.id)+'\n')
                    err.write('Requested User has no userprofile')
                    continue
            print "done"

    def create_onboardings(self, userp, errorlog):
        pref_roles = userp.pref_roles.filter(name="Content Developer")

        role_preference, rol_pre = RolePreference.objects.get_or_create(userprofile=userp, role=pref_roles[0])
        role_preference.role_onboarding_status = 0
        if role_preference.role_outcome == "Recommended":
            role_preference.role_outcome = "Inprocess"
        #steps = pref_roles[0].onboardingstep_set.all()

        step_status1, se = OnboardingStepStatus.objects.get_or_create(role_preference=role_preference, step_id=11)
        step_status2, red = OnboardingStepStatus.objects.get_or_create(role_preference=role_preference, step_id=8)
        step_status1.status = 0
        step_status2.status = 0

        try:
            userp.save()
            role_preference.save()
            step_status1.save()
            step_status2.save()
        except Exception as e:
            print e
            errorlog.write('Error processing user_id'+str(userp.id)+'\n')
            errorlog.write(str(e)+'\n')
