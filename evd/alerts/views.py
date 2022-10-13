from .views import  *
import genutilities.views as genUtility
import genutilities.logUtility as logService
from .models import *
from django.db import transaction, connection
import genutilities.pushNotificationService as pushNotificationService
import json
import traceback


# Create your views here.
def updatePushTokeForGuardin(guardian,pushtoken,deviceObj):
    try:
        if pushtoken is None:
            return  None
        tokenObjList = PushToken.objects.filter(belongs_to_id=guardian.id,device_id = deviceObj.id)
        if tokenObjList and len(tokenObjList) > 0:
            tokenObj = tokenObjList[0]
            tokenObj.push_token = pushtoken
            tokenObj.status = True
            tokenObj.save()
            return tokenObj
        else:
            tokenObj = PushToken.objects.create(
                belongs_to_id=guardian.id,device_id = deviceObj.id,
                push_token = pushtoken
            )
            tokenObj.save()
            return tokenObj
    except Exception as e:
        print("updatePushTokeForGuardin",e)
        logService.logExceptionWithExceptionobject("updatePushTokeForGuardin",e)
        return None

def deactivatePushTokeForGuardin(guardian,deviceId):
    try:
        status = PushToken.objects.filter(belongs_to_id=guardian.id,device_id = deviceId).update(status=False)
        print("status updated",status)

    except Exception as e:
        print("deactivatePushTokeForGuardin",e)
        logService.logException("deactivatePushTokeForGuardin",e.message)
        return None


def getSubjectNamesForStudent(studentId,calDate):
    try:
        queryString = '''SELECT timetable.student_id,group_concat(course.subject) 
from student_time_table_session as tt_session 
LEFT JOIN student_time_table as timetable ON(timetable.id = tt_session.timetable_id)
LEFT JOIN web_offering as offer ON (offer.id = tt_session.offering_id)
LEFT JOIN web_course as course ON (course.id = offer.course_id)
where tt_session.calDate= "{}" AND  timetable.status = "active" AND timetable.student_id = {}
GROUP BY timetable.id,timetable.student_id;'''.format(calDate,studentId)

        #print("queryString",queryString)

        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()
        subjectNames = None
        for eachRecord in dataList:
            studentidval = eachRecord[0]
            if studentidval:
                subjectNameStr = eachRecord[1]
                if subjectNameStr:
                    subjectNames = subjectNameStr.split(",")
                    break
        return subjectNames
    except Exception as e:
        print("getSubjectNamesForStudent",e)
        logService.logException("getSubjectNamesForStudent", e.message)
        return None

def getStudentsForClassReminder():
    try:
        studentList = []
        curDate = genUtility.getCurrentDateTimeinIST()
        calDate = genUtility.getStringFromDate(curDate)
        curTimeMin = genUtility.getTimeInMinutesDateObj(curDate)
        curTimeAfter30 = curTimeMin + 30
        fieldArray = ["ttId","studentId","studentName","sessionCount","startTimeArray","endTimeArray"]
        queryString = '''SELECT timetable.id,timetable.student_id,student.name,count(tt_session.id) as totalSessionCount,group_concat(tt_session.time_start),group_concat(tt_session.time_end) 
from student_time_table_session as tt_session 
LEFT JOIN student_time_table as timetable ON(timetable.id = tt_session.timetable_id)
LEFT JOIN web_student as student ON(student.id = timetable.student_id)
where tt_session.calDate= "{}" AND  timetable.status = "active" AND tt_session.time_start <= {} AND student.status = "Active"
GROUP BY timetable.id,timetable.student_id;'''.format(calDate,curTimeAfter30)

        #print("queryString",queryString)

        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()
        topicIdArray = []
        for eachRecord in dataList:
            eachObject = {}
            for i in range(len(fieldArray)):
                fieldName = fieldArray[i]
                eachObject[fieldName] = eachRecord[i]

            sessionCount = eachObject["sessionCount"]
            sessionCount = int(sessionCount)

            if sessionCount == 1:
                startTime = int(eachObject["startTimeArray"])
                endTime =  int(eachObject["endTimeArray"])
                if curTimeMin < startTime:
                    studentIdNew = eachObject["studentId"]
                    subjectNames = getSubjectNamesForStudent(studentIdNew, calDate)
                    eachObject["subjectNames"] = subjectNames
                    print("startTime,current time", curTimeMin, startTime, eachObject["studentId"], eachObject["subjectNames"])
                    studentList.append(eachObject)

        return studentList

    except Exception as e:
        print("getStudentsForClassReminder",e)
        logService.logException("getStudentsForClassReminder", e.message)
        return None


