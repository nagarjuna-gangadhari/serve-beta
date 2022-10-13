from django.core.management.base import BaseCommand
from web.models import UserProfile, Role, RolePreference, OnboardingStep, OnboardingStepStatus

class Command(BaseCommand):
    ''' Update Users role from Content Admin to Well Wisher for those, who had only Content Admin Role in UserProfile_role or UserProfile_pref_role tables is done in other file, but we missed to update their RolePreference Table
        as well as OnBoardingStepStatus Tables. In this Function we are updating them. '''
    def handle(self, *args, **options):
        userprofile_id_list = [228,1004,1685,1788,2701,2730,2800,2841,3112,5236,8381,9012,10131,10137,11534,13259,13265,13282,13747,13871,13884,13906,13913,14105,14152,14236,17334,17512,19362]
        for upid in userprofile_id_list:
            userp = UserProfile.objects.get(id=upid)
            print 'userp name is :',userp.user.username, ' userp id is :',userp.id
            try:
                rolepref = RolePreference.objects.get(userprofile_id=userp.id,role_id=5)
                rolepref.role_id = 4
                rolepref.role_status = 'Active'
                rolepref.role_outcome = 'Recommended'
                rolepref.save()
                onboard_status = OnboardingStepStatus.objects.filter(role_preference_id=rolepref.id)
                if onboard_status:
                    i=1
                    for obs in onboard_status:
                        if i == 1:
                            obs.step_id=10
                            obs.status=True
                            obs.save()
                            print 'Onboarding Step status is updated. Id is : ',obs.id
                        else:
                            print 'Onboarding Step status is deleted. Id is : ', obs.id
                            obs.delete()
                        i +=1
                else:
                    role = Role.objects.get(name='Well Wisher')
                    steps = role.onboardingstep_set.all()
                    for step in steps:
                        on_board_step_status = OnboardingStepStatus.objects.create(role_preference=rolepref, step=step, status=True)
                        on_board_step_status.save()
                        print 'Onboarding Step status is created. Id is : ', on_board_step_status.id
            except RolePreference.DoesNotExist:
                print 'RolePreference matching query does not Exist'
                pass