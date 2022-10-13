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
import genutilities.views as genUtility
import genutilities.logUtility as logService
import math
from datetime import datetime as datetimeObj
from datetime import timedelta as timedeltaObj
import traceback


class QueryExecutorCommand():
    def __init__(self):
        self.conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], \
                                    user=settings.DATABASES['default']['USER'], \
                                    passwd=settings.DATABASES['default']['PASSWORD'], \
                                    db=settings.DATABASES['default']['NAME'], \
                                    charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()


    def createCSVFile(self,header,dataRecords,outputFilePath):
       try:
           path = outputFilePath
           # open the file in the write mode
           f = open(path, 'w')

           # create the csv writer
           writer = csv.writer(f)

           writer.writerow(header)

           # write a row to the csv file
           for data in dataRecords:
               writer.writerow(data)

           # close the file
           f.close()
       except Exception as e:
           print("createCSVFile",e)
           traceback.print_exc()




    def executeQuery(self,queryStr,fieldArray):
        try:

            fieldsArray = fieldArray
            selectQuery = queryStr
            self.cursor.execute(selectQuery)
            dataList = self.cursor.fetchall()
            fieldCount = len(fieldsArray)
            resultData = []
            for eachRecord in dataList:
                eachObject = []
                totalValCount = len(eachRecord)
                for i in range(fieldCount):
                    fieldName = fieldsArray[i]
                    #eachObject[fieldName] = eachRecord[i]
                    dataVal = ""
                    if totalValCount > i:
                        dataVal = eachRecord[i]
                    keyVal = ""
                    if dataVal:
                        try:
                            keyVal = str(dataVal)
                        except:
                            keyVal = ""

                    eachObject.append(keyVal)

                resultData.append(eachObject)
            print("query completed")
            return (fieldsArray,resultData)

        except Exception as e:
            print("executeQuery", e)
            logService.logException("executeQuery function", e.message)
            traceback.print_exc()
            return []


    def getFieldArrayFromString(self,fieldString):
        fieldArray = fieldString.split(',')
        return fieldArray

    def readFileContent(self,fileName):
        try:
            f = open(fileName, 'r')
            dataString = f.read()
            return dataString
        except Exception as e:
            print("Reading file error",e)
            return None

    def runOperation(self):
        try:
           queryFileName = raw_input("Enter the query file name..:")

           queryStr = self.readFileContent(queryFileName)
           if queryStr is None:
               print("Invalid file")
               return

           queryStr = queryStr.replace("\n"," ")
           print("Entered Query: ",queryStr)
           print("Operation started")

           fieldString = raw_input("Enter the Field string in 1 line:")
           fieldArray = self.getFieldArrayFromString(fieldString)
           print("Entered fieldArray",fieldArray)

           outputFilePath = raw_input("Enter the Output file path:")
           print("Entered outputFilePath", outputFilePath)

           fieldsArray,resultData = self.executeQuery(queryStr,fieldArray)
           self.createCSVFile(fieldArray, resultData,outputFilePath)
           print("Operation completed")
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
    # parser.add_option('-t', '--type', default="", help='Student Time table generation')
    # parser.add_option('-i', '--id', default=None, help='Id of an student')
    parser.add_option('-s', '--source', default='dev', help='Source dev/prod')
    (options, args) = parser.parse_args()

    OBJ = QueryExecutorCommand()
    OBJ.main(options)