def sendNotificationsToMulipleDevices(pushTokens, title, body, dataPayload):
    try:
        return pushNotificationService.sendNotificationToMultipleDevices(pushTokens, title, body, dataPayload)

    except Exception as e:
        print("sendNotificationsToMulipleDevices", e)
        logService.logException("sendNotificationsToMulipleDevices", e.message)
        return (False,None)

def insertGuardianPushNotificationToHistoryTable(pushTokens, title, body, dataPayload,studentId,guardianId,status,resultsData):
    try:
        jsonString =  None
        type = None
        if dataPayload:
            jsonString = json.dumps(dataPayload)
            type = dataPayload.get("type")

        resultsDataStr = None
        resultsArray = None
        if resultsData:
            resultsDataStr = json.dumps(resultsData)
            resultsArray = resultsData.get("results")
        statusStr = "1"
        if status is False:
            statusStr = "0"

        for i in range(len(pushTokens)):

            phObj = PushNotificationHistory.objects.create(
                student_id = studentId,
                guardian_id=guardianId,
                push_token=pushTokens[i],
                payload=jsonString,
                title = title,
                body = body,
                status=statusStr,
                created_by_id=8668,
                gcm_response=resultsDataStr,
                message_type=type
            )
            phObj.save()
            if resultsArray and len(resultsArray) > i:
                resState = resultsArray[i]
                if resState:
                    errorMsg = resState.get("error")
                    if errorMsg and errorMsg == "NotRegistered":
                        pushObj = pushTokens[i]
                        pushObj.status = False
                        pushObj.save()
                        print("pushObj not register",pushObj)

        return True

    except Exception as e:
        print("insertGuardianPushNotificationToHistoryTable", e)
        logService.logException("insertGuardianPushNotificationToHistoryTable", e.message)
        return False

def insertAuthUserPushNotificationToHistoryTable(pushTokens, title, body, dataPayload,authUser,status,resultsData):
    try:
        jsonString =  None
        type = None
        if dataPayload:
            jsonString = json.dumps(dataPayload)
            type = dataPayload.get("type")

        resultsDataStr = None
        resultsArray = None
        if resultsData:
            resultsDataStr = json.dumps(resultsData)
            resultsArray = resultsData.get("results")
        statusStr = "1"
        if status is False:
            statusStr = "0"

        for i in range(len(pushTokens)):

            phObj = PushNotificationHistory.objects.create(
                auth_user = authUser,
                push_token=pushTokens[i],
                payload=jsonString,
                title = title,
                body = body,
                status=statusStr,
                created_by_id=8668,
                gcm_response=resultsDataStr,
                message_type=type
            )
            phObj.save()
            if resultsArray and len(resultsArray) > i:
                resState = resultsArray[i]
                if resState:
                    errorMsg = resState.get("error")
                    if errorMsg and errorMsg == "NotRegistered":
                        pushObj = pushTokens[i]
                        pushObj.status = False
                        pushObj.save()
                        print("pushObj not register",pushObj)

        return True

    except Exception as e:
        print("insertAuthUserPushNotificationToHistoryTable", e)
        logService.logException("insertAuthUserPushNotificationToHistoryTable", e.message)
        return False

def updatePushTokeForAuthUser(authUser,pushtoken,deviceObj):
    try:
        if pushtoken is None:
            return  None
        tokenObjList = PushToken.objects.filter(belongs_to_id=authUser.id,device_id = deviceObj.id)
        if tokenObjList and len(tokenObjList) > 0:
            tokenObj = tokenObjList[0]
            tokenObj.push_token = pushtoken
            tokenObj.type = "authuser"
            tokenObj.status = True
            tokenObj.save()
            return tokenObj
        else:
            tokenObj = PushToken.objects.create(
                belongs_to_id=authUser.id,device_id = deviceObj.id,
                push_token = pushtoken,
                type='authuser'
            )
            tokenObj.save()
            return tokenObj
    except Exception as e:
        print("updatePushTokeForAuthUser",e)
        logService.logExceptionWithExceptionobject("updatePushTokeForAuthUser",e)
        return None


