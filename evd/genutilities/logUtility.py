import logging
from django.conf import settings
from datetime import datetime as dateObj
import os

kLogUtilityFileFolder =  settings.PROJECT_DIR + "/logfiles"

def getTodayLogFileName():
    tDate = dateObj.now()
    return dateObj.strftime(tDate,'%Y-%m-%d')

def isLogFlagOn():
    environmentType = os.getenv('EVD_LOG_ON')
    if environmentType and environmentType == "on":
        return True
    else:
        return False

def isNonProdEnvironment():
    environmentType = os.getenv('EVD_ENVIRONMENT_TYPE')
    if environmentType and environmentType != "prod" and environmentType != "":
        return True
    else:
        return False

def configLoggerSettings():
    if isLogFlagOn():
        try:
            fileName = kLogUtilityFileFolder + "/"+getTodayLogFileName()+".log"
            logging.basicConfig(level=logging.DEBUG,filename=fileName, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
        except:
            pass


configLoggerSettings()


def logExceptionWithFunctionName(functionName, e):
    if isLogFlagOn():
        try:
            message = ""
            if e is None:
                message = " None"
            else:
                message = e.message
                if (message is None) or message == "":
                    message = str(e)
            logging.error(functionName + " "+message)
        except:
            pass

def logException(functionName, message):
    if isLogFlagOn():
        try:
            if message is None:
                message = " None"
            else:
                message = str(message)
            logging.error(functionName + " "+message)
        except:
            pass

def logExceptionWithExceptionobject(functionName, e):
    if isLogFlagOn():
        try:
            msObj = e
            if  e is None:
                msObj = " None"
            logging.error(functionName,msObj)
        except:
            pass


def logInfo(functionName,message):
    if isLogFlagOn():
        try:
            if message is None:
                message = " None"
            else:
                message = str(message)
            logging.info(functionName + " "+message)
        except:
            pass

