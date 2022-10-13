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
        with open('url_update_log.log', 'a') as lg:

            success_count = 0
            workbook = xlrd.open_workbook('topic_url_update.xlsx')

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
                #['topic_id', 'url', 'num_of_sess', 'priority']
                topic_id    = int(mainData_sheet.row_values(i)[0])
                url         = mainData_sheet.row_values(i)[1]
                num_of_sess = int(mainData_sheet.row_values(i)[2])
                priority    = int(mainData_sheet.row_values(i)[3])

                topic_query = "select * from web_topic where id='%s'" % (topic_id)
                up_query    = "update web_topic set url=\"%s\", num_sessions=\"%s\", priority=\"%s\" where id=\"%s\""
                up_values   = (url, num_of_sess, priority, topic_id)

                cursor.execute(up_query % up_values)
                conn.commit()

                success_count += 1
                lg.write(str(topic_id) + ":::" + url + ":::::" + str(num_of_sess) + str(priority) + "\n")
                print str(topic_id) + ":::" + url + ":::::" + str(num_of_sess) + str(priority) + "\n" 

            cursor.close()
            lg.write("updated: " + str(success_count) + '\n')
            lg.write("********************************************************************************************************************************")
            print "updated: " + str(success_count) + "\n"
