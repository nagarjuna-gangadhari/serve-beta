from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage

class Command(BaseCommand):
   def handle(self, *args, **options):
     
        now_date = datetime.datetime.now() 
        booked_slots = Demandslot.objects.filter(status='Booked')
        c=1 

        for slot in booked_slots:
            slot_date = slot.date_booked
            diff = now_date - slot_date
            days = diff.days
            days_to_hours = days * 24
            total_hours = days_to_hours

            user_id = slot.user_id
            user = UserProfile.objects.filter(pk=user_id)

            try:
                users_slots
            except NameError:
                users_slots = {}

            if user:
                user = user[0]
                status = user.profile_completion_status

                try:
                    users_slots[user.user.id]
                except KeyError:
                    users_slots[user.user.id] = {}
                    users_slots[user.user.id]['slots'] = []

                if status == False:
                    print slot
                else:
                    teacher_role_obj = RolePreference.objects.filter(userprofile=user,role__name='Teacher')
                    if teacher_role_obj:
                        role_outcome = teacher_role_obj[0].role_outcome
                        users_slots[user.user.id]["name"] = user.user.first_name + " " + user.user.last_name
                        users_slots[user.user.id]["center"] = slot.center.name
                        users_slots[user.user.id]["email"] = user.user.email

                        if  role_outcome == 'Inprocess':

                             if total_hours > 72:
                                slot.date_booked = None
                                slot.status      = 'Unallocated'
                                slot.user_id     = None
                                slot.save()

                                users_slots[user.user.id]["slots"].append(slot.day + " " + slot.start_time.strftime('%I:%M %p') + " to " + slot.end_time.strftime('%I:%M %p'))

                                #content = "<p>Hi " + {{user.user.first_name}} + " " + {{user.user.last_name}} +" ,</p>" + \
                                          #"Since you have not completed the teacher onboarding process we are releasing the booking you have done for" + \
                                          #{{slot.center.name}} + " , for "
                                

                        elif role_outcome == 'Recommended':

                            if total_hours > 240:
                                slot.date_booked = None
                                slot.status      = 'Unallocated'
                                slot.user_id     = None
                                slot.save()

                                users_slots[user.user.id]["slots"].append(slot.day + " " + slot.start_time.strftime('%I:%M %p') + " to " + slot.end_time.strftime('%I:%M %p'))
                        else:
                            
                            if total_hours > 2:
                                slot.date_booked = None
                                slot.status      = 'Unallocated'
                                slot.user_id     = None 
                                slot.save()

                                users_slots[user.user.id]["slots"].append(slot.day + " " + slot.start_time.strftime('%I:%M %p') + " to " + slot.end_time.strftime('%I:%M %p'))

                    else:
                        print "no"
        for key, value in users_slots.items():
            if value['slots']:
                content = "<p>Hi " + value['name'] + ",</p>" + \
                          "<p>Since you have not completed the teacher onboarding process we are releasing the booking you have done for " + \
                          value['center'] + " , for " + value['slots'][0] + " and " + value['slots'][1] + ".</p>" + \
                          "<p>KIndly complete the onboarindg process. Please Click here : http://www.evidyaloka.org/onboarding/ to check your" + \
                          " Onboarding Status or reach out to the volunteer management team at volunteer@evidyaloka.org </p>"
                msg = EmailMessage("Releasing the booking you have done" , content, 'evlsystem@evidyaloka.org', ['akhilraj@headrun.com', value['email']])
                msg.content_subtype = "html"
                msg.send()
        return "success"
