from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist
import MySQLdb
import xlrd
import MySQLdb
import xlrd

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('add_topic_details.log', 'w+') as lg:

            success_count = 0

            conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                                user=settings.DATABASES['default']['USER'],
                                passwd=settings.DATABASES['default']['PASSWORD'],
                                db=settings.DATABASES['default']['NAME'],
                                charset="utf8",
                                use_unicode=True)

            cursor = conn.cursor()

            topic_query = "select id, url from web_topic where id > 269 and url!=''"

            cursor.execute(topic_query)
            topics = cursor.fetchall()
            attribute_ids = ["TextBook", "Lesson Plan", "Transliteration", "Videos", "Pictures", "Activities", "Worksheets", "Assessments", "PowerPoint"]
            for topic in topics:
                for ind, att_id in enumerate(attribute_ids, 1):
                    url = '"' + topic[1] + "#tab=" + att_id + '"'
                    try:
                        details_query = "insert into web_topicdetails(topic_id, attribute_id, url, status, author_id, last_updated_date, updated_by_id)\
                                     values(%s, %s, %s, %s, %s, NOW(), %s)"
                        values        = (topic[0], ind, url, "'Not Started'", 1, 1)
                        details_query = details_query % values
                        cursor.execute(details_query)
                        #conn.commit()

                        success_count += 1
                        lg.write(str(topic[0]) + ":::" + url + ":::::" + str(ind) + "\n")
                        print str(topic[0]) + ":::" + url + ":::::" + str(ind) + "\n"

                    except:
                        traceback.print_exc()
                        print details_query
                        continue
            cursor.close()
            lg.write("total created: " + str(success_count) + '\n')
            print "total created: " + str(success_count) + "\n"
