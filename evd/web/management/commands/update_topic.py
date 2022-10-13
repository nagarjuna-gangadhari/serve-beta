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
        with open('topic_update_log.log', 'w+') as lg:

            success_count = 0
            workbook = xlrd.open_workbook('topic_update.xlsx')

            conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                                user=settings.DATABASES['default']['USER'],
                                passwd=settings.DATABASES['default']['PASSWORD'],
                                db=settings.DATABASES['default']['NAME'],
                                charset="utf8",
                                use_unicode=True)

            cursor = conn.cursor()

            mainData_sheet = workbook.sheet_by_index(0)
            for i in range(0, mainData_sheet.nrows):
                #[u'board_name', u'subject', u'grade', u'id', u'course_id_id', u'title', u'From Wikividya', u'url', u'num_sessions']
                #['topic_id', 'old', 'new']
                topic_id    = int(mainData_sheet.row_values(i)[0])
                old_title   = mainData_sheet.row_values(i)[1]
                new_title   = mainData_sheet.row_values(i)[2][:50]

                topic_query = "select * from web_topic where id='%s'" % (topic_id)
                up_query    = "update web_topic set title='%s' where id='%s'"
                up_values   = (new_title, topic_id)

                cursor.execute(up_query % up_values)
                conn.commit()

                success_count += 1
                lg.write(str(topic_id) + ":::" + old_title + ":::::" + new_title + "\n")
                print str(topic_id) + ":::" + old_title + ":::::" + new_title + "\n" 

            cursor.close()
            lg.write("updated: " + str(success_count) + '\n')
            print "updated: " + str(success_count) + "\n"
