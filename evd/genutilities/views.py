# Create your views here
from django.http import HttpResponse,HttpResponseBadRequest
import json
import re
from .models import ApiSession,Language
from django.utils.crypto import get_random_string
from web.models import *
from student.models import *
import os
import errorConstantUtility as errorConstService
from datetime import datetime as datetimeObj
from datetime import timedelta
import pytz as timezoneObj
import logging
import logUtility as logService
import  base64
import random
import math
from datetime import date as dateOnlyObj
import simplejson
import settings as appSettingObj
import requests
from django.template import Context
from django import template
from django.core.mail import EmailMessage
from django.shortcuts import render

def _get_new_session_key(userObj):
    # Todo: move to 0-9a-z charset in 1.5
    hex_chars = '1234567890abcdef'
    session_key = ""
    while True:
        session_key = get_random_string(32, hex_chars)
        if userObj:
            session_key = str(userObj.id)+session_key
        if checkIfSessionKeyExist(session_key):
            continue
        else:
            break
    return session_key

def getSuccessApiResponse(request,responseData):
    statusObject = {
        "status":"success",
        "statusCode":200,
        "data":responseData

    }
    return HttpResponse(json.dumps(statusObject), content_type='application/json')

def getBadRequestErrorApiResponse(request,errorCode,errorMessage):
    errorObject = {
        "status":"error",
        "statusCode":400,
        "error": {
           "code":errorCode,
           "message":errorMessage
        }
    }
    return HttpResponseBadRequest(json.dumps(errorObject), content_type='application/json')

def getForbiddenRequestErrorApiResponse(request,errorCode=None,errorMessage=None):
    if not errorMessage:
        errorMessage = "Access Denied"
    if not errorCode:
        errorCode = 102
    errorObject = {
        "status":"error",
        "statusCode":403,
        "error": {
           "code":errorCode,
           "message":errorMessage
        }
    }
    return HttpResponseBadRequest(json.dumps(errorObject), content_type='application/json')

def isObjectNotEmpty(keyObject):
    return (keyObject and len(keyObject))

def passwordValidator(password):
    uppCaseAvailable = re.search('[A-Z]',password)
    lowerCaseAvailable = re.search('[a-z]',password)
    if len(password) >= 8 and uppCaseAvailable and lowerCaseAvailable:
        return True
    return False

def checkIfSessionKeyExist(sessionKey):
    isSessionExist = False
    try:
        sessionKeys = ApiSession.objects.filter(session_key=sessionKey,status=True)
        if sessionKeys and len(sessionKeys) > 0:
            isSessionExist =  True
    except Exception as e:
        logService.logException("checkIfSessionKeyExist", e.message)

    return isSessionExist

def createSessionForUser(userObj,type=None,id=None):
    if not type:
        type = "other"
    sessionKey = _get_new_session_key(userObj)
    expirtyTime = datetimeObj.now() + timedelta(days=365)
    session =  ApiSession.objects.create(
        user=userObj,
        session_key = sessionKey,
        status = True,
        expiry_time=expirtyTime,
        belongs_to = id,
        type = type

    )
    session.save()
    return session

def invalidateSession(sessionObj):
    if sessionObj:
        sessionObj.status = False
        sessionObj.save()

def checkUserAuthentication(user):
    if user and user.is_authenticated:
        return True
    else:
        return False


def isValidEmailAddress(emailId):
    #regexForEmail = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    regexForEmail = "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
    if (re.search(regexForEmail, emailId)):
        return True

    else:
        return False


def getRandomString():
    hex_chars = '1234567890abcdef'
    randomString = get_random_string(10, hex_chars)
    return randomString


def isDSM(roles):
    for singleRole in roles:
        if 'DSM'in singleRole:
            return True
        else:
            return False

def isDSP(roles):
    for singleRole in roles:
        if 'DSP'in singleRole:
            return True
        else:
            return False

def returnRole(userId):
    userRoles = []
    if userId:
        userInstance = UserProfile.objects.get(user__id=int(userId))
        prefRoles =  userInstance.role.all()
        for role in prefRoles:
            if role.name == "Partner Admin":
                userRoles.append("DSP")
            if role.name == "Digital School Manager":
                userRoles.append("DSM")
            userRoles.append(role.name)
    return userRoles


def isDigitalPartner(partner):
    pTypes = partner.partnertype.values()
    for eachType in pTypes:
        if eachType['name'] == 'Digital Partner':
            return  True

    return False

