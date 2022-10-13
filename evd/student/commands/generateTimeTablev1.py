import optparse
import sys, os
import MySQLdb
import simplejson

project_dir = os.path.abspath(os.path.join(__file__, "../../../"))
sys.path.append(project_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings
from web.models import *
from student.models import *
import genutilities.views as genUtility
import genutilities.logUtility as logService
import math
from datetime import datetime as datetimeObj
from datetime import timedelta as timedeltaObj
import traceback

class TimeTableGenerationStudents():
    def __init__(self):
        self.conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], \
                                    user=settings.DATABASES['default']['USER'], \
                                    passwd=settings.DATABASES['default']['PASSWORD'], \
                                    db=settings.DATABASES['default']['NAME'], \
                                    charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.courseMetaData = {}
        self.currentDateTime = datetimeObj.now()
        self.currentDateTimeString = genUtility.getDbDateStringFromDate(self.currentDateTime)
        self.currentDateStr = genUtility.getStringFromDate(self.currentDateTime)
        self.createdById = 8668
        self.maximumIterationPerStudent = 5000
        self.maxDailySessionPerSubject = 2
        self.ttConfigObject = {}

    def loadTimeTableConfiguration(self):
        ttConfigLocal = genUtility.getSystemSettingObj("timetableConfig")
        if ttConfigLocal:
            try:
                ttConfigJson = simplejson.loads(ttConfigLocal.value)
                self.ttConfigObject = ttConfigJson
            except Exception as e:
                logService.logInfo("loadTimeTableConfiguration", e.message)

    def getDailyMaxSessionPerSubject(self):
        dailylimit = self.ttConfigObject.get("maxDailySessionPerSubject")
        if dailylimit:
            return int(dailylimit)
        return 1

    def getSessionSettingsDuration(self,systemSettingsObj,grade):
        gradeVal = systemSettingsObj.get(grade)
        if gradeVal:
            return int(gradeVal)
        return 0


    def insertBulkTimeTableSessionRecords(self,records,fieldsArray,student):
        isInserted = True
        try:
            self.startTransaction()
            insertQuery = "INSERT INTO student_time_table_session (timetable_id,offering_id,topic_id,subtopic_ids,session_type,time_start,time_end,calDate,day_of_the_week,created_by_id,created_on,updated_by_id,updated_on,has_attended) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            results = self.cursor.executemany(insertQuery,records)
            print("results",results)
            self.commitTransaction()
        except Exception as e:
            isInserted = False
            self.rollbackTransaction()
            print("insertTimeTableRecords", e)
            logService.logException("insertTimeTableRecords", e.message)
        return isInserted


    def parseQueryResults(self,queryResults,fieldArray):
        dataList = queryResults
        dataDictList = []
        fieldCount = len(fieldArray)
        for eachRecord in dataList:
            eachObject = {}
            for i in range(fieldCount):
                fieldName = fieldArray[i]
                eachObject[fieldName] = eachRecord[i]
            dataDictList.append(eachObject)
        return dataDictList

    def getStudyPreferenceStudent(self,studentObj):
        try:
            studyTimeObjs = Study_Time_Preference.objects.filter(student=studentObj, status="active").order_by('day_of_the_week')
            firstDay = None
            days = []
            slotslist = []
            for i in studyTimeObjs:
                slotdata = {}
                if i.day_of_the_week not in days:
                    days.append(int(i.day_of_the_week))
                if not firstDay:
                    firstDay = i.day_of_the_week
                if firstDay != i.day_of_the_week:
                    continue
                slotdata["startTime"] = i.time_start
                slotdata["endTime"] = i.time_end
                slotdata["startTimeMin"] = int(i.start_time_min)
                slotdata["endTimeMin"] = int(i.end_time_min)
                slotslist.append(slotdata)

            if len(days) > 0 and len(slotslist) > 0:
                return {
                    "days": days,
                    "slots": slotslist
                }
            else:
                return None
        except Exception as e:
            print("getStudyPreferenceStudent", e)
            logService.logException("getStudyPreferenceStudent", e.message)

    def getOfferingsOptedByStudent(self,student,currentDateString,offeringidStr):

       try:
           finOfString = ""
           if offeringidStr:
               finOfString = ' AND offer.id IN (' + offeringidStr +") "

           whereClause = "oe.student_id = " + str(student.id)+" and offer.status != 'completed' and offer.end_date > '"+ currentDateString+ "'" + finOfString
           fieldArray = ["offeringId","startDate","endDate","centerId","courseId"]
           selectQuery = '''select oe.offering_id, offer.start_date, offer.end_date, offer.center_id,co.id from web_offering_enrolled_students as oe 
                  LEFT JOIN web_offering as offer on (offer.id = oe.offering_id) LEFT JOIN web_course as co on (co.id = offer.course_id) 
                  where ''' + whereClause + ''' ORDER BY offer.start_date ASC'''
           self.cursor.execute(selectQuery)
           dataList = self.cursor.fetchall()
           dataDictList = self.parseQueryResults(dataList,fieldArray)
           return dataDictList
       except Exception as e:
           print("getOfferingsOptedByStudent", e)
           logService.logException("getOfferingsOptedByStudent", e.message)

    def checkIfDayFull(self,curDate,maxEndTimeMin,slotArray,sessionDuration):
        for h in range(len(slotArray)):
            aSlot = slotArray[h]
            startMin = int(aSlot["startTimeMin"])
            endMin = int(aSlot["endTimeMin"])
            if maxEndTimeMin >= startMin and maxEndTimeMin <= endMin:
                nextSlotEndDTime = maxEndTimeMin + sessionDuration
                if nextSlotEndDTime <= endMin:
                    return (0,maxEndTimeMin)
                else:
                    if len(slotArray) > (h + 1):
                        nxtSlot = slotArray[h]
                        startMin = int(aSlot["startTimeMin"])
                        return (0,startMin)
                    else:
                        return (1,-1)
        return (1,-1)

    def getSlotDetailsForStudent(self,student,timetableObj,startDateString,endDateString,slotArray,sessionDuration):

       try:
           whereClause = "stt.timetable_id = " + str(
               timetableObj.id) + " and stt.status = 1 and stt.calDate >= '" + startDateString + "' AND stt.calDate <= '" + endDateString + "'"
           selectQuery = '''SELECT stt.calDate,MAX(stt.time_end) 
                                FROM student_time_table_session as stt 
                                where ''' + whereClause + " GROUP by stt.calDate ORDER BY stt.calDate"

           self.cursor.execute(selectQuery)
           dataList = self.cursor.fetchall()
           dataDictList = {}
           calDays = []
           firstFreeCal = None
           firstDateUsed = None
           for eachRecord in dataList:
               calDate = eachRecord[0]
               endTimeMin = eachRecord[1]
               if calDate and endTimeMin:
                   calDateStr = genUtility.getStringFromDate(calDate)
                   #calDays.append(calDateStr)
                   sessionObj = dataDictList.get(calDateStr)
                   if sessionObj is None:
                       sessionObj = {}
                       dataDictList[calDateStr] = sessionObj
                   sessionObj["maxEndTimeMin"] = endTimeMin
                   if firstDateUsed is None:
                       firstDateUsed = calDate
                   isDayFull,nextStartTime = self.checkIfDayFull(calDate,endTimeMin,slotArray,sessionDuration)
                   sessionObj["isDayFull"] = isDayFull
                   if isDayFull == 0:
                       #TODO: Add break time
                       sessionObj["nextStartTimeMin"] = nextStartTime
                       if firstFreeCal is None:
                           firstFreeCal = calDate

           return (dataDictList,firstFreeCal,firstDateUsed)
       except Exception as e:
           print("getSlotDetailsForStudent", e)
           logService.logException("getSlotDetailsForStudent", e.message)
           return ({},None,None)

    def getCourseAndTopicDetails(self,courseId):
        try:
            courseMetaData = self.courseMetaData.get(str(courseId))
            if courseMetaData:
                return courseMetaData

            whereClause = "course.id = " + str(courseId) + " and course.status = 'active' and tp.status != 'Inactive' and st.status != 'Inactive' and tp.num_sessions > 0 "
            fieldArray = ["courseId", "topicId", "numberOfSesson", "subtopicIdStr"]
            selectQuery = '''select course.id,tp.id, tp.num_sessions, group_concat(st.id) from web_course as course 
            LEFT JOIN web_topic as tp on (tp.course_id_id = course.id) 
            LEFT JOIN web_subtopics as st on (st.topic_id = tp.id) 
            WHERE  ''' + whereClause + ''' GROUP BY course.id,tp.id ORDER BY tp.priority ; '''

            self.cursor.execute(selectQuery)


            dataList = self.cursor.fetchall()
            dataDictList = []
            fieldCount = len(fieldArray)
            for eachRecord in dataList:
                eachObject = {}
                isSubtopicExist = True
                for i in range(fieldCount):
                    fieldName = fieldArray[i]
                    if fieldName == "subtopicIdStr":
                        subtopicString = eachRecord[i]
                        if subtopicString and subtopicString != "NULL" and subtopicString != "":
                            stArray = subtopicString.split(',')
                            if stArray and len(stArray) > 0:
                                eachObject["subtopicIds"] = stArray
                            else:
                                isSubtopicExist = False
                        else:
                            isSubtopicExist  = False
                    else:
                        eachObject[fieldName] = eachRecord[i]

                if isSubtopicExist is True:
                    dataDictList.append(eachObject)

            if dataDictList and len(dataDictList) > 0:
                self.courseMetaData[str(courseId)] = dataDictList
            return dataDictList
        except Exception as e:
            print("getCourseAndTopicDetails", e)
            logService.logException("getCourseAndTopicDetails", e.message)

    def insertSlotToSessionList(self,currentSlot,finalSessionList,fieldsArray):
        recodList = list()
        for i in range(len(fieldsArray)):
            keyName = fieldsArray[i]
            valuevar = ""
            if keyName == "subTopicIds":
                subtopicsIds = currentSlot[keyName]
                valuevar = ','.join(str(x) for x in subtopicsIds)
            else:
                valuevar = currentSlot[keyName]
            recodList.append(valuevar)
        finalSessionList.append(recodList)

    def canGetSameDaySlot(self,slots,newFromTime,newEndTime):
        for j in range(len(slots)):
            aSlot = slots[j]
            startMin = int(aSlot["startTimeMin"])
            endMin = int(aSlot["endTimeMin"])
            if newFromTime >= startMin and newEndTime <= endMin:
                return True
        return False


    def getStartTimeOfSlotAvailable(self,selDate,selDay,freeslotDict,slotArray,sessionDuration,days):

        curDay, curDate = selDay,selDate
        isSuitableDateFound = False
        slotDict = None
        counter = 0
        maxCounter = len(freeslotDict) + 1
        while isSuitableDateFound is False and counter < maxCounter:
            counter = counter + 1
            selDateStr = genUtility.getStringFromDate(curDate)
            slotDict = freeslotDict.get(selDateStr)
            if slotDict and len(slotDict) > 0:
                isFullDay = slotDict["isDayFull"]
                if isFullDay == 1 or isFullDay == "1":
                    # Look for another day
                    curDate,curDay = self.getNextSuitableDay(days,curDay,curDate)
                else:
                    #startMin = slotDict["nextStartTimeMin"]
                    #endMin = startMin + sessionDuration
                    isSuitableDateFound = True
                    return (True,slotDict,curDate,curDay)
            else:
                return (False, None , curDate, curDay)

        return (False, None, curDate, curDay)



    def getNextSuitableDay(self,days,curDay,curDate):
        finalDay = int(days[0])
        diffDays = 0
        lenDays = len(days)
        for tt in range(lenDays):
            dayVar = int(days[tt])
            if  dayVar > curDay:
                finalDay = dayVar
                diffDays = dayVar - curDay
                break
        if diffDays == 0:
            diffDays = (7 - curDay) + finalDay

        nxtDate = curDate + timedeltaObj(days=diffDays)
        return [nxtDate,finalDay]

    def getFirstSlot(self,slotsPref,sessionDuration):
        if slotsPref and len(slotsPref) > 0:
            aSlot = slotsPref[0]
            startMin = int(aSlot["startTimeMin"])
            endMin = startMin + sessionDuration
            return [startMin,endMin]

    def resetAllSubjectCurrentSession(self,allSubjectStatusInfo):
        for eachKey in allSubjectStatusInfo:
            statusInfo = allSubjectStatusInfo[eachKey]
            statusInfo["dailySessionCount"] = 0

    def getNextSlot(self,prevSlot,studyPreference,sessionDuration,timeTableobj,scheduleStartDate,breakTime,subStatusInfo,freeslotDict,isRegeneration):
        try:
            if prevSlot:
                pass
                #print("prevSlot ", prevSlot["calDate"], prevSlot["startTimeMin"], prevSlot["endTimeMin"],prevSlot["dayOftheWeek"])
            nextSlot = {
                "timeTableId": timeTableobj.id,
                "sessionType": "1",
                "createdBy": self.createdById,
                "createdOn": self.currentDateTime,
                "updatedBy": self.createdById,
                "updatedOn": self.currentDateTime,
                "hasAttended":0,
                "status":1
            }

            prefDates = studyPreference["days"]
            slotsPref = studyPreference["slots"]
            startMin, endMin, selDate, selDay = 0, 0, None, 0
            if prevSlot is None or len(prevSlot) <= 0:
                weekDay = scheduleStartDate.weekday() + 1
                selDay = weekDay
                selDate = scheduleStartDate
                if weekDay not in prefDates:
                    selDate, selDay = self.getNextSuitableDay(prefDates, weekDay, scheduleStartDate)

                #print("FIRST SLOT SELECTED DAY and date ", selDay, selDate)
                # Select time slot
                if isRegeneration is True and freeslotDict and len(freeslotDict) > 0:
                    selDayStr = genUtility.getStringFromDate(selDate)
                    slotDict =  freeslotDict.get(selDayStr)
                    if slotDict:
                        timeMin = slotDict["nextStartTimeMin"]
                        startMin = int(timeMin)
                        endMin = startMin + sessionDuration
                    else:
                        startMin, endMin = self.getFirstSlot(slotsPref, sessionDuration)
                else:
                    startMin, endMin = self.getFirstSlot(slotsPref, sessionDuration)
            else:
                prevEndTime = prevSlot["endTimeMin"]
                newFromTime = prevEndTime + breakTime
                newEndTime = newFromTime + sessionDuration

                #TODO: Check if the slot belongs to live class

                prevCalDate = prevSlot["calDate"]
                # Check if end time can fall in the same day
                isSameDay = self.canGetSameDaySlot(slotsPref, newFromTime, newEndTime)
                if isSameDay is True:
                    #Check if all the subject's max session limit exceeded.
                    #if yes, reset all the subjects curDate and no of session count
                    numMaxSession =  self.maxDailySessionPerSubject
                    currentSessionCount = subStatusInfo["dailySessionCount"]
                    curCalDate = subStatusInfo["curCalDate"]
                    if curCalDate:
                        if currentSessionCount >= numMaxSession and (prevCalDate == curCalDate):
                            isSameDay = False
                            #logService.logInfo("isSameDay false","")
                            #print("isSameDay is false")

                if isSameDay is True:
                    startMin, endMin, selDate, selDay = newFromTime, newEndTime, prevSlot["calDate"], prevSlot[
                        "dayOftheWeek"]
                else:
                    selDate, selDay = self.getNextSuitableDay(prefDates, prevSlot["dayOftheWeek"], prevSlot["calDate"])
                    isTimeRequired = True
                    #check if Sel day has any bandwidth
                    if isRegeneration is True and freeslotDict and len(freeslotDict) > 0:
                        isSlotFound,slotDict,selDate,selDay = self.getStartTimeOfSlotAvailable(selDate, selDay, freeslotDict, slotsPref, sessionDuration,prefDates)
                        #print("isSlotFound,slotDict,selDate,selDay",isSlotFound,slotDict,selDate,selDay)
                        if isSlotFound is True:
                            startMin = slotDict["nextStartTimeMin"]
                            endMin = startMin + sessionDuration
                            isTimeRequired = False

                    if isTimeRequired is True:
                        # Select time slot
                        startMin, endMin = self.getFirstSlot(slotsPref, sessionDuration)

            nextSlot["startTimeMin"] = startMin
            nextSlot["endTimeMin"] = endMin
            nextSlot["calDate"] = selDate
            nextSlot["dayOftheWeek"] = selDay
            return nextSlot
        except Exception as e:
            print("getNextSlot", e)
            traceback.print_exc()
            logService.logException("getNextSlot", e.message)
            return None


    def calculateSubtopicToSessionAssignement(self,subtopicIds,requiredSes):
        try:
            slotAllocated = {}
            subtopicLen = len(subtopicIds)
            if subtopicIds:
                subtopicCount = subtopicLen
                perslot, reminder = 0, 0

                if subtopicCount >= requiredSes:
                    perSlot = int(subtopicCount) / int(requiredSes)
                    perslot = int(math.ceil(perSlot))
                    reminder = subtopicCount - (perSlot * requiredSes)
                    jj, lenJJ = 0, 0
                    for k in range(requiredSes):
                        if k == (requiredSes - 1):
                            idsAssigned = subtopicIds[jj:]
                        else:
                            idsAssigned = subtopicIds[jj:jj + perslot]
                            jj += perslot
                        slotAllocated[str(k + 1)] = idsAssigned
                    pass
                else:
                    perSlot = requiredSes / subtopicCount
                    perslot = int(math.ceil(perSlot))
                    reminder = requiredSes - (perslot * subtopicCount)
                    sessionNum = 1
                    for oCounter in range(subtopicLen):
                        stId = subtopicIds[oCounter]
                        for counter in range(perslot):
                            slotAllocated[str(sessionNum)] = [stId]
                            sessionNum = sessionNum + 1
                    if reminder > 0:
                        lastSubTopicId = subtopicIds[-1]
                        for rmIndex in range(reminder):
                            slotAllocated[str(sessionNum)] = [lastSubTopicId]
                            sessionNum = sessionNum + 1

            return slotAllocated
        except Exception as e:
            print("calculateSubtopicToSessionAssignement", e)
            logService.logException("calculateSubtopicToSessionAssignement", e.message)

    def isTimeTableGenerationPending(self,ttStatusInfo):
        isPending = False
        for key in ttStatusInfo:
            ttObj = ttStatusInfo[key]
            if ttObj["status"] == "0":
                isPending = True
                return isPending
        return isPending

    def isSlotSuitableForOffering(self, curSubject, curSlot,tpStatusInfo):
        sDate = tpStatusInfo.get("sDate")
        eDate = tpStatusInfo.get("eDate")
        slotDate = curSlot["calDate"]
        isStart,isEnd = False,False
        if sDate and ( sDate <= slotDate):
            isStart = True

        if eDate and (eDate >= slotDate):
            isEnd = True
        return (isStart and isEnd)

    def isSlotCrossedExpiryDate(self, curSubject, curSlot,tpStatusInfo):
        eDate = tpStatusInfo.get("eDate")
        slotDate = curSlot["calDate"]
        isCourseDateOver = False

        if eDate and (eDate >= slotDate):
            isCourseDateOver = False
        else:
            isCourseDateOver = True

        return isCourseDateOver


    def getNextSuitableDateIfRequired(self, curSubject, curSlot,subjectStateInfo,offeringsArray):
        # Check if slot can be used by any other offering, if not , move it to latest one.
        nextSuitableCalDate = None
        for kk in range(len(offeringsArray)):
            offerObj = offeringsArray[kk]
            curOfferingId = str(offerObj["offeringId"])
            stateInfo = subjectStateInfo[curOfferingId]
            if stateInfo["status"] == "0":
                isSuitable = self.isSlotSuitableForOffering(curSubject,curSlot,stateInfo)
                if isSuitable is True:
                    return None
                sDate = stateInfo.get("sDate")
                if nextSuitableCalDate is None or (nextSuitableCalDate > sDate):
                    nextSuitableCalDate = sDate
            else:
                continue
        #We have not found any suitable for current offering, hence fast tracking to next start date
        if nextSuitableCalDate:
            return nextSuitableCalDate
        else:
            return None


    def generateTimeTableForStudent(self,timetable,student,sessionDuration):
        try:
            # get offerings opted by student sort by their start time
            # get student's study preference
            # get topics for the course and number of sessions
            # get number of subtopics
            # create session for offering in Round robin fashion
            print("generateTimeTableForStudent", student.id,student)
            isGenerationSuccess = True
            logService.logInfo("generateTimeTableForStudent ",str(student.id))
            currentDateString = genUtility.getMidNightDateStringFromDate(genUtility.getCurrentTime())

            offeringIdStr = None
            if timetable.generation_type == "2":
                offerIdString = timetable.subject_to_be_processed
                if offerIdString:
                    offeringIdStr = offerIdString

            offeringArray = self.getOfferingsOptedByStudent(student, currentDateString,offeringIdStr)


            scheduleStartDate = None
            if offeringArray and len(offeringArray) > 0:
                tempVar = offeringArray[0]["startDate"]
                scheduleStartDate = tempVar.date()
            else:
                logService.logInfo("offeringArray is empty ","")
                return  False

            studyPreference = self.getStudyPreferenceStudent(student)
            if studyPreference and offeringArray:
                pass
            else:
                logService.logInfo("studyPreference and offeringArray is empty ","")
                return False
            numberOfSubjects = len(offeringArray)
            #print("numberOfSubjects",numberOfSubjects,offeringArray)
            currentSlot = {}
            prevSlot = {}
            topicCounterStatus = {}
            offeringIdsArr = []
            finEndDate = None
            for offerObj in offeringArray:
                curOfferingId = str(offerObj["offeringId"])
                offeringIdsArr.append(curOfferingId)
                sDate,eDate = None,None
                if offerObj["startDate"] is not None:
                    sDate = offerObj["startDate"].date()
                if offerObj["endDate"] is not None:
                    eDate = offerObj["endDate"].date()
                    if finEndDate is None or finEndDate < eDate:
                        finEndDate = eDate
                tpStatusInfo = {"topicIndex": 0, "numSessionCompleted": 0, "requiredSession": 0, "status": "0","sDate":sDate,"eDate":eDate,"curCalDate":None,"dailySessionCount":0}
                topicCounterStatus[curOfferingId] = tpStatusInfo

            maxSessionPerDayPerSubject = 2
            liveClassSchedule =  {} #self.getLiveClassSchedule(student, offeringIdsArr)
            #print("liveClassSchedule",liveClassSchedule)
            finalSessionList = []
            fieldsArray = ["timeTableId", "offeringId", "topicId", "subTopicIds", "sessionType", "startTimeMin",
                           "endTimeMin", "calDate", "dayOftheWeek", "createdBy", "createdOn", "updatedBy", "updatedOn","hasAttended"]
            breakTime = 5

            isRegeneration = False
            freeSlotDict = None
            firstFreeCalDate = None
            if timetable.generation_type == "2":
                prefDays = studyPreference["days"]
                weekValue = scheduleStartDate.weekday() + 1
                if weekValue not in prefDays:
                    scheduleStartDate, selDay = self.getNextSuitableDay(prefDays, weekValue, scheduleStartDate)

                startDateOffStr = genUtility.getStringFromDate(scheduleStartDate)
                endDateOffStr = genUtility.getStringFromDate(finEndDate)
                slotsArray = studyPreference["slots"]

                freeSlotDict,firstFreeCalDate,firstDateUsed = self.getSlotDetailsForStudent(student, timetable, startDateOffStr, endDateOffStr,slotsArray,sessionDuration)
                #TODO: Handle if scheduleStartDate is earlier than older offerings start date
                if freeSlotDict and len(freeSlotDict) > 0:
                    if firstDateUsed > scheduleStartDate:
                        pass
                    elif firstFreeCalDate > scheduleStartDate:
                        scheduleStartDate = firstFreeCalDate
                    isRegeneration = True

            #TODO: Live session time check
            ccounter, numIteration = 0,self.maximumIterationPerStudent
            while self.isTimeTableGenerationPending(topicCounterStatus) is True and ccounter < numIteration:
                ccounter = ccounter + 1
                if ccounter == (numIteration - 1):
                    print("Infinite loop check")
                    logService.logException("Infinite loop check for Time table generation.", str(student.id))

                for i in range(numberOfSubjects):
                    currentSubject = offeringArray[i]

                    if currentSubject["courseId"]:
                        curOfferingId = str(currentSubject["offeringId"])
                        tpStatusInfo = topicCounterStatus.get(curOfferingId)
                        if tpStatusInfo and tpStatusInfo["status"] == "1":
                            continue

                        currentSlot = self.getNextSlot(prevSlot, studyPreference, sessionDuration,timetable,scheduleStartDate,breakTime,tpStatusInfo,freeSlotDict,isRegeneration)

                        #check if slot date is suitable for current subject
                        isSuitable = self.isSlotSuitableForOffering(currentSubject,currentSlot,tpStatusInfo)
                        if isSuitable is False:
                            #Check if course end date is less than the slots
                            isCourseOver =  self.isSlotCrossedExpiryDate(currentSubject,currentSlot,tpStatusInfo)
                            if isCourseOver is True:
                                tpStatusInfo["status"] = "1"
                                logService.logInfo("COURSE IS OVER ",str(curOfferingId))
                                continue


                            nextCalDate = self.getNextSuitableDateIfRequired(currentSubject, currentSlot,topicCounterStatus,offeringArray)
                            if nextCalDate is None:
                                continue
                            else:
                                print("FAST FORWARDING ",nextCalDate)
                                scheduleStartDate = nextCalDate
                                prevSlot = {}
                                self.resetAllSubjectCurrentSession(topicCounterStatus)
                                continue

                        topicsMetaData = self.getCourseAndTopicDetails(currentSubject["courseId"])
                        topicLen = len(topicsMetaData)

                        # Get current topic counter
                        topicIndex = 0

                        if tpStatusInfo:
                            topicIndex = tpStatusInfo["topicIndex"]
                        else:
                            tpStatusInfo = {"topicIndex": 0, "numSessionCompleted": 0, "requiredSession": 0,
                                            "status": "0"}
                            topicCounterStatus[curOfferingId] = tpStatusInfo

                        if topicIndex >= topicLen:
                            tpStatusInfo["status"] = "1"
                            continue

                        topicObj = topicsMetaData[topicIndex]
                        subtopicIds = topicObj.get("subtopicIds")

                        if subtopicIds is None or len(subtopicIds) <= 0:
                            #print("Subtopic is empty for Id",topicObj)
                            topicIndex = topicIndex + 1
                            allSubtopicEmpty = True
                            while  topicIndex < topicLen:
                                topicObj = topicsMetaData[topicIndex]
                                subtopicIds = topicObj.get("subtopicIds")
                                if subtopicIds and len(subtopicIds) > 0:
                                    allSubtopicEmpty = False
                                    break
                                topicIndex = topicIndex + 1

                            if allSubtopicEmpty is True:
                                tpStatusInfo["topicIndex"] = topicIndex
                                tpStatusInfo["status"] = "1"
                                continue
                        subtopicLen = len(subtopicIds)
                        if tpStatusInfo["requiredSession"] is None or tpStatusInfo["requiredSession"] == 0:
                            tpStatusInfo["requiredSession"] = topicObj["numberOfSesson"]

                        completedSesNum = tpStatusInfo["numSessionCompleted"]
                        requiredSes = tpStatusInfo["requiredSession"]

                        if completedSesNum >= requiredSes:
                            # increase the counter,update topic info,status
                            continue
                        else:
                            # Assign Topic and subtopics to current slot
                            # Convert current slot to Tuple
                            # Add current slot to List
                            # Increment Topic counter, subTopic counter
                            # Assign current slot to previous slot
                            if completedSesNum == 0:
                                # calculate subtopic split
                                if subtopicIds and subtopicLen > 0:
                                    slotAllocated = self.calculateSubtopicToSessionAssignement(subtopicIds, requiredSes)
                                    if slotAllocated and len(slotAllocated):
                                        tpStatusInfo["stAssignments"] = slotAllocated
                                    else:
                                        continue

                            # Assign already split ids to the current session, increment counter,
                            # Check completedSesNum >= requiredSes after increment
                            stTopicsAssigned = tpStatusInfo["stAssignments"][str(completedSesNum + 1)]
                            currentSlot["subTopicIds"] = stTopicsAssigned
                            currentSlot["topicId"] = topicObj["topicId"]
                            currentSlot["offeringId"] = curOfferingId
                            completedSesNum = completedSesNum + 1
                            tpStatusInfo["numSessionCompleted"] = completedSesNum

                            newSlotDate = currentSlot["calDate"]
                            oldSlotDate = tpStatusInfo ["curCalDate"]
                            if oldSlotDate is None or newSlotDate != oldSlotDate:
                                tpStatusInfo["dailySessionCount"] = 1
                                tpStatusInfo["curCalDate"] = currentSlot["calDate"]
                            else:
                                tpStatusInfo["dailySessionCount"] = tpStatusInfo["dailySessionCount"] + 1



                            self.insertSlotToSessionList(currentSlot, finalSessionList, fieldsArray)

                            prevSlot = currentSlot
                            #print("Current Slot(date,st time, end time,weekday,topic id, subtopic id) ", prevSlot["calDate"], prevSlot["startTimeMin"], prevSlot["endTimeMin"],
                                 #prevSlot["dayOftheWeek"],currentSlot["topicId"],currentSlot["subTopicIds"],currentSlot["offeringId"])

                            if completedSesNum >= requiredSes:
                                # increase the counter,update topic info,status
                                topicIndex = topicIndex + 1
                                tpStatusInfo["topicIndex"] = topicIndex
                                tpStatusInfo["numSessionCompleted"] = 0
                                tpStatusInfo["requiredSession"] = 0
                                if topicIndex >= topicLen:
                                    tpStatusInfo["status"] = "1"



            print("finalSessionList ",len(finalSessionList),ccounter)
            logService.logInfo("finalSessionList", str(len(finalSessionList)) + " Number of iterations "+str(ccounter))
            isGenerationSuccess = self.insertBulkTimeTableSessionRecords(finalSessionList,fieldsArray,student)
            logService.logInfo("TT generation completed ", str(student.id))
        except Exception as e:
            isGenerationSuccess = False
            logService.logException("ERROR generateTimeTableForStudent", e.message)
            print("generateTimeTableForStudent result", e)
            traceback.print_exc()
        return isGenerationSuccess


    def updateTimeTableGenerationStatus(self,ttIdString,genStatus,status):
        isUpdated = False
        try:
            updatedFieldsString = "generation_status = '" + genStatus + "'"
            if status:
                updatedFieldsString += " , status = '"+status+"'"

            updateQuery = "UPDATE student_time_table SET "+ updatedFieldsString +" WHERE id IN (" + ttIdString + ")"
            result =  self.cursor.execute(updateQuery)
            isUpdated = True

        except Exception as e:
            logService.logException("updateStudentStatus", e.message)
            print("updateStudentStatus result", e)
            #traceback.print_exc()
        return isUpdated

    def getStudentIds(self,ttObjects):
        studentList = [ttObjects[0].id]
        studentIdStr = str(ttObjects[0].id)
        counter = 1
        while counter < len(ttObjects):
            tt = ttObjects[counter]
            studentList.append(tt.id)
            studentIdStr = studentIdStr + ","+ str(tt.id)
            counter = counter + 1
        return [studentList,studentIdStr]

    def getLiveClassSchedule(self,student, offeringIds):
        sessionList = None
        try:
            offeringString = ""
            if offeringIds and len(offeringIds) > 0:
                offeringString = genUtility.getStringFromIdArray(offeringIds)
            else:
                return None

            startDateStr =  self.currentDateStr
            startDateStr = startDateStr + " " + "00:00:00"

            fieldsArray = ["id", "offeringId", "startDate", "endDate"]
            fieldStr = "ws.id, ws.offering_id,ws.date_start,ws.date_end"
            whereClsStr = "ws.status = 'scheduled' and ws.offering_id IN (" + offeringString +") and ws.date_end >= '"+startDateStr+"' and ws.date_start >= '"+ startDateStr +"'"

            selectQuery = '''select ''' + fieldStr + ''' from web_session as ws 
                    WHERE ''' + whereClsStr +" ORDER BY ws.date_start"
            
            self.cursor.execute(selectQuery)
            dataList = self.cursor.fetchall()
            fieldCount = len(fieldsArray)
            liveClassSchedule = {}
            for eachRecord in dataList:
                eachObject = {}
                curDateString = None
                for i in range(fieldCount):
                    fieldName = fieldsArray[i]
                    if fieldName == "startDate":
                        startDateObj = eachRecord[i]
                        if startDateObj:
                            dateObjN= startDateObj.date()
                            eachObject["startDate"] = dateObjN
                            curDateString =  genUtility.getStringFromDate(dateObjN)
                            eachObject["startTime"] = genUtility.getTimeInMinutesDateObj(startDateObj)
                    elif fieldName == "endDate":
                        endDateObj = eachRecord[i]
                        if endDateObj:
                            eachObject["endDate"] = endDateObj.date()
                            eachObject["endTime"] = genUtility.getTimeInMinutesDateObj(endDateObj)
                    else:
                        eachObject[fieldName] = eachRecord[i]

                if curDateString:
                    sessionList = liveClassSchedule.get(curDateString)
                    if sessionList:
                        sessionList.append(eachObject)
                    else:
                        liveClassSchedule[curDateString] = [eachObject]

            return liveClassSchedule

        except Exception as e:
            print("getLiveClassSchedule", e)
            logService.logException("getLiveClassSchedule function", e.message)
            traceback.print_exc()
            return sessionList

    def startTransaction(self):
        try:
            transactionQuery = "START TRANSACTION;"
            result =  self.cursor.execute(transactionQuery)
            print("START TRANSACTION",result)
            logService.logInfo("START TRANSACTION",result)

        except Exception as e:
            logService.logException("startTransaction", e.message)
            print("startTransaction result", e)
            #traceback.print_exc()

    def commitTransaction(self):
        isUpdated = False
        try:
            transactionQuery = "COMMIT;"
            result = self.cursor.execute(transactionQuery)
            print("COMMIT TRANSACTION", result)
            logService.logInfo("COMMIT TRANSACTION", result)

        except Exception as e:
            logService.logException("commitTransaction", e.message)
            print("commitTransaction", e)
            # traceback.print_exc()

    def rollbackTransaction(self):
        isUpdated = False
        try:
            transactionQuery = "ROLLBACK;"
            result = self.cursor.execute(transactionQuery)
            print("ROLLBACK TRANSACTION", result)
            logService.logInfo("ROLLBACK TRANSACTION", result)

        except Exception as e:
            logService.logException("rollbackTransaction", e.message)
            print("rollbackTransaction", e)
            # traceback.print_exc()

    def generateTimeTableForPendingStudents(self):
        try:
            #Get students whose time table status is pending and created in last 24 hours
            #update their status to In progress
            #For each student, call generateTimeTableForStudent function
            #update status if generation success,else change it back to pending
            timeDeltaDateTime = genUtility.getTimeBeforeXhours(24)
            pState,prgState,cState,reGenState = "3","4","1","5"
            pendingStudents = Time_Table.objects.filter(status="pending",generation_status=pState,updated_on__gte=timeDeltaDateTime).select_related("student")
            studentCount = len(pendingStudents)
            logService.logInfo("pendingStudents count", str(studentCount))
            if studentCount > 0:
                ttIds, ttIdStr = self.getStudentIds(pendingStudents)
                isUpdated = self.updateTimeTableGenerationStatus(ttIdStr,prgState,None)
                if isUpdated is False:
                    logService.logInfo("status updated failed pendingStudents count", len(pendingStudents))
                    return
                durationConig = genUtility.getSystemSettingObj("SessonDurationGradewise")
                settingObj = {}
                if durationConig:
                    settingObj = simplejson.loads(durationConig.value)
                else:
                    logService.logInfo("Duration object is not set", "")
                    self.updateTimeTableGenerationStatus(ttIdStr, pState, None)
                    return

                self.loadTimeTableConfiguration()
                self.maxDailySessionPerSubject = self.getDailyMaxSessionPerSubject()
                for timeTableObj in pendingStudents:
                    eachStudent = timeTableObj.student
                    if eachStudent.grade is None:
                        self.updateTimeTableGenerationStatus(str(timeTableObj.id), pState, None)
                        continue
                    sessionDuration = self.getSessionSettingsDuration(settingObj,eachStudent.grade)
                    if sessionDuration <= 0:
                        self.updateTimeTableGenerationStatus(str(timeTableObj.id), pState, None)
                        continue


                    genStatus = self.generateTimeTableForStudent(timeTableObj,eachStudent,sessionDuration)
                    if genStatus is True:
                        #update status to completed
                        self.updateTimeTableGenerationStatus(str(timeTableObj.id), cState, "active")
                        pass
                    else:
                        #update back to pending
                        self.updateTimeTableGenerationStatus(str(timeTableObj.id), pState, None)
                        pass
            else:
                print("There were no students to process")
                logService.logInfo("There were no students to process","")

        except Exception as e:
            print("generateTimeTableForPendingStudents",e)
            #reset the ids back to In progress for any "In progress" ids of this batch
            logService.logException("generateTimeTableForPendingStudents", e.message)
            traceback.print_exc()


    def main(self, options):

        print("Start TimeTableGenerationStudents")
        self.generateTimeTableForPendingStudents()
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    #parser.add_option('-t', '--type', default="", help='Student Time table generation')
    #parser.add_option('-i', '--id', default=None, help='Id of an student')
    parser.add_option('-s', '--source', default='dev', help='Source dev/prod')
    (options, args) = parser.parse_args()

    OBJ = TimeTableGenerationStudents()
    OBJ.main(options)
