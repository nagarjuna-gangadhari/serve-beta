# Create your views here.
import os
import json
import ast
import simplejson
import requests
import logging
import traceback
import math
import random
from datetime import datetime as datetimeObj, date as dateObj

import settings
from django.db import transaction, connection
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from web.models import *
from .models import *
from genutilities.models import *
import genutilities.views as genUtility
import genutilities.logUtility as logService
import genutilities.uploadDocumentService as docUploadService
import alerts.views as notificationModule
import genutilities.pushNotificationService as pushNotificationService
from django.template.loader import get_template
from django.template import Context, loader
from django.core.mail import EmailMessage
from django.views.generic import View
from django.utils.decorators import method_decorator
from genutilities.views import get_object_or_none
import genutilities.cacheUtility as cacheService

## REUSABLE FUNCTIONS BELOW

def getUserDocument(docId):
    userDoc = None
    try:
        userDoc = UserDocument.objects.get(id=docId)
    except Exception as e:
        logService.logException("getUserDocument", e.message)
    return userDoc

def getCenterObjects(schoolObj):
    center = None
    try:
        centers = Center.objects.filter(digital_school=schoolObj)
        if centers and len(centers) > 0:
            center = centers[0]
    except Exception as e:
        logService.logException("getCenterObjects", e.message)
    return center

def getCenterObjectsForId(schoolId):
    center = None
    try:
        centerList = Center.objects.filter(digital_school_id=schoolId)
        if centerList and len(centerList) > 0:
            center = centerList[0]
    except Exception as e:
        logService.logException("getCenterObjects", e.message)
    return center

def getCourseProviderObject(courseProviderId):
    dataObject = None
    try:
        dataList = CourseProvider.objects.filter(id=courseProviderId)
        if dataList and len(dataList) > 0:
            dataObject = dataList[0]
    except Exception as e:
        logService.logException("getCourseProviderObject", e.message)
    return dataObject

def isUserDSMOfSchool(schoolId,userObj):
    staff = None
    try:

        role =  Role.objects.get(name="Digital School Manager")
        staffList = DigitalCenterStaff.objects.filter(digital_school_id=schoolId,user=userObj,role=role)
        if staffList and len(staffList) > 0:
            staff = staffList[0]
    except Exception as e:
        logService.logException("isUserDSMOfSchool", e.message)
    return staff

kstudentRelationShipTypes = ["mother","father","guardian"]
kstudentGenderTypes = ["Boy","Girl"]

def getValueElseThrowException(requestBodyParams,keyName):
    return genUtility.getValueElseThrowException(requestBodyParams,keyName)

def sendErrorResponse(request,errorConstant):
    return  genUtility.getStandardErrorResponse(request, errorConstant)

def isRelationShipTypeValid(reationShipType):

    if reationShipType in kstudentRelationShipTypes:
        return True
    return False

def isGenderValid(genderType):
    if genderType in kstudentGenderTypes:
        return True
    return False

def getOfferings(offeringIds,centerRec):
    offeringlist = None
    try:
        offeringlist = Offering.objects.filter(id__in=offeringIds,center=centerRec)
    except Exception as e:
        logService.logException("getOfferings", e.message)
    return offeringlist

def getOfferingsWithCoursePrefetch(offeringIds,centerRec):
    offeringlist = None
    try:
        offeringlist = Offering.objects.filter(id__in=offeringIds,center=centerRec).select_related("student")
    except Exception as e:
        logService.logException("getOfferings", e.message)
    return offeringlist

def getOfferingsForSchoolCenterForStudent(centerRec,studentId):
    dataArrayList = []
    try:
        currentDateString = genUtility.getCurrentDateTimeInStr()
        queryString = '''SELECT DISTINCT offering_id from web_offering_enrolled_students 
        INNER JOIN web_offering ON (web_offering.id=web_offering_enrolled_students.offering_id) 
        WHERE student_id='''+studentId+ ''' AND web_offering.center_id='''+str(centerRec.id) + " AND web_offering.status IN ('running','pending') AND web_offering.end_date >= '"+ currentDateString+ "' "

        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()
        for eachRecord in dataList:
            offeringId = eachRecord[0]
            if offeringId:
                dataArrayList.append(offeringId)

    except Exception as e:
        logService.logException("getOfferings for school and student", e.message)
    return dataArrayList

def getTimetableObject(studentObj):
    try:
        timetableObj = Time_Table.objects.get(student=studentObj)
        return timetableObj
    except:
        return None

def getTimetableForStudentId(studentId):
    try:
        timetableObj = Time_Table.objects.get(student_id=studentId)
        return timetableObj
    except:
        return None

def getOfferingsOptedByStudentInCurrentAcademicYear(studentId,currentDateString,centerId,offeringId):
    resDict = None
    try:
        offeringIdStr = ""
        if offeringId:
            offeringIdStr = "AND wo.id = "+ str(offeringId)

        queryString = '''SELECT  offering_id,wc.subject,wc.id,wc.language_id,gl.name,gl.code from web_offering_enrolled_students as woe
            LEFT JOIN web_offering as wo ON (wo.id=woe.offering_id) 
            LEFT JOIN web_course as wc ON (wc.id=wo.course_id) 
            LEFT JOIN genutilities_language as gl ON (gl.id=wc.language_id AND wc.language_id IS NOT NULL)
            WHERE woe.student_id=''' + str(studentId) + ''' AND wo.center_id=''' + str(centerId) + " AND wo.end_date >= '" + currentDateString + "' " + offeringIdStr
        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()
        resDict = {}
        for eachRecord in dataList:
            offeringId = eachRecord[0]
            subjectName = eachRecord[1]
            courseId = eachRecord[2]
            if offeringId  and subjectName:
                finalDict = {"name":subjectName,"courseId":courseId}

                languageId = eachRecord[3]
                languageName = eachRecord[4]
                languageCode = eachRecord[5]
                if languageName and languageCode and languageId:
                    finalDict["language"] = {"id":languageId,"name":languageName,"code":languageCode}

                resDict[offeringId] = finalDict

    except Exception as e:
        logService.logException("getOfferings  student", e.message)
    return resDict

def differenceInList(list1,list2):
    list1Len = len(list1)
    list2Len =  len(list2)
    differenceIds = []
    for j in range(list1Len):
        eachId = list1[j]
        if eachId in list2:
            continue
        else:
            differenceIds.append(eachId)
    return differenceIds

def getIdsListFromObjectList(objectList):
    listLen = len(objectList)
    idsList = []
    for j in range(listLen):
        someObj = objectList[j]
        if someObj.id:
            idsList.append(someObj.id)
    return idsList

def getGuardianForMobileNumber(mobile):
    mobile = str(mobile)
    guardian = None
    try:
        mobileList = Guardian.objects.filter(mobile=mobile)
        if mobileList and len(mobileList) > 0:
            guardian = mobileList[0]
    except Exception as e:
        logService.logException("getGuardianForMobileNumber", e.message)
    return guardian

def getGuardianForStudent(student):
    guardianRel = None
    try:
        dataList = Student_Guardian_Relation.objects.filter(student=student).prefetch_related("guardian")
        if dataList and len(dataList) > 0:
            guardianRel = dataList[0]
    except Exception as e:
        logService.logException("getGuardianForStudent", e.message)
    return guardianRel

def createGuardianObjecWithoutStudent(mobile,fullname,createdByUser,source):
    createdById = settings.SYSTEM_USER_ID_AUTH
    if createdByUser:
        createdById = createdByUser.id

    guardian = Guardian.objects.create(
        full_name=fullname,
        mobile=str(mobile),
        status="active",
        created_by_id=createdById,
        updated_by_id=createdById,
        source=source
    )
    guardian.save()
    return guardian

def createGuardianObjectIfNeeded(userObj,student,mobile,relationshipType,isPrimary,parentName,source):
    guardian = getGuardianForMobileNumber(mobile)
    if guardian is None:
        guardian = createGuardianObjecWithoutStudent(mobile, parentName, userObj,source)

    studentGuardianMap = Student_Guardian_Relation.objects.create(
        student=student,
        guardian=guardian,
        relationship_type=relationshipType,
        status=True,
        hasProvidedConsent=True,
        created_by=userObj,
        updated_by=userObj
    )
    studentGuardianMap.save()
    return studentGuardianMap

def getStudentStudyPreference(studentId):
    studyTimeObjs = Study_Time_Preference.objects.filter(student__id=studentId, status="active").order_by(
        'day_of_the_week')
    firstDay = None
    days = set()
    slotslist = []
    for i in studyTimeObjs:
        slotdata = {}
        days.add(i.day_of_the_week)
        if not firstDay:
            firstDay = i.day_of_the_week
        if firstDay != i.day_of_the_week:
            continue
        slotdata["startTime"] = i.time_start
        slotdata["endTime"] = i.time_end
        slotdata["startTimeMin"] = i.start_time_min
        slotdata["endTimeMin"] = i.end_time_min
        slotslist.append(slotdata)
    days = list(days)
    return (days,slotslist)


def filterStudentByParameters(digitalSchoolId,page,count,boardName,offeringId,grade,academicYearId,isCountNeeded):
    queryOffset = 0
    limitRecord = 50
    if page and count and genUtility.checkIfParamIfInteger(page) and genUtility.checkIfParamIfInteger(count):
        limitRecord = int(count)
        queryOffset = int(page) * limitRecord

    digitalSchoolIdStr = "sc.id = "+str(digitalSchoolId) + " "

    if  offeringId and genUtility.checkIfParamIfInteger(offeringId):
        tempIdl = long(offeringId)

        tempIdlStr = "AND offering.id = " + str(tempIdl) + " "
        digitalSchoolIdStr += tempIdlStr


    if academicYearId and genUtility.checkIfParamIfInteger(academicYearId):
        tempIdl = long(academicYearId)
        tempIdlStr = "AND offering.academic_year_id = " + str(tempIdl) + " "
        digitalSchoolIdStr += tempIdlStr

    if grade and genUtility.checkIfParamIfInteger(grade):
        tempIdl = int(grade)
        tempIdlStr = "AND course.grade = " + str(tempIdl) + " "
        digitalSchoolIdStr += tempIdlStr

    if boardName:
        tempIdlStr = "AND course.board_name LIKE '%%" + boardName + "%%' "
        digitalSchoolIdStr += tempIdlStr

    limitString = " LIMIT " + str(limitRecord) + " OFFSET " + str(queryOffset)+";"

    fieldArray = ["id", "name", "profileUrl","grade"]
    selectClauseStr = " DISTINCT st.id,st.name,st.profile_pic_url,st.grade,se.created_on "
    if isCountNeeded:
        selectClauseStr = " COUNT(DISTINCT st.id) "
        fieldArray = ["count"]
        limitString = ""



    queryString = '''select '''+selectClauseStr +'''
                    FROM web_digitalschool as sc
                    LEFT JOIN student_student_school_enrollment as se on (se.digital_school_id = sc.id)
                    LEFT JOIN web_student as st on (st.id = se.student_id)
                    LEFT JOIN web_offering_enrolled_students as es on (es.student_id = se.student_id)
                    LEFT JOIN web_offering as offering on (offering.id = es.offering_id AND offering.status != 'completed')
                    LEFT JOIN web_course as course on (course.id = offering.course_id) 
                    WHERE  ''' + digitalSchoolIdStr + '''  ORDER BY se.created_on DESC ''' + limitString


    cursor = connection.cursor()
    cursor.execute(queryString)
    dataList = cursor.fetchall()
    dataDictList = []
    fieldCount = len(fieldArray)
    for eachRecord in dataList:
        eachObject = {}
        for i in range(fieldCount):
            fieldName = fieldArray[i]
            eachObject[fieldName] = eachRecord[i]
        dataDictList.append(eachObject)
    return dataDictList

def getOfferingsOfStudentForSchool(student,center,schoolId,offeringId):
    studentIdStr = " es.student_id = " + str(student.id) + " "

    if offeringId and genUtility.checkIfParamIfInteger(offeringId):
        tempIdl = long(offeringId)
        tempIdlStr = "AND offering.id = " + str(tempIdl) + " "
        studentIdStr += tempIdlStr

    if center:
        tempIdl = center.id
        tempIdlStr = "AND offering.center_id = " + str(tempIdl) + " "
        studentIdStr += tempIdlStr

    queryString = '''select DISTINCT offering.id,course.grade,course.subject
                    FROM web_offering_enrolled_students as es
                    LEFT JOIN web_offering as offering on (offering.id = es.offering_id AND offering.status != 'completed')
                    LEFT JOIN web_course as course on (course.id = offering.course_id) 
                    WHERE  ''' + studentIdStr + ''' ; '''

    fieldArray = ["id", "grade", "subject"]
    cursor = connection.cursor()
    cursor.execute(queryString)
    dataList = cursor.fetchall()
    dataDictList = []
    fieldCount = len(fieldArray)
    for eachRecord in dataList:
        eachObject = {}
        for i in range(fieldCount):
            fieldName = fieldArray[i]
            eachObject[fieldName] = eachRecord[i]
        dataDictList.append(eachObject)
    return dataDictList


def getCenterId(digital_school):
    centerId = []
    centerObj = Center.objects.filter(digital_school__id=digital_school, status="Active").values('id')
    for singleCenter in centerObj:
        centerId.append(singleCenter['id'])

    return centerId


def getOfferingsByCenterIdList(centerId,curDateTime):
    offeringId = []
    offeringObjs = Offering.objects.filter(center__in=centerId,end_date__gte=curDateTime,status__in=['pending','running'])
    for i in offeringObjs:
        offeringId.append(i.id)

    return offeringId

def getOfferingByEnrolledObj(enrolledStudentsObj):
    offeringObj = []
    for i in enrolledStudentsObj:
        offeringObjs = Offering.objects.get(id=i.offering.id)
        offeringObj.append(offeringObjs)

    return offeringObj

def getNumberOfSessionRequiredForCourseIds(courseIds):
    try:
        courseIdStr = genUtility.getStringFromIdArray(courseIds)
        whereClause = "course.id IN (" + courseIdStr + ") and course.status = 'active' and tp.status != 'Inactive'  and tp.num_sessions > 0 "

        queryString = '''select course.id, SUM(tp.num_sessions) from web_course as course 
        LEFT JOIN web_topic as tp on (tp.course_id_id = course.id) 
        WHERE  ''' + whereClause + ''' GROUP BY course.id; '''
        cursor = connection.cursor()
        cursor.execute(queryString)

        dataList = cursor.fetchall()
        dataDictList = {}
        for eachRecord in dataList:
            courseId = eachRecord[0]
            numberOfSessions = eachRecord[1]
            if courseId and numberOfSessions and numberOfSessions > 0:
                dataDictList[str(courseId)] = str(numberOfSessions)

        return dataDictList
    except Exception as e:
        print("getNumberOfSessionRequiredForCourseIds", e)
        logService.logException("getNumberOfSessionRequiredForCourseIds", e.message)

def getSlotDetailsForStudent(student,timetableObj,startDateString,endDateString):
    try:
        whereClause = "stt.timetable_id = " + str(
            timetableObj.id) + " and stt.status = 1 and stt.calDate >= '" + startDateString + "' AND stt.calDate <= '" + endDateString + "'"
        selectQuery = '''SELECT stt.calDate,MAX(stt.time_end) 
                     FROM student_time_table_session as stt 
                     where ''' + whereClause + " GROUP by stt.calDate ORDER BY stt.calDate"

        cursor = connection.cursor()
        cursor.execute(selectQuery)
        dataList = cursor.fetchall()
        dataDictList = {}
        calDays = []
        for eachRecord in dataList:
            calDate = eachRecord[0]
            endTimeMin = eachRecord[1]
            if calDate and endTimeMin:
                calDateStr = genUtility.getStringFromDate(calDate)
                calDays.append(calDateStr)
                sessionObj = dataDictList.get(calDateStr)
                if sessionObj is None:
                    sessionObj = {}
                    dataDictList[calDateStr] = sessionObj
                sessionObj["maxEndTimeMin"] = endTimeMin

        return (dataDictList,calDays)
    except Exception as e:
        print("getSlotDetailsForStudent", e)
        logService.logException("getSlotDetailsForStudent", e.message)
        return ({},[])

def calculateTimeRemainingPerDay(slots,endTime):
    foundSlot = False
    timeRemaining = 0
    for j in range(len(slots)):
        aSlot = slots[j]
        sTime = aSlot["startTimeMin"]
        eTime = aSlot["endTimeMin"]
        if endTime >= sTime and endTime <= eTime:
            foundSlot = True
            timeRemaining =  eTime - endTime
        elif foundSlot == True:
            timeRemaining = timeRemaining + (eTime - sTime)
    return timeRemaining

def getSessionDurationForGrade(grade):
    sessionDurationJson = genUtility.getDictObjectFromSystemSettingJSONForKey("SessonDurationGradewise")
    sessionDurationGrade = sessionDurationByGrade(str(grade), sessionDurationJson)
    return int(sessionDurationGrade)

def getUsefulFutureDaysForStudy(endDate,startDate,days,slots,sessionDurationGrade,breakTime,numOfSubjects,maxSubLimit):
    finalDate = startDate
    dayOfTheWeek = finalDate.weekday() + 1
    remWeekDays = 7 - dayOfTheWeek
    deltaObj = endDate - finalDate
    numberOfDays = deltaObj.days
    numberOfDays = numberOfDays - remWeekDays
    numberOfWeeks = int(math.floor(numberOfDays / 7))
    totalNumStudyDays = numberOfWeeks * len(days)

    perDayDurationMin = getTotalStudyMinsPerDay(slots)
    totalDaySessionCount = getNumberOfUsefulSessions(numOfSubjects, perDayDurationMin, sessionDurationGrade, breakTime,maxSubLimit)

    if totalDaySessionCount >= numOfSubjects:
        #return totalNumStudyDays
        pass
    return (totalNumStudyDays,totalDaySessionCount)

def getNumberOfUsefulSessions(numberOfSubjects,perDayDurationMin,sessionDurationGrade,breakTime,maxSubLimit):
    totalDaySessionCount = int(math.floor(perDayDurationMin / (sessionDurationGrade + breakTime)))
    subperDayCount = numberOfSubjects * maxSubLimit
    if totalDaySessionCount > subperDayCount:
        return subperDayCount
    else:
        return totalDaySessionCount


def checkIfSlotsAreEnoughForAdditionaOfferings(offeringsObject, studentObj,timetableObj,studyPrefGl):
    try:
        #get number sessions required to finish offering
        #get end slots for each day or remaining time
        #get slots remaining between given offering start date and end date
        #Check if number sessions are enough
        courseIdArray = []
        startDate,endDate = None,None
        numOfSubjects = len(offeringsObject)
        grade = int(studentObj.grade)
        sessionDurationGrade = getSessionDurationForGrade(grade)
        breakTime = 5

        #logService.logInfo("numOfSubjects ", str(numOfSubjects))

        for ofObj in offeringsObject:
            couseId = ofObj.course_id
            if couseId:
                courseIdArray.append(couseId)

            if startDate is None or startDate > ofObj.start_date:
                startDate = ofObj.start_date

            if endDate is None or endDate < ofObj.end_date:
                endDate = ofObj.end_date

        startDateStr, endDateStr = "", ""
        if startDate and endDate:
            startDateStr = genUtility.getStringFromDate(startDate)
            endDateStr = genUtility.getStringFromDate(endDate)

        if studyPrefGl:
            days,slots =  studyPrefGl["days"],studyPrefGl["slots"]
        else:
            days, slots = getStudentStudyPreference(studentObj.id)

        courseMetaData = getNumberOfSessionRequiredForCourseIds(courseIdArray)


        curSlotDetails,calDays = getSlotDetailsForStudent(studentObj, timetableObj, startDateStr, endDateStr)

        if calDays is None or len(calDays) <= 0:
            return True

        maxPerDaySubjectLimit = 1

        # Calculate remaining days before current schedule start date and check if they are useful
        usefulDaysCount = 0
        newEndDateStr = calDays[0]
        validSessionCount = 0
        newEndDate = genUtility.getDateFromString(newEndDateStr)
        if startDate < newEndDate:
            totalAvailableDaysBegining,dailySesAvailable = getUsefulFutureDaysForStudy(newEndDate, startDate, days, slots, sessionDurationGrade,breakTime, numOfSubjects,maxPerDaySubjectLimit)
            usefulDaysCount = totalAvailableDaysBegining
            validSessionCount = dailySesAvailable * totalAvailableDaysBegining

        overAllTimeRemaining = 0
        numberOfDaysUsed = len(calDays)
        for i in range(numberOfDaysUsed):
            cuCalDay = calDays[i]
            curData =  curSlotDetails.get(cuCalDay)
            maxEndTimeMin = curData["maxEndTimeMin"]
            overAllTimeRemaining = overAllTimeRemaining + calculateTimeRemainingPerDay(slots, maxEndTimeMin)
            #totalSessionCount =  int(math.floor(overAllTimeRemaining/(sessionDurationGrade + breakTime)))
            totalSessionCount = getNumberOfUsefulSessions(numOfSubjects, overAllTimeRemaining, sessionDurationGrade, breakTime,maxPerDaySubjectLimit)
            if totalSessionCount > 0:
                usefulDaysCount = usefulDaysCount + 1
                validSessionCount = validSessionCount + totalSessionCount

        #Calculate remaining days and check if they are useful
        finalDateStr = calDays[numberOfDaysUsed - 1]
        finalDate = genUtility.getDateFromString(finalDateStr)
        totalNumStudyDays,dailyUseFulSess = getUsefulFutureDaysForStudy(endDate, finalDate, days, slots, sessionDurationGrade, breakTime, numOfSubjects,maxPerDaySubjectLimit)
        usefulDaysCount = usefulDaysCount + totalNumStudyDays
        validSessionCount = validSessionCount + dailyUseFulSess * totalNumStudyDays

        #print("valid session count and daily count",validSessionCount,usefulDaysCount)
        logService.logInfo("valid session count and daily count " , str(validSessionCount) + str(usefulDaysCount))
        for key in courseMetaData:
            numberOfSessionStr =  courseMetaData[key]
            numberOfSession = int(numberOfSessionStr)
            logService.logInfo("course meta data check ", str(key) + " " + str(numberOfSession) + " "+ str(validSessionCount))

            if numberOfSession > validSessionCount:
                return False
            validSessionCount = validSessionCount - numberOfSession

        return True
    except Exception as e:
        logService.logException("checkIfSlotsAreEnoughForAdditionaOfferings", e.message)
        traceback.print_exc()
        print("checkIfSlotsAreEnoughForAdditionaOfferings ", e)

