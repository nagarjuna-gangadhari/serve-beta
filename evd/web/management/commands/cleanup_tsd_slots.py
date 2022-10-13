from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('cleanup_slots.log', 'w+') as err:
            yestrdy = datetime.datetime.utcnow() + datetime.timedelta(days=-1, hours=5, minutes=30)
            delete_slots = SelectionDiscussionSlot.objects.filter(status="Not Booked", userp=None, start_time__lt = yestrdy)
            for slot_obj in delete_slots:
                history_obj = SelectionDiscussionSlotHistory.objects.filter(slot=slot_obj)
                if not history_obj:
                    err.write(str(slot_obj.id) + "--" + str(slot_obj.status) + "--" + str(slot_obj.outcome) + "\n")
                    slot_obj.delete()

        return "success"
