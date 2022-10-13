from django.core.management.base import BaseCommand, CommandError
from web.models import *
from mailer import send_mail
from evd import settings
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        now = datetime.datetime.now()
        today = datetime.date.today()
        tomorrow = today+ datetime.timedelta(days = 1)

        session = Session.objects.exclude(teacher = None)
        for i in range(len(session)):
            if session[i].date_start.date() == tomorrow:
                user = User.objects.filter(username = session[i].teacher)[0]
                receipents = [user.email]
                subject = session[i].offering
                body = session[i].offering
                send_mail(subject,body,settings.DEFAULT_FROM_EMAIL,receipents)
        self.stdout.write('Mail Sent')
