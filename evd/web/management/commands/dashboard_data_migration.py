from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('error.log', 'w+') as err:
            users = User.objects.all()
            success_count = 0
            total_count = users.count()
            for user in users:
                try:
                    userp = user.userprofile
                    if userp.profile_complete_status == 'Incomplete':
                        userp.profile_completion_status = False
                    else:
                        userp.profile_completion_status = True
                    self.create_onboardings(userp, err)
                    self.update_onboardings(userp, err)
                    print 'Successfully Updated user with ID : %s \n' %str(user.id)
                    success_count += 1

                except ObjectDoesNotExist:
                    print 'Requested User has no userprofile'
                    print user.id
                    err.write('Error processing user_id'+str(userp.id)+'\n')
                    err.write('Requested User has no userprofile')
                    continue
            print 'Total Users : ' + str(total_count)
            print 'Migration Success for users : ' + str(success_count)

    def create_onboardings(self, userp, errorlog):
        #Role onboarding
        pref_roles = userp.pref_roles.all()
        for role in pref_roles:
            role_preference, created = RolePreference.objects.get_or_create(userprofile=userp, role=role)
            steps = role.onboardingstep_set.all()
            for step in steps:
                step_status, creat = OnboardingStepStatus.objects.get_or_create(role_preference=role_preference, step=step)
            try:
                userp.save()
            except Exception as e:
                print e
                errorlog.write('Error processing user_id'+str(userp.id)+'\n')
                errorlog.write(str(e)+'\n')
                continue

    def update_onboardings(self, userp, errorlog):
        pref_roles = userp.pref_roles.all()
        discussion_outcome = userp.dicussion_outcome

        def mark_role_status(onboarding,status):
            if onboarding.role.name == 'Well Wisher':
                onboarding.role_outcome = 'Recommended'
                onboarding.save()
            else:
                onboarding.role_outcome = status
                onboarding.save()

        def save_step_status(step):
            step.status = True
            step.save()

        for role in pref_roles:
            role_onboarding = userp.rolepreference_set.filter(role=role)[0]
            if discussion_outcome == 'Not Scheduled':
                mark_role_status(role_onboarding,'Not Started')
            elif discussion_outcome == 'Recommended for Teaching':
                if role.name == 'Teacher':
                    mark_role_status(role_onboarding,'Recommended')
                    steps = role_onboarding.onboardingstepstatus_set.all()
                    if userp.self_eval:
                        se = steps.filter(step__stepname = 'Self Evaluation')[0]
                        save_step_status(se)
                    tsd = steps.filter(step__stepname = 'Teacher Selection Discussion')[0]
                    save_step_status(tsd)
                else:
                    mark_role_status(role_onboarding,'Not Started')
            elif discussion_outcome == 'Recommended for Admin':
                if role.name == 'Center Admin':
                    mark_role_status(role_onboarding,'Recommended')
                    steps = role_onboarding.onboardingstepstatus_set.all()
                    if userp.self_eval:
                        se = steps.filter(step__stepname = 'Self Evaluation')[0]
                        save_step_status(se)
                    asd = steps.filter(step__stepname = 'Admin Selection Discussion')[0]
                    save_step_status(asd)
                else:
                    mark_role_status(role_onboarding,'Not Started')
            elif discussion_outcome == 'Recommended for Content' or discussion_outcome == 'RFC':
                if role.name == 'Content Developer':
                    mark_role_status(role_onboarding,'Recommended')
                else:
                    mark_role_status(role_onboarding,'Not Started')
            elif discussion_outcome == 'Recommended for Alternate role' or discussion_outcome == 'Others':
                if role.name == 'Teacher':
                    mark_role_status(role_onboarding,'Recommended for Alternate role')
                    steps = role_onboarding.onboardingstepstatus_set.all()
                    if userp.self_eval:
                        se = steps.filter(step__stepname = 'Self Evaluation')[0]
                        save_step_status(se)
                    tsd = steps.filter(step__stepname = 'Teacher Selection Discussion')[0]
                    save_step_status(tsd)
                else:
                    mark_role_status(role_onboarding,'Not Started')
            else:
                continue
        try:
            userp.save()
        except Exception as e:
            errorlog.write('Error processing user_id'+str(userp.id)+'\n')
            errorlog.write(str(e)+'\n')
            print e