def inactivateStudyPrefrence(data):
    for singleData in data:
        singleData.status = "inactive"
        singleData.save()


def getStudyTimeByKey(key):
    settingsObj = SystemSettings.objects.get(key="studyTimeConfiguration")
    studyTimeJson = json.loads(str(settingsObj.value))
    for singleObj in studyTimeJson:
        keyName = singleObj.get("key")
        if keyName == key:
            return [singleObj.get("StartTime"), singleObj.get("EndTime")]


def getSystemSettingObj(key):
    return genUtility.getSystemSettingObj(key)


def slotKeyValidate(slots, settingsObj):
    keyNames = []

    keyNames = [singleObj.get("key") for singleObj in settingsObj]
    slotKeys = [singleSlot.get("key") for singleSlot in slots if singleSlot.get("key") in keyNames]
    if slotKeys:
        return True
    else:
        return False


def getTimeFromSettings(key, studyTimeJson):
    for singleObj in studyTimeJson:
        keyName = singleObj.get("key")
        if keyName == key:
            return [singleObj.get("StartTime"), singleObj.get("EndTime"), singleObj.get("startTimeMin"),
                    singleObj.get("endTimeMin")]


# return [singleObj.get("StartTime"),singleObj.get("EndTime")]
def daysValidatstion(data):
    for singleValue in data:
        try:
            int(singleValue)
            if not singleValue >= 0 or not singleValue <= 7:
                return False
        except:
            return False
    return True


def getGradeFromOffering(offering):
    grade = None
    obj = Offering.objects.get(id=offering)
    grade = obj.course.grade
    return grade


def sessionDurationByGrade(grade, sessionDurationJson):
    sessionDuration = sessionDurationJson.get(grade)
    return sessionDuration


def getTotalHoursPerDay(slots, studyTimeJson):
    duration = 0
    for singleSlot in slots:
        for singleKey in studyTimeJson:
            if singleSlot.get("key") == singleKey.get("key"):
                startTime = singleKey.get("StartTime")
                endTime = singleKey.get("EndTime")

                duration = int(endTime) - int(startTime)
                duration = + duration

    return duration

def getTotalStudyMinsPerDay(slots):
    durationTotal = 0
    for singleSlot in slots:
        startTime = singleSlot.get("startTimeMin")
        endTime = singleSlot.get("endTimeMin")

        duration = int(endTime) - int(startTime)
        durationTotal = durationTotal +  duration

    return durationTotal


def updateTimeTableForStudent(student):
    try:
        ttObjects = Time_Table.objects.filter(student=student)
        ttObject = None
        if ttObjects and len(ttObjects) > 0:
            ttObject = ttObjects[0]
            if ttObject.generation_status != "7":
                ttObject.generation_status = "3"
                ttObject.updated_on = genUtility.getCurrentTime()
        else:
            ttObject = Time_Table.objects.create(
                student=student
            )

        ttObject.save()

    except:
        logService.logException("updateTimeTableForStudent ", e.message)
        print("updateTimeTableForStudent ", e)


def getSystemSettingObjsByTime(slotslist):
    settingsObj = SystemSettings.objects.get(key="studyTimeConfiguration")
    studyTimeJson = json.loads(str(settingsObj.value))
    selectedSlots = []
    for i in slotslist:
        for singleslot in studyTimeJson:
            if i.get("startTime") == singleslot.get("StartTime") and i.get("endTime") == singleslot.get("EndTime"):
               selectedSlots.append(singleslot)
    return selectedSlots

def getStringFromIdArray(idsArray):
    return genUtility.getStringFromIdArray(idsArray)

def checkOfferingsOptedByStudent(studentId,offeringId):
    enrolledObj = Offering_enrolled_students.objects.get(student_id=studentId,offering=offeringId)
    if not enrolledObj:
        return False
    else:
        return True

def makeContentDict(fieldCount,fieldArr,eachRecord,tempDict):
    for i in range(fieldCount):
        tempDict[fieldArr[i]] = eachRecord[i]
    return tempDict

def checkPreviousSessionsAttended(sessionObj,offeringId):
    try:
        selectQuery = "SELECT id,has_attended from student_time_table_session where id < "+str(sessionObj.id)+" AND offering_id = " + str(offeringId) + " ORDER BY id DESC LIMIT 1"
        cursor = connection.cursor()
        cursor.execute(selectQuery)
        dataList = cursor.fetchall()
        for eachRecord in dataList:
            prevSessionId = eachRecord[0]
            hasAttended = eachRecord[1]
            if prevSessionId and hasAttended == 1:
                return True
    except:
        print("checkPreviousSessionsAttended", e)
        #traceback.print_exc()
        logService.logException("checkPreviousSessionsAttended", e.message)
    return False

def checkIfSessionInFuture(sessionObj):
    try:
        calDate = sessionObj.calDate
        todayDate = genUtility.getTodayDate()
        if calDate > todayDate:
            return True
    except Exception as e:
        print("checkIfSessionInFuture", e)
        # traceback.print_exc()
        logService.logException("checkIfSessionInFuture", e.message)
    return False


def enrollStudentToOfferings(offeringsObjects,studentObj):
    # Enroll for student for each offering
    for k in range(len(offeringsObjects)):
        offering = offeringsObjects[k]
        offering.enrolled_students.add(studentObj)

def updateTimetableRegeration(timetableObj,offeringsOpted):
    timetableObj.status = "pending"
    timetableObj.generation_status = "3"
    timetableObj.generation_type = "2"
    timetableObj.updated_on = genUtility.getCurrentTime()
    timetableObj.subject_to_be_processed = genUtility.getStringFromIdArray(offeringsOpted)
    timetableObj.save()

def verifyOTPWithServiceProvider(mobile,otp):
    return genUtility.verifyOTPWithServiceProvider(mobile,otp)

def sendOTPToMobileNumber(mobile,otpExpiryTime):
    return genUtility.sendOTPToMobileNumber(mobile, otpExpiryTime)

def getUserOTPObject(mobile,otp):
    return genUtility.getUserOTPObject(mobile,otp)

def getSystemSettingObjs(keyNames):
    objects = []
    try:
        objects = SystemSettings.objects.filter(key__in=keyNames)
    except:
        pass
    return objects

def getEnrolledStudentCountForDigitalSchool(dsschoolId):
    try:
        queryString = '''SELECT count(distinct se.student_id) from student_student_school_enrollment as se 
                WHERE  se.enrollment_status = 'active' AND se.digital_school_id = ''' + str(dsschoolId)
        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()
        studentCount = 0
        for eachRecord in dataList:
            studentCount = eachRecord[0]
            break
        return studentCount
    except Exception as e:
        print("getEnrolledStudentCountForDigitalSchool", e)
        #traceback.print_exc()
        logService.logException("getEnrolledStudentCountForDigitalSchool", e.message)
        return 0


def getDefaultSchoolDetailForboard(courseProviderId,grade):
    try:
        # Get settings
        # Get School for that given school Id with partner
        # Get DSM
        # Get school student count
        # Get Courses offered by school which are running , end date greater than today for that grade

        courseProviderObj = CourseProvider.objects.get(id=courseProviderId)
        schoolId = 0
        defaultSchoolSettings = genUtility.getDictObjectFromSystemSettingJSONForKey("defaultSchoolPerBoard")
        if defaultSchoolSettings:
            schoolIdStr = defaultSchoolSettings.get(courseProviderObj.code)
            if schoolIdStr:
                schoolId = long(schoolIdStr)
            else:
                return None
        else:
            return None

        dsSchool = None
        try:
            dsSchool = DigitalSchool.objects.get(id=schoolId,status='Active')
        except:
            return None

        dsmUser =  genUtility.getActiveDSMForSchool(dsSchool.id)

        userName = ""
        dsmUserId = None
        if dsmUser:
            userName = dsmUser.first_name + " " + dsmUser.last_name
            dsmUserId =dsmUser.id

        schoolCenter = Center.objects.get(digital_school=dsSchool)
        offeringObjs = Offering.objects.filter(center=schoolCenter, end_date__gte=genUtility.getCurrentTime(),status__in=['pending', 'running'],course__grade=grade).select_related('course')
        enrolledStudentCount = getEnrolledStudentCountForDigitalSchool(dsSchool.id)
        schoolDataObj = {
            "id":dsSchool.id,
            "name":dsSchool.name,
            "bannerUrl":dsSchool.banner_url,
            "schoolLogoUrl":dsSchool.logo_url,
            "description":dsSchool.description,
            "statementOfPurpose":dsSchool.statement_of_purpose,
            "status": dsSchool.status,
            "partnerId": dsSchool.partner_owner.id,
            "partnerName": dsSchool.partner_owner.name,
            "dsmName": userName,
            "dsmId": dsmUserId,
            "enrolledStudentCount":enrolledStudentCount,
            "medium":courseProviderObj.language_code
        }
        courseArray = []
        for i in range(len(offeringObjs)):
            offObj = offeringObjs[i]
            languageObj = offObj.course.language
            courseObj = {
                "offeringId":offObj.id,
                "name":offObj.course.subject,
                "courseId":offObj.course.id,
            }
            if languageObj:
                courseObj["languageId"] = languageObj.id
                courseObj["languageName"] = languageObj.name

            courseArray.append(courseObj)

        schoolDataObj["courses"] = courseArray
        return schoolDataObj
    except Exception as e:
        print("getDefaultSchoolDetailForboard", e)
        #traceback.print_exc()
        logService.logException("getDefaultSchoolDetailForboard", e.message)
        return None

def getAllowedTopicsForNewUser(courseId,numberChaptersAllowed):
    try:
        queryString = '''SELECT id FROM web_topic WHERE course_id_id = {} AND status != 'Inactive' ORDER BY priority LIMIT {}'''.format(courseId,numberChaptersAllowed)
        #logService.logInfo("getAllowedTopicsForNewUser",queryString)
        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()
        topicIdArray = []
        for eachRecord in dataList:
            topicId = eachRecord[0]
            topicIdArray.append(topicId)
        return topicIdArray
    except  Exception as e:
        print("getAllowedTopicsForNewUser", e)
        # traceback.print_exc()
        #logService.logException("getAllowedTopicsForNewUser", e.message)
        logService.logExceptionWithExceptionobject("getAllowedTopicsForNewUser",e)
        return []

def getAllowedSubTopicsForNewUser(topicId,numberChaptersAllowed):
    try:
        queryString = '''SELECT id FROM web_subtopics WHERE topic_id = {} AND status != 'Inactive' ORDER BY id LIMIT {}'''.format(topicId,numberChaptersAllowed)
        #logService.logInfo("getAllowedSubTopicsForNewUser", queryString)
        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()
        topicIdArray = []
        for eachRecord in dataList:
            topicId = eachRecord[0]
            topicIdArray.append(topicId)
        return topicIdArray
    except  Exception as e:
        print("getAllowedSubTopicsForNewUser", e)
        # traceback.print_exc()
        #logService.logException("getAllowedSubTopicsForNewUser", e.message)
        logService.logExceptionWithExceptionobject("getAllowedTopicsForNewUser", e)
        return []

def checkIfTopicAndSubtopicAllowedForNewUser(topicId,subtopicId,offeringObj,userType):
    # Check if this topic and sub topic allowed.
    chapterConfig = genUtility.getDictObjectFromSystemSettingJSONForKey("allowedChapterForNewUser")
    topicConfig = chapterConfig.get(userType)
    numberOfChapters = topicConfig.get("numberOfChapters")
    topicArray = getAllowedTopicsForNewUser(offeringObj.course_id, int(numberOfChapters))
    topicId = long(topicId)
    if topicId not in topicArray:
        return False

    subtopicId = long(subtopicId)
    subchaptersAllowed = topicConfig.get("numberOfSubtopicAllowedPerChapter")
    subtopicArray = getAllowedSubTopicsForNewUser(topicId, subchaptersAllowed)
    if subtopicId not in subtopicArray:
        return False
    return True

def getDeviceId(guardian,deviceInfo):
    deviceId = deviceInfo["deviceId"]
    userDevices = UserDevice.objects.filter(deviceId=deviceId, status=True, user_type='guardian', device_type='mobile')
    if userDevices and len(userDevices) > 0:
        return userDevices[0]
    return None

def updateOrCreateDeviceObjectForGuardian(guardian,deviceInfo):
    try:
        deviceId = deviceInfo["deviceId"]
        if deviceId is None:
            return None
        osType = deviceInfo["osType"]
        userDevices = UserDevice.objects.filter(deviceId=deviceId,status=True,user_type='guardian',device_type='mobile')
        if userDevices and len(userDevices) > 0:
            devcieObj = userDevices[0]
            if devcieObj.belongs_to_id != guardian.id:
                devcieObj.belongs_to_id = guardian.id
                devcieObj.save()
            return devcieObj
        else:
            devcieObj = UserDevice.objects.create(
                deviceId=deviceId,
                belongs_to_id = guardian.id,
                created_by_id = settings.SYSTEM_USER_ID_AUTH,
                updated_by_id=settings.SYSTEM_USER_ID_AUTH
            )
            devcieObj.save()
            return  devcieObj
    except Exception as e:
        print("updateOrCreateDeviceObjectForGuardian", e)
        logService.logExceptionWithExceptionobject("updateOrCreateDeviceObjectForGuardian ", e)
        return None

## END OF REUSABLE and INTERNAL FUNCTION

## API requests are below
@transaction.commit_on_success
def enrolStudentInDigitalSchool(request,requestParams,schoolRec,staffRec,partnerId,userType,guardianObj):
    #create student
    #create guardian
    #map guardian to student
    #enroll student to school

    try:
        isEnrollmentByGuardian = False
        if userType == 'guardian':
            isEnrollmentByGuardian = True

        #Validate required parameters
        try:
            studentName = getValueElseThrowException(requestParams, 'studentName')
            userObj = None
            if isEnrollmentByGuardian is False:
                parentName = getValueElseThrowException(requestParams, 'parentName')
                mobile = getValueElseThrowException(requestParams, 'mobile')
                userObj = request.user
            else:
                parentName = guardianObj.full_name
                mobile = guardianObj.mobile
                userObj = genUtility.getUserObj(settings.SYSTEM_USER_ID_AUTH)

            relationshipType = getValueElseThrowException(requestParams, 'relationshipType')
            dob = getValueElseThrowException(requestParams, 'dob')
            gender = getValueElseThrowException(requestParams, 'gender')
            grade = getValueElseThrowException(requestParams, 'grade')
            mediumOfStudy = getValueElseThrowException(requestParams, 'mediumOfStudy')
            hasTakenGuardianConsent = getValueElseThrowException(requestParams, 'hasTakenGuardianConsent')
            physicalSchoolName = getValueElseThrowException(requestParams, 'physicalSchoolName')

        except Exception as e:
            #logService.logException("kMissingReqFields ",e.message)
            return genUtility.getStandardErrorResponse(request, "kMissingReqFields")

        profilePicId = requestParams.get("profilePicId")
        offeringsOpted = requestParams.get("offeringsOpted")

        if hasTakenGuardianConsent == 0:
            return genUtility.getStandardErrorResponse(request, "kConsentMandatory")

        profileDocUrl = None
        profileDoc = None
        if profilePicId:
            profileDoc = getUserDocument(profilePicId)
            if profileDoc is None:
                return sendErrorResponse(request, "kFileDoesnotExist")
            profileDocUrl = profileDoc.url

        if isRelationShipTypeValid(relationshipType) is False:
            return sendErrorResponse(request, "kInvalidStudentRelationType")

        if isGenderValid(gender) is False:
            return sendErrorResponse(request, "kInvalidGender")

        language = Language.objects.get(id=mediumOfStudy)
        if language is None:
            return sendErrorResponse(request, "kInvalidLanguage")

        centerRec = None
        if staffRec:
            centerRec = staffRec.center

        if centerRec is None:
            centerRec = getCenterObjects(schoolRec)
            if centerRec is None:
                return genUtility.getStandardErrorResponse(request, "kCenterDoesNotExist")

        offeringsObjects = []
        if offeringsOpted and offeringsOpted != "" and len(offeringsOpted) > 0:
            offeringsObjects= getOfferings(offeringsOpted,centerRec)
            if offeringsObjects is None or len(offeringsObjects) <= 0:
                return sendErrorResponse(request, "kInvalidOfferings")



        dobDate =  genUtility.getDateFromString(dob)

        try:
            if studentName:
                #Student, Guardian, Map, Offering,Enrollment
                student = Student.objects.create(
                    name=studentName,
                    center=centerRec,
                    dob=dobDate,
                    gender=gender,
                    grade=grade,
                    phone=mobile,
                    status="Active",
                    created_by=userObj,
                    updated_by=userObj,
                    enrolled_by=userObj,
                    enrolled_on=datetimeObj.now(),
                    physical_school=physicalSchoolName,
                    profile_doc=profileDoc,
                    profile_pic_url=profileDocUrl,
                    school_medium_lng=language
                    )
                student.save()

                guardianMap =  createGuardianObjectIfNeeded(userObj, student, mobile, relationshipType, True, parentName,'1')

                enrollment = Student_School_Enrollment.objects.create(
                    student=student,
                    digital_school = schoolRec,
                    center = centerRec,
                    enrollment_status = "active",
                    enrolled_by=userObj,
                    created_by=userObj,
                    updated_by=userObj,
                    payment_status='free'
                    )
                enrollment.save()

                genUtility.updateDocumentBelongsTo(profileDoc,student.id)
                #Enroll for student for each offering
                for k in range(len(offeringsObjects)):
                    offering = offeringsObjects[k]
                    offering.enrolled_students.add(student)

                dataObj = {
                    "id": student.id,
                    "message": "Student enrolled  successfully"
                }
                return genUtility.getSuccessApiResponse(request, dataObj)

        except Exception as e:
            logService.logException("enrolStudentInDigitalSchool ", e.message)
            return genUtility.getStandardErrorResponse(request, "kStudentEnrollmentFailed")

    except Exception as e:
        print("enrolStudentInDigitalSchool",e)
        logService.logException("enrolStudentInDigitalSchool ", e.message)
        return genUtility.getStandardErrorResponse(request, "kStudentEnrollmentFailed")