def canSendEmail():
    environmentType = os.getenv('EVD_EMAIL_ON')
    if environmentType and environmentType == "on":
        return True
    else:
        return False

def getStandardErrorResponse(request,errorConstant):
    errorObj =  errorConstService.getErrorMessageAndCodeFromConstant(request,errorConstant)
    errorCode = errorObj.get("code")
    errorMsg = errorObj.get("msg")
    return  getBadRequestErrorApiResponse(request, errorCode,errorMsg)

def getTimeStampFromDate(someDateTime):
    try:
        if someDateTime:
            #timestamp = datetime.utcfromtimestamp(someDateTime)
            timestamp = (someDateTime - datetimeObj(1970, 1, 1)).total_seconds()
            return long(timestamp)
        else:
            return None
    except Exception as e:
        print("getTimeStampFromDate",e)
        return None

def checkIfParamIfInteger(valueNumber):
    valueNumber = long(valueNumber)
    if isinstance(valueNumber, (int, long)):
        return True
    else:
        return False

blackListedQueryWords = ["DROP TABLE"," UPDATE "]
def checkIfKeyIsSafeForQuery(searchKey):
    regexForQueryString = "^[a-zA-z0-9._]+$"
    if (re.match(regexForQueryString, searchKey)):
        if searchKey in blackListedQueryWords:
            return False
        return True
    else:
        return False

def isSchoolApproved(schoolId):
    try:
        DigitalSchool.objects.get(id=schoolId,status="Active")
        return True
    except:
        logging.exception("message")
        pass
    return False

def getCenter(schoolId):
    centerObj = None
    try:
        centerObj = Center.objects.get(digital_school_id=schoolId)
    except Exception as e:
        logService.logException("getCenter",e.message)

    return centerObj

def getLanguages():
    languages = []
    try:
        languages = Language.objects.filter(status=1).order_by('name')
    except Exception as e:
        print("getLanguages exception",e)
    return languages

def getValueElseThrowException(requestBodyParams,keyName):
    valueName = requestBodyParams.get(keyName)
    if valueName:
        return valueName
    raise Exception("Required field is missing " + keyName)


def getDateTimeFromString(dateString):
    return datetimeObj.strptime(dateString,'%Y-%m-%d %H:%M:%S')

def getDateFromString(dateString):
    return datetimeObj.strptime(dateString,'%Y-%m-%d')


def getStringFromDate(dateobj):
    return datetimeObj.strftime(dateobj,'%Y-%m-%d')

def getTimeStringFromDate(dateobj):
    return datetimeObj.strftime(dateobj,'%H:%M')

def getDbDateStringFromDate(dateobj):
    if dateobj:
        return datetimeObj.strftime(dateobj,'%Y-%m-%d %H:%M:%S')
    return None

def getMidNightDateStringFromDate(dateobj):
    return datetimeObj.strftime(dateobj,'%Y-%m-%d 23:59:59')

def getCurrentTime():
    return datetimeObj.now()

def getTodayDate():
    return dateOnlyObj.today()

def getCurrentDateTimeInStr():
    dateTimeObj = getCurrentTime()
    return getDbDateStringFromDate(dateTimeObj)

def settingGrade():
    data = {
        "supportedGrades": None,
    }

    grades = getDictObjectFromSystemSettingJSONForKey("supportedGrades")
    if grades is None:
        grades = {"from": 5, "to": 8}

    data["supportedGrades"] = grades
    return data

def timeStamFromDate(dateObj):
    return dateObj.replace(tzinfo=timezoneObj.utc).timestamp()
def dataFromTimeStampToObj(dateTimeStamp):
    return datetimeObj.fromtimestamp(dateTimeStamp)

def isNonProdEnvironment():
    environmentType = os.getenv('EVD_ENVIRONMENT_TYPE')
    if environmentType and environmentType != "prod" and environmentType != "":
        return True
    else:
        return False

def verifyBasicAuth(basicAuthKey):
    appKey =  os.getenv('EVD_PARTNER_APP_KEY')
    if appKey is None:
        return True
    if basicAuthKey is None:
        return False

    appSecret = os.getenv('EVD_PARTNER_APP_SECRET')
    basicKey = appKey+":"+appSecret
    baseEncodeString = "Basic " + base64.b64encode(basicKey)
    if baseEncodeString == basicAuthKey:
        return True
    else:
        return False

