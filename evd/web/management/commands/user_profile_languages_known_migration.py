from django.core.management.base import BaseCommand
from web.models import UserProfile

class Command(BaseCommand):
    def handle(self, *args, **options):
        userprofiles = UserProfile.objects.all()
        for user_prof in userprofiles.iterator():
            if user_prof.pref_medium:
                if user_prof.pref_medium == 'None':
                    pass
                else:
                    lang_known = [{u'lang': user_prof.pref_medium, u'write': 1, u'read': 1, u'speak': 1}]
                    user_prof.languages_known = lang_known
                    user_prof.save()
            else:
                pass