@transaction.commit_on_success
def editStudentEnrollmentForPartner(request,requestParams,schoolRec,staffRec,partnerId,studentId):
    try:
        studentRec = Student.objects.get(id=studentId)
        guardianRelObj = getGuardianForStudent(studentRec)
        guardian = guardianRelObj.guardian

        studentName = requestParams.get("studentName")
        parentName = requestParams.get("parentName")
        relationshipType = requestParams.get("relationshipType")
        mobile = requestParams.get("mobile")
        dob = requestParams.get("dob")
        gender = requestParams.get("gender")
        grade = requestParams.get("grade")
        mediumOfStudy = requestParams.get("mediumOfStudy")
        hasTakenGuardianConsent = requestParams.get("hasTakenGuardianConsent")
        physicalSchoolName = requestParams.get("physicalSchoolName")
        profilePicId = requestParams.get("profilePicId")
        offeringsOpted = requestParams.get("offeringsOpted")
        studentStatus = requestParams.get("status")


        if grade and (grade != studentRec.grade):
            if studentRec.onboarding_status == "completed":
                return genUtility.getStandardErrorResponse(request, "kGradeCannotChange")


        if hasTakenGuardianConsent == 0:
            return genUtility.getStandardErrorResponse(request, "kConsentMandatory")

        if relationshipType and isRelationShipTypeValid(relationshipType) is False:
            return sendErrorResponse(request, "kInvalidStudentRelationType")

        if gender and isGenderValid(gender) is False:
            return sendErrorResponse(request, "kInvalidGender")

        oldLanguage = studentRec.school_medium_lng
        newLanguage = None
        if mediumOfStudy and oldLanguage.id != mediumOfStudy:
            language = Language.objects.get(id=mediumOfStudy)
            if language is None:
                return sendErrorResponse(request, "kInvalidLanguage")
            else:
                newLanguage = language

        profileDocUrl = None
        newProfileDoc = None
        oldProfileDoc = studentRec.profile_doc
        if profilePicId and (oldProfileDoc is None or oldProfileDoc.id != profilePicId):
            profileDoc = getUserDocument(profilePicId)
            if profileDoc is None:
                return sendErrorResponse(request, "kFileDoesnotExist")
            profileDocUrl = profileDoc.url
            newProfileDoc = profileDoc

        centerRec = staffRec.center
        if centerRec is None:
            centerRec = getCenterObjects(schoolRec)
            if centerRec is None:
                return genUtility.getStandardErrorResponse(request, "kCenterDoesNotExist")

        newOfferingsToBeAdded = None
        offeringsTobeRemoved = None
        if offeringsOpted and offeringsOpted != "" and len(offeringsOpted) > 0:
            oldOfferings = getOfferingsForSchoolCenterForStudent(centerRec,str(studentId))
            if oldOfferings and len(oldOfferings) > 0:
                oldOffIds = oldOfferings #getIdsListFromObjectList(oldOfferings)
                diffList = differenceInList(offeringsOpted, oldOffIds)
                if len(diffList) > 0:
                    newOfferingsToBeAdded = diffList

                diffList = differenceInList(oldOffIds, offeringsOpted)
                if len(diffList) > 0:
                    offeringsTobeRemoved = diffList
            else:
                newOfferingsToBeAdded = offeringsOpted

        offeringsObjects = []

        if newOfferingsToBeAdded and len(newOfferingsToBeAdded) > 0:
            offeringsObjects = getOfferings(newOfferingsToBeAdded, centerRec)
            if offeringsObjects is None or len(offeringsObjects) <= 0:
                return sendErrorResponse(request, "kInvalidOfferings")

        # update student record
        # Update guardian record
        # update enrollment to offering or remove enrollment
        userObj = request.user

        if studentName and (studentName != studentRec.name):
            studentRec.name = studentName

        if mobile and (mobile != studentRec.phone):
            studentRec.phone = mobile

        if gender and (gender != studentRec.gender):
            studentRec.gender = gender

        if grade and (grade != studentRec.grade):
            studentRec.grade = grade

        if physicalSchoolName and (physicalSchoolName != studentRec.physical_school):
            studentRec.physical_school = physicalSchoolName

        if newProfileDoc:
            studentRec.profile_doc = newProfileDoc
            studentRec.profile_pic_url = profileDocUrl
            genUtility.updateDocumentBelongsTo(newProfileDoc, studentRec.id)

        if newLanguage:
            studentRec.school_medium_lng = newLanguage

        if dob:
            dobDate = genUtility.getDateFromString(dob)
            if studentRec.dob:
                previousDateStr = genUtility.getStringFromDate(studentRec.dob)
                if previousDateStr != dob:
                    studentRec.dob = dobDate
            else:
                studentRec.dob = dobDate
        if studentStatus:
            studentStatus = int(studentStatus)


        if studentStatus and studentStatus == 1 and studentRec.status != "Active":
            studentRec.status = "Active"
        elif studentStatus and studentStatus == 2 and studentRec.status == "Active":
            studentRec.status = "Alumni"


        studentRec.save()


        #update Guardian record
        isNewGuardianToBeCreated = False
        if guardian is None or guardian.mobile != mobile:
            isNewGuardianToBeCreated = True

        if isNewGuardianToBeCreated is True:
            newGuardianMap = createGuardianObjectIfNeeded(userObj, studentRec, mobile, relationshipType, True, parentName,'1')
            guardianRelObj.status = False
            guardianRelObj.save()
        else:
            if relationshipType and relationshipType != guardianRelObj.relationship_type:
                guardianRelObj.relationship_type = relationshipType

            if parentName and parentName != guardian.full_name:
                guardian.full_name = parentName
            guardianRelObj.save()
            guardian.save()


        # update Offerings record
        # Enroll for student for each offering
        for k in range(len(offeringsObjects)):
            offering = offeringsObjects[k]
            offering.enrolled_students.add(studentRec)



        if offeringsTobeRemoved and len(offeringsTobeRemoved) > 0:
            objectsToBeRemoved = getOfferings(offeringsTobeRemoved, centerRec)
            for k in range(len(objectsToBeRemoved)):
                offering = objectsToBeRemoved[k]
                offering.enrolled_students.remove(studentRec)


        dataObj = {
            "id": studentRec.id,
            "message": "Student updated  successfully"
        }
       
        return genUtility.getSuccessApiResponse(request, dataObj)

    except Exception as e:
        logService.logException("Edit enrolStudentByDSM ", e.message)
        return genUtility.getStandardErrorResponse(request, "kStudentEnrollmentFailed")


def getStudentListForPartner(request):
    try:
        digitalSchoolId = request.GET.get('digitalSchoolId')
        userType = request.GET.get('userType')
        page = request.GET.get('page')
        count = request.GET.get('count')
        user = request.user
        if digitalSchoolId is None or userType is None:
            return sendErrorResponse(request, "kMissingReqFields")
        else:

            if userType != "DSM":
                return sendErrorResponse(request, "kInvalidUserType")
            else:
                staff = isUserDSMOfSchool(digitalSchoolId,user)
                if staff is None:
                    return sendErrorResponse(request, "kInvalidUserType")

                courseProviderId = request.GET.get('courseProviderId')
                boardName = None
                if courseProviderId and genUtility.checkIfParamIfInteger(courseProviderId):
                    cp = getCourseProviderObject(courseProviderId)
                    if cp is None:
                        return sendErrorResponse(request, "kCourseProviderDoesNotExist")
                    else:
                        boardName = cp.code

                grade = request.GET.get('grade')
                offeringId = request.GET.get('offeringId')
                academicYearId = request.GET.get('academicYearId')
                try:
                    studRespList = []
                    totalCount = 0
                    fetcStudentDetails = False
                    if page is None:
                        page = 0


                    page = int(page)
                    if page == 0:
                        countData = filterStudentByParameters(digitalSchoolId, page, count, boardName, offeringId, grade,
                                                            academicYearId, True)
                        if countData and len(countData) > 0:
                            totalCount = countData[0].get("count")
                            if totalCount > 0:
                                fetcStudentDetails = True
                    else:
                        fetcStudentDetails = True

                    if fetcStudentDetails is True:
                            studentList = filterStudentByParameters(digitalSchoolId,page,count,boardName,offeringId,grade,academicYearId,False)
                            if studentList:
                                studRespList = studentList

                    dataObject = {
                            "students": studRespList,
                            "totalCount":totalCount
                    }
                    return genUtility.getSuccessApiResponse(request, dataObject)
                except Exception as e:
                    logService.logException("getStudentListForPartner ", e.message)
                    return sendErrorResponse(request, "kInvalidRequest")
    except Exception as e:
        logService.logException("getStudentListForPartner ", e.message)
        return sendErrorResponse(request, "kInvalidRequest")


def getStudentDetailForPartner(request,studentId):
    digitalSchoolId = request.GET.get('digitalSchoolId')
    if studentId is None or (genUtility.checkIfParamIfInteger(studentId) is False) or digitalSchoolId is None:
        return genUtility.getStandardErrorResponse(request, "kMissingReqFields")
    try:

        student = Student.objects.get(id=studentId)
        mediumOfStudy = {}
        if student.school_medium_lng is not None:
            mediumOfStudy = {"languageId": student.school_medium_lng.id, "name": student.school_medium_lng.name}

        dobString = ""
        if student.dob:
             dobString = genUtility.getStringFromDate(student.dob)
        aGuardian = None
        profilePicId = None
        if student.profile_doc:
            profilePicId = student.profile_doc.id

        studentDict = {
            "id":student.id,
            "name":student.name,
            "profileUrl":student.profile_pic_url,
            "dob":dobString,
            "gender":student.gender,
            "physicalSchoolName":student.physical_school,
            "grade":student.grade,
            "mediumOfStudy":mediumOfStudy,
            "profilePicId":profilePicId,
            "status":student.status,
            "onboardingStatus":student.onboarding_status
        }

        guardians = Student_Guardian_Relation.objects.filter(student=student,is_primary_guardian=True,status=True).prefetch_related("guardian")
        if guardians and len(guardians) > 0:
            aRelationShipObj = guardians[0]
            studentDict["guardianName"] = aRelationShipObj.guardian.full_name
            studentDict["mobile"] = aRelationShipObj.guardian.mobile
            studentDict["relationshipType"] = aRelationShipObj.relationship_type

        center = getCenterObjectsForId(digitalSchoolId)
        if center is not None:
            offeringId = request.GET.get('offeringId')
            courses = getOfferingsOfStudentForSchool(student,center,digitalSchoolId,offeringId)
            if courses and len(courses) > 0:
                studentDict["offeringsOpted"] = courses
            dataObject = {
                "students": studentDict,
            }
            return genUtility.getSuccessApiResponse(request, dataObject)

        else:
            return genUtility.getStandardErrorResponse(request, "kCenterDoesNotExist")

    except Exception as e:
        logService.logException("getStudentDetailForPartner ", e.message)
        return genUtility.getStandardErrorResponse(request, "kStudentNotFound")