def is_basic_auth_authenticated(request):
    if request.is_basic_auth_authenticated is True:
        return True
    return False

def getSystemSettingValue(key):
    value = None
    try:
        sysObj = SystemSettings.objects.get(key=key,status=True)
        value = sysObj.value
    except:
        pass
    return value

def generateOTP():
    otp = random.randint(1111,9999)
    return otp

def isGuardian(userId,userType):
    if userType.lower() != 'guardian':
        return False
    try:
        Guardian.objects.get(id=userId)
        return True
    except:
        return False

def isStudent(userId,userType):
    if userType.lower() != 'student':
        return False
    try:
        Student.objects.get(id=userId)
        return True
    except:
        logging.exception("message")
        return False


def isDevEnvironment():
    environmentType = os.getenv('EVD_ENVIRONMENT_TYPE')
    if environmentType and (environmentType == "dev" or environmentType == "local"):
        return True
    else:
        return False

def getTimeAfterXhours(numberofHours):
    timeAfterAdding = datetimeObj.now() + timedelta(hours=numberofHours)
    return timeAfterAdding

def getTimeBeforeXhours(numberofHours):
    timeAfterAdding = datetimeObj.now() - timedelta(hours=numberofHours)
    return timeAfterAdding


def getTimeAfterXhoursToDate(dateObj,numberofHours):
    timeAfterAdding = dateObj + timedelta(hours=numberofHours)
    return timeAfterAdding

def getTimeAfterXMinutesToDate(dateObj,numberOfMins):
    if dateObj:
        timeAfterAdding = dateObj + timedelta(minutes=numberOfMins)
        return timeAfterAdding
    return None

def getDateTimeinIST(dateObj):
    return getTimeAfterXMinutesToDate(dateObj, 630)

def getCurrentDateTimeinIST():
    dateVal = getCurrentTime()
    return getTimeAfterXMinutesToDate(dateVal, 630)

def getSystemSettingObj(key):
    settingsObj = None
    try:
        settingsObj = SystemSettings.objects.get(key=key, status=True)
    except Exception as e:
        logService.logException("getSystemSettingObj", e.message)
    return settingsObj

def isint(value):
    try:
        int(value)
        return True
    except:
        return False

def getTimeInHHMMFormat(timeInMinutes):
    timeInMinutes = int(timeInMinutes)
    minutes = timeInMinutes % 60
    hours = math.floor(timeInMinutes / 60)
    hours =int(hours)
    timeStr = ""
    if hours <= 9:
        timeStr = "0"
    timeStr = timeStr + str(hours) + ":"

    if minutes <= 9:
        timeStr = timeStr + "0"
    timeStr = timeStr + str(minutes)
    return timeStr

def getStringFromIdArray(idsArray):
    studentIdStr = str(idsArray[0])
    counter = 1
    while counter < len(idsArray):
        idVal = idsArray[counter]
        studentIdStr = studentIdStr + "," + str(idVal)
        counter = counter + 1
    return studentIdStr


def getTimeInMinutesDateObj(dateTimeObj):
    if dateTimeObj:
        hour = dateTimeObj.hour
        minutes = dateTimeObj.minute
        timeInMin = 0
        if hour:
            timeInMin = 60 * int(hour)

        if minutes:
            timeInMin = timeInMin + int(minutes)

        return timeInMin
    return 0

def getDatesBetweenStartandEndDate(startDate,endDate,startDateStr,endDateStr):
    dateObj = getTimeAfterXhoursToDate(startDate,24)
    dateStringArr = []
    if startDateStr:
        dateStringArr.append(startDateStr)

    counter = 0
    while (dateObj < endDate) and counter < 31:
        counter = counter + 1
        dateStr = getStringFromDate(dateObj)
        if dateStr:
            dateStringArr.append(dateStr)
        dateObj = getTimeAfterXhoursToDate(dateObj, 24)

    if endDateStr:
        dateStringArr.append(endDateStr)

    return dateStringArr



def isGuardianUserAuthenticated(request):
    try:
        if is_basic_auth_authenticated(request) is False:
            return False
        if request.guardian and request.guardian.id > -1 and request.currentSession and request.currentSession.status is True:
            return True
        return False
    except Exception as e:
        print("isGuardianUserAuthenticated",e)
        return False


