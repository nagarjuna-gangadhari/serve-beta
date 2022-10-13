from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('ay_to_offer_script.log', 'a+') as lg:

            offer_objs = Offering.objects.all()
            count = 0
            for offer_obj in offer_objs:
                start_year = offer_obj.start_date.year
                board = offer_obj.course.board_name
                try:
                    ayfy_obj = Ayfy.objects.get(start_date__year = start_year, board = board, types = 'Academic Year')
                    count += 1
                    offer_obj.academic_year = ayfy_obj
                    offer_obj.save()
                    lg.write(offer_obj.course.board_name + "__" + str(offer_obj.start_date.year) + " ::::: " + ayfy_obj.title + "__" + ayfy_obj.board + "\n\n")
                    print offer_obj.course , offer_obj.start_date.year ,
                    print ayfy_obj

                except:
                    continue
            lg.write("\n\ntotal ::: " + str(count))
            print "total :::: " + str(count)

        return "success"
