from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('planned_topic_to_offer_script.log', 'a+') as lg:
            offer_objs = Offering.objects.filter(academic_year__start_date__gte=datetime.datetime(2017, 4, 1, 0, 0, 0, 0))
            count = 0
            for offer_obj in offer_objs:
                try:
                    if offer_obj.academic_year.board == 'TNSB':
                        print offer_obj.academic_year
                        print offer_obj.course
                        print offer_obj.center
                        print offer_obj.planned_topics.count()
                        if offer_obj.planned_topics.count() == 0:
                            topic_objs = Topic.objects.filter(course_id = offer_obj.course_id)
                            for topic in topic_objs:
                                offer_obj.planned_topics.add(topic)

                            offer_obj.save()
                            #print offer_obj.planned_topics.all()
                        print "++++++++++++++++++++++++++++++++++++++++++++++++"
                        count += 1
                        lg.write(offer_obj.planned_topics.all() + "\n\n")

                except:
                    continue
                lg.write("\n\ntotal ::: " + str(count))
            print "total :::: " + str(count)

            return "success"