def checkIfStudentBelongsToGuardian(request,studentId):
    try:
        if request.guardian:
            guardianObj = request.guardian
            relList = Student_Guardian_Relation.objects.filter(guardian=guardianObj,status=True,student__id=studentId)
            if relList and len(relList) > 0:
                return True
        return False
    except Exception as e:
        print("checkIfStudentBelongsToGuardian",e)
        return False

def getGuardianForStudent(studentId):
    try:
        if studentId:
            relList = Student_Guardian_Relation.objects.filter(status=True,student__id=studentId)
            if relList and len(relList) > 0:
                guardinObj = relList[0].guardian
                return guardinObj
        return False
    except Exception as e:
        print("getGuardianForStudent",e)
        return None


def updateDocumentBelongsTo(userDoc,objectId):
    try:
        if userDoc:
            userDoc.belongs_to = objectId
            userDoc.save()
            return True
    except Exception as e:
        print("updateDocumentBelongsTo", e)
        logService.logInfo("updateDocumentBelongsTo ",e.message)
    return False


def getDictObjectFromSystemSettingJSONForKey(key):
    ttConfigLocal = getSystemSettingObj(key)
    if ttConfigLocal:
        try:
            ttConfigJson = simplejson.loads(ttConfigLocal.value)
            return ttConfigJson
        except Exception as e:
            logService.logInfo("getDataObjectFromSystemSettingJSONForKey", e.message)
            return None
    return None


def convertUnicodeIntegerArrayToIntegerArray(inArray):
    outArray = []
    try:
        for i in range(len(inArray)):
            outArray.append(long(inArray[i]))
    except Exception as e:
        print("convertUnicodeIntegerArrayToIntegerArray",e)
        logService.logInfo("convertUnicodeIntegerArrayToIntegerArray", e.message)
        return None
    return outArray

def isValidMobileNumber(mobile):
    mobile = str(mobile)
    regexForMob = "^[0-9]+$"
    if mobile and len(mobile) == 10 and (re.search(regexForMob, mobile)):
        return True
    else:
        return False

def getPincodes(stateId,searchText,page,count,connection):
    try:
        pincText = ""
        if searchText:
            searchText = str(searchText)
            pincText = " AND pc.pincode LIKE '%%{}%%'".format(searchText)

        stateString = ""
        if stateId:
            stateString = " AND pc.state_id = {}".format(stateId)


        queryString = "SELECT pc.id,pc.pincode,pc.district,pc.taluk from  genutilities_pincode as pc WHERE pc.status = 1 {} {} ORDER BY pc.pincode LIMIT {} OFFSET {}".format(
            stateString, pincText, count, page)

        cursor = connection.cursor()
        cursor.execute(queryString)
        dataList = cursor.fetchall()
        pLength = len(dataList)
        pincodeArr = []
        for counter in range(pLength):
            newObj = {}
            dataObj = dataList[counter]
            newObj["id"] = dataObj[0]
            newObj["pincode"] = dataObj[1]
            newObj["district"] = dataObj[2]
            newObj["taluk"] = dataObj[3]
            pincodeArr.append(newObj)
        return pincodeArr
    except Exception as e:
        print("getPincodes",e)
        logService.logExceptionWithExceptionobject("getPincodes",e)
        return []

def getActiveDSMForSchool(schoolId):
    roleObj = Role.objects.get(name="Digital School Manager")
    dsmObjects = DigitalCenterStaff.objects.filter(digital_school_id=schoolId, role=roleObj, status="Active")
    if dsmObjects and len(dsmObjects) > 0:
        return dsmObjects[0].user
    return None

def isLatLngValid(latVal):
    latVal = str(latVal)
    regexForLatLng = "^[\.0-9]+$"
    if latVal  and (re.search(regexForLatLng, latVal)):
        return True
    else:
        return False

def getUserObj(userId):
    userObj = None
    try:
        userObj = User.objects.get(id=userId)
    except Exception as e:
        pass
    return userObj

def isOTPEnabled():
    otpStatus = os.getenv('EVD_OTP_ON')
    if otpStatus and otpStatus == "on":
        return True
    else:
        return False

