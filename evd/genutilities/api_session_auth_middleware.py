from .models import ApiSession
from django.contrib.auth.models import User
import logUtility as logService
import views as utilService
from datetime import datetime as datetimeobj
from student.models import *
import os
from django.shortcuts import render

class mobile_api_auth_middleware:
    def checkBasicAuthVerification(self,request):
        basicAuthKey =  request.META.get("HTTP_AUTHORIZATION")
        return utilService.verifyBasicAuth(basicAuthKey)


    def isStudentAPI(self,request):
        if request.path and  "student/api/v1"  in request.path:
            return True
        return False

    def isNewMobileAPIs(self,request):
        if request.path and  "student/api/v1"  in request.path:
            return True
        if request.path and  "partner/api/v1"  in request.path:
            return True
        return False

    def getGuardianObject(self,guardianId):
        userDoc = None
        try:
            userDoc = Guardian.objects.get(id=guardianId)
        except Exception as e:
            logService.logException("getGuardianObject", e.message)
        return userDoc

    def enableMaintenanceMode(self,request):
        return render(request, 'maintenancewindow.html',{})


    def isMaintainanceMode(self,request):
        maintenanceMode = os.getenv('EVD_MAINTENANCE_MODE')
        if maintenanceMode and maintenanceMode == "on":
            return True
        else:
            return False

    def process_request(self,request):
        if self.isMaintainanceMode(request):
            return self.enableMaintenanceMode(request)

        if request.path and not self.isNewMobileAPIs(request):
            return None
        logService.logInfo("Request", request.path + " " + request.method)
        if request.META is not None:
            sessionId = request.META.get("HTTP_EVD_SESSION_ID")
            isBasicAuthPassed = self.checkBasicAuthVerification(request)
            if isBasicAuthPassed is False:
                request.is_basic_auth_authenticated = False
                if request.user:
                    request.user.is_anonymous = True
                    request.user.is_authenticated = False
                    request.is_basic_auth_authenticated = False
                logService.logException("mobile_api_auth_middleware", "Basic auth failed for "+ request.path)
                return None

            request.is_basic_auth_authenticated = True
            isStudentAPIVar = self.isStudentAPI(request)
            if isStudentAPIVar is True:
                request.guardian = None

            if sessionId is not None:
                #Get session object
                try:
                    curTime = datetimeobj.now()
                    sessionObj = ApiSession.objects.get(session_key=sessionId, status=True,expiry_time__gte=curTime)

                    if isStudentAPIVar and sessionObj.type == "guardian":
                        guardianId = sessionObj.belongs_to
                        if guardianId:
                            guardianObj = self.getGuardianObject(guardianId)
                            if guardianObj:
                                request.guardian = guardianObj
                                request.currentSession = sessionObj
                    else:
                        user = sessionObj.user
                        user.is_anonymous = False
                        user.is_authenticated = True
                        request.user = user
                        request.currentSession = sessionObj

                except ApiSession.DoesNotExist:

                    if request.user:
                        request.user.is_anonymous = True
                        request.user.is_authenticated = False

                except Exception as e:
                    logService.logException("mobile_api_auth_middleware", e.name)
            else:
                if request.user:
                    request.user.is_anonymous = True
                    request.user.is_authenticated = False
        return None