def getPushTokensForAuthUser(authUser):
    try:
        tokens = PushToken.objects.filter(status=True, belongs_to_id=authUser.id, type='authuser')
        tokenArray = []
        if tokens and len(tokens) > 0:
            for eachTokenObj in tokens:
                tokenArray.append(eachTokenObj.push_token)
            #print("getPushTokensForAuthUser count", len(tokens),authUser.id)
            return (tokens,tokenArray)
        return (None, None)
    except Exception as e:
        print("getPushTokensForAuthUser", e)
        logService.logException("getPushTokensForAuthUser", e.message)
        return (None,None)

def getPushTokensForGuardian(guardian):
    try:
        tokenArray = []
        tokens = PushToken.objects.filter(status=True, belongs_to_id=guardian.id, type='guardian')
        if tokens and len(tokens) > 0:
            for eachTokenObj in tokens:
                tokenArray.append(eachTokenObj.push_token)
            return (tokens, tokenArray)
        return (None, None)
    except Exception as e:
        print("getPushTokensForGuardian", e)
        logService.logException("getPushTokensForGuardian", e.message)
        return (None,None)

def getAuthUserFullName(authUser):
    userNameStr = ""
    if authUser and authUser.first_name:
        userNameStr = userNameStr + authUser.first_name

    if authUser and authUser.last_name:
        userNameStr = userNameStr + " "+ authUser.last_name

    return userNameStr
def sendSchoolApprovalNotification(authUser,partner,school):
    try:
        pTokenObjects,pTokens = getPushTokensForAuthUser(authUser)
        if pTokens and len(pTokens) > 0:
            pass
        else:
            return True

        userNameStr = getAuthUserFullName(authUser)


        dataPayload = {
            "type": "schoolApproved",
            "id": "124",
            "params": {
                "partnerId": partner.id,
                "schoolId": school.id,
                "userId": authUser.id,
                "schoolName": school.name,
                "userName":userNameStr
            }
        }
        title,body = None,None
        statusVal, resultsData = sendNotificationsToMulipleDevices(pTokens, title, body,dataPayload)
        insertAuthUserPushNotificationToHistoryTable(pTokenObjects, title, body, dataPayload, authUser,statusVal,resultsData)
        return True
    except Exception as e:
        print("sendSchoolApprovalNotification", e)
        #traceback.print_exc()
        logService.logException("sendSchoolApprovalNotification", e.message)
        return False


def sendPartnerApprovalNotification(partner,authUser):
    try:
        pTokenObjs,pTokens = getPushTokensForAuthUser(authUser)
        if pTokens and len(pTokens) > 0:
            pass
        else:
            return True

        userNameStr = getAuthUserFullName(authUser)
        dataPayload = {
            "type": "partnerApproved",
            "id": "125",
            "params": {
                "partnerId": partner.id,
                "userId": authUser.id,
                "orgName":partner.name_of_organization,
                "partnerName":partner.name,
                "userName":userNameStr
            }
        }
        title,body = None,None
        statusVal, resultsData = sendNotificationsToMulipleDevices(pTokens, title, body,dataPayload)
        insertAuthUserPushNotificationToHistoryTable(pTokenObjs, title, body, dataPayload, authUser,statusVal,resultsData)
        return True
    except Exception as e:
        print("sendPartnerApprovalNotification", e)
        logService.logException("sendPartnerApprovalNotification", e.message)
        return False


def sendDoubtRespondedNotificationToStudent(guardian,student,subjectName,doubtObj):
    try:

        pTokenObjects, pTokens = getPushTokensForGuardian(guardian)
        if pTokens and len(pTokens) > 0:
            pass
        else:
            return True

        stName = ""
        if doubtObj and doubtObj.subtopic:
            stName = doubtObj.subtopic.name

        dataPayload = {
            "type": "studentDoubtResponded",
            "id": "126",
            "params": {
                "subjectName": subjectName,
                "name": student.name,
                "studentId": student.id,
                "guardianId": guardian.id,
                "doubtId":doubtObj.id,
                "subTopicName":stName
            }

        }
        title = None
        body = None

        statusVal, resultsData = sendNotificationsToMulipleDevices(pTokens, title, body,dataPayload)
        #print("Doubt push notification",statusVal,resultsData)
        insertGuardianPushNotificationToHistoryTable(pTokenObjects, title, body, dataPayload,student.id, guardian.id, statusVal,resultsData)
        return True

    except Exception as e:
        print("sendDoubtRespondedNotificationToStudent", e)
        #traceback.print_exc()
        logService.logException("sendDoubtRespondedNotificationToStudent", e.message)