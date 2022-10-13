from django.core.management.base import BaseCommand
from web.models import UserProfile, Role

class Command(BaseCommand):
    ''' Update Users role from Content Admin to Well Wisher for those, who had only Content Admin Role in UserProfile_role or UserProfile_pref_role tables  '''
    def handle(self, *args, **options):
        users = UserProfile.objects.all()
        remove_role = Role.objects.get(name='Content Admin')
        add_role = Role.objects.get(name='Well Wisher')
        for user in users:
            if (remove_role in user.role.all() or remove_role in user.pref_roles.all()) and (user.pref_roles.all().count() == 1):
                print 'role name is ', user.role.all(), ' preferred role name is ', user.pref_roles.all()
                user.role.clear()
                user.pref_roles.clear()
                user.role.add(add_role)
                user.pref_roles.add(add_role)
                user.save()
                print 'user id is ', user.id, ' is update with Wellwisher role'