@csrf_exempt
def signin_mobile(request):
    try:
        if genUtility.is_basic_auth_authenticated(request) is False or request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        mobile = requestBodyParams.get("mobile")
        otpExpiryTime = genUtility.getSystemSettingValue("otpExpiryTime")
        if not mobile:
            return sendErrorResponse(request, "kMissingReqFields")
        try:
            userProfileObj = Guardian.objects.get(mobile=mobile,status='Active')
        except:
            return sendErrorResponse(request, "kUserDoesNotExist")


        if len(str(mobile)) > 10 or len(str(mobile)) < 10 :
            return sendErrorResponse(request, "kInvalidMobileNum")
        if genUtility.isDevEnvironment() is False:
            isSent = sendOTPToMobileNumber(mobile, otpExpiryTime)
            if isSent:
                dataObj = {
                    "message": "otp sent successfully" 
                }
                return genUtility.getSuccessApiResponse(request, dataObj)
            else:
                return sendErrorResponse(request, "kOtpNotSent")
        else:
            dataObj = {
                    "message": "otp sent successfully" 
                }
            return genUtility.getSuccessApiResponse(request, dataObj)
        
    except Exception as e:
        print("signin_mobile", e)
        logService.logException("signin_mobile", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def send_otp_guardian(request):
    try:
        if genUtility.is_basic_auth_authenticated(request) is False or request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        mobile = requestBodyParams.get("mobile")
        otpExpiryTime = genUtility.getSystemSettingValue("otpExpiryTime")
        maxOTPPerHour = genUtility.getSystemSettingValue("maxOTPPerHour")
        maxOTPPerHour = int(maxOTPPerHour)
        if not mobile:
            return sendErrorResponse(request, "kMissingReqFields")

        if genUtility.isValidMobileNumber(mobile) is False:
            return sendErrorResponse(request, "kInvalidMobileNum")

        guardianObj =  getGuardianForMobileNumber(str(mobile))
        if guardianObj:
            return sendErrorResponse(request, "kGuardianExist")

        if genUtility.isDevEnvironment() is False:
            curDate = genUtility.getTimeBeforeXhours(1)
            otpObjs = UserOtp.objects.filter(mobile=mobile,created_on__gte=curDate)
            if otpObjs and (len(otpObjs) >= maxOTPPerHour):
                return sendErrorResponse(request, "kMaxOTPExceed")

            sentOTP = sendOTPToMobileNumber(mobile, otpExpiryTime)
            mobile,sentOTP = str(mobile),str(sentOTP)
            if sentOTP:
                otpExpTime = genUtility.getTimeAfterXMinutesToDate(genUtility.getCurrentTime(),int(otpExpiryTime))
                otpObj =  UserOtp.objects.create(mobile=mobile,otp=sentOTP,type='guardian',expiry_time=otpExpTime)
                otpObj.save()
                dataObj = {
                    "message": "otp sent successfully"
                }
                return genUtility.getSuccessApiResponse(request, dataObj)
            else:
                return sendErrorResponse(request, "kOtpNotSent")
        else:
            dataObj = {
                "message": "otp sent successfully"
            }
            return genUtility.getSuccessApiResponse(request, dataObj)

    except Exception as e:
        print("send_otp_guardian", e)
        logService.logException("send_otp_guardian",e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def verify_otp(request):
    try:
        if genUtility.is_basic_auth_authenticated(request) is False or request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        mobile = requestBodyParams.get("mobile")
        otp = requestBodyParams.get("otp")
        deviceInfo = requestBodyParams.get("deviceInfo")

        if not mobile or not otp:
            return sendErrorResponse(request, "kMissingReqFields")

        verificationStatus = verifyOTPWithServiceProvider(mobile,otp)
        if verificationStatus == "success":
            try:
                userObj = Guardian.objects.get(mobile=mobile)
            except Exception as e:
                logService.logException("verify_otp user obj", e.message)
            if userObj:
                sessionObj = genUtility.createSessionForUser(userObj=None,type="guardian",id=userObj.id)
                session_key = sessionObj.session_key
                expiryTimeStamp = genUtility.getTimeStampFromDate(sessionObj.expiry_time)
                if userObj.created_on:
                    createdDate = genUtility.getTimeStampFromDate(userObj.created_on)
                else:
                    createdDate = None
                if userObj.has_logged_in_once is True:
                    pass
                else:
                    userObj.has_logged_in_once = True
                    userObj.first_logged_date = genUtility.getCurrentTime()
                    userObj.save()

                kycStatus = False
                if deviceInfo:
                    updateOrCreateDeviceObjectForGuardian(userObj,deviceInfo)

                responseData = {
                    "sessionId": session_key,
                    "sessionExpiryTime": str(expiryTimeStamp),
                    "fullName":userObj.full_name,
                    "status":userObj.status,
                    "mobile":userObj.mobile,
                    "kycStatus":kycStatus,
                    "createdDate":createdDate,
                    "id":userObj.id
                    
                }
                return genUtility.getSuccessApiResponse(request, responseData)
            else:
                return sendErrorResponse(request, "kUserProfileDoesNotExist")
        elif verificationStatus == "expired":
            return sendErrorResponse(request, "kOtpExpired")
        else:
            return sendErrorResponse(request, "kInvalidOtp")
    except Exception as e:
        logService.logException("verifyOTP", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def guardian_registration_api(request):
    try:
        if genUtility.is_basic_auth_authenticated(request) is False or request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        mobile = requestBodyParams.get("mobile")
        otp = requestBodyParams.get("otp")
        name = requestBodyParams.get("name")
        deviceInfo = requestBodyParams.get("deviceInfo")

        if not mobile or not otp or not name:
            return sendErrorResponse(request, "kMissingReqFields")

        if genUtility.isValidMobileNumber(mobile) is False:
            return sendErrorResponse(request, "kInvalidMobileNum")

        #verify parameters
        #Check if Mobile exist already
        #Verify OTP in our DB that its active
        #verify OTP with third party service
        #make otp inactive in our
        #Create guardian if required
        #Create session

        mobileStr = str(mobile)
        guardianObj = getGuardianForMobileNumber(mobileStr)
        if guardianObj:
            return sendErrorResponse(request, "kGuardianExist")

        isDevEnvironment = genUtility.isDevEnvironment()


        otpObj = getUserOTPObject(mobileStr,otp)
        if isDevEnvironment is False:
            if otpObj is None or otpObj.status is False:
                return sendErrorResponse(request, "kInvalidOtp")


        verificationStatus = verifyOTPWithServiceProvider(mobile, otp)
        if verificationStatus == "success":
            guardian = createGuardianObjecWithoutStudent(mobile,name,None,'2')
            sessionObj = genUtility.createSessionForUser(userObj=None, type="guardian", id=guardian.id)
            sessionObj.save()
            session_key = sessionObj.session_key
            expiryTimeStamp = genUtility.getTimeStampFromDate(sessionObj.expiry_time)
            createdDate = genUtility.getTimeStampFromDate(guardian.created_on)
            guardian.has_logged_in_once = True
            guardian.first_logged_date = genUtility.getCurrentTime()
            guardian.save()
            kycStatus = False
            if otpObj:
                otpObj.status = False
                otpObj.save()

            if deviceInfo:
                updateOrCreateDeviceObjectForGuardian(guardian, deviceInfo)

            responseData = {
                "sessionId": session_key,
                "sessionExpiryTime": str(expiryTimeStamp),
                "fullName": guardian.full_name,
                "status": guardian.status,
                "mobile": guardian.mobile,
                "kycStatus": kycStatus,
                "createdDate": createdDate,
                "id": guardian.id
            }
            return genUtility.getSuccessApiResponse(request, responseData)
        elif verificationStatus == "expired":
            return sendErrorResponse(request, "kOtpExpired")
        else:
            return sendErrorResponse(request, "kInvalidOtp")
    except Exception as e:
        logService.logException("guardian_registration_api", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def guardian_students(request):
    if request.method == "GET":
        try:
            if genUtility.isGuardianUserAuthenticated(request) is False:
                return genUtility.getForbiddenRequestErrorApiResponse(request)
            userId = request.GET.get("userId")
            userType = request.GET.get("userType")

            if not userId or not userType:
                return sendErrorResponse(request, "kMissingReqFields")

            try:
                int(userId)
            except:
                return sendErrorResponse(request, "kUserID")

            if not genUtility.isGuardian(userId,userType):
                return sendErrorResponse(request, "kUserGuardian")

            selectClauseStr = '''st.id, st.name, st.gender,st.grade, st.status, st.profile_pic_url, st.onboarding_status,
                                st.class_status, ds.id, ds.name, ds.logo_url, ds.banner_url,cp.name,cp.code'''

            fieldArray = ["id","name","gender","grade","status","profileImageUrl","onboardingStatus", "classStatus"]
            schoolfieldArray = ["id","name","schoolLogoUrl","schoolBannerUrl","boardName","boardCode"]

            queryString = '''select '''+selectClauseStr +'''
                        FROM student_guardian as gu
                        LEFT JOIN student_student_guardian_relation as sg on (sg.guardian_id = gu.id and sg.status=TRUE)
                        LEFT JOIN web_student as st on (st.id = sg.student_id)
                        LEFT JOIN student_student_school_enrollment as es on (es.student_id = st.id)
                        LEFT JOIN web_digitalschool as ds on (ds.id = es.digital_school_id)
                        LEFT JOIN web_courseprovider as cp on (cp.id = ds.course_provider_id)
                        WHERE  gu.id = {}'''.format(str(userId))

            cursor = connection.cursor()
            cursor.execute(queryString)
            dataList = cursor.fetchall()
            studentsList = []
            fieldCount = len(fieldArray)
            schoolfieldCount = len(schoolfieldArray)
            count = 0
            for eachRecord in dataList:
                if eachRecord[0]:
                    eachObject = {
                        "schoolAssigned": {}
                    }
                    for i in range(fieldCount):
                        fieldName = fieldArray[i]
                        eachObject[fieldName] = eachRecord[i]
                    for i in range(schoolfieldCount):
                        element = fieldCount + i
                        fieldName = schoolfieldArray[i]
                        eachObject["schoolAssigned"][fieldName] = eachRecord[element]
                    studentsList.append(eachObject)

            dataObj = {
                    "students": studentsList
                }
            return genUtility.getSuccessApiResponse(request, dataObj)
        except Exception as e:
            logService.logException("guardian_students", e.message)
            return sendErrorResponse(request, "kInvalidRequest")
    else:
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def digital_school_offerings(request):
    if request.method != 'GET':
        return sendErrorResponse(request, "kInvalidRequest")
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        digitalSchoolId = request.GET.get("digitalSchoolId")
        grade = request.GET.get("grade")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")

        if not digitalSchoolId or not grade or not userId or not userType:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(userId) or 
           not genUtility.isint(grade) or 
           not genUtility.isint(digitalSchoolId)):
            return sendErrorResponse(request, "kInvalidRequest")

        try:
            DigitalSchool.objects.get(id=digitalSchoolId)
        except:
            return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")
        try:
            if grade >= 1:
                pass
            else:
                return sendErrorResponse(request, "kGradeIdGreater")
        except:
            pass

        if not genUtility.isGuardian(userId,userType) and not genUtility.isStudent(userId,userType):
            return sendErrorResponse(request, "kUserGuardianStudent")

        currentYear = dateObj.today().year
        ncurDateTime = genUtility.getCurrentTime()
        centerId = getCenterId(digitalSchoolId)
        if not centerId:
            return genUtility.getStandardErrorResponse(request, "kCenterDoesNotExist")
        offeringsObj = Offering.objects.filter(
            course__grade = grade,
            center__in = centerId,
            status__in=['pending', 'running'],
        ).select_related('course')

        subjects = []
       
        for singleoffering in offeringsObj:
            data = {}
            if ((singleoffering.end_date == None or 
            singleoffering.end_date >= datetimeObj.now()) and (singleoffering.status != 'completed') ):
                data['id'] = singleoffering.id
                data['name'] = singleoffering.course.subject
                language = singleoffering.course.language
                if language:
                    data['languageId'] = language.id
                    data['languageName'] = language.name
                subjects.append(data)
        
        responseData = {
            "courses": subjects
        }
        return genUtility.getSuccessApiResponse(request, responseData)
    except Exception as e:
        print("digital_school_offerings", e)
        logService.logException("digital_school_offerings", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def generic_offering(request):
    if genUtility.isGuardianUserAuthenticated(request) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)

    if request.method == 'POST':
        return assigncourse(request)
    else:
        if request.method == 'GET':
            return get_student_offerings(request)
        else:
            return sendErrorResponse(request, "kInvalidRequest")

def get_student_offerings(request):
    try:
        digitalSchoolId = request.GET.get("digitalSchoolId")
        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")

        if not digitalSchoolId or not studentId or not userId or not userType:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(userId) or 
            not genUtility.isint(studentId) or
            not genUtility.isint(digitalSchoolId)
            ):
            return sendErrorResponse(request, "kInvalidRequest")

        try:
            Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")
        try:
            DigitalSchool.objects.get(id=digitalSchoolId)
        except:
            return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")

        if not genUtility.isGuardian(userId,userType) and not genUtility.isStudent(userId,userType):
            return sendErrorResponse(request, "kUserGuardianStudent")

        centerId = getCenterId(digitalSchoolId)
        if not centerId:
            return genUtility.getStandardErrorResponse(request, "kCenterDoesNotExist")

        #TODO: Optimise this code
        curDateTime = genUtility.getCurrentTime()
        offeringId = getOfferingsByCenterIdList(centerId,curDateTime)

        enrolledOfferingObj = Offering_enrolled_students.objects.filter(
            student_id = studentId,
            offering_id__in = offeringId
        )

        fieldArray = ["id","name"]
        subjects = []
        offeringObj = getOfferingByEnrolledObj(enrolledOfferingObj)

        for singleoffering in offeringObj:
            data = {}
            data['id'] = singleoffering.id
            data['name'] = singleoffering.course.subject
            subjects.append(data)

        responseData = {
            "courses": subjects
        }
        return genUtility.getSuccessApiResponse(request, responseData)

    except:
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def student_subject_add(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        if request.method != 'POST':
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        digitalSchoolId = requestBodyParams.get("digitalSchoolId")
        offeringsOpted = requestBodyParams.get("offerings")
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")


        if not digitalSchoolId or not offeringsOpted or not studentId or not userId or not userType:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(userId) or
            not genUtility.isint(studentId) or
            not genUtility.isint(digitalSchoolId)
            ):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        #Get student obj
        try:
            studentObj = Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")
        #Get Time table object
        try:
            timetableObj = Time_Table.objects.get(student=studentObj)
        except:
            return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")

        centerObj = getCenterObjectsForId(digitalSchoolId)
        if not centerObj:
           return genUtility.getStandardErrorResponse(request, "kCenterDoesNotExist")

        newOfferingObjs = getOfferings(offeringsOpted, centerObj)
        if len(newOfferingObjs) < len(offeringsOpted):
            return sendErrorResponse(request, "kInvalidOfferings")

        studyPref = None
        isSlotEnough =  checkIfSlotsAreEnoughForAdditionaOfferings(newOfferingObjs,studentObj,timetableObj,studyPref)
        responseData = {
            "isUpdateScheduleRequired": 0
        }
        #isSlotEnough = True
        if isSlotEnough is False:
            responseData["isUpdateScheduleRequired"] = 1
        else:
            # Add offering
            enrollStudentToOfferings(newOfferingObjs,studentObj)

            # update time table status
            updateTimetableRegeration(timetableObj, offeringsOpted)

        return genUtility.getSuccessApiResponse(request, responseData)
    except Exception as e:
        print("student_subject_add ",e)
        traceback.print_exc()
        logService.logException("student_subject_add", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def assigncourse(request):
    try:
        requestBodyParams = simplejson.loads(request.body)
        digitalSchoolId = requestBodyParams.get("digitalSchoolId")
        offeringsOpted = requestBodyParams.get("offerings")
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")


        if not digitalSchoolId or not offeringsOpted or not studentId or not userId or not userType:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(userId) or 
            not genUtility.isint(studentId) or
            not genUtility.isint(digitalSchoolId)
            ):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        #Get student obj
        try:
            studentObj = Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")
        #Get digital school obj
        try:
            digitalSchoolObj = DigitalSchool.objects.get(id=digitalSchoolId)
        except:
            return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")

        if not genUtility.isGuardian(userId,userType) and not genUtility.isStudent(userId,userType):
            return sendErrorResponse(request, "kUserGuardianStudent")
        centerObj = getCenterObjectsForId(digitalSchoolId)
        if not centerObj:
           return genUtility.getStandardErrorResponse(request, "kCenterDoesNotExist")


        newOfferingsToBeAdded = None
        offeringsTobeRemoved = None
        if offeringsOpted and offeringsOpted != "" and len(offeringsOpted) > 0:
            oldOfferings = getOfferingsForSchoolCenterForStudent(centerObj,str(studentId))
            if oldOfferings and len(oldOfferings) > 0:
                oldOffIds = oldOfferings #getIdsListFromObjectList(oldOfferings)
                diffList = differenceInList(offeringsOpted, oldOffIds)
                if len(diffList) > 0:
                    newOfferingsToBeAdded = diffList

                diffList = differenceInList(oldOffIds, offeringsOpted)
                if len(diffList) > 0:
                    offeringsTobeRemoved = diffList
            else:
                newOfferingsToBeAdded = offeringsOpted

        offeringsObjects = []

        if newOfferingsToBeAdded and len(newOfferingsToBeAdded) > 0:
            offeringsObjects = getOfferings(newOfferingsToBeAdded, centerObj)
            if offeringsObjects is None or len(offeringsObjects) <= 0:
                return sendErrorResponse(request, "kInvalidOfferings")

        # update Offerings record
        # Enroll for student for each offering
        for k in range(len(offeringsObjects)):
            offering = offeringsObjects[k]
            offering.enrolled_students.add(studentObj)

        if offeringsObjects:
            try:
                studentObj.onboarding_status = 'schedule not opted'
                studentObj.save()
            except:
                pass

        if offeringsTobeRemoved and len(offeringsTobeRemoved) > 0:
            objectsToBeRemoved = getOfferings(offeringsTobeRemoved, centerObj)
            for k in range(len(objectsToBeRemoved)):
                offering = objectsToBeRemoved[k]
                offering.enrolled_students.remove(studentObj)

        responseData = {
            "message":"offering added successfully!",
            "isUpdateScheduleRequired":0
        }
        return genUtility.getSuccessApiResponse(request, responseData)
    except:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def student_ping_api(request):
    if request.method != 'POST':
        return sendErrorResponse(request, "kInvalidRequest")

    if genUtility.is_basic_auth_authenticated(request) is False :
        return genUtility.getForbiddenRequestErrorApiResponse(request)

    try:
        requestBodyParams = simplejson.loads(request.body)
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")

        if not userId or not genUtility.isint(userId):
            return sendErrorResponse(request, "kMissingReqFields")

        userStatus = None
        keyNames = ["otpExpiryTime","studyTimeConfiguration","allowedChapterForNewUser","supportedGradesForb2c"]
        jsonKeys = ["studyTimeConfiguration","allowedChapterForNewUser","supportedGrades"]

        settings =  genUtility.getSettingsForUserType("guardian", keyNames, jsonKeys)

        try:
            sessionObj = request.currentSession
            sessionId = sessionObj.session_key
        except:
            sessionId = None
        if userId and userType and genUtility.isGuardian(userId,userType):
            guardianObj = Guardian.objects.get(id=userId)
            userStatus = guardianObj.status
        
        if userId and userType and genUtility.isStudent(userId,userType):
            studentObj = Student.objects.get(id=userId)
            userStatus = studentObj.status

        dataObj = {
                'sessionId': sessionId,
                'userId': userId,
                'settings':settings,
                'userStatus':userStatus

            }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("Student ping call",e)
        traceback.print_exc()
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def schedulecourse(request):
    if genUtility.isGuardianUserAuthenticated(request) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)

    if request.method == 'POST':
        return updateStudyPreference(request)
    else:
        if request.method == 'GET':
            return getStudyPreference(request)
        else:
            return sendErrorResponse(request, "kInvalidRequest")


def updateStudyPreference(request):
    try:
        requestBodyParams = simplejson.loads(request.body)
        studentId = requestBodyParams.get("studentId")
        digitalSchoolId = requestBodyParams.get("digitalSchoolId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        days = requestBodyParams.get("days")
        slots = requestBodyParams.get("slots")
        newOfferingsIds = requestBodyParams.get("newOfferings")
        isUpdateScheduleRequired = requestBodyParams.get("isUpdateScheduleRequired")
        
        if not days or not studentId or not userId or not userType or not slots:
            return sendErrorResponse(request, "kMissingReqFields")
        
        if not genUtility.isint(userId) or not genUtility.isint(studentId):
            return sendErrorResponse(request, "kInvalidRequest")

        if not daysValidatstion(days):
            return sendErrorResponse(request,"kDataFormatWrong")
        days = set(days)
        days = list(days)
        if not genUtility.isGuardian(userId,userType):
            return sendErrorResponse(request, "kUserGuardian")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        #Get student obj
        try:
            studentObj = Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")
        #Get digital school obj
        try:
            DigitalSchool.objects.get(id=digitalSchoolId)
        except:
            return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")


        centerObj = getCenterObjectsForId(digitalSchoolId)
        if not centerObj:
            return genUtility.getStandardErrorResponse(request, "kCenterDoesNotExist")
        centerIds = [centerObj.id]

        curDateTime = genUtility.getCurrentTime()
        offeringIds = getOfferingsByCenterIdList(centerIds,curDateTime)
        enrolledOfferingObj = Offering_enrolled_students.objects.filter(
            student_id=studentId,
            offering_id__in=offeringIds
        )

        offerIdLen = 1
        if enrolledOfferingObj and len(enrolledOfferingObj) > 0:
            offerIdLen = len(enrolledOfferingObj)

        isOfferingAndUpdateSchedule = False
        newOfferingObjs = None
        timetableObject = None
        if isUpdateScheduleRequired and isUpdateScheduleRequired == 1 and newOfferingsIds and len(newOfferingsIds) > 0:
            newOfferingObjs = getOfferings(newOfferingsIds, centerObj)
            if len(newOfferingObjs) < len(newOfferingsIds):
                return sendErrorResponse(request, "kInvalidOfferings")

            timetableObject = getTimetableObject(studentObj)
            if timetableObject is None:
                return sendErrorResponse(request, "kSlotsEditFailed")

            offerIdLen = offerIdLen + len(newOfferingsIds)
            isOfferingAndUpdateSchedule = True

        grade = studentObj.grade
        if not grade:
            return sendErrorResponse(request, "kSystemSettings")
        settingsObj = getSystemSettingObj("studyTimeConfiguration")
        studyTimeJson = json.loads(str(settingsObj.value))
        sessionDurationObj = getSystemSettingObj("SessonDurationGradewise")
        sessionDurationJson = ast.literal_eval(sessionDurationObj.value)
        sessionDuration = sessionDurationByGrade(grade,sessionDurationJson)
        totalDuration = int(sessionDuration) * offerIdLen * 3
        dayDuration = getTotalHoursPerDay(slots,studyTimeJson)
        studyPrefDuration = len(days) * dayDuration * 60
        if totalDuration > studyPrefDuration:
            return sendErrorResponse(request, "kSelectTime")

        if not slotKeyValidate(slots,studyTimeJson):
             return sendErrorResponse(request,"kDataFormatWrong")

        if isOfferingAndUpdateSchedule:
            studyPref = None
            slotsArray = []
            for eachSlot in slots:
                key = eachSlot["key"]
                startTime, endTime, startTimeMin, endTimeMin = getTimeFromSettings(key, studyTimeJson)
                slotsArray.append({"startTimeMin": startTimeMin,"endTimeMin": endTimeMin})
            studyPref = {"slots":slotsArray,"days":days}
            isSlotEnough = checkIfSlotsAreEnoughForAdditionaOfferings(newOfferingObjs, studentObj, timetableObject,studyPref)
            if isSlotEnough is False:
                return sendErrorResponse(request, "kSlotsNotEnough")

        studyPreffObj = Study_Time_Preference.objects.filter(student__id=studentId,status="active")
        if studyPreffObj:
            inactivateStudyPrefrence(studyPreffObj)
        # create study time preference
        for singleDay in days:
            for singleSlot in slots:
                key = singleSlot["key"]
                startTime,endTime,startTimeMin,endTimeMin = getTimeFromSettings(key,studyTimeJson)
                Study_Time_Preference.objects.create(
                    student = studentObj,
                    day_of_the_week = singleDay,
                    time_start = startTime,
                    time_end = endTime,
                    start_time_min=startTimeMin,
                    end_time_min=endTimeMin,
                )

        dataObj = {
            "id": studentId,
            "message": "schedule created successfully!"
        }

        if isOfferingAndUpdateSchedule is True:
            # Add offering and  update time table status
            enrollStudentToOfferings(newOfferingObjs, studentObj)
            updateTimetableRegeration(timetableObject, newOfferingsIds)
            return genUtility.getSuccessApiResponse(request, dataObj)
        try:
            studentObj.onboarding_status = 'completed'
            studentObj.save()
            #Create time table entry with status pending
            updateTimeTableForStudent(studentObj)
        except:
            pass

        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        logService.logException("postSchedule", e.message)
        print("postSchedule", e.message)
        return sendErrorResponse(request, "kInvalidRequest")


def getStudyPreference(request):
    try:
        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")

        if not studentId or not userId or not userType:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(studentId):
            return sendErrorResponse(request, "kInvalidRequest")
        #Get Student obj
        try:
            Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")

        if not genUtility.isGuardian(userId,userType):
            return sendErrorResponse(request, "kUserGuardian")
        days, slotslist = getStudentStudyPreference(studentId)
        selectedSlots = getSystemSettingObjsByTime(slotslist)
        dataObj = {
                "id":studentId,
                "days":days,
                "slots":selectedSlots

            }
        return genUtility.getSuccessApiResponse(request, dataObj)
        
    except:
        logging.exception("message")

def getTeacherForOffering(student,offeringId):
    try:
        teaderObj = None
        try:
            offObj = Offering.objects.get(id=offeringId)
            if offObj.active_teacher_id and offObj.active_teacher_id > 0:
                return offObj.active_teacher
        except:
            return None

        offeringString = str(offeringId)
        fieldStr = "ws.id, ws.teacher_id"
        whereClsStr = "ws.status = 'scheduled' and ws.offering_id IN ("+offeringString+") and ws.teacher_id IS NOT NULL"

        selectQuery = '''select '''+fieldStr +''' from web_session as ws 
                WHERE ''' + whereClsStr + '''  ORDER BY ws.id LIMIT 1'''

        cursor = connection.cursor()
        cursor.execute(selectQuery)
        dataList = cursor.fetchall()
        teacherId = None
        for eachRecord in dataList:
            tempId = eachRecord[1]
            if tempId and tempId > 0:
                teacherId = tempId
                break
        if teacherId:
            teaderObj = User.objects.get(id=teacherId)

        return teaderObj
    except Exception as e:
        print("getTeacherForOffering", e)
        logService.logException("getTeacherForOffering function", e.message)
        #traceback.print_exc()
        return None

def getLiveSessions(student,offeringId,startDate,endDate,centerObj):
    sessionList = None
    liveSessionDict = None
    totalCount = 0
    sessionIdsUnique = []
    try:
        offeringIds = []
        offeringString = ""
        if offeringId is None or offeringId == "":
            offeringIds = getOfferingsForSchoolCenterForStudent(centerObj,str(student.id))
            if offeringIds and len(offeringIds) > 0:
                offeringString = getStringFromIdArray(offeringIds)

        else:
            offeringString = str(offeringId)


        startDateStr = startDate + " "+"00:00:00"
        endDateStr = endDate+" "+"23:59:59"

        fieldsArray = ["id","offeringId","startDate","endDate","teacherName","status","liveClassUrl","subjectName","lngId","lngName","lngCode","attendanceRec"]
        fieldStr = "ws.id, ws.offering_id,ws.date_start,ws.date_end,au.first_name ,ws.status,ws.ts_link,wc.subject,gl.id,gl.name,gl.code,COUNT(wsa.id)"
        whereClsStr = "ws.status = 'scheduled' and ws.ts_link IS NOT NULL and ws.offering_id IN ("+offeringString+") and ws.date_start >= '"+startDateStr+"' and ws.date_start <= '"+ endDateStr +"'"

        selectQuery = '''select '''+fieldStr +''' from web_session as ws 
                LEFT JOIN auth_user as au on (au.id = ws.teacher_id)
                LEFT JOIN web_offering as wo on (wo.id = ws.offering_id)
                LEFT JOIN web_course as wc on (wc.id = wo.course_id)
                LEFT JOIN genutilities_language as gl on (gl.id = wc.language_id AND wc.language_id IS NOT NULL)
                LEFT JOIN web_sessionattendance as wsa on (wsa.session_id = ws.id AND wsa.is_present = 'yes')
                WHERE ''' + whereClsStr + ''' GROUP BY ws.id ORDER BY ws.date_start'''

        cursor = connection.cursor()
        cursor.execute(selectQuery)
        dataList = cursor.fetchall()

        sessionList = []
        fieldCount = len(fieldsArray)
        for eachRecord in dataList:
            eachObject = {}
            calDateString = None
            for i in range(fieldCount):
                fieldName = fieldsArray[i]
                if fieldName == "startDate":
                    startDateObj = eachRecord[i]
                    if startDateObj:
                        dateObjStr = genUtility.getStringFromDate(startDateObj)
                        eachObject["calDate"] = dateObjStr
                        calDateString = dateObjStr

                        eachObject["startTime"] = genUtility.getTimeStringFromDate(startDateObj)
                        eachObject["startTimeMin"] = genUtility.getTimeInMinutesDateObj(startDateObj)
                elif fieldName == "endDate":
                    endDateObj = eachRecord[i]
                    if endDateObj:
                        eachObject["endTime"] = genUtility.getTimeStringFromDate(endDateObj)
                        eachObject["endTimeMin"] = genUtility.getTimeInMinutesDateObj(endDateObj)
                elif fieldName == "attendanceRec":
                    attendanceCount = eachRecord[i]
                    hasAttended = 0
                    if attendanceCount and attendanceCount > 0:
                        hasAttended = 1
                    eachObject["hasAttended"] = hasAttended
                else:
                    eachObject[fieldName] = eachRecord[i]
            eachObject["classType"] = "2"
            if calDateString:
                if liveSessionDict is None:
                    liveSessionDict = {}
                sesList = liveSessionDict.get(calDateString)
                if sesList:
                    sesList.append(eachObject)
                else:
                    sesList = [eachObject]
                    liveSessionDict[calDateString] = sesList

            sessionIdsUnique.append(eachObject["id"])
            sessionList.append(eachObject)
            totalCount = totalCount + 1

        return (liveSessionDict,totalCount,sessionIdsUnique)

    except Exception as e:
        print("getLiveSessions", e)
        logService.logException("getLiveSessions function", e.message)
        #traceback.print_exc()
        return (None,0,None)

@csrf_exempt
def student_session_detail(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        sessionId = request.GET.get("sessionId")


        if not studentId or not userId or not sessionId or not userType:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(studentId):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        # Get Student obj
        studentObj = None
        try:
            studentObj = Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")

        if not genUtility.isGuardian(userId, userType):
            return sendErrorResponse(request, "kUserGuardian")


        # get Time Table object
        timeTable = None
        ttObjects = Time_Table.objects.filter(student=studentObj, status__in=["active"])
        if ttObjects and len(ttObjects) > 0:
            timeTable = ttObjects[0]
        else:
            return sendErrorResponse(request, "kStudentNotFound")

        sessionObj = None
        ttObjects = Time_Table_Session.objects.filter(timetable=timeTable, id=sessionId)
        if ttObjects and len(ttObjects) > 0:
            sessionObj = ttObjects[0]
        else:
            return sendErrorResponse(request, "kInvalidSession")


        subtopicStr = sessionObj.subtopic_ids
        subtopicObjects = []
        if subtopicStr:
            subtopicIds = subtopicStr.split(",")
            if subtopicIds and len(subtopicIds) > 0:
                stTopicsIds = SubTopics.objects.filter(id__in=subtopicIds)
                for stObj in stTopicsIds:
                    record = {}
                    record["id"] = stObj.id
                    record["name"] = stObj.name
                    record["type"] = stObj.type
                    subtopicObjects.append(record)


        dataObj = {
            "sessionId": sessionId,
            "subtopics": subtopicObjects
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("student_session_detail", e)
        # traceback.print_exc()
        logService.logException("student_session_detail", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

def getLiveClassToPreAppendIfAny(liveSessionDict,eachObject,sessionIdStatus,topicIdSessionMap,topicIdNameMap):
    livClsList = None
    if liveSessionDict is None:
        return livClsList
    try:
        calDate = eachObject["calDate"]
        sessionList = liveSessionDict.get(calDate)
        if sessionList and len(sessionList) > 0:
            startTime = eachObject["startTimeMin"]
            endTime = eachObject["endTimeMin"]
            livClsList = []
            for l in range(len(sessionList)):
                livSesObj = sessionList[l]
                sessId = livSesObj["id"]
                status = sessionIdStatus.get(sessId)
                if status and status == 1:
                    continue
                else:
                    sLivMin = livSesObj["startTimeMin"]
                    if startTime >= sLivMin:
                        updateTopicNameForSessionId(topicIdSessionMap, topicIdNameMap, livSesObj)
                        livClsList.append(livSesObj)
                        sessionIdStatus[sessId] = 1
        return livClsList
    except Exception as e:
        print("getLiveClassToPreAppendIfAny", e)
        #traceback.print_exc()
        logService.logException("getLiveClassToPreAppendIfAny", e.message)
        return livClsList

def updateTopicNameForSessionId(topicIdSessionMap,topicIdNameMap,livSesObj):
    if topicIdSessionMap and topicIdNameMap:
        sessId = livSesObj["id"]
        topicId = topicIdSessionMap.get(sessId)
        if topicId:
            livSesObj["topicName"] = topicIdNameMap.get(topicId)

def getMissingDates(allDatesQueries,nextDate,previousDate,liveSessionDict,topicIdSessionMap,topicIdNameMap):
    if liveSessionDict is None:
        return ([],None)
    newLiveSessList = []
    index = 0
    #print("allDatesQueries",allDatesQueries,nextDate)
    for r in range(len(allDatesQueries)):
        dateStr = allDatesQueries[r]
        if dateStr != nextDate:
            index = index + 1
            dl = liveSessionDict.get(dateStr)
            if dl:
                for l in range(len(dl)):
                    livSesObj = dl[l]
                    updateTopicNameForSessionId(topicIdSessionMap, topicIdNameMap, livSesObj)
                newLiveSessList.extend(dl)
        else:
            index = index + 1
            break
    if index < len(allDatesQueries):
        allDatesQueries = allDatesQueries[index:]
    else:
        allDatesQueries = []

    return (allDatesQueries,newLiveSessList)

def getPendingListFromLiveSessions(sessionIdStatusObj,calDate,liveSessionDict,topicIdSessionMap,topicIdNameMap):
    if liveSessionDict is None:
        return None
    newRecList = liveSessionDict.get(calDate)
    pendingList = []
    if newRecList and len(newRecList) > 0:
        newRcLen = len(newRecList)
        for t in range(newRcLen):
            eachRec = newRecList[t]
            sesId = eachRec["id"]
            statusKey = sessionIdStatusObj.get(sesId)
            if statusKey and statusKey == 1:
                pass
            else:
                updateTopicNameForSessionId(topicIdSessionMap, topicIdNameMap, eachRec)
                pendingList.append(eachRec)
    return pendingList


def getTopicMappingForTopicIds(topicIds):
    topicIdNameMap = {}
    try:
        sesionString = getStringFromIdArray(topicIds)
        whereClsStr = " id IN (" + sesionString + ")"

        selectQuery = '''select id,title from web_topic as wt 
                        WHERE ''' + whereClsStr
        cursor = connection.cursor()
        cursor.execute(selectQuery)
        dataList = cursor.fetchall()
        for eachRecord in dataList:
            tpId = eachRecord[0]
            if tpId:
                tpname = eachRecord[1]
                if tpname:
                    topicIdNameMap[tpId] = tpname
        return topicIdNameMap
    except Exception as e:
        print("getTopicMappingForTopicIds", e)
        logService.logException("getTopicMappingForTopicIds function", e.message)
        return None


def getTopicIdForSessions(sessionIdsUnique):
    topicIdSessionMap = {}
    try:
        topicIds = []
        sesionString = getStringFromIdArray(sessionIdsUnique)
        fieldStr = "ws.session_id, MIN(ws.topic_id)"
        whereClsStr = " ws.session_id IN (" + sesionString + ") GROUP BY ws.session_id"

        selectQuery = '''select ''' + fieldStr + ''' from web_session_planned_topics as ws 
                    WHERE ''' + whereClsStr


        #logService.logInfo("selectQuery LIVE", selectQuery)
        cursor = connection.cursor()
        cursor.execute(selectQuery)
        dataList = cursor.fetchall()
        for eachRecord in dataList:
            sessionId = eachRecord[0]
            if sessionId:
                topicId = eachRecord[1]
                if topicId:
                    topicIdSessionMap[sessionId] = topicId
                    topicIds.append(topicId)

        topicIdTittleMap = {}
        if len(topicIds) > 0:
            topicIdTittleMap = getTopicMappingForTopicIds(topicIds)

        return (topicIdSessionMap,topicIdTittleMap)
    except Exception as e:
        print("getTopicIdForSessions", e)
        logService.logException("getTopicIdForSessions function", e.message)
        return None,None

@csrf_exempt
def student_session(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        startDate = request.GET.get("startDate")
        endDate = request.GET.get("endDate")
        page = request.GET.get("page")
        count = request.GET.get("count")
        offeringId = request.GET.get("offeringId")
        schoolId = request.GET.get("schoolId")

        classType = request.GET.get("classType")


        if not studentId or not userId or not userType or not startDate or not endDate or not schoolId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(studentId) :
            return sendErrorResponse(request, "kInvalidRequest")

        isMissedClassOnly = False
        if classType and genUtility.isint(classType):
            classType = int(classType)
            if classType == 1:
                isMissedClassOnly = True

        else:
            if classType:
                return sendErrorResponse(request, "kInvalidRequest")


        if not genUtility.checkIfParamIfInteger(startDate) or not genUtility.checkIfParamIfInteger(endDate):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        #logService.logInfo("dataFromTimeStampToObj",str(startDate))
        startDateObj = genUtility.dataFromTimeStampToObj(float(startDate))
        endDateObj = genUtility.dataFromTimeStampToObj(float(endDate))

        curDate = genUtility.getTodayDate()
        endTodayDate = endDateObj.date()
        if isMissedClassOnly is True and (endTodayDate >= curDate):
            endDateObj = genUtility.getTimeBeforeXhours(24)

        startDateStr,endDateStr = "",""
        allDateObjs = []
        if startDateObj and endDateObj:
            startDateStr = genUtility.getStringFromDate(startDateObj)
            endDateStr = genUtility.getStringFromDate(endDateObj)
            if startDateStr != endDateStr:
                allDateObjs = genUtility.getDatesBetweenStartandEndDate(startDateObj,endDateObj,startDateStr,endDateStr)
                #print("allDateObjs",allDateObjs,startDateStr,endDateStr,startDateStr)
        else:
            return sendErrorResponse(request, "kInvalidRequest")

        #Get Student obj
        studentObj = None
        try:
            studentObj = Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")

        if not genUtility.isGuardian(userId,userType):
            return sendErrorResponse(request, "kUserGuardian")

        centerObj = getCenterObjectsForId(schoolId)
        if centerObj is None:
            return sendErrorResponse(request, "kCenterDoesNotExist")

        #get Time Table object
        timeTable = None
        ttObjects = Time_Table.objects.filter(student=studentObj,status__in=["pending","active"])
        if ttObjects and len(ttObjects) > 0:
            timeTable = ttObjects[0]
        else:
            return sendErrorResponse(request, "kStudentNotFound")


        if timeTable.status == "pending":
            dataObj = {
                "timetableStatus": "pending"
            }
            return genUtility.getSuccessApiResponse(request, dataObj)

        if page and genUtility.checkIfParamIfInteger(page) and count and genUtility.checkIfParamIfInteger(count) :
            page = int(page)
            if page < 0:
                page = 0
            count = int(count)
            if count > 50:
                count = 50
            page = page * count
        else:
            page,count = 0,50


        offeringIdStr = ""
        if offeringId and genUtility.checkIfParamIfInteger(offeringId):
            offeringIdStr = " AND " + 'sts.offering_id = '+str(offeringId)


        sessionIdStatusObj = {}
        classTypeClause = ''
        if isMissedClassOnly:
            liveSessionDict,totalLivClass,sessionIdsUnique = None,0,None
            classTypeClause = ' AND (sts.has_attended != 1 OR  sts.has_attended IS NULL ) '
        else:
            liveSessionDict,totalLivClass,sessionIdsUnique = getLiveSessions(studentObj, offeringId, startDateStr, endDateStr, centerObj)


        #get Topic names
        topicIdNameMap = {}
        topicIdSessionMap = {}
        if sessionIdsUnique and len(sessionIdsUnique) > 0:
            topicIdSessionMap,topicIdNameMap = getTopicIdForSessions(sessionIdsUnique)
            #print("topicIdNameMap",topicIdNameMap,topicIdSessionMap)


        #Prepare query with all the filters
        whereClsStr = "sts.timetable_id = " + str(timeTable.id) + " AND calDate >= '"+startDateStr+"' AND calDate <= '"+endDateStr+"'" + classTypeClause + offeringIdStr
        fieldsArray = ["offeringId","topicId","id","startTime","endTime","calDate","hasAttended","subtopicIdStr","classType","dayOfWeek","topicName","subjectName","lngId","lngName","lngCode"]
        fieldStr = "sts.offering_id,sts.topic_id, sts.id, sts.time_start ,sts.time_end,sts.calDate,sts.has_attended,sts.subtopic_ids, sts.session_type, sts.day_of_the_week,wt.title,wc.subject,wc.language_id,gl.name,gl.code"
        selectQUery = '''select ''' +fieldStr+ ''' from student_time_table_session as sts 
            LEFT JOIN web_topic as wt on (wt.id = sts.topic_id)
            LEFT JOIN web_course as wc on (wc.id = wt.course_id_id)
            LEFT JOIN genutilities_language as gl on (gl.id = wc.language_id AND wc.language_id IS NOT NULL)
            where ''' + whereClsStr + " ORDER BY sts.calDate,sts.time_start" + " LIMIT "+str(count)+" OFFSET "+str(page)

        #parse results and update page count
        #logService.logInfo("selectQUery",selectQUery)
        #logService.logInfo("selectQUery Get sess",selectQUery)
        cursor = connection.cursor()
        cursor.execute(selectQUery)
        dataList = cursor.fetchall()
        sessionList = []
        fieldCount = len(fieldsArray)
        previusDateKey = ""
        #SET PREVIOUS DATE
        if dataList and len(dataList) > 0:
            firstRecord = dataList[0]
            calDateObj = firstRecord[5]
            previusDateKey = genUtility.getStringFromDate(calDateObj)
            allDateObjs, remainingnewList = getMissingDates(allDateObjs, previusDateKey, "", liveSessionDict,topicIdSessionMap,topicIdNameMap)
            if remainingnewList and len(remainingnewList) > 0:
                sessionList.extend(remainingnewList)

        totalVodCount = len(dataList)
        recCounter = 0
        for eachRecord in dataList:
            eachObject = {}
            for i in range(fieldCount):
                fieldName = fieldsArray[i]
                if fieldName == "startTime" or  fieldName == "endTime":
                    timeStr = genUtility.getTimeInHHMMFormat(eachRecord[i])
                    eachObject[fieldName+"Min"] = eachRecord[i]
                    eachObject[fieldName] = timeStr

                elif fieldName == "calDate":
                    calDateObj = eachRecord[i]
                    dateStr = genUtility.getStringFromDate(calDateObj)
                    eachObject[fieldName] = dateStr
                else:
                    eachObject[fieldName] = eachRecord[i]
            eachObject["classType"] = "1"


            currentCalKey =  eachObject["calDate"]
            #Check if last record
            lastRecAndChangeKeyTrue = False
            if currentCalKey != previusDateKey or (recCounter == (totalVodCount - 1)):
                #Get any remaining live sessions from previous Date Key
                newLivList = getPendingListFromLiveSessions(sessionIdStatusObj, previusDateKey, liveSessionDict,topicIdSessionMap,topicIdNameMap)
                if newLivList and len(newLivList) > 0:
                    sessionList.extend(newLivList)

                if currentCalKey != previusDateKey and (recCounter == (totalVodCount - 1)):
                    lastRecAndChangeKeyTrue = True

                if allDateObjs and len(allDateObjs) > 0 and (currentCalKey != previusDateKey):
                    # Get any remaining live sessions for all dates from previous Date till current date
                    allDateObjs, remainingnewList = getMissingDates(allDateObjs, currentCalKey, previusDateKey,
                                                                liveSessionDict,topicIdSessionMap,topicIdNameMap)
                    if remainingnewList and len(remainingnewList) > 0:
                        sessionList.extend(remainingnewList)

                previusDateKey = currentCalKey


            #Get live classes if any to prepend on the same day
            liveClassList = getLiveClassToPreAppendIfAny(liveSessionDict, eachObject, sessionIdStatusObj,
                                                         topicIdSessionMap, topicIdNameMap)
            if liveClassList and len(liveClassList) > 0:
                sessionList.extend(liveClassList)

            sessionList.append(eachObject)
            if lastRecAndChangeKeyTrue is True:
                # Get any remaining live sessions for all dates from previous Date till current date
                #this is only for use case of last object has new date and also its a last  record
                newLivList = getPendingListFromLiveSessions(sessionIdStatusObj, previusDateKey, liveSessionDict,
                                                            topicIdSessionMap, topicIdNameMap)
                if newLivList and len(newLivList) > 0:
                    sessionList.extend(newLivList)

            recCounter = recCounter + 1

        if allDateObjs and len(allDateObjs) > 0:
            # this is only for use case of last object has new date and also its a last  record.
            allDateObjs, remainingnewList = getMissingDates(allDateObjs, previusDateKey, previusDateKey,
                                                            liveSessionDict, topicIdSessionMap, topicIdNameMap)
            if remainingnewList and len(remainingnewList) > 0:
                sessionList.extend(remainingnewList)


        totalVodClass = totalVodCount
        dataObj = {
            "timeTableId":timeTable.id,
            "count":totalVodClass,
            "timetableStatus":"completed",
            "sessions":sessionList
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("get_student_session", e)
        traceback.print_exc()
        logService.logException("get_student_session", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

def getContentForSubtopicId(studentId,subtopicId,topicId):
    try:
        viewStatusStr = ""
        if studentId:
            selectClauseStr = '''sd.id, ct.code, cm.code, ca.name, ws.code, sd.url, sd.duration, sc.progress, sc.status, sd.name, sd.description,sd.is_primary'''
            fieldArr = ['id', 'contentType', 'contentHost', 'author', 'mode', 'url', 'duration', 'progress',
                        'viewStatus', 'title', 'description', 'type']
            viewStatusStr = ''' left join student_content_view_status as sc on (sc.student_id = {} and sc.content_detail_id = sd.id) '''.format(
                studentId)
        else:
            selectClauseStr = '''sd.id, ct.code, cm.code, ca.name, ws.code, sd.url, sd.duration, sd.name, sd.description,sd.is_primary'''
            fieldArr = ['id', 'contentType', 'contentHost', 'author', 'mode', 'url', 'duration', 'title', 'description',
                        'type']

        queryString = '''select ''' + selectClauseStr + ''' FROM web_contentdetail as sd
               left join web_workstreamtype as ws ON (ws.id = sd.workstream_type_id)
               left join web_contenttypemaster as ct on (ct.id = sd.content_type_id)
               left join web_contenthostmaster as cm on (cm.id = sd.url_host_id)
               left join web_contentauthor as ca on (ca.id = sd.author_id) 
               ''' + viewStatusStr + ''' where (sd.subtopic_id = {} and sd.topic_id = {} and sd.status="approved") order by sd.priority;'''.format(
            subtopicId, topicId)

        # logService.logInfo("queryString",queryString)
        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()

        videos = []
        worksheets = []
        activities = []
        textbook = []

        fieldCount = len(fieldArr)
        for eachRecord in dataList:
            tempDict = {}
            code = eachRecord[4]
            if code == 'video':
                tempDict = makeContentDict(fieldCount, fieldArr, eachRecord, tempDict)
                videos.append(tempDict)
            if code == 'activity':
                tempDict = makeContentDict(fieldCount, fieldArr, eachRecord, tempDict)
                activities.append(tempDict)
            if code == 'worksheet':
                tempDict = makeContentDict(fieldCount, fieldArr, eachRecord, tempDict)
                worksheets.append(tempDict)
            if code == 'textbook':
                tempDict = makeContentDict(fieldCount, fieldArr, eachRecord, tempDict)
                textbook.append(tempDict)

        contentDetailData = {
            "videos": videos,
            "worksheets": worksheets,
            "activities": activities,
            "textbook": textbook
        }
        return contentDetailData
    except Exception as e:
        logService.logException("getContentForSubtopicId", e.message)
        return {}


@csrf_exempt
def contentdetails(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        sessionId = request.GET.get("sessionId")
        offeringId = request.GET.get("offeringId")
        topicId = request.GET.get("topicId")
        timetableId = request.GET.get("timetableId")
        subtopicId = request.GET.get("subtopicId")

        if  not userId or not userType  or not offeringId or not topicId  or not subtopicId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId):
            return sendErrorResponse(request, "kInvalidRequest")

        if not genUtility.isGuardian(userId, userType):
            return sendErrorResponse(request, "kUserGuardian")

        # Get offeringObj obj
        try:
            offeringObj = Offering.objects.get(id=offeringId)
        except:
            return sendErrorResponse(request, "kInvalidOfferings")

        if studentId and sessionId:

            if not timetableId:
                return sendErrorResponse(request, "kMissingReqFields")

            if not genUtility.isint(sessionId) or not genUtility.isint(studentId):
                return sendErrorResponse(request, "kInvalidRequest")

            if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
                return sendErrorResponse(request, "kInvalidStudentGuardRel")

            # Validate  Student obj
            try:
                studentObj = Student.objects.get(id=studentId)
            except:
                return sendErrorResponse(request, "kStudentNotFound")



            sessionObj = None
            # Get session obj
            try:
                sessionObj = Time_Table_Session.objects.get(id=sessionId)
            except:
                return sendErrorResponse(request, "kInvalidSession")

                # check if session is future session
            if checkIfSessionInFuture(sessionObj) is True:
                hasAttended = checkPreviousSessionsAttended(sessionObj, sessionObj.offering_id)
                hasAttended = True
                if hasAttended is False:
                    return sendErrorResponse(request, "kAttendPrevSession")

            # Get Topic obj
            try:
                topicObj = Topic.objects.get(id=topicId)
            except:
                return sendErrorResponse(request, "kInvalidSubtopic")

            # Get offeringObj obj
            try:
                offeringObj = Offering.objects.get(id=offeringId)
            except:
                return sendErrorResponse(request, "kStudentNotFound")
            # check topic course id should match with offering course id

            if not topicObj.course_id.id == offeringObj.course.id:
                return sendErrorResponse(request, "kInvalidRequest")

            if not checkOfferingsOptedByStudent(studentId, offeringId):
                return sendErrorResponse(request, "kInvalidRequest")

        else:
            # Check if this topic and sub topic allowed.
            isAllowed = checkIfTopicAndSubtopicAllowedForNewUser(topicId, subtopicId, offeringObj, "parent")
            if isAllowed is False:
                return sendErrorResponse(request, "kAccessDenied")

        hardCodedResponse = getContentForSubtopicId(studentId, subtopicId, topicId)
        hasAttended,hasLiked = 0,0
        if studentId  and sessionId:
            hasLiked = 0
            ratingObjList = Content_Rating.objects.filter(student_id=studentId, subtopic_id=subtopicId)
            if ratingObjList and len(ratingObjList) > 0:
                ratingObj = ratingObjList[0]
                ratingVal = ratingObj.rating
                if ratingVal >= 5:
                    hasLiked = 1

            hasAttended = 0
            if sessionObj.has_attended is True:
                hasAttended = 1

        dataObj = {
            "hasLiked":hasLiked,
            "hasAttended":hasAttended,
            "sessions":hardCodedResponse,
            "contentDetail":hardCodedResponse
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        logService.logException("courseDetails", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")

def getsubtopicsId(sessionObj):
    subtopic_ids = sessionObj.subtopic_ids
    if subtopic_ids:
        subtopic_ids = str(subtopic_ids).split(',')
    return subtopic_ids

def checkAndCreateStudentContentView(subtopicId,studentId,contentDeatailsObj,sessionObj):
    ctView = None
    isNewRecord = False
    try:
        ctView = Content_View_Status.objects.get(subtopic__id=subtopicId,content_detail=contentDeatailsObj,student_id=studentId)
    except Content_View_Status.DoesNotExist:
        ctView = Content_View_Status.objects.create(
            content_detail = contentDeatailsObj,
            status = 2,
            student_id = studentId,
            subtopic_id = subtopicId,
            session = sessionObj,
            offering_id = sessionObj.offering_id
        )
        ctView.save()
        isNewRecord = True
    except Exception as e:
        logService.logException("checkAndCreateStudentContentView", e.message)
        return None

    return (ctView,isNewRecord)

def checkSessionAndConTentView(subtopic_ids,studentId,contentDetailsId):
    contentObjs = Content_View_Status.objects.filter(
        student__id = studentId,
        subtopic__id__in = subtopic_ids
    ).annotate(Count('subtopic__id',distinct=True))
    if len(contentObjs) >= len(subtopic_ids):
        return True
    else:
        return False

def checkClientSubtopicInSession(subtopic_ids,subtopicId):
    if subtopicId in subtopic_ids:
        return True
    else:
        return False

def update_liveclass_attendance(request,sessionId,studentObj):
    try:
        try:
            sessionObj = Session.objects.get(id=sessionId)
        except:
            return sendErrorResponse(request, "kInvalidSession")

        sessAttendance = None
        sessObjts = SessionAttendance.objects.filter(session=sessionObj, student=studentObj)
        if sessObjts and len(sessObjts) > 0:
            sessAttendance = sessObjts[0]


        if sessAttendance and (sessAttendance.is_present is None or sessAttendance.is_present != "yes"):
            sessAttendance.is_present = "yes"
            sessAttendance.save()
        else:
            if sessAttendance is None:
                sessAttendance = SessionAttendance.objects.create(
                    student = studentObj,
                    session = sessionObj,
                    is_present = "yes"
                )
                sessAttendance.save()

        dataObj = {
            "message":"Attendance updated successfully"
        }

        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("update_liveclass_attendance",e)
        logService.logException("update_liveclass_attendance", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def update_attendance(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        sessionId = requestBodyParams.get("sessionId")
        contentDetailsId = requestBodyParams.get("contentDetailsId")
        subtopicId = requestBodyParams.get("subtopicId")
        classType = requestBodyParams.get("classType")

        if not studentId or not userId or not userType or not sessionId:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(userId) or not 
            genUtility.isint(studentId) or not
            genUtility.isint(sessionId)
            ):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        #Get Student obj
        try:
            studentObj = Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")

        if classType and classType == "2":
            return update_liveclass_attendance(request, sessionId, studentObj)


        if not contentDetailsId or not subtopicId:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(contentDetailsId) or not genUtility.isint(subtopicId) ):
            return sendErrorResponse(request, "kInvalidRequest")

        #Get session obj
        try:
            sessionObj = Time_Table_Session.objects.get(id=sessionId)
        except:
            return sendErrorResponse(request, "kInvalidSession")
         #Get Student obj
        try:
            contentDeatailsObj = ContentDetail.objects.get(id=contentDetailsId,subtopic_id=subtopicId)
        except:
            return sendErrorResponse(request, "kInvalidContent")

        dataObj = {
            "message":"Attendance updated successfully"
        }
        subtopic_ids = getsubtopicsId(sessionObj)
        subtopic_ids = [int(i) for i in subtopic_ids]
        if checkClientSubtopicInSession(subtopic_ids,subtopicId) is False:
            return sendErrorResponse(request, "kInvalidSubtopic")

        checkAndCreateStudentContentView(subtopicId,studentObj.id,contentDeatailsObj,sessionObj)

        sessionObj.has_attended = True
        sessionObj.save()
        return genUtility.getSuccessApiResponse(request, dataObj)

        #ignore the subtopic check as per the feedback received
        if len(subtopic_ids) == 1:
            sessionObj.has_attended = True
            sessionObj.save()
            return genUtility.getSuccessApiResponse(request, dataObj)

        if checkSessionAndConTentView(subtopic_ids,studentId,contentDetailsId):
            sessionObj.has_attended = True
            sessionObj.save()

        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        logService.logException("attendance", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def upload_student_document(request):
    try:
        if request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        intFormat = request.GET.get('format')  # png,jpg,pdf,doc,docx,jpeg
        intDocType = request.GET.get('doc_type')  # school_logo,school_banner,student_doubt etc

        if not userId or not userType or not intFormat or not intDocType :
            return sendErrorResponse(request, "kMissingReqFields")


        #Get Student obj
        studentObj = None
        guardianObj = None
        try:
            guardianObj = Guardian.objects.get(id=userId)
        except:
            return sendErrorResponse(request, "kUserDoesNotExist")

        if studentId:
            if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
                return sendErrorResponse(request, "kInvalidStudentGuardRel")
            try:
                studentObj = Student.objects.get(id=studentId)
            except:
                return sendErrorResponse(request, "kStudentNotFound")


        cloudFolderName = settings.STUDENT_DOUBT_DOCUMENT_STORAGE_FOLDER
        if intDocType == 6:
            cloudFolderName = settings.STUDENT_PROFILE_PICTURE_FOLDER

        userIdPref = str(guardianObj.id)
        if studentObj:
            userIdPref = userIdPref + str(studentObj.id)
        else:
            userIdPref = userIdPref + 'stud_profile_pic'

        return docUploadService.upload_user_document_s3(request,"guardian",guardianObj,cloudFolderName,userIdPref,None)

    except Exception as e:
        print("upload_student_document",e)
        traceback.print_exc()
        logService.logException("upload_student_document", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")


def sendRespondDoubtNotifications(student,doubtObj,doubtRespObj,dsm,dsp,courseName,schoolName,createdDateStr):
    try:

        ### Sending Registration Mail to the User by Copying to Organization
        args = {'studentName': student.name, 'courseName': courseName,
                'digitalSchoolName': schoolName,'createdDateTime':createdDateStr,"doubtText":doubtObj.text,"doubtAttachmentUrl":doubtObj.resource_url,"doubtResponseText":doubtRespObj.text,"doubtResponseAttachmentUrl":doubtRespObj.resource_url}
        mail = ''
        body = ''
        prefixString = ""
        if genUtility.isNonProdEnvironment():
            prefixString = "[Test Environment] "

        subject = prefixString +'Doubt in ' + schoolName + " under "+courseName + " resolved."
        from_email = settings.DEFAULT_FROM_EMAIL
        toEmails = []

        if dsm:
            toEmails.append(dsm.email)

        if dsp:
            toEmails.append(dsp.email)

        toEmails.append("vg-team@evidyaloka.org")

        body = get_template('respondToDoubtNotificationEmail.html').render(Context(args))
        mail = EmailMessage(subject, body, to=toEmails, from_email=from_email)

        mail.content_subtype = 'html'
        try:
            if genUtility.canSendEmail() is True:
                mail.send()
            else:
                print("EMAIL WILL NOT BE SENT")
                pass
            return True
        except Exception as e:
            print("EMAIL Exception ", e.message)
            logService.logException("Registration email", e.message)
            pass
        return True
    except Exception as e:
        print("sendRespondDoubtNotifications", e)
        logService.logInfo("sendRespondDoubtNotifications", e.message)
        traceback.print_exc()
        return False

def sendDoubtAskedNotifications(student,guardian,doubt,dsm,teacher,courseName,schoolName,createdDateStr):
    try:
        if teacher:
            teacherName = teacher.first_name
        else:
            teacherName = dsm.first_name

        ### Sending Registration Mail to the User by Copying to Organization
        args = {'senderName': teacherName, 'studentName': student.name, 'courseName': courseName,
                'digitalSchoolName': schoolName,'createdDateTime':createdDateStr}
        mail = ''
        body = ''
        prefixString = ""
        if genUtility.isNonProdEnvironment():
            prefixString = "[Test Environment] "

        subject = prefixString +'Doubt raised in ' + schoolName + " under "+courseName
        from_email = settings.DEFAULT_FROM_EMAIL
        toEmails = []
        if teacher:
            toEmails.append(teacher.email)

        if dsm:
            toEmails.append(dsm.email)

        toEmails.append("vg-team@evidyaloka.org")

        body = get_template('studentDoubtNotificationEmail.html').render(Context(args))
        mail = EmailMessage(subject, body, to=toEmails, from_email=from_email)

        mail.content_subtype = 'html'
        try:
            if genUtility.canSendEmail() is True:
                mail.send()
            else:
                print("EMAIL WILL NOT BE SENT")
                pass
            return True
        except Exception as e:
            print("EMAIL Exception ", e.message)
            logService.logException("Registration email", e.message)
            pass
        return True
    except Exception as e:
        print("sendDoubtAskedNotifications", e)
        logService.logInfo("sendDoubtAskedNotifications", e.message)
        traceback.print_exc()
        return False

@csrf_exempt
def student_doubt_api(request):
    if genUtility.isGuardianUserAuthenticated(request) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == "POST":
        return ask_doubt_api(request)
    elif (request.method == "PUT" or request.method == "PATCH"):
        return edit_doubt_api(request)
    elif (request.method == "GET"):
        return get_doubt_api(request)
    else:
        return genUtility.getForbiddenRequestErrorApiResponse(request)

@csrf_exempt
def ask_doubt_api(request):
    try:

        requestBodyParams = simplejson.loads(request.body)

        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        offeringId = requestBodyParams.get('offeringId')
        topicId = requestBodyParams.get('topicId')
        subTopicId = requestBodyParams.get('subTopicId')
        sessionId = requestBodyParams.get('sessionId')
        doubtPicId = requestBodyParams.get('doubtPicId')
        createdDateStr = requestBodyParams.get('createdDate')

        if studentId and  userId and offeringId and topicId and subTopicId and sessionId:
            pass
        else:
            return sendErrorResponse(request, "kMissingReqFields")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")


        studentObj,sessionObj = None,None
        try:
            studentObj = Student.objects.get(id=studentId)
            sessionObj = Time_Table_Session.objects.get(id=sessionId,topic__id=topicId,offering__id=offeringId)
        except:
            return sendErrorResponse(request, "kSessionNotFound")

        # Check if Subtopic contains this id
        if sessionObj.subtopic_ids:
            allIds =  sessionObj.subtopic_ids.split(",")
            isStFound = False
            for stId in allIds:
                if long(stId) == subTopicId:
                    isStFound = True

            if isStFound is False:
                return sendErrorResponse(request, "kInvalidSubtopic")


        #verify Document
        dtDoc = getUserDocument(doubtPicId)
        if dtDoc is None or dtDoc.url is None:
            return sendErrorResponse(request, "kFileDoesnotExist")

        createdDate = genUtility.getCurrentTime()
        try:
            if createdDateStr:
                createdDateNew = genUtility.getDateTimeFromString(createdDateStr)
                if createdDateNew:
                    createdDate = createdDateNew
        except Exception as e:
            logService.logException("ask_doubt_api Time issue", e.message)

        teacherObj = getTeacherForOffering(studentObj,offeringId)

        dtObject = Doubt_Thread.objects.create(
            student = studentObj,
            session = sessionObj,
            offering_id = offeringId,
            topic_id = topicId,
            subtopic_id = subTopicId,
            parent_thread = None,
            resource_url = dtDoc.url,
            resource_doc = dtDoc,
            content_type_id = 2,
            created_by_id = settings.SYSTEM_USER_ID_AUTH,
            updated_by_id = settings.SYSTEM_USER_ID_AUTH,
            #created_on = createdDate,
            assigned_to=teacherObj
        )

        dtObject.save()

        genUtility.updateDocumentBelongsTo(dtDoc, dtObject.id)

        courseName = ""
        offeringObj = sessionObj.offering
        if offeringObj:
            courseObj = offeringObj.course
            if courseObj:
                courseName = courseObj.subject

        centerObj = offeringObj.center
        schoolName = ""
        dsmUser = None
        if centerObj:
            schoolName = centerObj.name
            dsmUser = centerObj.delivery_coordinator

        sendDoubtAskedNotifications(studentObj, request.guardian, dtObject, dsmUser, teacherObj, courseName, schoolName, createdDateStr)
        #created doubt record
        dataObj = {
            "id" : dtObject.id,
            "message": "Doubt  created successfully"
        }

        return genUtility.getSuccessApiResponse(request, dataObj)


    except Exception as e:
        print("ask_doubt_api",e)
        logService.logException("ask_doubt_api", e.message)
        traceback.print_exc()
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def edit_doubt_api(request):
    try:

        requestBodyParams = simplejson.loads(request.body)

        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        doubtPicId = requestBodyParams.get('doubtPicId')
        doubtId = requestBodyParams.get('doubtId')

        if studentId and  userId and doubtId and doubtPicId:
            pass
        else:
            return sendErrorResponse(request, "kMissingReqFields")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        doubtObj = None
        try:
            doubtObj = Doubt_Thread.objects.get(id=doubtId,student__id=studentId,status='1')
        except:
            return sendErrorResponse(request, "kInvalidDoubt")


        #verify Document
        dtDoc = getUserDocument(doubtPicId)
        if dtDoc is None or dtDoc.url is None:
            return sendErrorResponse(request, "kFileDoesnotExist")

        if dtDoc.url != doubtObj.resource_url:
            doubtObj.resource_url = dtDoc.url
            doubtObj.resource_doc = dtDoc
            doubtObj.save()
            genUtility.updateDocumentBelongsTo(dtDoc, doubtObj.id)


        #created doubt record
        dataObj = {
            "id" : doubtObj.id,
            "message": "Doubt  updated successfully"
        }

        return genUtility.getSuccessApiResponse(request, dataObj)


    except Exception as e:
        print("edit_doubt_api",e)
        logService.logException("edit_doubt_api", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def get_doubt_api(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        page = request.GET.get("page")
        count = request.GET.get("count")
        offeringId = request.GET.get("offeringId")
        subtopicId = request.GET.get("subtopicId")
        schoolId = request.GET.get("schoolId")

        doubtId = request.GET.get("doubtId")
        if doubtId and doubtId != "":
            return get_doubt_detail(request)

        if not studentId or not userId or not userType or not schoolId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(studentId):
            return sendErrorResponse(request, "kInvalidRequest")

        if offeringId and genUtility.checkIfParamIfInteger(offeringId) is False:
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")


        centerObj = getCenterObjectsForId(schoolId)
        if centerObj is None:
            return sendErrorResponse(request, "kCenterDoesNotExist")

        if page and genUtility.checkIfParamIfInteger(page) and count and genUtility.checkIfParamIfInteger(count):
            page = int(page)
            if page < 0:
                page = 0
            count = int(count)
            if count > 20:
                count = 20
        else:
            page, count = 0, 20

        currentDateString = genUtility.getCurrentDateTimeInStr()
        offeringDictionary = getOfferingsOptedByStudentInCurrentAcademicYear(studentId,currentDateString,str(centerObj.id),offeringId)


        if offeringDictionary is None or len(offeringDictionary) <= 0:
            return genUtility.getSuccessApiResponse(request, {"doubts":[]})

        alloferingIds = offeringDictionary.keys()
        offeringIdInStr = genUtility.getStringFromIdArray(alloferingIds)

        stString = ""
        if subtopicId and genUtility.checkIfParamIfInteger(subtopicId):
            stString = " AND ws.id = "+ str(subtopicId)


        # Prepare query with all the filters
        whereClsStr = "record_type = '1' AND dt.offering_id IN  (" + offeringIdInStr + ") AND dt.student_id = " + str(studentId)+ stString
        fieldsArray = ["id", "recordType", "status", "offeringId", "url", "resourceType", "createdDate", "topicId",
                       "topicName", "subTopicId", "subTopicName"]
        fieldStr = "dt.id, dt.record_type,dt.status,dt.offering_id,dt.resource_url,dt.resource_type,dt.created_on,wt.id,wt.title,ws.id,ws.name"
        selectQUery = '''select ''' + fieldStr + ''' from student_doubt_thread as dt 
                LEFT JOIN web_topic as wt on (wt.id = dt.topic_id) 
                LEFT JOIN web_subtopics as ws on (ws.id = dt.subtopic_id)
                where ''' + whereClsStr + " ORDER BY dt.created_on DESC" + " LIMIT " + str(
            count) + " OFFSET " + str(page)

        # parse results and update page count
        cursor = connection.cursor()
        cursor.execute(selectQUery)
        dataList = cursor.fetchall()
        respList = []
        fieldCount = len(fieldsArray)
        for eachRecord in dataList:
            eachObject = {}
            for i in range(fieldCount):
                fieldName = fieldsArray[i]
                if fieldName == "offeringId":
                    ofId = eachRecord[i]
                    if ofId:
                        offDict = offeringDictionary.get(ofId)
                        eachObject["subjectName"] = offDict.get("name")
                    eachObject[fieldName] = ofId

                elif fieldName == "createdDate":
                    calDateObj = eachRecord[i]
                    calDateObj = genUtility.getDateTimeinIST(calDateObj)
                    dateStr = genUtility.getDbDateStringFromDate(calDateObj)
                    eachObject[fieldName] = dateStr
                else:
                    eachObject[fieldName] = eachRecord[i]
            eachObject["contentType"] = "image-standard"
            respList.append(eachObject)


        dataObj = {
            "doubts": respList
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("get_doubt_api", e)
        logService.logException("get_doubt_api", e.message)
        #traceback.print_exc()
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def get_subject_progress(request):
    try:
        if request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        schoolId = request.GET.get("schoolId")

        if not studentId or not userId or not userType or not schoolId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(studentId):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")


        centerObj = getCenterObjectsForId(schoolId)
        if centerObj is None:
            return sendErrorResponse(request, "kCenterDoesNotExist")


        currentDateString = genUtility.getCurrentDateTimeInStr()
        offeringDictionary = getOfferingsOptedByStudentInCurrentAcademicYear(studentId,currentDateString,str(centerObj.id),None)

        allCourseIds = []
        courseIdToOfferingMap = {}
        for eachKey in offeringDictionary:
            offDict = offeringDictionary.get(eachKey)
            courseId = offDict.get("courseId")
            subName = offDict.get("name")
            if courseId:
                allCourseIds.append(courseId)
                courseFinalData = {"offeringId":eachKey,"courseId":courseId,"totalTopicsViewed":0,"totalTopics":0,"subjectName":subName}
                languageDict = offeringDictionary.get('language')
                if languageDict:
                    courseFinalData["language"] = languageDict
                courseIdToOfferingMap[courseId] = courseFinalData



        if len(allCourseIds) <= 0:
            return genUtility.getSuccessApiResponse(request, {"subjects":[]})

        alloferingIds = offeringDictionary.keys()
        offeringIdInStr = genUtility.getStringFromIdArray(alloferingIds)
        courseIdInStr = genUtility.getStringFromIdArray(allCourseIds)



        # Prepare query with all the filters
        whereClsStr = "wt.status != 'Inactive' AND wst.status != 'Inactive' AND wc.id IN  (" + courseIdInStr + ")"
        fieldsArray = ["courseId", "topicId", "topicCount", "subtopicCount","ctViewCount"]
        fieldStr = "wc.id, wt.id, COUNT(DISTINCT wst.id), COUNT( DISTINCT vs.subtopic_id)"
        selectQUery = '''select ''' + fieldStr + ''' from web_course as wc  
        LEFT JOIN web_topic as wt on (wc.id = wt.course_id_id ) 
        LEFT JOIN web_subtopics as wst on (wst.topic_id = wt.id ) 
        LEFT JOIN student_content_view_status as vs on (vs.subtopic_id = wst.id AND vs.student_id = '''+str(studentId)+''' AND vs.offering_id IN ('''+ offeringIdInStr +'''))   
        WHERE ''' + whereClsStr + " GROUP BY wt.id"

        # parse results and update page count
        cursor = connection.cursor()
        cursor.execute(selectQUery)
        dataList = cursor.fetchall()

        for eachRecord in dataList:
            courseId = eachRecord[0]
            if courseId:
                courseObj = courseIdToOfferingMap.get(courseId)
                tpTotal = courseObj["totalTopics"]
                tpViewed = courseObj["totalTopicsViewed"]

                courseObj["totalTopics"] = tpTotal + 1
                topicId = eachRecord[1]
                subtopicCount = eachRecord[2]
                subtopicCountViewed = eachRecord[3]
                if subtopicCountViewed >= subtopicCount:
                    courseObj["totalTopicsViewed"] = tpViewed + 1


        allObjects = courseIdToOfferingMap.values()
        dataObj = {
            "subjects": allObjects
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("get_subject_progress", e)
        logService.logException("get_subject_progress", e.message)
        traceback.print_exc()
        return sendErrorResponse(request, "kInvalidRequest")

def getTopicAndSubtopicForCourse(offeringId,courseId,studentId):
    try:
        offeringIdInStr = str(offeringId)
        courseIdInStr = str(courseId)

        # Prepare query with all the filters
        whereClsStr = "wt.status != 'Inactive' AND wst.status != 'Inactive' AND wst.name IS NOT NULL AND wc.id = " + courseIdInStr
        leftJoinStr = ""
        if studentId:
            fieldStr = "wt.id, wt.title, wst.id, wst.name, wst.type, COUNT(vs.id)"
            leftJoinStr = ''' LEFT JOIN student_content_view_status as vs on (vs.subtopic_id = wst.id AND vs.student_id = ''' + str(
            studentId) + ''' AND vs.offering_id = ''' + offeringIdInStr + ''' ) '''
        else:
            fieldStr = "wt.id, wt.title, wst.id, wst.name"

        selectQUery = '''select ''' + fieldStr + ''' from web_course as wc  
               LEFT JOIN web_topic as wt on (wc.id = wt.course_id_id ) 
               LEFT JOIN web_subtopics as wst on (wst.topic_id = wt.id ) ''' + leftJoinStr  + '''  
               WHERE ''' + whereClsStr + " GROUP BY wst.id ORDER BY wt.priority,wst.id"


        # parse results and update page count
        cursor = connection.cursor()
        cursor.execute(selectQUery)
        dataList = cursor.fetchall()
        topicMap = {}
        topicIdArray = []
        for eachRecord in dataList:
            topicId = eachRecord[0]
            if topicId:
                topicObj = topicMap.get(topicId)
                if topicObj is None:
                    tTitle = eachRecord[1]
                    if tTitle:
                        topicObj = {"id": topicId, "name": tTitle}
                    else:
                        continue
                    topicMap[topicId] = topicObj
                    topicIdArray.append(topicId)

                stId = eachRecord[2]
                stTitle = eachRecord[3]
                stType = eachRecord[4]
                viewCount = 0
                if studentId:
                    viewCount = eachRecord[5]

                if stId and stTitle:
                    subtopicsList = topicObj.get("subtopics")
                    if subtopicsList is None:
                        subtopicsList = []
                        topicObj["subtopics"] = subtopicsList
                    stObj = {"id": stId, "name": stTitle, "type": stType}
                    hasViewed = 0
                    if viewCount and viewCount > 0:
                        hasViewed = 1
                    stObj["hasViewed"] = hasViewed
                    subtopicsList.append(stObj)

        allObjects = []
        for j in range(len(topicIdArray)):
            tpId = topicIdArray[j]
            topicObj = topicMap.get(tpId)
            if topicObj:
                allObjects.append(topicObj)
        return allObjects

    except Exception as e:
        print("getTopicAndSubtopicForCourse", e)
        logService.logException("getTopicAndSubtopicForCourse", e.message)
        return []
        #traceback.print_exc()

@csrf_exempt
def get_subject_detail(request):
    try:
        if request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        offeringId = request.GET.get("offeringId")
        courseId = request.GET.get("courseId")

        if  not userId or not userType or not offeringId or not courseId:
            return sendErrorResponse(request, "kMissingReqFields")

        if  studentId and not genUtility.isint(studentId):
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId)  or not genUtility.isint(offeringId) or not genUtility.isint(courseId):
            return sendErrorResponse(request, "kInvalidRequest")
        if studentId:
            if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
                return sendErrorResponse(request, "kInvalidStudentGuardRel")
        else:
            studentId = None

        allObjects = getTopicAndSubtopicForCourse(offeringId,courseId,studentId)
        dataObj = {
            "topics": allObjects
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("get_subject_detail", e)
        logService.logException("get_subject_detail", e.message)
        traceback.print_exc()
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def update_content_view_status(request):
    try:
        if request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        sessionId = requestBodyParams.get("sessionId")
        contentDetailsId = requestBodyParams.get("contentDetailsId")
        subtopicId = requestBodyParams.get("subtopicId")
        progress = requestBodyParams.get("progress")

        if not studentId or not userId or not userType or not sessionId or not contentDetailsId or not subtopicId or not progress:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(userId) or not
            genUtility.isint(studentId) or not
            genUtility.isint(sessionId) or not
            genUtility.isint(contentDetailsId) or not
            genUtility.isint(subtopicId)
            ):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        #Get session obj
        try:
            sessionObj = Time_Table_Session.objects.get(id=sessionId)
        except:
            return sendErrorResponse(request, "kInvalidSession")

         #Get Content detail obj
        try:
            contentDeatailsObj = ContentDetail.objects.get(id=contentDetailsId,subtopic_id=subtopicId)
        except:
            return sendErrorResponse(request, "kInvalidContent")


        subtopic_ids = getsubtopicsId(sessionObj)
        subtopic_ids = [int(i) for i in subtopic_ids]
        if checkClientSubtopicInSession(subtopic_ids,subtopicId) is False:
            return sendErrorResponse(request, "kInvalidSession")


        ctView,isNewRecord = checkAndCreateStudentContentView(subtopicId,studentId,contentDeatailsObj,sessionObj)
        if ctView:
            ctView.progress = progress
            if isNewRecord is False:
                ctView.number_of_times_viewed = ctView.number_of_times_viewed + 1
            ctView.save()

        dataObj = {
            "message": "Progress updated successfully"
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        logService.logException("update_content_progress", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def get_doubt_detail(request):
    try:
        if request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        doubtId = request.GET.get("doubtId")

        if not studentId or not userId or not userType or not doubtId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(studentId) or not genUtility.isint(doubtId):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        try:
            doubtObj = Doubt_Thread.objects.get(id=doubtId)
        except:
            return sendErrorResponse(request, "kInvalidDoubt")
        respList = []
        calDateObj = genUtility.getDateTimeinIST(doubtObj.created_on)
        createdDateTimeStr = genUtility.getDbDateStringFromDate(calDateObj)
        doubtDict = {
            "id":doubtId,
            "url":doubtObj.resource_url,
            "recordType":doubtObj.record_type,
            "subTopicId":doubtObj.subtopic_id,
            "offeringId": doubtObj.offering_id,
            "status":doubtObj.status,
            "contentType":"image-standard",
            "resourceType":doubtObj.resource_type,
            "createdDate":createdDateTimeStr
        }
        respList.append(doubtDict)

        dtList = []
        if doubtObj.status == '2':
            dtList = Doubt_Thread.objects.filter(parent_thread_id=doubtId).select_related("assigned_to")


        if dtList and len(dtList) > 0:
            dtRespObj = dtList[0]
            calDateObj = genUtility.getDateTimeinIST(dtRespObj.created_on)
            createdDateTimeStr = genUtility.getDbDateStringFromDate(calDateObj)
            doubtRespDict = {
                "id": dtRespObj.id,
                "url": dtRespObj.resource_url,
                "recordType": dtRespObj.record_type,
                "subTopicId": dtRespObj.subtopic_id,
                "offeringId": dtRespObj.offering_id,
                "status": dtRespObj.status,
                "contentType": "image-standard",
                "resourceType": dtRespObj.resource_type,
                "text":dtRespObj.text,
                "createdDate": createdDateTimeStr
            }
            teacher = dtRespObj.assigned_to
            if teacher and teacher.first_name:
                teacherName = teacher.first_name
                if teacher.last_name:
                    teacherName = teacherName + " " + teacher.last_name

                doubtRespDict["teacherName"] = teacherName


            respList.append(doubtRespDict)

        dataObj = {
            "doubts": respList
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("get_doubt_detail",e)
        logService.logException("get_doubt_detail", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def student_logout(request):
    try:
        if request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        deviceInfo = requestBodyParams.get("deviceInfo")
        guardianObj = request.guardian

        if  not userId or not userType:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId):
            return sendErrorResponse(request, "kInvalidRequest")


        sessionInstance = request.currentSession
        if sessionInstance:
            sessionInstance.status = False
            sessionInstance.expiry_time = genUtility.getCurrentTime()
            sessionInstance.save()
        else:
            return genUtility.getStandardErrorResponse(request, "kInvalidSession")

        deviceObj = getDeviceId(guardianObj, deviceInfo)
        if deviceObj:
            notificationModule.deactivatePushTokeForGuardin(guardianObj,deviceObj.id)

        dataObj = {
            "message": "Logged out successfully"
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("student_logout", e)
        logService.logException("student_logout", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def student_session_rate(request):
    try:
        if request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        subtopicId = requestBodyParams.get("subtopicId")
        sessionId = requestBodyParams.get("sessionId")
        hasLiked = requestBodyParams.get("hasLiked")


        if not studentId or not userId or not subtopicId or not sessionId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(studentId) \
                or not genUtility.isint(subtopicId) or not genUtility.isint(hasLiked) or not genUtility.isint(sessionId):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        try:
            studentObj = Student.objects.get(id=studentId)
        except:
            return sendErrorResponse(request, "kStudentNotFound")
        ratingVal = 0
        if hasLiked == 1:
            ratingVal = 5

        # Check if rating already exist in content_rating table for student and subtopic
        ratingObj = None
        ratingObjList = Content_Rating.objects.filter(student_id=studentId, subtopic_id=subtopicId)
        if ratingObjList and len(ratingObjList) > 0:
            ratingObj = ratingObjList[0]
            ratingObj.rating = ratingVal
            ratingObj.session_id = sessionId
        else:
            ratingObj = Content_Rating.objects.create(
                student = studentObj,
                subtopic_id = subtopicId,
                rating = ratingVal,
                created_by_id=settings.SYSTEM_USER_ID_AUTH,
                updated_by_id=settings.SYSTEM_USER_ID_AUTH,
                session_id = sessionId
            )

        ratingObj.save()
        dataObj = {
            "message": "Rating has been updated successfully"
        }
        return genUtility.getSuccessApiResponse(request, dataObj)

    except Exception as e:
        print("student_session_rate", e)
        logService.logException("student_session_rate", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")


def student_missed_session(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "GET" :
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        schoolId = request.GET.get("schoolId")

        if not studentId or not userId or not userType or not schoolId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(studentId) or not genUtility.isint(schoolId):
            return sendErrorResponse(request, "kInvalidRequest")


        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        timeTable = getTimetableForStudentId(studentId)
        if timeTable is None:
            return sendErrorResponse(request, "kInvalidRequest")

        centerObj = getCenterObjectsForId(schoolId)
        offeringIdList = getOfferingsForSchoolCenterForStudent(centerObj,studentId)
        offeringIdStr = ""
        if offeringIdList and len(offeringIdList) > 0:
            offeringIdStr = " AND " + 'sts.offering_id IN ('+  genUtility.getStringFromIdArray(offeringIdList) + ")"

        todayDate = genUtility.getCurrentTime()
        endDateStr = genUtility.getStringFromDate(todayDate)
        #Prepare query with all the filters
        whereClsStr = "sts.timetable_id = " + str(timeTable.id) + " AND (sts.has_attended != 1 OR sts.has_attended is NULL) AND calDate < '"+endDateStr+"'" + offeringIdStr
        fieldStr = "COUNT(sts.id),MIN(calDate)"
        selectQUery = '''select ''' +fieldStr+ ''' from student_time_table_session as sts 
            where ''' + whereClsStr


        cursor = connection.cursor()
        cursor.execute(selectQUery)
        dataList = cursor.fetchall()
        sessionCount = 0
        firstMissedDateStr = ''

        if dataList and len(dataList) > 0:
            eachRecord = dataList[0]
            sessionCount = eachRecord[0]
            firstMissedDate = eachRecord[1]
            if firstMissedDate:
                firstMissedDateStr = genUtility.getStringFromDate(firstMissedDate)


        dataObj = {
            "count":sessionCount,
            "firstMissedDate":firstMissedDateStr
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("student_missed_session", e)
        traceback.print_exc()
        logService.logException("student_missed_session", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

def student_get_pincodes(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "GET" :
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        searchText = request.GET.get("searchText")
        page = request.GET.get("page")
        count = request.GET.get("count")

        if not userId or not page or not count or not searchText:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(page) or not genUtility.isint(count):
            return sendErrorResponse(request, "kInvalidRequest")
        else:
            page = int(page)
            count = int(count)

        if searchText and (len(searchText) < 4 or genUtility.checkIfKeyIsSafeForQuery(searchText) is False):
            return sendErrorResponse(request, "kInvalidSearchKey")

        if count > 50:
            count = 50

        if page < 0:
            page = 0

        page = page * count

        pincodes = genUtility.getPincodes(None, searchText, page, count, connection)
        dataObj = {
            "pincodes": pincodes
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("student_get_pincodes", e)
        traceback.print_exc()
        logService.logException("student_get_pincode", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def student_get_languages(request):
    if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "GET":
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:
        languages = genUtility.getLanguages()
        languageRespList = []
        for i in range(len(languages)):
            lngObj = languages[i]
            languageRespList.append({'id': lngObj.id, 'name': lngObj.name, 'code': lngObj.code})

        dataObj = {
            "languages": languageRespList
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        logService.logExceptionWithExceptionobject("student_language_api ", e)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def student_get_courseproviders(request):
    if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "GET":
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:
        allCourseProviders = CourseProvider.objects.filter(status=True).order_by('name')
        courseProviderList = []
        for singleCourseProvider in allCourseProviders:
            singleCourseProviderDict = {}
            singleCourseProviderDict["id"] = singleCourseProvider.id
            singleCourseProviderDict["name"] = singleCourseProvider.name
            singleCourseProviderDict["type"] = singleCourseProvider.type
            singleCourseProviderDict["code"] = singleCourseProvider.code
            courseProviderList.append(singleCourseProviderDict)

        dataObj = {
            "courseProviders": courseProviderList
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        logService.logExceptionWithExceptionobject("student_get_courseproviders ", e)
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def school_explore_detail_api(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "GET" :
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        courseProviderId = request.GET.get("courseProviderId")
        grade = request.GET.get("grade")

        #Create a common function to get default school for board
        if not userId or not courseProviderId or not grade:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(courseProviderId) or not genUtility.isint(grade):
            return sendErrorResponse(request, "kInvalidRequest")

        schoolDetail = getDefaultSchoolDetailForboard(courseProviderId,grade)
        if schoolDetail is None:
            return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")

        dataObj = {
            "schools": [schoolDetail]
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("school_explore_detail_api", e)
        traceback.print_exc()
        logService.logException("school_explore_detail_api", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def guardian_enroll_student(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        # Check if user id is DSM of the school id and school status is active
        requestBodyParams = simplejson.loads(request.body)
        guardianId = requestBodyParams.get("userId")
        schoolId = requestBodyParams.get("digitalSchoolId")
        guardianObj = request.guardian
        if schoolId:
            try:
                dsSchool = DigitalSchool.objects.get(id=schoolId)
                if dsSchool.status == "Active":
                    return enrolStudentInDigitalSchool(request, requestBodyParams, dsSchool, None, None, "guardian", guardianObj)
                else:
                    return sendErrorResponse(request, "kInvalidSchoolStatus")
            except Exception as e:
                return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")
        else:
            return sendErrorResponse(request, "kMissingReqFields")
    except Exception as e:
        print("guardian_enroll_student ",e)
        traceback.print_exc()
        logService.logException("guardian_enroll_student", e.message)
        return sendErrorResponse(request, "kInvalidRequest")



@csrf_exempt
def student_guardian_update_details(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        if request.method != 'POST':
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        latitude = requestBodyParams.get("lat")
        longitude = requestBodyParams.get("lng")
        pincode = requestBodyParams.get("pincode")

        if  not userId or not userType:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(userId) or not genUtility.isint(pincode) ):
            return sendErrorResponse(request, "kInvalidRequest")

        pincodes = Pincode.objects.filter(pincode=pincode)
        if pincodes and len(pincodes) > 0:
            pass

        guardianobj = request.guardian

        if longitude and latitude and genUtility.isLatLngValid(latitude) and genUtility.isLatLngValid(longitude):
            guardianobj.latitude = str(latitude)
            guardianobj.longitude = str(longitude)
        elif longitude and latitude:
            return sendErrorResponse(request, "kInvalidLocation")

        guardianobj.pin_code = str(pincode)
        guardianobj.save()
        responseData = {
            "message": "Guardian details updated successfully"
        }
        return genUtility.getSuccessApiResponse(request, responseData)
    except Exception as e:
        print("student_guardian_update_details ",e)
        traceback.print_exc()
        logService.logException("student_guardian_update_details", e.message)
        return sendErrorResponse(request, "kInvalidRequest")

def getOfferingForCourseProvider(courseProvider):
    offeringObjs = Offering.objects.filter(end_date__gte=genUtility.getCurrentTime(),
                                           status__in=['pending', 'running'],
                                           course__board_name=courseProvider.code,course__status='active').select_related('course').order_by('course__board_name')
    return offeringObjs

@csrf_exempt
def student_get_grade(request):
    if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "GET":
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:

        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        courseProviderId = request.GET.get("courseProviderId")

        if not userId or not courseProviderId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(courseProviderId):
            return sendErrorResponse(request, "kInvalidRequest")

        try:
            courseProvider = CourseProvider.objects.get(id=courseProviderId)
        except:
            return sendErrorResponse(request, "kCourseProviderDoesNotExist")

        offeringObjs = getOfferingForCourseProvider(courseProvider)
        gradeArray = []
        for i in range(len(offeringObjs)):
            offObj = offeringObjs[i]
            gradeVal = offObj.course.grade
            gradeVal = str(gradeVal)
            if gradeVal not in gradeArray:
                gradeArray.append(gradeVal)

        dataObj = {
            "grades": gradeArray
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("student_get_grade",e)
        logService.logExceptionWithExceptionobject("student_get_grade ", e)
        return sendErrorResponse(request, "kInvalidRequest")



@csrf_exempt
def guardian_update_push_token(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        # Check if user id is DSM of the school id and school status is active
        requestBodyParams = simplejson.loads(request.body)
        userId = requestBodyParams.get("userId")
        pushToken = requestBodyParams.get("pushToken")
        deviceInfo = requestBodyParams.get("deviceInfo")
        guardianObj = request.guardian

        if not userId or not pushToken or not deviceInfo:
            return sendErrorResponse(request, "kMissingReqFields")

        #Check if device exist, if not, create device
        #update push notification for the user and device
        deviceObj = updateOrCreateDeviceObjectForGuardian(guardianObj, deviceInfo)
        if deviceObj is None:
            return sendErrorResponse(request, "kMissingReqFields")

        notificationModule.updatePushTokeForGuardin(guardianObj, pushToken, deviceObj)
        dataObj = {
            "message": "Token updated successfully"
        }
        return genUtility.getSuccessApiResponse(request, dataObj)

    except Exception as e:
        print("guardian_update_push_token ",e)
        traceback.print_exc()
        logService.logExceptionWithExceptionobject("guardian_update_push_token", e)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def test_push_api(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        pushToken1 = requestBodyParams.get("pushToken")
        name = requestBodyParams.get("name")

        title = "eVidyaloka Learning App"
        body = "Hi" +name +", This is push notification from eVidyaLoka Team.Sent at 2PM in release. "
        data_message = {"sessionId": "newSessionId2325"}
        pushToken = pushToken1
        result = pushNotificationService.sendNotificationToSingleDevice(pushToken,title,body,data_message)
        dataObj = {
            "update": "message sent",
            "result":result
        }
        return genUtility.getSuccessApiResponse(request, dataObj)

    except Exception as e:
        print("test_push_api ",e)
        traceback.print_exc()
        logService.logExceptionWithExceptionobject("test_push_api", e)
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def test_redis(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        if request.method == "GET":
            return test_get_redis(request)

        requestBodyParams = simplejson.loads(request.body)
        key = requestBodyParams.get("key")
        value = requestBodyParams.get("value")

        cacheService.setValueStringForKey(key,value)

        dataObj = {
            "message": "cache updated",
        }
        return genUtility.getSuccessApiResponse(request, dataObj)

    except Exception as e:
        print("test_redis ",e)
        traceback.print_exc()
        logService.logExceptionWithExceptionobject("test_redis", e)
        return sendErrorResponse(request, "kInvalidRequest")

def test_get_redis(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False or request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        key = requestBodyParams.get("key")

        value = cacheService.getValueStringForKey(key)
        dataObj = {
            "value": value,
        }
        return genUtility.getSuccessApiResponse(request, dataObj)

    except Exception as e:
        print("test_redis ",e)
        traceback.print_exc()
        logService.logExceptionWithExceptionobject("test_redis", e)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def student_get_session_detail(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        offeringId = request.GET.get("offeringId")
        topicId = request.GET.get("topicId")
        subtopicId = request.GET.get("subtopicId")
        schoolId = request.GET.get("schoolId")

        if  not userId or not userType  or not offeringId or not topicId  or not subtopicId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(topicId) or not genUtility.isint(subtopicId):
            return sendErrorResponse(request, "kInvalidRequest")

        if not genUtility.isGuardian(userId, userType):
            return sendErrorResponse(request, "kUserGuardian")

        subtopicIdStr = str(subtopicId)
        # Get offeringObj obj
        try:
            offeringObj = Offering.objects.get(id=offeringId)
        except:
            return sendErrorResponse(request, "kInvalidOfferings")

        if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        # Validate  Student obj
        try:
            studentObj = Student.objects.get(id=studentId,status='Active')
        except:
            return sendErrorResponse(request, "kStudentNotFound")

        # Get session obj
        timetableObjList = Time_Table.objects.filter(student=studentObj, status='active')
        timetableObj = None
        if timetableObjList and len(timetableObjList) > 0:
            timetableObj = timetableObjList[0]

        if timetableObj is None:
            return sendErrorResponse(request, "kTimetableNotFound")

        # Get session obj
        try:
            sessionObjs = Time_Table_Session.objects.filter(timetable=timetableObj,topic_id=topicId,offering_id=offeringId,subtopic_ids__contains=subtopicId)
        except Exception as e:
            return sendErrorResponse(request, "kInvalidSession")

        finalSession = None
        for eachSession in sessionObjs:
            subtopicIdsStr = eachSession.subtopic_ids
            if subtopicIdsStr:
                subtopics = subtopicIdsStr.split(",")
                if subtopicIdStr in subtopics:
                    finalSession = eachSession
                    break

        if finalSession is None:
            return sendErrorResponse(request, "kInvalidSession")

        dataObj = {
            "topicId":topicId,
            "subtopicId":subtopicId,
            "offeringId":offeringId,
            "sessionId":finalSession.id,
            "timetableId":timetableObj.id

        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("student_get_session_detail",e)
        logService.logException("student_get_session_detail", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")



@csrf_exempt
def update_content_download_status(request):
    try:
        if request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        sessionId = requestBodyParams.get("sessionId")
        contentDetailsId = requestBodyParams.get("contentDetailsId")
        subtopicId = requestBodyParams.get("subtopicId")
        offeringId = requestBodyParams.get("offeringId")
        downloadStatus = requestBodyParams.get("downloadStatus")
        deviceId = requestBodyParams.get("deviceId")

        if not studentId or not userId or not userType or not sessionId or not contentDetailsId or not subtopicId or not downloadStatus or not deviceId:
            return sendErrorResponse(request, "kMissingReqFields")

        if (not genUtility.isint(userId) or not
            genUtility.isint(studentId) or not
            genUtility.isint(sessionId) or not
            genUtility.isint(contentDetailsId) or not
            genUtility.isint(subtopicId)
            ):
            return sendErrorResponse(request, "kInvalidRequest")

        if genUtility.checkIfStudentBelongsToGuardian(request,studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        #Get session obj
        try:
            sessionObj = Time_Table_Session.objects.get(id=sessionId)
        except:
            return sendErrorResponse(request, "kInvalidSession")

        #Get Content detail obj
        try:
            contentDetailsObj = ContentDetail.objects.get(id=contentDetailsId,subtopic_id=subtopicId)
        except:
            return sendErrorResponse(request, "kInvalidContent")

        # Get Device Id
        try:
            deviceInfo = None
            devices = UserDevice.objects.filter(deviceId=deviceId, status=1,belongs_to_id=userId)
            if devices and len(devices) > 0:
                deviceInfo = devices[0]
            else:
                return sendErrorResponse(request, "kDeviceDoesNotExist")


        except Exception as e:
            print("kDeviceDoesNotExist",e)
            return sendErrorResponse(request, "kDeviceDoesNotExist")


        if downloadStatus == 2:
            historyObjects = Content_Download_History.objects.filter(content_detail=contentDetailsObj,student_id=studentId,device=deviceInfo)
            for eachH in historyObjects:
                eachH.file_status = "2"
                eachH.save()

        else:
            cHistoryObj = Content_Download_History.objects.create(
                content_detail=contentDetailsObj,
                student_id=studentId,
                session=sessionObj,
                offering_id=sessionObj.offering_id,
                topic_id=contentDetailsObj.topic_id,
                subtopic_id=contentDetailsObj.subtopic_id,
                device=deviceInfo,
                created_by_id=settings.SYSTEM_USER_ID_AUTH,
                updated_by_id=settings.SYSTEM_USER_ID_AUTH,
            )
            cHistoryObj.save()


        dataObj = {
            "message": "Download status updated successfully"
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        logService.logException("update_content_download_status", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")


def createStudentKyc(student=None, created_by=None, doc_type='1' ,kyc_number=None, status='1'):
    if not student and not created_by:
        return None
    else:
        try:
            kyc = KycDetails.objects.create(student=student, created_by=created_by, updated_by=created_by, doc_type=doc_type, kyc_number=kyc_number, status=status)
            kyc.save()
            return kyc.id
        except Exception as e:
            logService.logException("create_kyc", e.message)
            return None
        

def updateStudentKyc(student_id, updated_by, doc_type=None ,kyc_number=None, status=None):
    if not student_id and not updated_by:
        return None
    else:
        try:
            kyc = get_object_or_none(KycDetails, student=student_id)
            print('------kyc -------',kyc)
            if kyc is not None:
                kyc.updated_by=updated_by
                kyc.doc_type=doc_type
                kyc.kyc_number=kyc_number
                kyc.status=status
                kyc.save()
                return kyc.id
        except Exception as e:
            logService.logException("update_kyc", e.message)
            return None


@transaction.commit_on_success
def promotStudentForPartner(request, requestParams):
    try:
        isUpdateAllStudent = requestParams.get("isUpdateAllStudent")
        currentGrade = requestParams.get("grade")
        studentIds = requestParams.get("studentIds")
        digitalSchoolId = requestParams.get("digitalSchoolId")
        courseProviderId = requestParams.get('courseProviderId')
        studentPromotionType = requestParams.get('studentPromotionType')
        ayfy = genUtility.getAcademicYearByCourseProviderId(courseProviderId)
        promotGrade = int(currentGrade)+1
        user = request.user

        if isUpdateAllStudent and digitalSchoolId and digitalSchoolId is None or courseProviderId is None and ayfy is None:
            return sendErrorResponse(request, "kMissingReqFields")

        if studentPromotionType == 'Active':
            studentStatus = 'Active'
        else:
            if studentPromotionType == 'Alumni':
                studentStatus = 'Alumni'
            else:
                return sendErrorResponse(request, "kInvalidPromotionType")

        if isUpdateAllStudent is True:
            studentsList = Student.objects.filter(
                student_school_enrollment__digital_school_id=digitalSchoolId,
                grade=currentGrade,
                status='Active'
            )
        else:
            studentsList = Student.objects.filter(
                student_school_enrollment__digital_school_id=digitalSchoolId,
                grade=currentGrade,
                status='Active',
                pk__in=studentIds
            )
        for student in studentsList:
            try:
                student.grade = promotGrade
                # Update student class status to 3 ie.Promoted ,Course not opted
                student.class_status = 3
                student.status = studentStatus
                promotionHistory = Promotion_History(
                    student=student,
                    ayfy_id=ayfy.pk,
                    from_grade=currentGrade,
                    to_grade=promotGrade,
                    digital_school_id=digitalSchoolId,
                    promoted_by=user,
                    promoted_on=genUtility.getCurrentTime(),
                    created_by_id=settings.SYSTEM_USER_ID_AUTH,
                    updated_by_id=settings.SYSTEM_USER_ID_AUTH
                )
                sessions = Time_Table_Session.objects.filter(timetable__student__pk=student.pk)
                if sessions:
                    sessions.update(status=False)
                student.save()
                promotionHistory.save()
            except Exception as e:
                logService.logException("Promot StudentByDSM ", e.message)
                return genUtility.getStandardErrorResponse(request, "kStudentPromotionFailed")

        if studentsList:
            dataObj = {
                "promotedCount": len(studentsList),
                "message": "Student promoted  successfully"
            }
            return genUtility.getSuccessApiResponse(request, dataObj)
        else:
            return genUtility.getStandardErrorResponse(request, "kInvalidStudentList")

    except Exception as e:
        logService.logException("Promot StudentByDSM ", e.message)
        return genUtility.getStandardErrorResponse(request, "kStudentPromotionFailed")


def getStudentPromotionListForPartner(request):
    try:
        digitalSchoolId = request.GET.get('digitalSchoolId')
        userType = request.GET.get('userType')
        page = request.GET.get('page')
        count = request.GET.get('count')
        grade = request.GET.get('grade')
        filter = request.GET.get('filter')
        courseProviderId = request.GET.get('courseProviderId')

        if digitalSchoolId is None or userType is None or grade is None or courseProviderId is None:
            return sendErrorResponse(request, "kMissingReqFields")
        else:
            try:
                studRespList = []
                totalCount = 0
                fetcStudentDetails = False
                if page is None:
                    page = 0

                page = int(page)
                if page == 0:
                    countData = filterPromotionStudentByParameters(digitalSchoolId, page, count, grade,
                                                        courseProviderId, True,filter)
                    if countData and len(countData) > 0:
                        totalCount = countData[0].get("count")
                        if totalCount > 0:
                            fetcStudentDetails = True
                else:
                    fetcStudentDetails = True

                if fetcStudentDetails is True:
                        studentList = filterPromotionStudentByParameters(digitalSchoolId, page, count, grade, courseProviderId, False,filter)
                        if studentList:
                            studRespList = studentList

                dataObject = {
                        "students": studRespList,
                        "totalCount":totalCount
                }
                return genUtility.getSuccessApiResponse(request, dataObject)
            except Exception as e:
                logService.logException("getStudentListForPartner ", e.message)
                return sendErrorResponse(request, "kInvalidRequest")
    except Exception as e:
        logService.logException("getStudentPromotionListForPartner ", e.message)
        return sendErrorResponse(request, "kInvalidRequest")



def filterPromotionStudentByParameters(digitalSchoolId,page,count,grade,courseProviderId,isCountNeeded,filter):
    try:
        queryOffset = 0
        limitRecord = 50

        academicYearId = genUtility.getAcademicYearByCourseProviderId(courseProviderId).pk
        if page and count and genUtility.checkIfParamIfInteger(page) and genUtility.checkIfParamIfInteger(count):
            limitRecord = int(count)
            queryOffset = int(page) * limitRecord

        fieldArray = ["id", "name", "profileUrl", "grade"]
        queryParams = [str(digitalSchoolId), grade,str(academicYearId),str(digitalSchoolId)]


        whereConditionString = "sc.id = %s AND st.grade = %s "
        promotionHistory = "(SELECT student_id From student_promotion_history where ayfy_id =%s AND digital_school_id=%s)"
        limitString = " LIMIT %s OFFSET %s;"
        limitParam = [limitRecord,queryOffset]

        selectClauseStr = " DISTINCT st.id,st.name,st.profile_pic_url,st.grade,se.created_on "
        if isCountNeeded:
            selectClauseStr = " COUNT(DISTINCT st.id) "
            fieldArray = ["count"]
            limitString = ""
            limitParam = []

        queryString = '''select '''+selectClauseStr +'''
                        FROM web_digitalschool as sc
                        LEFT JOIN student_student_school_enrollment as se on (se.digital_school_id = sc.id)
                        LEFT JOIN web_student as st on (st.id = se.student_id)
                        WHERE  ''' + whereConditionString
        if filter is not None:
            queryString +=" AND st.name LIKE %s "
            queryParams.insert(2,"%"+filter+"%")

        queryString += ''' AND st.id NOT IN '''+promotionHistory+''' ORDER BY se.created_on DESC '''+ limitString

        queryParams.extend(limitParam)
        cursor = connection.cursor()
        cursor.execute(queryString,queryParams)
        dataList = cursor.fetchall()
        dataDictList = []
        fieldCount = len(fieldArray)
        for eachRecord in dataList:
            eachObject = {}
            for i in range(fieldCount):
                fieldName = fieldArray[i]
                eachObject[fieldName] = eachRecord[i]
            dataDictList.append(eachObject)
        return dataDictList
    except Exception as e:
        logService.logException("getStudentListForPartner ", e.message)


@csrf_exempt
def student_get_question_set(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        offeringId = request.GET.get("offeringId")
        topicId = request.GET.get("topicId")
        subtopicId = request.GET.get("subtopicId")

        if not userId or not userType or not topicId or not subtopicId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(topicId) or not genUtility.isint(subtopicId):
            return sendErrorResponse(request, "kInvalidRequest")

        if not genUtility.isGuardian(userId, userType):
            return sendErrorResponse(request, "kUserGuardian")

        if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        # Validate  Student obj
        try:
            studentObj = Student.objects.get(id=studentId, status='Active')
        except:
            return sendErrorResponse(request, "kStudentNotFound")

        questionSets = Question_Set.objects.filter(topic__id=topicId,subtopic__id= subtopicId)
        questionSetList = []
        for questionSet in questionSets:
            questionSetObj = { "id": questionSet.id, "name": questionSet.name, "type": questionSet.type, "contentDetailsId": questionSet.content_detail_id}
            questionSetList.append(questionSetObj)

        return genUtility.getSuccessApiResponse(request, questionSetList)
    except Exception as e:
        print("student_get_question_set", e)
        logService.logException("student_get_question_set", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def student_get_quiz(request):
    try:
        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        studentId = request.GET.get("studentId")
        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        offeringId = request.GET.get("offeringId")
        topicId = request.GET.get("topicId")
        subtopicId = request.GET.get("subtopicId")
        questionsetId = request.GET.get("questionsetId")

        if not userId or not userType or not topicId or not subtopicId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(topicId) or not genUtility.isint(subtopicId):
            return sendErrorResponse(request, "kInvalidRequest")

        if not genUtility.isGuardian(userId, userType):
            return sendErrorResponse(request, "kUserGuardian")

        if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        # Validate  Student obj
        try:
            studentObj = Student.objects.get(id=studentId, status='Active')
        except:
            return sendErrorResponse(request, "kStudentNotFound")

        questions = []
        fieldArray = ["id","title","text","type","points","sequence","actualSequenceString"]
        queryString = '''SELECT question.id,question.title,question.text,type.code,question.points,question.sequence,question.actual_sequence_string
                    FROM
                        (
                        (select * from questionbank_question where questionbank_question.complexity = 3 and questionbank_question.questionset_id = %(questionset_id)s order by rand() Limit 2) 
                        union all
                        (select * from questionbank_question where questionbank_question.complexity = 2 and questionbank_question.questionset_id = %(questionset_id)s order by rand() Limit 2) 
                        union all
                        (select * from questionbank_question where questionbank_question.complexity = 1 and questionbank_question.questionset_id = %(questionset_id)s order by rand() Limit 3) 
                        )as question LEFT JOIN questionbank_question_type as type on (question.type_id = type.id) order by question.sequence'''
        cursor = connection.cursor()
        cursor.execute(queryString,{"questionset_id": questionsetId})
        dataList = cursor.fetchall()
        fieldCount = len(fieldArray)
        for question in dataList:
            questionObject = {}
            for i in range(fieldCount):
                fieldName = fieldArray[i]
                questionObject[fieldName] = question[i]

            if questionObject["type"] == "orderBy":
                questionObject["actualSequenceString"] = map(int,questionObject["actualSequenceString"].split(','))
            else:
                questionObject.pop("actualSequenceString")
            questionComponents = Question_Component.objects.filter(question__id=questionObject["id"]).order_by("subtype","sequence")
            options = []
            leftColumn = []
            rightColumn = []
            categorys =[]
            categoryItems = []
            for component in questionComponents:
                if questionObject["type"] == "mcq" or questionObject["type"] == "mmcq" or questionObject["type"] == "orderBy":
                    option = {"id": component.id, "text": component.text, "isAnswer": component.is_answer,
                              "imageUrl": component.image_url}
                    options.append(option)
                elif questionObject["type"] == "matchTheFollowing":
                    if component.subtype == '2':
                        leftoption = {"text": component.text, "id": component.id,
                                      "correctAnswerId": component.matching_component_id}
                        leftColumn.append(leftoption)
                    else:
                        rightoption = {"text": component.text, "id": component.id}
                        rightColumn.append(rightoption)
                elif questionObject["type"] == "categorise":
                    if component.subtype == '4':
                        category = {"text": component.text, "id": component.id}
                        categorys.append(category)
                    else:
                        categoryItem = {"text": component.text, "id": component.id,
                                      "categoryId": component.matching_component_id}
                        categoryItems.append(categoryItem)
            if questionObject["type"] == "matchTheFollowing":
                questionObject["leftColumn"] = leftColumn
                questionObject["rightColumn"] = rightColumn
            elif questionObject["type"] == "categorise":
                questionObject["category"] = categorys
                questionObject["categoryItem"] = categoryItems
            else:
                questionObject["options"] = options
            questions.append(questionObject)


        return genUtility.getSuccessApiResponse(request, questions)
    except Exception as e:
        print("student_get_quiz", e)
        logService.logExceptionWithFunctionName("student_get_quiz", e)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def student_update_quiz_summary(request):
    try:
        if request.method != "POST":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        if genUtility.isGuardianUserAuthenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        requestBodyParams = simplejson.loads(request.body)
        studentId = requestBodyParams.get("studentId")
        userId = requestBodyParams.get("userId")
        userType = requestBodyParams.get("userType")
        questionSetId = requestBodyParams.get("questionSetId")
        contentDetailsId = requestBodyParams.get("contentDetailsId")
        totalPoints = requestBodyParams.get("totalPoints")
        questions = requestBodyParams.get("questions")



        if not userId or not userType or not questionSetId or not questions:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(questionSetId):
            return sendErrorResponse(request, "kInvalidRequest")

        if not genUtility.isGuardian(userId, userType):
            return sendErrorResponse(request, "kUserGuardian")

        if genUtility.checkIfStudentBelongsToGuardian(request, studentId) is False:
            return sendErrorResponse(request, "kInvalidStudentGuardRel")

        # Validate  Student obj
        try:
            studentObj = Student.objects.get(id=studentId, status='Active')
        except:
            return sendErrorResponse(request, "kStudentNotFound")

        quizHistory = Quiz_History(
            student=studentObj,
            content_detail_id=contentDetailsId,
            question_set_id=questionSetId,
            total_points=totalPoints
        )
        quizHistory.save()
        for question in questions:
            quizHistorydetails = Quiz_History_Detail(
                quiz_history=quizHistory,
                question_id=question.get("id"),
                points_earned=question.get("points"),
                answer_given=question
            )
            quizHistorydetails.save()
        responseData = {
            "message": "Quiz submitted successfully!",
        }
        return genUtility.getSuccessApiResponse(request, responseData)
    except Exception as e:
        print("student_get_question_set", e)
        logService.logException("student_get_question_set", e.message)
        return genUtility.getStandardErrorResponse(request, "kInvalidRequest")
