from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('availability_log.log', 'w+') as err:
            err.write("availability log\n")
            role_pref_objects = RolePreference.objects.filter(Q(role_id = 1), Q(role_status = 'New') | Q(role_status = 'Active'))
            i = 0
            for role_pref in role_pref_objects:
                i = i+1
                role_pref.availability = True
                role_pref.save()
                err.write( str(role_pref.id) + "-" + str(role_pref.role_status) + "-" + str(role_pref.availability) + "\n")
            err.write(str(i))
                
