import optparse
import sys, os
import MySQLdb
import simplejson
import csv

project_dir = os.path.abspath(os.path.join(__file__, "../../../"))
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings
from web.models import *
from student.models import *
from alerts.models import *
import genutilities.views as genUtility
import genutilities.logUtility as logService
import alerts.views as notificationService
import traceback


class StudentClassReminderNotification():
    def __init__(self):
        self.conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], \
                                    user=settings.DATABASES['default']['USER'], \
                                    passwd=settings.DATABASES['default']['PASSWORD'], \
                                    db=settings.DATABASES['default']['NAME'], \
                                    charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()


    def getPushTokensForStudent(self,studentId):
        try:
            if studentId:
                relList = Student_Guardian_Relation.objects.filter(status=True,
                                                                   student__id=studentId).select_related('guardian')
                if relList and len(relList) > 0:
                    guardianRel = relList[0]
                    guardianObj = guardianRel.guardian
                    print("getPushTokensForStudent detail",studentId,guardianObj.id)
                    tokens = PushToken.objects.filter(status=True,belongs_to_id=guardianObj.id,type='guardian')
                    if tokens and len(tokens) > 0:
                        print("getPushTokensForStudent count", tokens)
                        return tokens,guardianObj

            return None, None
        except Exception as e:
            print("getPushTokensForStudent", e)
            logService.logException("sendPushNotificationToStudent", e.message)
            return None, None

    def sendPushNotificationToStudent(self,studentDict,guardianObj,pushTokensInstances):
        try:
            tokenArray = []
            for eachTokenObj in pushTokensInstances:
                tokenArray.append(eachTokenObj.push_token)

            timeTableId = studentDict["ttId"]
            subjects = studentDict["subjectNames"]
            studentId = studentDict["studentId"]
            sName = studentDict["studentName"]
            dataPayload = {
                "type":"classReminder",
                "id":"123",
                "params":{
                    "timetableId": timeTableId,
                    "subjectNames": subjects,
                    "name": sName,
                    "studentId": studentId,
                    "guardianId": guardianObj.id
                }

            }
            title = None
            body =None

            statusVal,resultsData =  notificationService.sendNotificationsToMulipleDevices(tokenArray, title, body, dataPayload)
            print("student id resultsData",studentId,resultsData)
            notificationService.insertGuardianPushNotificationToHistoryTable(pushTokensInstances, title, body, dataPayload,studentId,guardianObj.id,statusVal,resultsData)
            return True

        except Exception as e:
            print("sendPushNotificationToStudent", e)
            logService.logException("sendPushNotificationToStudent", e.message)
            return False

    def sendNotificationToStudents(self,students):
        try:
            for eachStudentDict in students:
                #Get active Push tokens
                #Send push notification
                #Insert History Records with status
                studentId = eachStudentDict.get('studentId')
                pushTokens,guardianObj = self.getPushTokensForStudent(studentId)
                if pushTokens:
                    self.sendPushNotificationToStudent(eachStudentDict,guardianObj,pushTokens)
        except Exception as e:
            print("sendNotificationToStudents", e)
            logService.logException("sendNotificationToStudents function", e.message)
            traceback.print_exc()


    def runOperation(self):
        try:

            #get students for sending notification
            students = notificationService.getStudentsForClassReminder()

            if students:
                totalCount = len(students)
                # Send notification
                self.sendNotificationToStudents(students)
                logService.logInfo("Class Reminder Notification sent for", str(totalCount))
                print("Class Reminder Notification sent for", totalCount)
            else:
                logService.logInfo("Class Reminder","No students classes scheduled.")
                print("Class Reminder","No students classes scheduled.")

        except Exception as e:
            print("runOperation", e)
            logService.logException("runOperation", e.message)
            traceback.print_exc()

    def main(self, options):
        self.runOperation()
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    # parser.add_option('-t', '--type', default="", help='StudentClassReminderNotification')
    # parser.add_option('-i', '--id', default=None, help='Id of an student')
    parser.add_option('-s', '--source', default='dev', help='Source dev/prod')
    (options, args) = parser.parse_args()

    OBJ = StudentClassReminderNotification()
    OBJ.main(options)