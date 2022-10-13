from django.core.management.base import BaseCommand
from web.models import UserProfile, RolePreference, Role, Center
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, *args, **options):
        ca = Role.objects.get(id=6)
        centers = Center.objects.all().exclude(Q(status='Inactive') | Q(status='Closed'))
        for center in centers:
            print center.name
            ca_userprofile = center.assistant
            if ca_userprofile:
                try :
                    ca_roles = ca_userprofile.userprofile.role.all()
                    ca_pref_roles = ca_userprofile.userprofile.pref_roles.all()
                    if ca in ca_userprofile.userprofile.role.all():
                        try:
                            role_preference = RolePreference.objects.get(userprofile_id=ca_userprofile.userprofile.id,role_id=ca.id)
                            if (role_preference.role_status=='New' or role_preference.role_status=='Active') and (role_preference.role_outcome=='Not Started' or role_preference.role_outcome=='Inprocess' or role_preference.role_outcome=='Recommended'):
                                role_preference.role_status = 'Active'
                                role_preference.role_outcome = 'Recommended'
                                role_preference.save()
                                print role_preference.role_status, role_preference.role_outcome
                                print 'RolePreference is updated for the user_id : %s' % ca_userprofile.id
                        except RolePreference.DoesNotExist:
                            print 'RolePreference matching query Doesnot exist for the user_id : %s' %ca_userprofile.id
                            role_preference = RolePreference.objects.create(userprofile=ca_userprofile.userprofile,role=ca,availability=True,role_status='Active',role_outcome = 'Recommended')
                            role_preference.save()
                            print 'RolePreference is added for the user_id : %s' % ca_userprofile.id
                    elif ca in ca_userprofile.userprofile.pref_roles.all():
                        try:
                            role_preference = RolePreference.objects.get(userprofile_id=ca_userprofile.userprofile.id,role_id=ca.id)
                            if (role_preference.role_status == 'New' or role_preference.role_status == 'Active') and (role_preference.role_outcome == 'Not Started' or role_preference.role_outcome == 'Inprocess' or role_preference.role_outcome=='Recommended'):
                                role_preference.role_status='Active'
                                role_preference.role_outcome='Recommended'
                                role_preference.save()
                                print role_preference.role_status, role_preference.role_outcome
                                print 'RolePreference is updated for the user_id : %s' % ca_userprofile.id
                        except RolePreference.DoesNotExist:
                            print 'RolePreference matching query Doesnot exist for the user_id : %s' %ca_userprofile.id
                            role_preference = RolePreference.objects.create(userprofile=ca_userprofile.userprofile,role=ca, availability=True,role_status='Active',role_outcome='Recommended')
                            role_preference.save()
                            print 'RolePreference is added for the user_id : %s' % ca_userprofile.id
                    else:
                        print 'No Roles or Preferred Roles found for the user_id : %s' % ca_userprofile.id
                except RolePreference.DoesNotExist:
                    print 'No Roles or Preferred Roles found for the user_id : %s' % ca_userprofile.id
            else:
                print 'No Class assistant for the center : %s' % center.name