def sendOTPToMobileNumber(mobile,otpExpiryTime):
    authKey = appSettingObj.SMS_AUTHENTICATION_KEY
    templateId = appSettingObj.TEMPLATE_ID
    dltId = appSettingObj.MOBILE_DLT_TE_ID
    if isOTPEnabled() is True:
        mobileHashCode = appSettingObj.MOBILE_HASH_CODE_LOCAL
        mobile = appSettingObj.MOBILE_PREFIX + str(mobile)
        otp = generateOTP()

        #message = "Your eVidyaLoka login otp is {}. {}".format(otp, mobileHashCode)
        mobileHashCode = " " +mobileHashCode+". -EVIDYALOKA"
        message = "Your eVidyaLoka login otp is {}. {}".format(otp, mobileHashCode)
        sender = appSettingObj.MOBILE_SENDER_ID
        if otpExpiryTime:
            otpExpiry = int(otpExpiryTime)
        else:
            otpExpiry = 5
        extra_params = {}
        sender = "EVDYLK"
        baseURL = appSettingObj.BASE_URL_MSG91

        url = baseURL + "/api/sendotp.php?authkey={}&mobile={}&message={}&sender={}&otp={}&otp_expiry={}&DLT_TE_ID=1107164075999531088".format(
            authKey, mobile, message, sender, otp, otpExpiry)
        resp = requests.get(url)
        response = resp.json()
        #logService.logInfo("OTP url " , url)

        #print("OTP url", url)
        #print("OTP response",response)
        if response.get('type') and str(response.get('type')) == 'success':
            return otp
        else:
            return None
    else:
        return 'anyotp'


def verifyOTPWithServiceProvider(mobile,otp):
    phone = appSettingObj.MOBILE_PREFIX + str(mobile)
    authKey = appSettingObj.SMS_AUTHENTICATION_KEY
    templateId = appSettingObj.TEMPLATE_ID

    baseURL = appSettingObj.BASE_URL_MSG91

    if isOTPEnabled() is False:
        return "success"

    url = baseURL + "/api/verifyRequestOTP.php?authkey={}&mobile={}&otp={}".format(
        authKey,
        phone,
        otp
    )
    #logService.logInfo("OTP url ", url)
    resp = requests.get(url)
    response = resp.json()
    if (response.get('type') and str(response.get('type')) == 'success'):
       return "success"
    if response.get('message') and str(response.get('message')) == 'otp_expired':
        return "expired"
    else:
        return "failed"

def getUserOTPObject(mobile,otp):
    otpObjs = UserOtp.objects.filter(mobile=mobile, otp=otp)
    if otpObjs and len(otpObjs) > 0:
        return otpObjs[0]
    else:
        return None

def getSystemSettingObjs(keyNames):
    objects = []
    try:
        objects = SystemSettings.objects.filter(key__in=keyNames)
    except:
        pass
    return objects

def getSettingsForUserType(userType,keyNames,jsonKeys):
    try:
        results = getSystemSettingObjs(keyNames)
        settings = {}
        for eachObj in results:
            if str(eachObj.key) in jsonKeys:
                settings[eachObj.key] = json.loads(str(eachObj.value))
            else:
                settings[eachObj.key] = eachObj.value
        return settings
    except Exception as e:
        return {}

def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except Exception as e:
        return None

def getAcademicYearByCourseProviderId(courseProviderId):
    try:
        courseProviderObject = CourseProvider.objects.get(
            id=courseProviderId)
        ayfy = Ayfy.objects.filter(
            board=courseProviderObject.code,
            is_current= True
         )
        if ayfy:
            return ayfy[0]
        else:
            return None
    except Exception as e:
        return None

def getAcademicYearByCourseProvideCode(courseProviderCode):
    try:
        ayfy = Ayfy.objects.filter(
            board=courseProviderCode,
            is_current=True
        )
        if ayfy:
            return ayfy[0]
        else:
            return None
    except Exception as e:
        return None



def getErrorMessageFromException(e):
    msg = ""
    try:
        msg = e.message
        if (msg is None) or msg == "":
            msg = str(e)
    except Exception as e:
        msg=""
    return msg


    
def has_role_preference(user_obj, role_name):
    if not user_obj or not role_name: return False
    roles = RolePreference.objects.filter(userprofile=user_obj.userprofile, role__name=role_name)
    if len(roles)>0: return True
    return False

def get_mail_content(template_path, args):
    t = template.loader.get_template(template_path)
    return t.render(Context(args))


def send_mail_thread(subject, body, from_email, to, cc=[]):
    mail = EmailMessage(subject=subject, body=body, to=to, cc=cc, from_email=from_email)
    mail.content_subtype = 'html'
    mail.send()
    

def error_404(request, message=''):
    return render(request, 'error_404.html', {'message':message})

