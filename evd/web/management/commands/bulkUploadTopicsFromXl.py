from django.core.management.base import BaseCommand
from web.models import Topic, Course
import xlrd


class Command(BaseCommand):
    def handle(self, *args, **options):
        failed_topics = open('errorfiles/failed_bilk_upload_files.txt','w')
        path = args[0]
        wb = xlrd.open_workbook(path)
        sheet = wb.sheet_by_index(0)
        for i in range(sheet.nrows):
            row = sheet.row_values(i)
            topic_title = row[1]
            course_id = row[2]
            topic_wiki_url = row[3]
            number_of_sessions = row[4]
            topic_status = row[5]
            priority = row[6]
            try:
                course = Course.objects.get(id=int(course_id))
                topic = Topic.objects.create(title=topic_title,course_id=course,url=topic_wiki_url,num_sessions=number_of_sessions,status=topic_status,priority=priority)
                topic.save()
                print "topic %s with course ID %s is successfully added" %(topic_title,course_id)
            except:
                failed_topics.write('failed to get the course from the table for course_id %s, topic %s' %(course_id,topic_title))