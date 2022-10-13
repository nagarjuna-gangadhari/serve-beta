# Create your views here.
import re
import time
import json, ast
import math
import MySQLdb
import simplejson
import os
import traceback
from django.db import connection
from django.contrib import messages
from datetime import datetime
from collections import OrderedDict
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.forms.models import model_to_dict
from django.shortcuts import render
from PIL import Image as PIL
from dateutil.relativedelta import relativedelta
import xlrd
import itertools
from operator import itemgetter
from configs.models import AppreciationReason, Stickers
from django.contrib import messages
from questionbank.forms import HolidaysForm, Add_HolidaysForm, Apply_HolidaysForm
from web.models import *
from .models import *
from questionbank.models import *
import base64, ast
from student.views import createGuardianObjectIfNeeded
from student.models import *
from partner.views import has_pref_role,has_role
import datetime as dt
import dateutil.parser as dparser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from ast import literal_eval
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render as render_response
from django.template import Context
from django.core import mail

from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from web.utils import *
from django.db.models import Count
from configs.models import SettingsGroup
from social_auth.models import UserSocialAuth
from alerts.models import Alerts
from collections import OrderedDict
import thread
import genutilities.uploadDocumentService as docUploadService
from genutilities.views import get_object_or_none, getTimeStampFromDate, has_role_preference
import genutilities.views as genUtility
import student.views as studentApp
import alerts.views as notificationModule

from django.views.generic import View
from django.utils.decorators import method_decorator
from django.db.models import Q, F
import genutilities.logUtility as logService
import csv
import requests
from xlwt import Workbook
from web.views import getAllCenters, get_ongoing_courses, daterange
from web.views import has_mail_receive_accepted, save_user_activity, create_task_for_EVD, weekday_sorter, insert_into_alerts
from web.views import confirm_reject_slot, add_dynamic_session_accept, auto_login_wikividya, create_wikividya_account, make_date_time, make_number_verb, cummulative, transpose, _send_mail
import calendar
from datetime import timedelta

WIKI_BASE_URL = 'http://wikividya.evidyaloka.org/'
WIKI_FAILURE_MESSAGE = 'Failure_wiki'
WIKI_PASS = '123'
WEB_BASE_URL = settings.WEB_BASE_URL
PROVISIONAL_CENTER = "Provisional Center"
PROVISIONAL_KEYWORD = "Provisional"
UNALLOCATED_KEYWORD = "Unallocated"


def updateTransliteration(request,sheet,curr_timestap):
    if sheet:
        sheet_list = []
        count_update_success = 0
        count_update_error = 0
        count_flag = False
        count_flag_error = False
        rejected_list = []
        count = 0
        message=''
        for row_index in range(1, sheet.nrows):
            title = ""
            link = ""
            message = 'No Record updated'
            check_title=True
            try:
                board = sheet.cell(row_index,0).value
                subject = sheet.cell(row_index,1).value
                grade = sheet.cell(row_index,2).value
                lessionNumber = sheet.cell(row_index,3).value
                lessonName = sheet.cell(row_index,4).value
                transliterations = sheet.cell(row_index,5).value
                action = sheet.cell(row_index,6).value
            except:
                board = ''
                subject = ''
                grade = ''
                lessionNumber = ''
                lessonName = ''
                transliterations = ''
                action = ''
            if "\n" in transliterations:
                transliterations=transliterations.replace("\n", " ")
            if "'''" in transliterations:
                transliterations=transliterations.replace("''", "'''\''")
            trns=''
            trns+=" ".join(transliterations.split())
            transliterations=trns
            #action = sheet.cell(row_index,6).value
            if board and subject and grade and lessionNumber and lessonName and transliterations:
                lessonName = '_'.join(lessonName.split())
                "lessonName = lessonName.replace(' ','_')"
                title = str(board)+'_-_'+str(int(grade))+'_-_'+str(subject)+'_::_'+str(lessonName)
                title = title.replace("'", "\\'")
                data = {'title':title,'lessionNumber':str(int(lessionNumber)),'lessonName':lessonName,'transliterations':transliterations,'action':action}
                sheet_list.append(data)
            else:
                title = str(board)+'_-_'+str(grade)+'_-_'+str(subject)+'_::_'+str(lessonName)
                title = title.replace("'", "\\'")
                rejected_list.append({'title':title,'lessionNumber':str(lessionNumber),'lessonName':lessonName,'transliterations':transliterations,'action':action})
        if rejected_list and len(rejected_list)>0:
            count_flag_error = True
            count_update_error += len(rejected_list)
            insert_rejected_data_in_table(request, rejected_list,curr_timestap)
        if sheet_list and len(sheet_list)>0:
            new_sheet_list = []
            final_sheet_list = []
            for new_value in sheet_list:new_sheet_list.append({'title':new_value['title']+'_'+new_value['lessionNumber'],'value':new_value['transliterations'],'action':new_value['action']})      
            new_sheet_list = sorted(new_sheet_list, key=lambda k: k['title']) 
            for key, group in itertools.groupby(new_sheet_list, key=lambda x:x['title']):
                temp = key.rfind("_")
                key = key.replace(" ", "")
                count = len(key)-temp
                key = key.replace(" ", "")[:-count]
                final_sheet_list.append({'title':key,'data':list(group)})
            for data in final_sheet_list: 
                action_data = ''
                if data['title']:
                    count_record = len(data['data'])
                    db = evd_getDB('wikividya')
                    tot_user_cur = db.cursor()
                    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
                    query = "select page_latest,page_id from page where page_title='"+str(data['title'])+"'"
                    dict_cur.execute(query)
                    page_details = dict_cur.fetchall()
                    if page_details and len(page_details)>0:
                        count_flag = True
                        count_update_success += count_record
                    for page in page_details:
                        pageId = page['page_id']
                        page_latest = page['page_latest']
                        query="select * from pagelinks where pl_from="+str(pageId)+" and pl_title='"+str(data['title'])+"' "
                        dict_cur.execute(query)
                        pagelinks = dict_cur.fetchall()
                        if pagelinks and len(pagelinks)>0:
                            query = "update pagelinks set pl_title= '"+str(data['title'])+"' where pl_from= "+str(pageId)
                            dict_cur.execute(query)
                            db.commit()
                        query="select rev_text_id from revision where rev_id="+str(page_latest)
                        dict_cur.execute(query)
                        rev_text_id_obj = dict_cur.fetchall()
                        if rev_text_id_obj and len(rev_text_id_obj)>0:
                            rev_text_id=rev_text_id_obj[0]['rev_text_id']
                            query="select * from text where old_id="+str(rev_text_id)
                            dict_cur.execute(query)
                            text_id_obj = dict_cur.fetchall()
                            if text_id_obj and len(text_id_obj)>0:
                                rev_txt_id=text_id_obj[0]['old_id']
                                old_txt=text_id_obj[0]['old_text']
                                old_txt=str(old_txt)
                                new_trans_list = []
                                if old_txt:
                                    final_list = old_txt.split("\n")
                                    if "=Transliteration=" in final_list or "=Transliterations=" in final_list:
                                        if "=Transliteration=" in final_list:workstream = "=Transliteration="
                                        else:workstream = "=Transliterations="
                                        data_index = final_list.index(workstream)
                                        index_list = get_all_index_list(final_list)
                                        start_index = data_index
                                        index_value = index_list.index(start_index)
                                        end_index = 0
                                        if len(index_list)>=(index_value+1):
                                            end_index = index_list[index_value+1]
                                            my_text = '{| class="wikitable" \n'
                                            for trans in data['data']:
                                                action_data = trans['action']
                                                my_text_list = trans['value'].split('-')
                                                count = 0 
                                                for trans_text in my_text_list:
                                                    if count < len(my_text_list)-1:
                                                        my_text += '|'+trans_text.encode('utf-8')+'|'
                                                        count += 1
                                                    else:
                                                        my_text += '|'+trans_text.encode('utf-8')
                                                my_text += '\n|-\n'
                                            my_text += ' \n |}'
                                            if end_index>0:
                                                if action_data and action_data == 'A' or action_data == 'a' :
                                                    final_list.insert( end_index-1, my_text)
                                                elif action_data and action_data == 'O' or action_data == 'o':
                                                    del final_list[start_index+1:end_index-1]
                                                    final_list.insert( start_index+1, my_text)
                                                else :
                                                    final_list.insert( end_index-1, my_text)
                                            else:
                                                final_list.insert(start_index+1, my_text)
                                        new_text =  '\n'.join(final_list)
                                        new_text = new_text.replace("'", "\\'")
                                        query = "update  text set old_text='"+new_text+"' where old_id="+str(rev_txt_id)
                                        dict_cur.execute(query)
                                        db.commit()
        if count_flag:
            message = str(count_update_success)+ ' records updated successfully '
        if count_flag_error:
            message
            if count_flag: 
                message += ' and '
            else:
                message=''
            message += str(count_update_error)+' records rejected.'
        if not count_flag and not count_flag_error:
            message='File contains no records'
        return message

def insert_rejected_data_in_table(request, rejected_list,curr_timestap):
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user="root",
                        passwd="evd^123",
                        db="wiki_1_26",
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    for rejected_data in rejected_list:
        query="insert into data_exception (page_title,workstream,user_name,upload_date,type) values('%s', '%s', '%s', '%s', '%s')"
        values = (str(rejected_data['title']),simplejson.dumps(rejected_data),request.user.username,curr_timestap,'Trans')
        dict_cur.execute(query%values)
        db.commit()

def bulk_upload(request):
    message = request.GET.get('message','')
    return render(request, "bulk_update_wikividya.html",{'message':message})

def get_bulk_upload(request):
    if request.user.is_superuser:
        actionRadio = request.POST.get('actionRadio')
        action =request.POST.get('method_called')
        curr_time = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
        curr_timestap = ""
        if curr_time:
            curr_timestap += str(curr_time.year)
            if curr_time.month <= 9:
                curr_timestap += "0"
            curr_timestap += str(curr_time.month)
            if curr_time.day <= 9:
                curr_timestap += "0"
            curr_timestap += str(curr_time.day)
            if curr_time.hour <= 9:
                curr_timestap += "0"
            curr_timestap += str(curr_time.hour)
            if curr_time.minute <= 9:
                curr_timestap += "0"
            curr_timestap += str(curr_time.minute)
            if curr_time.second <= 9:
                curr_timestap += "0"
            curr_timestap += str(curr_time.second)
            
        xlsxFlag=False
        insertFlag=False
        rejectFlag=False
        updateFlag=False
        gradeCkeck=False
        
        countforUpdate=0
        countforInsert=0
        countforRejected=0
        message=""
        rejectedMsg=""
        if 'files' in request.FILES:
            file=request.FILES['files']
            file=str(file)
            if file.find(".")!=-1 :
                file=file.split('.')
                if file[1]=='xlsx':
                    xlsxFlag=True
        if xlsxFlag:
            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user="root",
                        passwd="evd^123",
                        db="wiki_1_26",
                        charset="utf8",
                        use_unicode=True)
            tot_user_cur = db.cursor()
            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
            count=0
            input_excel = request.FILES['files']
            book = xlrd.open_workbook(file_contents=input_excel.read())
            sheet = book.sheet_by_index(0)
            if (actionRadio=='updateTransliteration'):
                message =  updateTransliteration(request,sheet,curr_timestap)
                return render(request, "bulk_update_wikividya.html",{"message":message})
            for row_index in range(1, sheet.nrows):
                title = ""
                link = ""
                check_title=True
                try:
                    board = sheet.cell(row_index,0).value
                    subject = sheet.cell(row_index,1).value
                    grade = sheet.cell(row_index,2).value
                    topic = sheet.cell(row_index,4).value
                    lessonPlan = sheet.cell(row_index,5).value
                    A_O_for_lessonPlan = sheet.cell(row_index,6).value
                    textbook = sheet.cell(row_index,7).value
                    A_O_for_textbook = sheet.cell(row_index,8).value
                    vedio = sheet.cell(row_index,9).value
                    A_O_for_vedio = sheet.cell(row_index,10).value
                    image=sheet.cell(row_index,11).value
                    A_O_for_image=sheet.cell(row_index,12).value
                    activities=sheet.cell(row_index,13).value
                    A_O_for_activities = sheet.cell(row_index,14).value
                    additional_aids = sheet.cell(row_index,15).value
                    A_O_for_additional_aids = sheet.cell(row_index,16).value
                    worksheets = sheet.cell(row_index,17).value
                    A_O_for_worksheets = sheet.cell(row_index,18).value
                    assessments=sheet.cell(row_index,19).value
                    A_O_for_assessments=sheet.cell(row_index,20).value
                except:
                    board = ''
                    subject = ''
                    grade = ''
                    topic = ''
                    lessonPlan = ''
                    A_O_for_lessonPlan=''
                    A_O_for_textbook = ''
                    textbook = ''
                    A_O_for_vedio = ''
                    vedio = ''
                    A_O_for_image = ''
                    image=''
                    A_O_for_activities=''
                    activities=''
                    A_O_for_additional_aids = ''
                    additional_aids = ''
                    A_O_for_worksheets = ''
                    worksheets = ''
                    assessments=''
                    A_O_for_assessments=''
                flag = False
                if board and board is not None:
                    title += str(board)
                    flag = True
                else:
                    check_title=False 
                try:
                    float(grade)
                    gradeCkeck = True
                except ValueError:
                    gradeCkeck = False
                if grade and grade is not None and gradeCkeck:
                    if flag:
                        title += "_-_"
                    grade = int(grade)
                    title += str(grade)
                    flag = True
                else:
                    check_title=False
                if subject and subject is not None:
                    if flag:
                        title += "_-_"
                    title += str(subject)
                    flag = True
                else:
                    check_title=False
                if topic and topic is not None:
                    if flag:
                        title += "_::_"
                    topic = topic.replace(u'\xa0', u' ')
                    topic=str(topic)
                    if topic.find(" ") != -1 :
                        topic = topic.replace(" ", "_")
                    title += str(topic)
                else:
                    check_title=False
                title=str(title)
                if title.find("'")!=-1 :
                    title=title.replace("'", "\\'")
                link=str(link)
                check_Action=False
                if str(A_O_for_lessonPlan).lower()=='a' or str(A_O_for_lessonPlan).lower()=='o':
                    check_Action=True
                if str(A_O_for_textbook).lower()=='a' or  str(A_O_for_textbook).lower()=='o':
                    check_Action=True
                if str(A_O_for_vedio).lower()=='a' or str(A_O_for_vedio).lower()=='o':
                    check_Action=True
                if str(A_O_for_image).lower()=='a' or str(A_O_for_image).lower()=='o':
                    check_Action=True
                if str(A_O_for_activities).lower()=='a' or str(A_O_for_activities).lower()=='o':
                    check_Action=True
                if str(A_O_for_additional_aids).lower()=='a'or str(A_O_for_additional_aids).lower()=='o':
                    check_Action=True
                if str(A_O_for_worksheets).lower()=='a' or str(A_O_for_worksheets).lower()=='o':
                    check_Action=True
                if str(A_O_for_assessments).lower()=='a' or str(A_O_for_assessments).lower()=='o':
                    check_Action=True      
                excel_sheet_for_update=[lessonPlan,A_O_for_lessonPlan,textbook,A_O_for_textbook,vedio,A_O_for_vedio,image,A_O_for_image,activities,A_O_for_activities,additional_aids,A_O_for_additional_aids,worksheets,A_O_for_worksheets,assessments,A_O_for_assessments]
                if title and check_title and check_Action:
                    query = "SELECT page_latest , page_id FROM page  where page_title='"+title+"'"
                    dict_cur.execute(query)
                    page_latest_list = dict_cur.fetchall()
                    if page_latest_list and len(page_latest_list)>0:
                        for data in page_latest_list:
                            if actionRadio and actionRadio == 'update' or actionRadio=='insertorupdate':
                                pageId=data['page_id']
                                dic_obj=update_data_in_table(title,data['page_latest'],countforUpdate,updateFlag,pageId,excel_sheet_for_update)
                                countforUpdate=dic_obj['returnCount']
                                updateFlag=dic_obj['updateFlag']
                            else:
                                count+=1
                    else:
                        if actionRadio=='insertorupdate' or actionRadio=='insert':
                            try:
                                message="insert"
                                # dic_obj=insert_data_in_table(title, link,countforInsert,insertFlag,curr_timestap,request.user.id,request.user.username)
                                #countforInsert=dic_obj['returnCount']
                                #insertFlag=dic_obj['insertFlag']
                            except:
                                message="Error"
                        else:
                            count+=1
                else:
                    jsondata={"lessonPlan":urllib.quote(lessonPlan.encode('utf8')),"A_O_for_lessonPlan":A_O_for_lessonPlan,"textbook":urllib.quote(textbook.encode('utf8')),"A_O_for_textbook":A_O_for_textbook,"vedio":urllib.quote(vedio.encode('utf8')),"A_O_for_vedio":A_O_for_vedio,"image":urllib.quote(image.encode('utf8')),"A_O_for_image":A_O_for_image,"activities":urllib.quote(activities.encode('utf8')),"A_O_for_activities":A_O_for_activities,"additional_aids":urllib.quote(additional_aids.encode('utf8')),"A_O_for_additional_aids":A_O_for_additional_aids,"worksheets":urllib.quote(worksheets.encode('utf8')),"A_O_for_worksheets":A_O_for_worksheets,"assessments":assessments,"A_O_for_assessments":A_O_for_assessments}
                    query="insert into data_exception (page_title,workstream,user_name,upload_date,type) values('%s', '%s', '%s', '%s', '%s')"
                    values = (str(title),simplejson.dumps(jsondata),request.user.username,curr_timestap,'All')
                    dict_cur.execute(query%values)
                    db.commit()
                    countforRejected+=1
                    rejectFlag=True
            if actionRadio=='insert':
                message=poc_message_display(insertFlag,False,rejectFlag,countforRejected,0,countforInsert,actionRadio,count)  
            elif actionRadio == 'update': 
                message=poc_message_display(False,updateFlag,rejectFlag,countforRejected,countforUpdate,0,actionRadio,count) 
            else: 
                message=poc_message_display(insertFlag,updateFlag,rejectFlag,countforRejected,countforUpdate,countforInsert,actionRadio,count)   
            db.close()
            dict_cur.close()
            tot_user_cur.close()
            return redirect('/v2/bulk_upload/?message='+message)
        else:
            if action:
                message="Please,Upload Valid File"
            return redirect('/v2/bulk_upload/?message='+message)
        
def poc_message_display(insertFlag,updateFlag,rejectFlag,countforRejected,countforUpdate,countforInsert,actionRadio,count):  
    message=''
    if insertFlag and updateFlag:
        if rejectFlag:
            message+=str(countforRejected)+' record(s) Rejected ,'
        message+= str(countforUpdate)+" record(s) Updated successfully and "+str(countforInsert)+" record(s) Uploaded successfully"
    elif insertFlag:
        if rejectFlag:
            message+=str(countforRejected)+' record(s) Rejected and '
        message+= str(countforInsert)+" record(s) Uploaded successfully "
    elif updateFlag:
        if rejectFlag:
            message+=str(countforRejected)+' record(s) Rejected and '
        message+= str(countforUpdate)+" record(s) Updated successfully"
    elif rejectFlag:
        if actionRadio=='insert' and count>0:
            message=str(countforRejected)+' record(s) Rejected and '+str(count)+' record(s) already exist in a Database'
        elif actionRadio=='update' and count>0:
            message=str(countforRejected)+' record(s) Rejected and '+str(count)+' record(s) Not Found in Database'
        else:
            message='All records Rejected'
    else:
        if actionRadio=='insert' and count>0:
            message='These records already exist in a Database'
        elif actionRadio=='update' and count>0:
            message='These records Not Found in Database'
        else:
            message='File contains no record'  
       
    return  message 
     
def update_data_in_table(title,page_latest,countforUpdate,updateFlag,pageId,excel_sheet_for_update):
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user="root",
                        passwd="evd^123",
                        db="wiki_1_26",
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    if pageId:
            query="select * from pagelinks where pl_from="+str(pageId)+" and pl_title='"+str(title)+"' "
            dict_cur.execute(query)
            pagelinks = dict_cur.fetchall()
            if len(pagelinks)>0:
                query = "update pagelinks set pl_title= '"+str(title)+"' where pl_from= "+str(pageId)
                dict_cur.execute(query)
                db.commit()
    if page_latest:
        query="select rev_text_id from revision where rev_id="+str(page_latest)
        dict_cur.execute(query)
        rev_text_id_obj = dict_cur.fetchall()
        if len(rev_text_id_obj)>0:
            rev_text_id=rev_text_id_obj[0]['rev_text_id']
            query="select * from text where old_id="+str(rev_text_id)
            dict_cur.execute(query)
            text_id_obj = dict_cur.fetchall()
            if len(text_id_obj)>0:
                rev_txt_id=text_id_obj[0]['old_id']
                old_txt=text_id_obj[0]['old_text']
                old_txt=str(old_txt)
                final_data = ''
                old_txt_line_wise =old_txt.split('\n')
                final_list = old_txt_line_wise
                is_updated = False
                if "=Lesson Plans=" in final_list or "=Lesson Plan=" in final_list:
                    if "=Lesson Plans=" in final_list:workstream =  "=Lesson Plans="
                    else:workstream =  "=Lesson Plan="
                    data = '\n'+str(excel_sheet_for_update[0])
                    data_list = data.split("\n")
                    new_data_list = []
                    for new_data in data_list:
                        if ''!=new_data: new_data += '\n'
                        new_data_list.append(new_data)
                    if new_data_list:data = '\n'.join(new_data_list)
                    final_list_data = get_update_bulk_list(workstream, excel_sheet_for_update[1], data, final_list)
                    final_list=final_list_data['final_list']
                    invalid_action=final_list_data['invalid_action']
                    if not invalid_action :
                        is_updated = True
               
                if "=Textbooks=" in final_list or "=Textbook=" in final_list:
                    if "=Textbooks=" in final_list:workstream =  "=Textbooks="
                    else:workstream =  "=Textbook="
                    data = '\n'+str(excel_sheet_for_update[2])
                    data_list = data.split("\n")
                    new_data_list = []
                    for new_data in data_list:
                        if ''!=new_data: new_data += '\n'
                        new_data_list.append(new_data)
                    if new_data_list:data = '\n'.join(new_data_list)
                    final_list_data = get_update_bulk_list(workstream, excel_sheet_for_update[3], data, final_list)
                    final_list=final_list_data['final_list']
                    invalid_action=final_list_data['invalid_action']
                    if not invalid_action :
                        is_updated = True
               
                if "=Videos=" in final_list:
                    data = '\n'+str(excel_sheet_for_update[4])
                    data_list = data.split("\n")
                    new_data_list = []
                    for new_data in data_list:
                        if ''!=new_data: new_data += '\n'
                        new_data_list.append(new_data)
                    if new_data_list:data = '\n'.join(new_data_list)
                    final_list_data = get_update_bulk_list("=Videos=", excel_sheet_for_update[5], data, final_list)
                    final_list=final_list_data['final_list']
                    invalid_action=final_list_data['invalid_action']
                    if not invalid_action :
                        is_updated = True
               
                if "=Images=" in final_list:
                    data = '\n'+str(excel_sheet_for_update[6])
                    data_list = data.split("\n")
                    new_data_list = []
                    for new_data in data_list:
                        if ''!=new_data: new_data += '\n'
                        new_data_list.append(new_data)
                    if new_data_list:data = '\n'.join(new_data_list)
                    final_list_data = get_update_bulk_list("=Images=", excel_sheet_for_update[7], data, final_list)
                    final_list=final_list_data['final_list']
                    invalid_action=final_list_data['invalid_action']
                    if not invalid_action :
                        is_updated = True
                    
                if "=Activities=" in final_list:
                    data = '\n'+str(excel_sheet_for_update[8])
                    data_list = data.split("\n")
                    new_data_list = []
                    for new_data in data_list:
                        if ''!=new_data: new_data += '\n'
                        new_data_list.append(new_data)
                    if new_data_list:data = '\n'.join(new_data_list)
                    final_list_data = get_update_bulk_list("=Activities=", excel_sheet_for_update[9], data, final_list)
                    final_list=final_list_data['final_list']
                    invalid_action=final_list_data['invalid_action']
                    if not invalid_action :
                        is_updated = True
                
                if "=Additional Aids=" in final_list:
                    data = '\n'+str(excel_sheet_for_update[10])
                    data_list = data.split("\n")
                    new_data_list = []
                    for new_data in data_list:
                        if ''!=new_data: new_data += '\n'
                        new_data_list.append(new_data)
                    if new_data_list:data = '\n'.join(new_data_list)
                    final_list_data = get_update_bulk_list("=Additional Aids=", excel_sheet_for_update[11], data, final_list)
                    final_list=final_list_data['final_list']
                    invalid_action=final_list_data['invalid_action']
                    if not invalid_action :
                        is_updated = True
                    
                if "=Worksheets=" in final_list:
                    data = '\n'+str(excel_sheet_for_update[12])
                    data_list = data.split("\n")
                    new_data_list = []
                    for new_data in data_list:
                        if ''!=new_data: new_data += '\n'
                        new_data_list.append(new_data)
                    if new_data_list:data = '\n'.join(new_data_list)
                    final_list_data = get_update_bulk_list("=Worksheets=", excel_sheet_for_update[13], data, final_list)
                    final_list=final_list_data['final_list']
                    invalid_action=final_list_data['invalid_action']
                    if not invalid_action :
                        is_updated = True    
                if "=Assessments="in final_list:
                    data= '\n'+str(excel_sheet_for_update[14]) 
                    data_list = data.split("\n")
                    new_data_list=[]
                    for new_data in data_list:
                        if ''!=new_data: new_data += '\n'
                        new_data_list.append(new_data)
                    if new_data_list:data = '\n'.join(new_data_list) 
                    final_list_data = get_update_bulk_list("=Assessments=", excel_sheet_for_update[15], data, final_list)   
                    final_list=final_list_data['final_list']
                    invalid_action=final_list_data['invalid_action']
                    if not invalid_action :
                        is_updated = True 
                    
                    
                    
                                        
                if final_list and is_updated and rev_txt_id:
                    final_data = '\n'.join(final_list)
                    final_data = final_data.replace("'", "\\'")
                    query = "update  text set old_text='"+final_data+"' where old_id="+str(rev_txt_id)
                    dict_cur.execute(query)
                    db.commit()
                    countforUpdate+=1
                    updateFlag=True
    dic_record={"returnCount":countforUpdate,"updateFlag":updateFlag}
    db.close()
    dict_cur.close()
    tot_user_cur.close()
    return dic_record

def get_update_bulk_list(workstream, action, data, final_list):
    action = str(action).lower()
    data_index = final_list.index(workstream)
    index_list = get_all_index_list(final_list)
    start_index = data_index
    index_value = index_list.index(start_index)
    end_index = 0
    invalid_action=False
    if len(index_list)>=(index_value+1):
        end_index = index_list[index_value+1]
        if action=='a':
            if end_index>0:
                final_list.insert( end_index-1, data.encode('utf-8'))
            else:
                final_list.insert(start_index+1, data.encode('utf-8'))
        elif action=='o':
            end = 0
            if end_index>0:
                end = end_index-1
            else:end = len(final_list)-1
            del final_list[start_index+1:end]
            final_list.insert(start_index+1, data.encode('utf-8'))
        else:
            invalid_action=True
        final_list_data={'final_list':final_list,'invalid_action':invalid_action}
    return final_list_data

def get_all_index_list(final_list):
    index_list = []
    count = 0 
    for data in final_list:
        if data=='=Lesson Plans=' or data=='=Lesson Plan=':
            index_list.append(count)
        if data=='=Textbooks=' or data=='=Textbook=':
            index_list.append(count)
        if data=='=Transliterations=' or data == '=Transliteration=':
            index_list.append(count)
        if data=='=Videos=':
            index_list.append(count)
        if data=='=Images=':
            index_list.append(count)
        if data=='=Activities=':
            index_list.append(count)
        if data=='=Worksheets=':
            index_list.append(count)
        if data=='=Assessments=':
            index_list.append(count)
        if data=='=Powerpoint Slides=':
            index_list.append(count)
        if data=='=Additional Aids=':
            index_list.append(count)
        if data=='=Assessments=':
            index_list.append(count)    
        count += 1
    return index_list

   
                       
@csrf_exempt       
def get_uploaded_data(request):
    if request.user.is_authenticated:
        flag=request.GET.get('flag')
        if flag:
            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user="root",
                        passwd="evd^123",
                        db="wiki_1_26",
                        charset="utf8",
                        use_unicode=True)
            tot_user_cur = db.cursor()
            data_exception_list =  trans_exception_list = []
            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query="select * from data_exception where type='All' order by upload_date desc"
            try:
                dict_cur.execute(query)
                allData = dict_cur.fetchall()
            except:
                allData =[]
            query="select * from data_exception where type='Trans' order by upload_date desc"   
            try:
                dict_cur.execute(query)
                allTransData = dict_cur.fetchall()
            except:
                allTransData =[]
            tot_user_cur.close()
            message1=''
            message2=''
            if len(allData)>0:
                for obj in allData:
                    workstream= obj['workstream']
                    workstream=json.loads(workstream)
                    jsondata={"lessonPlan":workstream['lessonPlan'],"A_O_for_lessonPlan":workstream['A_O_for_lessonPlan'],"textbook":workstream['textbook'],"A_O_for_textbook":workstream['A_O_for_textbook'],"vedio":workstream['vedio'],"A_O_for_vedio":workstream['A_O_for_vedio'],"image":workstream['image'],"A_O_for_image":workstream['A_O_for_image'],"activities":workstream['activities'],"A_O_for_activities":workstream['A_O_for_activities'],"additional_aids":workstream['additional_aids'],"A_O_for_additional_aids":workstream['A_O_for_additional_aids'],"worksheets":workstream['worksheets'],"A_O_for_worksheets":workstream['A_O_for_worksheets']}
                    jsonFormate={'id':obj['id'],'page_title':obj['page_title'],'workstream':jsondata,'user_name':obj['user_name'],'upload_date':obj['upload_date']}
                    data_exception_list.append(jsonFormate)
            else:
                message1='No data available.'
            if len(allTransData)>0:
                for obj in allTransData:
                    workstream= obj['workstream']
                    workstream=json.loads(workstream)
                    jsondata = ""
                    if workstream:
                        var = workstream['transliterations']+""
                        splitedData = var.split('-')
                        transliterations_data = ''
                        for data in splitedData:
                            if bool(re.search(r'\d', data)):
                                dataEncoded = data.replace('u', '\\u')
                                dataEncoded_formate = 'u\''+dataEncoded+'\''
                                if transliterations_data:
                                    transliterations_data+="-"+ literal_eval(dataEncoded_formate)
                                else:
                                    transliterations_data = literal_eval(dataEncoded_formate)
                            else:
                                if transliterations_data:
                                    transliterations_data+="-"+data
                                else:
                                    transliterations_data = data
                        jsondata={"lessionNumber":workstream['lessionNumber'],"transliterations":transliterations_data,"lessonName":workstream['lessonName'],"title":workstream['title']}
                        
                    jsonFormate={'id':obj['id'],'page_title':obj['page_title'],'workstream':jsondata,'user_name':obj['user_name'],'upload_date':obj['upload_date']}
                    trans_exception_list.append(jsonFormate)
            else:
                message2='No data available.'
            json_list = {'data_exception_list':data_exception_list,'trans_exception_list':trans_exception_list,"message1":message1,"message2":message2}
            return HttpResponse(simplejson.dumps(json_list),mimetype='application/json') 

def provisional_demand_offerings_table_parser(course_id):
    provisional_offerings = Offering.objects.filter(course_id=course_id, status=PROVISIONAL_KEYWORD).values_list("id", flat=True)
    total_count = len(provisional_offerings)
    pds = ProvisionalDemandslot.objects.filter(Q(offering_id__in=provisional_offerings)).count()
    pds = pds//2
    return (total_count - pds, pds)


def checkValidOfferingForFilters(platform, sel_states, sel_days, sel_langs, sel_times, offering) :
    if platform:
        if len(sel_states) == 0:
            sel_states = Demandslot.objects.values_list('center__state',flat=True).distinct()
    if len(sel_days)==0:
        sel_days =  Demandslot.objects.values_list('day',flat=True).distinct()
    if len(sel_langs)==0:
        sel_langs = Demandslot.objects.values_list('center__language',flat=True).distinct()
        
    if platform:
        if offering:
            return set(Demandslot.objects.filter( Q(day__in=sel_days) & Q(center__language__in=sel_langs) & Q(center__state__in=sel_states) & Q(start_time__gte=sel_times[0]) & Q(end_time__lte=sel_times[1]) & Q(offering_id=offering.id)).values_list('center_id',flat=True))
        else:
            return set(Demandslot.objects.filter( Q(day__in=sel_days) & Q(center__language__in=sel_langs) & Q(center__state__in=sel_states) & Q(start_time__gte=sel_times[0]) & Q(end_time__lte=sel_times[1])).values_list('center_id',flat=True))
    else:
        if offering:
            return set(Demandslot.objects.filter( Q(day__in=sel_days) & Q(center__language__in=sel_langs) & Q(start_time__gte=sel_times[0]) & Q(end_time__lte=sel_times[1]) & Q(offering_id=offering.id)).values_list('center_id',flat=True))
        else:
            return set(Demandslot.objects.filter( Q(day__in=sel_days) & Q(center__language__in=sel_langs) & Q(start_time__gte=sel_times[0]) & Q(end_time__lte=sel_times[1])).values_list('center_id',flat=True))
    return None
    


def confirm_center_slot(demandslot_id,courseId,center_name):
    if demandslot_id and courseId and center_name:
        today_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
        today_date = today_date.strftime("%d-%m-%Y")
        today_date = datetime.datetime.strptime(today_date.strip(), "%d-%m-%Y")
        center_list=[]
        slotIds=[]
        slot_list=[]
        demand_centers=[]
        days=[]
        start_times=[]
        end_times=[]
        """demandslot_id=request.GET.get('demandslot_id','')
        courseId=request.GET.get('courseId','')
        center_name = request.GET.get('center_name','')"""
        center_id_list = []
        if demandslot_id:
            demandslot_id=str(demandslot_id)
            day_time_list=demandslot_id.split(',')
            for day_time in day_time_list:
                slot=str(day_time).split(' ')
                slot_list.append(slot)
            centerslists=[]
            center_lists=[]
            final_centerList = []
            list_center = []
            for i in range(0,len(slot_list)):
                day=slot_list[i][0]
                days.append(day)
                s_time=slot_list[i][1]+" "+slot_list[i][2]
                e_time=slot_list[i][4]+" "+slot_list[i][5]
                s_time=dparser.parse(s_time)
                e_time=dparser.parse(e_time)
                s_time=s_time.strftime('%H:%M')
                e_time=e_time.strftime('%H:%M')
                start_times.append(s_time)
                end_times.append(e_time)
                if center_name and center_name != 'All' :
                    center_id = Center.objects.values('id').filter(name=center_name)
                    for centerId in center_id :
                        center_id_list.append(centerId['id'])
                    if center_id_list:
                        center_lists = center_id_list
                else :
                    if centerslists:
                        center_lists=Demandslot.objects.filter(Q(day=days[i],start_time=start_times[i],end_time=end_times[i]),center_id__in=centerslists,status='Unallocated').values_list('center_id',flat=True).distinct()
                    else:
                        center_lists = Demandslot.objects.filter(Q(day=days[i],start_time=start_times[i],end_time=end_times[i]),status='Unallocated').values_list('center_id',flat=True).distinct()
                for id in center_lists:
                    offeringIds=Offering.objects.filter((Q(center_id=id) & Q(course_id=courseId) & Q(end_date__gt=today_date) )& (Q(status='pending') | Q(status=PROVISIONAL_KEYWORD) |(Q(status='running')& Q(active_teacher_id=None)))).values_list('id',flat=True)
                    if offeringIds:centerslists.append(id)
            for center in centerslists:
                if not list_center:
                    list_center.append(center)
                else :
                    if center not in list_center:
                        list_center.append(center)
                    else:
                        final_centerList.append(center)
            if final_centerList:
                centers=Center.objects.filter(id__in=final_centerList).distinct()
            else:
                centers=Center.objects.filter(id__in=list_center).distinct()
            """for list in centers:
                jsondata={"id":list.id,"center_name":list.name}
                demand_centers.append(jsondata)"""
        return centers




def send_email_thread(subject, message, recipients, from_email, cc):
    msg = EmailMessage(subject, message, to=recipients, from_email=from_email, cc=cc)
    msg.send()


def create_task_thread(request, dueDate, comment, category, subject, assign_to, login_user):
    create_task_for_EVD(request, dueDate, comment, category, subject, 'New Task has been Assigned to you.', assign_to,
                        login_user, subject, login_user)


#@login_required
def release_demand(request):
    platform = request.POST.get('platform', '')
    center = request.POST.get('center','')
    slot = request.POST.get('slot','')
    flag = request.POST.get('flag','')
    is_provisional_demand = request.POST.get('provisional', False)
    is_provisional_demand = False if is_provisional_demand == 'False' or is_provisional_demand == 'false' else True

    current_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
    userObj = None
    if request.user.is_authenticated():
        userObj = request.user

    if not flag:
        slot = request.GET.get('slot','')
        center = request.GET.get('center','')
        teacher = request.GET.get('teacher','')
        flag = request.GET.get('flag','')
        if userObj == None:
            userObj = User.objects.get(pk=teacher)
            
    if flag == 'true':
        if is_provisional_demand:
            user_slots = ProvisionalDemandslot.objects.filter(user_id=userObj.id)
        else:
            user_slots = Demandslot.objects.filter(user_id=userObj.id,status='Allocated')

        if len(user_slots)==0:
            return redirect('/myevidyaloka/?demandRelease=false')
    # else:
    #     if is_provisional_demand:
    #         user_slots = ProvisionalDemandslot.objects.filter(user_id=userObj.id)
    #     else:
    #         user_slots = Demandslot.objects.filter(user_id=userObj.id, status='Booked')

    resp = release_slots(userObj, is_provisional_demand, str(center))
    if platform:
        centr = {}
        if resp==True:
            save_user_activity(request,'Previous Release Slots:'+str(center)+','+slot,'Action')
            centr['status'] = 200
            centr['message']  = 'success'
            centr['data'] = 'All your previous slots are released..'
        else:
            centr['status'] = 404
            centr['message']  = 'failed'
            centr['data'] = 'Some Error Occurred!.. Please try Again.'
        return HttpResponse(json.dumps(centr), content_type='application/json')

    else:
        if resp==True:
            centerObj = ''
            dc_email = ''
            user_name = ''
            dc_user_id = None
            dc=''
            try:
                centerObj = Center.objects.get(name=center)
                center_name = centerObj.name
            except:
                centerObj = ''
            if centerObj:
                if not is_provisional_demand and centerObj.delivery_coordinator:
                    dc = centerObj.delivery_coordinator
                    if dc:
                        dc_email = dc.email
                        dc_user_id = dc.id
                            
                if userObj.first_name:
                    user_name = str(userObj.first_name)+' '+str(userObj.last_name)
                else:
                    user_name = userObj.username
            if not is_provisional_demand:
                vol_cor = User.objects.get(pk=19064)
            ca=''
            try:
                ca=centerObj.admin
            except:
                pass

            assignTo=None
            if dc!=None:
                assignTo=dc
            else:
                assignTo=ca
            if flag == 'true':
                if request.user.is_authenticated():
                    save_user_activity(request,'Previous Release Slots:'+str(center)+','+slot,'Action')
                to = [userObj.email]
                from_email = settings.DEFAULT_FROM_EMAIL
                cc = [dc_email]
                subject = 'Your booked slots in '+str(center) +' are released'
                ctx = {'user':user_name,'center_name':center,'msg':True}
                message = get_template('mail/auto_release_slot.txt').render(Context(ctx))
                msg = EmailMessage(subject, message, to=to, from_email=from_email,cc=cc)
                msg.content_subtype = 'html'
                msg.send()
                if not is_provisional_demand:
                    demand_tasks = Task.objects.filter(assignedTo = vol_cor,performedOn_userId = userObj.id,subject='Your allocation of the selected course is Confirmed').order_by('-taskCreatedDate')
                    if len(demand_tasks)>0:
                        Task.objects.filter(id=demand_tasks[0].id).update(taskStatus = 'Closed',taskUpdatedDate = current_date)

                return redirect('/myevidyaloka/?slot='+slot+'&center='+center)
            else:
                save_user_activity(request,'Previous Release Slots:'+str(center)+','+slot,'Action')
                demand_tasks = Task.objects.filter(assignedTo = assignTo,performedOn_userId = userObj.id,taskStatus='Open').order_by('-taskCreatedDate')
                if len(demand_tasks)>0:
                    if request.user.first_name:
                        commentNew = 'Rejected by ' + str(request.user.first_name) + ' ' + str(request.user.last_name) + " :: " + str(
                        request.user.id)
                    Task.objects.filter(id=demand_tasks[0].id).update(taskStatus = 'Closed',comment=commentNew,
                                                              subject='Your selection of course is Not Confirmed',taskUpdatedDate = current_date)
                return HttpResponse('All your previous slots are released..')
        else:
            return HttpResponse('Some Error Occurred!.. Please try Again.')


def release_slots(user, is_provisional_demand, center_name):
    status = True
    if is_provisional_demand:
        center_id = (Center.objects.get(name=center_name)).id
        pds = ProvisionalDemandslot.objects.filter(center_id=center_id, user_id=user.id).values_list('id')
        for each in pds:
            ProvisionalDemandslot.objects.get(pk=each[0]).delete()
    else:
        user_slots = Demandslot.objects.filter(user_id=user.id)
        for ent in user_slots:
            ent.offering_id = None
            ent.user_id = None
            ent.status = 'Unallocated'
            ent.date_booked = None
            try:
                ent.save()
            except Exception as exp:
                status = status and False
    return status


@csrf_exempt
def get_demandslots(request):
    course_id = request.GET.get('course_id','')
    center_list = []
    timerange = request.GET.get('timerange','')
    timerange1 = request.GET.get('timerange1','')
    days_list =  request.GET.get('days_list','')
    offering_start_month =  request.GET.get('offering_start_month','')
    offering_start_year =  request.GET.get('offering_start_year','')

    days_list = days_list.split(",")
    center_name = request.GET.get('center_name','')
    sel_lang = request.GET.get('sel_lang','')
    backfill = request.GET.get('backfill','')
    is_provisional = request.GET.get('provisional','')
    is_provisional = False if is_provisional == 'false' or is_provisional == 'False' else True

    status_filter = {}
    if backfill == 'true':
       status_filter['status'] = 'running'
       status_filter ['active_teacher_id'] = None
    elif is_provisional:
        status_filter['status'] = PROVISIONAL_KEYWORD
    else:
        status_filter['status'] = 'pending'

    today_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
    today_date = today_date.strftime("%d-%m-%Y")
    today_date = datetime.datetime.strptime(today_date.strip(), "%d-%m-%Y")

    center_id_list = []
    try:
        center_obj = Center.objects.get(name = center_name)
        user_number = UserProfile.objects.get(user_id = center_obj.delivery_coordinator_id)
        phone = user_number.phone
    except:
        center_obj = None
        phone = ""
    if course_id:
        course = Course.objects.get(pk = course_id)
        if course:
            grouped_slots = []
            booked_offering = Demandslot.objects.values_list('offering_id', flat = True).filter(status = 'Booked').distinct()
            if is_provisional:
                booked_offering = ProvisionalDemandslot.objects.values_list('offering_id', flat=True).distinct()

            #Filter center id from offering based on condition .
            center_ids = Offering.objects.values_list('center_id',flat = True).filter(( Q(start_date__month = offering_start_month) &
                         Q(course = course) & Q(end_date__gt = today_date))).filter(
                         **status_filter).exclude(id__in = booked_offering, center__status = 'Closed')

            if not backfill:
                center_ids = Offering.objects.values_list('center_id', flat=True).filter(
                    (Q(start_date__month=offering_start_month) &
                     Q(course=course) & Q(end_date__gt=today_date))).filter(**status_filter).exclude(
                    id__in=booked_offering, center__status='Closed')

            #Filter center id from Demand slot based on condition .
            filtered_center_ids = set(Demandslot.objects.filter(center_id__in = center_ids,start_time__gte = timerange+':00' , center__language=sel_lang,
                                  end_time__lte=timerange1+':00', status='Unallocated').values_list('center_id',flat=True))

            centers = Center.objects.filter(id__in = filtered_center_ids)
            for center in centers:
                center_list.append(center.name)
                
            if center_obj:
                center_id_list.append(center_obj.id)
                filtered_center_ids = set(Demandslot.objects.filter(center_id__in = center_id_list,start_time__gte = timerange+':00',
                                      end_time__lte = timerange1+':00', status = 'Unallocated').values_list('center_id',flat = True))
                
            if filtered_center_ids:
                offering_manage_slot_ids = Demandslot.objects.values_list('id',flat = True).filter(center_id__in = filtered_center_ids,
                                               start_time__gte = timerange+':00',end_time__lte = timerange1+':00',
                                               status = 'Unallocated',offering__course = course).exclude(offering = None)

                bounded_offering = Offering.objects.filter(( Q(start_date__month = offering_start_month) &
                         Q(course = course) & Q(end_date__gt = today_date))).filter(
                         **status_filter).exclude(id__in = booked_offering,center__status = 'Closed')

                if center_obj  :    
                    center_demand = Demandslot.objects.filter(center_id__in = filtered_center_ids, start_time__gte = timerange+':00',
                                    end_time__lte = timerange1+':00', status = 'Unallocated')
                    if offering_manage_slot_ids:
                        center_demand = center_demand.filter(offering = bounded_offering.filter(center = center_obj))
                    else:
                        center_demand = Demandslot.objects.filter(center_id__in = filtered_center_ids, start_time__gte = timerange+':00',
                                    end_time__lte = timerange1+':00', status = 'Unallocated', offering=None)
                else:
                    center_demand = Demandslot.objects.filter(center_id__in = filtered_center_ids, start_time__gte = timerange+':00', 
                                    end_time__lte = timerange1+':00', status = 'Unallocated')
                    bounded_center = set(center_demand.values_list('center_id',flat=True).exclude(offering = None))
                    bounded_center_slots = center_demand.filter(offering = None,center_id__in = bounded_center)

                    if len(filtered_center_ids)>1:
                        center_demand = center_demand.filter(Q(offering__course = course)|Q(offering = None)).exclude(id__in = bounded_center_slots)
                    elif offering_manage_slot_ids: 
                        center_demand = center_demand.filter(offering = bounded_offering.filter(center_id__in = bounded_center))
                    else:
                        center_demand = center_demand.filter(offering = None,center_id__in=filtered_center_ids)
                    
                if len(days_list) == 1 :
                    days_list = set(center_demand.values_list('day',flat=True).distinct())
                    
                if days_list:
                    days_list = weekday_sorter(days_list)
                    all_slots=[]
                    for ent in days_list:
                        temp_buffer = center_demand.filter(day=ent).values_list('day','start_time','end_time')
                        entx = [(x[0],x[1].strftime("%I:%M %p"),x[2].strftime("%I:%M %p")) for x in sorted(set(temp_buffer))]
                        all_slots.append(entx)
                    for slots in all_slots:
                        grouped_slots.append(slots)

        jsondata={'grouped_slots':grouped_slots,"centers":center_list,"center_name":center_name,'phone':phone} 
        return HttpResponse(simplejson.dumps(jsondata),mimetype='application/json')


@csrf_exempt
def updateRoleSupport(request):
    username = request.GET.get('username','')
    if username:
        user = User.objects.get(pk=User.objects.values_list('id',flat=True).filter(email=username)[0])
        userp = user.userprofile
        try:
            userp.pref_roles.clear()
            role = Role.objects.get(name = 'support')
            if role:
                userp.pref_roles.add(role)
            user.save()
            userp.save()
        except Exception as e: pass
    return HttpResponse('Ok')

def content_lookup(request):
    if request.user.id == None:
        return HttpResponseRedirect("/?next=/myevidyaloka/&show_popup=True/")
    if request.user.is_authenticated():
        is_authenticated = True
    else:
        is_authenticated = False
    course_id = request.GET.get('course_id','')
    topic_titles = []
    workstream = []
    if course_id:
        course = Course.objects.get(pk=course_id)
        pref_subject = course.subject
        pref_board = course.board_name
        pref_grade = course.grade
        topicDetails = TopicDetails.objects.filter(topic__course_id_id=course_id,status='Not Started',topic__status = "Not Started").distinct()
        for topic in topicDetails:
            topic_titles.append(topic.topic.title) 
            workstream.append(topic.attribute.types)
    return render_to_response('contentLookup.html',{"topic_titles": sorted(set(topic_titles)),'course_id':course_id,'pref_board':pref_board,'pref_grade':pref_grade,'pref_subject':pref_subject,'is_authenticated':is_authenticated,'workStream':sorted(set(workstream))},context_instance=RequestContext(request))
    
def get_content_lookup(request):
    sel_grades = request.POST.get('sel_grades','')
    sel_subjects = request.POST.get('sel_subjects','')
    sel_boards = request.POST.get('sel_boards' ,'')
    course_id = request.POST.get('course_id','')
    topics = json.loads(request.POST.get('topics','[]'))
    workStream = json.loads(request.POST.get('workStream','[]'))
    topics_data = []
    unique_subjects = []
    unique_grades = []
    unique_board = [] 
    teacher_id = None
    if has_role(request.user.userprofile,'Content Admin'):
        is_teacher = 0
    elif request.user.is_superuser:
        is_teacher = 0
    else:
        is_teacher = 1
        teacher_id = request.user.id
    if course_id:
        course = Course.objects.get(pk=course_id)
        topic_details = TopicDetails.objects.filter(status='Not Started',topic__course_id=course)
        if workStream and len(workStream)>0 and topics and len(topics)>0:
            topic_details = TopicDetails.objects.filter(status='Not Started',topic__course_id=course,topic__title__in=topics,attribute__types__in = workStream)
        elif topics and len(topics)>0:
            topic_details = TopicDetails.objects.filter(status='Not Started',topic__course_id=course,topic__title__in=topics)
        elif workStream and len(workStream)>0:
            topic_details = TopicDetails.objects.filter(status='Not Started',topic__course_id=course,attribute__types__in = workStream)
        for topic in topic_details:
            topic_status = Topic.objects.filter(id = topic.topic_id).values_list("status",flat=True)[0]
            if topic_status == "Not Started":
                topic_picture = '/static/images/no_image_thumb.gif'
                if '5' in str(course.grade):unique_grades.append(5)
                if '6' in str(course.grade):unique_grades.append(6)
                if '7' in str(course.grade):unique_grades.append(7)
                if '8' in str(course.grade):unique_grades.append(8)
                if '9' in str(course.grade):unique_grades.append(9)
                if '10' in str(course.grade):unique_grades.append(10)
                if '11' in str(course.grade):unique_grades.append(11)
                if '12' in str(course.grade):unique_grades.append(12)
                try:
                    subtopic_list = []
                    subtopiclist = SubTopics.objects.values_list("name",flat=True).filter(topic_id = topic.topic.id,status="Not Started")
                    for subtopic in subtopiclist:
                        subtopic_list.append(subtopic)
                    videos_involved = len(subtopic_list)
                except:
                    subtopic_list = []
                    videos_involved = 0

                topics_data.append({'course_id':course.id,
                                    'image':topic_picture,
                                    'grades':course.grade,
                                    'subject':course.subject,
                                    'board_name':course.board_name,
                                    'topic':topic.topic.title,
                                    'id':topic.topic.id,
                                    'topic_url': topic.url,
                                    'attribute_id':topic.attribute.id,
                                    'workstream':topic.attribute.types,
                                    'videos_involved': videos_involved,
                                    'subtopic_list':subtopic_list,
                                    'is_teacher':is_teacher,
                                    'teacher_id':teacher_id
                                    })
                unique_subjects.append(course.subject)
                unique_board.append(course.board_name)
    topics_data = {value['id']:value for value in topics_data}.values()
    return HttpResponse(simplejson.dumps({'topic_details':topics_data,'unique_subjects':sorted(set(unique_subjects)),'unique_grades':sorted(set(unique_grades)),'unique_board':sorted(set(unique_board))}),mimetype = 'application/json')

def get_content_volunteer(topic_details_id):
    td = TopicDetails.objects.get(id = topic_details_id)
    board = td.topic.course_id.board_name
    content_volunteer = Role.objects.get(name = "Content Developer")
    teacher_role = Role.objects.get(name = "Teacher")

    if board == "NCERT":
        user_pref_cv = UserProfile.objects.filter(~Q(pref_roles = teacher_role), pref_roles = content_volunteer, pref_medium = "Hindi")
    elif board == "TNSB":
        user_pref_cv = UserProfile.objects.filter(~Q(pref_roles = teacher_role), pref_roles = content_volunteer,  pref_medium = "Tamil")
    elif board == "APSB":
        user_pref_cv = UserProfile.objects.filter(~Q(pref_roles = teacher_role), pref_roles = content_volunteer,  pref_medium = "Telugu")
    else: user_pref_cv = []

    if user_pref_cv: user_pref_cv = [{"id": obj.user.id, "username": obj.user.first_name+" "+ obj.user.last_name } for obj in user_pref_cv]
    return user_pref_cv

@login_required
def block_demand(request):
    block_response = {"status": 0, "message": "Success"}
    platform = request.POST.get('platform', '')
    center_id = request.POST.get('center_id')
    offer_id = request.POST.get('offer_id')
    slots = request.POST.get('slot_ids')
    user_id = request.POST.get('user_id') or request.user.id
    if center_id and offer_id and slots:
        slots = slots.split(',')
        slot_objs = []
        try:
            try:
                centerobj = Center.objects.get(id=center_id)
            except Center.DoesNotExist:
                message = "Center entry with Id: {} DoesNotExist".format(center_id)
                if platform:
                    block_response = {"status": 1, "message": message}
                    return HttpResponse(json.dumps(block_response), content_type='application/json')
                else:
                    return HttpResponse(message)

            try:
                offering_obj = Offering.objects.get(id=offer_id)
            except Offering.DoesNotExist:
                message = "Offering entry with Id: {} DoesNotExist".format(offer_id)
                if platform:
                    block_response = {"status": 1, "message": message}
                    return HttpResponse(json.dumps(block_response), content_type='application/json')
                else:
                    return HttpResponse(message)

            for ent in slots:
                try:
                    slot = Demandslot.objects.get(pk=ent)
                except Demandslot.DoesNotExist:
                    message = "Demandslot entry with Id: {} DoesNotExist".format(ent)
                    if platform:
                        block_response = {"status": 1, "message": message}
                        return HttpResponse(json.dumps(block_response), content_type='application/json')
                    else:
                        return HttpResponse(message)

                slot.offering = offering_obj
                slot.status = 'Booked'
                if int(user_id) != request.user.id:
                    try:
                        userobj = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        message = "User entry with Id: {} DoesNotExist".format(user_id)
                        if platform:
                            block_response = {"status": 1, "message": message}
                            return HttpResponse(json.dumps(block_response), content_type='application/json')
                        else:
                            return HttpResponse(message)
                else:
                    userobj = request.user
                slot.user = userobj
                slot.date_booked = datetime.datetime.now()
                slot.save()
                slot_objs.append(slot)
            pref_role_status = RolePreference.objects.filter(userprofile_id=user_id, role__name='Teacher')
            if pref_role_status:
                pref_role_status = pref_role_status[0].role_outcome
            else:
                pref_role_status = ''

            center_state = centerobj.state.title().rstrip()
            center_admin_mail = centerobj.admin.email
            VA_coord_mail = ""

            state_coord=[]

            if center_state == "Karnataka":
        
                state_coord = Center.objects.filter(state="Karnataka", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Tamil Nadu":
                
                state_coord = Center.objects.filter(state="Tamil Nadu", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Jharkhand":
                
                state_coord = Center.objects.filter(state="Jharkhand", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Andhra Pradesh":
                
                state_coord = Center.objects.filter(state="Andhra Pradesh", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Telengana":
               
                state_coord = Center.objects.filter(state="Telengana", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Maharashtra":

                state_coord = Center.objects.filter(state="Maharashtra", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "West Bengal":
                
                state_coord = Center.objects.filter(state="West Bengal", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()

            
            args = {'user':userobj,'slots':slot_objs,'contxt' : 'Blocked', 'role_status': pref_role_status, \
                    'confirm_url': WEB_BASE_URL+"centeradmin/?center_id=" + center_id }

            subject_template = 'mail/_demand_handle/short.txt'
            subject = genUtility.get_mail_content(subject_template, args).replace('\n', '')
            if pref_role_status == 'Recommended':
                recipients = [center_admin_mail, userobj.email].extend(state_coord)
                body_template = 'mail/_demand_handle/full_rft.txt'
            else:
                recipients = state_coord.extend([VA_coord_mail, userobj.email])
                body_template = 'mail/_demand_handle/full_not_rft.txt'


            body = genUtility.get_mail_content(body_template, args)
            #change it after testing
            # recipients.append('akhilraj@headrun.com') # He is headrun developer, Should not sent any emailers
            # recipients.append('rini.jose@evidyaloka.org')
            userid = ''
            if userobj:
                userid = userobj.id
            insert_into_alerts(subject, body, ','.join(recipients), userid, 'email')
            #_send_mail(test,'_demand_handle',{'user':request.user,'slots':slot_objs,'contxt' : 'Blocked', 'role_status': pref_role_status})
        except Exception as e:
            if platform:
                block_response = {"status": 1, "message": "Error"}
                return HttpResponse(json.dumps(block_response), content_type='application/json')
            else:
                return HttpResponse('Error')
    if platform:
        return HttpResponse(json.dumps(block_response), content_type='application/json')
    if centerobj and offering_obj and slots:
        timeSlot=''
        for ent in slots:
            demandSlotObj=Demandslot.objects.get(pk=ent)
            timeSlot+=str(demandSlotObj.day)+":"+str(demandSlotObj.start_time)+" to "+str(demandSlotObj.end_time)+" and "
        timeSlot.rsplit(' ', 1)[0]
        corseObj=Course.objects.get(id=offering_obj.course_id)
        save_user_activity(request,'Confirmed Oppourtunities:'+str(centerobj.name)+','+str(corseObj.subject)+','+timeSlot,'Action')
    return HttpResponse('ok')

def centerNew(request):
    centers = Center.objects.filter(Q(status = 'Planned') | Q(status = 'Active'))
    language_list = []
    location_list=[]
    sorted_list = []
    for center in centers:
        location_list.append(center.state)
        language_list.append(center.language)
    for list in sorted(set(location_list)):
        if list is None:
            continue
        if list.replace(' ','').lower() not in (i.replace(' ','').lower() for i in sorted_list):
            sorted_list.append(list)
    return render_response(request, "center.html",{'language_list': sorted(set(language_list)),'location_list':sorted_list})

def centers(request):
    select_language = json.loads(request.POST.get('sel_langs', ''))
    select_location = json.loads(request.POST.get('sel_location', ''))
    page = request.POST.get('page', 1)
    center_image = ''
    centers = Center.objects.filter(Q(status = 'Planned') | Q(status = 'Active'))
    for center in centers:
        if center.photo:
            photopath = os.path.exists(center.photo.path)
            if not photopath:
                center.photo = 'static/images/no_image_thumb.gif'
    if select_language or select_location:
        if select_language and select_location:
            centers = centers.filter( Q(language__in=select_language) & Q(state__in=select_location))
        elif select_location:
            centers = centers.filter(state__in=select_location)
        else:
            centers = centers.filter(language__in=select_language)
    center_data = []
    paginator = Paginator(centers, 10)
    try:
        centers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        centers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        centers = paginator.page(paginator.num_pages)
    for center in centers:
        if center.photo:
            if crop(center.photo,"250x250"):
                center_image = "/" + crop(center.photo,"250x250")
        else :
            center_image = "/static/images/no_image_thumb.gif "
        center_data.append({'name':center.name,
                            'state':center.state,
                            'photo':center_image,
                            'id':center.id
                            })
        center_image = ''
    return HttpResponse(simplejson.dumps({'center_data':center_data,'prev': centers.previous_page_number(),'next': centers.next_page_number(),'current': centers.number,'total': centers.paginator.num_pages}), mimetype='application/json')

def centerDetails(request):  
    centerId = request.GET.get('center_id','')
    centers = Center.objects.filter(id = centerId)
    counts = []
    centers_data = []
    user = None
    if request.user and request.user.is_authenticated():
        user = request.user
    if centers:
        for center in centers:
            empty_courses, assigned_courses, other_lang_courses = get_ongoing_courses(center, user)
            counts.append(len(empty_courses))
            length = len(empty_courses) + len(other_lang_courses)
            center_image = "http://placehold.it/133x133/F15A22/fff/&text=" + center.name
            if center.photo:
                if crop(center.photo,"250x250"):
                    center_image = "/" + crop(center.photo,"250x250")
            centers_data.append({"title":center.name, "description":center.description, "image":center_image, "empty_courses":empty_courses, "assigned_courses":assigned_courses, "other_lang_courses": other_lang_courses, "grades":center.grades, "subjects_covered": center.subjectscovered, "location":center.classlocation, "noofchildren":center.noofchildren, "launch_date": center.launchdate,"ops_donor":center.ops_donor_name, "donor":center.donor_name, "length":length })
    counts.sort()
    counts.reverse()     
    return render_response(request, "centerDetails.html",{'centers_data':centers_data})    

@csrf_exempt
def time_table(request):
    if request.is_ajax():
        center_id = request.GET.get('center_id','')
        days = []
        for x in range(0, 7):
            todayDate=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30)).date() + timedelta(x)
            todayDay = calendar.day_name[todayDate.weekday()]
            days.append(todayDay)
        s_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30)).date()
        e_date = (s_date+timedelta(days=int(7)))
        e_date = str(e_date)
        time_slot_list = []
        if s_date and e_date:
            last_date = datetime.datetime.strptime(e_date ,"%Y-%m-%d")
            last_date = last_date.strftime("%Y-%m-%d")
            center = Center.objects.get(id = center_id,status='Active')
            time_slot_details=[]
            sub = ''
            if center:
                offering_ids = Offering.objects.values_list('id',flat=True).filter(center = center.id,status='running').exclude(active_teacher_id__isnull=True).distinct()
                
                for id in offering_ids:
                    if s_date and e_date:
                        length_max_session = 10
                        time_slots = Session.objects.filter(offering_id=id, status='scheduled', date_start__gte=s_date, date_end__lt=last_date).order_by('date_start','date_end')
                        if len(time_slots)==0:
                            length_max_session = 2
                            time_slots = Session.objects.filter(offering_id=id, status='scheduled', date_end__gte=last_date).order_by('date_start','date_end')
                        length=0
                        for time_slot in time_slots:
                            if length<length_max_session:
                                if time_slot.date_start.strftime('%H:%M')>='06:59:59' and  time_slot.date_start.strftime('%H:%M') <='21:00:00':
                                    if 'English' in str(time_slot.offering.course.subject):sub=('E')
                                    elif 'Math' in str(time_slot.offering.course.subject):sub=('M')
                                    elif 'Science' in str(time_slot.offering.course.subject):sub=('S')
                                    session_end_date = time_slot.date_end.strftime("%Y-%m-%d")
                                    slot_data = ''
                                    if time_slot.teacher:
                                        slot_data = str(time_slot.offering.course.grade)+''+str(sub)+'-'+str(time_slot.teacher.first_name)+'' 
                                    if session_end_date > e_date and slot_data != '' : slot_data += '('+time_slot.date_end.strftime("%d-%m-%Y")+')'
                                    time_slot_data={'day':time_slot.date_start.strftime("%A"),
                                            'time_slot':time_slot.date_start.strftime('%H:%M %p')+"-"+time_slot.date_end.strftime('%H:%M %p'),
                                            'slot_data':slot_data,
                                        }
                                    time_slot_details.append(time_slot_data)
                                    length+=1
            time_slot_data_group =[]
            time_slot_details = sorted(time_slot_details, key = itemgetter('time_slot','day'))
            for time_slot_key, time_slot_group in itertools.groupby(time_slot_details, key=itemgetter('time_slot')):
                data = {'slot':time_slot_key,'time_slot_data':list(time_slot_group)}
                time_slot_data_group.append(data)
            for time_data in time_slot_data_group:
                mon, tue, wed, thurs, fri, sat,sun= ['']*7
                count_mon = 0
                count_tue = 0
                count_wed = 0
                count_thurs = 0
                count_fri = 0
                count_sat = 0
                count_sun = 0
                i = 0
                mon_day = ''
                tue_day = ''
                wed_day = ''
                thu_day = ''
                fri_day = ''
                stu_day = ''
                sun_day = ''
                for data in time_data['time_slot_data']:
                    if data['day']=='Monday' and count_mon <=1:
                        if str(data['slot_data'])!='':
                            splited_teacher = str(data['slot_data']).split('-')[1]
                            if splited_teacher!= mon_day:
                                count_mon +=1;
                                if len(mon)>0:
                                    mon += ', '
                                mon += data['slot_data']
                                mon_day = data['slot_data']
                                mon_day = mon_day.split('-')[1]
                    if data['day']=='Tuesday' and count_tue <=1:
                        if str(data['slot_data'])!='':
                            splited_teacher = str(data['slot_data']).split('-')[1]
                            if splited_teacher!= tue_day:
                                count_tue +=1
                                if len(tue)>0:
                                    tue += ', '
                                tue += data['slot_data']
                                tue_day = data['slot_data']
                                tue_day = tue_day.split('-')[1]
                    if data['day']=='Wednesday' and count_wed <= 1:
                        if str(data['slot_data'])!='':
                            splited_teacher = str(data['slot_data']).split('-')[1]
                            if splited_teacher!= wed_day:
                                count_wed +=1
                                if len(wed)>0:
                                    wed += ', '
                                wed += data['slot_data']
                                wed_day = data['slot_data']
                                wed_day = wed_day.split('-')[1] 
                    if data['day']=='Thursday' and count_thurs <=1:
                        if str(data['slot_data'])!='':
                            splited_teacher = str(data['slot_data']).split('-')[1]
                            if splited_teacher!= thu_day:
                                count_thurs += 1 
                                if len(thurs)>0:
                                    thurs += ', '
                                thurs += data['slot_data']
                                thu_day = data['slot_data']
                                thu_day = thu_day.split('-')[1] 
                    if data['day']=='Friday' and count_fri <= 1:
                        if str(data['slot_data'])!='':
                            splited_teacher = str(data['slot_data']).split('-')[1]
                            if splited_teacher!= fri_day:
                                count_fri += 1 
                                if len(fri)>0:
                                    fri += ', '
                                fri += data['slot_data']
                                fri_day = data['slot_data']
                                fri_day = fri_day.split('-')[1] 
                    if data['day']=='Saturday' and count_sat <= 1:
                        if str(data['slot_data'])!='':
                            splited_teacher = str(data['slot_data']).split('-')[1]
                            if splited_teacher!= stu_day:
                                count_sat += 1 
                                if len(sat)>0:
                                    sat += ', '
                                sat += data['slot_data']
                                stu_day = data['slot_data']
                                stu_day = stu_day.split('-')[1] 
                    if data['day']=='Sunday' and count_sat <= 1:
                        if str(data['slot_data'])!='':
                            splited_teacher = str(data['slot_data']).split('-')[1]
                            if splited_teacher!= sun_day:
                                count_sun += 1
                                if len(sun)>0:
                                    sun += ', ' 
                                sun += data['slot_data']
                                sun_day = data['slot_data']
                                sun_day = sun_day.split('-')[1] 
                    i += 1
                    data = {'slot':time_data['slot'],'Monday':mon,'Tuesday':tue,'Wednesday':wed,'Thursday':thurs,'Friday':fri,'Saturday':sat,'Sunday':sun}
                days_val = []
                for day in days:
                    day_dic ={''+day+'':data[''+day+'']}
                    days_val.append(day_dic)
                final_dic = {'slot':time_data['slot'],'days':days_val}
                time_slot_list.append(final_dic)
        return HttpResponse(simplejson.dumps({'time_slot_list':time_slot_list,'days':days}),mimetype='application/json')
    return HttpResponse('ok')

@login_required
def enroll_student(request):
    message = request.GET.get('message','')
    #centers = Center.objects.all()
    center_id = request.GET.get('center_id','')
    save_flag = request.GET.get('save_flag','')
    return render_response(request, "enrollStudent.html",{'centers':center_id,'message':message,'save_flag':save_flag})

def save_enrollStudent(request):
    try:
        if request.method =='POST':
            my_image_data = request.POST.get('my_image_data','')
            student_id = request.POST.get('student_id','')
            page = request.POST.get('page','')
            gradeId = request.POST.get('gradeId','')
            genderId = request.POST.get('genderId','')
            studentPhoto = request.POST.get('studentPhoto','')
            save_flag = request.POST.get('save_flag','')
            #new_image = base64.b64decode(my_image_data);
            studentName = request.POST.get('studentName','')
            dob = request.POST.get('dob','')
            grade = request.POST.get('grade','')
            gender = request.POST.get('gender','')
            fatherOccupation = request.POST.get('fatherOccupation','')
            motherOccupation = request.POST.get('motherOccupation','')
            strengths = request.POST.get('strengths','')
            weakness = request.POST.get('weakness','')
            observation = request.POST.get('observation','')
            status = request.POST.get('status','')
            currentSchool = request.POST.get('currentSchool','')
            currentgrade = request.POST.get('currentgrade','')
            familyIncome = request.POST.get('familyIncome','')
            eventName = request.POST.get('eventName','')
            performance = request.POST.get('performance','')
            description = request.POST.get('description','')
            achievments = request.POST.get('achievments_json','')
            center_id = request.POST.get('center_id','')
            centerId = request.POST.get('centerId','')
            schoolRollNumber = request.POST.get('schoolRollNumber','')
            phone_no = request.POST.get('phone_no','')
            # get guardian name and relation
            guardianName = request.POST.get('guardianName')
            relationshipType = request.POST.get('relationshipType','')
            kycdoctype = request.POST.get('kycdoctype', None)
            kycdocnum = request.POST.get('kycdocnum', None)
            photo = ''
            message = ''
            today = datetime.datetime.now()
            newPhoto = ''
            i = 0
            j= 20
            if 'photo' in request.FILES:
                photo = request.FILES['photo']
                photonew = photo.name.split('.')
                if len(photonew[0]) > 45 or len(photonew) > 2:
                    for pht in photonew[0]:
                        if i < j:
                            newPhoto += pht
                        i += 1 
                    newPhoto += '.' 
                    newPhoto += photonew[-1]
                else :
                    newPhoto = photo.name
                new_photo = 'static/uploads/student/'+ studentName +''+today.strftime("%d_%m_%Y")+''+today.strftime("%X")+ '_'+ newPhoto +''
                f_path = os.getcwd()
                f_name = '/static/uploads/student/' + studentName + ''+today.strftime("%d_%m_%Y")+''+today.strftime("%X")+'_'+ newPhoto +''
                f = open(f_path + f_name, 'w+')
                f.write(photo.read())
                f.close()
            else :
                photo = studentPhoto
                new_photo = studentPhoto
            date_dob = None
            if dob:
                date_dob = datetime.datetime.strptime(dob, "%d/%m/%Y")
            center = None
            if center_id:
                center = Center.objects.get(pk=center_id)
            else:
                center = Center.objects.get(pk=centerId)

            if student_id:
                message = "Student Details Updated Successfully."
                Student.objects.filter(id=student_id).update(name=studentName,dob=date_dob,center=center,gender=gender,grade=grade,father_occupation=fatherOccupation,mother_occupation=motherOccupation,strengths=strengths,weakness=weakness,observation=observation,status=status,school_rollno=schoolRollNumber, photo=new_photo,phone = phone_no)
                kyc = get_object_or_none(KycDetails, student=student_id)
                if kyc:
                    studentApp.updateStudentKyc(student_id=student_id, updated_by=request.user, doc_type=kycdoctype ,kyc_number=kycdocnum, status='1')
                else:
                    student = Student.objects.get(id=student_id)
                    studentApp.createStudentKyc(student=student, created_by=request.user, doc_type=kycdoctype ,kyc_number=kycdocnum, status='1')

                if (status == 'Alumni'):
                    if familyIncome  == '':
                        familyIncome_log = None
                    else:
                        familyIncome_log = float(familyIncome) 
                    studentlog = StudentLog.objects.filter(student_id=student_id)
                    if studentlog:
                        studentLog = StudentLog.objects.filter(student_id=student_id).update(current_school=currentSchool,current_grade=currentgrade,family_income=familyIncome_log,event_name=eventName,notes_onperformance=performance,event_description=description,achievments=achievments)
                    else:
                        studentLog = StudentLog(student_id=student_id,current_school=currentSchool,current_grade=currentgrade,family_income=familyIncome_log,event_name=eventName,notes_onperformance=performance,event_description=description,achievments=achievments)
                        studentLog.save()
                return redirect('/v2/enrollStudent_list/?center_id='+centerId+'&message='+message+'&page='+page+'&grade='+gradeId+'&gender='+genderId)
            else:
                if str(Student.objects.filter(phone = phone_no,name = studentName, gender=gender,dob=date_dob))=='[]':
                    message = "Student Enrolled Successfully."
                    enrolledby=request.user
                    enrolled_on=datetime.datetime.now()
                    updatedby=request.user
                    createdby=request.user
                    student = Student(name=studentName,dob=date_dob,center=center,gender=gender,
                    grade=grade,father_occupation=fatherOccupation,mother_occupation=motherOccupation,
                    strengths=strengths,weakness=weakness,observation=observation,status=status,
                    school_rollno=schoolRollNumber, photo=new_photo,enrolled_on=enrolled_on,
                    enrolled_by=enrolledby,updated_by=updatedby,created_by=createdby,phone = phone_no)
                    student.save()
                    if student.id:
                        studentApp.createStudentKyc(student=student, created_by=request.user, doc_type=kycdoctype ,kyc_number=kycdocnum, status='1')
                    if (status == 'Alumni'):
                        if familyIncome  == '':
                            familyIncome_log = None
                        else:
                            familyIncome_log = float(familyIncome) 
                        studentlog = StudentLog(student_id=student.id,current_school=currentSchool,current_grade=currentgrade,family_income=familyIncome_log,event_name=eventName,notes_onperformance=performance,event_description=description,achievments=achievments)
                        studentlog.save()
                    ### code for sync mobile and portal
                    try:
                        digitalSchool = center.digital_school
                        digitalSchoolPartner = center.digital_school_partner
                    except:
                        digitalSchool = None
                        digitalSchoolPartner = None
                    if digitalSchool and digitalSchoolPartner and guardianName and relationshipType:
                        createGuardianObjectIfNeeded(createdby, student, phone_no, relationshipType, True, guardianName,'3')
                        enrollment = Student_School_Enrollment.objects.create(
                            student=student,
                            digital_school = center.digital_school,
                            center = center,
                            enrollment_status = "active",
                            enrolled_by=createdby,
                            created_by=createdby,
                            updated_by=createdby,
                            payment_status='free'
                            )
                        enrollment.save()
                    return redirect('/v2/enroll_student/?center_id='+center_id+'&message='+message+'&save_flag='+save_flag)
                else:
                    return redirect('/v2/enroll_student/?center_id='+center_id+'&message='+'Student already exists!'+'&save_flag='+save_flag+'&existing=exist')
    except Exception as e:
        traceback.print_exc()
        logService.logException("SavestudentsView GET Exception error", e.message)
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

@login_required
def enrollStudent_list(request):
    message = request.GET.get('message','')
    studentId = request.GET.get('student_id','')
    page = request.GET.get('page','')
    centerId = request.GET.get('center_id','')
    grade = request.GET.get('grade','')
    gender = request.GET.get('gender','')
    status = request.GET.get('status','')
    is_Assistant = False
    is_centeradmin = False
    is_partner = False
    is_field_coordinator = False
    user = request.user
    user_profile = UserProfile.objects.filter(user = request.user)[0]
    roles = user_profile.role.values_list('name',flat=True)
    if roles:
            user_role = roles[0]
            if "Center Admin" in roles: is_centeradmin = True
            else:is_centeradmin = False
            if "Class Assistant" in roles: is_Assistant = True
            else: is_Assistant = False
            if "Partner Admin" in roles: is_partner = True
            else: is_partner = False
            if "Field co-ordinator" in roles: is_field_coordinator = True
            else: is_field_coordinator = False

            if 'Delivery co-ordinator' in roles: is_delivery=True
            else: is_delivery=False


    return render_response(request, "listEnrollStudent.html",{'user':user,'is_partner':is_partner,'is_centeradmin':is_centeradmin,'is_Assistant':is_Assistant,'page':page,'centerId':centerId, 'is_field_coordinator':is_field_coordinator,
            'is_delivery':is_delivery,  'grade':grade,'gender':gender,'message':message,'status':status})

def getstudentLIstData(request):
    try:
        message = request.POST.get('message','')
        centerId = request.POST.get('center','')
        grade = request.POST.get('grade','')
        gender = request.POST.get('gender','')
        status = request.POST.get('status','')
        is_all = request.POST.get('is_all', '')
        students = None
        if centerId :
            center = Center.objects.get(pk=centerId)
            students = Student.objects.all().filter(center=centerId).order_by("-id")
            if status:
                students = students.filter(status=status)
            if grade:
                students = students.filter(grade=grade)
        promoted_grade_list = []
        if grade and len(students) > 0:
            promoted_grade_list = [str(int(grade) + 1)]
        if gender:
            if 'Male' in gender:
                students = students.filter(Q(gender=gender) | Q(gender='boy') | Q(gender='M') | Q(gender='b') | Q(gender='Boy'))
            else:
                students = students.filter(Q(gender=gender) | Q(gender='Girl') | Q(gender='F') | Q(gender='g') | Q(gender='girl'))
        without_pagination_count = len(students)
        student_list = []
        if not is_all:
            page = request.POST.get('page', 1)
            paginator = Paginator(students, 10)
            try:
                students = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                students = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                students = paginator.page(paginator.num_pages)
        centerName = ''
        rollNo = ''
        for student in students:
            center_name = Center.objects.values('name').filter(id=student.center_id)
            kyc = get_object_or_none(KycDetails, student=student.id)
            if center_name:
                for name in center_name:
                    centerName = name['name']
            if student.school_rollno:
                rollNo = student.school_rollno

            sticker_obj = Recognition.objects.filter(object_id= student.id,
                                            content_type=ContentType.objects.get(model='student')).values(
                'sticker__sticker_name', 'sticker__sticker_path').annotate(countofreg=Count('sticker__sticker_name'))

            sticker_list = []
            if sticker_obj:
                for i in sticker_obj:
                    sticker_list.append(i)


            photo = str(student.photo)
            if photo:
                if not 'static' in photo:
                    photo = '/static/uploads/student/'+photo
                else:
                    photo = '/'+photo
            student_list.append({'id':student.id,
                                'studentName':student.name,
                                'center_id' : student.center_id,
                                'centerName' :centerName,
                                'DOB':student.dob,
                                'gender':student.gender,
                                'grade':student.grade,
                                'father_occupation':student.father_occupation,
                                'mother_occupation':student.mother_occupation,
                                'strengths':student.strengths,
                                'weakness':student.weakness,
                                'observation':student.observation,
                                'status':student.status,
                                'is_reached':student.is_reached,
                                'school_rollno':rollNo,
                                'center_id':student.center_id,
                                'photo':photo,
                                'stickers': sticker_list,
                                'kyc_number': kyc.kyc_number if kyc else '',
                                })
        if is_all:
            num_of_pages = math.ceil(len(student_list) / 10)

            return HttpResponse(simplejson.dumps({
                'student_list':student_list,
                'prev': 1,
                'next': 2,
                'current': 1,
                'total': num_of_pages,
                'message': '',
                'grade': grade,
                'gender': gender,
                'status': status,
                'count': len(student_list),
                'promoted_grade':sorted(promoted_grade_list)
            }, default = myconverter), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'student_list':student_list,'prev': students.previous_page_number(),
                                            'next': students.next_page_number(),'current': students.number,
                                            'total': students.paginator.num_pages,'message':message,'grade':grade,
                                            'gender':gender,'status':status,'count':without_pagination_count,'promoted_grade':sorted(promoted_grade_list) },
                                            default = myconverter), mimetype='application/json')
    except Exception as e:
        traceback.print_exc()
        logService.logException("GetstudentsView GET Exception error", e.message)
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

@login_required
def edit_student(request):
    student_id = request.GET.get('student_id','')
    center_id = request.GET.get('center_id','')
    page = request.GET.get('page','')
    grade = request.GET.get('grade','')
    gender = request.GET.get('gender','')
    if student_id:
        student = Student.objects.get(pk=student_id)
        studentLog = student.studentlog_set.filter(student_id=student.id)
        sticker_list = []
        sticker_obj = Recognition.objects.filter(object_id=student.id,
                                                 content_type=ContentType.objects.get(model='student')).values(
            'sticker__sticker_name', 'sticker__sticker_path').annotate(countofreg=Count('sticker__sticker_name'))

        if sticker_obj:[sticker_list.append(i) for i in sticker_obj]
        context = {'student':student,'page':page,'gradeId':grade,'genderId':gender,'stickers': sticker_list, 'photo': str(student.photo),'edit_flag':True, 'kyc_type':'', 'kyc_number':''}
        kyc = get_object_or_none(studentApp.KycDetails, student=student.id)
        if kyc:
            context['doc_type'] = kyc.doc_type
            context['kyc_number'] = kyc.kyc_number

        if studentLog:
            for student_log in studentLog:
                context['studentlog']=student_log
                return render_response(request, "enrollStudent.html",context)
        else:
            return render_response(request, "enrollStudent.html",context)
    return redirect('/v2/enrollStudent_list/?center_id='+center_id)

@csrf_exempt
def delete_student(request):
    student_id = request.GET.get('student_id','')
    center_id = request.GET.get('centerId','')
    page = request.GET.get('page','')
    grade = request.GET.get('grade','')
    gender = request.GET.get('gender','')
    message = ''
    if student_id:
        student = Student.objects.filter(id=student_id).update(status='Inactive') 
        studentName = Student.objects.values('name').filter(id=student_id)
        for name in studentName:
            student =  name['name']
        message = " "+student+" Deleted Successfully"
    return HttpResponse(simplejson.dumps({'student_id':student_id,'center_id':center_id,'page':page,'message':message},default = myconverter), mimetype='application/json')

@csrf_exempt
def get_users(request):
    if request.is_ajax():
        search_term =  request.GET.get('term', '')
        flag_value = request.GET.get('action','')
        term = search_term.split();
        if len(term) > 1:
            users = User.objects.filter((Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term) | Q(username__icontains=search_term) | Q(id__icontains=search_term)  | Q(first_name__icontains=term[0] , last_name__icontains=term[1])) & Q(is_active=True))[:20]
        else:
            users = User.objects.filter((Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term) | Q(username__icontains=search_term) | Q(id__icontains=search_term)) & Q(is_active=True))[:20]
        user_result = []
        for ent in users:
            refer_dict = {}
            refer_dict['id'] = ent.id
            refer_dict['label'] = ''
            if flag_value == 'performed_on':
                if ent.first_name and ent.last_name:
                    refer_dict['label'] = ent.first_name +'  '+ent.last_name
                else:
                    refer_dict['label'] = ent.username
                refer_dict['label'] += '-'+str(ent.id)
            elif flag_value == 'assigned_to':
                refer_dict['label'] = ent.username
                refer_dict['label'] += '-'+str(ent.id)
                refer_dict['name'] = ent.username
            refer_dict['value'] = refer_dict['label']
            user_result.append(refer_dict)
        data = json.dumps(user_result)
    else:
        data= 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@csrf_exempt
def save_rating(request):
    session_id = int(request.GET.get("session_id",None))
    star_rating = json.loads(request.GET.get('star_rating', ''))
    data = {"msg":"Rating can not be saved."}
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        session = None
    if session and star_rating:
        status = session.status
        if (status == 'Completed' or status == 'completed'):
            for rating in star_rating:
                if request.user.is_authenticated():
                    session_rating = SessionRatings(is_rated=True, question=rating['ques'], no_of_stars=rating['rating'], created_date=datetime.datetime.now().date(), question_no=rating['ques_no'],user_id=session.teacher, created_by=request.user, session_id=session)
                    session_rating.save()
                else:
                    session_rating = SessionRatings(is_rated=True, question=rating['ques'], no_of_stars=rating['rating'], created_date=datetime.datetime.now().date(), question_no=rating['ques_no'],user_id=session.teacher, created_by=session.teacher, session_id=session)
                    session_rating.save()
            data={"msg":"Rating Saved Successfully"}
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

@login_required
def downloadSampleBulkUpload(request):
    path = 'static/uploads/poc/WikividyaBulkSample.xlsx'
    if not os.path.isfile(path):
        path = 'static/uploads/poc/WikividyaBulkSample.xlsx'
    certificate = open(path, "r")
    response = HttpResponse(FileWrapper(certificate), content_type='application/xlsx')
    response['Content-Disposition'] = 'attachment; filename= WikividyaBulkSample.xlsx'
    return response

@login_required
def downloadSampleTransliteration(request):
    path = 'static/uploads/poc/TranslitrationSample.xlsx'
    if not os.path.isfile(path):
        path = 'static/uploads/poc/TranslitrationSample.xlsx'
    certificate = open(path, "r")
    response = HttpResponse(FileWrapper(certificate), content_type='application/xlsx')
    response['Content-Disposition'] = 'attachment; filename=TranslitrationSample.xlsx'
    return response

def get_sesstionRating(request):
    sessionId=request.GET.get("session",'')
    if sessionId:
        try:
            session = Session.objects.get(pk = int(sessionId))
            sess_rating_json = []
            sess_ratings = session.sr_session_id.all()
            for sess_rat in sess_ratings:
                sess_rating_json.append({"stars":sess_rat.no_of_stars,"ques_no":sess_rat.question_no})
            return HttpResponse(simplejson.dumps(sess_rating_json), mimetype='application/json')
        except Session.DoesNotExist:
            return HttpResponse(simplejson.dumps({"error":"Session id not found"}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({"error":"Session id not found"}), mimetype='application/json')

@login_required    
def upload_task(request):
    upload_download = request.POST.get('upload_download','')
    if upload_download:
        curr_time = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
        xlsxFlag=False
        if 'files' in request.FILES:
                file = request.FILES['files']
                file = str(file)
                if file.find(".")!=-1 :
                    file = file.split('.')
                    if file[1] == 'xlsx':
                        xlsxFlag = True
        if xlsxFlag:
            task_fail = 0
            task_success = 0
            input_excel = request.FILES['files']
            book = None
            sheet = None
            mail_flag = False
            try:
                book = xlrd.open_workbook(file_contents=input_excel.read())
                sheet = book.sheet_by_index(0)
            except:
                book = None
                sheet = None
            successMsg = ''
            errorMsg = ''
            emptyFile = ''
            
            if sheet and sheet.nrows<=1:
                emptyFile = 'File contain no data.'
            if sheet:
                for row_index in range(1, sheet.nrows):
                    mail_flag = False
                    user_date_joined = None
                    performedOn_name = ''
                    dueDate = ''
                    try:
                        subject = sheet.cell(row_index,0).value
                        dueDate = sheet.cell(row_index,1).value
                        comment = sheet.cell(row_index,2).value
                        assignedTo_id = sheet.cell(row_index,3).value
                        priority = sheet.cell(row_index,4).value
                        performed_on_userId = sheet.cell(row_index,5).value
                        task_type = sheet.cell(row_index,6).value
                        taskStatus = sheet.cell(row_index,7).value
                        category = sheet.cell(row_index,8).value
                        if task_type:
                            task_type = str(task_type)
                            task_type = task_type.upper()
                            if task_type == 'INTERNAL':
                                task_type = 'MANUAL'
                            elif task_type == 'OTHER OPPORTUNITY':
                                task_type = 'OTHER' 
                        if priority:
                            priority = str(priority)
                            priority = priority.lower()
                            priority = priority.title()
                        if taskStatus:
                            taskStatus = str(taskStatus)
                            taskStatus = taskStatus.lower()
                            if taskStatus == 'wip':
                                taskStatus=taskStatus.upper()
                            else:
                                taskStatus = taskStatus.title()
                        if category:
                            category = str(category)
                            category = category.lower()
                            if category == 'it':
                                category = category.upper()
                            else:
                                category = category.title()
                        if dueDate:
                            dueDate =datetime.datetime.strptime(str(dueDate), "%d-%m-%Y").date()
                        else:
                            dueDate=None
                        user_date_joined = None
                        performedOn_name = ''
                        if performed_on_userId:
                            performed_on_userId = int(performed_on_userId)
                            assignedTo_id = int(assignedTo_id)
                        if assignedTo_id:
                            assignedToObj = User.objects.get(pk=assignedTo_id)
                            if not assignedToObj:
                                assignedTo_id = ''
                        if performed_on_userId:
                            userobj = User.objects.get(pk = performed_on_userId)
                            if userobj:
                                if userobj.first_name or userobj.last_name:
                                    performedOn_name = userobj.first_name+" "+userobj.last_name+"-"+str(performed_on_userId)
                                else:
                                    performedOn_name = userobj.username
                                user_date_joined=userobj.date_joined
                            else:
                                performed_on_userId = ''
                        else:
                            performed_on_userId =''
                        if subject and dueDate and (priority == 'Normal' or priority == 'High' or priority == 'Urgent' or priority == 'Immediate') and (task_type == 'MANUAL'or task_type == 'SYSTEM' or (task_type == 'OTHER' and (category == 'IT' or category == 'Marketing' or category == 'Admin' or category == 'Reporting'))) and (taskStatus == 'WIP' or taskStatus == 'Open' or taskStatus == 'Resolved' or taskStatus == 'Closed'):
                            if task_type == 'OTHER':
                                task = Task(comment = comment,subject = subject,assignedTo = '',dueDate = dueDate,priority = priority,taskCreatedBy_userId = request.user,taskStatus = taskStatus,performedOn_userId = '', taskCreatedDate = curr_time, user_date_joined = user_date_joined,performedOn_name = '',taskType = task_type,task_other_status = 'Pending',category = category)
                                task.save()
                                task_success+=1
                            elif assignedTo_id:
                                task = Task(comment=comment,subject=subject,assignedTo=assignedToObj,dueDate=dueDate,priority=priority,taskCreatedBy_userId=request.user,taskStatus=taskStatus,performedOn_userId=performed_on_userId, taskCreatedDate=curr_time, user_date_joined=user_date_joined,performedOn_name=performedOn_name,taskType=task_type,task_other_status = '')
                                task.save()
                                task_success += 1
                                mail_flag =True
                                assignTo_user = User.objects.get(pk=assignedTo_id)
                                if assignTo_user and assignTo_user.email:
                                    recipients = []
                                    name = assignTo_user.first_name+' '+assignTo_user.last_name
                                    if not name:
                                        name = assignTo_user.username
                                    recipients.append(assignTo_user.email)
                                    todayDate=datetime.datetime.today()
                                    todayDay=calendar.day_name[todayDate.weekday()]
                                    """comment=str(comment).replace("'", ' ')  
                                    subject=str(subject).replace("'", ' ') 
                                    subject=str(subject).replace("<", '\<') 
                                    subject=str(subject).replace(">", '\>')  """  
                                    args = {'user':name,'date':curr_time,'subject' : subject, 'comment': comment, \
                                            'confirm_url':WEB_BASE_URL+"edit_task/?id=" + str(task.id),'todayDay':todayDay }
                                    body_template = 'mail/task/task_full.txt'
                                    body = genUtility.get_mail_content(body_template, args)
                                    try:
                                        send_mail("New Task has been Assigned to you.", body, settings.DEFAULT_FROM_EMAIL, recipients)
                                    except: pass
                            else:
                                task_fail += 1
                                taskRejected=TaskRejected(comment=comment,dueDate=dueDate,priority=priority,subject=subject,taskCreatedDate=curr_time,taskStatus=taskStatus,taskCreatedBy_userId=request.user,assignedTo=assignedTo_id,performedOn_userId = performed_on_userId,user_date_joined = user_date_joined,performedOn_name = performedOn_name,taskType = task_type,task_other_status='',category = category)
                                taskRejected.save()   
                        else:
                            task_fail+=1
                            taskRejected=TaskRejected(comment=comment,dueDate=dueDate,priority=priority,subject=subject,taskCreatedDate=curr_time,taskStatus=taskStatus,taskCreatedBy_userId=request.user,assignedTo=assignedTo_id,performedOn_userId = performed_on_userId,user_date_joined = user_date_joined,performedOn_name = performedOn_name,taskType = task_type,task_other_status='',category = category)
                            taskRejected.save()
                    except:
                        taskRejected=TaskRejected(comment=comment,dueDate=None,priority=priority,subject=subject,taskCreatedDate=curr_time,taskStatus=taskStatus,taskCreatedBy_userId=request.user,assignedTo=assignedTo_id,performedOn_userId = performed_on_userId,user_date_joined = user_date_joined,performedOn_name = performedOn_name,taskType = task_type,task_other_status='',category = category)
                        taskRejected.save()
                        if not mail_flag:
                            task_fail+=1
                        else:
                            task_fail = task_fail
            if task_fail == 0 and task_success>=1:
                successMsg = " All Task saved successfully "
            elif task_fail>=1 and task_success>=1:
                successMsg = str(task_success)+" Task saved successfully and "+str(task_fail)+" Task Rejected. "
            else:
                errorMsg = "All Task failed to save"
                if emptyFile:
                    errorMsg = emptyFile
            return render_response(request, "bulkUploadTask.html",{"msg":successMsg,'error':errorMsg})
        else:
            return render_response(request, "bulkUploadTask.html",{"error":"Please,Upload valid file"})
    else:
        return render_response(request, "bulkUploadTask.html",{})

@login_required
def downloadSampleTask(request):
    path = 'static/uploads/task/TaskSample.xlsx'
    if not os.path.isfile(path):
        path = 'static/uploads/task/TaskSample.xlsx'
    certificate = open(path, "r")
    response = HttpResponse(FileWrapper(certificate), content_type='application/xlsx')
    response['Content-Disposition'] = 'attachment; filename=TaskSample.xlsx'
    return response

def task_reporting(request):  
    start_date = request.GET.get('startDate','')
    end_date = request.GET.get('endDate','')
    selected_userId = request.GET.get('prfm_id','')
    #selected_user_by_name = request.GET.get('prfm_name','')
    selected_user_username = None
    selected_user = None
    '''if selected_user_by_name:
        userId_by_name =  selected_user_by_name.split('-')[1]
        selected_user_by_name = User.objects.get(pk=userId_by_name)
        selected_user_username = selected_user_by_name.username'''
    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date,'%d-%m-%Y').date().strftime('%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date,'%d-%m-%Y').date().strftime('%Y-%m-%d')
    if selected_userId:
        selected_user = User.objects.get(pk=selected_userId)
        selected_user_username = selected_user.username
    if start_date == '' and end_date == '':
        today = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
        end_date = str(today.date())
        start_date = str(today.date() - timedelta(7))
    overall_view = get_overall_task_view(start_date,end_date,selected_user_username)
    data_for_overall_task_view = simplejson.dumps(overall_view)
    task_by_users_priority = get_task_by_users_priority(start_date,end_date,selected_user_username)
    data_for_task_by_users_priority = simplejson.dumps(task_by_users_priority)
    task_trends = get_task_trends(start_date,end_date,selected_user_username)
    data_for_task_trends = simplejson.dumps(task_trends)
    start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d').date().strftime('%d-%m-%Y')
    end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d').date().strftime('%d-%m-%Y')
    return render_response(request, "task_report.html",{'overall_view_data':data_for_overall_task_view,'task_by_users_data':data_for_task_by_users_priority,'task_trends_data':data_for_task_trends,'start_date':start_date,'end_date':end_date,'selected_user':selected_user})

def get_overall_task_view(start_date,end_date,username):
    overall_task_view_data =[]
    if username is not None:
        tasks_data = Task.objects.filter(assignedTo = username,dueDate__gte = start_date , dueDate__lte = end_date)
    else:
        tasks_data = Task.objects.filter(dueDate__gte = start_date , dueDate__lte = end_date)
    open_task = 0
    WIP_task = 0
    Resolved_task = 0
    Closed_task = 0
    for task_data in tasks_data:
        taskStatus = (task_data.taskStatus).lower()
        if taskStatus == 'open':
            open_task += 1
        elif taskStatus == 'wip':
            WIP_task += 1
        elif taskStatus == 'resolved':
            Resolved_task += 1
        elif taskStatus == 'closed':
            Closed_task += 1
    data = {'open_task':open_task,
            'WIP_task':WIP_task,
            'Resolved_task':Resolved_task,
            'Closed_task':Closed_task
            }
    overall_task_view_data.append(data)
    return overall_task_view_data
    
def get_task_by_users_priority(start_date,end_date,username):
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select distinct(assignedTo) from web_task where subject != '' and assignedTo != '' and dueDate >= '"+start_date+"'and dueDate <='"+end_date+"'"
    if username is not None:
        query += "and assignedTo = '"+username+"' "
    query += " group by assignedTo "
    dict_cur.execute(query)
    assignedTo_users= list(dict_cur.fetchall());
    task_by_users_priority_data =[]
    for assignedTo_user in assignedTo_users:
        assignedTo = assignedTo_user['assignedTo']
        tasks_data = Task.objects.filter(dueDate__gte = start_date , dueDate__lte = end_date,assignedTo = assignedTo)
        normal_task = 0
        high_task = 0
        urgent_task = 0
        immediate_task = 0
        for task_data in tasks_data:
            user_obj = User.objects.get(username=task_data.assignedTo)
            if user_obj:
                if user_obj.first_name and user_obj.last_name:
                    username = user_obj.first_name
                    username += ' '+user_obj.last_name
                    userId = str(user_obj.id)
                    username += '-'+userId
                else:
                    username = user_obj.username
            else:
                username = task_data.assignedTo
            priority = (task_data.priority).lower()
            if priority == "normal":
                normal_task += 1
            elif priority == "high":
                high_task += 1
            elif priority == "urgent":
                urgent_task += 1
            elif priority == "immediate":
                immediate_task += 1
        data = {'Normal':normal_task,
                'High':high_task,
                'Urgent':urgent_task,
                'Immediate':immediate_task,
                'username':username
                }
        task_by_users_priority_data.append(data)
    return task_by_users_priority_data

def get_task_trends(start_date,end_date,username):
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select distinct(dueDate) from web_task where  subject != '' and dueDate >= '"+start_date+"'and dueDate <='"+end_date+"'"
    if username is not None:
        query += "and assignedTo = '"+username+"' "
    query += " group by dueDate "
    dict_cur.execute(query)
    dueDates = list(dict_cur.fetchall());
    task_trends_data= []
    for dueDate in dueDates:
        dueDate = dueDate['dueDate']
        if username is not None:
            tasks_data = Task.objects.filter(assignedTo = username,dueDate = dueDate)
        else:
            tasks_data = Task.objects.filter(dueDate = dueDate)
        open_task = 0
        WIP_task = 0
        Resolved_task = 0
        Closed_task = 0
        dueDate = dueDate.date()
        dueDate = str(dueDate)
        dueDate = datetime.datetime.strptime(dueDate,'%Y-%m-%d').strftime('%d-%m-%Y')
        for task_data in tasks_data:
            taskStatus = (task_data.taskStatus).lower()
            if taskStatus == 'open':
                open_task += 1
            elif taskStatus == 'wip':
                WIP_task += 1
            elif taskStatus == 'resolved':
                Resolved_task += 1
            elif taskStatus == 'closed':
                Closed_task += 1
        data = {'Open':open_task,
                'WIP':WIP_task,
                'Resolved':Resolved_task,
                'Closed':Closed_task,
                'dueDate':dueDate
                }
        task_trends_data.append(data)
    return task_trends_data

def center_access(request):
    if request.is_ajax():
        center_id = request.GET.get("center_id",'')
        if center_id:
            try:
                center_obj = Center.objects.get(id=center_id,status='Active')
            except:
                center_obj = None
            if center_obj and center_obj is not None:
                center_access_list = []
                partner_id = None
                partner = Partner.objects.filter(contactperson_id=request.user.id)
                if partner:
                    partner_id = partner[0].id
                if partner_id is not None:
                    centers_access = Center.objects.values_list('id','name').filter(Q(admin_id = request.user.id) | Q(assistant_id = request.user.id) | Q(funding_partner_id = partner_id) | Q(delivery_partner_id = partner_id) | Q(field_coordinator_id = request.user.id) | Q(delivery_coordinator_id = request.user.id)).exclude(id = center_obj.id).exclude(status='Closed')
                else:
                    centers_access = Center.objects.values_list('id','name').filter(Q(admin_id = request.user.id) | Q(assistant_id = request.user.id) | Q(field_coordinator_id = request.user.id) | Q(delivery_coordinator_id = request.user.id)).exclude(id = center_obj.id).exclude(status='Closed')
                if centers_access:
                    for center_access in centers_access:
                        center_access_list.append({'id':center_access[0], 'name':center_access[1]})
            return HttpResponse(simplejson.dumps(center_access_list),mimetype='application/json')
        else:
            return HttpResponse("")
        
@login_required      
def get_rejected_task(request):
    flag = request.GET.get('flag','')
    if flag:
        rejectedTaskList = TaskRejected.objects.all()
        rejectedJsonData =[]
        if len(rejectedTaskList)>0:
            for rejectedTask in rejectedTaskList:
                data = {'taskName':rejectedTask.subject,'dueDate':str(rejectedTask.dueDate),'comment':rejectedTask.comment,'assignTo':rejectedTask.assignedTo,'priority':rejectedTask.priority,'permormedOn_userId':rejectedTask.performedOn_userId,'taskType':rejectedTask.taskType,'taskStatus':rejectedTask.taskStatus,'category':rejectedTask.category}
                rejectedJsonData.append(data)
            return HttpResponse(simplejson.dumps({'rejectedJsonData':rejectedJsonData}),mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'msg':'No data available.'}),mimetype='application/json')
                
@login_required
def get_username(request):
    if request.is_ajax():
        search_term =  request.GET.get('term', '')
        flag_value = request.GET.get('action','')
        term = search_term.split();
        if len(term) > 1:
            usernames = UserActivityHistory.objects.filter((Q(id__icontains=search_term) | Q(username__icontains=search_term) | Q(name__icontains=search_term)))[:20]
        else:
            usernames = UserActivityHistory.objects.filter((Q(id__icontains=search_term) | Q(username__icontains=search_term) | Q(name__icontains=search_term)))[:20]
        user_result = []
        for ent in usernames:
            refer_dict = {}
            refer_dict['id'] = ent.id
            refer_dict['label'] = ''
            if flag_value == 'username':
                if ent.name:
                    refer_dict['label'] = ent.name
                else:
                    refer_dict['label'] = ent.username
            refer_dict['value'] = refer_dict['label']
            user_result.append(refer_dict['value'])
        user_result=list(set(user_result))
        data = json.dumps(user_result)
    else:
        data= 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@login_required
def walloffame(request):
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select teacher_id,id,count(case when date_start >= '2013-01-01' and date_end <'2014-01-01' then 1 end) as 'AY-13-14',"\
    "count(case when date_start >= '2014-01-01' and date_end <'2015-01-01' then 1 end) as 'AY-14-15',count(case when date_start >= '2015-01-01' and date_end <'2016-01-01' then 1 end) as 'AY-15-16',"\
    "count(case when date_start >= '2016-01-01' and date_end <'2017-01-01' then 1 end) as 'AY-16-17',count(case when date_start >= '2017-01-01' and date_end <'2018-01-01' then 1 end) as 'AY-17-18' from web_session where status='Completed' group by teacher_id"
    dict_cur.execute(query)
    teachers = list(dict_cur.fetchall())
    db.close()
    dict_cur.close()
    VolCompThreeYear = []
    VolCompfourYear =[]
    VolCompFiveYear = []
    usersForFiveYearVol = []
    usersForFourYearVol = []
    usersForThreeYearVol = []
    if teachers:
        for teacher in teachers:
            if teacher['AY-13-14'] and teacher['AY-14-15'] and teacher['AY-15-16'] and teacher['AY-16-17'] and teacher['AY-17-18']:
                VolCompFiveYear.append(teacher['teacher_id'])
            elif (teacher['AY-13-14'] and teacher['AY-14-15'] and teacher['AY-15-16'] and teacher['AY-16-17']) or \
            (teacher['AY-13-14'] and teacher['AY-15-16'] and teacher['AY-16-17'] and teacher['AY-17-18']) or \
            (teacher['AY-14-15'] and teacher['AY-15-16'] and teacher['AY-16-17'] and teacher['AY-17-18']) or \
            (teacher['AY-13-14'] and teacher['AY-14-15'] and teacher['AY-16-17'] and teacher['AY-17-18']) or \
            (teacher['AY-13-14'] and teacher['AY-14-15'] and teacher['AY-15-16'] and teacher['AY-17-18']) :
                VolCompfourYear.append(teacher['teacher_id'])
            elif (teacher['AY-13-14'] and teacher['AY-14-15'] and teacher['AY-15-16']) or (teacher['AY-13-14'] and teacher['AY-15-16'] and teacher['AY-17-18']) or \
            (teacher['AY-13-14'] and teacher['AY-15-16']  and teacher['AY-17-18']) or (teacher['AY-14-15'] and teacher['AY-15-16'] and teacher['AY-17-18']) or  \
            (teacher['AY-13-14'] and teacher['AY-16-17'] and teacher['AY-17-18']) or (teacher['AY-14-15'] and teacher['AY-16-17'] and teacher['AY-17-18']) or \
            (teacher['AY-15-16'] and teacher['AY-16-17'] and teacher['AY-17-18']) or (teacher['AY-14-15'] and teacher['AY-15-16'] and teacher['AY-17-18']) or \
            (teacher['AY-13-14'] and teacher['AY-14-15'] and teacher['AY-17-18']) or (teacher['AY-13-14'] and teacher['AY-15-16'] and teacher['AY-17-18']):
                VolCompThreeYear.append(teacher['teacher_id'])
    
    if VolCompFiveYear or VolCompfourYear or VolCompThreeYear:
        if VolCompFiveYear:
            users = User.objects.filter(id__in=VolCompFiveYear)
            for user in users:
                userDetails = UserProfile.objects.values('picture').filter(user_id = user.id)
                if user.first_name and user.last_name:
                    name = user.first_name +' '+user.last_name
                for photo in userDetails:
                    picture = photo['picture']
                    if "/static/profile_images" in picture:
                        picture = ''
                    data = {'id':user.id,
                         'name':name,
                         'picture':picture
                         }
                    usersForFiveYearVol.append(data)
        if VolCompfourYear:
            users = User.objects.filter(id__in=VolCompfourYear)
            for user in users:
                userDetails = UserProfile.objects.values('picture').filter(user_id = user.id)
                if user.first_name and user.last_name:
                    name = user.first_name +' '+user.last_name
                for photo in userDetails:
                    picture = photo['picture']
                    if "/static/profile_images" in picture:
                        picture = ''
                    data = {'id':user.id,
                         'name':name,
                         'picture':picture
                         }
                    usersForFourYearVol.append(data)
        if VolCompThreeYear:
            users = User.objects.filter(id__in=VolCompThreeYear)
            for user in users:
                userDetails = UserProfile.objects.values('picture').filter(user_id = user.id)
                if user.first_name and user.last_name:
                    name = user.first_name +' '+user.last_name
                if user.id == 2572:
                    name = "Prasad Kaggallu"
                if user.id == 3452:
                    name = "Meenakshi Ashok Kumar"
                for photo in userDetails:
                    picture = photo['picture']
                    if "/static/profile_images" in picture:
                        picture = ''
                    data = {'id':user.id,
                         'name':name,
                         'picture':picture
                         }
                    usersForThreeYearVol.append(data)
    return render_response(request,"longServingCitation.html",{'usersForFiveYearVol':simplejson.dumps(usersForFiveYearVol),'usersForFourYearVol':simplejson.dumps(usersForFourYearVol),'usersForThreeYearVol':simplejson.dumps(usersForThreeYearVol)})
    

def dropTeacher(request): 
    center_id = request.GET.get('center_id','')
    teacher_id = request.GET.get('teacher_id','')
    drop_date = request.GET.get('drop_date','')
    offering_id = request.GET.get('offeringId','')
    drop_reason = request.GET.get('drop_reason_val', '')
    drop_category = request.GET.get('drop_category_val', '')
    
    cur_date = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
    if  teacher_id and offering_id and center_id:
        try :
            offering_teacher_mapping=OfferingTeacherMapping.objects.filter(offering_id=offering_id,teacher_id=teacher_id).latest('created_date')
            offering_teacher_mapping.dropped_date=datetime.datetime.strptime(drop_date, "%d-%m-%Y").date()
            offering_teacher_mapping.dropped_reason=drop_reason
            offering_teacher_mapping.dropped_category=drop_category
            offering_teacher_mapping.updated_by_id=request.user.id
            offering_teacher_mapping.save() 
        except:
            offering_teacher_mapping=OfferingTeacherMapping.objects.create(offering_id=offering_id,teacher_id=teacher_id)
            offering_teacher_mapping.dropped_date=datetime.datetime.strptime(drop_date, "%d-%m-%Y").date()
            offering_teacher_mapping.dropped_reason=drop_reason
            offering_teacher_mapping.dropped_category=drop_category
            offering_teacher_mapping.updated_by_id=request.user.id
            offering_teacher_mapping.save() 
        allocatedDemand = Demandslot.objects.filter(status = 'Allocated',
                        center_id = center_id,offering_id = offering_id)
        if len(allocatedDemand)>0:
            allocatedDemand.update(status = 'Unallocated', user = None,date_booked = None)
        drop_date =datetime.datetime.strptime(drop_date, "%d-%m-%Y").date()
        sess = Session.objects.filter(date_start__gte = drop_date, offering__center_id = center_id, teacher_id = teacher_id,offering_id = offering_id,status='scheduled')
        if len(sess)>0:
            sess.update(teacher = None,dt_updated = cur_date,updated_by = request.user)
            userp_id = UserProfile.objects.values_list('id', flat=True).filter(user_id=teacher_id)[0]
            Offering.objects.filter(id = offering_id, status='running', active_teacher=teacher_id).update(updated_date = cur_date,updated_by = request.user)
            if Session.objects.filter(teacher_id = teacher_id).count() <= 0:
                RolePreference.objects.filter(userprofile_id=userp_id,role_id='1').update(role_status='Inactive')
            user_name = User.objects.get(id= teacher_id)
            name = user_name.first_name +' '+ user_name.last_name
            id= teacher_id

            if not name:
                name = request.user.username
            obj =  Offering.objects.filter(center_id = center_id , status = 'running' , id =offering_id )
            centerobj = Center.objects.get(id=center_id)
            first_session_date = Session.objects.filter(offering_id=offering_id).values_list("date_start").order_by('date_start')
            date_first_session = [fsdt[0].strftime("%d-%m-%Y") for fsdt in first_session_date][0]
            usr = User.objects.get(pk=centerobj.delivery_coordinator_id)
            args = {'Id': id, 'Name': name, 'Center': centerobj.name,'Joining': date_first_session, \
                    'Grade':obj[0].course.grade , 'Subject':obj[0].course.subject,'Drop_Date':drop_date ,\
                    'drop_reason':drop_reason,'drop_category':drop_category
                    }
            mail = ''; message = ''
            subject = "Teacher - Drop out Notification Mail"
            from_email = settings.DEFAULT_FROM_EMAIL
            if usr!= 'None':
                cc = [usr.email]
            else:
                cc = []
            
            to = ['smita.singh@evidyaloka.org', 'tabrez.khan@evidyaloka.org']
            if centerobj.admin: to.append(centerobj.admin.email)
            message = get_template('mail/_drop_teacher/drop_template.txt').render(Context(args))
            mail = EmailMessage(subject, message, to=to, from_email=from_email, cc=cc)
            mail.content_subtype = 'html'
            mail.send()
            msg = 'Teacher Dropped Successfully. '+ obj[0].course.grade+'th '+obj[0].course.subject +'('+str(offering_id)+') offering will reflect in backfill as well as in demand page from next scheduled session.'

        else:
            msg = 'There is no future  session  for this offering('+str(offering_id)+')'
            
    else:
        msg = 'Teacher not found.'
    return HttpResponse(simplejson.dumps({'msg':msg}),mimetype='application/json')
    
def demand_task(request):
    dueDate = (datetime.datetime.utcnow()+relativedelta(hours=48, minutes=30))
    comment = request.GET.get('comment','')
    category = request.POST.get('categoryId','')
    subject="Unable to book a demand"
    mail_subject = 'New Task has been Assigned to you.'
    login_user = request.user
    task_id = create_task_for_EVD(request,dueDate,comment,category,subject,mail_subject,46599,login_user,subject,login_user)
    if task_id:
        return HttpResponse(simplejson.dumps({'task_id':task_id}),mimetype='application/json')

def students_log(request):
    return render(request, 'student_log.html',{})

@csrf_exempt
def get_students_log_details(request):
    centerid = request.POST.get('center_id',None)
    status = request.POST.get('status',None)
    offer_count = 0
    offerings = []
    ay_list   = []
    if centerid:
        offer = Offering.objects.filter(center_id = centerid)
        board = Center.objects.get(id = centerid).board
        ay_objs = Ayfy.objects.filter(board = board, types='Academic Year')
        try:
            current_ay = Ayfy.objects.get(board = board, start_date__year = datetime.datetime.now().year, types='Academic Year').id
        except:
            last_year = (datetime.datetime.now()+relativedelta(years=-1)).year
            current_ay = Ayfy.objects.get(board = board, start_date__year = last_year, types='Academic Year').id
        for ay in ay_objs:
            ay_temp = {
            "ay_id" : ay.id,
            "ay_title" : ay.title,
            "ay_board" : ay.board
            }
            ay_list.append(ay_temp)

        offer_count = offer.count()
        if offer_count ==0:
            return HttpResponse('No Running offerings for the selected center.')
    else:
        temp=[]
        board = Offering.objects.filter(active_teacher=request.user)[0].course.board_name
        ay_objs = Ayfy.objects.filter(board = board, types='Academic Year')
        current_ay = Ayfy.objects.get(board=board, start_date__year = datetime.datetime.now().year, types='Academic Year').id
        for ay in ay_objs:
            ay_temp = {
            "ay_id" : ay.id,
            "ay_title" : ay.title,
            "ay_board" : ay.board
            }
            ay_list.append(ay_temp)

        user_sessions = Session.objects.filter(teacher = request.user)
        for sess in user_sessions:
            temp.append(sess.offering)
        offer = set(temp)
        offer_count=len(offer)
        if offer_count==0:
            return HttpResponse('No Running course under your course list.')
    if offer_count!=0:
        for ent in offer:
            if ent.academic_year is not None:
                stud_list = []
                if status is not None:
                    enroll_stud = ent.enrolled_students.filter(status = status)
                else:
                    enroll_stud = ent.enrolled_students.all()
                for  ent1 in enroll_stud:
                    if  ent1.dob:
                        stud_dob =  ent1.dob.strftime('%d/%m/%Y')
                    else:
                        stud_dob = ""
                    if ent1.photo:
                        photo_url = ent1.photo.url
                    else:
                        photo_url = "static/images/noimage.jpg"
                    #getting attendance month wise
                    sa  = SessionAttendance.objects.filter(session__offering=ent).filter(student=ent1)
                    #sa_list = get_month_attend(ent,sa)
                    sa_list = ''
                    student_log = None
                    
                    if status is not None:
                        student_log = ent1.studentlog_set.filter(student_id=ent1.id)
                    if student_log:
                        for student in student_log:
                            achievments_list = get_achievments_list(student.achievments)
                            stud = {
                                "stud_id" : ent1.id,
                                "stud_name" : ent1.name,
                                "stud_grade" : ent1.grade,
                                "stud_dob" : stud_dob,
                                "stud_gender" : ent1.gender,
                                "stud_sch_rollno" : ent1.school_rollno,
                                "stud_photo" : photo_url,
                                "stud_fath_occ" : ent1.father_occupation,
                                "stud_moth_occ" : ent1.mother_occupation,
                                "stud_status"  : ent1.status,
                                "stud_center"  : ent1.center.name,
                                "stud_att"     :  sa_list,
                                "stud_log_curr_schl": student.current_school,
                                "stud_log_curr_grade": student.current_grade,
                                "stud_log_note_prfm": student.notes_onperformance,
                                "stud_log_famliy_income": student.family_income,
                                "stud_log_event_name": student.event_name,
                                "stud_log_event_desc": student.event_description,
                                "stud_log_achivements": achievments_list
                                }
                            stud_list.append(stud)
                    else:
                        stud = {
                        "stud_id" : ent1.id,
                        "stud_name" : ent1.name,
                        "stud_grade" : ent1.grade,
                        "stud_dob" : stud_dob,
                        "stud_gender" : ent1.gender,
                        "stud_sch_rollno" : ent1.school_rollno,
                        "stud_photo" : photo_url,
                        "stud_fath_occ" : ent1.father_occupation,
                        "stud_moth_occ" : ent1.mother_occupation,
                        "stud_status"  : ent1.status,
                        "stud_center"  : ent1.center.name,
                        "stud_att"     :  sa_list
    
                        }
                        stud_list.append(stud)
                temp = {
                    "offer_id" : ent.id,
                    "offer_name" : str(ent.course.board_name)+'  '+ str(ent.course.grade) +' '+ str(ent.course.subject),
                    "offer_stud_count" : ent.enrolled_students.count(),
                    "offer_ay_id" : ent.academic_year.id,
                    "offer_en_stud" : stud_list
                }
                offerings.append(temp)
        return HttpResponse(simplejson.dumps({ "offer_count" :  offer_count, "offerings" : offerings, "ay_list" : ay_list, 'current_ay': current_ay }), mimetype = 'application/json')
    else:
        return HttpResponse('No data') 

def get_achievments_list(achievments)  :
    stud_achievments = []
    json_string = json.loads(achievments)
    for json_achivements in json_string:
        stud_achievments.append(json_achivements)
    return stud_achievments 
      
@csrf_exempt
def save_help(request):
    if request.user.is_authenticated():
        subject = request.GET.get('subject','')
        comment = request.GET.get('comments','')
        taskType = request.GET.get('taskType','')
        dueDate = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)+datetime.timedelta(days=+2)).date()
        createdDate = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
        assignedTo = "pallabi.seal@evidyaloka.org"
        user = request.user

        if assignedTo is not None:
            if request.user.first_name and request.user.last_name:
                performedOn_name = str(request.user.first_name +' '+request.user.last_name) + '-' + str(request.user.id)
            else:
                performedOn_name = str(request.user.username) + '-'+str(request.user.id)
            task =Task(subject=subject,comment=comment,dueDate=dueDate,taskType=taskType,priority='Normal',taskStatus='Open',
                   taskCreatedBy_userId=request.user.username,performedOn_userId=request.user.id,assignedTo=assignedTo,
                   taskCreatedDate=createdDate, user_date_joined=request.user.date_joined,performedOn_name=performedOn_name,
                   task_other_status='')
            task.save()
            taskCreatedDate = datetime.datetime.now()
            todayDate = datetime.datetime.today()
            todayDay = calendar.day_name[todayDate.weekday()]
            recipients = ["pallabi.seal@evidyaloka.org"]
            try:
                user = User.objects.get(username=task.assignedTo)
            except:
                user = ''
            if user:
                email = user.email
                if email:
                    name = user.first_name + ' ' + user.last_name
                    if not name:
                        name = user.username

                    args = {'user': name, 'date': taskCreatedDate, 'subject': subject, 'comment': comment, \
                            'confirm_url': WEB_BASE_URL + "edit_task/?id=" + str(task.id), 'todayDay': todayDay}
                    body_template = 'mail/task/task_full.txt'
                    body = genUtility.get_mail_content(body_template, args)
                    try:
                        thread.start_new_thread(send_email_request_raised, ("New Task has been Assigned to you.", body, settings.DEFAULT_FROM_EMAIL, recipients))
                    except:
                        pass
                    # send_mail("New Task has been Assigned to you.", body, settings.DEFAULT_FROM_EMAIL,recipients)
            return HttpResponse('success')
        return HttpResponse('failure')
    return HttpResponse("error")

def send_email_request_raised(sub,body,settings,recipients):
    send_mail(sub, body,settings,recipients)

def create_Task_autoAlocation(request):
    teacher_id = request.GET.get('teacher','')
    dueDate = (datetime.datetime.utcnow()+relativedelta(hours=48, minutes=30))
    login_user = request.user
    if login_user:
        performedOn_name = str(login_user.first_name) +'  '+ str(login_user.last_name) +'-'+str(login_user.id)
    taskCreatedBy_userId = login_user
    taskCreatedDate = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
    date_joined = None
    todayDate=datetime.datetime.today()
    todayDay=calendar.day_name[todayDate.weekday()]
    teacher = None
    try:
        teacher = User.objects.get(pk=teacher_id)
    except:
        teacher = None
    center = ''
    course = ''
    role_outcome = ''
    if teacher!=None:
        user_profile = teacher.userprofile
        role_preferences = user_profile.rolepreference_set.filter(role__in = user_profile.pref_roles.all())
        if role_preferences:
            role_outcome = role_preferences.filter(role_id=1)[0].role_outcome
        demand_slot = Demandslot.objects.filter(user=teacher)
        for slot in demand_slot:
            center = slot.center.name
            course = slot.offering.course.subject
    try:
        usrobj = User.objects.get(pk=19064)
        date_joined = usrobj.date_joined
    except:
        usrobj = None
    task = Task(comment='' +str(teacher.first_name+' '+teacher.last_name)+' - has booked a demand in'+' '+str(center)+' for ' +str(course)+'.The Role Outcome of the volunteer is' +' '+str(role_outcome)+' Please complete the onboarding steps.',subject='New Task has been Assigned to you ',assignedTo=usrobj,dueDate=dueDate,priority="Normal",
               taskCreatedBy_userId=taskCreatedBy_userId,taskStatus="Open",performedOn_userId = usrobj.id,
                taskCreatedDate=taskCreatedDate, user_date_joined=date_joined,performedOn_name=performedOn_name,
                taskType="SYSTEM")
    task.save()
    subject = "New Task has been Assigned to you"
    recipients = []
    from_email = settings.DEFAULT_FROM_EMAIL
    name = ''
    if teacher:
        if teacher.first_name:
            name = teacher.first_name+' '+teacher.last_name
            if not name:
                name = teacher.username
    to = ['sushreeta.mohapatra@evidyaloka.org']

    ctx = {'user':name,'date':taskCreatedDate,'subject' : 'New Task has been Assigned to you ', 'comment': '', \
                        'confirm_url':WEB_BASE_URL+"edit_task/?id=" + str(task.id),
                        'todayDay':todayDay,'center':center,'course':course,'role_outcome':role_outcome}
    message = get_template('mail/task/center_task.txt').render(Context(ctx))
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()  
    return HttpResponse(simplejson.dumps({'msg':'Task Created Successfully for Vol_Co-Ordinator'}), mimetype = 'application/json')

def confirm_demand(request):
    center_id = request.GET.get('center_id','')
    offering_id = request.GET.get('offering_id','')
    start_date = request.GET.get('startDate','')
    end_date = request.GET.get('endDate','')
    prefered_days = request.GET.get('pref_days','')
    prefered_timings = request.GET.get('pref_time','')
    teacher = request.GET.get('teacher','')
    software_link = request.GET.get('software_link','')
    demandSlots = Demandslot.objects.filter(user_id=teacher)
    slots = ''
    if teacher:
        user=User.objects.get(pk=teacher)
        teacher_id=user.id
    if offering_id and teacher_id:
        demand_slot=Demandslot.objects.filter(user_id=teacher_id,offering_id=offering_id)
        demand_slot_id=demand_slot.values_list('id',flat=True)
        demand_slot_mapped_ids=map(int,demand_slot_id)
        try:
            offering_teacher_mapping=OfferingTeacherMapping.objects.filter(offering_id=offering_id,teacher_id=teacher_id).latest('created_date')
            offering_teacher_mapping.demand_slot_id=demand_slot_mapped_ids
            offering_teacher_mapping.confirmation_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
            offering_teacher_mapping.assigned_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
            offering_teacher_mapping.updated_by_id=request.user.id
            offering_teacher_mapping.save()
        except:
            offering_teacher_mapping=OfferingTeacherMapping.objects.create(offering_id=offering_id,teacher_id=teacher_id)
            offering_teacher_mapping.demand_slot_id=demand_slot_mapped_ids
            offering_teacher_mapping.confirmation_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
            offering_teacher_mapping.assigned_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
            offering_teacher_mapping.updated_by_id=request.user.id
            offering_teacher_mapping.save()
    if demandSlots:
        slot_details = demandSlots.values_list('center__name','day','start_time','end_time')
        i = 0
        for slot in slot_details:
            if i==0:
                slots+=str(slot[1])+' '+str(slot[2])+' to '+str(slot[3])
            else:
                slots+= ' and '+str(slot[1])+' '+str(slot[2])+' to '+str(slot[3])
            i+=1
    tchr_email = ''
    teacher_name = ''
    teacher_id = None
    tchr = None
    if teacher:
        tchr = User.objects.get(pk=teacher)
        tchr_email = tchr.email
        teacher_id = tchr.id
        if tchr.first_name:
            teacher_name = str(tchr.first_name)+' '+str(tchr.last_name)
        else:
            teacher_name =  tchr.username
    usr = request.user
    name = center_name =subject_name =grade = dc_email = ''
    dc = None
    performed_on = None
    center_admin = None
    if center_id:
        center = Center.objects.get(pk=center_id)
        center_name = center.name
        if center.admin :
            center_admin = center.admin
        dc = center.delivery_coordinator
        if dc:
            dc_email = dc.email
    if offering_id:
        offering = Offering.objects.get(pk=offering_id)
        subject_name = offering.course.subject
        grade = offering.course.grade
    if usr.first_name and usr.last_name:
        name = str(usr.first_name)+' '+str(usr.last_name)
    else:
        name =  usr.username
    btn_type = 'confirm'
    reason = ''
    dueDate = datetime.datetime.utcnow()+timedelta(days=int(3))
    comment = ''
    category = ''
    if dc!=None:
        performed_on = dc
    else:
        performed_on = center_admin
    #.....................calling method to allocate demand to user.....................
    vol_cor = User.objects.get(pk=19064)
    data = confirm_reject_slot(usr,btn_type,center_id,offering_id,reason,request)
    subject = 'Your allocation of the selected course (offering Id -'+str(offering_id)+" ) - "+str(subject_name)+' is Confirmed '
    #create_task_for_EVD(request,dueDate,comment,category,subject,'New Task has been Assigned to you.',19064,tchr,'Your allocation of the selected course is Confirmed',vol_cor)
    
    #WEB_BASE_URL ='https://dev.evidyaloka.org/'
    accept_url = WEB_BASE_URL+'v2/accept_decline_mail?userId='+str(teacher) +'&center_id='+str(center_id)+'&offering_id='+str(offering_id)+'&startDate='+str(start_date)+'&endDate='+str(end_date)+'&pref_days='+str(prefered_days)+'&pref_time='+str(prefered_timings)+'&software_link='+software_link
    decline_url = WEB_BASE_URL+'v2/release_demand?center='+str(center_name)+'&teacher='+str(teacher)+'&slot='+str(slots)+'&flag=true' 
    subject = "Action required on your chosen eVidyaloka opportunity"
    to = [tchr_email]
    from_email = settings.DEFAULT_FROM_EMAIL
    cc = [dc_email]
    cc.append("surya.r@evidyaloka.org")
    ctx = {'user':teacher_name,'center_name':center_name,'subject':subject_name,'grade':grade,'accept_url':accept_url,'decline_url':decline_url,'slots':slots }
    message = get_template('mail/accept_or_declineDemand.html').render(Context(ctx))
    msg = EmailMessage(subject, message, to=to, from_email=from_email,cc=cc)
    msg.content_subtype = 'html'
    msg.send()  
    current_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
    assign_to = None
    if dc!=None:
        assign_to = dc
    else:
        assign_to = center_admin
    demand_tasks = Task.objects.filter(assignedTo = assign_to,performedOn_userId = teacher_id,subject='User has been booked demand',taskStatus='Open').order_by('taskCreatedDate')
    if len(demand_tasks)>0:
        Task.objects.filter(id=demand_tasks[0].id).update(taskStatus='Closed',taskUpdatedDate = current_date)
        
    return HttpResponse(simplejson.dumps({'msg':'Mail has been sent to volunteer to accept or decline demand'}), mimetype = 'application/json')


@csrf_exempt
def accept_decline_mail(request):
    userId = request.GET.get('userId','')
    center_id = request.GET.get('center_id','')
    offering_id = request.GET.get('offering_id','')
    start_date = request.GET.get('startDate','')
    end_date = request.GET.get('endDate','')
    _pref_days = request.GET.get('pref_days','')
    pref_slots = request.GET.get('pref_time','')
    software_link = request.GET.get('software_link','')
    usr = None
    teacher_name = ''
    center_name = ''
    teacher_email = ''
    dc_email = ''
    ca_email = ''
    vol_admin_email=''
    assistant_email = ''
    delivery_coordinator = None
    center_admin = None
    center_details = ''
    assistant = None
    assistant_details = ''
    
    
    if offering_id and userId:
        try :
            offering_teacher_mapping=OfferingTeacherMapping.objects.filter(offering_id=offering_id,teacher_id=userId).latest('created_date')
            offering_teacher_mapping.assigned_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
            offering_teacher_mapping.updated_by_id=request.user.id
            offering_teacher_mapping.save() 
        except :
            offering_teacher_mapping=OfferingTeacherMapping.objects.create(offering_id=offering_id,teacher_id=userId)
            offering_teacher_mapping.assigned_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
            offering_teacher_mapping.updated_by_id=request.user.id
            offering_teacher_mapping.save() 
    if center_id:
        try:
            center = Center.objects.get(pk=center_id)
            center_name = center.name
            if center.admin!=None:
                center_admin = center.admin
                ca_email = center_admin.email
                center_details = UserProfile.objects.get(user_id = center.admin.id)
            if center.delivery_coordinator!=None:
                delivery_coordinator = center.delivery_coordinator
                dc_email = delivery_coordinator.email
            if center.assistant!=None:
                assistant_email = center.assistant.email
                assistant = center.assistant
                assistant_details = UserProfile.objects.get(user_id = center.assistant.id)
        except:
            center_name = ''
    if userId:
        usr = User.objects.get(pk=userId)
        username = usr.username
        teacher_email = usr.email
        if usr.first_name:
            teacher_name = str(usr.first_name)+" "+(usr.last_name)
        else:
            teacher_name = usr.username
        btn_type = 'confirm'
        reason = ''
        demand = Demandslot.objects.filter(user = usr,status='Allocated',offering_id=int(offering_id))
        sess = Session.objects.filter(offering_id = offering_id)
        offer_data = ''
        offeringObj = None
        teacher_subject = ''
        grade = ''
        subject = ''
        days = ''
        try:
           offeringObj = Offering.objects.get(pk=offering_id)
           offer_data = str(offeringObj.course.grade)+'th '+str(offeringObj.course.subject)+', '+str(make_date_time(offeringObj.start_date)["date"])+ ", "+str(make_date_time(offeringObj.start_date)["year"]) +' to '+str(make_date_time(offeringObj.end_date)["date"])+','+str(make_date_time(offeringObj.end_date)["year"])
           teacher_subject = str(offeringObj.course.grade)+'th '+str(offeringObj.course.subject)
           grade = offeringObj.course.grade
           subject = offeringObj.course.subject
        except:
           offeringObj = None
        if offeringObj and offeringObj.active_teacher_id is not None:
                return redirect('/myevidyaloka/?SessionCreated=true')   
        if len(demand)>0:
            sess_arr = add_dynamic_session_accept(userId,offering_id,start_date,end_date,2,software_link,_pref_days,pref_slots,'true',request)
            subject1 = "Welcome on-board as a teacher in "+str(center_name)
            to = [teacher_email]
            from_email = settings.DEFAULT_FROM_EMAIL
            cc = [ca_email,assistant_email]
            content_admins = AlertUser.objects.filter(role__name='vol_admin')
            content_admins = content_admins[0].user.all()
            if content_admins:
                cc.extend([user.email for user in content_admins])
            
            ctx1 = {'user':teacher_name,'center_name':center_name,'subject':teacher_subject}
            message1 = get_template('mail/teacher_on_board.txt').render(Context(ctx1))
            msg1 = EmailMessage(subject1, message1, to=to, from_email=from_email,cc=cc)
            msg1.content_subtype = 'html'
            with open('mail/_offer_accepted/eV_circle_time.pdf', 'rb') as pdf:
                msg1.attach('eV Circle Time.pdf', pdf.read())
            msg1.send()
            i = 0
            for slot in demand:
                
                if len(demand)==i:
                    days+=str(slot.day)
                else:
                    days+=str(slot.day)+' , '
                i+=1
                
            subject2 = "eVidyaloka Class Kit-Connect with your Class"
            ctx2 = {'user':teacher_name,'dc':delivery_coordinator,'center':center,'center_details':center_details,
                    'grade':grade,'subjects':subject,'days':days,'assistant':assistant,'assistant_details':assistant_details}
            message2 = get_template('mail/eVidyaloka_classKit.html').render(Context(ctx2))
            msg2 = EmailMessage(subject2, message2, to=to, from_email=from_email,cc=cc)
            msg2.content_subtype = 'html'
            msg2.send()
            current_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))

            vol_co = User.objects.get(pk=19064)
            demand_tasks = Task.objects.filter(assignedTo = vol_co,performedOn_userId = usr.id,subject='Your allocation of the selected course is Confirmed',taskStatus='Open').order_by('taskCreatedDate')
            if len(demand_tasks)>0:
                Task.objects.filter(id=demand_tasks[0].id).update(taskStatus='Closed',taskUpdatedDate = current_date)
            return HttpResponseRedirect('/myevidyaloka/?offering='+str(offering_id)+'&teacher='+str(userId))
        else:
            return redirect('/myevidyaloka/?demandRelease=false')
        
@csrf_exempt    
def callMedia(request):
    if request.user.is_authenticated:
        role_list = ['Teacher','Center Admin','Content Developer' ,'Content Admin']
        user_profile = UserProfile.objects.filter(Q(user__is_active=True) & Q(pref_roles__name__in=role_list) & Q(user=request.user)).distinct()
        if user_profile:
            user_profile = user_profile[0].rolepreference_set.filter(role_outcome='Recommended')
            if user_profile and len(user_profile)>0:
                username = request.user.username.split("@")[0] + str(request.user.id)
                passw = base64.b64encode(WIKI_PASS)
                try:
                    wiki_user = UserWikividya.objects.get(wiki_username=username)
                except UserWikividya.DoesNotExist:
                    createdDate = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
                    wiki_user = UserWikividya(user=request.user, user_password=passw, wiki_username=username, created_by=request.user.username, created_date=createdDate).save()
                wiki_user = UserWikividya.objects.get(wiki_username=username)
                if wiki_user:
                    passw = base64.b64decode(wiki_user.user_password)
                    final_response = auto_login_wikividya(WIKI_BASE_URL, username, passw, False)
                    result = final_response.json()['login']['result']
                    if result=='NotExists':
                        create_wikividya_account(WIKI_BASE_URL, username, passw)
                    final_response = auto_login_wikividya(WIKI_BASE_URL, username, passw, True)
                    if final_response.json()['login']['result'] == 'NeedToken':
                        return HttpResponse(final_response.json()['login']['token']+"__"+str(final_response.cookies)+"__"+username+","+passw )
    return HttpResponse(WIKI_FAILURE_MESSAGE)

    
def getCenterNameByStateType(request):
    
    if request.is_ajax():
        state_id = request.GET.get('state_name','')
        partner = request.GET.get('partner', '-1')
        delivery_coordinator=request.GET.get('id_delivery_coord', '-1')
        data = centers = []
        all_centers = getAllCenters(request)
        
        if state_id != 'All':
            center =  all_centers.filter(state = state_id,status = 'Active' ).order_by('name')
        elif state_id == 'All':
            center =  all_centers.filter(status = 'Active' ).order_by('name')
        if partner and partner !='All':
            if partner != '-1':
                center = center.filter(delivery_partner_id=int(partner)).distinct()
        if delivery_coordinator and delivery_coordinator !='All':
            if delivery_coordinator!='-1':
                center = center.filter(delivery_coordinator_id=int(delivery_coordinator)).distinct()
        for center_name in center:
            data = { "center":center_name.name, "center_id":center_name.id,"state":center_name.state,
                       'partnerid':center_name.delivery_partner_id, 'partner_name':center_name.delivery_partner.name_of_organization,'del_coordinator_id':center_name.delivery_coordinator_id,"del_coord_name":((str(center_name.delivery_coordinator.first_name)+" "+str(center_name.delivery_coordinator.last_name))if center_name.delivery_coordinator else '')}
            centers.append(data)
               
        return HttpResponse(simplejson.dumps(centers), mimetype = 'application/json')
   
def created_Session(request):
    offering_id = request.GET.get('offering','')
    teacher_id  = request.GET.get('teacher','')
    offer_data = ''
    offeringObj = None
    teacherObj = None
    if teacher_id:
        try:
            teacherObj = User.objects.get(pk=teacher_id)
        except:
            teacherObj = None
    if teacherObj!=None:
        user_p = teacherObj.userprofile
        role_pref = user_p.rolepreference_set.filter(role = 1)
        if role_pref:
            role_pref = role_pref[0]
            if role_pref.role_status == 'New':
                role_pref.role_status = 'Active'
                role_pref.save()
    try:
        offeringObj = Offering.objects.get(pk=offering_id)
        offer_data = str(offeringObj.course.grade)+'th '+str(offeringObj.course.subject)+', '+str(make_date_time(offeringObj.start_date)["date"])+ ", "+str(make_date_time(offeringObj.start_date)["year"]) +' to '+str(make_date_time(offeringObj.end_date)["date"])+','+str(make_date_time(offeringObj.end_date)["year"])
        teacher_subject = str(offeringObj.course.grade)+'th '+str(offeringObj.course.subject)
    except:
        offeringObj = None
    session_arr = []
    if offering_id and teacher_id:
        sess_list = Session.objects.filter(teacher = teacher_id,offering = offering_id).order_by('id')
        for session in sess_list:
            session_arr.append(make_number_verb(session.offering.course.grade) + ' ' + session.offering.course.subject + ' ' + session.offering.center.name + ' - ' + make_date_time(session.date_start)["date"] + ' ' + make_date_time(session.date_start)["time"])
        return HttpResponse(simplejson.dumps({'session_arr':session_arr,'offer_data':offer_data}), mimetype = 'application/json')

def prefDaysAndPrefSlots(request):
    teacher_id  = request.GET.get('teacher', None)
    offering_id  = request.GET.get('offering_id', None)
    slot_list = []
    if teacher_id:
        teacher = get_object_or_none(User, id=teacher_id)
    if teacher !=None:
        slots = Demandslot.objects.filter(user=teacher, offering_id=offering_id,  status='Booked')
        for slot in slots:
            days_mapping_for_user = {'Monday':'Mon', 'Tuesday':'Tue', 'Wednesday':'Wed', 'Thursday':'Thu', 'Friday':'Fri', 'Saturday':'Sat', 'Sunday':'Sun'}
            data = {'day':days_mapping_for_user[slot.day],'times':str(slot.start_time)+'-'+str(slot.end_time)}
            slot_list.append(data)
    return HttpResponse(simplejson.dumps(slot_list), mimetype = 'application/json')


def custom_login(request):
    try :
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        return HttpResponse("Success")
    except :
        return HttpResponse("Failure")
    
@csrf_exempt     
def getCentesByState(request):
    
    state = request.GET.get('state', '-1')
    partner = request.GET.get('partner', '-1')
    funding_partner=request.GET.get('id_fund_partner', '-1')
    all_centers = getAllCenters(request)
    total_centers = all_centers.filter(delivery_partner_id=partner,state=state).distinct().order_by('name')
    total_centers = len(total_centers)

    if all_centers !=None:
        for center in all_centers:
            all_centers = all_centers.values('id','name','state','delivery_partner_id','delivery_partner__name_of_organization','funding_partner_id','funding_partner__name_of_organization').distinct().order_by('name')
    all_centers_donors = all_centers.all().distinct().order_by('name')
    centers = []
    if state != str('-1'):
        all_centers = all_centers.filter(state=state).distinct().order_by('name')
    if total_centers != 0:
        all_centers = all_centers.filter(delivery_partner_id=partner).distinct().order_by('name')
    if partner != str('-1'):
        all_centers = all_centers.filter(delivery_partner_id=partner).distinct().order_by('name')
    if funding_partner != str('-1'):
        all_centers = all_centers.filter(funding_partner_id=funding_partner).distinct().order_by('name')
        for center in all_centers_donors:
            centers.append({'id':'undefined','name':'undefined','state':'undefined','partnerid':'undefined','partner_name':'undefined','fundingpartner_id':center['funding_partner_id'],'fundingpartner_name':center['funding_partner__name_of_organization']})
    for center in all_centers:
        centers.append({'id':center['id'],'name':center['name'],'state':center['state'],'partnerid':center['delivery_partner_id'],'partner_name':center['delivery_partner__name_of_organization'],'fundingpartner_id':center['funding_partner_id'],'fundingpartner_name':center['funding_partner__name_of_organization']})
    # centers = [center for center in reversed(centers)]
    return HttpResponse(simplejson.dumps(centers), mimetype = 'application/json')

@csrf_exempt
def getSummaryData(request):
    
    state = request.GET.get('state','-1')
    [center_id] = request.GET.getlist('center_id', -1)
    center_id = center_id.strip('][').split(', ')
    if int(center_id[0]) == -1:
        center_id = -1
    # center_data = int(request.GET.get('center_data', -1))
    partner_id = int(request.GET.get("partner_id","-1"))
    funding_partner_id=int(request.GET.get("funding_partner_id","-1"))
    date_start = datetime.datetime.strptime(request.GET.get("date_start") ,"%d-%m-%Y")
    date_end = datetime.datetime.strptime(request.GET.get("date_end") ,"%d-%m-%Y")
    ay_id= request.GET.get("ay_id","")
    all_centers = getAllCenters(request)
    if center_id != -1:
        all_centers = all_centers.filter(id__in = center_id) 
    elif state != str('-1'):
        all_centers = all_centers.filter(state=state)
    if partner_id != -1:
        all_centers = all_centers.filter(delivery_partner_id=partner_id).distinct().order_by('name')
    if funding_partner_id != -1:
        all_centers = all_centers.filter(funding_partner_id=funding_partner_id).distinct().order_by('name')
    if ay_id:
        for center in all_centers:
            if center.offering_set.filter(academic_year__title=ay_id):
                pass
            else:
                all_centers.exclude(id=center.id)
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    global_data = {'center_count':0, 'teacher_count' : 0,'active_teacher_count' : 0,'active_offering_count' : 0, 'total_student' : 0, 'planvsact' : 0, 'child_attend': 0}
    center_ids = all_centers.values_list('id',flat=True)
    center_ids = ','.join(map(str, center_ids)) 
    idList = center_ids.split(",")
    myCenterId=''
    i=0;
    if len(idList) > 0 : 
        for ids in idList:
            myCenterId+= "'"+ids+"'"
            i=i+1;
            if i < len(idList) :
                myCenterId += ","
    #query = "select count(distinct(teacher_id)) as unique_teachers_count from web_session ws join web_offering wo on wo.id=ws.offering_id where DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' and wo.center_id in ("+str(center_ids)+") and ((DATE(start_date)<='"+str(date_start)+"' and DATE(end_date) >= '"+str(date_start)+"') OR (DATE(start_date)<='"+str(date_end)+"' and DATE(end_date) >= '"+str(date_end)+"')) and (teacher_id is not null or teacher_id != '')"
    query = "select count(distinct(teacher_id)) as unique_teachers_count from web_session ws join web_offering wo on wo.id=ws.offering_id  join web_ayfy on wo.academic_year_id=web_ayfy.id where DATE(ws.date_start)>='"+str(date_start)+"' and DATE(ws.date_start)<='"+str(date_end)+"'  and web_ayfy.title='"+str(ay_id)+"' and wo.center_id in ("+str(myCenterId)+") and (teacher_id is not null or teacher_id != '' )"
    dict_cur.execute(query)
    unique_teachers_count = dict_cur.fetchall()
    global_data['teacher_count'] = unique_teachers_count[0]['unique_teachers_count']
    
    query = "select count(distinct(web_sessionattendance.id)) as attendance_count from \
             web_sessionattendance join web_session on web_session.id=web_sessionattendance.session_id \
             join web_offering on web_offering.id=web_session.offering_id \
              join web_ayfy on web_offering.academic_year_id=web_ayfy.id\
             where web_offering.center_id in ("+str(myCenterId)+") \
              and web_ayfy.title='"+str(ay_id)+"'\
             and (DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' )"
    
    dict_cur.execute(query)
    total_count = dict_cur.fetchall()[0]
    attendance_count = total_count['attendance_count']
    
    query = "select count(distinct(woes.student_id)) as student_count from web_offering wo ,web_session ws ,web_offering_enrolled_students woes \
            where wo.id = woes.offering_id and ws.offering_id = wo.id and (DATE(ws.date_start)>='"+str(date_start)+"' \
            and DATE(ws.date_start)<='"+str(date_end)+"') and wo.center_id in ("+str(myCenterId)+")" 
    dict_cur.execute(query)
    total_count = dict_cur.fetchall()[0]
    global_data['total_student'] = total_count['student_count']
    
    
    query = "select count(distinct(web_session.id)) as total_session from web_session \
             join web_offering on web_offering.id=web_session.offering_id \
             where DATE(web_session.date_start)>='" +str(date_start)+"' \
             and DATE(web_session.date_start)<='"+str(date_end)+"' \
             and web_offering.center_id in ("+str(myCenterId)+") \
             and (teacher_id is not null or teacher_id !='') "
    dict_cur.execute(query)
    total_sessions = dict_cur.fetchall()[0]['total_session']
    if total_sessions>0:
        query = "select count(distinct(web_session.id)) as completed_session from web_session \
         join web_offering on web_offering.id=web_session.offering_id where DATE(web_session.date_start)>='"+str(date_start)+"' \
         and DATE(web_session.date_start)<='"+str(date_end)+"' and web_offering.center_id in ("+str(myCenterId)+") \
         and (web_session.status='Completed' or web_session.status='completed') and (teacher_id is not null or teacher_id != '')"
        #and ((DATE(start_date)<='"+str(date_start)+"' and DATE(end_date) >= '"+str(date_start)+"') OR (DATE(start_date)<='"+str(date_end)+"' and DATE(end_date) >= '"+str(date_end)+"')) and 
        dict_cur.execute(query)
        completed_sessions = dict_cur.fetchall()[0]['completed_session']
        global_data['planvsact'] = round(((float(completed_sessions)/total_sessions)*100),1)
    if attendance_count>0:
        query = "select count(distinct(web_sessionattendance.id)) as present_student from web_sessionattendance \
        join web_session on web_session.id=web_sessionattendance.session_id join \
        web_offering on web_offering.id=web_session.offering_id join web_ayfy on web_offering.academic_year_id=web_ayfy.id\
        where DATE(date_start)>='"+str(date_start)+"' \
        and DATE(date_start)<'"+str(date_end)+"' and web_offering.center_id in ("+str(myCenterId)+") \
         and web_ayfy.title='"+str(ay_id)+"'\
        and web_sessionattendance.is_present='yes' and (teacher_id is not null or teacher_id != '')"
        dict_cur.execute(query)
        present_student = dict_cur.fetchall()[0]['present_student']
        global_data['child_attend'] = int(round(((float(present_student)/attendance_count)*100 ),2))
    #query = "select count(distinct(wo.center_id)) as center_count from web_offering wo join web_center wc on wo.center_id=wc.id where wc.status='Active' and ((DATE(wo.start_date)<='"+str(date_start)+"' and DATE(wo.end_date) >= '"+str(date_start)+"') OR (DATE(wo.start_date)<='"+str(date_end)+"' and DATE(wo.end_date) >= '"+str(date_end)+"')) "
#     query ="select count(distinct (wc.id)) as center_count from web_session ws join web_offering wo on wo.id=ws.offering_id join web_center wc on wc.id=wo.center_id  join auth_user au on au.id=ws.teacher_id  and wc.status='Active'and DATE(ws.date_start)>='"+str(date_start)+"'and DATE(ws.date_start)<='"+str(date_end)+"' and wc.id in ("+str(myCenterId)+") "
    """if state != '-1':
        query += " and wc.id in ("+str(center_ids)+") """
#     dict_cur.execute(query)
#     center_count = dict_cur.fetchall()[0]['center_count']
    if len(idList):
        if len(idList[0])>0 : 
            center_count = len(idList)
            if center_count:
                global_data['center_count'] = center_count
    active_offering_teacher = Session.objects.values_list('offering_id','offering__active_teacher_id').filter(
                              offering__status='running',offering__active_teacher__isnull = False,
                              offering__center__in = all_centers,date_start__range = [str(date_start),str(date_end)])
    active_teacher = []
    active_offering = []
    for data in active_offering_teacher:
        active_offering.append(data[0])
        active_teacher.append(data[1])
        
    global_data ['active_teacher_count'] = len(list(set(active_teacher)))
    global_data ['active_offering_count'] = len(list(set(active_offering)))
    db.close()
    dict_cur.close()
    return HttpResponse(simplejson.dumps(global_data), mimetype = 'application/json')
    
@csrf_exempt
def getStatsClassesData(request):
    
    [center_id] = request.GET.getlist('center_id', -1)
    center_id = center_id.strip('][').split(', ')
    if int(center_id[0]) == -1:
        center_id = -1
    state = request.GET.get("state","-1")
    partner_id = int(request.GET.get("partner_id","-1"))
    funding_partner_id=int(request.GET.get("funding_partner_id","-1"))
    time_start = request.GET.get("time_start"," ")
    time_end = request.GET.get("time_end"," ")
    date_start = datetime.datetime.strptime(request.GET.get("date_start") ,"%d-%m-%Y")
    date_start = str(date_start).split(' ')[0]
    date_end = datetime.datetime.strptime(request.GET.get("date_end") ,"%d-%m-%Y")
    date_end= str(date_end).split(' ')[0]
    ay_id= request.GET.get("ay_id","")
    type = request.GET.get("type")
    all_centers = getAllCenters(request)
    if center_id != -1:
        all_centers = all_centers.filter(id__in=center_id) 
    elif state != str('-1'):
        all_centers = all_centers.filter(state=state)
    if partner_id != -1:
        all_centers = all_centers.filter(delivery_partner_id=partner_id).distinct().order_by('name')
    if funding_partner_id != -1:
        all_centers = all_centers.filter(funding_partner_id=funding_partner_id).distinct().order_by('name')
    if ay_id:
        for center in all_centers:
            if center.offering_set.filter(academic_year__title=ay_id):
                pass
            else:
                all_centers.exclude(id=center.id)
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    center_ids = all_centers.values_list('id',flat=True)
    center_ids = ','.join(map(str, center_ids))
    idList = center_ids.split(",")
    myCenterId=''
    i=0;
    if len(idList) > 0 : 
        for ids in idList:
            myCenterId+= "'"+ids+"'"
            i=i+1;
            if i < len(idList) :
                myCenterId += ","
    if type == "cancell_reasons":
        #query = "select count(web_session.id) as session_cancellReason_count, cancel_reason from web_session join web_offering on web_offering.id=web_session.offering_id where DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' and web_offering.center_id in ("+str(center_ids)+") and (teacher_id is not null or teacher_id !='') and (cancel_reason is not null or cancel_reason!='') and ((DATE(start_date)<='"+str(date_start)+"' and DATE(end_date) >= '"+str(date_start)+"') OR (DATE(start_date)<='"+str(date_end)+"' and DATE(end_date) >= '"+str(date_end)+"')) group by cancel_reason"
        query = "select count(web_session.id) as session_cancellReason_count, cancel_reason from web_session join web_offering on web_offering.id=web_session.offering_id join web_ayfy on web_offering.academic_year_id=web_ayfy.id where DATE(web_session.date_start)>='"+str(date_start)+"'and TIME(web_session.date_start)>='"+str(time_start)+"' and DATE(web_session.date_end)<='"+str(date_end)+"'and TIME(web_session.date_end)<='"+str(time_end)+"' and web_offering.center_id in ("+str(myCenterId)+") and (teacher_id is not null or teacher_id !='') and (cancel_reason is not null or cancel_reason!='')and web_ayfy.title='"+str(ay_id)+"'  group by cancel_reason"
    else:
        #query = "select count(web_session.id) as session_status_count, web_session.status from web_session join web_offering on web_offering.id=web_session.offering_id where DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' and web_offering.center_id in ("+str(center_ids)+") and (teacher_id is not null or teacher_id !='') and ((DATE(start_date)<='"+str(date_start)+"' and DATE(end_date) >= '"+str(date_start)+"') OR (DATE(start_date)<='"+str(date_end)+"' and DATE(end_date) >= '"+str(date_end)+"')) group by web_session.status"
        query = "select count(web_session.id) as session_status_count, web_session.status from web_session join web_offering on web_offering.id=web_session.offering_id join web_ayfy on web_offering.academic_year_id=web_ayfy.id  where DATE(web_session.date_start)>='"+str(date_start)+"' and TIME(web_session.date_start)>='"+str(time_start)+"' and DATE(web_session.date_end)<='"+str(date_end)+"'and TIME(web_session.date_end)<='"+str(time_end)+"' and web_offering.center_id in ("+str(myCenterId)+") and(teacher_id is not null or teacher_id !='')   and web_ayfy.title='"+str(ay_id)+"' group by web_session.status"
    dict_cur.execute(query)
    status_count = dict_cur.fetchall()
    db.close()
    dict_cur.close()
    return HttpResponse(simplejson.dumps(status_count), mimetype = 'application/json')

    
@csrf_exempt
def getCenterOfferingDetails(request):
    
    [center_id] = request.GET.getlist('center_id', -1)
    center_id = center_id.strip('][').split(', ')
    center_id = [str(id) for id in center_id]
    if int(center_id[0]) == -1:
        center_id = -1
    state = request.GET.get("state","-1")
    partner_id = int(request.GET.get("partner_id","-1"))
    funding_partner_id=int(request.GET.get("funding_partner_id","-1"))
    date_start = datetime.datetime.strptime(request.GET.get("date_start") ,"%d-%m-%Y")
    date_end = datetime.datetime.strptime(request.GET.get("date_end") ,"%d-%m-%Y")
    all_centers = getAllCenters(request)
    ay_id = request.GET.get("ay_id","")
    if center_id != -1:
        all_centers = all_centers.filter(id__in=center_id) 
    elif state != str('-1'):
        all_centers = all_centers.filter(state=state)
    if partner_id != -1:
        all_centers = all_centers.filter(delivery_partner_id=partner_id).distinct().order_by('name')
    if funding_partner_id != -1:
        all_centers = all_centers.filter(funding_partner_id=funding_partner_id).distinct().order_by('name')
    if ay_id:
        for center in all_centers:
            if center.offering_set.filter(academic_year__title=ay_id):
                pass
            else:
                all_centers.exclude(id=center.id)
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    data = []
    if center_id == -1:
        for center in all_centers:
            query = "select count(distinct(web_offering.id)) as offering_count,\
                    count(distinct(web_session.id)) as planned_session,\
                    count(case when web_session.status in ( 'completed') then 1 end) actual_session,count(case when web_session.status = 'offline' then 1 end) offline_session,  count(case when web_session.status = 'cancelled' then 1 end) cancelled_session from web_session \
                    join web_offering on web_offering.id=web_session.offering_id \
                    where DATE(web_session.date_start)>='"+str(date_start)+"' and DATE(web_session.date_start)<='"+str(date_end)+"' \
                    and web_offering.center_id in ("+str(center.id)+") and (active_teacher_id is not null or active_teacher_id !='')"
            dict_cur.execute(query)
            session_details = dict_cur.fetchall()
            query = "select count(distinct(student_id)) as unique_student_count, \
                     count(web_sessionattendance.is_present) as student_count, \
                     count(case when web_sessionattendance.is_present = 'yes' then 1 end) Present  \
                     from web_sessionattendance join web_session on web_session.id=web_sessionattendance.session_id \
                     join web_offering on web_offering.id=web_session.offering_id \
                     where (DATE(web_session.date_start)>='"+str(date_start)+"') and (DATE(date_start) <= '"+str(date_end)+"') \
                     and web_offering.center_id in ("+str(center.id)+") and (teacher_id is not null or teacher_id !='') "
            
            dict_cur.execute(query)
            student_details = dict_cur.fetchall()
            offering_id = Offering.objects.values_list("id",flat=True).filter(center_id = center.id)
            session_data = Session.objects.values_list("id",flat=True).filter(offering_id__in = offering_id,date_start__gte = date_start,date_end__lte = date_end)
            student_id_count = SessionAttendance.objects.values_list("student_id",flat=True).filter(session_id__in = session_data,is_present = "yes").distinct().count()
            attendance_perc = 0
            if student_details[0]['student_count']>0:
                # attendance_perc = int(round(((float( student_details[0]['Present'])/ student_details[0]['student_count'])*100 ),2))
                attendance_perc = (100 * student_id_count)/student_details[0]['unique_student_count']

            details = {'center_name':center.name,
                       'offering_count':session_details[0]['offering_count'],
                       'planned_session':session_details[0]['planned_session'],
                       'actual_session':session_details[0]['actual_session'], 
                       'cancelled_session':session_details[0]['cancelled_session'],
                        'offline_session':session_details[0]['offline_session'],
                       'total_children':student_details[0]['unique_student_count'],
                       'attendance_perc':attendance_perc,
                       'students_present': student_id_count}
            data.append(details)
    else:
        identified_centers = [str(center.id) for center in all_centers]
        centers = ",".join(identified_centers)
        query = "select distinct(id) from web_offering where center_id in (" + centers + ") and ((DATE(start_date)<='"+str(date_start)+"' and DATE(end_date) >= '"+str(date_start)+"') OR (DATE(start_date)<='"+str(date_end)+"' and DATE(end_date) >= '"+str(date_end)+"'))"
        dict_cur.execute(query)
        offering_ids = dict_cur.fetchall()
        for id in offering_ids:
            offering = Offering.objects.get(id=id['id'])
            query = "select count(distinct(web_session.id)) as planned_sessions, count(case when web_session.status in ( 'completed') then 1 end) as actual_sessions, count(case when web_session.status = 'offline' then 1 end) offline_session, count(case when web_session.status = 'cancelled' then 1 end) cancelled_sessions from web_session join web_offering on web_offering.id=web_session.offering_id where web_session.offering_id='"+str(offering.id)+"' and DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' and (teacher_id is not null or teacher_id !='')"
            dict_cur.execute(query)
            session_details = dict_cur.fetchall()
            query = "select auth_user.first_name, auth_user.last_name from web_session join web_offering on web_offering.id=web_session.offering_id join auth_user on auth_user.id=web_session.teacher_id where web_session.offering_id='"+str(offering.id)+"' and DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' and (teacher_id is not null or teacher_id !='') limit 1"
            dict_cur.execute(query)
            session_teacher = dict_cur.fetchall()
            if session_details:
                session_data = Session.objects.values_list("id",flat=True).filter(offering_id = offering.id,date_start__gte = date_start,date_end__lte = date_end)
                student_id_count = SessionAttendance.objects.values_list("student_id",flat=True).filter(session_id__in = session_data,is_present = "yes").distinct().count()
                query = "select count(distinct(student_id)) as unique_student_count, \
                        count(web_sessionattendance.is_present) as student_count, \
                        count(case when web_sessionattendance.is_present = 'yes' then 1 end) Present  \
                        from web_sessionattendance join web_session on web_session.id=web_sessionattendance.session_id \
                        join web_offering on web_offering.id=web_session.offering_id \
                        where DATE(date_start)>='"+str(date_start)+"' \
                        and DATE(date_start)<='"+str(date_end)+"' \
                        and web_session.offering_id='"+str(offering.id)+"' \
                        and (teacher_id is not null or teacher_id !='') "
                dict_cur.execute(query)
                student_data = dict_cur.fetchall()
                attendance_perc = 0
                if student_data and student_data[0]['student_count']>0:
                    # attendance_perc = int(round(((float(student_data[0]['Present'])/student_data[0]['student_count'])*100 ),2))
                    attendance_perc = (100 * student_id_count)/student_data[0]['unique_student_count']
                teacher_name = ''
                if session_teacher:
                    teacher_name = session_teacher[0]['last_name']
                    if session_teacher[0]['first_name']:
                        teacher_name = session_teacher[0]['first_name'] + ' ' + session_teacher[0]['last_name']
                    details = {'subject':offering.course.subject,
                               'grade':offering.course.grade,
                               'planned_sessions':session_details[0]['planned_sessions'],
                               'actual_sessions':session_details[0]['actual_sessions'],
                               'cancelled_sessions':session_details[0]['cancelled_sessions'],
                               'offline_sessions': session_details[0]['offline_sessions'] if 'offline_sessions' in session_details[0]  else session_details[0]['offline_session'],
                               'teacher':teacher_name,
                               'total_children':student_data[0]['unique_student_count'],
                               'attendance_perc':attendance_perc,
                                'students_present': student_id_count,
                               'total_attendance':student_data[0]['student_count']}
                    data.append(details)
    db.close()
    dict_cur.close()
    return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')

@csrf_exempt
def getCourseCoverage(request):
    
    [center_id] = request.GET.getlist('center_id', -1)
    center_id = center_id.strip('][').split(', ')
    if int(center_id[0]) == -1:
        center_id = -1
    course_table = []
    data = []
    if (center_id) != -1:
        date_start = datetime.datetime.strptime(request.GET.get("date_start") ,"%d-%m-%Y")
        date_end = datetime.datetime.strptime(request.GET.get("date_end") ,"%d-%m-%Y")
        all_centers = getAllCenters(request)
        all_centers = all_centers.filter(id__in=center_id) 
        ay_id = request.GET.get("ay_id","")
        if ay_id:
            for center in all_centers:
                if center.offering_set.filter(academic_year__title=ay_id):
                    pass
                else:
                    all_centers.exclude(id=center.id)
        db = evd_getDB()
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query = "select distinct(id) from web_offering where center_id='"+str(all_centers[0].id)+"' and ((DATE(start_date)<='"+str(date_start)+"' and DATE(end_date) >= '"+str(date_start)+"') OR (DATE(start_date)<='"+str(date_end)+"' and DATE(end_date) >= '"+str(date_end)+"' and academic_year_id in (select id from web_ayfy where title='"+str(ay_id)+"')))"
        dict_cur.execute(query)
        offering_ids = dict_cur.fetchall()
        if offering_ids:
            today = datetime.datetime.now()
            for id in offering_ids:
                offering = Offering.objects.get(id=id['id'])
                grade_subject = str(offering.course.grade) + ' ' + str(offering.course.subject)
                plot = []
                for month in [6,7,8,9,10,11,12]:
                    yearinc = (today.year)-1
                    query = "select count(distinct(id)) as session_count from web_session where (status='completed' or status='Completed') and MONTH(date_start)='"+str(month)+"' and YEAR(date_start)='"+str(yearinc)+"' and (teacher_id is not null or teacher_id!='') and offering_id='"+str(id['id'])+"'" 
                    dict_cur.execute(query)
                    session_count = dict_cur.fetchall()
                    plot.append(session_count[0]['session_count'])
                    for mont in [1,2,3,4]:
                        query = "select count(distinct(id)) as session_count_e from web_session where (status='completed' or status='Completed') and MONTH(date_start)='"+str(mont)+"' and YEAR(date_start)='"+str(today.year)+"' and (teacher_id is not null or teacher_id!='') and offering_id='"+str(id['id'])+"'" 
                        dict_cur.execute(query)
                        session_count_e = dict_cur.fetchall()
                        plot.append(session_count_e[0]['session_count_e'])
                course_table.append({'course':grade_subject,'plot':plot})
            cummulative(course_table)
        data.append({'course_table':course_table,'course_table_tr':simplejson.dumps(transpose(course_table))})
        db.close()
        dict_cur.close()
    return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')

@csrf_exempt   
def getAttndClassesData(request):
    
    [center_id] = request.GET.getlist('center_id', -1)
    center_id = center_id.strip('][').split(', ')
    center_id = [str(id) for id in center_id]

    if int(center_id[0]) == -1:
        center_id = -1
    partner_id = int(request.GET.get("partner_id","-1"))
    funding_partner_id=int(request.GET.get("funding_partner_id","-1"))
    ay_id = request.GET.get("ay_id","")
    state = request.GET.get("state","-1")
    start_date = datetime.datetime.strptime(request.GET.get("date_start") ,"%d-%m-%Y")
    end_date = datetime.datetime.strptime(request.GET.get("date_end") ,"%d-%m-%Y")
    time_start = request.GET.get("time_start"," ")
    time_end = request.GET.get("time_end"," ")
    type = request.GET.get("type")
    all_centers = getAllCenters(request)
    if center_id != -1:
        all_centers = all_centers.filter(id__in=center_id) 
    elif state != str('-1'):
        all_centers = all_centers.filter(state=state)
    if partner_id != -1:
        all_centers = all_centers.filter(delivery_partner_id=partner_id).distinct().order_by('name')
    if funding_partner_id != -1:
        all_centers = all_centers.filter(funding_partner_id=funding_partner_id).distinct().order_by('name')
    if ay_id:
        for center in all_centers:
            if center.offering_set.filter(academic_year__title=ay_id):
                pass
            else:
                all_centers.exclude(id=center.id)
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    session_table = []
    attnd_table = []
    if all_centers:
        center_ids = [str(centerid) for centerid in all_centers.values_list('id',flat=True)]
        center_ids = ",".join(center_ids)
        query = "select ws.id, wco.subject, wco.board_name, wco.grade, ws.date_start, ws.date_end, au.first_name, au.last_name, wc.name, ws.status, ws.cancel_reason from web_session ws join web_offering wo on wo.id=ws.offering_id join web_course wco on wco.id=wo.course_id join web_center wc on wc.id=wo.center_id join auth_user au on au.id=ws.teacher_id join web_ayfy ay on ay.id = wo.academic_year_id where wo.center_id in ("+center_ids+") and ay.title = '"+str(ay_id) +"' and DATE(ws.date_start)>='"+str(start_date)+"' and TIME(ws.date_start)>='"+str(time_start)+"' and DATE(ws.date_end)<='"+str(end_date)+"' and TIME(ws.date_end)<='"+str(time_end)+"' and (ws.teacher_id is not null or ws.teacher_id !='') order by ws.date_start asc"
        #and ((DATE(start_date)<='"+str(start_date)+"' and DATE(end_date) >= '"+str(start_date)+"') OR (DATE(start_date)<='"+str(end_date)+"' and DATE(end_date) >= '"+str(end_date)+"'))"

        dict_cur.execute(query)
        sessions = dict_cur.fetchall()
        if sessions and len(sessions)>0:
            for session in sessions:
                cancel_reason = session['cancel_reason']
                subject = str(session['board_name']) + ' ' + str(session['subject']) + ' ' + str(session['grade'])
                if session['first_name'] or session['last_name']:
                    teacher = session['last_name']
                    if session['first_name']:
                        teacher = session['first_name'] + '' + session['last_name']
                        query = "select count(is_present) as student_count,count(case when is_present = 'yes' then 1 end) Present from web_sessionattendance where session_id='"+str(session['id'])+"' "
                        dict_cur.execute(query)
                        attendance_count = dict_cur.fetchall()
                        attendance = 0
                        if attendance_count and len(attendance_count)>0:
                            if attendance_count[0]['student_count']>0:
                                attendance = (float(attendance_count[0]['Present'])/attendance_count[0]['student_count'])*100
                        details = {'course':subject,'starttime':str(session['date_start'].strftime("%b. %d, %Y, %I:%M %p")),'endtime':str(session['date_end'].strftime("%b. %d, %Y, %I:%M %p")),
                                'session_attendance':str(round(attendance,0)),'Teacher':teacher,'center':str(session['name']),'status':session['status'], 'cancel_reason': session['cancel_reason'],'total_student':str(attendance_count[0]['Present'])}       

                        session_table.append(details)
        if center_id!=-1:
            query = "select id, name from web_student where center_id in ("+center_ids+")"
            dict_cur.execute(query)
            students = dict_cur.fetchall() 
            if students:
                for student in students:
                    query = "select distinct(wof.id) from web_offering wof join web_session ws on wof.id=ws.offering_id join web_sessionattendance wsa on ws.id=wsa.session_id where wsa.student_id='"+str(student['id'])+"' and DATE(ws.date_start)>='"+str(start_date)+"' and DATE(ws.date_start)<='"+str(end_date)+"' and ((DATE(start_date)<='"+str(start_date)+"' and DATE(end_date) >= '"+str(start_date)+"') OR (DATE(start_date)<='"+str(end_date)+"' and DATE(end_date) >= '"+str(end_date)+"'))"
                    dict_cur.execute(query)
                    offering_ids = dict_cur.fetchall()
                    student_name = X(student['name'])
                    if offering_ids:
                        for offering_id in offering_ids:
                            offering = Offering.objects.get(id=offering_id['id'])
                            offering_name = str(offering.course.board_name) + ' ' + str(offering.course.subject) + ' ' + str(offering.course.grade)
                            query = "select count(distinct(ws.id)) as total_session from web_session ws where ws.offering_id='"+str(offering.id)+"' and DATE(date_start)>='"+str(start_date)+"' and DATE(date_start)<='"+str(end_date)+"' and (teacher_id is not null or teacher_id!='') "
                            dict_cur.execute(query)
                            total_session = dict_cur.fetchall()
                            query = "select count(case when is_present = 'yes' then 1 end) as present_count, count(case when is_present = 'no' then 1 end) as absent_count from web_sessionattendance wsa join web_session ws on ws.id=wsa.session_id where wsa.student_id='"+str(student['id'])+"' and DATE(ws.date_start)>='"+str(start_date)+"' and DATE(ws.date_start)<='"+str(end_date)+"' and ws.offering_id='"+str(offering.id)+"'"
                            dict_cur.execute(query)
                            attendance_count = dict_cur.fetchall()
                            today = datetime.datetime.now()
                            change_date = end_date
                            if end_date>=today:
                                change_date = today
                            query = "select count(distinct(ws.id)) as asoftoday from web_session ws where ws.offering_id='"+str(offering.id)+"' and DATE(date_start)>='"+str(start_date)+"' and DATE(date_start)<='"+str(change_date)+"' and (teacher_id is not null or teacher_id!='') "
                            dict_cur.execute(query)
                            asoftoday = dict_cur.fetchall()
                            if asoftoday and attendance_count:
                                
                                uncap = asoftoday[0]['asoftoday'] - (attendance_count[0]['present_count'] + attendance_count[0]['absent_count'])
                                details = {'student':student_name,'course':offering_name,'present':attendance_count[0]['present_count'],
                                           'absent':attendance_count[0]['absent_count'],"asoftoday": asoftoday[0]['asoftoday'],'totalsess':total_session[0]['total_session'],'uncap':uncap,'total_student':attendance_count[0]['present_count']}
                                attnd_table.append(details)    
    db.close()
    dict_cur.close()       
    return HttpResponse(simplejson.dumps({'session_table':session_table,'attnd_table':attnd_table}), mimetype = 'application/json')

   
@csrf_exempt
def getSelCenters(request):
    search_term = request.GET.get('term', '')
    ay_id = request.GET.get('ay_id')
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    # query = "select id, name as label, name as value, language from web_center where status = 'Active' "
    query = "select id , name as label, name as value, language,board from web_center  where status = 'Active' "
    if search_term is not None and search_term != '':
        query += " and name like '%" + search_term + "%' group by id"       
    dict_cur.execute(query)
    center_data = dict_cur.fetchall()
    for center in center_data:
        center_board = center['board']
        try:
            current_ay = Ayfy.objects.get(start_date__year=datetime.datetime.now().year, board=center_board)
        except:
            last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
            current_ay = Ayfy.objects.get(start_date__year=last_year, board=center_board)
        center['ay'] = current_ay.id     
    db.close()
    dict_cur.close()
    return HttpResponse(simplejson.dumps(center_data))

def getCentersForPartner(request):
    search_term = request.GET.get('term', '')
    ay_id = request.GET.get('ay_id')
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
#     funding_partnerId = request.user.partner_set.all()[0].id
    
    user=request.user
    user_id=str(user.id)
    user_profile = UserProfile.objects.filter(user = request.user)[0]
    roles = user_profile.role.values_list('name',flat=True)
    
    query = "select id , funding_partner_id,name as label, name as value,\
     language,board from web_center where status = 'Active' "
    if request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 2: 
        query += " and  delivery_partner_id = '"+str(request.user.partner_set.all()[0].id)+"'"
    if request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 3: 
        query += " or funding_partner_id = '"+str(request.user.partner_set.all()[0].id)+"'"
    if 'Delivery co-ordinator' in roles:
        query += " or delivery_coordinator_id='"+user_id+"'"
    if search_term is not None and search_term != '':
        query += " and name like '%" + search_term + "%' group by id" 
         
    dict_cur.execute(query)
    center_data = dict_cur.fetchall()
    for center in center_data:
        center_board = center['board']
        try:
            current_ay = Ayfy.objects.get(start_date__year=datetime.datetime.now().year, board=center_board)
        except:
            last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
            current_ay = Ayfy.objects.get(start_date__year=last_year, board=center_board)
        center['ay'] = current_ay.id 
    db.close()
    dict_cur.close()
    return HttpResponse(simplejson.dumps(center_data))

def get_student_db(request):
    grade=request.GET.get("grade",'')
    status=request.GET.get("status",'')
    center_id=request.GET.get("centerId",'')
    gender =request.GET.get("gender",'')
    sheet_name = 'get_student_db'
    wb = Workbook()
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select id,name,school_rollno,grade,gender,father_occupation,mother_occupation,strengths,weakness,observation,status from web_student where web_student.center_id ="+str(center_id)+""
        
    # if len(grade)== 0 and len(status)== 0 and len(gender) == 0 :
    #     query = "select id,name,dob,school_rollno,grade,gender,father_occupation,mother_occupation,strengths,weakness,observation,status from web_student where web_student.center_id ="+str(center_id)+""
    if len(grade) !=0:
        query+= " and (grade='"+grade+"')"
    if len(gender)> 0:
        if gender == 'Female':
           query+=  " and gender in ('Female','girl')"
        else:
            query+=  " and gender in ('Male','boy')"
    if len(status)> 0:
        query+=  " and (status='"+status+"')" 
    dict_cur.execute(query)
    student_data = dict_cur.fetchall()
    db.close()
    dict_cur.close()
    return HttpResponse(simplejson.dumps(student_data))



def getSelUsers(request):
    try:
        search_term =  request.GET.get('term', '')
        role_id = request.GET.get('role_id','')
        type = request.GET.get('type', '')
        center_id = request.GET.get('center_id','')
        db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        center_language = ''
        #center_name = ''
        center_state=''
        
        try : 
            center = Center.objects.get(id=center_id)
            center_language = center.language
            #center_name=center.name
            center_state=center.state;
        except: center = None
        if type == 'partner':
            query = "select pp.id, pp.name, concat(pp.id,' :: ',pp.name) as label, concat(pp.id,' :: ',pp.name) as value, GROUP_CONCAT(wc.id) as center_id from partner_partner pp join partner_partner_partnertype pppt on pp.id=pppt.partner_id join web_center wc on wc.delivery_partner_id=pp.id where pppt.partnertype_id='"+role_id+"'"
            if search_term is not None and search_term!='':
                query += " and (pp.name like '%"+search_term+"%' or pp.id like '%"+search_term+"%') "
            query += " group by pp.id "
        elif type == 'orgpartner':
            # query = "select pp.id, pp.name, concat(pp.id,' :: ',pp.name) as label, concat(pp.id,' :: ',pp.name) as value, GROUP_CONCAT(wc.id) as center_id from partner_partner pp join partner_partner_partnertype pppt on pp.id=pppt.partner_id join web_center wc on wc.orgunit_partner_id=pp.id where pppt.partnertype_id='"+role_id+"'"
            query = "select pp.id, pp.name, concat(pp.id,' :: ',pp.name) as label, concat(pp.id,' :: ',pp.name) as value from partner_partner pp , partner_partnertype pt ,auth_user au , partner_partner_partnertype ppt where ppt.partner_id = pp.id and ppt.partnertype_id = pt.id and pp.contactperson_id = au.id and pt.id='"+role_id+"'"
            if search_term is not None and search_term!='':
                query += " and (pp.name like '%"+search_term+"%' or pp.id like '%"+search_term+"%') "
            query += " group by pp.id "
            dict_cur.execute(query)
            user_data = dict_cur.fetchall()
            for ud in user_data:ud['center_id']=''
            db.close()
            dict_cur.close()
            return HttpResponse(simplejson.dumps(user_data), mimetype='application/json')
        else:
            query = "select u.id, u.username, concat(u.id,' :: ',u.first_name, ' ' ,u.last_name) as label, concat(u.id,' :: ',u.first_name, ' ' ,u.last_name) as value "
            if role_id and center_id and center_id != '' and (role_id=='2' or role_id=='6' or role_id=='11' or role_id=='12'):
                query += ", GROUP_CONCAT(wc.id) as center_id "
            query += " from auth_user u join  web_userprofile wup on u.id=wup.user_id join web_rolepreference wrp on wup.id=wrp.userprofile_id join  web_userprofile_pref_roles wupr on wup.id=wupr.userprofile_id "
            if role_id and center_id and center_id != '' and role_id != '':
                if role_id == '2': query += "  join web_center wc "
                elif role_id == '6': query += " join web_center wc  "
                elif role_id == '11': query += " join web_center wc "
                elif role_id == '12': query += " join web_center wc "
            query += " where "
            if role_id and role_id != '':
                query += " wupr.role_id='"+role_id+"' and u.is_active is true  and wrp.role_outcome='recommended'"
            if search_term is not None and search_term!='':
                query += " and (u.username like '%"+search_term+"%' or u.first_name like '%"+search_term+"%' or u.last_name like '%"+search_term+"%' or u.id like '%"+search_term+"%') "
            if center_state:
                query += " and wc.state='"+center_state+"' and wc.language= '"+ center_language+"'"
            query += " group by u.id "
        dict_cur.execute('SET SESSION group_concat_max_len = 999999')
        dict_cur.execute(query)
        user_data = dict_cur.fetchall()
        db.close()
        dict_cur.close()
        return HttpResponse(simplejson.dumps(user_data), mimetype = 'application/json')
    except Exception as e:
        print("Error reason =", e); print("Error at line no = ", traceback.format_exc())
        return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')


def getCenterUsers(request):
    center_id = request.GET.get('center_id','')
    data = []
    if center_id is not None and center_id != '':
        center = Center.objects.get(id=center_id)
        if center:
            if center.admin:
                label = str(center.admin.id) + ' :: ' + center.admin.first_name + ' ' + center.admin.last_name
                data.append({'role':'admin','value':center.admin.id,'label':label})
            if center.assistant:
                label = str(center.assistant.id) + ' :: ' + center.assistant.first_name + ' ' + center.assistant.last_name
                data.append({'role':'assistant','value':center.assistant.id,'label':label})
            if center.delivery_partner:
                label = str(center.delivery_partner.id) + ' :: ' + center.delivery_partner.name
                data.append({'role':'delivery_partner','value':center.delivery_partner.id,'label':label})
            if center.field_coordinator:
                label = str(center.field_coordinator.id) + ' :: ' + center.field_coordinator.first_name + ' ' + center.field_coordinator.last_name
                data.append({'role':'field_coordinator','value':center.field_coordinator.id,'label':label})
            if center.delivery_coordinator:
                label = str(center.delivery_coordinator.id) + ' :: ' + center.delivery_coordinator.first_name + ' ' + center.delivery_coordinator.last_name
                data.append({'role':'delivery_coordinator','value':center.delivery_coordinator.id,'label':label})
            if center.orgunit_partner:
                label = str(center.orgunit_partner.id) + ' :: ' + center.orgunit_partner.name
                data.append({'role':'organization_unit','value':center.orgunit_partner.id,'label':label})
    return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')





def getPartnerUsers(request):
    partner_id = request.GET.get('partner_id','')
    data = []
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    if partner_id is not None and partner_id != '':
        partner=Partner.objects.get(contactperson_id=partner_id)
        pam_name=''
        if partner:
            query=" select partner_partnertype.name as value from partner_partner inner join partner_partner_partnertype on partner_partner.id=partner_partner_partnertype.partner_id inner join partner_partnertype on partner_partner_partnertype.partnertype_id =partner_partnertype.id where partner_partner.contactperson_id="+str(partner_id)+" "
            dict_cur.execute(query)
            # partner_name = dict_cur.fetchall() 
            partner_name = [str(each['value']) for each in dict_cur.fetchall()]
            partner_name.sort()
            # partner_name = partner_name["value"]
           
            partnr_name= tuple(partner_name)
            partnr_name= partner_name[0]
            query="SELECT CONCAT(auth_user.first_name,' ',auth_user.last_name) as pam from partner_partner_partnertype inner join partner_partner on partner_partner.id=partner_partner_partnertype.partner_id inner join partner_partnertype on partner_partner_partnertype.partnertype_id= partner_partnertype.id inner join auth_user  on partner_partner_partnertype.pam=auth_user.id where partner_partnertype.name='"+str(partnr_name)+"'  and partner_partner_partnertype.partner_id='"+str(partner.id)+"'"
            dict_cur.execute(query)
            pam_name = [str(each['pam']) for each in dict_cur.fetchall()]
            pam_name.sort()
            
            data.append({'name':partner.name,'organistaion_name':partner.name_of_organization,'type':partner_name,'pam_name':pam_name})
	
    db.close()
    dict_cur.close()
    return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')



def stub(request):
    message = request.GET.get('message', '')
    return render(request, "evd_stub.html", {'message':message})
    
def saveStub(request):
    school_code = request.GET.get('schoolCode', '')
    school_name = request.GET.get('schoolName', '')
    village_name = request.GET.get('villageName', '')
    distirict_name = request.GET.get('distirictName', '')
    state = request.GET.get('state', '')
    headMaster_name = request.GET.get('headMasterName', '')
    no_of_teachers = request.GET.get('noOfTeacher', '')
    no_of_students = request.GET.get('noOfStudents', '')
    service_provider = request.GET.get('serviceProvider', '')
    connection_type = request.GET.get('connectionType', '')
    download_speed = request.GET.get('downloadSpeed', '')
    upload_speed = request.GET.get('uploadSpeed', '')
    date_of_entry = request.GET.get('dateOfEntry', '')
    system_availability = request.GET.get('systemAvailability', '')
    latitude = request.GET.get('latitude', '')
    longitude = request.GET.get('longitude', '')
    created_date = datetime.datetime.now()
    updated_date = datetime.datetime.now()
    school_viability=SchoolViability(school_code=school_code, school_name=school_name,
        village_name=village_name, distirict_name=distirict_name, state=state,
        headmaster_name=headMaster_name, no_of_teachers=no_of_teachers, 
        no_of_students=no_of_students, servive_provider=service_provider,
        connection_type=connection_type, download_speed=download_speed, 
        upload_speed=upload_speed, date_of_entry=date_of_entry,
        system_availability=system_availability, latitude=latitude,
        longitude=longitude, created_date=created_date, updated_date=updated_date)
    try:
        school_viability.save()
        message = "Details have been saved successfully"
    except:
        message = "Error in saving Details"
    return redirect('/v2/stub/?message='+message)

@csrf_exempt
def get_allteachers(request):
    search_term = request.GET.get('term', '')
    center_id=request.GET.get('center_id','-1')

    is_search_type_int = search_term.isdigit()
    center = Center.objects.get(id=center_id)
    center_language = center.language

    center_deliverypartner = None
    center_dp = Center.objects.filter(id=center_id).values_list('delivery_partner_id',flat=True)
    if len(center_dp) > 0:
        center_deliverypartner = center_dp[0]

    logged_in_user = request.user

    user_ref_channel = None
    ref_channel_partner = None
    center_dc_id = None
    center_fc_id = None

    # Get Delivery coordinator of the center
    temp = Center.objects.filter(id=center_id).values_list('delivery_coordinator_id',flat=True)
    if len(temp) > 0:
        center_dc_id = temp[0]

    # Get Field coordinator of the center
    temp = Center.objects.filter(id=center_id).values_list('field_coordinator_id', flat=True)
    if len(temp) > 0:
        center_fc_id = temp[0]

    # Check if logged in user in DC or FC and get reference channel so
    if center_dc_id is not None and logged_in_user.id == center_dc_id:
        temp_ref_channel = UserProfile.objects.filter(user_id=center_dc_id).values_list('referencechannel_id', flat=True)
        if len(temp_ref_channel) > 0:
            user_ref_channel = temp_ref_channel[0]
    elif center_fc_id is not None and logged_in_user.id == center_fc_id:
        temp_ref_channel = UserProfile.objects.filter(user_id=center_fc_id).values_list('referencechannel_id', flat=True)
        if len(temp_ref_channel) > 0:
            user_ref_channel = temp_ref_channel[0]

    if user_ref_channel is not None:
        refchannel_partner = ReferenceChannel.objects.filter(id=user_ref_channel).values_list('partner_id',flat=True)
        if len(refchannel_partner) > 0:
            ref_channel_partner = refchannel_partner[0]

    teachers_count= Teachers.objects.filter(user=request.user).count()
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)

    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)

    query = "SELECT au.id, concat(au.id,'::',au.first_name,' ',au.last_name) as value FROM auth_user au join web_userprofile wup on wup.user_id = au.id join web_userprofile_role wur on wur.userprofile_id = wup.id left join web_rolepreference wrp on wrp.userprofile_id=wup.id where ((wrp.role_id in (1, 3, 6, 18, 20) and wrp.role_outcome in ('Recommended','Inprocess') and SUBSTRING_INDEX(wup.pref_medium, ',', 1)='" + center_language + "') or wur.role_id in (6, 18)) "
    if teachers_count:
        query = "SELECT au.id, concat(au.id,'::',au.first_name,' ',au.last_name) as value FROM auth_user au join web_userprofile wup on wup.user_id = au.id join web_userprofile_role wur on wur.userprofile_id = wup.id left join web_rolepreference wrp on wrp.userprofile_id=wup.id join web_teachers wt on au.id = wt.user_id where ((wrp.role_id in (1, 3, 6, 18, 20) and wrp.role_outcome in ('Recommended','Inprocess') and SUBSTRING_INDEX(wup.pref_medium, ',', 1)='" + center_language + "') or wur.role_id in (6, 18)) "

    if ref_channel_partner is not None and ref_channel_partner == center_deliverypartner:
        query = "SELECT au.id, concat(au.id,'::',au.first_name,' ',au.last_name) as value FROM auth_user au join web_userprofile wup on wup.user_id = au.id join web_userprofile_role wur on wur.userprofile_id = wup.id left join web_rolepreference wrp on wrp.userprofile_id=wup.id where ((wrp.role_id in (1, 3, 6, 18, 20) and wrp.role_outcome in ('Recommended','Inprocess') and SUBSTRING_INDEX(wup.pref_medium, ',', 1)='"+center_language+"') or wur.role_id in (6, 18)) and wup.referencechannel_id='"+str(user_ref_channel)+"'"

    if is_search_type_int:
        query += " and (au.id like '%" + search_term + "%') group by au.id"
    else:
        query += " and (au.first_name like '%" + search_term + "%' or au.last_name like '%" + search_term + "%') group by au.id"

    dict_cur.execute(query)
    teachers_data = dict_cur.fetchall()
    dict_cur.close()
    db.close()
    print(teachers_data)

    return HttpResponse(simplejson.dumps(teachers_data))



def getSelCentersBaseOnUser(request):
    search_term = request.GET.get('term', '')
    user=request.user
    superUser=request.user.is_superuser
    user_id=str(user.id)
    user_profile = UserProfile.objects.filter(user = request.user)[0]
    roleNames = user_profile.role.values_list('name',flat=True)
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query=""
    partner = Partner.objects.filter(contactperson_id=request.user.id)
    is_true = False
    if partner:
        partner_id = partner[0].id
        partner_id=str(partner_id)
    try:     
        
        if superUser:
            query = "select id , name as label, name as value, language,board \
            from web_center  where status = 'Active' "
            
        else:
            query="select id , name as label, name as value, language,board \
                    from web_center  where status = 'Active'"
            if 'Partner Admin' in roleNames and partner:
                is_true = True
                query+= " and (delivery_partner_id='"+partner_id+"' \
                        or funding_partner_id= '"+partner_id+"')" 

            if 'School Admin' in roleNames:
                query += " and (delivery_partner_id='"+partner_id+"')"

            if 'OUAdmin' in roleNames:
                query+= " and orgunit_partner_id='"+partner_id+"'"
                      
            if 'Class Assistant' in roleNames:
                if is_true:
                    query+= " or "
                else:
                    query+= " and "
                is_true = True
                query+= "  assistant_id='"+user_id +"'"
                
            if 'Field co-ordinator' in roleNames:
                if is_true:
                    query+= " or "
                else:
                    query+= " and "
                is_true = True
                query+= "  field_coordinator_id='"+user_id+"'"

            if 'Delivery co-ordinator' in roleNames and 'Center Admin' in roleNames:
                if 'Center Admin' in roleNames:
                    if is_true:
                        query+= " or ("
                    else:
                        query+= " and ("
                    query+= " admin_id='"+user_id+"' "
                    is_true = True

                if 'Delivery co-ordinator' in roleNames:
                    if is_true:
                        query+= " or "
                    else:
                        query+= " and "
                    query+= " delivery_coordinator_id='"+user_id +"' )"           
            else:        
                if 'Delivery co-ordinator' in roleNames:
                    if is_true:
                        query+= " or "
                    else:
                        query+= " and "
                    query+= " delivery_coordinator_id='"+user_id +"'"  

                if  'Center Admin' in roleNames:
                    if is_true:
                        query+= " or "
                    else:
                        query+= " and "
                    query+= " admin_id='"+user_id+"'"
                    is_true = True                         
    
        # query = "select id, name as label, name as value, language from web_center where status = 'Active' "
        if search_term is not None and search_term != '':
            query += " and name like '%" + search_term + "%'and status='active'  group by id"             
        dict_cur.execute(query)
        center_data = dict_cur.fetchall()
        
    except:
        pass
     
    for center in center_data:
        center_board = center['board']
        try:
            current_ay = Ayfy.objects.get(start_date__year=datetime.datetime.now().year, board=center_board)
        except  Exception as e:

            last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
            current_ay = Ayfy.objects.get(start_date__year=last_year, board=center_board)
        center['ay'] = current_ay.id

    dict_cur.close()
    db.close()
    return HttpResponse(simplejson.dumps(center_data))



def getSchools(request):
    search_term = request.GET.get('term', '')

    #user=request.user
    #superUser=request.user.is_superuser
    #user_id=str(user.id)
    #user_profile = UserProfile.objects.filter(user = request.user)[0]
    #roleNames = user_profile.role.values_list('name',flat=True)
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    #partner = Partner.objects.filter(contactperson_id=request.user.id)
    query=""
    try:
        query = " select id as value, concat(IFNULL(concat('(',school_code,') - '),''), concat(IFNULL(name,''),concat(', ',concat(block ,concat(' - ',village))))) as label from web_school where 1=1 "
        if search_term :
            query+= " and "
            query+= " ( school_code like '"+search_term+"%' "
            query+= "  or  village like '"+search_term+"%' "
            query+= "  or  name like '"+search_term+"%' "
            query+= "  or  block like '"+search_term+"%' )"
        query+= " order by name "
        # query+= " limit 300 "
        # import datetime
        dict_cur.execute(query)
        schools = dict_cur.fetchall()
    except:
        pass

    db.close()
    dict_cur.close()
    # schools = list(School.objects.filter(Q(name__icontains=search_term) | Q(village__icontains=search_term) | Q(school_code__contains=search_term) | Q(block__icontains=search_term)).values_list("id", "name", "village", "school_code", "block").order_by("name"))
    return HttpResponse(simplejson.dumps(schools))

def reset_password(request):
    if request.method=="GET":
        uid=request.GET.get('uid','')
        uidOrg=int(uid,36)
        try:
            alertObj = Alerts.objects.filter(user=uidOrg).order_by('-dt_updated')[0] 
            if alertObj.status_message == "completed":
                return HttpResponse('<h4>Sorry to say that link is already expired</h4>')
        except:
            pass    
        dictID={"uid":uid}
    return render(request,'registration/resetpasswordpage.html',{"dictID":dictID})


def resetpassword_done(request):
    if request.method =="POST":
        pass1=request.POST.get('new_password1','')
        pass2=request.POST.get('new_password2','')
        uid=request.POST.get('idValue','')
        uid=int(uid,36)
        try:
            alertObj = Alerts.objects.filter(user=uid).order_by('-dt_updated')[0] 
            alertObj.status_message = "completed"
            alertObj.save()
        except:
            pass    
        if(pass1==pass2):
            u = User.objects.get(id=uid)
            u.set_password(pass2)
            u.save()
    return render_response(request,'registration/_password_reset_complete.html',{})
   
def newevdpage(request):
    return render_response(request,'runforevidyaloka_homepage.html')

def my_referrals(request):
    return render_response(request,'referrals.html',{})

def my_referrals_details(request):
    page = request.GET.get('page')
    userp = UserProfile.objects.filter(referred_user = request.user)
    user_list_without_pagination = len(userp)
    paginator = Paginator(userp, 20)
    try:
        userp = paginator.page(page)
    except PageNotAnInteger:
        userp = paginator.page(1)
    except EmptyPage:
        userp = paginator.page(paginator.num_pages)
    user_list = []
    if len(userp)>0:
        for u in userp:
            data = {'id':u.user_id,'user_name':str(u.user.first_name)+ ' ' +str(u.user.last_name),'email':u.user.email,'phone':u.phone}
            user_list.append(data)
        #return HttpResponse(simplejson.dumps(user_list))
        return HttpResponse(simplejson.dumps({'user_list':user_list,'prev': userp.previous_page_number(),
            'next': userp.next_page_number(),'current': userp.number,
            'total': userp.paginator.num_pages,'count':user_list_without_pagination}), mimetype = 'application/json')
    else:
        return HttpResponse(user_list)
    
@login_required
def plan_topics(request,cent_id,off_id):
    offering = Offering.objects.filter(id=int(off_id))[0]

    subject = offering.course.subject
    grade = offering.course.grade
    board = offering.academic_year.board
    courses_a = Course.objects.filter(board_name=board, subject=subject)

    revision_grades =[]
    for course in courses_a:
        if  len(course.grade)<2:
            if int(course.grade) < int(grade):
                revision_grades.append(int(course.grade))

    revision_grades=sorted(revision_grades, reverse=True)

    planned_topics = offering.planned_topics.all().order_by('priority')
    all_topics = Topic.objects.filter(course_id=offering.course_id).order_by('priority')
    course_topics =[]
    for course_topic in all_topics:
        published_topic = TopicDetails.objects.filter(topic = course_topic , status='Published',url__contains='Lesson Plan')
        published = False
        if len(published_topic)>0:
            published = True
        course_topics.append({'id':course_topic.id,'url':course_topic.url,'title':course_topic.title,'publish':published})
        
    sessions = offering.session_set.all()
    complted_topic = []
    unique_topic_id = []
    for sess in sessions:
        actual_topic = sess.actual_topics.all()
        if len(actual_topic)>0:
            unique_topic_id.append(actual_topic[0].id)
    unique_topic_id = list(set(unique_topic_id))
    for topic in Topic.objects.filter(id__in = unique_topic_id):
        data = {'id':topic.id,'title':topic.title}
        complted_topic.append(data)
        
    return  render_response(request, 'plan_topic.html',{'all_topics':course_topics,'planned_topics':planned_topics,"offering":offering,'complted_topic':complted_topic,'center':offering.center, 'revision_grades':revision_grades})

def change_grade(request):

    if request.method == 'POST':
        off_id = request.POST.get('offering_id', None)
        current_grade = request.POST.get('grade', None)
        offering = Offering.objects.filter(id=int(off_id))[0]
        subject = offering.course.subject
        board = offering.academic_year.board
        courses_a = Course.objects.filter(board_name=board, subject=subject)
        revi = []
        for course in courses_a:
            if int(course.grade) == int(current_grade):
                revi.append(int(course.id))

        revised_courses = Topic.objects.filter(course_id__in=revi)
        course_topics =[]
        for course_topic in revised_courses:
            course_topics.append({'id':course_topic.id,'url':course_topic.url,'title':course_topic.title})

        return HttpResponse(simplejson.dumps(course_topics))
    return HttpResponse('No topic', content_type='application/json')
    
    
def get_sub_topic(request):
    topic_id = request.GET.get('topic_id')
    offering_id = request.GET.get('offering_id')
    is_completed_sub_topic = request.GET.get('is_complted_sub_topic')
    if is_completed_sub_topic == 'true':
        offering = Offering.objects.get(id = offering_id)
        sub_topic_ids = Session.objects.values_list('sub_topic',flat=True).filter(offering_id = offering_id,status='Completed')
    topicList = []
    if is_completed_sub_topic == 'true':
        sub_topic = SubTopics.objects.filter(topic_id = topic_id,id__in = sub_topic_ids)
    else:
        sub_topic = SubTopics.objects.filter(topic_id = topic_id)
    for topic in sub_topic:
        data = {'id':topic.id,'name':topic.name}
        topicList.append(data)
    return HttpResponse(simplejson.dumps(topicList))

def modify_topics(request):
    today_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
    center_id = request.POST['center_id']
    center = Center.objects.get(id=center_id)
    offering = Offering.objects.get(id=request.POST['offering_id'])
    new_planned_topics = request.POST.getlist('enrolllist1[]')
    recvdellist = request.POST.getlist('derolllist1[]')
    """sessions = offering.session_set.all()
    sessions_t = sessions.values_list('id',flat=True).filter(date_start__gte = today_date).order_by('date_start')
    count = 0"""
    
    """if len(sessions_t)>0:
        for topic in new_planned_topics:
            t = Topic.objects.get(id = topic)
            topic_sessions = t.num_sessions or 1
            for topic_session in range(topic_sessions):
                try:
                    session = Session.objects.get(id = sessions_t[count])
                    if session.teacher is None:
                        continue
                    session.planned_topics.clear()
                    session.planned_topics.add(t)
                    session.save()
                    count+=1
                except IndexError:
                    break
            
        if count < len(sessions_t):
            for i in range(count, len(sessions_t)):
                try:
                    session = Session.objects.get(id = sessions_t[i])
                    if session.teacher is None:
                        continue
                    session.planned_topics.clear()
                    session.save()
                except IndexError:
                    break"""
  
    course_topic_list = []
    planned_topic_list = []
    new_topics = ''
    for ent in new_planned_topics:
        new_topics+=str(ent)+','
    new_topics = new_topics[:-1]
    if new_topics != '':
        new_topics = new_topics.split(",")
    new_topics = map(int, new_topics)
    for ent in offering.planned_topics.all():
            course_topic_list.append(int(ent.id))
            if ent.id not in new_topics:
                t = Topic.objects.get(id=ent.id)
                offering.planned_topics.remove(t)
    for i in new_planned_topics:
            if int(i) not in  course_topic_list:
                t = Topic.objects.get(id=i)
                offering.planned_topics.add(t)
    offering.save()
    message = "Topic modified "
    return render_response(request, 'success.html',{"message": message })

def delete_duplicate_data(request):

    # ay_ids = Ayfy.objects.values_list('id',flat=True).filter(title='AY-18-19',board__in = ['APSB','SCERT'])
    # total_session = 0
    # offerings = Offering.objects.filter(academic_year_id__in = ay_ids)
    # for offer in offerings:
    #     board = offer.course.board_name
    #     holiday_dates = get_holidays(board)
    #     sessions = offer.session_set.all()
    #     if sessions:
    #         for  sess in sessions:
    #             if holiday_dates:
    #                 if sess.date_start.date() in holiday_dates:
    #                     deleted_history.append(str(sess.date_start) +' '+str(offer.center.name)+' '+str(offer.course.grade)+' '+str(offer.course.subject))
    #                     total_session+=1
    #                     sess.delete()

    center_all = []
    center_all = Center.objects.values_list('id', flat="true").filter(status="Active")
    center_all = [str(i) for i in center_all]
    deleted_history = []
    unique_student_g7 = []
    unique_student_g6 = []
    unique_student_g5 = []
    total__duplicate_student = 0
    for student_g7 in Student.objects.filter(center_id__in = center_all, grade = 7 ):
        std = capitalize_words(student_g7.name)
        if std not in  unique_student_g7:
            unique_student_g7.append(std)
        else:
            deleted_history.append(str(student_g7.id) + ' ' + str(student_g7.name) + ' ' + str(student_g7.grade) + ' '+ str(student_g7.center_id))
            total__duplicate_student += 1
            student_g7.delete()
    for student_g6 in Student.objects.filter(center_id__in = center_all, grade = 6 ):
        std = capitalize_words(student_g6.name)
        if std not in unique_student_g6:
            unique_student_g6.append(std)
        else:
            deleted_history.append(str(student_g6.id) + ' ' + str(student_g6.name) + ' ' + str(student_g6.grade) + ' '+ str(student_g6.center_id))
            total__duplicate_student += 1
            student_g6.delete()
    for student_g5 in Student.objects.filter(center_id__in = center_all, grade = 5 ):
        std = capitalize_words(student_g5.name)
        if std not in unique_student_g5:
            unique_student_g5.append(std)
        else:
            deleted_history.append(str(student_g5.id) + ' ' + str(student_g5.name) + ' ' + str(student_g5.grade) + ' '+ str(student_g5.center_id))
            total__duplicate_student += 1
            student_g5.delete()
    return render_response(request, 'msg.html',{"message": deleted_history,'total':'Total duplicate records deleted : '+str(total__duplicate_student) })


def capitalize_words(string):
    words = string.split()
    return ' '.join([word.capitalize() for word in words])

@login_required
def change_password(request):
    error_msg = ''
    success_msg = ''
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            success_msg = 'Password has been changed successfully !'
        else:
            error_msg =  'Please correct the error below.'
    else:
        form = PasswordChangeForm(request.user)
    return render_response(request,'change_password.html',{"form":form,'success_msg':success_msg,'error_msg':error_msg})

@csrf_exempt
def new_signup(request):
    try:
        json_p = request.POST.get('json','')
        details_json = json.loads(json_p)
        first_name = details_json['first_name']
        last_name  = details_json['last_name']
        email    = details_json['email']
        password = details_json['password']
        phone    = details_json['phone']
        skype    = details_json['skype']
        gender   = details_json['gender']
        dob      = details_json['dob']
        no_of_hrs = details_json['no_of_hrs']
        # native_country = details_json['native_country']
        # native_state = details_json['native_state']
        # native_city = details_json['native_city']
        current_country = details_json['current_country']
        current_state = details_json['current_state']
        current_city = details_json['current_city']
        current_job = details_json['current_job']
        profession  = details_json['profession']
        work_exp    = details_json['work_exp']
        qualification = details_json['qualification']
        referal = details_json['referal']
        referal_p = details_json['referal_p']
        terms_and_conditions    = details_json['terms']

        import datetime
        #dob = 20-12-1994
        #dob = int(dob)
        #mydate = datetime.datetime(dob, 01, 01)
        #mydate = datetime.datetime.strftime(mydate ,'%d-%m-%Y')
        #mynewdatestr=str(dob)+"01-01"
        #dob = datetime.datetime.strptime(mydate ,'%d-%m-%Y').date()
        dob = datetime.datetime.strptime('01-01-'+str(dob),"%d-%m-%Y")

        languages_known = details_json['lang_array']
        pref_medium = languages_known[0]['lang']
        courses  =  details_json['course_arr']
        existing_user = User.objects.filter(email=email)
        
        response_data = {}
        if existing_user:
            response_data['status'] = 1
            response_data['message'] = 'User already exists, please login'
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        new_user = User.objects.create_user(email=email, username=email)
        new_user.set_password(password)
        new_user.save()
        user = authenticate(username=email, password=password)
        login(request, user)
        userp = user.userprofile
        user.first_name = first_name
        user.last_name = last_name
        userp.phone = phone
        userp.pref_medium = pref_medium
        userp.gender = gender
        userp.dob = dob
        userp.work_exp = work_exp
        userp.profession = profession
        # userp.qualification = qualification
        userp.country = current_country
        userp.state = current_state
        userp.city = current_city
        # userp.native_country = native_country
        # userp.native_state = native_state
        # userp.native_city = native_city

        userp.skype_id = skype
        userp.languages_known = languages_known
        userp.current_job = current_job
        userp.no_hrs_week = no_of_hrs
        userp.terms_and_conditions = terms_and_conditions
        try:
            referencechannel = ReferenceChannel.objects.get(id=1)
            userp.referencechannel = referencechannel
        except:
            pass
        
        roles = courses #request.POST.get('roles')
        reference_channel = ''
        if referal_p:
            try:
                referal_partner = ReferenceChannel.objects.filter(partner_id = int(referal_p))
                if len(referal_partner)>0:
                    reference_channel = referal_partner[0]
            except:
                pass

        referal_name = ''
        referalUser = None
        if referal:
            try:
                if '/' in referal and referal_p:
                    preferal = referal.split('/')[1]
                    refpartnerd = Partner.objects.get(id=int(preferal))
                    referal=refpartnerd.contactperson_id
                referal = int(referal)
                referalUser = User.objects.get(id = referal)
                referal_name = referalUser.get_full_name()
            except:
                pass

        if referal_name and referalUser != None:
                userp.referer = referal_name
                userp.referred_user = referalUser
        if reference_channel:
            userp.referencechannel  = reference_channel



        data = {
            'referal': referal,
            'referal_p' : referal_p,
            'referal_name': referal_name,
            'reference_channel': reference_channel
            
        }
            
        print('reference data: ', data)

        if roles:
            selected_roles = [Role.objects.get(pk=int(role)) for role in roles if role]
        else:
            selected_roles = [Role.objects.get(id=1)]

        userp.role.clear()
        for role in selected_roles:
            userp.role.add(role)

        userp.pref_roles.clear()
        for role in selected_roles:
            userp.pref_roles.add(role)

        userp.profile_completion_status = True
        userp.profile_complete_status = 'Started'
        user.save()
        userp.save()
        
        host = 'http://' + request.META['HTTP_HOST']
        try:
            UserSocialAuth.objects.get(user_id=user.id)
            fb_user = True
        except:
            fb_user = False

        args = { 'username': email, 'First_Name':first_name,'Last_Name':last_name,'host':host ,'fb_user':fb_user}
        mail = ''
        body = ''
        subject = 'Welcome to eVidyaloka - '+ first_name + " " +last_name
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email]
        body = get_template('mail/_volunteer_joined/welcome_mail_template.html').render(Context(args))
        mail = EmailMessage(subject, body, to=to, from_email=from_email)
        mail.content_subtype = 'html'
        mail.send()
        
        
        pref_roles = request.user.userprofile.pref_roles.all()
        for role in pref_roles:
            role_preference, created = RolePreference.objects.get_or_create(userprofile=userp, role=role)
            if role.name == 'Well Wisher':
                role_preference.role_outcome = 'Recommended'
                role_preference.save()
            steps = role.onboardingstep_set.all()
            for step in steps:
                step_status, creat = OnboardingStepStatus.objects.get_or_create(role_preference=role_preference,
                                                                                step=step)
        response_data['referal_name'] = referal_name
        
        if str(1).encode("utf-8").decode("utf-8")  in roles:
            onboarding = userp.rolepreference_set.filter(role=1)
            onboarding_id = onboarding[0].id
            onboard = RolePreference.objects.get(id=int(onboarding_id))

            onboard = RolePreference.objects.get(id=int(onboarding_id))
            date_submited = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
            step = onboard.onboardingstepstatus_set.all().filter(step__stepname='Self Evaluation')[0]
            step.status = True
            step.date_completed = date_submited
            try:
                step.save()
            except Exception as e:
                return 'Error'
                return 'Success'

        #### Mail Sending to Partner If User Signed up with Partner Reference
        if referal_p:
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [userp.referencechannel.partner.contactperson.email]
            subject = '%s %s registered through your reference channel' % (userp.user.first_name, userp.user.last_name)
            mail_args = {'partner_fname': userp.referencechannel.partner.contactperson.first_name, 'partner_lname': userp.referencechannel.partner.contactperson.last_name,
                        'partner_id':str(userp.referencechannel.partner_id),'username':userp.user.username,'user_email':userp.user.email}
            body = get_template('mail/_partner/Partner_ref_vol_signup_mail_notify_parnter.html').render(Context(mail_args))
            if userp.referencechannel.partner.email:
                cc = [userp.referencechannel.partner.email]
                mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
            else:
                mail = EmailMessage(subject, body, to=to, from_email=from_email)
            mail.content_subtype = 'html'
            mail.send()

        return HttpResponse(simplejson.dumps(response_data),mimetype='application/json')
    except Exception as e:
        traceback.print_exc()
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
    


def get_year_wise_teachers(year_in_num):
    import datetime
    nowdte = datetime.datetime.now()
    users = User.objects.all()
    data = []
    i=0
    if year_in_num == 6:
        end_date = nowdte.year - 6
    elif year_in_num == 5:
        end_date = nowdte.year - 5
    elif year_in_num == 4:
        end_date = nowdte.year - 4
    users = users.filter(date_joined__year=end_date)
    for u in users.iterator():
        u_sesd = []
        u_ses = Session.objects.filter(teacher=u).order_by('id')

        if u_ses.count() > 0:
            if u_ses[0].date_start.year == end_date:
                u_sesd = u_ses[0]
        if u_sesd:
            sessioninfo = {}
            sessioninfo['username'] = u.first_name + u.last_name
            sessioninfo['starting'] = u_sesd.date_start
            sessioninfo['ending'] = u_sesd.date_end
            sessioninfo['picture'] = u.userprofile.picture
            sessioninfo['city'] = u.userprofile.city
            if u.userprofile.languages_known:
                sessioninfo['languages_known'] = literal_eval(u.userprofile.languages_known)
            data.append(sessioninfo)

        i+=1
        if i ==10:
            break
    return data

def get_year_wise_teachers(year_in_num):
    import datetime
    nowdte = datetime.datetime.now()
    users = User.objects.all()
    data = []
    i=0
    if year_in_num == 6:
        end_date = nowdte.year - 6
    elif year_in_num == 5:
        end_date = nowdte.year - 5
    elif year_in_num == 4:
        end_date = nowdte.year - 4
    users = users.filter(date_joined__year=end_date)
    for u in users.iterator():
        u_sesd = []
        u_ses = Session.objects.filter(teacher=u).order_by('id')
        
        if u_ses.count() > 0:
            if u_ses[0].date_start.year == end_date:
                u_sesd = u_ses[0]
        if u_sesd:
            sessioninfo = {}
            sessioninfo['username'] = u.first_name + u.last_name
            sessioninfo['starting'] = u_sesd.date_start
            sessioninfo['ending'] = u_sesd.date_end
            sessioninfo['picture'] = u.userprofile.picture
            sessioninfo['city'] = u.userprofile.city
            if u.userprofile.languages_known:
                sessioninfo['languages_known'] = literal_eval(u.userprofile.languages_known)
            data.append(sessioninfo)
        
        i+=1
        if i ==10:
            break
    return data
def vol_of_fame(request):
    from datetime import datetime
    curr_mon = datetime.now().month
    vol_of_month = VolOfMonth.objects.filter(month = curr_mon,status='approved')

    if vol_of_month.count() < 3:
        vol_of_month = VolOfMonth.objects.filter(status='approved').order_by('-id')[:20]
    
    for vol_of_month1 in vol_of_month:
          vol_of_month1 = check_prof_pic(vol_of_month1)  
          count1 = vol_of_month1.elected_user.session_set.filter(status='Completed').count()
          vol_of_month1.sessionCount = count1
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query_L1 = "select *,count(ws.teacher_id) as teacher_count \
            from web_userprofile wup, auth_user au,web_session ws where wup.user_id = au.id \
            and au.id= ws.teacher_id and ws.status = 'completed' group by \
            ws.teacher_id having(teacher_count > 150) order by picture desc;"
    
    query_L2 = "select *,count(ws.teacher_id) as teacher_count \
            from web_userprofile wup, auth_user au,web_session ws where wup.user_id = au.id \
            and au.id= ws.teacher_id and ws.status = 'completed' group by \
            ws.teacher_id having(teacher_count > 75 and teacher_count < 150) order by picture desc;"
    
    query_L3 = "select *,count(ws.teacher_id) as teacher_count \
            from web_userprofile wup, auth_user au,web_session ws where wup.user_id = au.id \
            and au.id= ws.teacher_id and ws.status = 'completed' group by \
            ws.teacher_id having(teacher_count > 25 and teacher_count < 75) order by picture desc;"

    dict_cur.execute(query_L1)
    years_6 = dict_cur.fetchall() 
    for obj_years in years_6:
        check_prof_pic(obj_years)
    
    
    dict_cur.execute(query_L2)
    years_5 = dict_cur.fetchall() 
    for obj_years in years_5:
        check_prof_pic(obj_years)
    
    dict_cur.execute(query_L3)
    years_4 = dict_cur.fetchall() 
    for obj_years in years_4:
        check_prof_pic(obj_years)
    
    db.close()
    dict_cur.close()
    #years_6 = get_year_wise_teachers(6)
    #years_5 = get_year_wise_teachers(5)
    #years_4 = get_year_wise_teachers(4)
    
    #max_year = Expo.objects.latest('date').date.year
    
    return render_response(request, 'hall_of_fame.html',{"years_6": years_6, "years_5": years_5, "years_4": years_4, "vol_of_month": vol_of_month })

def check_prof_pic(check_image):
    if isinstance(check_image, VolOfMonth):
        path = check_image.elected_user.userprofile.picture
    else:
        path = check_image['picture']
    picture_name = path.split('/')
    if picture_name and path:
        pic_static_dir = picture_name[1] 
        if pic_static_dir == 'static':
            try:
                path = path[1:]
                present = PIL.open(path)
            except:
                if isinstance(check_image, VolOfMonth):
                    check_image.elected_user.userprofile.picture = '/static/images/defaultteacherimg_1.png'
                else:
                    check_image['picture'] = '/static/images/defaultteacherimg_1.png'
    return check_image
@login_required
@csrf_exempt
def new_landing_view(request):
    if request.method == 'POST':
            schoolId = request.POST.get('schoolId', '')
            myschoolId = request.POST.get('myschoolId', '')
            # school = School.objects.only('id').get(id=myschoolId)
            # school.locaton_map  = request.POST.get('latitude', '')
            # school.locaton_map = request.POST.get('longitude', '')
            # school.broadband = request.POST.get('broadband', '')
            # school.computer = request.POST.get('computer', '')
            # school.screen = request.POST.get('screen', '')
            # school.camera = request.POST.get('camera', '')
            # school.save()
            mySchool = MySchool.objects.get(id=myschoolId)

            # teachersAvailable= setSchoolDetail.object.get()
            latitude = request.POST.get('latitude', '')
            longitude = request.POST.get('longitude', '')
            broadband = request.POST.get('broadband', '')
            computer = request.POST.get('computer', '')
            screen = request.POST.get('screen', '')
            camera = request.POST.get('camera', '')
            other_log_info = {}
            # other_log_info['AvailableTeacher']= setSchoolDetail(teachersAvailable)
            other_log_info['schoolCode'] = schoolId
            other_log_info['schoolName'] = mySchool
            other_log_info['broadband'] = broadband
            other_log_info['latitude'] = latitude
            other_log_info['longitude'] = longitude
            other_log_info['computer'] = computer
            other_log_info['screen'] = screen
            other_log_info['camera'] = camera
            cur = connection.cursor()
            cur.execute("SELECT myschool_id FROM partner_myschoolstatus where myschool_id = "+ str(myschoolId) )

            if cur.fetchone():
                myschoolstatus = MySchoolStatus.objects.update(added_by=request.user, other_info=other_log_info)
                mySchool.status = 'Verified'
                mySchool.save()
            else:
                myschoolstatus = MySchoolStatus.objects.create(myschool=mySchool, added_by=request.user,other_info=other_log_info)
                mySchool.status = 'Verification in Progress'
                mySchool.save()
            return  redirect("/v2/vLounge#schoolslist")

    if request.method == 'GET':
        referal_name = request.GET.get('referal_name', '')
        organization_name = ''
        userprofile = request.user.userprofile
        if referal_name:
            partner_id = userprofile.referred_user_id
            organization = Partner.objects.filter(contactperson = partner_id)
            if organization :
                organization_name = organization[0].name_of_organization+'/'
        if has_pref_role(userprofile, "vol_admin") or has_pref_role(userprofile, "vol_co-ordinator") or has_pref_role(userprofile, "support"):
            if has_pref_role(userprofile, "Teacher") or has_pref_role(userprofile, "Center Admin") or has_pref_role(userprofile, "Content Developer") or has_pref_role(userprofile, "Well Wisher") or has_pref_role(userprofile, "Content Admin") or has_pref_role(userprofile,"Class Assistant") or has_pref_role(userprofile, "TSD Panel Member"):
                pass
            else:
                return redirect('/task_list/')
        orientation_status = userprofile.evd_rep
        demand_allocate = {}
        #role = get_role_title(role_name)
        selectionDescussion = []
        onboarding = userprofile.rolepreference_set.all()
        evd_rep_check = userprofile.evd_rep
        availability = False
        modif_step_status = {}
        follow_up_date = ''
        if onboarding :
            availability = RolePreference.objects.get(id=onboarding[0].id).availability
            follow_up_date = RolePreference.objects.get(id=onboarding[0].id).follow_up_date
            selectionDescussion = SelectionDiscussion.objects.filter(userp=userprofile).values_list("start_time", "end_time")
        if onboarding :
            for onboarding  in onboarding :
                role_name = onboarding.role.name
                stepstatuses = onboarding.onboardingstepstatus_set.all().order_by('step__order')
                
                if role_name == 'Teacher' or role_name == 'Facilitator Teacher':
                    demand_booked1 = request.user.demandslot_set.filter(status__in = ['Booked','Allocated'])
                    prefered_days = ''
                    prefered_timings = ''
                    for index, demand in enumerate(demand_booked1):
                        demand_allocate['subject'] = demand.offering.course.subject
                        demand_allocate['grade'] = demand.offering.course.grade
                        center_name = demand.offering.center
                        demand_allocate['center'] = center_name
                        if demand.status == 'Allocated':
                            slots = ''
                            if demand_booked1:
                                slot_details = demand_booked1.values_list('center__name','day','start_time','end_time')
                                i = 0
                                for slot in slot_details:
                                    if i==0:
                                        slots+=str(slot[1])+' '+str(slot[2])+' to '+str(slot[3])
                                    else:
                                        slots+= ' and '+str(slot[1])+' '+str(slot[2])+' to '+str(slot[3])
                                    i+=1

                            demand_allocate['demand_allocated'] = True
                            center_id = demand.center_id
                            offering_id = demand.offering.id
                            offering_accepted = Offering.objects.filter(active_teacher=request.user,id = offering_id).exclude(status='completed').order_by('start_date')
                            if offering_accepted:
                                demand_allocate['offering_accepted'] = True
                            days_mapping_for_user = {'Monday':'Mon', 'Tuesday':'Tue', 'Wednesday':'Wed', 'Thursday':'Thu', 'Friday':'Fri', 'Saturday':'Sat', 'Sunday':'Sun'}
                            prefered_days += days_mapping_for_user[demand.day]
                            prefered_timings += str(demand.start_time)+'-'+str(demand.end_time)
                            if index < 1:
                                prefered_days += ','
                                prefered_timings += ','
                            start_date = int(time.mktime(demand.offering.start_date.timetuple()) * 1000) if demand.offering.start_date else ''
                            start_date = datetime.datetime.fromtimestamp(start_date/1000).strftime("%d-%m-%Y")
                            end_date = int(time.mktime(demand.offering.end_date.timetuple()) * 1000) if demand.offering.end_date else ''
                            end_date = datetime.datetime.fromtimestamp(end_date/1000).strftime("%d-%m-%Y")
                            teacher = request.user.id
                            accepturl ='/v2/accept_decline_mail?userId='+ str(teacher) +'&center_id='+ str(center_id) +'&offering_id='+ str(offering_id) +'&startDate='+str(start_date)+'&endDate='+str(end_date)+'&pref_days='+str(prefered_days)+'&pref_time='+str(prefered_timings)
                            declineurl = '/v2/release_demand?center='+str(center_name)+'&teacher='+str(teacher)+'&slot='+str(slots)+'&flag=true'
                            demand_allocate['prefered_days'] = str(prefered_days)
                            demand_allocate['accepturl'] = accepturl
                            demand_allocate['declineurl'] = declineurl

                step_list1 = []
                for stepstatus in stepstatuses:
                    step_dict = model_to_dict(stepstatus)

                    if step_dict['status'] is True:
                        continue
                    if role_name in ('Teacher', 'Center Admin', 'Facilitator Teacher') and stepstatus.step.stepname == 'Self Evaluation':
                        continue
                    step_dict['step_name'] = stepstatus.step.stepname
                    step_dict['desc'] = stepstatus.step.description
                    step_dict['short_name'] = (stepstatus.step.stepname).replace(' ', '_')
                    step_dict['repeatable'] = stepstatus.step.repeatable
                    # step_dict['role_stat'] = stepstatus.role_preference.role_status
                    step_dict['onboarding_id'] = onboarding.id
                    if role_name == 'Teacher' or role_name == 'Center Admin' or role_name == 'Content Developer' or role_name=='Facilitator Teacher':
                        demand_booked = request.user.demandslot_set.filter(status__in = ['Booked'])
                        for demand in demand_booked:
                            step_dict['subject'] = demand.offering.course.subject
                            step_dict['grade'] = demand.offering.course.grade
                            center_name = demand.offering.center
                            step_dict['center'] = center_name
                            if demand.status == 'Booked':
                                step_dict['demand_booked'] = True

                        discussion_slot_booked = userprofile.selectiondiscussionslot_set.filter(status = 'Booked')
                        
                        for i in discussion_slot_booked:    
                            if role_name == i.role.name :
                                step_dict['discussion_slot_booked'] = True
                                step_dict['slot_booked_time'] = discussion_slot_booked[0].start_time
                                break
                            else:
                                step_dict['discussion_slot_booked'] = False
                    prerequisite = stepstatus.step.prerequisite
                    if prerequisite:
                        pre_step_status = stepstatuses.filter(step=prerequisite)
                        if pre_step_status:
                            step_dict['prerequisite'] = pre_step_status[0].status
                    step_list1.append(step_dict)
                    if step_dict['status'] is False:
                        break
                modif_step_status[role_name] = step_list1

        # settings code starts
        settingsgroup = SettingsGroup.objects.all()
    #     userprofile = UserProfile.objects.get(user=request.user)
        if userprofile.languages_known:
            userprofile.languages_known = literal_eval(userprofile.languages_known)
        else:
            userprofile.languages_known = []
        if userprofile.usersettings_data:
            usersettings_json = literal_eval(userprofile.usersettings_data)
        else:
            usersettings_json = {}
        user_profile_dict = userprofile.get_dict()
        location_fields = ['country', 'state', 'city']
        user_location_info = {}
        for k, v in user_profile_dict.iteritems():
            if k in location_fields and v:
                user_location_info[k] = str(v)
        refchannel = ReferenceChannel.objects.filter(id=userprofile.referencechannel_id)
        if refchannel: refchannel = refchannel[0]
        ref_channels = ReferenceChannel.objects.filter(partner__status='Approved')

    #         curr_user = request.user
        roles, pref_roles, unassigned_offering_arr, prof_per = [], [], [], 35
    #         user_profile = UserProfile.objects.filter(user=curr_user)
        if userprofile:
            admin_assigned_roles = ["TSD Panel Member", "Class Assistant", "vol_admin", "vol_co-ordinator", "Partner Admin", "Content Admin"]
            roles = Role.objects.exclude(name__in=admin_assigned_roles)
            pref_roles = [role.id for role in userprofile.pref_roles.exclude(name__in=admin_assigned_roles)]
        language_dropdown = ['Bengali','Gujarathi','Hindi','Kannada','Marathi','Oriya','Tamil','Telugu']
        unavail_list = [x for x in dict(UserProfile._meta.get_field('unavailability_reason').choices)]
        teacher_flag = False
        if not request.user.is_superuser and request.user.partner_set.all().count() == 0:
            if userprofile and has_role(userprofile, "Teacher"):
                teacher_flag = True

        partner_schools =""
        if request.user.id:
            partner_schools = MySchool.objects.filter(added_by_id=request.user.id).order_by('-added_on')

        isExternal=True
        is_content_developer = False
        is_ft_teacher = False
        centeradmin_status = ''
        teacher_status = ''
        ft_teacher_status = ''
        content_developer_status =''
        if  has_role(request.user.userprofile,"Content Developer"):
            is_content_developer = False
            content_developer_status =  RolePreference.objects.filter(userprofile_id = userprofile.id,role_id= '3').values_list('role_outcome',flat=True)[0]
            
        if  has_role(request.user.userprofile,"Teacher") :
            teacher_status =  RolePreference.objects.filter(userprofile_id = userprofile.id,role_id= '1').values_list('role_outcome',flat=True)[0]
            
        if  has_role(request.user.userprofile,"Center Admin"):
            centeradmin_status =  RolePreference.objects.filter(userprofile_id = userprofile.id,role_id= '2').values_list('role_outcome',flat=True)[0]
        
        if  has_role(request.user.userprofile,"Facilitator Teacher"):
            is_ft_teacher = True
            ft_teacher_status =  RolePreference.objects.filter(userprofile_id = userprofile.id,role_id= '20').values_list('role_outcome',flat=True)[0]
        
        role_list = RolePreference.objects.filter(userprofile_id = userprofile.id).values_list('role_id',flat=True)
        return render(request, 'new_landing_page.html',
                               {'user_profile': userprofile,'isExternal':isExternal,'content_developer_status':content_developer_status,'teacher_status':teacher_status,'centeradmin_status':centeradmin_status ,'partner_schools': partner_schools, 'onboarding': onboarding, 'steps': modif_step_status, \
                                'selection_descussion': selectionDescussion,'settings':settingsgroup,'is_content_developer':is_content_developer, 'ft_teacher_status':ft_teacher_status,
                                'availability': availability,'user_settings':usersettings_json,'user_location_info': user_location_info,
                                'follow_up_date': follow_up_date,'ref_channels': ref_channels,'referencechannel': refchannel, 'roles': roles,
                                'evd_rep_check': evd_rep_check, 'pref_roles': pref_roles,'language_dropdown':language_dropdown,
                                'unavail_list':unavail_list,'teacher_flag':teacher_flag , 'demand_allocate': demand_allocate,
                                'referal_name': referal_name, 'organization_name': organization_name,'role_list':role_list})

@login_required
def update_centerInfo(request):
    if request.method=='GET':       
        center_name=request.GET.get('center_name','')
        center_id=request.GET.get('centerID','')
        user=request.user
        teacher_center = Center.objects.get(id=center_id)
        skype_id='Not available'
        CA_name='Not available'
        hm='Not available'
        CA_phoneno=''
        dc='Not available' 
        dc_phoneno=''
        fc='Not available'
        fc_phoneno=''
        c_admin='Not available'
        c_admin_phoneno=''
        if teacher_center.skype_id:
            skype_id=teacher_center.skype_id
        else: 
            skype_id='Not available'
        
        if teacher_center.assistant:
            try:        
               CA_name=teacher_center.assistant.first_name+" "+teacher_center.assistant.last_name
               CA_phoneno=teacher_center.assistant.userprofile.phone
            except:
              CA_name='Not available'
              CA_phoneno=''
              
        if teacher_center.HM:           
            hm=teacher_center.HM
        else:
            hm='Not available'
        
        if teacher_center.field_coordinator:
            try:       
                fc=teacher_center.field_coordinator.first_name+" "+teacher_center.field_coordinator.last_name
                fc_phoneno=teacher_center.field_coordinator.userprofile.phone
            except:
               fc='Not available'
               fc_phoneno=''
        
        if teacher_center.delivery_coordinator:
            try:
                dc=teacher_center.delivery_coordinator.first_name+" "+teacher_center.delivery_coordinator.last_name
                dc_phoneno=teacher_center.delivery_coordinator.userprofile.phone
            except:
                 dc='Not available' 
                 dc_phoneno=''
        
        if teacher_center.admin:
            try:            
                c_admin=teacher_center.admin.first_name+" "+teacher_center.admin.last_name  
                c_admin_phoneno=teacher_center.admin.userprofile.phone
            except:
               c_admin='Not available'
               c_admin_phoneno=''
        resp={
            'center_name':center_name,
            'skype_id':skype_id,
            'CA_name':CA_name,
            'CA_phoneno':CA_phoneno,
            'hm':hm,
            'fc':fc,
            'fc_phoneno':fc_phoneno,
            'dc':dc,
            'dc_phoneno':dc_phoneno,
            'c_admin':c_admin,
            'c_admin_phoneno':c_admin_phoneno
            }
        return HttpResponse(simplejson.dumps(resp),content_type='application/json') 
    
@login_required
def show_map(request):
    centerName=request.GET.get('center_name','')
    return render_response(request,'ShowMapForCenter.html',{'centerName':centerName})    
    

@login_required
def get_differentDate(request):
    if request.method =='GET':
        sessionId=request.GET.get('sessionId','')
        session_start_date=str(Session.objects.get(id=int(sessionId)).date_start)
        sessionDate=datetime.datetime.strptime(session_start_date.strip(), "%Y-%m-%d %H:%M:%S")
        todayDate=(datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30))
        data={'todayDate':todayDate,'sessionDate':sessionDate}
        return HttpResponse(simplejson.dumps(data,default=myconverter),content_type='application/json')
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__() 
def cancelled_sesssion_status(request):
    if request.method=='GET':
        session_id=int(request.GET.get('session',''))
        session=Session.objects.get(id=session_id)
        session_canclled=session.status
        if session_canclled=='Cancelled':
            cancelled_status="cancelled"
        else:
            cancelled_status="notcancelled"
            
        return HttpResponse(simplejson.dumps({'cancelled_status':cancelled_status}),content_type='application/json')   
    
def tsd_details(request):
    slot_id = request.GET.get('slot_id') 
    panel_member_list = []
    panel_members_obj = UserProfile.objects.filter(role__in = ('7','17'))
    
    
    for panel_member in panel_members_obj:
        data = {'id':panel_member.id,'name': panel_member.user.first_name + " " + panel_member.user.last_name}
        panel_member_list.append(data)
        
    tsd_outcome_list = ['Scheduled', 'Assigned', 'Completed', 'Cancelled']

    cancel_reasons = ['Online on mobile', 'Skype issue', 'No show from volunteer', 'Duplicate booking', 'Existing RFT',
                      'Infra issue', 'Panel missed, rebook', 'Personal Reasons', 'Others']
    booked_slots = {}
    if slot_id:
        slot = SelectionDiscussionSlot.objects.get(pk=slot_id)
        booked_slots['id'] = slot.id
        booked_slots['outcome'] = slot.outcome
    if slot.tsd_panel_member:
            booked_slots['tsd_member'] = slot.tsd_panel_member.user.first_name + " " + slot.tsd_panel_member.user.last_name
        
    return HttpResponse(simplejson.dumps({'booked_slots': booked_slots, 'panel_member_list': panel_member_list,
                                          'tsd_outcome_list': tsd_outcome_list,'cancel_reasons': cancel_reasons}),
                                          content_type='application/json')
    
    

def tsd_user_details(request):
    userId = request.GET.get('userId') 
    userId=int(userId)
    if userId:
        user = User.objects.get(pk = userId)
        userp = user.userprofile
        user_profile_id = userp.id
        role_preference = RolePreference.objects.filter(Q(userprofile_id = user_profile_id) & (Q(role_id = 1) | Q(role_id = 3)))
        try: 
            if role_preference[1].role_outcome != "":
                try:
                    role_status = str(role_preference[0].role_status) + "," +str(role_preference[1].role_status)
                    role_outcome = str(role_preference[0].role_outcome) + "," + str(role_preference[1].role_outcome)
                    if role_preference[0].role_id == 1:
                        roles = "Teacher,Content Developer"
                    else:
                        roles = "Content Developer,Teacher"
                except:
                    role_status = "NA"
                    role_outcome = "NA"
                    roles = "NA"
        except:
            try:
                role_status = str(role_preference[0].role_status)
                role_outcome = str(role_preference[0].role_outcome)
                if role_preference[0].role_id == 1:
                    roles = "Teacher"
                else:
                    roles = "Content Developer"
                
            except:
                role_status = "NA"
                role_outcome = "NA"
                roles = "NA"
        try:
            ref_channel = ReferenceChannel.objects.get(id = userp.referencechannel_id).name
        except:
            ref_channel = userp.old_reference_channel
        data = {'user_id':user.id,'username':user.username,'email':user.email,'skype':userp.skype_id,
                'phone':userp.phone,'medium':userp.pref_medium,'subject':userp.pref_subjects,'location':userp.city + ", " + userp.state,
                'role_status':role_status,'role_outcome':role_outcome,'reference_channel':ref_channel,'roles':roles}
        return HttpResponse(simplejson.dumps(data),content_type='application/json')
    

@login_required
def add_userprofile(request):
    if request.method == 'GET':
        user_location_info = {'country': '', 'state': '', 'city': ''}
        ref_channels = ReferenceChannel.objects.filter(partner__status='Approved')
        return render(request,'add_userprofile_for_user.html',{'user':request.user,'user_location_info': user_location_info,'ref_channels':ref_channels})
    elif request.method == 'POST':
        user = User.objects.get(id=request.user.id)
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user)
        user.firstname = request.POST.get('firstname')
        user.lastname = request.POST.get('lastname')
        user.email = request.POST.get('email')
        user_profile.secondary_email = request.POST.get('alt_email')
        user_profile.skype_id = request.POST.get('skype_id')
        user_profile.phone = request.POST.get('phone')
        user_profile.gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        dateofbirth = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
        user_profile.dob = dateofbirth
        user_profile.pref_medium = request.POST.get('prefered_medium')
        user_profile.languages_known = [{u'lang': request.POST.get('prefered_medium'), u'write': 1, u'read': 1, u'speak': 1}]
        # refer = request.POST.get('refer')
        # reference_id = request.POST.get('reference_id')
        # referrence_channel = request.POST.get('referrence_channel')
        user_profile.country = request.POST.get('country')
        user_profile.state = request.POST.get('state')
        user_profile.city = request.POST.get('city')
        user_profile.profession = request.POST.get('profession')
        user_profile.short_notes = request.POST.get('short_notes')
        user_profile.profile_completion_status = True
        user_profile.user.save()
        user_profile.save()
        return  HttpResponseRedirect('/myevidyaloka/')

def save_rubaru_even_data(request):
    today_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
    name = request.GET.get('name')
    email = request.GET.get('email')
    designation = request.GET.get('designation')
    organization = request.GET.get('organization')
    allergies = request.GET.get('allergies')
    comment = request.GET.get('comment')
    if email:
        try:
            rubaru  = RubaruRegistration.objects.get(email = email)
        except RubaruRegistration.DoesNotExist:
            rubaru = None
        if rubaru:
            return HttpResponse("You have already registered !")
        
        rubaru = RubaruRegistration(name = name , email = email , designation = designation , organization = organization ,allergies = allergies , comment = comment ,created_date = today_date)
        rubaru.save() 
        return HttpResponse("Registered Successfully.")

    
@login_required  
def get_external_roles_volunteer(request):
    search_term = request.GET.get('term', '')
    center_id = request.GET.get('center_id')
    centerobj = Center.objects.get(pk=center_id)
    user_id=request.user.id
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)
    users_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select auth_user.id , CONCAT( auth_user.id ,' :: ',auth_user.first_name ,' ' ,auth_user.last_name) as value from web_offering  inner join auth_user on web_offering.active_teacher_id=auth_user.id where auth_user.id != "+str(user_id)+" and web_offering.center_id="+str(center_id)+" and web_offering.status='running' and active_teacher_id is not null "
    query +=" and (auth_user.first_name like '%"+search_term+"%' or auth_user.last_name like '%"+search_term+"%' )  group by auth_user.id limit 50"
    users_cur.execute(query)
    volunteers = users_cur.fetchall()
    db.close()
    users_cur.close()
    return HttpResponse(simplejson.dumps(volunteers))
    

@login_required  
def get_external_roles_partner(request):
    search_term = request.GET.get('term', '')
    user_id=request.user.id
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)
    users_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select auth_user.id , CONCAT( auth_user.id ,' :: ',auth_user.first_name ,' ' ,auth_user.last_name) as value from auth_user inner join partner_partner on auth_user.id=partner_partner.contactperson_id where partner_partner.status='Approved' " 
    query +=" and (auth_user.first_name like '%"+search_term+"%' or auth_user.last_name like '%"+search_term+"%')  group by auth_user.id limit 50"
    users_cur.execute(query)
    partners = users_cur.fetchall()
    db.close()
    users_cur.close()

    return HttpResponse(simplejson.dumps(partners))


@login_required  
def get_external_roles_pam(request):
    type_id = request.GET.get('partner_type_id', '')
    search_term = request.GET.get('term', '')
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)
    users_cur = db.cursor(MySQLdb.cursors.DictCursor)
    if type_id == "Delivery Partner" :
        type=1,3
    if type_id == "Funding Partner" :
        type=1,2
    if type_id == "Volunteering Partner" :
        type=2,3
    query = "select pam from partner_partner_partnertype where partnertype_id in "+str(type)+" and pam is not null"
    users_cur.execute(query)
    type_pam = [str(each['pam']) for each in users_cur.fetchall()]
    type_pam.sort()
    user_id=request.user.id
    type_pam = tuple(map(int, type_pam))

    if len(type_pam) == 1 :
        type_pam = type_pam[0]
        query = "select auth_user.id , CONCAT( auth_user.id ,' :: ',auth_user.first_name ,' ' ,auth_user.last_name) as value from auth_user inner join web_userprofile  on auth_user.id = web_userprofile.user_id inner join web_rolepreference  on web_userprofile.id = web_rolepreference.userprofile_id where web_rolepreference.role_id = 15  and web_rolepreference.role_outcome= 'recommended' and auth_user.id not in ("+str(type_pam)+")" 
        query +=" and (auth_user.first_name like '%"+search_term+"%' or auth_user.last_name like '%"+search_term+"%')  group by auth_user.id limit 50"
    elif len(type_pam) == 0 :
        query = "select auth_user.id , CONCAT( auth_user.id ,' :: ',auth_user.first_name ,' ' ,auth_user.last_name) as value from auth_user inner join web_userprofile  on auth_user.id = web_userprofile.user_id inner join web_rolepreference  on web_userprofile.id = web_rolepreference.userprofile_id where web_rolepreference.role_id = 15  and web_rolepreference.role_outcome= 'recommended' "
        query +=" and (auth_user.first_name like '%"+search_term+"%' or auth_user.last_name like '%"+search_term+"%')  group by auth_user.id limit 50"
    else:
        query = "select auth_user.id , CONCAT( auth_user.id ,' :: ',auth_user.first_name ,' ' ,auth_user.last_name) as value from auth_user inner join web_userprofile  on auth_user.id = web_userprofile.user_id inner join web_rolepreference  on web_userprofile.id = web_rolepreference.userprofile_id where web_rolepreference.role_id = 15  and web_rolepreference.role_outcome= 'recommended' and  auth_user.id not in "+str(type_pam)+""
        query +=" and (auth_user.first_name like '%"+search_term+"%' or auth_user.last_name like '%"+search_term+"%')  group by auth_user.id limit 50"

    users_cur.execute(query)
    pam = users_cur.fetchall()
    db.close()
    users_cur.close()

    return HttpResponse(simplejson.dumps(pam))


@login_required 
def get_sticker_and_reason(request):
    reason_type = request.GET.get('reason_type', '')
    for_whom = request.GET.get('for_whom', '')
    reason_data = []
    stickers_data = []
    appreciation_reason = AppreciationReason.objects.filter(reason_type = reason_type , for_whom = for_whom)
    for reason_obj in appreciation_reason:
        reason_data.append({'id':reason_obj.id,'reason':reason_obj.reason})
        
    stickers = Stickers.objects.filter(sticker_type = reason_type , for_whom = for_whom)
    
    for sticker_obj in stickers:
        stickers_data.append({'id':sticker_obj.id,'sticker_name':sticker_obj.sticker_name,'path':str(sticker_obj.sticker_path)})
    return HttpResponse(simplejson.dumps({'reason':reason_data,'sticker':stickers_data}),content_type='application/json')
    
@csrf_exempt     
@login_required  
def submitt_appreciation(request):
    today_date = datetime.datetime.now()
    appreciationId = request.POST.get('appreciationId', '')
    stickerId = request.POST.get('stickerId', '')
    volunteerId = request.POST.get('volunteerId', '')
    # student_id = request.POST.get('student_id', '')
    offering_id = request.POST.get('offering_id', '')
    for_whom = request.POST.get('for_whom', '')
    otherReason = request.POST.get('otherReason', '')
    reason_type = request.POST.get('reason_type', '')
    comment = request.POST.get('comment', '')
    # if otherReason:
    #     try:
    #         appre_reason = AppreciationReason.objects.get(reason_type = reason_type,for_whom = for_whom,reason = otherReason)
    #     except AppreciationReason.DoesNotExist:
    #         appre_reason = AppreciationReason.objects.create(reason_type = reason_type, for_whom = for_whom, reason = otherReason,added_by = request.user)

    to_whom = None
    appreciationReason = None
    stickers = None
    offering =None
    if for_whom == 'volunteer':
        if volunteerId:
            try:
                to_whom = User.objects.get(id = volunteerId)
            except User.DoesNotExist:
                pass

    elif for_whom == 'student':
        try:
            to_whom = Student.objects.get(id = volunteerId)
        except Student.DoesNotExist:
            pass

    if appreciationId!=str('others').lower():
        try:
            appreciationReason = AppreciationReason.objects.get(id = appreciationId)
        except AppreciationReason.DoesNotExist:
            pass
    # else:
    #     appreciationReason = appre_reason
        
    if stickerId:
        try:
            stickers = Stickers.objects.get(id = stickerId)
        except Stickers.DoesNotExist:
            pass

    if offering_id:
        try:
            offering = Offering.objects.get(id=offering_id)
        except Offering.DoesNotExist:
            pass

    if to_whom and appreciationReason and stickers:
        recognition = Recognition.objects.create(reason = appreciationReason,sticker = stickers,
                      added_by = request.user,added_on = today_date,content_object = to_whom ,
                      object_id = to_whom.id,detailed_reason = comment, offering = offering)
        recognition.save()
        return HttpResponse("Success")
    else:
        return HttpResponse("Error")
    

    
    

@login_required
def add_vol_of_month(request):
    return render_response(request, "add_vol_of_month.html", {})


def get_vol_of_month(request):
    search_term = request.GET.get('term')
    category = request.GET.get('category') 
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = " select au.id, concat(au.id,'::',au.first_name,'  ',au.last_name) as value \
             from auth_user au,web_userprofile wup,web_rolepreference wrp  where \
             au.id=wup.user_id and wup.id=wrp.userprofile_id  and (wrp.role_id=1 or wrp.role_id=3) and \
             wrp.role_outcome in('Recommended','Inprocess')  and wup.pref_medium='"+ category +"'"
    if search_term is not None and search_term != '':
        query += " and au.first_name like '%" + search_term + "%' group by au.id"   
    dict_cur.execute(query)
    teachers_data = dict_cur.fetchall() 
    db.close()
    dict_cur.close()
    
    return HttpResponse(simplejson.dumps(teachers_data), content_type='application/json')

def save_vol_of_month(request):
    addEditParam = request.GET.get('addEditParam','')
    category = request.GET.get('category','')
    volunteer = request.GET.get('volunteer','')
    volunteer_id = volunteer.split('::')[0]
    user = User.objects.get(id = volunteer_id)
    year = request.GET.get('year','')
    month = request.GET.get('month','')
    write_up = request.GET.get('write_up','')
    status = request.GET.get('status','')
    added_updated_by = request.user
    curr_date = datetime.datetime.now()
    
    #for edit
    vol_of_id = request.GET.get('vol_of_id','')
    data = {}
    
    if addEditParam == 'add':
        vol_of_month_user = VolOfMonth.objects.filter(elected_user_id = volunteer_id, year = year, month = month)
        if len(vol_of_month_user) == 0:
            try:
                save_volunteer = VolOfMonth(elected_user = user, category = category, year = year, month = month, \
                                               writeup = write_up, added_by = added_updated_by, added_on = curr_date, \
                                               updated_by = added_updated_by, updated_on = curr_date, status = status)
                save_volunteer.save()
                msg = "Volunteer added successfully"
            except:
                msg = "Error in adding volunteer try again"

            data = {'msg': msg}
        else:
            data = {'msg': "Volunteer {} is already added.".format(volunteer.split('::')[1])}

        return HttpResponse(simplejson.dumps(data), content_type='application/json')
    else: 
        try:
            update_user = VolOfMonth.objects.filter(id = vol_of_id)
            update_user.update(elected_user = user, category = category, year = year, month = month, \
                                               writeup = write_up, updated_by = added_updated_by, \
                                               updated_on = curr_date, status = status)
            msg = "Volunteer details updated successfully"
        except:
            msg = "Failed to update details please try again"
        data = {'msg': msg}
        return HttpResponse(simplejson.dumps(data), content_type='application/json')
    return redirect("/v2/list_vol_of_month")

def list_vol_of_month(request):
    succ_msg = request.GET.get('succ_msg','')
    vol_of_month = VolOfMonth.objects.filter(status='approved')
    for vol_of_month1 in vol_of_month:
        vol_of_month1.center_names = vol_of_month1.elected_user.offering_set.all().values_list('center__name',flat=True).distinct()
    return render_response(request, "list_vol_of_month.html", {'vol_of_month': vol_of_month, 'succ_msg': succ_msg})

def edit_vol_of_month(request):
    user_id = request.GET.get('user_id', '')
    user_details = VolOfMonth.objects.get(elected_user = user_id)
    if user_details:
        user = {
        'elected_user' : str(user_details.elected_user.id)+'::'+str(user_details.elected_user.first_name)+' '+ str(user_details.elected_user.last_name), #au.id,'::',au.first_name,'  ',au.last_name
        'category' : user_details.category,
        'month' : user_details.month,
        'year': user_details.year,
        'status' : user_details.status,
        'writeup' : user_details.writeup,
        'vol_of_id': user_details.id
        }
    return render_response(request, "add_vol_of_month.html", {'user_details': user})

#--------------------Holiday list functions and  Apply Holidays------------------------

@login_required
def holidaylistform(request):
    if request.method == "GET":
        holiday_form = HolidaysForm()
        boards = Center.objects.filter(status="Active").values_list("board", flat=True).distinct().order_by("board")
        board_choices = [("","Select Board")]+[(i, i) for i in boards]
        board_choices = tuple(board_choices)
        holiday_form.fields["board"].choices = board_choices
        add_holidays_form = Add_HolidaysForm()
        return render(request, 'holidaylist.html', {'holiday_form': holiday_form,"list_view":False,'add_holidays_form': add_holidays_form})
    elif request.method == "POST":
        holiday_form = HolidaysForm(request.POST)
        boards = Center.objects.filter(status="Active").values_list("board", flat=True).distinct().order_by("board")
        board_choices = [("","Select Board")]+[(i, i) for i in boards]
        board_choices = tuple(board_choices)
        holiday_form.fields["board"].choices = board_choices

        form_board = request.POST.get("board", "")
        academic_yr_choices = get_academic_year_choices(form_board)
        holiday_form.fields["academic"].choices = academic_yr_choices

        form_calender = request.POST.get("academic", "")
        calender_choices = get_calender_Choices(form_board,form_calender)
        holiday_form.fields["calender"].choices = calender_choices

        calender_id = request.POST.get("calender")

        center = request.POST.get("center")
        district = request.POST.get("district")
        filters = {}
        if district:
            filters['district'] = district
        if center:
            filters['center'] = center
        holidays = Holiday.objects.filter(calender=int(calender_id)).filter(**filters).values().order_by("day")
        for i in holidays:
            i['day_date']=datetime.datetime.strftime(i['day'],"%d/%m/%Y")
        add_holidays_form = Add_HolidaysForm()
        district = Center.objects.filter(status="Active",board=form_board).values_list("district", flat=True).distinct().order_by("district")
        district_choices = [("", "Select District")] + [(i, i) for i in district]
        district_choices = tuple(district_choices)
        add_holidays_form.fields["district"].choices = district_choices
        holiday_form.fields["district"].choices = district_choices

        if filters['district']:
            centers = Center.objects.filter(status="Active",board=form_board, district=filters['district']).values_list("name", flat=True).distinct().order_by("district")
        else:
            centers = Center.objects.filter(status="Active",board=form_board).values_list("name", flat=True).distinct().order_by("district")
        center_choices = [("", "Select Center")] + [(i, i) for i in centers]
        center_choices = tuple(center_choices)
        holiday_form.fields["center"].choices = center_choices
        return render(request, 'holidaylist.html', {'holiday_form': holiday_form,'add_holidays_form': add_holidays_form,'holidays': holidays, "list_view": True})
    else:
        return render(request, 'holidaylist.html', {'holiday_form': holiday_form})


def get_center_choise(district):
    centers = Center.objects.filter(district=district).values_list("name", flat=True).distinct().order_by("name")
    center_choise = [(i, i) for i in centers]
    return center_choise

def get_calender_Choices(board,academic_yr):
    db_calender = Calender.objects.filter(board=board,academic_year_id=academic_yr).values_list("name","id").distinct().order_by("name")
    calender_list = []
    for calender in db_calender:
        calender_list.append(calender)
    calender_choices = [(i[1],i[0]) for i in calender_list]
    return calender_choices

def get_academic_year_choices(board):
    if board is not None:
        academic_yr = Ayfy.objects.filter(board=board).values_list("board", "title", "id").order_by("-id")
    else:
        academic_yr = Ayfy.objects.filter().values_list("board", "title", "id").order_by("-id")
    academic_yr_choices = [(i[2], i[0] + " - " + i[1]) for i in academic_yr]
    return academic_yr_choices

def getHolidaysDropdowns(request,type_name):
    if request.method == "GET":
        if type_name == "getacademic_year":
            board = request.GET.get("board", "")
            academic_yr_choices = get_academic_year_choices(board)
            return HttpResponse(json.dumps(academic_yr_choices), content_type='application/json')
        elif type_name == "getcalender":
            board = request.GET.get("board", "")
            title = request.GET.get("academic_yr", "")
            calender_choices = get_calender_Choices(board, title)
            return HttpResponse(json.dumps(calender_choices), content_type='application/json')
        elif type_name == "getdistrict":
            district = request.GET.get("district", "")
            get_district_choise1 = get_center_choise(district)
            return HttpResponse(json.dumps(get_district_choise1), content_type='application/json')
        elif type_name == "getcenter":
            board = request.GET.get("board", "")
            if request.user.is_superuser:
                centers = Center.objects.filter(board=board).values_list("name", "id").distinct().order_by("name")
            else:
                centers = Center.objects.filter(
                    Q(board=board) & Q(status="Active") & (Q(field_coordinator_id=request.user.id) | Q(
                        delivery_coordinator_id=request.user.id))).values_list("name", "id").distinct().order_by("name")
            center_choices = [(i[1], i[0]) for i in centers]
            return HttpResponse(json.dumps(center_choices), content_type='application/json')
        elif type_name == "getoffering":
            center = request.GET.get("center", "")
            get_district_choise1 = getoffering_choise(center)
            return HttpResponse(json.dumps(get_district_choise1), content_type='application/json')


def getcenter_choise(board):
    centers = Center.objects.filter(board=board).values_list("name","id").distinct().order_by("name")

    center_choise = [(i[1], i[0]) for i in centers]

    return center_choise

def getoffering_choise(center):
    offerings = Offering.objects.filter(center_id=center,status="running").values("course_id","start_date","end_date","id")
    list=[]
    for i in offerings:
         st_date=startdate(i['start_date'].strftime("%Y-%m-%d"))
         ed_date = enddate(i['end_date'].strftime("%Y-%m-%d"))
         cource = Course.objects.filter(id= i['course_id']).values()
         dict={'subject':str(cource[0]['grade'])+"th"+" "+cource[0]['subject']+" "+st_date+" "+"to"+" "+ed_date,'id':cource[0]['id'],'offring_id':i['id']}
         list.append(dict)
    course_choise = [(i['offring_id'],i['subject']) for i in list]
    return list

def startdate(stdate):
    date=datetime.datetime.strptime(str(stdate), "%Y-%m-%d")
    st_year =date.year
    monnth = date.month
    st_day =date.day
    st_month=make_month(monnth)
    start_date1=(str(st_day) + "th"+" " + st_month+","+" "+str(st_year))
    return start_date1

def enddate(eddate):
    date=datetime.datetime.strptime(str(eddate), "%Y-%m-%d")
    st_year =date.year
    monnth = date.month
    st_day =date.day
    st_month=make_month(monnth)
    start_date1=(str(st_day) + "th"+" " + st_month+","+" "+str(st_year))
    return start_date1


def make_month(month_of_year):
    if (month_of_year) == 1:
        month = "Jan"
    elif (month_of_year) == 2:
        month = "Feb"
    elif (month_of_year) == 3:
        month = "Mar"
    elif (month_of_year) == 4:
        month = "Apr"
    elif (month_of_year) == 5:
        month = "May"
    elif (month_of_year) == 6:
        month = "Jun"
    elif (month_of_year) == 7:
        month = "July"
    elif (month_of_year) == 8:
        month = "Aug"
    elif (month_of_year) == 9:
        month = "Sep"
    elif (month_of_year) == 10:
        month = "Oct"
    elif (month_of_year) == 11:
        month = "Nov"
    elif (month_of_year) == 12:
        month = "Dec"
    return month

def updateHoliday(request):
    if request.method == "POST":
        id = request.POST.get("id")
        day = str(request.POST.get("day")).split('/')
        new_date = datetime.datetime(int(day[2]), int(day[1]), int(day[0]))
        description = request.POST.get("description")
        convt_date = new_date.strftime('%Y-%m-%d')
        # convt_date = datetime.datetime.strptime(day, '%d/%m/%Y').strftime('%Y-%m-%d')
        holidays = Holiday.objects.filter(id=int(id)).update(day=convt_date,description=description)
        return HttpResponse(holidays)

def deleteHoliday(request):
    if request.method == "POST":
        id = request.POST.get("id")
        del_holidays = Holiday.objects.filter(id=int(id)).delete()
        return HttpResponse(del_holidays)


def AddHolidays(request):
    if request.method == "POST":
        try:
            date=request.POST.get("date")
            convt_date = datetime.datetime.strptime(date, '%Y-%m-%d')
            if request.POST.get("description") and request.POST.get("date"):
                obj = Holiday()
                centerList = request.POST.getlist("centerList[]")
                if request.POST.get("center") == "All":
                    for i in range(len(centerList)):
                        obj = Holiday()
                        center = Center.objects.get(pk = int(centerList[i]))
                        obj.center = center.name
                        obj.district = request.POST.get("district")
                        obj.calender_id = request.POST.get("calender_id")
                        obj.description = request.POST.get("description")
                        obj.day = convt_date.date()
                        obj.save()
                else:
                    center = Center.objects.get(pk = int(request.POST.get("center")))
                    obj.center = center.name
                    obj.district = request.POST.get("district")
                    obj.calender_id = request.POST.get("calender_id")
                    obj.description = request.POST.get("description")
                    obj.day = convt_date.date()
                    obj.save()
                status='success'
            else:
                status='failure'
            return HttpResponse(simplejson.dumps({'status': status}), mimetype='application/json');
        except Exception as e:
            status ="db_issue"
            return HttpResponse(simplejson.dumps({'status': status}), mimetype='application/json');


@login_required
def Apply_holidays(request):
    if not request.user.is_superuser:
        applyholiday_form = Apply_HolidaysForm()
        boards = Center.objects.filter(Q(status = "Active") & (Q(field_coordinator_id = request.user.id) | Q(delivery_coordinator_id = request.user.id))).values_list("board", flat=True).distinct().order_by("board")
    elif request.user.is_superuser:
        applyholiday_form = Apply_HolidaysForm()
        boards = Center.objects.filter(status="Active").values_list("board", flat=True).distinct().order_by("board")
    if request.method == "POST":
        applyholiday_form = Apply_HolidaysForm(request.POST)

        calender_id = request.POST.get("calender")
        form_board = request.POST.get("board", "")
        offering_id = request.POST.get("offering")
        #district_id = request.POST.get("district")
        center_id = request.POST.get("center")
        #center_id = Center.objects.get(name = center_id).id
        academic_id = request.POST.get("academic")

        board_choices = [("","Select Board")]+[(i, i) for i in boards]
        board_choices = tuple(board_choices)
        applyholiday_form.fields["board"].choices = board_choices

        academic_yr_choices = get_academic_year_choices(form_board)
        applyholiday_form.fields["academic"].choices = academic_yr_choices

        calender_choices = get_calender_Choices(form_board,academic_id)
        applyholiday_form.fields["calender"].choices = calender_choices

        center_choices = getcenter_choise(form_board)
        applyholiday_form.fields["center"].choices = center_choices
        offering_choices = []

        if center_id:
            center = Center.objects.get(pk = int(center_id))
            holidays = Holiday.objects.filter(center = center.name,calender_id = int(calender_id))
            if holidays:
                offering_choices = getoffering_choise(center_id)
        return render(request, 'applyholidays.html', {'applyholiday_form': applyholiday_form,'display_holidays': offering_choices, "list_view": True})
    elif request.method == "GET":
        board_choices = [("","Select Board")]+[(i, i) for i in boards]
        board_choices = tuple(board_choices)
        applyholiday_form.fields["board"].choices = board_choices
        return render(request, 'applyholidays.html', {'applyholiday_form': applyholiday_form,"list_view":False})
    else:
        return render(request, 'applyholidays.html', {'applyholiday_form': applyholiday_form})

#-=====================Delete Holiday Sessions===================

def fetch_apply_holiday(request):
    if request.method == "POST":
        calender_id = request.POST.get("calender_id")
        form_board = request.POST.get("board", "")
        offering_id = request.POST.getlist("offering_id[]")
        center_id = request.POST.get("center")
        academic_id = request.POST.get("academic_id")

        district_name = Center.objects.filter(id=center_id).values('district','name').distinct().order_by("board")
        holidays = Holiday.objects.filter(Q(calender=int(calender_id)) | Q(district=district_name[0]['district']) | Q(center=district_name[0]['name'])).values().order_by("day")
        holiday_list = []
        session_list = {}
        offering_session_holiday = {}
        for i in holidays:
            convt_date = i['day'].strftime("%Y-%m-%d")
            holiday_list.append(convt_date)
        offering_ids = [int(ids) for ids in offering_id ]
        session = Session.objects.filter(offering_id__in = offering_ids)
        for j in session:
            convt_date = j.date_start.strftime("%Y-%m-%d")
            ed_date = j.date_end.strftime("%Y-%m-%d")
            offering_data = str(j.offering.course.grade)+"th "+str(j.offering.course.subject)#+" "+str(j.offering.start_date.strftime("%Y-%m-%d"))+" to "+str(j.offering.end_date.strftime("%Y-%m-%d"))
            if convt_date in holiday_list:
                if str(int(j.offering.id)) in offering_session_holiday:
                    offering_session_holiday[str(int(j.offering.id))]['session'].append({'start_date':convt_date,'end_date':ed_date,'id':j.id})
                else:
                    offering_session_holiday[str(int(j.offering.id))] = {} #str(int(j.offering.id))
                    offering_session_holiday[str(int(j.offering.id))]['name'] = offering_data
                    offering_session_holiday[str(int(j.offering.id))]['session'] = [{'start_date':convt_date,'end_date':ed_date,'id':j.id}]
            else:
                pass
        return HttpResponse(simplejson.dumps(offering_session_holiday), mimetype='application/json')

@login_required
def getboards(request):
    centers_boards_all = Center.objects.filter(status = 'Active').values_list('board', flat=True).distinct().order_by('board')
    return render_response(request, 'applyholidays.html', {'boards': centers_boards_all} )


def Delete_singleoffering_Sessions(request):
    if request.method == "POST":
        offer_ids= request.POST.getlist("offering_id[]")
        count = 0
        for _id in offer_ids:
            session_dates = request.POST.getlist("session_dates[" + str(_id) + "][]")
            for date in session_dates:
                try:
                    session = Session.objects.get(offering_id = _id, date_start__gte = str(date)+' 00:00:00',date_start__lte=str(date)+' 23:59:59').delete()
                except Session.DoesNotExist:
                    pass
                except Session.MultipleObjectsReturned:
                    sessions = Session.objects.filter(offering_id = _id, date_start__gte = str(date)+' 00:00:00',date_start__lte=str(date)+' 23:59:59')
                    for each in sessions:
                        each.delete()
                        count = count + 1
                else:
                    count = count + 1
        msg = {'msg':'{} Sessions Deleted Succesfully'.format(str(count))}
        return HttpResponse(simplejson.dumps(msg), mimetype='application/json')
        # msg = "Error in deleted session try again"
        # return HttpResponse(msg)

def get_holidaysList_to_add_holiday(request):
    board_name = request.GET.get("board_id")
    academic_id = request.GET.get("academic_id")
    calender_id = request.GET.get("calender_id")
    board_list = []
    academic_joson = {}
    calender_json = {}
    board_list = Center.objects.filter(status="Active").values_list("board", flat=True).distinct().order_by("board")
    board_list = [ val for val in board_list]
    if board_name:
        for value in get_academic_year_choices(board_name):
            academic_joson[int(value[0])] = str(value[1])
    if academic_id and board_name:
        for value in get_calender_Choices(board_name,academic_id):
            calender_json[int(value[0])] = str(value[1])
    data = {'board_list':board_list,'academic_list':academic_joson,'calender_list':calender_json}

    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def get_academic_years_by_board(request):
    board_name = request.GET.get("board_name")
    academic_json = {}
    district_list = []
    center_json = {}
    if board_name:
        centers_list = Center.objects.filter(status="Active",board=board_name).values("district","name","id").distinct().order_by("district")
        for center in centers_list:
            district_list.append(center['district'])
            center_json[center['id']] = center['name']
        for value in get_academic_year_choices(board_name):
            academic_json[int(value[0])] = str(value[1])

    return HttpResponse(simplejson.dumps({'academic_json':academic_json,'district':list(set(district_list)),'center_json':center_json}), mimetype='application/json')

def get_calender_by_academic_id(request):
    board_name = request.GET.get("board_name")
    academic_id = request.GET.get("academic_id")
    calender_json = {}
    if board_name and academic_id:
        for value in get_calender_Choices(board_name,academic_id):
            calender_json[int(value[0])] = str(value[1])
    return HttpResponse(simplejson.dumps(calender_json), mimetype='application/json')

@csrf_exempt
def deleting_student(request):
    std_id=eval(request.POST['my_check_box_ids'])
    std_ids = []
    for i in std_id:
        std_ids.append(i.split('_')[1])
    students = Student.objects.filter(id__in=std_ids)
    for student in students:
        student.status='Inactive'
        student.save()
    return HttpResponse('Updated Successfully')


#Function for promoting students
def students_grade_promotion(request):
    try:
        promote_grade		= request.POST.get('grade_to_promote')
        students_ids_list	= request.POST.getlist('selected_students[]')
        selected_grade		= request.POST.get('grade')
        selected_gender		= request.POST.get('gender')
        selected_status		= request.POST.get('status')
        selected_center		= request.POST.get('center_id')
        is_all_students		= str(request.POST.get('is_all'))

        is_all_students		= True if is_all_students == "1" else False

        number_of_students_to_be_promoted = 0
        if students_ids_list is not None:
            student_ids = []

        center = Center.objects.get(pk=selected_center)

        if is_all_students:
            
            students_data = Student.objects.filter(center=selected_center, grade=selected_grade)

            if selected_gender != "" and selected_status != "":
                gender = ("male","boy") if selected_gender.lower() == "male" else ("female","girl")
                student_ids = students_data.values_list('id', flat = True).filter(status=selected_status, gender__in=gender).order_by("-id")
            elif selected_gender != "" and selected_status == "":
                gender = ("male","boy") if selected_gender.lower() == "male" else ("female","girl")
                student_ids	= students_data.values_list('id', flat = True).filter(gender__in=gender).order_by("-id")
            elif selected_grade == "" and selected_status != "":
                student_ids	= students_data.values_list('id', flat = True).filter(status=selected_status).order_by("-id")
            else:
                student_ids	= students_data.values_list('id', flat = True).order_by("-id")

        else:
            for i in students_ids_list:
                student_ids.append(str(i).split('_')[1])
        filtered_student = Student.objects.filter(id__in = student_ids)

        number_of_students_to_be_promoted = len(filtered_student)
        number_of_student_promoted = 0

        for student in filtered_student:		
            student_details = {}
            student_details['promoted_on'] = datetime.datetime.now()
            student_details['promote_grade'] = promote_grade
            student_details['updated_by'] = request.user

            acaedemic_year = Ayfy.objects.filter(board = student.center.board).order_by('-id')[:1]
            if student.promoted_on is not None:
                if student.promoted_on < acaedemic_year[0].start_date:
                    promote_student(student,student_details)
                    number_of_student_promoted += 1
            else:
                promote_student(student,student_details)
                number_of_student_promoted += 1
            
            grade = int(student.grade)
            Promotion_History.objects.create(student=student, ayfy=acaedemic_year[0], from_grade=grade, to_grade=grade+1, center=center, 
                    promoted_by=request.user, promoted_on=genUtility.getCurrentTime(), created_by=request.user, updated_by=request.user)


        response_message = ''
        if number_of_student_promoted == number_of_students_to_be_promoted:
            response_message = "All selected students are promoted successfully from grade {} to {}.".format(selected_grade, promote_grade)
        elif number_of_student_promoted > 0:
            response_message = "All eligible {} students are promoted from grade {} to {}".format(
                number_of_student_promoted, selected_grade, promote_grade)
        else:
            response_message = "Selected students are not eligible for grade promotion."

        return HttpResponse(response_message)
    except Exception as e:
        traceback.print_exc()
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

def promote_student(student,student_details):
    student.promoted_on = student_details['promoted_on']
    if student_details['promote_grade'] == 'Alumni':
        student.status = 'Alumni'
    else:
        student.grade = student_details['promote_grade']
    student.updated_by = student_details['updated_by']
    student.promoted_by = student_details['updated_by']
    student.save()


def get_centers_by_district(request):
    district = request.GET.get('district')
    center_json = {}
    if district:
        centers_list = Center.objects.filter(status="Active",district = district).values("name","id").distinct().order_by("district")
        for center in centers_list:
            center_json[center['id']] = center['name']
        return HttpResponse(simplejson.dumps({'center_json':center_json}), mimetype='application/json')


def getPam(request):
    data = []
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
    user=settings.DATABASES['default']['USER'],
    passwd=settings.DATABASES['default']['PASSWORD'],
    db=settings.DATABASES['default']['NAME'],
    charset="utf8",
    use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    partner_id = request.GET.get('partner', '')
    partner_type = request.GET.get("partner_type",'')
    partner_id = partner_id.split(":")
    partner_id=partner_id[0]
            
    partner = Partner.objects.filter(contactperson = partner_id).values_list("id",flat=True)
    partner = (tuple(map (int,partner)))
    partner = partner[0]

    query="SELECT CONCAT(auth_user.first_name,' ',auth_user.last_name) as pam from partner_partner_partnertype inner join partner_partner on partner_partner.id=partner_partner_partnertype.partner_id inner join partner_partnertype on partner_partner_partnertype.partnertype_id= partner_partnertype.id inner join auth_user  on partner_partner_partnertype.pam=auth_user.id where partner_partnertype.name='"+str(partner_type)+"'  and partner_partner_partnertype.partner_id='"+str(partner)+"'"

    dict_cur.execute(query)
    pam_name = [str(each['pam']) for each in dict_cur.fetchall()]
    pam_name.sort()

    db.close()
    dict_cur.close()
    data.append({'pam_name':pam_name})     
    return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')


def confirm_pam(request):
    partner_id = request.POST.get('partner_id', '')
    partner_type = request.POST.get("type_id",'')
    partner_id=partner_id.split(":")
    if partner_type == 'Funding Partner':
        partner_typee=3
    elif partner_type == 'Volunteering Partner':
        partner_typee=1
    else :
        partner_typee= 2
    pam_id = request.POST.get('pam_id', '')
    pam_id = pam_id.split(":")
    partner_id=partner_id[0]
    pam_user_id = pam_id[0]
    
    partner_id = Partner.objects.filter(contactperson_id=partner_id).values_list("id",flat=True)
    partner_id = tuple(map(int, partner_id))
    partner_id=partner_id[0]
    conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
               user=settings.DATABASES['default']['USER'],
               passwd=settings.DATABASES['default']['PASSWORD'],
               db=settings.DATABASES['default']['NAME'],
               charset="utf8",
               use_unicode=True)

    cursor = conn.cursor()

    query = "UPDATE partner_partner_partnertype SET pam='"+str(pam_user_id)+"' WHERE partner_id ='"+str(partner_id)+"' and partnertype_id='"+str(partner_typee)+"'"
    cursor.execute(query)
    conn.commit()
    
    return HttpResponse(simplejson.dumps({'status': 'Success'}),mimetype='application/json')

    
def remove_pam(request):
    partner_id = request.POST.get('partner_id', '')
    partner_type = request.POST.get("type_id",'')
    if partner_type == 'Funding Partner':
        partner_typee=3
    elif partner_type == 'Volunteering Partner':
        partner_typee=1
    else :
        partner_typee= 2
    partner_id=partner_id.split(":")
    partner_id=partner_id[0]
    partner_pam = Partner.objects.filter(contactperson_id=partner_id).values_list("id",flat=True)
    partner_pam = tuple(map(int, partner_pam))
    partner_pam = partner_pam[0]
    conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                           user=settings.DATABASES['default']['USER'],
                           passwd=settings.DATABASES['default']['PASSWORD'],
                           db=settings.DATABASES['default']['NAME'],
                           charset="utf8",
                           use_unicode=True)

    cursor = conn.cursor()

    query = "UPDATE partner_partner_partnertype SET pam = NULL WHERE partner_id ='"+str(partner_pam)+"' and partnertype_id='"+str(partner_typee)+"'"
    cursor.execute(query)
    conn.commit()
    return HttpResponse(simplejson.dumps({'status': 'Success'}),mimetype='application/json')


@login_required
def authenticated_user_role(request):
    pam_role = False
    user=request.user.id
    userp = UserProfile.objects.get(user_id=user)
    user_roles = RolePreference.objects.filter(userprofile_id=userp)
    for user_role in user_roles:
        if user_role.role_id == 15:
           pam_role = True
           break
    return HttpResponse(simplejson.dumps(pam_role), mimetype='application/JSON')

    
@login_required
def authenticated_funding_role(request):
    partner = request.user.partner_set.all()
    is_funding = False
    if partner:
        partner_types = partner[0].partnertype.values()
        for partnerty in partner_types:
            if partnerty['name'] == 'Funding Partner':
                is_funding = True
                break
    return HttpResponse(simplejson.dumps(is_funding), mimetype='application/JSON')


def get_language_from_board(board):
    language = [lan[0] for lan in Center.objects.filter(board=board).values_list('language').distinct()]
    return str(language[0])


def get_state_from_board(board):
    state = [state[0] for state in Center.objects.filter(board=board).values_list('state').distinct()]
    return str(state[0])


def get_primary_info(request):
    board = request.POST.get('board')
    start_date = request.POST.get('start_date')
    subject = request.POST.get('subject')
    grade = request.POST.get('grade')
    no_of_teachers_required = request.POST.get('no_of_teachers')

    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")

    return (board, start_date, subject, grade, no_of_teachers_required)


def get_provisionally_booked_slots():
    return ProvisionalDemandslot.objects.filter().values_list('offering_id', flat=True).distinct()


def get_or_create_provisional_center(name, language, board, created_by):
    is_new = False

    board_state = get_state_from_board(board)
    provisional_center = Center.objects.filter(Q(name=name))

    if len(provisional_center) == 0:
        provisional_center = Center.objects.create(name=name, language=language, working_days="Mon,Tue,Wed,Thu,Fri,Sat",
            working_slots="09:00-16:00,09:00-16:00,09:00-16:00,09:00-16:00,09:00-16:00,09:00-16:00",
            state=board_state, board=board, created_by=created_by, status=PROVISIONAL_KEYWORD)

        is_new = True
    else:
        provisional_center = provisional_center[0]

    return (is_new, provisional_center)


def get_or_create_course(board, subject, grade):
    is_new = False
    try:
        course = Course.objects.get(board_name=board, subject=subject, grade=grade, type='S')
    except Course.DoesNotExist:
        # Create if doesn't exists
        course = Course.objects.create(board_name=board, subject=subject, grade=grade, type='S')
        is_new = True
    return (is_new, course)


def get_next_hour(hour):
    hour = list(hour)
    temp = int("".join(hour[:2]))
    temp += 1
    hour[0:2] = list(str(temp)) if temp > 9 else list("0{}".format(str(temp)))
    return "".join(hour)


def create_provisional_center_demand_slots(provisional_center_id, slots_data):
    for day, time in slots_data.items():
        start_time, end_time = time.split("-")
        Demandslot.objects.create(center_id=provisional_center_id, day=day, start_time=start_time.strip(), end_time=end_time.strip(),
                                  user_id=None, offering_id=None, status="Unallocated")

        start_time = get_next_hour(start_time)
        end_time = get_next_hour(end_time)
        Demandslot.objects.create(center_id=provisional_center_id, day=day, start_time=start_time.strip(),
                                  end_time=end_time.strip(),
                                  user_id=None, offering_id=None, status="Unallocated")


def create_provisional_offering(board,course, center_id, language, start_date, end_date, user):
    try:
        accademic_year_id =int(Ayfy.objects.values_list("id",flat=True).filter(start_date__lte = start_date,end_date__gte = start_date,board=board)[0])
    except:
        accademic_year_id = ""
    offer = Offering.objects.create(course=course, center_id=center_id, language=language,
                                    start_date=start_date, end_date=end_date,
                                    status=PROVISIONAL_KEYWORD,
                                    course_type='S', created_date=dt.datetime.now(),
                                    created_by=user,academic_year_id=accademic_year_id)
    return offer


@login_required
def provisionally_booked_demands(request):
    center_id = str(request.GET.get('center', 0))
    course_id = request.GET.get('course_id', 0)
    board_name = request.GET.get('board', '')
    is_conversion = request.GET.get('convert', False)
    #
    # pd_center_name = Center.objects.get(id=center_id)
    #
    # pd_center_name = "{}-{}-{}".format(board_name, PROVISIONAL_CENTER, course_id)
    # center_id = (Center.objects.get(name=pd_center_name)).id

    booked_provisional_slots = ProvisionalDemandslot.objects.filter(center_id=center_id).values_list('user_id',
                                    'offering_id', 'user_pref', 'center_id').distinct()

    json_response = {'volunteers': [None] * len(booked_provisional_slots)}
    name_order = []

    for each in booked_provisional_slots:
        name = User.objects.get(id=each[0])
        full_name = "{} {}".format(name.first_name, name.last_name)
        full_name = full_name.upper()

        name_order.append(full_name)
    name_order = sorted(name_order)

    for each in booked_provisional_slots:
        vol_teacher = {'id': each[0], 'name': '', 'offering_id': each[1], 'user_pref': each[2], 'center': each[3], 'course': course_id, 'board': board_name, 'role_outcome': 'NA'}
        name = User.objects.get(id=each[0])
        vol_teacher['name'] = "{} {}".format(name.first_name, name.last_name)
        vol_teacher['name'] = vol_teacher['name'].upper()
        vol_user_role_pref = RolePreference.objects.filter(userprofile=UserProfile.objects.get(user_id=each[0]), role_id = 1)
        if len(vol_user_role_pref) > 0:
            vol_teacher['role_outcome'] = vol_user_role_pref[0].role_outcome

        db_days = ProvisionalDemandslot.objects.filter(center_id=each[3], offering_id=each[1]).values_list('day', 'start_time', 'end_time')
        slots = {}

        for each_slot in db_days:
            slots[each_slot[0]] = "{}-{}".format(each_slot[1], each_slot[2])

        db_offer_dates = Offering.objects.filter(pk=each[1]).values('start_date', 'end_date')
        for each_entry in db_offer_dates:
            vol_teacher['offer_start'] = str(each_entry['start_date'])
            vol_teacher['offer_end'] = str(each_entry['end_date'])

        vol_teacher['slots'] = slots
        name_order_index = name_order.index(vol_teacher['name'])
        # json_response['volunteers'].append(vol_teacher)
        json_response['volunteers'][name_order_index] = vol_teacher

    if is_conversion:
        json_response['centers'] = []
        if request.user.is_superuser:
            db_board_centers = Center.objects.filter(
                Q(board=board_name) & Q(status__in=['Active', 'Planned'])).order_by("name")
        else:
            db_board_centers = Center.objects.filter(Q(board=board_name) & Q(status__in=['Active', 'Planned']) & (
                    Q(delivery_coordinator_id=request.user.id) | Q(field_coordinator_id=request.user.id))).order_by("name")

        for center in db_board_centers:
            center_data = {'id': center.id, 'name': (center.name).upper(), 'dc': center.delivery_coordinator_id, 'fc': center.field_coordinator_id}
            json_response['centers'].append(center_data)

    return HttpResponse(simplejson.dumps(json_response), mimetype='application/json')


@login_required
def provisional_demand(request):
    cursor = connection.cursor()
    cursor.execute('''SELECT web_provisionaldemandslot.user_id, auth_user.first_name, auth_user.last_name,
    auth_user.email, web_userprofile.pref_medium, web_rolepreference.role_outcome ,
    web_offering.course_id,web_course.subject, web_course.grade,
    web_course.board_name, web_provisionaldemandslot.day, web_provisionaldemandslot.start_time, web_provisionaldemandslot.end_time,
    web_provisionaldemandslot.user_pref,web_provisionaldemandslot.date_booked,web_provisionaldemandslot.status,
    web_rolepreference.recommended_date,web_userprofile.phone
    FROM web_provisionaldemandslot
    inner join auth_user on auth_user.id = web_provisionaldemandslot.user_id
    inner join web_userprofile on web_userprofile.user_id = web_provisionaldemandslot.user_id
    inner join web_offering on web_offering.id = web_provisionaldemandslot.offering_id
    inner join web_course on web_offering.course_id = web_course.id
    inner join web_rolepreference on web_rolepreference.userprofile_id = web_userprofile.id
    where role_id = 1''')
    pd_csvData = cursor.fetchall()
    pdStr = 'user_id,first_name,last_name,email,languages_known,role_outcome,course_id,subject,grade,board_name,day,start_time,end_time,date_booked,status,user_pref,recommended_date,phone\n'
    for i in range(len(pd_csvData)):
        pref = str(pd_csvData[i][13]).split(",")
        preference_full = []
        for pref in pref:
            if pref == "T":
                preference_full.append("Time")
            elif pref == "C":
                preference_full.append("Center")
            elif pref == "S":
                preference_full.append("Subject")
        preference = (','.join(preference_full))
        pdStr = pdStr + str(pd_csvData[i][0])+','+str(pd_csvData[i][1])+','+str(pd_csvData[i][2])+','+str(pd_csvData[i][3])+','+str(pd_csvData[i][4]).replace(',',':')+','+str(pd_csvData[i][5])+','+str(pd_csvData[i][6])+','+str(pd_csvData[i][7])+','+str(pd_csvData[i][8])+','+str(pd_csvData[i][9])+','+str(pd_csvData[i][10])+','+str(pd_csvData[i][11])+','+str(pd_csvData[i][12])+','+str(pd_csvData[i][14])+','+str(pd_csvData[i][15])+','+preference.replace(',',':')+','+str(pd_csvData[i][16])+','+str(pd_csvData[i][17])+'\n'

    user_board = ''
    boards = [str(brd).strip() for brd in Center.objects.values_list('board', flat=True).distinct().order_by("board")]
    centers = None

    if not request.user.is_superuser and request.user.is_active:
        user_profile = UserProfile.objects.filter(Q(user_id=request.user.id)).values('id', 'pref_medium',
                                                                                     'profile_complete_status')
        if user_profile[0]['profile_complete_status'] != "Inactive":
            user_language = user_profile[0]['pref_medium']
            centers = Center.objects.filter(Q(language=user_language), Q(status__in=['Active', 'Planned']),
                                            Q(delivery_coordinator_id=request.user.id) | Q(field_coordinator_id=request.user.id))
            boards = [str(brd).strip() for brd in centers.values_list('board', flat=True).distinct().order_by("board")]
            user_board = boards

    if centers is not None and len(boards) == 0:
        return redirect("/myevidyaloka")

    if "None" in boards:
        idx = boards.index("None")
        boards.pop(idx)

    # subjects = [str(sub).strip() for sub in Course.objects.filter(type='s').values_list('subject', flat=True).distinct().order_by('subject')]
    subjects = ['English Foundation', 'Maths', 'Science']
    if "None" in subjects:
        idx = subjects.index("None")
        subjects.pop(idx)

    provisional_center_id = str(request.GET.get('center', "-1"))
    provisional_course_id = str(request.GET.get('course_id', -1))
    board_name = str(request.GET.get('board', -1))

    if provisional_center_id != "-1":
        db_course_data = Course.objects.get(id=provisional_course_id)
        json_response = {'boards': [str(db_course_data.board_name).strip()], 'subjects': [str(db_course_data.subject).strip()], 'start_date': '', 'end_date': ''}

        linked_offerings = Offering.objects.filter(course_id=provisional_course_id, center_id=provisional_center_id, status="{}".format(PROVISIONAL_KEYWORD))

        if len(linked_offerings) < 1:
            ayfy_data = Ayfy.objects.filter(Q(board=board_name)).order_by("-id")[0]
            json_response['start_date'] = str(ayfy_data.start_date + relativedelta(months=12)).split()[0]
            json_response['end_date'] = str(ayfy_data.end_date + relativedelta(months=12)).split()[0]
        else:
            json_response['start_date'] = str(linked_offerings[0].start_date).split()[0]
            json_response['end_date'] = str(linked_offerings[0].end_date).split()[0]

        time_window = Demandslot.objects.filter(Q(center_id=provisional_center_id) & Q(day='Monday')).values('start_time', 'end_time').order_by("id")

        json_response['start_time'] = str(time_window[0]['start_time'])
        json_response['end_time'] = str(time_window[0]['end_time'])

        return HttpResponse(simplejson.dumps(json_response), mimetype='application/json')

    if request.user.is_superuser:
        provisional_centers = Center.objects.filter(Q(status='Provisional')).values('id', 'name', 'created_by_id', 'board', 'dt_added')
    elif not request.user.is_superuser and request.user.is_active:
        provisional_centers = Center.objects.filter(Q(status='Provisional') & Q(created_by_id=request.user.id)).values('id',
            'name', 'created_by_id', 'board', 'dt_added')

    provisional_demands_list = []
    no_of_provisional_demands = 0
    for pc in provisional_centers:
        center_id = pc['id']
        pc_offerings = Offering.objects.filter(Q(center_id=center_id) & Q(status=PROVISIONAL_KEYWORD))
        pc_offering_courses = pc_offerings.values_list('course_id', flat=True).distinct()
        time_window = Demandslot.objects.filter(Q(center_id=center_id) & Q(day='Monday')).values('start_time', 'end_time').order_by("id")
        provisionally_booked_offerings = ProvisionalDemandslot.objects.filter(Q(center_id=center_id)).values_list(
            'offering_id', flat=True).distinct()

        added_by = pc['created_by_id']
        published_date = str(pc['dt_added']).split()[0]

        db_user = User.objects.get(id=added_by)
        added_by_name = "{} {}".format(db_user.first_name, db_user.last_name)

        start_time = str(time_window[0]['start_time'])[:2]
        end_time = str(time_window[1]['end_time'])[:2]

        if int(start_time) > 11:
            start_time = int(start_time) - 12
            start_time = str(start_time) if start_time > 9 else "0{}".format(str(start_time))
            start_time += " PM"
        else:
            start_time += " AM"

        if int(end_time) > 12:
            end_time = int(end_time) - 12
            end_time = str(end_time) if end_time > 9 else "0{}".format(str(end_time))
            end_time += " PM"
        else:
            end_time += " AM"

        for pd_course in pc_offering_courses:
            db_course = Course.objects.get(id=pd_course)
            pdc_dict = OrderedDict()
            pdc_dict['center_id'] = center_id
            pdc_dict['course_id'] = pd_course
            pdc_dict['board'] = str(db_course.board_name)
            pdc_dict['grade'] = str(db_course.grade)
            pdc_dict['subject'] = str(db_course.subject)
            pdc_dict['count'] = len(pc_offerings)
            pdc_dict['time'] = "{} - {}".format(start_time, end_time)
            pdc_dict['booked_count'] = len(provisionally_booked_offerings)
            pdc_dict['added_by'] = added_by_name
            pdc_dict['published_date'] = published_date
            if str(pdc_dict['count']) != '0':
                provisional_demands_list.append(pdc_dict)
                no_of_provisional_demands += 1

        if len(pc_offering_courses) == 0:
            pdc_dict = OrderedDict()
            pdc_dict['center_id'] = center_id
            center_name = pc['name']

            try:
                temp_board, dummy, course, __ = center_name.split("-")
            except ValueError:
                temp_board, dummy, course = center_name.split("-")

            pdc_dict['course_id'] = course
            pdc_dict['board'] = temp_board

            db_course = Course.objects.get(id=course)
            pdc_dict['grade'] = str(db_course.grade)
            pdc_dict['subject'] = str(db_course.subject)
            pdc_dict['count'] = '0'
            pdc_dict['time'] = "{} - {}".format(start_time, end_time)
            pdc_dict['booked_count'] = '0'
            pdc_dict['added_by'] = added_by_name

            pdc_dict['published_date'] = published_date
            if str(pdc_dict['count']) != '0':
                provisional_demands_list.append(pdc_dict)
                no_of_provisional_demands += 1
    return render_response(request, 'provisional_demand.html', {'pdStr': pdStr, 'boards': boards, 'subjects': subjects,
                            'no_of_demands': no_of_provisional_demands, 'provisional_demands': provisional_demands_list})


@login_required
def get_provisional_center_time(request):
    board = request.GET.get('board', '')
    subject = request.GET.get('subject', '')
    grade = request.GET.get('grade', '')

    pd_course = (Course.objects.filter(Q(board_name=board) & Q(subject=subject) & Q(grade=grade)))[0]

    center_name = '{}-{}-{}'.format(board, PROVISIONAL_CENTER, pd_course.id)
    time_range = ""

    pd_center = Center.objects.filter(name=center_name)
    if len(pd_center) > 0:
        pd_center_slot = Demandslot.objects.filter(center_id=pd_center[0].id)
        if len(pd_center_slot) > 0:
            time_range = "{}-{}".format(str(pd_center_slot[0].start_time), str(pd_center_slot[0].end_time))

    return HttpResponse(simplejson.dumps({'time': time_range}), mimetype='application/json')


@login_required
def add_provisional_demand(request):
    board, start_date, subject, grade, no_of_teachers_required = get_primary_info(request)
    start_date_time = start_date.strftime("%Y-%m-%d %H:%M:%S")

    slots_data = json.loads(str(request.POST.get('slots')))
    start_time, end_time = "", ""
    for day, time in slots_data.items():
        start_time, end_time = time.split("-")
        estart_time = start_time[:5]
        start_time = start_time[:2]
        eend_time = end_time[:5]
        end_time = end_time[:2]
        break

    board_language = get_language_from_board(board)
    response = {'message': ''}

    has_offering = False

    is_new_course, provisional_course = get_or_create_course(board, subject, grade)

    user_id = request.user.id
    pc_name = "{}-{}-{}-{}{}{}".format(board, "Provisional", provisional_course.id, start_time, end_time, str(user_id))   # pc --> Provisional Center

    is_new, provisional_center = get_or_create_provisional_center(pc_name, board_language, board, request.user)
    if is_new:
        create_provisional_center_demand_slots(provisional_center.id, slots_data)

    center_id = provisional_center.id

    if not is_new_course:
        has_offering = Offering.objects.filter(course_id=provisional_course.id, center_id=center_id,
                                                  language=board_language).count() > 0

    if has_offering:
        response['message'] = "Similar provisional demand already exists for {} - {}th grade {}".format(board, grade, subject)
    else:
        end_date = Ayfy.objects.filter(board=board).values_list('end_date').order_by("-id")
        if end_date[0][0].month != 12:
            end_date_time = "{}-{}-{} 23:59:59".format(str(start_date.year + 1), end_date[0][0].month, end_date[0][0].day)
        else:
            end_date_time = "{}-{}-{} 23:59:59".format(str(start_date.year), end_date[0][0].month, end_date[0][0].day)

        for i in range(int(no_of_teachers_required)):
            offer = create_provisional_offering(board,provisional_course, center_id, board_language, start_date_time,
                                                end_date_time, request.user)

            response['message'] = "{} provisional demands saved successfully".format(no_of_teachers_required)
        ename = str(request.user)
        user_email = str(request.user.email)
        eid = str(user_id)
        egrade = str(grade)+'th'
        eboard = str(board)
        esubject = str(subject)
        etime = str(estart_time)+" to "+str(eend_time)
        erequired = str(no_of_teachers_required)
        emailsubject = "Provisional demand booked by {0} ({1})".format(ename,eid)    
        ebody = "Dear Mamatha,\n\n("+eid+"), "+ename+" has booked the provisional demand "+etime+" for "+egrade+" "+esubject+" in "+eboard+"\nRequired teacher - "+erequired+"\n\nRegards,\neVidyaloka jupiter team"
        mail = EmailMessage(emailsubject, ebody, to=['mamatha.bv@evidyaloka.org',user_email], from_email=settings.DEFAULT_FROM_EMAIL)
        mail.send()
    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


@login_required
def update_provisional_demand(request):
    provisional_center = request.POST.get('center')
    provisional_demand_id = request.POST.get('id')
    response = {'message': "Updated successfully"}

    provisional_course = Course.objects.filter(id=provisional_demand_id).values()
    provisional_course_object = Course.objects.filter(id=provisional_demand_id)[0]
    if len(provisional_course) < 1:
        response['message'] = "The provisional demand you are trying to update is no longer available. Please contact support."
        return HttpResponse(simplejson.dumps(response), mimetype='application/json')

    provisional_course = provisional_course[0]
    current_board = str(provisional_course['board_name'])
    current_subject = str(provisional_course['subject'])
    current_grade = str(provisional_course['grade'])
    slots_data = json.loads(str(request.POST.get('slot')))

    # Get details from HTTP  Request
    board, start_date, subject, grade, no_of_teachers_required = get_primary_info(request)

    end_date_str = str(request.POST.get('end_date')) + " 23:59:59"
    end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
    end_date_time = end_date.strftime("%Y-%m-%d %H:%M:%S")

    language = get_language_from_board(board)

    provisional_demand_offers = Offering.objects.filter(center_id = provisional_center, course_id=provisional_course['id'],
                                                        status=PROVISIONAL_KEYWORD).order_by("id")

    mapped_offers_count = provisional_demand_offers.count()

    booked_slots = ProvisionalDemandslot.objects.filter(Q(offering_id__in=provisional_demand_offers.values_list('id', flat=True))).values_list('offering_id', flat=True).distinct()

    existing_info = None
    if mapped_offers_count > 0:
        existing_info = provisional_demand_offers.values()[0]

    is_add_or_delete = 0  # 1 for add, -1 for delete
    diff = 0
    if int(no_of_teachers_required) > mapped_offers_count:
        is_add_or_delete = 1
        diff = int(no_of_teachers_required) - mapped_offers_count
    elif int(no_of_teachers_required) < mapped_offers_count:
        is_add_or_delete = -1
        diff = mapped_offers_count - int(no_of_teachers_required)
        if diff < 0:
            diff = 0

    is_new_course = False
    is_new_center = False
    course_data = None
    course_id_for_pc = provisional_course['id']
    existing_unallocated_offers = Offering.objects.filter(center_id=provisional_center, course_id=provisional_course['id'], status=PROVISIONAL_KEYWORD).exclude(
        Q(id__in=booked_slots)).order_by("id").values_list('id')
    existing_unallocated_offers = [each[0] for each in existing_unallocated_offers]
    existing_unallocated_offers.sort()

    if current_board != board or current_subject != str(subject) or current_grade != str(grade):
        # is_new_course, course_data = get_or_create_course(board, str(subject), str(grade))
        # is_new_center, center = get_or_create_provisional_center("{}-{}-{}".format(board, PROVISIONAL_CENTER, course_data.id), language,
        #                                                          board, request.user)
        # course_id_for_pc = course_data.id
        #
        # for each in existing_unallocated_offers:
        #     Offering.objects.filter(id=each).update(course=course_data.id)
        #
        # if is_new_center:
        #     create_provisional_center_demand_slots(center.id, slots_data)
        #
        # for each in existing_unallocated_offers:
        #     Offering.objects.filter(id=each).update(center=center)
        #
        # if provisional_course['id'] != course_data.id:
        #     provisional_course_object = course_data

        ##### DO NOT DELETE THIS COMMENT, REQUIRED IN FUTURE TO ENABLE
        pass

    if existing_info is not None and (str(existing_info['start_date']) != str(start_date) or str(existing_info['end_date']) != str(end_date)):
        start_date_time = start_date.strftime("%Y-%m-%d %H:%M:%S")
        for each in existing_unallocated_offers:
            Offering.objects.filter(id=each).update(start_date=start_date_time, end_date=end_date_time)

    db_center = Center.objects.get(id=provisional_center)
    pc_name = db_center.name
    # if current_board != board:
    #     pc_name = "{}-{}-{}".format(board, PROVISIONAL_CENTER, course_id_for_pc)
    #provisional_center = Center.objects.get(name=pc_name)

    if not is_new_center:
        time_window = str(request.POST.get('time_window'))
        start_time, end_time = time_window.split('-')
        next_start = get_next_hour(start_time)
        next_end = get_next_hour(end_time)
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
            demand_slots = Demandslot.objects.filter(center_id=db_center.id, day=day).order_by("id")
            for idx, each_slot in enumerate(demand_slots):
                if idx == 0:
                    Demandslot.objects.filter(id=each_slot.id).update(start_time=start_time, end_time=end_time)
                else:
                    Demandslot.objects.filter(id=each_slot.id).update(start_time=next_start, end_time=next_end)

    if is_add_or_delete < 0 and len(existing_unallocated_offers) >= diff:
        for i in range (diff):
            Offering.objects.filter(id=existing_unallocated_offers[i]).delete()
    elif is_add_or_delete > 0:
        for i in range(diff):
            offer = create_provisional_offering(board,provisional_course_object, db_center.id, language, start_date,
                                            end_date_time, request.user)

    return HttpResponse(simplejson.dumps(response), mimetype = 'application/json')


@login_required
def delete_provisional_demand(request):
    id_list = request.POST.getlist('id[]')
    boards_list = request.POST.getlist('boards[]')
    grades_list = request.POST.getlist('grades[]')
    subjects_list = request.POST.getlist('subjects[]')
    required_list = request.POST.getlist('required[]')
    times_list = request.POST.getlist('times[]')
    user_id = str(request.user.id)
    username = str(request.user)
    user_email = str(request.user.email)
    response = {'message': 'Selected provisional demand(s) and all linked offerings are deleted successfully'}

    # Get offerings which are not provisionally booked (saved in ProvisionalDemandSlot)
    provisional_demand_slots = ProvisionalDemandslot.objects.filter().values_list('offering_id', flat=True).distinct()

    # Delete only which are provisionally not booked
    try:
        for i in range(len(id_list)):
            provisional_demand_offers = Offering.objects.filter(center_id=id_list[i], status=PROVISIONAL_KEYWORD).exclude(
                                            Q(id__in=provisional_demand_slots)).order_by("id")
            for offer in provisional_demand_offers:
                Offering.objects.filter(id=offer.id).delete()
            emailsubject = "Provisional demand deleted by {0} ({1})".format(username,user_id)    
            ebody = "Dear Mamatha,\n\n("+user_id+"), "+username+" has deleted the provisional demand "+times_list[i]+" for "+grades_list[i]+"th "+subjects_list[i]+" in "+boards_list[i]+"\nRequired teacher - "+required_list[i]+"\n\nRegards,\neVidyaloka jupiter team"
            mail = EmailMessage(emailsubject, ebody, to=["mamatha.bv@evidyaloka.org",user_email], from_email=settings.DEFAULT_FROM_EMAIL)
            mail.send()
    except Exception as e:
        response['message'] = "Demands which you are trying to delete are not found. Please contact support."

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


@login_required
def drop_provisional_demand_slot(request):
    offering_id = request.POST.get('offering_id', 0)
    user_id = request.POST.get('user_id', 0)
    reason = request.POST.get('reason', '')
    user_id =User.objects.get(id=user_id)
    offering = Offering.objects.get(id=offering_id)
    
    response = {'status': 0, 'message': 'Provisional booking is released successfully'}
    try:
        pds = ProvisionalDemandslot.objects.filter(user_id=user_id, offering_id=offering_id).order_by("id")
        for each in pds:
            each.delete()
            args = {'volunteer_name': user_id.first_name+" "+ user_id.last_name ,'center':offering.center.name,'offering':offering.course.grade+" "+offering.course.subject,'reason':reason}
     
            subject = "Provisional Demand slots realesed"
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [user_id.email]
            cc = [offering.created_by.email,"mamatha.bv@evidyaloka.org"]
            message = get_template('mail/_provisioal_demand/pd_slots_releasing.txt').render(Context(args))
        
        mail = EmailMessage(subject, message, to=to, from_email=from_email,cc=cc)
        
        mail.content_subtype = 'html'
        mail.send()
    except Exception as exp:
        response['status'] = -1
        response['message'] = "An error occurred : {} ".format(str(exp))

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


@csrf_exempt
def get_country_state_city(request):
    country = request.GET.get('country', '')
    state = str(request.GET.get('state', ''))

    response = {'data': []}

    if state != '' and country != '':
        db_data = CountryStateCities.objects.filter(Q(custom_country_id=country) & Q(custom_state_id=state)).values(
            'custom_city_id', 'city_name').distinct().order_by('city_name')
    elif state == '' and country != '':
        db_data = CountryStateCities.objects.filter(Q(custom_country_id=country)).values('custom_state_id',
                                                      'state_name').distinct().order_by('state_name')
    else:
        db_data = CountryStateCities.objects.all().values('custom_country_id', 'country_name').distinct().order_by(
            'country_name')

    for each in db_data:
        response['data'].append(each)

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')



def check_for_overlap(source_start, source_end, target_start, target_end):
    # return (target_end < source_start or source_end < target_start)
    return (source_start <= target_end and source_end >= target_start)


@login_required
@csrf_exempt
def bulk_enroll_student(request):
    message = request.GET.get('message','')
    #centers = Center.objects.all()
    center_id = request.GET.get('center_id','')
    save_flag = request.GET.get('save_flag','')
    center_details = Center.objects.get(id = center_id)
    file_name = (center_details.name + "_bulk_enroll_student.csv").replace(' ', '_')
    return render_response(request, "bulkenrollStudent.html",{'centers':center_id,'file_name' : file_name,'message':message,'save_flag':save_flag})


@login_required
@csrf_exempt
def bulk_enroll_student_multi_center(request):
    message = request.GET.get('message','')
    save_flag = request.GET.get('save_flag','')
    file_name = "Multi_center_bulk_enroll_student.csv"
    return render_response(request, "bulkenrollStudentMultiCenter.html",{'file_name' : file_name,'message':message,'save_flag':save_flag})


def testing_data(request):
    student_data_list = request.POST.get('student_data_list').split (",")
    student_center_id = request.POST.get('center_id', '')
    response ={}
    student_enroll_data = []
    for i in range(0, len(student_data_list[16:]), 15):
        student_enroll_data.append(student_data_list[16:][i:i + 15])
    student_enroll_data_header = student_data_list[:15]
    # student_enroll_data = student_enroll_data[1:]
    message = []
    if len(student_enroll_data_header) <= 11:
        response['message'] = "No of columns doesnot match"
    else:
        count= 1
        for student_data in student_enroll_data:
            try:
                existing_data = Student.objects.values().filter(Q(name = student_data[0]) & Q(gender = student_data[2]) & Q(grade = student_data[3]) & Q(center_id = student_center_id))
            except:
                existing_data = ""
            if existing_data:
                message.append("Sl No " + str(count) + " : Student data already exists")
            else:
                if student_data[0] == "":
                    message.append("Sl No " + str(count) +" : Missing Name information")
                # if student_data[1] == "":
                #     message.append("Sl No " + str(count) +" : Missing Date of Birth information")
                if student_data[1] != "":
                    if student_data[1][4] != "-" or student_data[1][7] != "-":
                        message.append("Sl No " + str(count) +" : Wrong format for Date of Birth(Expected: YYYY-MM-DD)")
                # if student_data[2] == "":
                #     message.append("Sl No " + str(count) +" : Missing Center information")
                if student_data[2] == "":
                    message.append("Sl No " + str(count) +" : Missing DOB information")
                if student_data[3] == "":
                    message.append("Sl No " + str(count) +" : Missing Grade information")

            count += 1
    if len(message) > 0:
        response['message'] = message
    else:
        message.append("Data is ready to upload")
        response['message'] = message

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


def testing_data_multi_center(request):
    student_data_list = request.POST.get('student_data_list').split (",")
    student_center_id = request.POST.get('center_id', '')
    response ={}
    student_enroll_data = []
    for i in range(0, len(student_data_list[17:]), 16):
        student_enroll_data.append(student_data_list[17:][i:i + 16])
    student_enroll_data_header = student_data_list[:16]
    # student_enroll_data = student_enroll_data[1:]
    message = []
    if len(student_enroll_data_header) <= 12:
        response['message'] = "No of columns doesnot match"
    else:
        count= 1
        for student_data in student_enroll_data:
            try:
                existing_data = Student.objects.values().filter(Q(name = student_data[0]) & Q(gender = student_data[2]) & Q(grade = student_data[3]) & Q(center_id = student_data[16]))
            except:
                existing_data = ""
            if existing_data:
                message.append("Sl No " + str(count) + " : Student data already exists")
            else:
                if student_data[0] == "":
                    message.append("Sl No " + str(count) +" : Missing Name information")
                # if student_data[1] == "":
                #     message.append("Sl No " + str(count) +" : Missing Date of Birth information")
                if student_data[1] != "":
                    if student_data[1][4] != "-" or student_data[1][7] != "-":
                        message.append("Sl No " + str(count) +" : Wrong format for Date of Birth(Expected: YYYY-MM-DD)")
                # if student_data[2] == "":
                #     message.append("Sl No " + str(count) +" : Missing Center information")
                if student_data[2] == "":
                    message.append("Sl No " + str(count) +" : Missing DOB information")
                if student_data[3] == "":
                    message.append("Sl No " + str(count) +" : Missing Grade information")

            count += 1
    if len(message) > 0:
        response['message'] = message
    else:
        message.append("Data is ready to upload")
        response['message'] = message

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')

@csrf_exempt
def bulk_uplaod_student_enroll(request):
    student_data_list = request.POST.get('student_data_list').split(",")
    center_id = request.POST.get('center_id')
    student_enroll_data = []
    for i in range(0, len(student_data_list[16:]), 15):
        student_enroll_data.append(student_data_list[16:][i:i + 15])
    # student_enroll_data = student_enroll_data[1:]
    createdBy = request.user
    for student_data in student_enroll_data:
        student = Student()
        student.name = student_data[0]
        if student_data[1] == "":
            pass

        else:
            try:
                student.dob = student_data[1] + " 00:00:00"
            except:
                pass
        student.center_id = center_id
        student.gender = student_data[2]
        student.grade = student_data[3]
        student.father_occupation = student_data[4]
        student.mother_occupation = student_data[5]
        student.strengths = student_data[6]
        student.weakness = student_data[7]
        student.phone = student_data[8]
        student.status = "Active"
        student.school_rollno = student_data[9]
        student.observation = student_data[10]
        student.created_by_id = request.user.id
        student.created_on = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        student.save()
        try:
            if student_data[13] and student_data[14]:
                kyc = KycDetails.objects.create(student=student, doc_type=str(student_data[13]), kyc_number=student_data[14], created_by=request.user)
                kyc.save()
        except Exception as e: pass

        try:
            centerObj = Center.objects.get(id=center_id)
        except:
            centerObj = None
        if centerObj and centerObj.digital_school and centerObj.digital_school_partner:
            relationShipType = student_data[12]
            if "mother" in relationShipType:
                relationShipType = "mother"
            elif "father" in relationShipType:
                relationShipType = "father"
            elif "guardian" in relationShipType:
                relationShipType = "guardian"

            createGuardianObjectIfNeeded(createdBy, student, student_data[8], relationShipType, True,
                                         student_data[11],'3')
            enrollment = Student_School_Enrollment.objects.create(
                student=student,
                digital_school=centerObj.digital_school,
                center=centerObj,
                enrollment_status="active",
                enrolled_by=createdBy,
                created_by=createdBy,
                updated_by=createdBy,
                payment_status='free'
            )
            enrollment.save()


    response = {}
    response['message'] = "Successfully uploaded"
    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


@csrf_exempt
def bulk_upload_student_enroll_multi_center(request):
    try: 
        student_data_list = request.POST.get('student_data_list').split(",")
        student_enroll_data = []
        for i in range(0, len(student_data_list[17:]), 16):
            student_enroll_data.append(student_data_list[17:][i:i + 16])

        createdBy = request.user
        for student_data in student_enroll_data:
            if student_data[15] == "":
                pass 
            else:
                student = Student()
                student.name = student_data[0]
                try:
                    center_id = int(re.findall("\d+", student_data[15])[0])
                except:
                    pass
                
                if  student_data[1] !='':
                    student.dob = student_data[1] + " 00:00:00"

                student.center_id = center_id
                student.gender = student_data[2]
                student.grade = student_data[3]
                student.father_occupation = student_data[4]
                student.mother_occupation = student_data[5]
                student.strengths = student_data[6]
                student.weakness = student_data[7]
                student.phone = student_data[8]
                student.status = "Active"
                student.school_rollno = student_data[9]
                student.observation = student_data[10]
                student.created_by_id = request.user.id
                student.created_on = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
                student.save()
                try:
                    if student_data[13] and student_data[14]:
                        kyc = KycDetails.objects.create(student=student, doc_type=str(student_data[13]), kyc_number=student_data[14], created_by=request.user)
                        kyc.save()
                except Exception as e: pass
                centerObj = get_object_or_none(Center, id=center_id)
                if centerObj and centerObj.digital_school and centerObj.digital_school_partner:
                    relationShipType = student_data[12]
                    if "mother" in relationShipType:
                        relationShipType = "mother"
                    elif "father" in relationShipType:
                        relationShipType = "father"
                    elif "guardian" in relationShipType:
                        relationShipType = "guardian"
                    createGuardianObjectIfNeeded(createdBy, student, student_data[8], relationShipType, True,
                                                student_data[11],'3')
                    enrollment = Student_School_Enrollment.objects.create(
                        student=student,
                        digital_school=centerObj.digital_school,
                        center=centerObj,
                        enrollment_status="active",
                        enrolled_by=createdBy,
                        created_by=createdBy,
                        updated_by=createdBy,
                        payment_status='free'
                    )
                    enrollment.save()
    except Exception as e: pass

    response = {}
    response['message'] = "Successfully uploaded"
    return HttpResponse(simplejson.dumps(response), mimetype='application/json')

@csrf_exempt
def add_lfh_scholastics(request):
    user = request.user
    student_id = request.POST.get('student_id', '')
    offering_id = request.POST.get('offering_id', '')
    child_data = json.loads(request.POST.get('child_data'))
    offering_details = Offering.objects.get(id=offering_id)
    course_details = Course.objects.get(id=offering_details.course_id)
    subject = course_details.subject
    LFH_Scholatics.objects.create(
        offering_id=offering_id, student_id=student_id, topic_id=child_data['topics'],
        subject=subject, outcome=child_data['outcome'], is_present=child_data['is_present'],
        record_type=child_data['record_type'], record_date=child_data['accessed_date'],
        added_by = request.user, added_on=datetime.datetime.now()
        )
    return HttpResponse('ok')

@csrf_exempt
def update_scholastic_lfh(request):
    scholastic_lfh_data = json.loads(request.POST.get('scholastic_lfh_data'))
    if scholastic_lfh_data:
        for ent in scholastic_lfh_data:
            lfh_scholastics_data = LFH_Scholatics.objects.get(id=ent['id'])
            lfh_scholastics_data.outcome = ent['outcome']
            lfh_scholastics_data.is_present = ent['is_present']
            lfh_scholastics_data.record_type = ent['record_type']
            lfh_scholastics_data.record_date = ent['record_date']
            lfh_scholastics_data.updated_by = request.user
            lfh_scholastics_data.updated_on = datetime.datetime.now()
            lfh_scholastics_data.save()
        return HttpResponse('Success')
    return HttpResponse('No records to update')


@csrf_exempt
def school_admin_signup(request):
    try:
        resp = {}
        if request.method == 'GET':
            resp = {'message' : 'Invalid request.'}
            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
        elif request.method == 'POST':
            email = request.POST.get('email_id', '')
            phone = request.POST.get('phone_number', '')
            school_id = request.POST.get('school_id', '')
            is_file_data = request.POST.get('is_file_data', '')
            f_name = request.POST.get('first_name', '')
            l_name = request.POST.get('last_name', '')
            name = f_name + ' ' + l_name
            if email and phone and f_name and l_name and school_id:
                ### Checking for Contact Person Already Exist or not
                try:
                    existing_user = User.objects.get(username=email)
                    errormsg = 'User already exist with email ' + email
                    resp = {'message' : errormsg}
                    if is_file_data:
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                    else:
                        errormsg = 'User already exist with email : %s' % email
                        resp = {'message' : errormsg}
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                except User.DoesNotExist:
                    pass
                except User.MultipleObjectsReturned:
                    errormsg = 'User exists already.'
                    resp = {'message' : 'User already exist with email ' + email}
                    if is_file_data:
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                    else:
                        errormsg = 'User already exist with email : %s' % email
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

                ### Creating User and UserProfile
                new_user = User.objects.create_user(email=email, username=email)
                password = User.objects.make_random_password()
                new_user.set_password(password)
                new_user.save()
                user = authenticate(username=email, password=password)
                user.first_name = f_name
                user.last_name = l_name
                user_profile = user.userprofile
                try:
                    user_profile.phone = phone
                    user_profile.organization_complete_status=True
                    # Creating School admin info
                    school_model = School.objects.get(id=school_id)
                    name_of_organization = school_model.name
                    role = Role.objects.get(name='School Admin')
                    partner_model = Partner.objects.create(
                                contactperson=user, name = name, name_of_organization = name_of_organization, phone = phone, email = email, status = 'New',
                                dt_added=datetime.datetime.now(), role_id=role.id, address = ''
                                )
                    partner_model.save()
                    ### Creating Reference Channel Entry
                    try:
                        ref_channel = ReferenceChannel.objects.get(name=name_of_organization)
                        ref_channel.partner = partner_model
                        ref_channel.is_schooladmin = 1
                    except:
                        ref_channel = ReferenceChannel.objects.create(name=name_of_organization, is_schooladmin=1, partner=partner_model)
                    ref_channel.save()

                    ### Updating Users Referencechannel and Saving his Profile
                    user_profile.referencechannel = ref_channel
                    ### Adding Shool Admin Role to the User
                    if role:
                        user_profile.role.add(role)
                        user_profile.pref_roles.add(role)
                    user_profile.save()
                    user.save()
                except Exception as e: pass
                ### Sending Registration Mail to the User by Copying to Organization
                args = {'username': email, 'name': str(name), 'password': password,
                        'name_of_organization': name_of_organization}
                mail = ''
                body = ''
                subject = 'Welcome to eVidyaloka - ' + str(name_of_organization)
                from_email = settings.DEFAULT_FROM_EMAIL
                to = [email]
                body = get_template('school_admin_signup_mail.html').render(Context(args))
                mail = EmailMessage(subject, body, to=to, from_email=from_email)
                mail.content_subtype = 'html'
                mail.send()

                try:
                    role_pref_obj = RolePreference.objects.create(userprofile=user_profile, role=role, role_status='New', role_onboarding_status=0, role_outcome='Recommended', availability=True)
                    school_data = School.objects.only('id', 'name', 'school_code', 'village', 'district_details').get(id=school_id)
                    myschool = MySchool.objects.create(school=school_data, partner_id=partner_model.id,
                                                        status="Verified", added_by=user,
                                                        grades_in_school='',
                                                        teachers_available=0,
                                                        teachers_required=0,
                                                        electricity='true',
                                                        computer='true', projector_or_led='true',
                                                        internet='true')
                    myschoolstatus = MySchoolStatus.objects.create(myschool=myschool,verification_type='Internet and Geo',status=True,added_by=user)#other_info=other_log_info,
                except Exception as e: pass
                db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                                 user=settings.DATABASES['default']['USER'],
                                 passwd=settings.DATABASES['default']['PASSWORD'],
                                 db=settings.DATABASES['default']['NAME'],
                                 charset="utf8",
                                 use_unicode=True)

                dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
                query = "Insert into partner_partner_partnertype (partner_id, partnertype_id) VALUES ('{}', '{}'), ('{}', '{}')".format(partner_model.id, 2, partner_model.id, 5)
                dict_cur.execute(query)
                msg = 'School admin created successfully with email %s' % email
                resp = {'message' : msg}
                if(is_file_data):
                    pass
                else:
                    login(request, user)
                    resp = {'success' : {'message' : "Profile created successfully with email " + email}}
                    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            else:
                resp = {"error" : {"massage" : "Required parameters not sent"}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e: pass
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


@login_required
def school_admin_teachers_signup(request):
    try:
        if request.method == 'POST':
            try:
                f_name = request.POST.get('f_name', '')
                l_name = request.POST.get('l_name', '')
                email = request.POST.get('email', '')
                phone = request.POST.get('phone', '')
                gender = request.POST.get('gender', '')  
                added_by_id = request.user.id 
                is_school_admin = True
                admin_assigned_roles = ["Class Assistant", "Field co-ordinator", "Delivery co-ordinator"]
                roles = Role.objects.filter(name__in=admin_assigned_roles)
                users_count = 0
                schooladmin_id = (Partner.objects.filter(contactperson_id = request.user.id))[0].id
                reference_channel_id = ReferenceChannel.objects.values_list("id",flat= True).filter(partner_id = schooladmin_id)
                users=UserProfile.objects.filter(referencechannel_id=reference_channel_id)
                if users:
                    users_count=users.count()
                if f_name and l_name and email and phone and added_by_id:
                    ### Checking for Contact Person Already Exist or not
                    try:
                        existing_user = User.objects.get(username=email)
                        errormsg = 'User already exist with email ' + email
                        return render(request, 'my_users.html', {'errormsg': errormsg, 'is_school_admin': True, 'my_users' : True,'roles':roles, 'users_count':users_count})
                    except User.DoesNotExist:
                        pass
                    except User.MultipleObjectsReturned:
                        errormsg = 'User already exist with email : %s' % email
                        return render(request, 'my_users.html', {'errormsg': errormsg, 'is_school_admin': True, 'my_users' : True,'roles':roles, 'users_count':users_count})

                    ### Creating User and UserProfile
                    new_user = User.objects.create_user(email=email, username=email)
                    password = User.objects.make_random_password()
                    new_user.set_password(password)
                    new_user.save()

                    user = authenticate(username=email, password=password)
                    user.first_name = f_name
                    user.last_name = l_name
                    user_profile = user.userprofile
                    user_profile.phone = phone
                    user_profile.gender = gender
                    user_profile.profile_completion_status = 1
                    user_profile.pref_medium = request.user.userprofile.pref_medium
                    # Creating School admin info
                    teacher_model = Teachers.objects.create(user=user,first_name= f_name, last_name = l_name, email = email, 
                                        phone = phone, added_by_id = request.user.id, added_by = request.user,
                                        added_on = datetime.datetime.now()
                                        )
                    teacher_model.save()

                    role = Role.objects.get(name='Teacher')
                    if role:
                        user_profile.role.add(role)
                        user_profile.pref_roles.add(role)
                    schooladmin_id = (Partner.objects.filter(contactperson_id = added_by_id))[0].id
                    ref_channel = ReferenceChannel.objects.filter(partner_id=schooladmin_id)
                    user_profile.referencechannel_id = ref_channel[0].id
                    user_profile.profile_complete_status = 'Started'
                    user_profile.save()
                    user.save()

                    role_preference, created = RolePreference.objects.get_or_create(userprofile=user_profile, role=role)
                    if role.name == 'Teacher':
                        role_preference.role_outcome = 'Recommended'
                        role_preference.role_status ='Active'
                        role_preference.role_onboarding_status = 0
                        role_preference.save()
                    steps = role.onboardingstep_set.all()
                    for step in steps:
                        step_status, creat = OnboardingStepStatus.objects.get_or_create(role_preference=role_preference, step=step)

                    onboarding = user_profile.rolepreference_set.filter(role=1)
                    if onboarding:
                        onboarding_id = onboarding[0].id
                        onboard = RolePreference.objects.get(id=int(onboarding_id))

                        onboard = RolePreference.objects.get(id=int(onboarding_id))
                        date_submited = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
                        step = onboard.onboardingstepstatus_set.all().filter(step__stepname='Self Evaluation')[0]
                        step.status = True
                        step.date_completed = date_submited
                        try:
                            step.save()
                        except Exception as e: pass
                    name_of_organization = ref_channel[0].name
                    args = {'username': email, 'name': str(f_name) + ' ' + str(l_name), 'password': password,
                                'name_of_organization': name_of_organization}
                    mail = ''
                    body = ''
                    subject = 'Welcome to eVidyaloka - ' + str(name_of_organization)
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to = [email]
                    body = get_template('teacher_signup_email.html').render(Context(args))
                    mail = EmailMessage(subject, body, to=to, from_email=from_email)
                    mail.content_subtype = 'html'
                    mail.send()
                    successmsg = 'Teacher added successfully for email- %s' % email
                    users=UserProfile.objects.filter(referencechannel_id=reference_channel_id)
                    if users:
                        users_count=users.count()
                    return render(request, 'my_users.html', {'is_school_admin' : is_school_admin, 'successmsg' : successmsg, 'my_users' : True, 'roles' : roles, 'users_count':users_count})
                else:
                    error_msg = 'Please provide all the required details'
                    return render(request, 'my_users.html', {'is_school_admin' : is_school_admin, 'my_users' : True, 'roles':roles, 'users_count':users_count})   
            except Exception as e: pass
        else:
            error_msg = 'Invalid request format. Please check'
            return render(request, 'my_users.html', {'is_school_admin' : True, 'errormsg' : error_msg, 'my_users' : True, 'users_count':users_count})
    except Exception as e: pass

def school_admin_users(request):
    try:
        is_school_admin = True
        my_users = True
        user_id = request.user.id
        schooladmin_id = (Partner.objects.filter(contactperson_id = user_id))[0].id
        reference_channel_id = ReferenceChannel.objects.values_list("id",flat= True).filter(partner_id = schooladmin_id)
        users=UserProfile.objects.filter(referencechannel_id=reference_channel_id)
        if users:
            users_count=users.count()
        else :
            users_count= 0
        admin_assigned_roles = ["Class Assistant", "Field co-ordinator", "Delivery co-ordinator"]
        roles = Role.objects.filter(name__in=admin_assigned_roles)
    except Exception as e: pass
    return render(request, 'my_users.html', {'is_school_admin': is_school_admin, 'my_users' : my_users, 'roles' : roles, 'users_count':users_count})

def update_school(request):
    if request.method == 'POST':
        state = request.POST.get('state', '')
        city_village = request.POST.get('city_village', '')
        district = request.POST.get('district', '')
        pincode = request.POST.get('pincode', '')
        type_of_school = request.POST.get('type_of_school', '')
        no_of_children = request.POST.get('no_of_children', '')
        school_id = request.POST.get('school_id', '')
        type_of_school = type_of_school if type_of_school else 'Co-educational'
        pincode = pincode if pincode else 0
        no_of_children = no_of_children if no_of_children else 0
        if state and district:
            School.objects.filter(id=school_id).update(state=state, village = city_village, district_details = district,
                                                 pincode = pincode, type_of_school = type_of_school, noofchildren = no_of_children)
            Schooladmin_school.objects.filter(school_id=school_id).update(status='Verified')
            userp = request.user.userprofile
            userp.organization_complete_status=True
            userp.save()
            return HttpResponseRedirect('/myevidyaloka')
        else:
            return render_response(request, 'school_onboarding_stage1.html', {'errormsg' : 'Please fill all the details.'})
    else:
        return render_response(request, 'school_onboarding_stage1.html', {'errormsg' : 'Invalid Request'})

def list_schooladmin_schools(request):
    """For listing all Schools added by schooladmin. If the user is a school admin, then returns only schools added by requested user"""
    schooladmin_id = (Partner.objects.filter(contactperson_id = request.user.id))[0].id
    schooladmin_school = MySchool.objects.filter(partner_id=schooladmin_id)
    is_school_admin = True
    schooladmin = Partner.objects.get(contactperson=request.user)
    return render(request,'list_partner_myschools_for_superuser.html',{'partner_schools':schooladmin_school,"is_partner":False,"schooladmin":schooladmin,"is_funding_partner":False, 'is_school_admin' :is_school_admin})


def view_schooladmin_myschool(request,myschool_id=None,tab_name='',error_msg=''):
    ''' Function to view requested School information '''
    if request.method == "GET":
        try:
            if myschool_id:
                usrprof = UserProfile.objects.get(user=request.user)
                uroles = usrprof.role.all()
                rolesrequired = uroles.filter(Q(name='School Admin'))
                rolepreference_outcome = []
                for role in rolesrequired:
                    try:
                        roleprefe = RolePreference.objects.get(userprofile_id=usrprof.id, role_id=role.id)
                        if roleprefe.role_status == 'New' or roleprefe.role_status == 'Active':
                            rolepreference_outcome.append(roleprefe.role_outcome)
                    except RolePreference.DoesNotExist:
                        pass

                parnter_count = Schooladmin.objects.filter(contactperson=request.user).count()
                user_refchanel_partner = False
                if usrprof.referencechannel:
                    if usrprof.referencechannel.partner_id:
                        user_refchanel_partner = True
                if (user_refchanel_partner and (rolesrequired.count() > 0) and ('Recommended' in rolepreference_outcome)) or parnter_count > 0:
                    if parnter_count > 0:
                        partner = Schooladmin.objects.get(contactperson=request.user)
                
                is_pam = False
                
                myschool  = Schooladmin_school.objects.select_related('school_id', 'schooladmin').filter( (Q(schooladmin_id=partner))).distinct().get(id=myschool_id)
                myschoolstatus = Schooladmin_schoolStatus.objects.filter(schooladmin_school=myschool).distinct()
                for msstatus in myschoolstatus:
                    msstatus.other_info = ast.literal_eval(msstatus.other_info)

                log_history = UpdateHistoryLog.objects.filter(referred_table_id=myschool.school_id.id,log_type='1').order_by('-id')
                for log in log_history:
                    log.other_info = ast.literal_eval(log.other_info)
                log_list = []
                for log in log_history:
                     if log.other_info['verification_type'] == 'Connectivity & Geo Verification':
                         log_list.append(log)
                if log_list:
                    log = log_list[0]
                else:
                    log = None
                return render(request,'view_partner_myschool.html',{'myschool':myschool,'myschoolstatus':myschoolstatus,'is_super':request.user.is_superuser,'tab':tab_name,'error_msg':error_msg,'log':log,"is_partner":partner,"partner":partner,"school":1,
                                            "is_school_admin":True,'is_pam':is_pam,   'is_orgUnit':has_role(request.user.userprofile,'OUAdmin')})
        except Exception as e: pass

def report_load(request):
    type_report = request.GET.get("reports",'')
    start_date = request.GET.get("from",'')
    enddate_date = request.GET.get("to",'')
    ay_id = str(request.GET.get("AY_id",''))
    import csv
    if type_report == 'Class_completion_report':
        with open('/var/www/evd/static/reports/kpi_02.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            results = filter(lambda row:  row[15] >= start_date and row[15] <= enddate_date and row[0] == ay_id, reader)
        with open('/var/www/evd/static/reports/kpi_02.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                header = list(row)

    if type_report == 'teacher_report':
        with open('/var/www/evd/static/reports/kpi_04.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            results = filter(lambda row:  row[22] >= start_date and row[22] <= enddate_date and row[0] == ay_id, reader)
        with open('/var/www/evd/static/reports/kpi_04.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                header = list(row)

    if type_report == 'offering_report':
        with open('/var/www/evd/static/reports/kpi_08.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            results = []
            for row in reader:
                try:
                    if row[11] >= start_date and row[11] <= enddate_date and row[0] == ay_id:
                        results.append(row)
                except:
                    pass
        with open('/var/www/evd/static/reports/kpi_08.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                header = list(row)

    if type_report == 'partner_school_report':
        with open('/var/www/evd/static/reports/kpi_09.csv', 'rb') as csvfile:
            header = next(csvfile).strip("\n").split(",")
            reader = csv.reader(csvfile)
            results = filter(lambda row:  row[12] >= start_date and row[12] <= enddate_date , reader)

    filename= type_report+'_'+start_date+'_to_'+enddate_date
    with open(filename+".csv", 'wb') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        for result in results:

            writer.writerow(result)
    data = open(os.path.join(filename+".csv"),'r').read()
    resp = HttpResponse(data, mimetype='application/x-download')
    resp['Content-Disposition'] = 'attachment;filename='+filename+'.csv'
    return resp
            
def reports(request):
    userprofile = request.user.userprofile
    if request.user.is_superuser:
        is_superuser=True
    else:
        is_superuser=False
    if has_pref_role(userprofile, "vol_admin"):
        is_vol_admin=True
    else:
        is_vol_admin=False
    if has_pref_role(userprofile, "vol_co-ordinator"):
        is_vol_coordinator=True
    else:
        is_vol_coordinator=False
    if has_pref_role(userprofile, "Delivery co-ordinator"):
        is_delivery_coordinator = True
    else:
         is_delivery_coordinator = False
    if has_pref_role(userprofile, "Partner Account Manager"):
        is_pam = True
    else:
        is_pam = False
    partner = request.user.partner_set.all()
    if partner:
        partner_types = partner[0].partnertype.values()
        for partnerty in partner_types:
            if partnerty['name'] == 'Organization Unit': 
                is_orgUnit = True    
            else:
                is_orgUnit = False
    else:
        is_orgUnit = False
    return render_response(request, "reports.html",{'is_superuser':is_superuser,'is_vol_admin':is_vol_admin,'is_vol_coordinator':is_vol_coordinator,'is_delivery_coordinator':is_delivery_coordinator,'is_pam':is_pam,'is_orgUnit':is_orgUnit})

def get_videos(request):
    try:
        return_data = {}
        if request.method == 'GET':
            center_id = request.GET.get('center_id', '')
            offer_data = request.GET.get('offer_details')
            topics = request.GET.get('topics', '')
            is_teacher_data = request.GET.get('is_teacher_data', '')
            if center_id and offer_data and topics:
                board_name = ((Center.objects.get(id=center_id)).board)
                
                if is_teacher_data:
                    offer_data = offer_data.split('   ')
                    grade = (offer_data[0])[0]
                    subject = offer_data[1]
                else:
                    offer_data = offer_data.split(',')
                    offer_data_grade = offer_data[0][:3]
                    # grade = offer_data[0][0:(len(offer_data[0]) - 2)]
                    grade = offer_data_grade[0]
                    subject = offer_data[0][4:]
                if topics == 'Select Topic':
                    video_assignments = VideoAssignments.objects.filter(board_name=board_name, grade=grade, subject=subject, status='Approved')
                else:
                    video_assignments = VideoAssignments.objects.filter(board_name=board_name, grade=grade, subject=subject, topic=topics, status='Approved')
                video_url = []
                for assignments in video_assignments:
                    video_url.append(assignments.video_url)
                return_data['video_url'] = video_url 
            else:
                return_data['error_msg'] = 'Please provide offer details, topics and center id.'
            return HttpResponse(simplejson.dumps(return_data),mimetype='application/json')
        else:
            return_data['error_msg'] = "Invalid request. Please check"
            return HttpResponse(simplejson.dumps(return_data),mimetype='application/json')
    except Exception as e:
        pass

def update_video_for_session(request):
    return_data = {}
    _date = request.POST.get('session_date', '')
    session_id = request.POST.get('session_id', '')
    video_url = request.POST.get('video_url', '')
    mode_ = request.POST.get('mode', '')
    return_data['success_msg'] = 'Video url updated successfully for session date = ' + str(_date)
    try:
        Session.objects.filter(id=session_id).update(video_link=video_url, mode=mode_)
    except Exception as e:
        return_data['error_msg'] = 'Internal Error while updating session for date' +  str(_date)
    return HttpResponse(simplejson.dumps(return_data),mimetype='application/json')

def test(request):
    email_id = request.GET.getlist('email') 
    for email_id in email_id:
        user_id =User.objects.get(email=email_id)
        userprofile_id = UserProfile.objects.get(user_id= user_id.id)
        start_time = SelectionDiscussionSlot.objects.get(userp_id = userprofile_id.id).start_time
        mail = ''
        args = {'volunteer_name': user_id.first_name+" "+ user_id.last_name , 'date_time': start_time}
     
        subject = "eVidyaloka - Teacher Selection Discussion Booking Reminder - User id:"+" "+str(user_id.id)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email_id]
        if email_id:
            cc = [email_id]
            message = get_template('mail/_tsd_slot_book/tsd_reminder.txt').render(Context(args))
            mail = EmailMessage(subject, message, to=to, from_email=from_email, cc=cc)
            
        else:
            message = get_template('mail/_tsd_slot_book/tsd_reminder.txt').render(Context(args))
            mail = EmailMessage(subject, message, to=to, from_email=from_email)
           
        mail.content_subtype = 'html'
        mail.send()
    return HttpResponse(simplejson.dumps(email_id), content_type="application/json")

@login_required
def list_schooladmin(request, schooladmin_id = None):
    if request.method == 'GET' and request.user.is_superuser:
        if schooladmin_id:
            try:
                schooladmin = Partner.objects.get(id=schooladmin_id)
                status_choices = [ 'New', 'In Process', 'Approved', 'On Hold', 'Not Approved']
                return render(request,'list_schooladmins.html',{'schooladmins':schooladmin,'view_flag':True,'status_choices':status_choices})
            except Partner.DoesNotExist:
                return HttpResponseRedirect('/v2/school_admins/')
        schooladmin = Partner.objects.filter(role_id=16).order_by('id')
        return render(request,'list_schooladmins.html',{'schooladmins':schooladmin})
    else:
        return HttpResponseRedirect('/myevidyaloka/')

def update_schooladmin_status(request, schooladmin_id):
    if request.method == 'POST' and request.user.is_superuser:
        status = request.POST.get('schooladmin_status')
        if schooladmin_id:
            schooladmin = Partner.objects.get(id=schooladmin_id)
            schooladmin.status = status
            schooladmin.save()
            if schooladmin.status == 'Approved':
                from_email = settings.DEFAULT_FROM_EMAIL
                to = [schooladmin.contactperson.email]
                subject = 'Congratulations! You are a schooladmin at eVidyaloka' 
                mail_args = {'first_name': schooladmin.contactperson.first_name, 'last_name': schooladmin.contactperson.last_name}
                body = get_template('mail/_school_admin/schooladmin_status_update.html').render(Context(mail_args))
                if schooladmin.email:
                    cc = [schooladmin.email]
                    mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
                else:
                    mail = EmailMessage(subject, body, to=to, from_email=from_email)
                mail.content_subtype = 'html'
                mail.send()

            return HttpResponseRedirect('/v2/school_admins/%s/' %schooladmin.id)
        else:
            return HttpResponseRedirect('/v2/school_admins/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


def test(request):
    email_id = request.GET.getlist('email') 
    for email_id in email_id:
        user_id =User.objects.get(email=email_id)
        userprofile_id = UserProfile.objects.get(user_id= user_id.id)
        start_time = SelectionDiscussionSlot.objects.get(userp_id = userprofile_id.id).start_time
        mail = ''
        args = {'volunteer_name': user_id.first_name+" "+ user_id.last_name , 'date_time': start_time}
     
        subject = "eVidyaloka - Teacher Selection Discussion Booking Reminder - User id:"+" "+str(user_id.id)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email_id]
        if email_id:
            cc = [email_id]
            message = get_template('mail/_tsd_slot_book/tsd_reminder.txt').render(Context(args))
            mail = EmailMessage(subject, message, to=to, from_email=from_email, cc=cc)
            
        else:
            message = get_template('mail/_tsd_slot_book/tsd_reminder.txt').render(Context(args))
            mail = EmailMessage(subject, message, to=to, from_email=from_email)
           
        mail.content_subtype = 'html'
        mail.send()
    return HttpResponse(simplejson.dumps(email_id), content_type="application/json")
    


def remove_offering(request):
    offering_id = request.POST.get('offering_id', '')
    offering_id=offering_id.split(":")
    offering_id=offering_id[0]
    conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                           user=settings.DATABASES['default']['USER'],
                           passwd=settings.DATABASES['default']['PASSWORD'],
                           db=settings.DATABASES['default']['NAME'],
                           charset="utf8",
                           use_unicode=True)

    cursor = conn.cursor()

    query = "DELETE from web_offering  WHERE id ='"+str(offering_id)+"'"
    cursor.execute(query)
    conn.commit()
    return HttpResponse(simplejson.dumps({'status': 'Success'}),mimetype='application/json')

# Fetching children stars of the month for center
def get_children_stars_of_month(request):
        center_id = request.GET.get('center_id', '')
        from_date = request.GET.get('from_date', '')
        to_date = request.GET.get('to_date', '')
        student_list ={}
        get_stickers_for_students =[]
        student_ids = Student.objects.values_list('id', flat ='True').filter(center__id = center_id).distinct()

        if student_ids:
                
            students = Recognition.objects.filter(object_id__in = student_ids,content_type = ContentType.objects.get(model='student'), added_on__gte = from_date, added_on__lte = to_date).values('object_id').annotate(
                                        countofreg=Count('object_id')).order_by('-countofreg')
            for stud in students:
                    student = Student.objects.get(id = stud['object_id'])
                    get_stick_count_std = Recognition.objects.filter(object_id=stud['object_id'],
                                                content_type=ContentType.objects.get(model='student')).values(
                                                'sticker__sticker_name', 'sticker__sticker_path').annotate(countofsticker=Count('sticker__sticker_name'))
                    
                    exists = os.path.isfile(str(settings.PROJECT_DIR)+'/'+str(student.photo))
                    photo = student.photo
                    if exists:
                        pass
                    else:
                        photo = ''
                    student_list = {'std_name': student.name, 'std_grade': student.grade, 'std_photo': photo,'get_stick_count_std':get_stick_count_std,'std_gender':student.gender}
                    get_stickers_for_students.append(student_list)

            return_val = {"get_stickers_for_students":get_stickers_for_students}

            return HttpResponse(str(return_val))
def video_tool(request):
    school_admin_data = Partner.objects.filter(contactperson = request.user)
    if request.method == 'GET':
        teaching_software_ids = []
        if school_admin_data.count() == 0:
            return HttpResponseRedirect('/myevidyaloka/')
        teaching_software_id = school_admin_data[0].teaching_software_id
        if teaching_software_id and len(teaching_software_id):
            teaching_software_ids = teaching_software_id.split(',')
        is_school_admin = True
        is_partner_volunteer,is_partner_delivery,is_partner_funding = [False] * 3


        if school_admin_data.filter(Q(role_id = '16')).count() == 0:
            is_school_admin = False
            school_admin_data = Partner.objects.get(contactperson = request.user)
            
            for ptype in school_admin_data.partnertype.all():
                if ptype.id == 1:
                    is_partner_volunteer = True
                elif ptype.id == 2:
                    is_partner_delivery = True
                elif ptype.id == 3:
                    is_partner_funding = True
            
            myschools_count = MySchool.objects.filter(Q(center__funding_partner=school_admin_data.id)|Q(center__delivery_partner=school_admin_data.id)).count()
            mycenters_count = Center.objects.filter(Q(funding_partner_id=school_admin_data.id,status='Active')|Q(orgunit_partner_id=school_admin_data.id,status='Active')|Q(delivery_partner_id=school_admin_data.id,status='Active')).count()
            admin_assigned_roles = ["Class Assistant", "TSD Panel Member", "vol_admin", "vol_co-ordinator", "Field co-ordinator", "Delivery co-ordinator", "support"]

            roles = Role.objects.filter(name__in=admin_assigned_roles)
            users=UserProfile.objects.filter(referencechannel_id=school_admin_data.id)
            if users:
                users_count=users.count()
            else :
                users_count=None

            is_funding_partner = ""
            if school_admin_data:
                try:
                    is_funding_partner = Partner.objects.values("partnertype").filter(contactperson=request.user, partnertype=3)
                except:
                    is_funding_partner = ""
            else:
                is_funding_partner = ""

            return render(request,'video_tool_integration.html',{
                'partner':school_admin_data,'is_partner_volunteer':is_partner_volunteer,'is_partner_delivery':is_partner_delivery,
                'myschools_count':myschools_count, 'mycenters_count':mycenters_count,'roles':roles,'is_partner_funding':is_partner_funding,
                'partner_name':school_admin_data.name_of_organization,'is_partner':school_admin_data,"is_funding_partner":is_funding_partner,
                'is_school_admin' : is_school_admin, 'is_video_tool' : True, "teaching_software_ids" : teaching_software_ids
                })

        return render_response(request, 'video_tool_integration.html', {'is_school_admin' : is_school_admin, 'is_video_tool' : True, "teaching_software_ids" : teaching_software_ids})
    elif request.method == 'POST':
        video_tool_ids = request.POST.getlist('video_tool_ids[]')
        resp = {}
        try:
            if video_tool_ids and len(video_tool_ids) > 0:
                video_tool_ids = ",".join(video_tool_ids)
                school_admin_data.update(teaching_software_id=video_tool_ids)
                resp = {'success' : 'Video tools added successfully.'}
            else:
                resp = {'error' : 'Invalid request.'}
        except Exception as e:
            resp = {'error' : 'Internal error.'}
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@csrf_exempt
def update_offerings_date(request):
    try:
        if request.method == 'POST':
            start_date_offer = request.POST.get('start_date', '')
            end_date_offer = request.POST.get('end_date','')
            offering_id = request.POST.get('offer', '')
            course_name = request.POST.get('course_nm','')
            offering_obj = Offering.objects.get(id=offering_id)
            start_date_offer_dt = dt.datetime.strptime(start_date_offer, "%d-%m-%Y")
            start_date_offer = dt.datetime.strftime(start_date_offer_dt,"%Y-%m-%dT%H:%M:%S")
            end_date_offer_dt = dt.datetime.strptime(end_date_offer, "%d-%m-%Y")
            end_date_offer = dt.datetime.strftime(end_date_offer_dt,"%Y-%m-%dT%H:%M:%S")
            if offering_obj:
                offer_update = Offering.objects.filter(id = offering_id).update(start_date=start_date_offer, end_date=end_date_offer)
                data = "Successfully updated Offering start and end date"
                if course_name:
                    course_name = course_name.split(',')
                    if start_date_offer_dt.day%10 == 1:
                        start_date_offer_dt = str(start_date_offer_dt.strftime("%dst %b, %Y"))
                    elif start_date_offer_dt.day%10 ==2:
                        start_date_offer_dt = str(start_date_offer_dt.strftime("%dnd %b, %Y"))
                    elif start_date_offer_dt.day%10 ==3:
                        start_date_offer_dt = str(start_date_offer_dt.strftime("%drd %b, %Y"))
                    else:
                        start_date_offer_dt = str(start_date_offer_dt.strftime("%dth %b, %Y"))

                    if end_date_offer_dt.day%10 == 1:
                        end_date_offer_dt = str(end_date_offer_dt.strftime("%dst %b, %Y")) 
                    elif end_date_offer_dt.day%10 ==2:
                        end_date_offer_dt = str(end_date_offer_dt.strftime("%dnd %b, %Y"))
                    elif end_date_offer_dt.day%10 ==3:
                        end_date_offer_dt = str(end_date_offer_dt.strftime("%drd %b, %Y"))
                    else:
                        end_date_offer_dt = str(end_date_offer_dt.strftime("%dth %b, %Y"))

                    course_name = str(course_name[0])+", "+ start_date_offer_dt+" to "+end_date_offer_dt                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
            else:
                data = "Offering does not exits."
            return_data = {'msg' : data, 'course_name':course_name}
            return HttpResponse(simplejson.dumps(return_data),mimetype='application/json')
    except Exception as e:
        traceback.print_exc()

def topic_name(request):
    topic_id = request.POST.get('topic_id')
    topic_name = Topic.objects.values_list("title",flat=True).filter(id = topic_id)[0]
    data = {}
    data['topic_name'] = topic_name
    return HttpResponse(simplejson.dumps(data),mimetype='application/json') 


def verify_teacher(request):
    teacher_id = request.POST.get('teacher_id')
    if request.user.is_superuser:
        role = request.POST.get('role')
    try:
        user = User.objects.get(id = teacher_id)
    except:
        user = 0
    is_booked = 0
    try:
        if request.user.is_superuser and has_role(user.userprofile,'Teacher') or has_role(user.userprofile,'Content Developer'):
            is_teacher = 1
        else:
            is_teacher = 0
    except:
        is_teacher = 0
    if is_teacher == 1 and role:
        slots = SelectionDiscussionSlot.objects.filter(userp_id=user.userprofile.id,status ='Booked')
        if slots:
            is_booked = 1
        else:
            is_booked = 0
    data = {}
    data['is_teacher'] = is_teacher
    data['is_booked'] = is_booked
    return HttpResponse(simplejson.dumps(data),mimetype='application/json')


def verify_teacher_csd_tsd(request):
    teacher_id = request.POST.get('teacher_id')
    role = request.POST.get('role')
    user = User.objects.get(id = teacher_id)
    is_booked = is_content_developer = is_teacher = 0
    try:
        if role == 'Teacher' and has_role(user.userprofile,'Teacher'): is_teacher = 1
        if role == 'Content Developer' and has_role(user.userprofile,'Content Developer'): is_content_developer = 1
    except: pass

    if (is_teacher == 1 or  is_content_developer == 1) and role:
        slots = SelectionDiscussionSlot.objects.filter(userp_id=user.userprofile.id,status ='Booked')
        if slots: is_booked = 1
    data = {}
    data['is_teacher'] = is_teacher
    data['is_content_developer'] = is_content_developer
    data['is_booked'] = is_booked
    data['role'] = role
    return HttpResponse(simplejson.dumps(data),mimetype='application/json')


@csrf_exempt
def update_pledge_details(request):

    post_data = request.POST
    donation_id = post_data.get("donor_id")

    if not donation_id:
        return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}),
                            mimetype="application/json", status=500)

    donation = Donation.objects.filter(id=donation_id)

    if not donation:
        return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}),
                            mimetype="application/json", status=500)

    donation = donation[0]

    donation.name = post_data.get("first_name", "")
    donation.last_name = post_data.get("last_name", "")
    donation.email = post_data.get("email", "")
    donation.phone = post_data.get("phone_no", "")
    donation.pan_number = post_data.get("pan_no", "")
    donation.passport_number = post_data.get("passport_no", "")
    donation.address = post_data.get("address", "")
    donation.country = post_data.get("country", "")
    donation.city = post_data.get("city", "")
    donation.pincode = post_data.get("pin_code", "")
    donation.online_txn_status = post_data.get("status", "started")
    donation.payment_type = post_data.get('payment_mode', "")
    donation.amount = post_data.get('amount', 0)
    donation.donation_time = post_data.get('donation_time', "")

    _file = request.FILES.get('receipt', '')
    try:
        if _file:
            f_path = 'static/uploads/donation_receipts/'
            #testing
            # f_path = '/home/user/my_proj/kanishka/testing_upload/'
            no_of_files = len(os.listdir(f_path))
            no_of_files += 1
            _file_name = _file.name
            _file.name = (os.path.splitext(_file_name)[0] + '_' + str(no_of_files) + os.path.splitext(_file_name)[1]).replace(' ', '_')
            _file_name = _file.name
            valid_extensions = ['.txt', '.doc', '.pdf', '.docx']
            if len(os.path.splitext(_file_name)) > 1 and (os.path.splitext(_file_name))[1] not in valid_extensions:
                resp = {'data' : {'message' : 'Invalid file format.', "status" : 422}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')

            # Moving file to uploads/assignment folder
            f_name = _file_name
            donation.receipt = f_path+f_name
            f = open(f_path + f_name, 'w+')
            f.write(_file.read())
            f.close()
    except Exception as e:
        return HttpResponse(json.dumps({"status": "error", "message": str(e)}), mimetype="application/json", status=500)
    try:
        donation.save()
        return HttpResponse(json.dumps({"status": "success"}), mimetype="application/json", status=200)
    except Exception as e:
        return HttpResponse(json.dumps({"status": "error", "message": str(e)}), mimetype="application/json", status=500)

@csrf_exempt
def delete_pledge_details(request):
    try:
        donation_id = request.POST.get("donor_id")
        donation_id = donation_id.split(",")[:-1]
        print("dele",donation_id)

        if not donation_id:
            return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}),
                                mimetype="application/json", status=500)

        donation = Donation.objects.filter(id__in=donation_id)
        if not donation:
            return HttpResponse(json.dumps({"status": "error", "message": "Donation not found"}),
                                mimetype="application/json", status=500)

        try:
            for donation_data in donation:
                donation = donation_data
                donation.is_deleted = 'yes'
                donation.save()
            return HttpResponse(json.dumps({"status": "success"}),mimetype="application/json", status=200)
        except Exception as e:
            return HttpResponse(json.dumps({"status": "error", "message": str(e)}), mimetype="application/json", status=500)
    except Exception as e:
        traceback.print_exc()

@csrf_exempt
def edit_pledge(request):
    try:
        send_mail = request.POST.get("send_mail", "no")
        pledge_details = {}
        pledge_details["address"] = request.POST.get("address", "")
        pledge_details["address2"] = request.POST.get("address2", "")
        pledge_details["amount"] = int(request.POST.get("amount", "0"))
        pledge_details["channel"] = request.POST.get("channel", "")
        pledge_details["city"] = request.POST.get("city", "")
        pledge_details["country"] = request.POST.get("country", "")
        pledge_details["comments"] = request.POST.get("comments", "")
        pledge_details["donation_time"] = datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30)
        pledge_details["donation_type"] = request.POST.get("donate", "")
        pledge_details["email"] = request.POST.get("email", "")
        pledge_details["name"] = request.POST.get("first_name", "")
        pledge_details["last_name"] = request.POST.get("last_name", "")
        pledge_details["num_centers"] = request.POST.get("num_centers", "")
        pledge_details["num_classrooms"] = request.POST.get("num_classrooms", "")
        pledge_details["num_months"] = request.POST.get("num_months", "")
        pledge_details["num_students"] = request.POST.get("num_children", "")
        pledge_details["num_subjects"] = request.POST.get("num_subjects", "")
        pledge_details["pan_number"] = request.POST.get("pan", "")
        pledge_details["passport_number"] = request.POST.get("passport", "")
        pledge_details["payment_type"] = request.POST.get("payment_type", "")
        pledge_details["phone"] = request.POST.get("phone", "")
        pledge_details["pincode"] = request.POST.get("pincode", "")
        pledge_details["reference"] = request.POST.get("reference", "")
        pledge_details["resident"] = request.POST.get("res_status", "")
        pledge_details["state"] = request.POST.get("state", "")
        pledge_details["honorary_name"] = request.POST.get("honorary_name", "")
        pledge_details["area_of_donation"] = request.POST.get("area_of_donation", "")
        pledge_details["status"] = request.POST.get("status", "")
        pledge_details["upi_transaction_no"] = request.POST.get("transaction_no", "")

        pledge_id = request.POST.get("donation_id", "")
        
        donation = Donation.objects.filter(id=pledge_id)

        if not donation:
            return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}), mimetype="application/json", status=500)

        donation = donation[0]

        if pledge_details['address']:
            donation.address = pledge_details['address']
        if pledge_details['address2']:
            donation.address2 = pledge_details['address2']
        if pledge_details['amount']:
            donation.amount = pledge_details['amount']
        if pledge_details['channel']:
            donation.channel = pledge_details['channel']
        if pledge_details['city']:
            donation.city = pledge_details['city']
        if pledge_details['country']:
            donation.country = pledge_details['country']
        if pledge_details['comments']:
            donation.comments = pledge_details['comments']
        if pledge_details['donation_time']:
            donation.donation_time = pledge_details['donation_time']
        if pledge_details['donation_type']:
            donation.donation_type = pledge_details['donation_type']
        if pledge_details['email']:
            donation.email = pledge_details['email']
        if pledge_details['name']:
            donation.name = pledge_details['name']
        if pledge_details['last_name']:
            donation.last_name = pledge_details['last_name']
        if pledge_details['num_centers']:
            donation.num_centers = pledge_details['num_centers']
        if pledge_details['num_classrooms']:
            donation.num_classrooms = pledge_details['num_classrooms']
        if pledge_details['num_months']:
            donation.num_months = pledge_details['num_months']
        if pledge_details['num_students']:
            donation.num_students = pledge_details['num_students']
        if pledge_details['num_subjects']:
            donation.num_subjects = pledge_details['num_subjects']
        if pledge_details['pan_number']:
            donation.pan_number = pledge_details['pan_number']
        if pledge_details['passport_number']:
            donation.passport_number = pledge_details['passport_number']
        if pledge_details['payment_type']:
            donation.payment_type = pledge_details['payment_type']
        if pledge_details['phone']:
            donation.phone = pledge_details['phone']
        if pledge_details['pincode']:
            donation.pincode = pledge_details['pincode']
        if pledge_details['reference']:
            donation.reference = pledge_details['reference']
        if pledge_details['resident']:
            donation.resident = pledge_details['resident']
        if pledge_details['state']:
            donation.state = pledge_details['state']
        if pledge_details['honorary_name']:
            donation.honorary_name = pledge_details['honorary_name']
        if pledge_details['area_of_donation']:
            donation.area_of_donation = pledge_details['area_of_donation']
        if pledge_details['status']:
            donation.status = pledge_details['status']
        if pledge_details['upi_transaction_no']:
            donation.upi_transaction_no = pledge_details['upi_transaction_no']

        donation.save()        
        return HttpResponse(json.dumps({"status": "success", "donation_id": donation.id, "amount" : donation.amount}), mimetype="application/json",
                            status=200)

    except Exception as e: pass


@csrf_exempt
def donation_give_india(request):
    message = request.POST.get("msg")

    if message:
        message_arr = message.split("|")

        txn_status = message_arr[-2]
        txn_status = 'completed' if txn_status == 'NA' else None

        donation_id = message_arr[1]
        donation = Donation.objects.filter(id=donation_id)

        if donation:
            donation = donation[0]
            donation.online_resp_msg = message

            if txn_status:
                donation.online_txn_status = 'completed'

            user = donation.user

            payment_info = {"name": donation.name, \
                            "last_name": donation.last_name, \
                            "amount": donation.amount, \
                            "payment_type": "online",
                            "txn_status": txn_status,
                            "payment_response": True,
                            "donation_type": donation.donation_type}

            _send_mail([user], '_pledge', payment_info)

            # admins = User.objects.filter(is_superuser = True)
            admins = User.objects.filter(email__in=['venkat.sriraman@evidyaloka.org', 'Nandini.sarkar@evidyaloka.org'])
            _send_mail(admins, '_pledge', payment_info)

            donation.save()

    return render_response(request, "donation_response_give_india.html", {})

def get_session_url(request):
    session = Session.objects.get(pk=int(request.POST.get("session", None)))
    response ={}
    response['session_url'] = session.video_link
    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


@login_required
def student_doubt_detail(request):
    try:

        if request.method != "GET":
            return HttpResponseNotFound('Doubt list page Not Found')
        doubts_list = []
        offeringId = request.GET.get('subjectId')
        centerId = request.GET.get('centerId')
        centerName = request.GET.get('cname')
        if centerName is None:
            centerobj = getCenterDetail(centerId)
            if centerobj:
                centerName = centerobj.name

        subObj = getCourseDetail(offeringId)
        subjectName = ''
        if subObj:
            subjectName = subObj.course.subject

        doubtId = request.GET.get('doubtId')
        doubtObj = None
        doubtList = Doubt_Thread.objects.filter(offering_id=offeringId, id=doubtId).select_related(
            'student', 'topic', 'subtopic','assigned_to')

        if doubtList and len(doubtList) > 0:
            doubtObj = doubtList[0]
        else:
            return HttpResponseNotFound('Doubt Not Found')

        doubtResponse = None
        hasResponded = 0
        doubtCreatedDate = genUtility.getDateTimeinIST(doubtObj.created_on)
        doubtStatusText = "Open"
        attachmentType = "Image"
        doubResponseCreatedDate = None
        doubtModalActionUrl = "/v2/center/doubt/respond"
        urlString = ""
        if doubtObj.status == "2":
            doubtResponseList = Doubt_Thread.objects.filter(offering_id=offeringId, parent_thread=doubtObj,record_type="2").select_related(
            'student', 'topic', 'subtopic','assigned_to')
            doubtStatusText = "Resolved"
            if doubtResponseList and len(doubtResponseList) > 0:
                doubtResponse = doubtResponseList[0]

                hasResponded = 1
                doubtModalActionUrl = "/v2/center/doubt/responseedit"
                doubResponseCreatedDate = genUtility.getDateTimeinIST(doubtResponse.created_on)
                if doubtResponse.resource_type == '5':
                    attachmentType = 'Url'
                    urlString = doubtResponse.resource_url

        backPageUrl = "/v2/center/subject/studentdoubts?subjectId="+offeringId+"&centerId="+centerId

        #get Content details for subtopic
        cArray = []
        if doubtObj.subtopic_id:
            subtopicId = doubtObj.subtopic_id

            contentArray = ContentDetail.objects.filter(subtopic_id=subtopicId,status='approved').order_by('priority').select_related('WorkStreamType')
            for contentObj in contentArray:
                contentDict = {}
                contentDict["id"] = contentObj.id
                contentDict["name"] = contentObj.name
                contentDict["description"] = contentObj.description
                contentDict["url"] = contentObj.url
                contentDict["workstreamType"] = contentObj.workstream_type.code
                cArray.append(contentDict)


        return render(request, 'view_student_doubt_detail.html',
                      {'doubtObj':doubtObj,'doubtResponse': doubtResponse,'hasResponded':hasResponded,"doubtModalActionUrl":doubtModalActionUrl,
                       'is_super': request.user.is_superuser,"centerName":centerName,"subjectName":subjectName,"urlString":urlString,
                       'doubtStatusText': doubtStatusText,"backPageUrl":backPageUrl,"centerId":centerId,
                       "is_partner": False, "school": 1,"attachmentType":attachmentType,"contentList":cArray,
                       'is_pam': False,"doubtCreatedDate":doubtCreatedDate,"doubResponsetCreatedDate":doubResponseCreatedDate,
                        })


    except Exception as e:
        return HttpResponseRedirect('/myevidyaloka/')

@login_required
def student_doubt_respond(request):
    try:

        if request.method != "POST":
            return HttpResponseNotFound('Doubt respond page Not Found')
        doubtId = request.POST.get("doubtId")
        centerId = request.POST.get("centerId")
        text = request.POST.get("responseText")
        urlString = request.POST.get("url")
        attachmentType = request.POST.get("attachmentType")
        doubtId = int(doubtId)

        doubtObj = None
        doubtList = Doubt_Thread.objects.filter(id=doubtId)

        if doubtList and len(doubtList) > 0:
            doubtObj = doubtList[0]
        else:
            return HttpResponseNotFound('Doubt Not Found')
        offeringId = doubtObj.offering_id
        dtDoc = None
        resourceType = '2'
        resourceUrl = ''
        contentTypeId = 2
        if attachmentType == "image":
            cloudFolderName = settings.TEACHER_DOUBT_RESPONSE_STORAGE_FOLDER
            dtDoc = docUploadService.upload_user_document_s3(request, "teacher", None, cloudFolderName,None,"obj")
            resourceUrl = dtDoc.url

        elif urlString and len(urlString) > 10:
            resourceType = '5'
            resourceUrl = urlString
            contentTypeId = 4
        else:
            return HttpResponseNotFound('Attachment type Not Found')


        if doubtObj.status == "1":
            # curDateTime = genUtility.getCurrentTime()
            dtObject = Doubt_Thread.objects.create(
                student_id=doubtObj.student_id,
                session_id=doubtObj.session_id,
                offering_id=offeringId,
                topic_id=doubtObj.topic_id,
                subtopic_id=doubtObj.subtopic_id,
                parent_thread=doubtObj,
                resource_url=resourceUrl,
                resource_doc=dtDoc,
                status='3',
                text=text,
                record_type='2',
                content_type_id=contentTypeId,
                resource_type=resourceType,
                created_by_id=settings.SYSTEM_USER_ID_AUTH,
                updated_by_id=settings.SYSTEM_USER_ID_AUTH,
                assigned_to=request.user,
                #created_on=curDateTime,
            )
            doubtObj.status = '2'
            dtObject.save()
            doubtObj.save()

            studentRec = doubtObj.student
            offeringRec = doubtObj.offering
            courseRec = offeringRec.course
            courseName = courseRec.subject
            schoolName = ""
            dsmRec = None
            dspRec = None
            dateTimeIst = genUtility.getCurrentDateTimeinIST()
            createdDateStr = genUtility.getDbDateStringFromDate(dateTimeIst)
            if offeringRec:
                centerRec = offeringRec.center
                schoolName = centerRec.name
                dsmRec = centerRec.delivery_coordinator


            guardianobj = genUtility.getGuardianForStudent(studentRec.id)
            studentApp.sendRespondDoubtNotifications(studentRec,doubtObj,dtObject,dsmRec,dspRec,courseName,schoolName,createdDateStr)
            notificationModule.sendDoubtRespondedNotificationToStudent(guardianobj,studentRec,courseName,doubtObj)

        redirectPageUrl = "/v2/center/doubt/detail?doubtId=" + str(doubtId) + "&subjectId=" + str(offeringId) + "&centerId=" + str(centerId)
        return HttpResponseRedirect(redirectPageUrl)

    except Exception as e:
        traceback.print_exc()
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def student_edit_doubt_respond(request):
    try:

        if request.method != "POST":
            return HttpResponseNotFound('Doubt edit page Not Found')
        doubtId = request.POST.get("doubtId")
        doubtResponseId = request.POST.get("doubtResponseId")
        centerId = request.POST.get("centerId")
        text = request.POST.get("responseText")
        urlString = request.POST.get("url")
        attachmentType = request.POST.get("attachmentType")
        doubtId = int(doubtId)

        doubtRespObj = None
        doubtList = Doubt_Thread.objects.filter(id=doubtResponseId)

        if doubtList and len(doubtList) > 0:
            doubtRespObj = doubtList[0]
        else:
            return HttpResponseNotFound('Doubt Not Found')
        offeringId = doubtRespObj.offering_id
        dtDoc = None
        resourceType = '2'
        resourceUrl = None
        contentTypeId = 2
        if attachmentType == "image":
            cloudFolderName = settings.TEACHER_DOUBT_RESPONSE_STORAGE_FOLDER
            dtDoc = docUploadService.upload_user_document_s3(request, "teacher", None, cloudFolderName,None,"obj")
            resourceUrl = dtDoc.url

        elif urlString and len(urlString) > 10:
            resourceType = '5'
            resourceUrl = urlString
            contentTypeId = 4
        
        if doubtRespObj.status == "3":
            if dtDoc or resourceUrl:
                if resourceUrl != doubtRespObj.resource_url:
                    doubtRespObj.resource_url = resourceUrl
                    doubtRespObj.resource_doc = dtDoc
                    doubtRespObj.content_type_id = contentTypeId
                    doubtRespObj.resource_type = resourceType

            if text and text != doubtRespObj.text:
                doubtRespObj.text = text

            doubtRespObj.save()


        redirectPageUrl = "/v2/center/doubt/detail?doubtId=" + str(doubtId) + "&subjectId=" + str(offeringId) + "&centerId=" + str(centerId)
        return HttpResponseRedirect(redirectPageUrl)

    except Exception as e:
        traceback.print_exc()
        return HttpResponseRedirect('/myevidyaloka/')

def getCourseDetail(offeringId):
    try:
        offObj = Offering.objects.get(id=offeringId)
        return offObj
    except Exception as e:
        return None

def getCenterDetail(centerId):
    try:
        center = Center.objects.get(id=centerId)
        return center
    except Exception as e:
        return None

def getUserAuthorisedDataRestriction(user,centerObj):
    if user.is_superuser is True:
        return None
    if centerObj.delivery_coordinator_id == user.id:
        return None
    return user


@login_required
def student_doubt_list(request):
    try:
        if request.method != "GET":
            return HttpResponseNotFound('Doubt list page Not Found')
        doubts_list = []
        offeringId = request.GET.get('subjectId')
        centerId = request.GET.get('centerId')
        centerName = request.GET.get('cname')
        centerobj = getCenterDetail(centerId)
        if centerName is None:
            centerName = centerobj.name

        subObj = getCourseDetail(offeringId)
        subjectName = ''
        if subObj:
            subjectName = subObj.course.subject

        assignedToUser =  getUserAuthorisedDataRestriction(request.user,centerobj)

        if assignedToUser:
            doubtList = Doubt_Thread.objects.filter(offering_id=offeringId, record_type="1",assigned_to_id=assignedToUser.id).select_related(
                'student', 'topic', 'subtopic', 'assigned_to')
        else:
            doubtList = Doubt_Thread.objects.filter(offering_id=offeringId, record_type="1").select_related(
                'student', 'topic', 'subtopic', 'assigned_to')

        for data in doubtList:
            dtStausStr = "Resolved"
            if data.status == "1":
                dtStausStr = "Open"

            teacherName = "Not Assigned"
            if data.assigned_to and data.assigned_to_id >= 0:
                teacherName = data.assigned_to.first_name + " " + data.assigned_to.last_name

            doubtCreatedDate = genUtility.getDateTimeinIST(data.created_on)

            doubtData = {
                "id": data.id,
                "offeringId": offeringId,
                "centerId": centerId,
                "student": data.student,
                "resourceUrl": data.resource_url,
                "topic": data.topic,
                "subtopic": data.subtopic,
                "status": dtStausStr,
                "created_on": doubtCreatedDate,
                "teacherName": teacherName,
                "doubt":data
            }
            doubts_list.append(doubtData)

        return render(request, 'list_school_student_doubts.html',
                      {'doubtList': doubts_list, 'partner_schools': [],"is_partner": False,
                       "is_funding_partner": False, "is_school_admin": False, "isExternal": False,"subjectName":subjectName,"centerName":centerName})

        #return render_response(request, 'list_school_student_doubts.html', {"doubtList": doubts_list})

    except Exception as e:
        return HttpResponseRedirect('/myevidyaloka/')


class TopicDetailsView(View):
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            offeringId = self.request.GET.get('offering_id', None)
            centerId = self.request.GET.get('center_id', None)
            ayfyId = self.request.GET.get('ayfy_id', None)
            backTopicId = self.request.GET.get('topic_id', None)
            userType = self.request.GET.get('user_type', None)

            try:
                offeringObj = Offering.objects.get(id=offeringId)
                courseObj = offeringObj.course
            except:
                return HttpResponseNotFound("Offering and Course Not found")

            try:
                centerObj = Center.objects.get(id=centerId)
            except:
                return HttpResponseNotFound("Center Not found")

            queryRec = ~Q(status='Inactive') & Q(topic__course_id=courseObj) & ~Q(topic__status="Inactive")
            subTopicArray = SubTopics.objects.filter(queryRec).order_by('topic__priority').select_related('topic')

            viewStatusDictionary = {}
            if subTopicArray and len(subTopicArray) > 0:
                viewStatusRecs = FLTeacher_Content_View_Status.objects.filter(offering=offeringObj, user=request.user,subtopic__in=subTopicArray)
                for eachRec in viewStatusRecs:
                    if eachRec.subtopic_id:
                        viewStatusDictionary[eachRec.subtopic_id] = eachRec.number_of_times_viewed

            topicIdPriorityArr = []; topicData = {}
            for i in range(len(subTopicArray)):
                subtopicRec = subTopicArray[i]
                topicRec = subtopicRec.topic
                dataRec = topicData.get(topicRec.id)
                if dataRec is None:
                    dataRec = {"id": topicRec.id, "name": topicRec.title, "subtopics": []}
                    topicData[topicRec.id] = dataRec
                    topicIdPriorityArr.append(topicRec.id)

                subtopicsArr = dataRec.get("subtopics")
                hasViewed = 0
                viewCount = viewStatusDictionary.get(subtopicRec.id)
                if viewCount:
                    hasViewed = 1

                subtopicData = {"id": subtopicRec.id, "name": subtopicRec.name, "hasViewed": hasViewed, "viewCount":viewCount,"type":subtopicRec.type}
                subtopicsArr.append(subtopicData)

            finalTopicArr = []
            for j in range(len(topicIdPriorityArr)):
                topicId = topicIdPriorityArr[j]
                tDataRec = topicData.get(topicId)
                if tDataRec:
                    finalTopicArr.append(tDataRec)

            context = {
                'offeringId': offeringId,
                'subject': courseObj.subject,
                'grade': courseObj.grade,
                'board': courseObj.board_name,
                'centerName': centerObj.name,
                'centerId': centerId,
                'ayId': ayfyId,
                'btopicId':backTopicId,
                'userType': userType,
                "topics": finalTopicArr,
            }
            enrolledStudents = offeringObj.enrolled_students.all()
            print(enrolledStudents)

            slist = []
            for s in enrolledStudents:
                slist.append({"id": s.id, "name":s.name})
                
            context['enrolledStudents'] = slist            
            context['is_sampoorna']=True

            if centerObj.digital_school:context['is_digital']=True
            else:context['is_digital']=False
            today = datetime.datetime.now()
            min_dt = datetime.datetime.combine(today, today.time().min)
            max_dt = datetime.datetime.combine(today, today.time().max)
            if FLTeacher_Content_View_Status.objects.filter(offering=offeringObj, user=self.request.user, created_on__range=(min_dt, max_dt)): context['is_update']=True
            else: context['is_update']=False

            return render_response(self.request, 'flm_topic_details.html', context)
        except Exception as e:
            return HttpResponseNotFound("Page not found " + e.message)
           
class SubTopicDetailsView(View):
    ''''GET: rtc player'''
    def getChildRecord(self,contentId):
        try:
            url = "https://api.dev.diksha.gov.in/api/content/v1/read/"+contentId
            authDict = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBOGt5dGptMDdXN2tJOGxNY0c3Unljc3I2b1Q2NWhoViJ9.OMhRtUiochad7pMiozTVY9lOUC9kG3Us7NnA-lezVoc"}

            url = str(url)
            response = requests.get(url,headers=authDict)
            respDict = response.json()
            responseCode = respDict.get("responseCode")
            contentList = []

            if responseCode == "OK":
                result = respDict.get("result")
                contentObj = result.get("content")
                if contentObj:
                    name = contentObj.get("name")
                    mimeType = contentObj.get("mimeType")
                    artifactUrl = contentObj.get("artifactUrl")
                    if (mimeType == "video/mp4" or mimeType == "application/pdf") and artifactUrl:
                        mimtype = "worksheet"
                        if mimeType == "video/mp4":
                            mimtype = "video"

                        ctObj = {
                            "id":contentId,
                            "name":name,
                            "url":artifactUrl,
                            "mimeType":mimtype

                        }
                        contentList.append(ctObj)


            #print("contentList",contentList)
            return contentList
        except Exception as e:
            print("getChildRecord ",e)
            traceback.print_exc()
            return None

    def getChildNodeDetails(self,leafNodes):
        try:
            childList = []
            for contentId in leafNodes:
                #print("contentId",contentId)
                newList = self.getChildRecord(contentId)
                if newList and len(newList) > 0:
                    childList.extend(newList)
            #print("childList",childList)
            return childList
        except Exception as e:
            print("getChildNodeDetails ",e)
            traceback.print_exc()
            return None

    def getChildRecord(self, contentId):
        try:
            url = "https://api.dev.diksha.gov.in/api/content/v1/read/" + contentId
            authDict = {
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBOGt5dGptMDdXN2tJOGxNY0c3Unljc3I2b1Q2NWhoViJ9.OMhRtUiochad7pMiozTVY9lOUC9kG3Us7NnA-lezVoc"}

            url = str(url)
            response = requests.get(url, headers=authDict)
            respDict = response.json()
            responseCode = respDict.get("responseCode")
            contentList = []

            if responseCode == "OK":
                result = respDict.get("result")
                contentObj = result.get("content")
                if contentObj:
                    name = contentObj.get("name")
                    mimeType = contentObj.get("mimeType")
                    artifactUrl = contentObj.get("artifactUrl")
                    if (mimeType == "video/mp4" or mimeType == "application/pdf") and artifactUrl:
                        mimtype = "worksheet"
                        if mimeType == "video/mp4":
                            mimtype = "video"

                        ctObj = {
                            "id": contentId,
                            "name": name,
                            "url": artifactUrl,
                            "mimeType": mimtype

                        }
                        contentList.append(ctObj)
            return contentList
        except Exception as e:
            traceback.print_exc()
            return None

    def getChildNodeDetails(self, leafNodes):
        try:
            childList = []
            for contentId in leafNodes:
                newList = self.getChildRecord(contentId)
                if newList and len(newList) > 0:
                    childList.extend(newList)
            return childList
        except Exception as e:
            traceback.print_exc()
            return None

    def getContentFromThirdParty(self):
        try:
            url = "https://api.dev.diksha.gov.in/api/content/v1/search"
            payloadData = {
                "request": {

                    "filters": {
                        "primaryCategory": [
                            "Digital Textbook"
                        ],
                        "se_boards": [
                            "CBSE"
                        ],
                        "se_mediums": [
                            "English"
                        ],
                        "se_gradeLevels": [
                            "Class 7"
                        ]
                    },
                    "limit": 1000,
                    "fields": [
                        "string",
                        "name",
                        "contentType",
                        "leafNodes"

                    ]
                }
            }


            authDict = {
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJBOGt5dGptMDdXN2tJOGxNY0c3Unljc3I2b1Q2NWhoViJ9.OMhRtUiochad7pMiozTVY9lOUC9kG3Us7NnA-lezVoc"}
            response = requests.post(url, json=payloadData, headers=authDict)
            respDict = response.json()
            responseCode = respDict.get("responseCode")
            contentList = []
            videoList = []
            if responseCode == "OK":
                result = respDict.get("result")
                contentObjs = result.get("content")
                for each in contentObjs:
                    eachId = each.get("identifier")
                    contentType = each.get("contentType")


                    leafNodes = each.get("leafNodes")
                    if leafNodes and len(leafNodes) > 0:
                        pass
                    tlist = self.getChildNodeDetails(leafNodes)
                    if tlist and len(tlist) > 0:
                        for newObj in tlist:
                            cType = newObj.get("mimeType")
                            eachDict = {
                                "id": 3788,
                                "did": newObj.get("id"),
                                "title": newObj.get("name"),
                                "contentType": newObj.get("mimeType"),
                                "url": newObj.get("url"),
                                "author": "Diksha",
                                "duration": 960,
                                "isPrimary": True,
                                "contentHost": "s3",
                                "description": ''

                            }
                            if cType != "video":
                                contentList.append(eachDict)
                            else:
                                videoList.append(eachDict)



                    else:
                        eachDict = {
                            "id": 3788,
                            "did": eachId,
                            "title": each.get("name"),
                            "contentType": contentType,
                            "objectType": each.get("objectType"),
                            "url": "https://dev.diksha.gov.in/play/collection/" + eachId + "?contentType=" + contentType
                        }

                        contentList.append(eachDict)


                return (contentList, videoList)
            else:
                return ([], [])


        except Exception as e:
            traceback.print_exc()
            return (None, None)



    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            offeringId = self.request.GET.get('offering_id', None)
            centerId = self.request.GET.get('center_id', None)
            ayfyId = self.request.GET.get('ayfy_id', None)
            subtopicId = self.request.GET.get('subtopic_id', None)
            topicId = self.request.GET.get('topic_id', None)

            try:
                offeringObj = Offering.objects.get(id=offeringId)
                courseObj = offeringObj.course
            except:
                return HttpResponseNotFound("Offering and Course Not found")

            try:
                centerObj = Center.objects.get(id=centerId)
            except:
                return HttpResponseNotFound("Center Not found")

            try:
                subtopicObj = SubTopics.objects.get(id=subtopicId)
                topicObj = subtopicObj.topic
            except:
                return HttpResponseNotFound("SubTopics Not found")

            contentRecords = ContentDetail.objects.filter(status="approved", subtopic=subtopicObj).select_related(
                'workstream_type', 'content_type', 'url_host').order_by('priority')


            contentDetailData = {
                'subtopic_id': subtopicId,
                'subtopic_name': subtopicObj.name,
                'offeringId': offeringId,
                'subject': courseObj.subject,
                'grade': courseObj.grade,
                'board': courseObj.board_name,
                'centerName': centerObj.name,
                'centerId': centerObj.id,
                'ayId': ayfyId,
                'topicId':topicId
            }
            for i in range(len(contentRecords)):
                contentRec = contentRecords[i]
                workStreamType = contentRec.workstream_type
                contentTypeRec = contentRec.content_type
                contentHostRec = contentRec.url_host

                if not contentTypeRec or not contentHostRec or not workStreamType: continue
                logService.logInfo("workStreamType code", workStreamType.code)
                dataRecArr = contentDetailData.get(workStreamType.code)
                if dataRecArr is None:
                    dataRecArr = []
                    contentDetailData[workStreamType.code] = dataRecArr

                contentDict = {"id": contentRec.id,
                               "title": contentRec.name,
                               "description": contentRec.description,
                               "author": "eVidyaloka",
                               "duration": contentRec.duration,
                               "url": contentRec.url,
                               "isPrimary": contentRec.is_primary,
                               "contentType": contentTypeRec.code,
                               "contentHost": contentHostRec.code
                               }
                dataRecArr.append(contentDict)

            #get records from third party

            context = contentDetailData
            doubts = list(Doubt_Thread.objects.values('id', 'student_id', 'student__name', 'text', 'created_on', 'resource_type', 'resource_url','resource_doc_id', 'content_type_id', 'parent_thread_id', 'created_by_id', 'created_by__first_name', 'created_by__last_name'))
            for doubt in doubts:
                for key,val in doubt.items():
                    if isinstance(val, datetime.datetime):
                        doubt[key] = val.isoformat()
            
            context['doubts'] = doubts

            if centerObj.id == 1220:
                cList, videoList = self.getContentFromThirdParty()

                if cList and len(cList) > 0:
                    context['tpContentList'] = cList
                    context['showTpContent'] = 1
                else:
                    context['showTpContent'] = 0

                if videoList and len(videoList) > 0:
                    evdList = context['video']
                    if evdList and len(evdList) > 0:
                        evdList.extend(videoList)
                        # print("evdList ",evdList)


            offering = Offering.objects.get(id=offeringId)
            
            context['enrolled_student'] = list(offering.enrolled_students.values('id', 'name'))
            context['doubtList'] = Doubt_Thread.objects.filter(offering=offeringObj, subtopic=subtopicObj).exclude(parent_thread__isnull=False)

            return render_response(self.request, 'flm_content_details.html', context)
        except  Exception  as e:
            return HttpResponseNotFound("Page not found " + e.message)

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        requestParams = json.loads(self.request.body)
        try:
            today = datetime.datetime.now()
            min_dt = datetime.datetime.combine(today, today.time().min)
            max_dt = datetime.datetime.combine(today, today.time().max)
            existing_rating = Flm_Content_Rating.objects.filter(reviewer=self.request.user, offering_id=int(requestParams['offeringId']), subtopic_id=int(requestParams['subtopicId']), updated_on__range=(min_dt, max_dt))
            if len(existing_rating) >0:
                rate = existing_rating[0]
                rate.videoRating=float(requestParams['videoRating'])
                rate.worksheetRating=float(requestParams['worksheetRating'])
                rate.comment=str(requestParams['comment'])
                rate.save()
            else:
                rate = Flm_Content_Rating.objects.create(reviewer=self.request.user, offering_id=int(requestParams['offeringId']), subtopic_id=int(requestParams['subtopicId']), videoRating=float(requestParams['videoRating']), worksheetRating=float(requestParams['worksheetRating']), comment=str(requestParams['comment']))
            return genUtility.getSuccessApiResponse(request, {'message': 'Rating saved successfully', 'id':rate.id})
        except Exception as e:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


def student_reach_status(request):
    studentId = request.POST.get('id', None)
    is_reached = request.POST.get('is_reached', None)
    
    if studentId:
        student = Student.objects.get(id=studentId)
    
    if is_reached !='0':
        student.is_reached=True
    else:
        student.is_reached=False
    
    student.save()
    data={'id':student.id,'is_reached':student.is_reached}
    
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

class FlmStudentAttendanceView(View):
    '''
    This view is used to get the student attendance details
    [GET] In=> offeringId, centerId, ayfyId, Out=> student attendance details,
    [POST] In=> studentId, is_present, Out=> student attendance details
    '''

    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        
        try:
            offeringId = self.request.GET.get('offeringId', None)
            centerId = self.request.GET.get('centerId', None)
            ayfyId = self.request.GET.get('ayfyId', None)
            classFromDate = self.request.GET.get('classFromDate', None)
            offeringIdLng = int(offeringId)
            if not all([offeringId, centerId, ayfyId, classFromDate]): # only if no empty list
                return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')

            else:
                classFromDateObj = genUtility.dataFromTimeStampToObj(int(classFromDate))+relativedelta(hours=5, minutes=30)
                offeringObj = Offering.objects.get(id=offeringIdLng)
                userObj = offeringObj.active_teacher
                teacherName = ""
                if userObj and userObj.first_name: 
                    teacherName = userObj.first_name
                    if userObj.last_name: teacherName = teacherName + " " + userObj.last_name
                
                min_dt = datetime.datetime.combine(classFromDateObj, classFromDateObj.time().min)
                max_dt = datetime.datetime.combine(classFromDateObj, classFromDateObj.time().max)
                studentsArray = [{'id':int(student.id), 'name':str(student.name)} for student in offeringObj.enrolled_students.all()]
                previous_students = FLMClassAttendance.objects.filter(offering=offeringObj, updated_on__range=(min_dt, max_dt))
                old_student_ids = list(set([int(student.student.id) for student in previous_students]))

                
                classes = FLMClassTaken.objects.filter(offering=offeringObj, startTime__range=(min_dt, max_dt)).order_by('-id')

                old_subtopics = []; old_comment = ''
                if len(classes)>0:
                    old_comment = classes[0].comments
                    for i in classes[0].subtopic.all():
                        old_subtopics.append({'topicId':i.topic.id, 'subtopicId':i.id})

                dataObject = {
                    "teacherName": teacherName,
                    "students": studentsArray,
                    "old_student_ids":old_student_ids,
                    "old_subtopics":old_subtopics,
                    'old_comment': old_comment
                }
                return genUtility.getSuccessApiResponse(request, dataObject)
        except Exception as e:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        requestParams = json.loads(self.request.body)
        try:
            offeringId = requestParams.get('offeringId', None)
            centerId = requestParams.get('centerId', None)
            ayfyId = requestParams.get('ayfyId', None)
            classStart = requestParams.get('classStart', None)  # timestamp UTC
            classEnd = requestParams.get('classEnd', None)  # timestamp UTC
            students = requestParams.get('students', None) # list of student ids
            comment = requestParams.get('comment', None)
            topicId = requestParams.get('topicId', None)
            subtopicIds = [int(elm) for elm in requestParams.get('subtopicIds', None)]
            
            if offeringId is None or centerId is None or ayfyId is None or classStart is None or classEnd is None or students is None or len(students) <= 0 or topicId is None or subtopicIds is None or len(subtopicIds) <= 0:
                return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')
            offeringObj = get_object_or_none(Offering, id=offeringId)
            TopicObj = get_object_or_none(Topic, id=topicId)
            subtopics = SubTopics.objects.filter(id__in=subtopicIds)
            startDateObj = genUtility.dataFromTimeStampToObj(int(classStart))+relativedelta(hours=10, minutes=30)
            endDateObj = genUtility.dataFromTimeStampToObj(int(classEnd))+relativedelta(hours=10, minutes=30)
            min_dt = datetime.datetime.combine(startDateObj, startDateObj.time().min)
            max_dt = datetime.datetime.combine(startDateObj, startDateObj.time().max)
            
            # remove previous viewed subtopics on same day
            nonRequiredSubtopics = FLTeacher_Content_View_Status.objects.filter(offering=offeringObj, user=self.request.user, created_on__range=(min_dt, max_dt)).exclude(subtopic__in=subtopics)
            if nonRequiredSubtopics: nonRequiredSubtopics.delete()
            
            
            # how many times viewed 
            viewStatusRecs = FLTeacher_Content_View_Status.objects.filter(offering=offeringObj, user=self.request.user, subtopic__in=subtopics)
            if viewStatusRecs and len(viewStatusRecs) > 0:
                for viewObj in viewStatusRecs:
                    viewObj.number_of_times_viewed = viewObj.number_of_times_viewed + 1
                    viewObj.save()
                    
            
            # if more update subtopics viewed
            excludeSubtopicIds = [int(elm) for elm in viewStatusRecs.values_list('subtopic_id', flat=True)]
            newSubtopics = [elem for elem in subtopicIds if elem not in excludeSubtopicIds]
            if len(newSubtopics) > 0:
                for subtopic in SubTopics.objects.filter(id__in=newSubtopics):
                    FLTeacher_Content_View_Status.objects.create(offering=offeringObj, user=self.request.user, subtopic=subtopic, topic=subtopic.topic)

            #update class attendance
            classes = FLMClassTaken.objects.filter(offering=offeringObj, startTime__range=(min_dt, max_dt), startTime=startDateObj, endTime=endDateObj).order_by('-id')
            if classes:
                flmClassObj = classes[0]
                flmClassObj.subtopic.clear()
            else:
                flmClassObj = FLMClassTaken.objects.create(teacher=self.request.user, offering=offeringObj, topic=TopicObj, startTime=startDateObj, endTime = endDateObj, comments=comment, created_by=self.request.user)
            
            flmClassObj.subtopic.add(*subtopics)
            flmClassObj.save()
            
            samedayAtt = FLMClassAttendance.objects.filter(flm_class = flmClassObj, offering=offeringObj, updated_on__range=(min_dt, max_dt)).order_by('-id')
            if samedayAtt: samedayAtt.delete()
            for studRec in students:
                studentId = int(studRec.get("id"))
                isPresent = int(studRec.get("is_present"))
                if isPresent == 1:
                    FLMClassAttendance.objects.create(flm_class = flmClassObj, offering = offeringObj, student_id = studentId, created_by=self.request.user, updated_by=self.request.user, created_on=endDateObj, updated_on=endDateObj)

            dataObject = {
                "message": "Updated the attendance successfully"
            }
            return genUtility.getSuccessApiResponse(request, dataObject)

        except Exception as e:
            traceback.print_exc()
            logService.logException("FlmStudentAttendanceView POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


def check_kyc_number(request):
    """checks kyc number"""
    try:
        # import pdb;pdb.set_trace()
        docType = request.GET.get('docType', None)
        kycDocNum = request.GET.get('kycDocNum', None)
        if docType is None or kycDocNum is None:
            return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')
        else:
            kyc = KycDetails.objects.filter(doc_type=docType, kyc_number=kycDocNum)
            dataObject = {}
            if kyc:
                dataObject["isavialable"] =0
            else:
                dataObject["isavialable"] =1
            return genUtility.getSuccessApiResponse(request, dataObject)
    except Exception as e:
            traceback.print_exc()
            logService.logException("check attendance Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


class BulkPromoteStudents(View):
    '''
    Bulk promote students
    '''
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            
            all_centers = getAllCenters(request)
            centers_list = list(all_centers.values_list('id', flat=True))
            center_str = ""  
            for id in centers_list: 
                center_str +=  ','+str(int(id))

            context={};mydict={}
            cursor = connection.cursor()
            centers_condition = "and web_center.id in (1" + center_str + ")"

            querytxt = '''SELECT web_center.id, web_center.name, web_student.grade, count(web_student.grade) as students,
                 count(case when web_student.promoted_on < (select start_date from web_ayfy where board=web_center.board order by id desc limit 1) then 1 
                            when web_student.promoted_on is null then 1
                        end) as eligble_for_promote
                 FROM web_student join web_center on web_center.id = web_student.center_id where web_center.status="Active" and web_student.grade is not null 
                 and web_student.grade >= 5 and web_student.grade <= 12 and web_student.status = "Active" '''+ centers_condition + ''' group by web_student.center_id, web_student.grade'''
            
            
            cursor.execute(querytxt)
            mylist = cursor.fetchall()

            for a,b,c,d,e in mylist:
                exDict = mydict.get(a)
                if exDict is None:
                    mydict[a] = {}
                    mydict[a]['grades'] = {}
                    
                mydict[a]['name'] = b
                mydict[a]['grades'][c] = {'students':d, 'promote_students':e}

            #logService.logInfo("BulkEnrollStudents query", "completed")
            context['centers'] = mydict
            return render(self.request, 'bulk_promot_students.html', context)
        except Exception as e:
            traceback.print_exc()
            logService.logException("BulkEnrollStudents",e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            centers = requestParams.get('centers', None)
            students =[]
            if centers:
                for center in centers:
                    centerId = center.get('center_id', None)
                    grades = center.get('grades', None)
                    if centerId is None or grades is None:
                        continue
                        # return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')
                    else:
                        promote_grades = []; alumni_grades = []
                        for grade in grades:                           
                            status = grade.split('_')[-1]
                            g = int(grade.split('_')[1])
                            if status == 'P':
                                promote_grades.append(g)
                            elif status == 'A':
                                alumni_grades.append(g)
                        centerObj = Center.objects.get(id=int(centerId))
                        ayfy = Ayfy.objects.filter(board=centerObj.board).order_by('-id')[0]
                        ayStartDate = ayfy.start_date
                        Student.objects.filter(center=centerObj, grade__in=alumni_grades).update(status='Alumni', updated_by=self.request.user, updated_on=datetime.datetime.now())
                        
                        promoteStudents = Student.objects.filter(center=centerObj, grade__in=promote_grades).filter(Q(promoted_on__isnull=True) | Q(promoted_on__lt=ayStartDate))
                        promoteStudents.update(grade =F('grade')+ 1, promoted_by=self.request.user, promoted_on=datetime.datetime.now())
                        
                        for student in promoteStudents:
                            grade = int(student.grade)
                            Promotion_History.objects.create(student=student, ayfy_id=ayfy.pk, from_grade=grade, to_grade=grade+1, center=centerObj, 
                                promoted_by=self.request.user, promoted_on=genUtility.getCurrentTime(), created_by=self.request.user, updated_by=self.request.user)

                        new_grades = [int(grade) + 1 for grade in promote_grades]  + alumni_grades
                        students = students + list(Student.objects.filter(center=centerObj, grade__in=new_grades).values('id','name','center','grade', 'status'))
            dataObject={'status':'success', 'students':students}
            return genUtility.getSuccessApiResponse(request, dataObject)
        except Exception as e:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


class FlmContentStatusView(View):
    """flm content view status
    """
    # @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        requestParams = json.loads(self.request.body)
        try:
            offeringId = requestParams.get('offeringId', None)
            topicId = requestParams.get('topicId', None)
            subtopicId = requestParams.get('subtopicId', None)
            contentDetailsId = requestParams.get('contentDetailsId', None)
            progress = requestParams.get('progress', None)  # timestamp UTC

            if offeringId is None or topicId is None or contentDetailsId is None or subtopicId is None or progress is None:
                return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')

            else:

                contentDetail = ContentDetail.objects.get(id=int(contentDetailsId))
                offering = Offering.objects.get(id=offeringId)
                topic = Topic.objects.get(id=topicId)
                subtopic = SubTopics.objects.get(id=subtopicId)

                contentStatus = FlmContentViewStatus.objects.filter(offering=offering, topic=topic, subtopic=subtopic, content_detail=contentDetail)
                if contentStatus:
                    contentStatus.update(progress=progress)
                else:
                    FlmContentViewStatus.objects.create(offering=offering, topic=topic, subtopic=subtopic, content_detail=contentDetail, progress=progress, user=request.user)

                # classStartLng = long(classStart)
                # classEndLng = long(classEnd)
                # offeringObj = Offering.objects.get(id=offeringId)

                # classStartLng = classStartLng - 60
                # classEndLng = classEndLng + 60

                # startDateObj = genUtility.dataFromTimeStampToObj(classStartLng)
                # endDateObj = genUtility.dataFromTimeStampToObj(classEndLng)

                # classes = FLMClassTaken.objects.filter(startTime__gte=startDateObj, endTime__lte=endDateObj,offering=offeringObj)

                # isClassExistOnSameDay = 0
                # if classes and len(classes) > 0:
                #     isClassExistOnSameDay = 1

                dataObject = {"status": "success",
                                "data": {"message": "Status  updated successfully",},
                                "statusCode": 200
                            }
                return genUtility.getSuccessApiResponse(request, dataObject)
        except Exception as e:
            traceback.print_exc()
            logService.logException("FlmStudentAttendanceView POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

class SqlView(View):
    ''' sql editor for default db in setings
        IN=> str:  sql query 
        OUT=> json: json object
    '''
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        if not self.request.user.groups.filter(name='DBUSER').exists(): return redirect('/v2/vLounge/')   
        try:
            context={}
            return render_response(self.request, 'sql.html', context)
        except Exception as e:
            traceback.print_exc()
            logService.logException("SQL GET Exception error", e.message)
    
    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        if not self.request.user.groups.filter(name='DBUSER').exists(): return redirect('/v2/vLounge/')        
        try:
            requestParams = json.loads(self.request.body)
            query = requestParams.get('query', None)
            
            if query is None or query == '':
                return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

            db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], 
            passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True, compress=True, connect_timeout=30)
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)
            users_cur.execute('SET SESSION TRANSACTION READ ONLY')
            users_cur.execute('SET SESSION MAX_EXECUTION_TIME=30000')
            users_cur.execute(query)
            result = users_cur.fetchall()
            headers=[x[0] for x in users_cur.description] #this will extract row headers
            db.close()
            users_cur.close()
                        
            json_data = json.dumps({'data':result, 'headers':headers}, sort_keys=False, indent=1, separators=(',', ':'), default=str)
            return HttpResponse(json_data, mimetype="application/json", status=200)
        except Exception as e:
            logService.logException("SQL POST error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kCustomErrorMsg__'+str(e))


def alert_dsm_for_demand_book(request, to_mail, cc, mailParams, *args, **kwargs):
        try:
            cc = [i for i in cc if i]                       
            table_row = ''
            for row in mailParams:
                table_row += "<tr><td>"+row['language']+"</td><td>"+row['grade']+"th</td> <td>"+row['courseName']+"</td><td>"+row['centerName']+"</td></tr>"
            
            message = "<p>Dear "+mailParams[0]['dsm_name']+",</p>\
                    <br>\
                    <p>"+mailParams[0]['ft_name']+ "("+str(mailParams[0]['ft_id'])+")  has booked the offering's</p>\
                    <table style='text-align: left;'>\
                        <tr><th>LANGUAGE</th><th>GRADE</th><th>SUBJECT</th><th>CENTER</th></tr> "+table_row+" \
                    </table><br>\
                    <p>The sessions will be generated after you confirm the demand.</p>\
                    <br>\
                    <p>Thanks and regards,</p>\
                    <p>eVidyaloka Team</p>"

            subject = 'Demand Blocked by '+str(request.user.get_full_name())+'('+str(request.user.id)+')'
            mail = EmailMessage(subject, message, to=to_mail, from_email=settings.DEFAULT_FROM_EMAIL, cc=cc)
            mail.content_subtype = 'html'
            mail.send()

                        
        except BadHeaderError:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, Invalid email header.")


class BookSlots(View):
    def get(self, request,  *args, **kwargs):
        selected_role = self.request.GET.get('role', None)
        try:
            if request.user.is_superuser:
                user_roles = list(Role.objects.values('id','name').filter(id__in=[1,3,20]))
            else:
                user_roles = list(request.user.userprofile.role.values('id','name').filter(id__in=[1,3,20]))
            slots = self.get_slots(self.request)
            
            return render_response(self.request, 'book_slots.html', {'data':{'user_roles':user_roles, 'selected_role':selected_role}, 'slots':slots})
        except Exception as e:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
        
    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            roleId = requestParams.get('role_id', None)
            
            if roleId is not None:
                slots =  SelectionDiscussionSlot.objects.filter(userp = request.user.userprofile, role = Role.objects.get(id=roleId), status='Booked', outcome__in=['Assigned', 'Completed'])
                data = {'is_booked':False, 'data':[]}
                if len(slots)>=1:
                    data['is_booked']=True
                    for slot in slots:
                        data['data'].append({'slotId':slot.id, 'roleId':slot.role.id, 'startTime':slot.start_time.strftime("%Y-%m-%d, %H:%M:%S"), 'endTime':slot.end_time.strftime("%H:%M:%S"),  'status':slot.status, 'outcome':slot.outcome})
                return genUtility.getSuccessApiResponse(request, data)
            else:
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, not found.")
        except Exception as e:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
    
    @method_decorator(login_required)
    def put(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            slotId = requestParams.get('slot_id', None)
            roleId = requestParams.get('role_id', None)
            bookfor = requestParams.get('bookfor', None)
            userId = requestParams.get('user_id', None)
         
            if bookfor:
                user = get_object_or_none(User, id=userId)
                if user is None: return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, user id not found.")
                userprofile = user.userprofile
            else:
                userprofile = request.user.userprofile
            
            if all([slotId, roleId]):
                slot = SelectionDiscussionSlot.objects.get(id=slotId)
                slot.userp = userprofile
                slot.role = Role.objects.get(id=roleId)
                slot.status='Booked'
                slot.booked_date = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
                slot.save()
                SelectionDiscussionSlotHistory.objects.create(slot=slot, userp=request.user.userprofile, status='Booked', booked_date=datetime.datetime.utcnow() + timedelta(hours=5, minutes=30))
                
                user = User.objects.get(id = userprofile.user.pk)    
                booking_date = slot.booked_date.strftime("%m/%d/%Y, %H:%M:%S")
                booking_time = slot.start_time.strftime("%m/%d/%Y, %H:%M:%S") + ' - ' + slot.end_time.strftime("%H:%M:%S")

                self.alert_confrirm_booking(str(user.id), user.get_full_name(), str(user.email), slot.role.id, booking_date, booking_time)
                return genUtility.getSuccessApiResponse(request, 'Success')
            else:
                return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
        except Exception as e:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
        
    @method_decorator(login_required)
    def delete(self, request,  *args, **kwargs):
        slotId = self.request.GET.get('slotId', None)       
        if slotId is not None:
            try:
                slot = SelectionDiscussionSlot.objects.get(id=slotId)
                slot.userp = None
                slot.role = None
                slot.status='Not Booked'
                slot.booked_date = None
                slot.outcome = 'Assigned'
                slot.save()
                SelectionDiscussionSlotHistory.objects.create(slot=slot, userp=request.user.userprofile, status='Booked')
                return genUtility.getSuccessApiResponse(request, 'Success')
            except Exception as e:
                traceback.print_exc()
                return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
        else:return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, no id found.")
           
    def get_slots(self, request,  *args, **kwargs):
        ''''Input = None; Output = list of slots/month/day[json]'''
        
        teacher_slots = SelectionDiscussionSlot.objects.values().filter(start_time__gt=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30) + datetime.timedelta(hours=3)), status='Not Booked', publisher_role__in=[7]).order_by('start_time')
        content_slots = SelectionDiscussionSlot.objects.values().filter(start_time__gt=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30) + datetime.timedelta(hours=3)), status='Not Booked', publisher_role__in=[17]).order_by('start_time')
            
        from itertools import groupby
        slots_dict = {'teacher_slots':{}, 'content_slots':{}}
        for count, slots in enumerate([teacher_slots, content_slots]):   
            month_wise_slots ={}; day_wise_slots ={}
            for k,v in groupby(slots,key=lambda x:(x['start_time'].month, x['start_time'].year)):
                month_wise_slots[k] = list(v)
                
            for month in month_wise_slots:
                slots = month_wise_slots[month]
                key = str(month[0])+','+str(month[1])
                day_wise_slots[key]={}
                for k,v in groupby(slots,key=lambda x:x['start_time'].day):
                    day_wise_slots[key][k]=list(v)
                if count==0: slots_dict['teacher_slots']=day_wise_slots
                if count==1: slots_dict['content_slots']=day_wise_slots
        return json.dumps(slots_dict, default=str)

    def alert_confrirm_booking(self, id, username, to_email, role_id, booking_date, booking_time,  *args, **kwargs):
        try:            
            subject = " eVidyaloka - Selection Discussion Booking confirmed -" + id
            args = {'username': username, 'role_id':role_id, 'booking_date':booking_date, 'booking_time':booking_time }                
            body = get_template('mail/_tsd_slot_book/full.html').render(Context(args))
            email = mail.EmailMessage(subject, body, to=[to_email], from_email=settings.DEFAULT_FROM_EMAIL)
            email.content_subtype = 'html'
            email.send()
        except Exception as e:
            pass
            
            
class ConfirmDemandView(View):
    
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            center_id = self.request.GET.get('center_id','')
            offering_id = self.request.GET.get('offering_id','')
            start_date = self.request.GET.get('startDate','')
            end_date = self.request.GET.get('endDate','')
            prefered_days = self.request.GET.get('pref_days','')
            prefered_timings = self.request.GET.get('pref_time','')
            teacher = self.request.GET.get('teacher','')
            software_link = self.request.GET.get('software_link','')
            demandSlots = Demandslot.objects.filter(user_id=teacher)
            slots = ''
            if teacher:
                user=User.objects.get(pk=teacher)
                teacher_id=user.id
            if offering_id and teacher_id:
                demand_slot=Demandslot.objects.filter(user_id=teacher_id,offering_id=offering_id)
                demand_slot_id=demand_slot.values_list('id',flat=True)
                demand_slot_mapped_ids=map(int,demand_slot_id)
                try:
                    offering_teacher_mapping=OfferingTeacherMapping.objects.filter(offering_id=offering_id,teacher_id=teacher_id).latest('created_date')
                    offering_teacher_mapping.demand_slot_id=demand_slot_mapped_ids
                    offering_teacher_mapping.confirmation_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
                    offering_teacher_mapping.updated_by_id=self.request.user.id
                    offering_teacher_mapping.save()
                except:
                    offering_teacher_mapping=OfferingTeacherMapping.objects.create(offering_id=offering_id,teacher_id=teacher_id)
                    offering_teacher_mapping.demand_slot_id=demand_slot_mapped_ids
                    offering_teacher_mapping.confirmation_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
                    offering_teacher_mapping.updated_by_id=self.request.user.id
                    offering_teacher_mapping.save()
            if demandSlots:
                slot_details = demandSlots.values_list('center__name','day','start_time','end_time')
                i = 0
                for slot in slot_details:
                    if i==0:
                        slots+=str(slot[1])+' '+str(slot[2])+' to '+str(slot[3])
                    else:
                        slots+= ' and '+str(slot[1])+' '+str(slot[2])+' to '+str(slot[3])
                    i+=1

            teacher_id = dc = center_admin = None
            if center_id:
                center = Center.objects.get(pk=center_id)
                if center.admin :
                    center_admin = center.admin
                dc = center.delivery_coordinator
          
            self.accept(self.request, userId=str(teacher), center_id=str(center_id), offering_id=str(offering_id), startDate=str(start_date), endDate=str(end_date), pref_days=str(prefered_days), pref_time=str(prefered_timings), software_link=software_link)
            current_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
            assign_to = None
            if dc!=None: assign_to = dc
            else: assign_to = center_admin
            demand_tasks = Task.objects.filter(assignedTo = assign_to,performedOn_userId = teacher_id,subject='User has been booked demand',taskStatus='Open').order_by('taskCreatedDate')
            if len(demand_tasks)>0:
                Task.objects.filter(id=demand_tasks[0].id).update(taskStatus='Closed',taskUpdatedDate = current_date)
            return HttpResponse(simplejson.dumps({'msg':'Session has been creted for demand'}), mimetype = 'application/json')
        except Exception as e:
            traceback.print_exc()
    
    def accept(self, request,  *args, **kwargs):
        try:
            userId = kwargs.get('userId','')
            center_id = kwargs.get('center_id','')
            offering_id = kwargs.get('offering_id','')
            start_date = kwargs.get('startDate','')
            end_date = kwargs.get('endDate','')
            _pref_days = kwargs.get('pref_days','')
            pref_slots = kwargs.get('pref_time','')
            software_link = kwargs.get('software_link','')
            
            teacher_name = center_name = teacher_email = dc_email = ca_email = vol_admin_email=assistant_email = center_details = assistant_details = ''
            usr = delivery_coordinator = center_admin = assistant = None
            
            if offering_id and userId:
                try :
                    offering_teacher_mapping=OfferingTeacherMapping.objects.filter(offering_id=offering_id,teacher_id=userId).latest('created_date')
                    offering_teacher_mapping.assigned_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
                    offering_teacher_mapping.updated_by_id=self.request.user.id
                    offering_teacher_mapping.save() 
                except :
                    offering_teacher_mapping=OfferingTeacherMapping.objects.create(offering_id=offering_id,teacher_id=userId)
                    offering_teacher_mapping.assigned_date=(datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
                    offering_teacher_mapping.updated_by_id=self.request.user.id
                    offering_teacher_mapping.save() 
            if center_id:
                try:
                    center = Center.objects.get(pk=center_id)
                    center_name = center.name
                    if center.admin!=None:
                        center_admin = center.admin
                        ca_email = center_admin.email
                        center_details = UserProfile.objects.get(user_id = center.admin.id)
                    if center.delivery_coordinator!=None:
                        delivery_coordinator = center.delivery_coordinator
                        dc_email = delivery_coordinator.email
                    if center.assistant!=None:
                        assistant_email = center.assistant.email
                        assistant = center.assistant
                        assistant_details = UserProfile.objects.get(user_id = center.assistant.id)
                except:
                    center_name = ''
            if userId:
                usr = User.objects.get(pk=userId)
                username = usr.username
                teacher_email = usr.email
                if usr.first_name:
                    teacher_name = str(usr.first_name)+" "+(usr.last_name)
                else:
                    teacher_name = usr.username
                btn_type = 'confirm'
                
                demand = Demandslot.objects.filter(user = usr,status='Booked',offering_id=int(offering_id))
                sess = Session.objects.filter(offering_id = offering_id)
                offer_data = reason = teacher_subject = grade = subject = days = ''
                offeringObj = None
                
                try:
                    offeringObj = Offering.objects.get(pk=offering_id)
                    offer_data = str(offeringObj.course.grade)+'th '+str(offeringObj.course.subject)+', '+str(make_date_time(offeringObj.start_date)["date"])+ ", "+str(make_date_time(offeringObj.start_date)["year"]) +' to '+str(make_date_time(offeringObj.end_date)["date"])+','+str(make_date_time(offeringObj.end_date)["year"])
                    teacher_subject = str(offeringObj.course.grade)+'th '+str(offeringObj.course.subject)
                    grade = offeringObj.course.grade
                    subject = offeringObj.course.subject
                except:
                    offeringObj = None
                if offeringObj and offeringObj.active_teacher_id is not None:
                        return True
                if len(demand)>0:
                    sess_arr = add_dynamic_session_accept(userId,offering_id,start_date,end_date,None,software_link,_pref_days,pref_slots,'true',self.request)
                    demand.update(status='Allocated')
                    user_profile = UserProfile.objects.get(user=usr)
                    role_pre = RolePreference.objects.filter(userprofile=user_profile, role_id__in=[1,20])
                    for role in role_pre:
                        role.role_status = 'Active'
                        role.save()

                    subject1 = "Welcome on-board as a teacher in "+str(center_name)
                    to = [teacher_email]
                    from_email = settings.DEFAULT_FROM_EMAIL
                    cc = [ca_email,assistant_email]
                    content_admins = AlertUser.objects.filter(role__name='vol_admin')
                    content_admins = content_admins[0].user.all()
                    if content_admins:
                        cc.extend([user.email for user in content_admins])
                    
                    
                    ctx1 = {'user':teacher_name,'center_name':center_name,'subject':teacher_subject}
                    message1 = get_template('mail/teacher_on_board.txt').render(Context(ctx1))
                    msg1 = EmailMessage(subject1, message1, to=to, from_email=from_email,cc=cc)
                    msg1.content_subtype = 'html'
                    msg1.send()
                    i = 0
                    for slot in demand:
                        if len(demand)==i:
                            days+=str(slot.day)
                        else:
                            days+=str(slot.day)+' , '
                        i+=1
                        
                        
                    subject2 = "eVidyaloka Class Kit-Connect with your Class"
                    ctx2 = {'user':teacher_name,'dc':delivery_coordinator,'center':center,'center_details':center_details,
                            'grade':grade,'subjects':subject,'days':days,'assistant':assistant,'assistant_details':assistant_details}
                    message2 = get_template('mail/eVidyaloka_classKit.html').render(Context(ctx2))
                    msg2 = EmailMessage(subject2, message2, to=to, from_email=from_email,cc=cc)
                    msg2.content_subtype = 'html'
                    msg2.send()
                    current_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
                    vol_co = User.objects.get(pk=19064)
                    demand_tasks = Task.objects.filter(assignedTo = vol_co,performedOn_userId = usr.id,subject='Your allocation of the selected course is Confirmed',taskStatus='Open').order_by('taskCreatedDate')
                    if len(demand_tasks)>0:
                        Task.objects.filter(id=demand_tasks[0].id).update(taskStatus='Closed',taskUpdatedDate = current_date)
        except Exception as e:
            traceback.print_exc()


@login_required
def search_teacher(request):
    try:
        teacher_type = request.GET.get('teacher_type', None)
        search_text = request.GET.get('search_text', None)
        if search_text is None or teacher_type is None: return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, teacher not found.")
        users = User.objects.filter((Q(id__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text)) & Q(userprofile__rolepreference__role__name=teacher_type) & Q(userprofile__rolepreference__role_outcome='Recommended')).exclude(first_name__isnull=True, last_name__isnull=True, first_name='', last_name='').values('id', 'first_name', 'last_name').distinct()
        return HttpResponse(simplejson.dumps({'data':list(users)}), mimetype = 'application/json')
    except Exception as e:
        traceback.print_exc()
        return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, not found.")


class FlmDoubtsThread(View):
    def get(self, request,  *args, **kwargs):
        try:
            offeringId = self.request.GET.get('offeringId', None)
            doubtId = self.request.GET.get('doubtId', None)
                       
            if not all([offeringId, doubtId]):
                return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
                
            doubts = list(Doubt_Thread.objects.filter(id=int(doubtId), offering_id=int(offeringId)).values('id', 'student_id', 'student__name', 'text', 'created_on', 'resource_type', 'resource_url','resource_doc_id', 'content_type_id', 'parent_thread_id', 'created_by_id', 'created_by__first_name', 'created_by__last_name', 'assigned_to_id', 'assigned_to__first_name', 'assigned_to__last_name', 'status', 'topic__title', 'subtopic__name'))
            response = list(Doubt_Thread.objects.filter(offering_id=int(offeringId), parent_thread_id=int(doubtId)).values('id', 'student_id', 'student__name', 'text', 'created_on', 'resource_type', 'resource_url','resource_doc_id', 'content_type_id', 'parent_thread_id', 'created_by_id', 'created_by__first_name', 'created_by__last_name', 'assigned_to__first_name', 'assigned_to__last_name'))
            
            for doubt in doubts:
                for key,val in doubt.items():
                    if isinstance(val, datetime.datetime):
                        doubt[key] = val.isoformat()
            for doubt in response:
                for key,val in doubt.items():
                    if isinstance(val, datetime.datetime):
                        doubt[key] = val.isoformat()
            
            dataObject = {'doubts':doubts, 'response':response}
            return genUtility.getSuccessApiResponse(request, dataObject)
        except Exception as e:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
        
    def post(self, request,  *args, **kwargs):

        try:
            centerId = self.request.POST.get('centerId', None)
            offeringId = self.request.POST.get('offeringId', None)
            topicId = self.request.POST.get('topicId', None)
            subtopicId = self.request.POST.get('subtopicId', None)
            studentId = self.request.POST.get('studentId', None)
            doubtText = self.request.POST.get('doubtText', None)
            urlString = self.request.POST.get('url', None)
            attachmentType = self.request.POST.get('attachmentType', None)
            
            dtDoc = None; resourceType = '2'; resourceUrl = ''; contentTypeId = 2
            
            if attachmentType == "image":
                cloudFolderName = settings.TEACHER_DOUBT_RESPONSE_STORAGE_FOLDER
                dtDoc = docUploadService.upload_user_document_s3(self.request, "teacher", None, cloudFolderName,None,"obj")
                resourceUrl = dtDoc.url

            elif urlString and len(urlString) > 10:
                resourceType = '5'
                resourceUrl = urlString
                contentTypeId = 4
                
            dtObject = Doubt_Thread.objects.create(student_id=studentId, offering_id=offeringId, topic_id=topicId, subtopic_id=subtopicId,
                resource_url=resourceUrl, resource_doc=dtDoc, status='1', text=doubtText, record_type='1', content_type_id=contentTypeId,
                resource_type=resourceType, created_by=self.request.user, updated_by_id=settings.SYSTEM_USER_ID_AUTH,
                created_on=genUtility.getCurrentTime()
            )
            dtObject.save()
            
            
            dataObject = {'id':dtObject.id, 'text':dtObject.text, 'url':dtObject.resource_url}
            return genUtility.getSuccessApiResponse(request, dataObject)

        except Exception as e:
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


class ContentUploadView(View):
    
    
    def __init__(self):
        self.tables = ['auth_user','partner_partner', 'web_contentdetail', 'web_content_demand']
    
    
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return render(request, "bulk_upload_content_view.html", {'tables':self.tables})
        else:
            return HttpResponseNotFound("Forbidden Access")

    def validateandContentHeaders(self,fieldsArray):
        try:
            for i in range(0, len(fieldsArray)):
                fieldVal = fieldsArray[i]
                if fieldVal:
                    if i == 0:
                        valueStr = "(" + fieldVal 
                    else:
                        valueStr = valueStr + "," + fieldVal
            valueStr = valueStr + ")"
            return valueStr
        except Exception as e:
            print("validateandContentHeaders Exceptions", e)
            traceback.print_exc()
            return None

    def getDValueString(self, fieldsArray, csvRow):
        try:
            valueStringArray = []
            valueStr = ""
            for i in range(0, len(fieldsArray)):
                fieldVal = csvRow[i]
                fieldName = fieldsArray[i]
                if fieldVal is None:
                    fieldVal = "null"
                if i == 0:
                    valueStr = "('" + fieldVal + "'"
                else:
                    valueStr = valueStr + ",'" + fieldVal + "'"



            valueStr = valueStr + ")"

            return valueStr
        except Exception as e:
            print("getDValueString Exceptions", e)
            traceback.print_exc()
            return None

    def post(self, request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                pass
            else:
                return HttpResponseNotFound("Forbidden Access")

            tableName = request.POST.get('tableName')

            inputCsvFile = request.FILES['file']
            csvReader = csv.reader(inputCsvFile, delimiter=',')
            j = 0
            fieldsArray = None
            fieldsStr = ""
            valueDataString = ""
            for row in csvReader:
                if j == 0:
                    fieldsArray = row
                    fieldsStr = self.validateandContentHeaders(row)
                    if fieldsStr is None:
                        return render(request, "bulk_upload_content_view.html", {"rejectedData": "Improper column value", 'tables':self.tables})
                else:
                    if j == 1:
                        pass
                    else:
                        valueDataString = valueDataString + " , "

                    valueString = self.getDValueString(fieldsArray, row)
                    if valueString is None:
                            return render(request, "bulk_upload_content_view.html",{"rejectedData": "Invalid Values at row " + str(j-2), 'tables':self.tables})
                    else:
                        valueDataString = valueDataString + valueString
                j = j + 1
            query = "INSERT INTO " + tableName + "" +fieldsStr + " VALUES "+ valueDataString + ";"
            

            db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], 
            passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True, compress=True, connect_timeout=30)
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)
            users_cur.execute(query)
            db.close()
            users_cur.close()
            
            return render(request, "bulk_upload_content_view.html", {"message": "Successfully uploaded the records. Table Name "+tableName+". Total number of records " + str(j-1), 'tables':self.tables})


        except Exception as e:
            logService.logExceptionWithFunctionName("ContentUploadView POST",e)
            msg = genUtility.getErrorMessageFromException(e)
            return render(request, "bulk_upload_content_view.html", {"rejectedData": msg, 'tables':self.tables})


class QuizResult(View):
    
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
            center  = Center.objects.all().order_by('name')
            ay      = Ayfy.objects.filter(types='Academic Year').order_by('title')

            data = {
                "centers"   : center,
                'ay'        : ay,
            }

            return render(request, 'quizresult.html', {"data":data})
    
    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        studList = []
        try:
            centerId = self.request.POST.get('centerId', None)
            ay = self.request.POST.get('academicYear', None)
            grade = self.request.POST.get('grade',None)
            subject = self.request.POST.get('subject',None)
            fromDate = self.request.POST.get('fromDate', None)
            toDate = self.request.POST.get('toDate', None)

            print('grade', grade)

            offerObj = Offering.objects.filter(center_id=centerId).exclude(academic_year=None)
            print('offer', offerObj)

            offerLen = offerObj.count()
            
            if offerLen != 0:
                for ent in offerObj:
                    enroll_stud = ent.enrolled_students.all().exclude(center=None).filter(center__id=ent.center_id).distinct()

                    for ent1 in enroll_stud:
                        quizObj = Quiz_History.objects.filter(student_id=ent1.id,offering_id=ent.id,created_on__lte=toDate, created_on__gte=fromDate).order_by('attempt')
                        print('quizObj',quizObj)
                        if len(quizObj) > 0:
                            score = 0
                            date = 0
                            acScore = []
                            if grade:
                                print('inside grade')
                                if subject:
                                    if grade == ent1.grade and subject == ent.course.subject:
                                        for q in quizObj:
                                            question = Quiz_History_Detail.objects.filter(quiz_history_id=q.id)
                                            score = len(question)
                                            date    = q.created_on
                                            correctAns = Quiz_History_Detail.objects.filter(quiz_history_id=q.id, result=1).count()

                                            stud = {
                                                'centerName': ent1.center.name,
                                                'offeringId': ent.id,
                                                'studentId' : ent1.id,
                                                'studentName': ent1.name,
                                                'subject'   : ent.course.subject,
                                                'grade'     : ent1.grade,
                                                'attempt'   : q.attempt,
                                                'maxScore'  : score,
                                                'actualScore': correctAns,
                                                'date'      : date
                                            }
                                            studList.append(stud)

                                else:
                                    
                                    if grade == ent1.grade:
                                        print('inside only grade')
                                        for q in quizObj:
                                            question = Quiz_History_Detail.objects.filter(quiz_history_id=q.id)
                                            score = len(question)
                                            date    = q.created_on
                                            correctAns = Quiz_History_Detail.objects.filter(quiz_history_id=q.id, result=1).count()

                                            stud = {
                                                'centerName': ent1.center.name,
                                                'offeringId': ent.id,
                                                'studentId' : ent1.id,
                                                'studentName': ent1.name,
                                                'subject'   : ent.course.subject,
                                                'grade'     : ent1.grade,
                                                'attempt'   : q.attempt,
                                                'maxScore'  : score,
                                                'actualScore': correctAns,
                                                'date'      : date
                                            }
                                            studList.append(stud)

                            else:
                                print('outside grade')
                                for q in quizObj:
                                    question = Quiz_History_Detail.objects.filter(quiz_history_id=q.id)
                                    score = len(question)
                                    date    = q.created_on
                                    correctAns = Quiz_History_Detail.objects.filter(quiz_history_id=q.id, result=1).count()

                                    stud = {
                                        'centerName': ent1.center.name,
                                        'offeringId': ent.id,
                                        'studentId' : ent1.id,
                                        'studentName': ent1.name,
                                        'subject'   : ent.course.subject,
                                        'grade'     : ent1.grade,
                                        'attempt'   : q.attempt,
                                        'maxScore'  : score,
                                        'actualScore': correctAns,
                                        'date'      : date
                                        }
                                    studList.append(stud)

            else:
                return HttpResponse('No data')

            #p = Paginator(studlist,10)
            #page = request.GET.get('page')
            #stud = p.get_page(page)

            center  = Center.objects.all().order_by('name')
            ay      = Ayfy.objects.filter(types='Academic Year').order_by('title')

            data = {
                "centers"   : center,
                'ay'        : ay,
            }

            return render(request, 'quizresult.html', {"data":data, 'studList':studList})
        
        except Exception as e:
            print("POST Exception  e", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

@login_required
def quizfilter(request):
    print('inside quiz fliter')
    centerId = request.GET.get('centerId')
    ayId    = request.GET.get('ay')
    print(centerId)
    print('ayId', ayId)

    if centerId and ayId:
        #ayObj   = Ayfy.objects.filter(id= ayId)
        offerObj = Offering.objects.filter(center_id=centerId).exclude(academic_year=None)

        subject = []
        grade   = []
        for offer in offerObj:
            print('id',offer.course.subject)
            if offer.course.subject not in subject:
                subject.append(offer.course.subject)
            if offer.course.grade not in grade:
                grade.append(offer.course.grade)
        
        print('subject', subject)
        print(grade)

        data = {'subject': subject, 'grade': grade}

        return HttpResponse(simplejson.dumps({'data':data}), mimetype='application/json')

    else:
        return 'Invalid Request'

class SimilarCourse(View):
    
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            ay = self.request.GET.get('ay', None)
            centerId = self.request.GET.get('center_id', None)
            courseId = self.request.GET.get('course_id', None)
            context = {'exist':False}
            offerings = Offering.objects.filter(course_id=courseId, center_id=centerId, academic_year_id=ay).values('course__subject', 'course__grade', 'status')
            if len(offerings)>0: 
                context['exist'] = True
                context['offerings'] = list(offerings)
            return genUtility.getSuccessApiResponse(request, context)
        except Exception as e:
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')

    
class Assistance(View):
    
    @method_decorator(login_required)
    def put(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(request.body)
            assistance = requestParams.get('assistance', None)
            if assistance: 
                UserProfile.objects.filter(user=request.user).update(assistance=assistance)
                return genUtility.getSuccessApiResponse(request, 'Success')
            else: return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
        except Exception as e:
            logService.logException("Assistance PUT Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


class Demand(View): 
    
    def get(self, request,  *args, **kwargs):
        """get all demands

        Returns:
           request (GET): html template with all type of demands
        """        
        try:   
            db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True)
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query = "select subject, id from web_course  group by subject "
            users_cur.execute(query)
            courses = users_cur.fetchall()

            teaching_data = []
            is_content_developer=False; is_teacher=False; is_flt_teacher=False
            today_date = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
            today_date = today_date.strftime("%d-%m-%Y")
            today_date = datetime.datetime.strptime(today_date.strip(), "%d-%m-%Y")
            for course_subject in courses:            
                running_courses_count = 0; pending_courses_count = 0
                course_offering = Offering.objects.filter(course__subject=course_subject['subject'],end_date__gt=today_date)
                center_ids = Offering.objects.values_list('center_id',flat=True).filter(course__subject=course_subject['subject'],end_date__gt=today_date, center__digital_school__isnull=True).distinct()
                filtered_center_ids = set(Demandslot.objects.filter( Q(center_id__in=center_ids) & Q(start_time__gte='09:00:00') & Q(end_time__lte='17:00:00')).values_list('center_id',flat=True))
                
                if filtered_center_ids:
                    for center_id in filtered_center_ids:
                        demand_slot_booked = Demandslot.objects.filter(center_id=center_id, status='Booked').values_list('offering',flat=True).distinct()
                        pending_offers = []
                        if course_offering:
                            running_offers = course_offering.filter(center_id=center_id,status='running').exclude(active_teacher_id=None)
                            running_courses_count += running_offers.count() 
                            if demand_slot_booked:
                                pending_offers = course_offering.filter(center_id=center_id).filter(Q(status='pending')|(Q(status='running')& Q(active_teacher_id=None))).exclude(id__in=demand_slot_booked)
                                pending_courses_count += pending_offers.count()
                            else:
                                pending_offers = course_offering.filter(center_id=center_id).filter(Q(status='pending')|(Q(status='running')& Q(active_teacher_id=None)))
                                pending_courses_count += pending_offers.count()
                    if pending_courses_count<=0:continue               
                    data = {'subject':course_subject['subject'],'running_teacher':running_courses_count,'pending_teacher':pending_courses_count,'course_id':course_subject['id']}
                    teaching_data.append(data)

            if  request.user.is_authenticated() and has_pref_role( request.user.userprofile, "Content Developer"):is_content_developer = True
            if  request.user.is_authenticated() and has_pref_role( request.user.userprofile, "Teacher"):is_teacher = True
            if  request.user.is_authenticated() and has_pref_role( request.user.userprofile, "Facilitator Teacher"):is_flt_teacher = True
            now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            known_languages_string = ""
            if  request.user.is_authenticated():
                known_languages_json = UserProfile.objects.get(user= request.user).languages_known
                known_languages = [i['lang'] for i in ast.literal_eval(known_languages_json)]
                
                count=1; known_languages_string2=""
                for st in known_languages:
                    known_languages_string2 += "'"+str(st) +"'"
                    if count < len(known_languages):
                        known_languages_string2+=","
                    count+=1

                known_languages_string = "AND genutilities_language.name in ("+ known_languages_string2 +")"
                
            query = "SELECT web_course.subject, (select count(distinct(id)) from web_offering where course_id=web_course.id and active_teacher_id is not null and status='running') as teaching, count(distinct(web_offering.id)) as required\
                    FROM web_course INNER JOIN web_offering ON web_course.id = web_offering.course_id INNER JOIN web_center ON web_offering.center_id = web_center.id INNER JOIN web_demandslot ON web_center.id = web_demandslot.center_id\
                    INNER JOIN genutilities_language ON web_course.language_id = genutilities_language.id\
                    WHERE  web_demandslot.start_time >= '09:00:00' AND web_demandslot.end_time <= '17:00:00' AND web_center.digital_school_id IS NOT NULL AND web_offering.end_date > '"+ now_time +"' AND web_course.status = 'active'\
                    AND web_offering.active_teacher_id is null AND web_offering.status IN ('running', 'pending') AND web_demandslot.status = 'Unallocated' AND web_center.status != 'Closed' "+ known_languages_string +" group by web_course.subject"
            users_cur.execute(query)
            flt_data = users_cur.fetchall()
            users_cur.close()
            db.close()
            
            content_demand = Content_Demand.objects.values('workstream__name').annotate(workstream_count=Count('workstream__name'))    
            
            context = {'teaching_data':simplejson.dumps(teaching_data),'content_dev':['Math','Science', 'English Foundation'], 'flt_data':simplejson.dumps(flt_data), 
                        'content_demand':list(content_demand),'is_content_developer':is_content_developer, 'is_flt_teacher':is_flt_teacher, 'is_teacher':is_teacher}
            return render(request, 'demand.html',context)
        except Exception as e:
            logService.logException("Demand GET Exception error", e.message)
            return genUtility.error_404(request)
    


class OnlineDemand(View):
    '''
    Online Demand
    '''
    
    # @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        
        """get online demand

        Returns:
            request (GET): html template: online demand
        """        
        
        subject = self.request.GET.get('subject', None)
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            user_details = {'is_teacher': None, 'profile_status': None, 'preferred_language': []}
            known_languages_string = ''
            avoid_test_ceters = ' AND web_center.is_test=0'
            if request.user.is_authenticated():
                known_languages_json = UserProfile.objects.get(user=request.user).languages_known
                known_languages = [str(i['lang']) for i in ast.literal_eval(known_languages_json)]
                known_languages_string = "AND web_center.language in ('{lang}') AND genutilities_language.name in ('English','{lang}')".format(lang="','".join(known_languages))
                    
                user_details = {
                    'is_teacher': has_pref_role(request.user.userprofile, "Teacher"),
                    'profile_status': True if request.user.userprofile.profile_completion_status else False,
                    'preferred_language': known_languages
                }

                if request.user.is_superuser:
                    avoid_test_ceters = ''

            query = '''SELECT web_center.name as centerName, group_concat(distinct(web_center.id)) as centerId, web_offering.id as offeringId,
                    web_course.subject, web_course.id as courseId, web_course.grade, group_concat(web_demandslot.day) as days, 
                    genutilities_language.name as language, min(web_demandslot.start_time) as start_time, max(web_demandslot.end_time) as end_time,
                    (select count(distinct(id)) from web_offering where course_id=web_course.id and active_teacher_id is not null and status='running') as teaching, 
                    count(distinct(web_offering.id)) as required, web_center.district as district,
                    (select count(id) from web_offering where course_id=web_course.id and active_teacher_id is null and status='running' AND web_offering.end_date > '{now_time}') as backfill
                    FROM web_course INNER JOIN web_offering ON web_course.id = web_offering.course_id LEFT JOIN web_center ON web_offering.center_id = web_center.id 
                    INNER JOIN genutilities_language ON web_course.language_id = genutilities_language.id LEFT JOIN web_demandslot ON web_center.id = web_demandslot.center_id 
                    WHERE web_demandslot.start_time >= '09:00:00' AND web_demandslot.end_time <= '17:00:00' {known_languages_string} {avoid_test_ceters}
                    AND web_offering.end_date > '{now_time}' and web_course.status = 'active'  AND web_offering.active_teacher_id is null AND web_center.digital_school_id IS NULL 
                    AND web_offering.status IN ('running', 'pending') AND web_demandslot.status = 'Unallocated' AND web_demandslot.status != 'Booked'  AND web_center.status != 'Closed' 
                    AND (CASE WHEN (select count(id) from web_demandslot wd where wd.offering_id=web_offering.id)>0 THEN web_demandslot.offering_id=web_offering.id ELSE web_demandslot.offering_id is null END)
                    group by web_course.grade, web_course.subject, genutilities_language.name'''.format(now_time=now_time, known_languages_string=known_languages_string, avoid_test_ceters=avoid_test_ceters)

            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'],
                                 passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True)
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)
            users_cur.execute('SET SESSION group_concat_max_len = 999999')
            users_cur.execute(query)
            demand_course = users_cur.fetchall()
            users_cur.close()
            db.close()

            for demand in demand_course:
                demand['days'] = demand['days'].split(',')
                demand['centerId'] = demand['centerId'].split(',')
                demand['start_time'] = demand['start_time'].total_seconds()
                demand['end_time'] = demand['end_time'].total_seconds()
            data = {}
            data['flt_data'] = demand_course
            data['subject'] = subject

            # check previous booking
            previous_booking = {'is_booked': False}
            is_book_for_others = False
            if self.request.user.is_authenticated():
                booked_demadslot = Demandslot.objects.filter(user=self.request.user, status='Booked', center__digital_school__isnull=True).values(
                    'id', 'center__name', 'date_booked', 'day', 'start_time', 'end_time', 'offering__course__subject', 'offering__batch', 'offering__language', 'offering__course__grade')
                if len(booked_demadslot) > 0:
                    previous_booking['is_booked'] = True
                    previous_booking['slots'] = list(booked_demadslot)
                if has_role_preference(self.request.user, "Center Admin") or has_role_preference(self.request.user, "Delivery co-ordinator") or self.request.user.is_superuser:
                    is_book_for_others = True
            return render(self.request, 'demand_online.html', {'flt_data': simplejson.dumps(data), 'user_details': user_details, 'previous_booking': simplejson.dumps(previous_booking, default=str), 'is_book_for_others': is_book_for_others})
        except Exception as e:
            logService.logException("OnlineDemand GET Exception error", e.message)
            return genUtility.error_404(request, e.message)

    # @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        
        """Online demand slots in centers by subject

        Returns:
            request (POST): JSON list of dict of slots
        """        
        
        try:
            requestParams = json.loads(self.request.body)
            subjects = requestParams.get('subjects', None)
            grades = requestParams.get('grades', None)
            days = requestParams.get('days', None)
            languages = requestParams.get('languages', None)
            prefred_languages = requestParams.get('prefred_languages', None)
            startTime = requestParams.get('startTime', None)
            endTime = requestParams.get('endTime', None)
            now_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            centerobj = current_ay = None
            center = Center.objects.filter(language=languages)
            if center:
                centerobj = center[0]

            if centerobj:
                current_ay = get_object_or_none(Ayfy, start_date__year=datetime.datetime.now().year, board=centerobj.board)
                if not current_ay:
                    last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
                    current_ay = get_object_or_none(Ayfy, start_date__year=last_year, board=centerobj.board)

            avoid_test_ceters = subjectString = gradesString = daysString = languagesString = known_languages_string = demanday = startTimeString = endTimeString = ''

            if request.user.is_authenticated:
                if not request.user.is_superuser:
                    avoid_test_ceters = ' AND web_center.is_test=0'
                    known_languages_json = UserProfile.objects.get(user=request.user).languages_known
                    known_languages = [str(i['lang']) for i in ast.literal_eval(known_languages_json)]
                    known_languages_string = "AND web_center.language in ('{lang}')".format(lang="','".join(known_languages))

            if subjects is not None and len(subjects) > 0:
                subjectString = " AND web_course.subject = '{}'".format(str(subjects))
            if grades is not None and len(grades) > 0:
                gradesString = " AND web_course.grade = '{}'".format(str(grades))
            if days is not None and len(days) > 0:
                daysString = " AND web_demandslot.day in ('{}')".format("','".join(days))
            if languages is not None and len(languages) > 0:
                languagesString = " AND genutilities_language.name = '{}'".format(str(languages))

            # if prefred_languages is not None and len(prefred_languages) > 0:
            #     prefred_languagesString = " AND web_center.language in ('{}')".format("','".join(prefred_languages))

            if current_ay:
                demanday = "AND (web_demandslot.created_on >= '{ay}' OR web_demandslot.offering_id = web_offering.id)".format(ay=str(current_ay.start_date).zfill(2))
            if startTime is not None and int(startTime) > 0:
                startTimeString = " AND web_demandslot.start_time >= '{}:00:00'".format(str(startTime).zfill(2))
            if endTime is not None and int(endTime) > 0:
                endTimeString = " AND web_demandslot.end_time <= '{}:00:00'".format(str(endTime).zfill(2))

            conditionString = avoid_test_ceters+startTimeString+demanday+endTimeString + \
                subjectString+gradesString+daysString+languagesString+known_languages_string

            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'],
                                 passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True)
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query = '''SELECT web_offering.status, web_offering.active_teacher_id, web_offering.batch as batch, web_center.id as centerId, 
                    web_center.name as centerName, web_center.location_map, web_center.state as centerState, web_center.district as centerDistrict, 
                    web_center.board as centerBoard, web_course.id as courseId, web_course.subject, web_course.grade, web_center.language as language,
                    web_offering.id as offeringId, group_concat(web_demandslot.day, '--', concat(web_demandslot.id,'-',web_demandslot.start_time,'-',web_demandslot.end_time)) as slots 
                    FROM web_course INNER JOIN web_offering ON web_course.id = web_offering.course_id INNER JOIN web_center ON web_offering.center_id = web_center.id 
                    INNER JOIN web_demandslot ON web_center.id = web_demandslot.center_id  
                    INNER JOIN genutilities_language ON web_course.language_id = genutilities_language.id
                    WHERE  web_course.status = 'active' AND web_offering.active_teacher_id is null AND web_offering.status IN ('running', 'pending') 
                    AND web_demandslot.status = 'Unallocated' AND web_center.status != 'Closed' AND (web_center.board=web_course.board_name OR web_course.board_name='eVidyaloka')
                    AND (CASE WHEN (select count(id) from web_demandslot wd where wd.offering_id=web_offering.id)>0 THEN web_demandslot.offering_id=web_offering.id 
                    ELSE web_demandslot.offering_id is null END) AND web_center.digital_school_id is null {conditionString}AND web_offering.end_date > '{now_datetime}' 
                    group by web_offering.id, (web_demandslot.start_time and web_demandslot.end_time) 
                    order by web_offering.active_teacher_id'''.format(conditionString=conditionString, now_datetime=now_datetime)

            users_cur.execute('SET SESSION group_concat_max_len = 999999')
            users_cur.execute(query)
            offering_demand = users_cur.fetchall()
            users_cur.close()
            db.close()

            for demand in offering_demand:
                dm = {}
                for slot in demand['slots'].split(','):
                    day = slot.split('--')[0]
                    slots = slot.split('--')[1]
                    if not dm.has_key(day):
                        dm[day] = []
                    slot_times = slots.split('-')
                    dm[day].append(
                        {'demandId': slot_times[0], 'startTime': slot_times[1], 'endTime': slot_times[2]})
                    dm[day] = [dict(t)
                               for t in {tuple(d.items()) for d in dm[day]}]
                demand['enrolledStudents'] = Offering_enrolled_students.objects.filter(
                    offering_id=demand['offeringId']).count()
                demand['slots'] = dm

            return genUtility.getSuccessApiResponse(request, offering_demand)
        except Exception as e:
            logService.logException("OnlineDemand POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


class BookOnlineDemand(View):

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            # import pdb; pdb.set_trace()
            requestParams = json.loads(self.request.body)
            book_for_others = requestParams.get('book_for_others', None)
            teacher_id = requestParams.get('teacher_id', None)
            slot_data = requestParams.get('cart', None)
            teacher = None
            teacher = self.request.user
            if book_for_others:
                if teacher_id is not None:
                    teacher = get_object_or_none(User, id=teacher_id)
                if teacher is None:
                    return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 1, User not exist.")

            user_role = get_object_or_none(RolePreference, userprofile=teacher.userprofile, role_id=1)
            if user_role is None:
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 1, User do not have role.")
            elif user_role.role_outcome != 'Recommended':
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 2, Please complete selection discution.")

            booked_demadslot = Demandslot.objects.filter(user=teacher, status='Booked', center__digital_school__isnull=True)
            if len(booked_demadslot) > 0:
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 3, Release previous booked demand.")

            offeringId = slot_data[0].get('offeringId', None)
            if offeringId:
                offering = get_object_or_none(Offering, id=offeringId)
                lang = offering.center.language
                known_languages_json = UserProfile.objects.get(user=request.user).languages_known
                known_languages = [str(i['lang']) for i in ast.literal_eval(known_languages_json)]
                
                if lang not in known_languages:
                    return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 1, Teacher and center language mismatch.")

            slot_objs = []
            for slots in slot_data:
                offeringId = slots.get('offeringId', None)
                demandId = slots.get('demandId', None)
                if offeringId is not None and demandId is not None:
                    offering = get_object_or_none(Offering, id=offeringId)
                    slot = get_object_or_none(Demandslot, id=demandId)
                else:
                    continue
                if offering and slot:
                    offering_teacher_mapping = OfferingTeacherMapping.objects.create(offering=offering, teacher=teacher,
                                                                                     booked_date=datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30),
                                                                                     created_by=request.user, updated_by=request.user)

                    slot.offering = offering
                    slot.status = 'Booked'
                    slot.user = teacher
                    slot.date_booked = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
                    slot.save()
                    slot_objs.append(slot)

            recipients = new_cc = []
            centerobj = offering.center
            current_ay = None
            center_admin_mail = centerobj.admin.email if centerobj.admin else None
            dc_mail = centerobj.delivery_coordinator.email if centerobj.delivery_coordinator else None
            current_ay = Ayfy.objects.filter(board=centerobj.board).order_by('-id')[0]

            args = {'user': teacher, 'slots': slot_objs, 'contxt': 'Blocked', 'confirm_url': settings.WEB_BASE_URL + "centeradmin/?center_id=" + str(offering.center.id)+'&ay_id='+str(current_ay.id)}
            subject = 'Demand Blocked by ' + str(teacher.get_full_name()) + '( id:'+str(teacher.id)+')'
            message = get_template('mail/_demand_handle/full_rft.txt').render(Context(args))

            if dc_mail is not None:
                new_cc.append(dc_mail)
            if center_admin_mail is not None:
                new_cc.append(center_admin_mail)

            admin = AlertUser.objects.get(role__name='vol_admin')
            if admin: new_cc.extend([user.email for user in admin.user.all()])

            try:
                thread.start_new_thread(genUtility.send_mail_thread, (subject, message, settings.DEFAULT_FROM_EMAIL, recipients, new_cc))
            except Exception as e:
                logService.logException("BookOnlineDemandView MAIL Exception error", e.message)

            return genUtility.getSuccessApiResponse(request, 'Success')
        except Exception as e:
            logService.logException("BookOnlineDemandView PUT Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest, 0, something went wrong.')

    @method_decorator(login_required)
    def put(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            slots = [int(x) for x in requestParams.get('selected', [])]
            user_slots = Demandslot.objects.filter(
                user=request.user, id__in=slots)
            demand = user_slots[0]
            offering = get_object_or_none(Offering, id=demand.offering_id)
            if offering:
                if offering.status == 'runnning' and offering.active_teacher:
                    return genUtility.getSuccessApiResponse(request, 'kCustomErrorMsg, Demand already confirmed.')

            for ent in user_slots:
                try:
                    if ent.type == 1:
                        ent.offering = None
                    ent.user = None
                    ent.status = 'Unallocated'
                    ent.date_booked = None
                    ent.save()
                except Exception as exp:
                    continue
            return genUtility.getSuccessApiResponse(request, 'kCustomErrorMsg, Demand Released.')
        except Exception as e:
            logService.logException(
                "BookOnlineDemandView PUT Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


class FtDemand(View):
    '''
    FLT Demand
    '''
    # @method_decorator(login_required)

    def get(self, request,  *args, **kwargs):
        subject = self.request.GET.get('subject', None)
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            user_details = {'is_content_developer': None,
                            'profile_status': None, 'preferred_language': []}
            known_languages_string = ""
            if request.user.is_authenticated():
                known_languages_json = UserProfile.objects.get(user=request.user).languages_known
                known_languages = [i['lang'] for i in ast.literal_eval(known_languages_json)]
                known_languages_string = " AND web_center.language in ('{lang}') AND genutilities_language.name in ('English','{lang}')".format(lang="','".join(known_languages))
                user_details = {
                    'is_content_developer': has_pref_role(request.user.userprofile, "Content Developer"),
                    'profile_status': True if request.user.userprofile.profile_completion_status else False,
                    'preferred_language': known_languages
                }

            query = "SELECT web_center.name as centerName, group_concat(distinct(web_center.id)) as centerId, web_offering.id as offeringId, web_course.subject, web_course.id as courseId, web_course.grade, group_concat(web_demandslot.day) as days, genutilities_language.name as language, min(web_demandslot.start_time) as start_time, max(web_demandslot.end_time) as end_time,\
                    (select count(distinct(id)) from web_offering where course_id=web_course.id and active_teacher_id is not null and status='running') as teaching, count(distinct(web_offering.id)) as required, web_center.district as district\
                    FROM web_course INNER JOIN web_offering ON web_course.id = web_offering.course_id INNER JOIN web_center ON web_offering.center_id = web_center.id INNER JOIN genutilities_language ON web_course.language_id = genutilities_language.id\
                    INNER JOIN web_demandslot ON web_center.id = web_demandslot.center_id WHERE web_course.status = 'active' " + known_languages_string + "\
                    AND web_offering.end_date > '" + now_time + "' AND web_offering.active_teacher_id is null AND web_center.digital_school_id IS NOT NULL \
                    AND (CASE WHEN (select count(id) from web_demandslot wd where wd.offering_id=web_offering.id)>0 THEN web_demandslot.offering_id=web_offering.id ELSE web_demandslot.offering_id is null END)\
                    AND web_offering.status IN ('running', 'pending') AND web_demandslot.status = 'Unallocated'  AND web_center.status != 'Closed' group by web_course.grade, web_course.subject, genutilities_language.name"

            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'],
                                 passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True)
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)
            users_cur.execute('SET SESSION group_concat_max_len = 999999')
            users_cur.execute(query)
            demand_course = users_cur.fetchall()
            users_cur.close()
            db.close()

            for demand in demand_course:
                demand['days'] = demand['days'].split(',')
                demand['centerId'] = demand['centerId'].split(',')
                demand['start_time'] = demand['start_time'].total_seconds()
                demand['end_time'] = demand['end_time'].total_seconds()
            data = {}
            data['flt_data'] = demand_course
            data['subject'] = subject

            # check previous booking
            previous_booking = {'is_booked': False}
            is_book_for_others = False
            if self.request.user.is_authenticated():
                booked_demadslot = Demandslot.objects.filter(user=self.request.user, status='Booked').values(
                    'id', 'center__name', 'date_booked', 'day', 'start_time', 'end_time', 'offering__course__subject', 'offering__batch', 'offering__language', 'offering__course__grade')
                if len(booked_demadslot) > 0:
                    previous_booking['is_booked'] = True
                    previous_booking['slots'] = list(booked_demadslot)
                if has_role(self.request.user.userprofile, "Center Admin") or has_pref_role(self.request.user.userprofile, "Center Admin") or self.request.user.is_superuser:
                    is_book_for_others = True
            return render(self.request, 'demand_ft.html', {'flt_data': simplejson.dumps(data), 'user_details': user_details, 'previous_booking': simplejson.dumps(previous_booking, default=str), 'is_book_for_others': is_book_for_others})
        except Exception as e:
            logService.logException("FtDemand GET Exception error", e.message)
            return genUtility.error_404(request, e.message)

    # @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            subjects = requestParams.get('subjects', None)
            grades = requestParams.get('grades', None)
            days = requestParams.get('days', None)
            languages = requestParams.get('languages', None)
            board = requestParams.get('board', None)
            districts = requestParams.get('districts', None)
            startTime = requestParams.get('startTime', None)
            endTime = requestParams.get('endTime', None)
            now_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_ay = None
            centerobj = Center.objects.filter(language=languages)
            if centerobj:
                centerobj = centerobj[0]

            if centerobj:
                current_ay = get_object_or_none(Ayfy, start_date__year=datetime.datetime.now().year, board=centerobj.board)
                if not current_ay:
                    last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
                    current_ay = get_object_or_none(Ayfy, start_date__year=last_year, board=centerobj.board)
                        
            boardString = avoid_test_ceters = subjectString = gradesString = daysString = languagesString = demanday = startTimeString = endTimeString = center_language = ''

            if not request.user.is_superuser:
                avoid_test_ceters = ' AND web_center.is_test=0'
            if subjects is not None and len(subjects) > 0:
                subjectString = " AND web_course.subject = '{}'".format(str(subjects))
            if grades is not None and len(grades) > 0:
                gradesString = " AND web_course.grade = '{}'".format(str(grades))
            if board is not None and len(board) > 0:
                boardString = " AND web_course.board_name = '{}'".format(str(board))
            if days is not None and len(days) > 0:
                daysString = " AND web_demandslot.day in ('{}')".format("','".join(days))
            if languages is not None and len(languages) > 0:
                languagesString = " AND genutilities_language.name = '{}'".format(str(languages))
            if current_ay:
                demanday = " AND (web_demandslot.created_on >= '{}' OR web_demandslot.offering_id = web_offering.id)".format(str(current_ay.start_date).zfill(2))
            if startTime is not None and int(startTime) > 0:
                startTimeString = " AND web_demandslot.start_time >= '{}:00:00'".format(str(startTime).zfill(2))
            if endTime is not None and int(endTime) > 0:
                endTimeString = " AND web_demandslot.end_time <= '{}:00:00'".format(str(endTime).zfill(2))

            if request.user.is_authenticated():
                known_languages_json = UserProfile.objects.get(user=request.user).languages_known
                known_languages = [i['lang'] for i in ast.literal_eval(known_languages_json)]
                center_language = " AND web_center.language in ('{lang}')".format(lang="','".join(known_languages))

            conditionString = avoid_test_ceters + startTimeString + demanday+endTimeString + subjectString + gradesString + daysString + languagesString + center_language

            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'],
                                 passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True)
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query = "SELECT genutilities_pincode.pincode as centerPincode, web_offering.batch as batch, web_center.id as centerId, web_center.name as centerName, web_center.state as centerState, web_center.district as centerDistrict, web_center.board as centerBoard, web_course.id as courseId, web_course.subject, web_course.grade, web_course.board_name, genutilities_language.name as language,\
                    web_offering.id as offeringId, group_concat(web_demandslot.day, '--', concat(web_demandslot.id,'-',web_demandslot.start_time,'-',web_demandslot.end_time)) as slots \
                    FROM web_course INNER JOIN web_offering ON web_course.id = web_offering.course_id INNER JOIN web_center ON web_offering.center_id = web_center.id INNER JOIN web_demandslot ON web_center.id = web_demandslot.center_id AND (web_demandslot.offering_id is null OR web_demandslot.offering_id=web_offering.id) AND web_center.digital_school_id is not null \
                    INNER JOIN genutilities_language ON web_course.language_id = genutilities_language.id LEFT JOIN web_digitalschool_location_preference on web_digitalschool_location_preference.digital_school_id = web_center.digital_school_id LEFT JOIN genutilities_pincode ON genutilities_pincode.id  = web_digitalschool_location_preference.pincode_id \
                    WHERE  web_course.status = 'active' AND web_offering.active_teacher_id is null AND web_offering.status IN ('running', 'pending') AND web_demandslot.status = 'Unallocated' AND web_center.status != 'Closed' \
                    "+conditionString+"AND web_offering.end_date > '" + now_datetime + "' group by web_offering.id, (web_demandslot.start_time and web_demandslot.end_time)"
            users_cur.execute('SET SESSION group_concat_max_len = 999999')
            users_cur.execute(query)
            offering_demand = users_cur.fetchall()
            users_cur.close()
            db.close()

            for demand in offering_demand:
                dm = {}
                for slot in demand['slots'].split(','):
                    day = slot.split('--')[0]
                    slots = slot.split('--')[1]
                    if not dm.has_key(day):
                        dm[day] = []
                    slot_times = slots.split('-')
                    dm[day].append(
                        {'demandId': slot_times[0], 'startTime': slot_times[1], 'endTime': slot_times[2]})
                    dm[day] = [dict(t)
                               for t in {tuple(d.items()) for d in dm[day]}]
                demand['enrolledStudents'] = Offering_enrolled_students.objects.filter(
                    offering_id=demand['offeringId']).count()
                demand['slots'] = dm

            return genUtility.getSuccessApiResponse(request, offering_demand)
        except Exception as e:
            logService.logException("FtDemand POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


class BookFtDemand(View):

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            book_for_others = requestParams.get('book_for_others', None)
            teacher_id = requestParams.get('teacher_id', None)
            slot_data = requestParams.get('cart', None)
            teacher = None
            if not book_for_others:
                teacher = self.request.user
            else:
                if teacher_id is not None:
                    teacher = get_object_or_none(User, id=teacher_id)
                if teacher is None:
                    return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 1, User not exist.")

            user_role = get_object_or_none(RolePreference, userprofile=teacher.userprofile, role_id=20)
            if user_role is None:
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 1, User do not have role.")
            elif user_role.role_outcome != 'Recommended':
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 2, Please complete selection discution.")

            booked_demadslot = Demandslot.objects.filter(user=teacher, status='Booked')
            if len(booked_demadslot) > 0:
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 3, Release previous booked demand.")


            offeringId = slot_data[0].get('offeringId', None)
            if offeringId:
                offering = get_object_or_none(Offering, id=offeringId)
                lang = offering.center.language
                known_languages_json = UserProfile.objects.get(user=teacher).languages_known
                known_languages = [str(i['lang']) for i in ast.literal_eval(known_languages_json)]
                if lang not in known_languages:
                    return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 1, Teacher and center language mismatch.")

            center_wise = dict()
            for slots in slot_data:
                offeringId = slots.get('offeringId', None)
                demandId = slots.get('demandId', None)
                if offeringId is not None and demandId is not None:
                    offering = get_object_or_none(Offering, id=offeringId)
                    slot = get_object_or_none(Demandslot, id=demandId)
                else:
                    continue
                if offering and slot:
                    offering_teacher_mapping = OfferingTeacherMapping.objects.create(offering=offering, teacher=teacher,
                                                                                     booked_date=datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30),
                                                                                     created_by=request.user, updated_by=request.user)

                slot.offering = offering
                slot.status = 'Booked'
                slot.user = teacher
                slot.date_booked = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
                slot.save()

                dsmUser = genUtility.getActiveDSMForSchool(offering.center.digital_school.id)
                dsm_name = None
                dsm_email = None
                dsp_email = None
                if dsmUser:
                    dsm_name = dsmUser.get_full_name()
                    dsm_email = dsmUser.email if dsmUser.email else None
                if offering.center.digital_school_partner:
                    dsp_email = offering.center.digital_school_partner.contactperson.email if offering.center.digital_school_partner.contactperson.email else None

                mp = {'centerName': offering.center.name, 'state': offering.center.state, 'courseName': offering.course.subject, 'grade': offering.course.grade, 'state': offering.center.state,
                      'language': offering.course.language.name, 'dsm_name': dsm_name, 'dsm_email': dsm_email, 'dsp_email': dsp_email, 'ft_name': teacher.get_full_name(), 'ft_id': teacher.id}

                if center_wise.get(offering.center.name):
                    center_wise[offering.center.name].append(mp)
                else:
                    center_wise[offering.center.name] = [mp]

            for key, val in center_wise.items():
                mailParams = val
                to_mail = val[0]['dsm_email']
                cc = [teacher.email, val[0]['dsp_email']]
                if offering.center.admin: cc.append(offering.center.admin.email)
                state = val[0]['state']
                if state:
                    if len({state}.intersection({'Andhra Pradesh', 'Tamilnadu', 'Telangana'})) > 0:
                        cc.append(User.objects.get(id=46614).email)
                        cc.append(User.objects.get(id=59483).email)
                    if len({state}.intersection({'Karnataka'})) > 0:
                        cc.append(User.objects.get(id=19072).email)
                    if len({state}.intersection({'Bihar', 'UP', 'UK', 'JH', 'Haryana', 'Manipur'})) > 0:
                        cc.append(User.objects.get(id=46614).email)
                    if len({state}.intersection({'Maharashtra'})) > 0:
                        cc.append(User.objects.get(id=59486).email)
                if to_mail:
                    thread.start_new_thread(alert_dsm_for_demand_book, (request, [to_mail], cc, mailParams))

            return genUtility.getSuccessApiResponse(request, 'Success')
        except Exception as e:
            logService.logException("BookFtDemand POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest, 0, something went wrong.')

    @method_decorator(login_required)
    def put(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            slots = [int(x) for x in requestParams.get('selected', [])]
            user_slots = Demandslot.objects.filter(
                user=self.request.user, id__in=slots)
            for ent in user_slots:
                if ent.type == 1:
                    ent.offering_id = None
                ent.user_id = None
                ent.status = 'Unallocated'
                ent.date_booked = None
                try:
                    ent.save()
                except Exception:
                    logService.logException("BookFtDemand PUT Exception error", e.message)
            return genUtility.getSuccessApiResponse(request, 'kCustomErrorMsg, Demand Released.')
        except Exception as e:
            logService.logException("BookFtDemand PUT Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


class ContentDemand(View):

    def get(self, request,  *args, **kwargs):

        try:
            user_details = {'is_content_developer': None,
                            'profile_status': None, 'preferred_language': []}
            known_languages = []
            if request.user.is_authenticated():
                known_languages_json = UserProfile.objects.get(
                    user=request.user).languages_known
                known_languages = [i['lang']
                                   for i in ast.literal_eval(known_languages_json)]
                user_details = {
                    'is_content_developer': True if self.request.user.is_superuser else has_pref_role(request.user.userprofile, "Content Developer"),
                    'profile_status': True if request.user.userprofile.profile_completion_status else False,
                    'preferred_language': known_languages
                }
            subject = request.GET.get('subject', '')

            if request.user.is_authenticated() and not request.user.is_superuser and not has_pref_role(request.user.userprofile, "Content Admin"):
                contents = Content_Demand.objects.filter(status=1, topic__course_id__language__name__in=known_languages).values('id', 'topic__id', 'topic__title', 'topic__course_id__board_name',
                                                                                                                                'topic__course_id__subject', 'topic__course_id__grade', 'topic__course_id__language__name', 'subtopic__name', 'workstream__name', 'workstream__id')
            else:
                contents = Content_Demand.objects.filter(status=1).values('id', 'topic__id', 'topic__title', 'topic__course_id__board_name',
                                                                          'topic__course_id__subject', 'topic__course_id__grade', 'topic__course_id__language__name', 'subtopic__name', 'workstream__name', 'workstream__id')
            contents = self.groupby_multiple_keys(contents, ['topic__id', 'topic__course_id__board_name',
                                                  'topic__course_id__subject', 'topic__course_id__grade', 'workstream__name'], 'subtopic__name')

            # check previous booking
            previous_booking = {'is_booked': False}
            if self.request.user.is_authenticated():
                booked_demadslot = Content_Demand.objects.filter(author=self.request.user, status=2).values('id', 'topic__id',
                                                                                                            'topic__title', 'topic__course_id__board_name', 'topic__course_id__subject', 'topic__course_id__grade',
                                                                                                            'topic__course_id__language__name', 'subtopic__name', 'workstream__name', 'updated_on')
                if len(booked_demadslot) > 0:
                    previous_booking['is_booked'] = True
                    previous_booking['slots'] = list(booked_demadslot)

            return render(request, 'demand_content.html', {'pref_subject': subject, 'user_details': user_details, 'demand': list(contents), 'previous_booking': simplejson.dumps(previous_booking, default=str)})

        except Exception as e:
            logService.logException("ContentDemand GET Exception error", e.message)
            return genUtility.error_404(request, e.message)

    def groupby_multiple_keys(self, lst, groups, key):
        l = [list(y) for x, y in itertools.groupby(sorted(lst, key=lambda x: tuple(
            x[y] for y in groups)), lambda x: tuple(x[y] for y in groups))]
        return [{k: (v if k != key else list(set([x[key] for x in i]))) for k, v in i[0].items()} for i in l]

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            topic_id = requestParams.get('topic_id', None)
            grade = requestParams.get('grade', None)
            subject = requestParams.get('subject', None)
            workstream_id = requestParams.get('workstream_id', None)
            author_id = requestParams.get('author_id', None)

            author = request.user
            if author_id is not None:
                author = get_object_or_none(User, id=author_id)
            if author is None:
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 1, User not exist.")

            user_role = get_object_or_none(
                RolePreference, userprofile=author.userprofile, role_id=3)
            if user_role is None:
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 1, User do not have role.")
            # elif user_role.role_outcome != 'Recommended': return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 2, Please complete selection discution.")

            booked_demadslot = Content_Demand.objects.filter(
                author=author, status__in=[2, 3])
            if len(booked_demadslot) > 0:
                return genUtility.getStandardErrorResponse(request, "kCustomErrorMsg, 2, Please complete your previous booking.")
            demand = Content_Demand.objects.filter(
                topic__id=topic_id, topic__course_id__subject=subject, topic__course_id__grade=grade, workstream__id=workstream_id)
            demand.update(author=author, status=2)
            username = author.get_full_name()
            to = [author.email]
            cc = []
            admin = AlertUser.objects.get(role__name='vol_admin')
            if admin: cc.extend([user.email for user in admin.user.all()])
            demand = demand[0]
            args = {'username': username,
                    'topic_name': demand.topic.title,
                    'workstream': demand.workstream.name,
                    'grade': demand.topic.course_id.grade,
                    'subject': demand.topic.course_id.subject,
                    'board': demand.topic.course_id.board_name
                    }
            body_template = 'mail/content/book.txt'
            body = genUtility.get_mail_content(body_template, args)
            try:
                thread.start_new_thread(
                    genUtility.send_mail_thread, ("Your content has been booked", body, settings.DEFAULT_FROM_EMAIL, to, cc))
            except Exception as e: logService.logException("ContentDemandBook email Exception error", e.message)

            return genUtility.getSuccessApiResponse(self.request, 'Success')
        except Exception as e:
            logService.logException("ContentDemand POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')

    @method_decorator(login_required)
    def put(self, request,  *args, **kwargs):
        try:
            demands = Content_Demand.objects.filter(author=request.user, status=2)
            username = request.user.get_full_name()
            to = [request.user.email]
            cc = []
            content_admins = AlertUser.objects.filter(role__name='vol_admin')
            content_admins = content_admins[0].user.all()
            if content_admins:
                cc.extend([user.email for user in content_admins])
            demand = demands[0]
            args = {'username': username,
                    'topic_name': demand.topic.title,
                    'workstream': demand.workstream.name,
                    'grade': demand.topic.course_id.grade,
                    'subject': demand.topic.course_id.subject,
                    'board': demand.topic.course_id.board_name,
                    'language': demand.topic.course_id.language.name
                    }
            demands.update(author=None, status=1)
            body_template = 'mail/content/release_booking.txt'
            body = genUtility.get_mail_content(body_template, args)
            try:
                thread.start_new_thread(
                    genUtility.send_mail_thread, ("Your content has been released", body, settings.DEFAULT_FROM_EMAIL, to, cc))
            except Exception as e: logService.logException("ContentRelease email Exception error", e.message)
            return genUtility.getSuccessApiResponse(self.request, 'Success')
        except Exception as e:
            logService.logException("ContentDemand PUT Exception error", e.message)
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')






class ContentReviewCheckList(View):

    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            content_demand_id = self.request.GET.get('content_demand_id', None)
            workstream_id = self.request.GET.get('workstream_id', None)
            context = {'exist': False,
                       'content_demand_id': content_demand_id, 'checks': []}
            sbd = get_object_or_none(Content_Demand, id=int(content_demand_id))
            pre_comments = []
            if sbd:
                pre_comments = Content_Demand_Checklist_Comments.objects.filter(content_demand=sbd).values(
                    'id', 'content_demand_id', 'checklist__id', 'checklist__checklist', 'answers', 'comments')
            if len(pre_comments) > 0:
                context['exist'] = True
                context['comment'] = sbd.comment
                context['checks'] = [{'id': x['id'], 'checklist_id':x['checklist__id'], 'checklist':x['checklist__checklist'],
                                      'check_comment':x['comments'], 'answers':x['answers']} for x in pre_comments]

            else:
                new_comments = Content_Demand_Review_Checklist.objects.filter(
                    workstream__id=int(workstream_id)).values()
                if new_comments:
                    context['checks'] = [{'id': None, 'checklist_id': x['id'], 'checklist':x['checklist'],
                                          'check_comment':'', 'answers':1, 'comment':sbd.comment} for x in new_comments]

            return HttpResponse(simplejson.dumps(context), mimetype='application/json')
        except Exception as e:
            logService.logException("ContentReviewCheckList GET Exception error", e.message)
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            is_checklist_given = requestParams.get('is_checklist_given', None)
            content_demand_id = requestParams.get('content_demand_id', None)
            response = requestParams.get('response', None)
            checklist_data = requestParams.get('checklist_data', None)
            comment = requestParams.get('comment', None)
            sbd = get_object_or_none(Content_Demand, id=int(content_demand_id))
            if comment:
                sbd.comment = comment
                sbd.status = int(response)
                sbd.save()
            if is_checklist_given:
                for check in checklist_data:
                    Content_Demand_Checklist_Comments.objects.filter(id=check['id']).update(
                        answers=check['check'], comments=check['note'])
            else:
                for check in checklist_data:
                    Content_Demand_Checklist_Comments.objects.create(content_demand=sbd, checklist_id=int(check['checklist_id']),
                                                                     answers=check['check'], comments=check['note'])

            username = request.user.get_full_name()
            to = [sbd.author.email]
            cc = [request.user.email]
            content_admins = AlertUser.objects.filter(role__name='vol_admin')
            content_admins = content_admins[0].user.all()
            if content_admins:
                cc.extend([user.email for user in content_admins])
            
            demand = sbd
            args = {'username': username,
                    'topic_name': demand.topic.title,
                    'workstream': demand.workstream.name,
                    'grade': demand.topic.course_id.grade,
                    'subject': demand.topic.course_id.subject,
                    'board': demand.topic.course_id.board_name,
                    'language': demand.topic.course_id.language.name
                    }
            if response == 7:
                body_template = 'mail/content/resubmit.txt'
            else:
                body_template = 'mail/content/approve.txt'

            body = genUtility.get_mail_content(body_template, args)
            try:
                thread.start_new_thread(
                    genUtility.send_mail_thread, ("Your content has been released", body, settings.DEFAULT_FROM_EMAIL, to, cc))
            except Exception as e:logService.logException("ContentReviewCheckList email Exception error", e.message)

            return genUtility.getSuccessApiResponse(self.request, 'Success')
        except Exception as e:
            logService.logException("ContentReviewCheckList POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')


def contentreview(request):
    try:
        content_demand_id = request.GET.get('content_demand_id', None)
        workstream_id = request.GET.get('workstream_id', None)
        context = {'exist': False, 'checks': []}

        pre_comments = Content_Demand_Checklist_Comments.objects.filter(
            content_demand_id=int(content_demand_id))
        if pre_comments:
            context['exist'] = True
            context['checks'] = list(pre_comments.values())

        else:
            new_comments = Content_Demand_Review_Checklist.objects.filter(
                workstream__id=int(workstream_id)).values()
            if new_comments:
                context['checks'] = list(new_comments.values())

        return HttpResponse(simplejson.dumps({}), mimetype='application/json')
    except Exception as e:
        logService.logException("contentreviews GET Exception error", e.message)
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')



class StatsDemand(View):
    
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            is_partner = False
            if request.user.partner_set.values():
                is_partner = True
            
            centerObj = getAllCenters(request)
            centers_all = centerObj.exclude(state__isnull=True).exclude(state__exact='').exclude(is_test=1)
            states_all = centers_all.values_list('state',flat=True).distinct().order_by('state')
            partners_list = centers_all.values('delivery_partner_id',"delivery_partner__name_of_organization").distinct()
            del_coordinator_list = centers_all.values('delivery_coordinator_id','delivery_coordinator__first_name','delivery_coordinator__last_name').distinct()
            partner = get_object_or_none(Partner, contactperson=request.user)
            is_funding_partner = False
            if partner:
                is_funding_partner = Partner.objects.filter(contactperson=request.user,partnertype=3)
                if is_funding_partner:
                        is_funding_partner= True

            ayfys_titles = Ayfy.objects.filter(board__isnull = False, types='Academic Year').values_list('title', flat=True).order_by('-id')
            unique = []
            [unique.append(item) for item in ayfys_titles if item not in unique]
            context = {'partner':partner,'is_partner':is_partner,'is_funding_partner':is_funding_partner, 'state':states_all, 
                       'partners_list':partners_list,'center':centers_all, 'del_coordinator_list':del_coordinator_list,
                        'ayfys_titles':unique}
            return render(request,'demand_dash.html', context)
        
        except Exception as e:
            logService.logException("ContentDemand GET Exception error", e.message)
            return genUtility.error_404(request, e.message)
    
    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            
            request_params = request.POST
            state = center = delivery_partner = delivery_coordinator = from_date = to_date = avoid_test_ceters = ''
            ay = Ayfy.objects.all()[0].title
            
            if not request.user.is_superuser:
                avoid_test_ceters = ' AND center.is_test=0'
            
            if request_params.get('ay', ay):
                ay=" ay.title = '{ay}'".format(ay=request_params.get('ay', ay))  
            if request_params.get('states') != 'All':
                state=" AND center.state = '{}'".format(request_params.get('states'))
            if request_params.get('centers') != 'All':
                center=" AND center.id = '{}'".format(request_params.get('centers'))
            if request_params.get('partners') != 'All':
                delivery_partner=" AND center.delivery_partner_id = '{}'".format(request_params.get('partners'))
            if request_params.get('delivery') != 'All':
                delivery_coordinator=" AND center.delivery_coordinator_id = '{}'".format(request_params.get('delivery'))
            if request_params.get('from'):
                from_date =" AND web_demandslot.updated_on >= '{}'".format(request_params.get('from'))
            if request_params.get('to'):
                to_date=" AND web_demandslot.updated_on <= '{}'".format(request_params.get('to'))

            
                
            filters = ay + state + center + delivery_partner + delivery_coordinator + from_date + to_date + avoid_test_ceters
            
            query = '''SELECT off.id, course.board_name, course.grade, course.subject, off.language, center.name , off.status, user.id userId, 
                        user.first_name, user.last_name, user.email, web_userprofile.phone, web_demandslot.date_booked, web_session.date_start as first_session, 
                        om.assigned_date as assigned_date, web_demandslot.status as demand_status, center.program_type 
                        FROM evldb.web_offering off
                        inner join web_ayfy ay on  off.academic_year_id = ay.id
                        inner join web_course course on course.id = off.course_id
                        inner join web_center center on center.id = off.center_id
                        LEFT JOIN web_offeringteachermapping om on om.offering_id = off.id and om.assigned_date is not null
                        left JOIN auth_user user on user.id = off.active_teacher_id
                        left join web_userprofile on web_userprofile.user_id = user.id
                        left join web_demandslot on web_demandslot.offering_id = off.id
                        left join web_session on web_session.offering_id = off.id and web_session.status = 'completed'
                        where {fil}
                        group by off.id
                        order by -off.id
                        
                        
                        '''.format(fil = filters)

            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'],
                                 passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True)
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)
            users_cur.execute('SET SESSION group_concat_max_len = 999999')
            users_cur.execute(query)
            data = users_cur.fetchall()
            users_cur.close()
            db.close()

            print(query)
            
            return HttpResponse(simplejson.dumps(data, default=str), mimetype = 'application/json')
        except Exception as e:
            traceback.print_exc()
            logService.logException("OfferingReport POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')


class PublishBookingSlots(View):
    
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        print("Am here")
        try:
            # Copy paste of old publish booking slots code
            api = request.GET.get("api", "false") == "true"

            is_panelmember = False
            ref = ReferenceChannel.objects.get(id = request.user.userprofile.referencechannel.id)
            partner = None
            without_partner = False
            if has_role(request.user.userprofile, "TSD Panel Member") or has_pref_role(request.user.userprofile,"TSD Panel Member"):
                is_panelmember = True
            if is_panelmember and not request.user.is_superuser:
                publish_slots = SelectionDiscussionSlot.objects.values('start_time', 'end_time', 'status','id','publisher_role_id').filter(tsd_panel_member = request.user.userprofile).order_by('-start_time')
            elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
                if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
                    partner = Partner.objects.get(contactperson = request.user)
                else:
                    partner = ref.partner
                if partner and len(partner.partnertype.filter(name = 'Delivery Partner')) > 0:
                    publish_slots = SelectionDiscussionSlot.objects.values('start_time', 'end_time', 'status','id','publisher_role_id').filter(tsd_panel_member__referencechannel__partner = partner).order_by('-start_time')
                else:
                    without_partner = False

            if without_partner or request.user.is_superuser or ref is None:
                publish_slots = SelectionDiscussionSlot.objects.values('start_time', 'end_time', 'status','id','publisher_role_id').order_by('-start_time')

            publish_slots_list = []
            for publish_slot in publish_slots:
                publish_slot['start_time'] = datetime.datetime.strftime(publish_slot['start_time'], '%b %d %Y %I:%M%p')
                publish_slot['end_time'] = datetime.time.strftime(publish_slot['end_time'], '%I:%M%p')
                publish_slots_list.append({"start_date": publish_slot['start_time'].rsplit(' ', 1)[0],
                                        "start_time": publish_slot['start_time'].rsplit(' ', 1)[1], \
                                        "end_time": publish_slot['end_time'],"role": str(publish_slot['publisher_role_id']), "status": publish_slot['status'],"id": publish_slot['id']})
            
            if api:
                return HttpResponse(simplejson.dumps(publish_slots_list), mimetype='application/json')
            return render_to_response('publish_booking_slots.html', {
                "request": request,
                'dbg': simplejson.dumps(publish_slots_list),
                'publish_slots': publish_slots_list,
                'days': ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            })

        except Exception as e:
            print("GET Exception  e", e); traceback.print_exc()
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')
    
    @method_decorator(login_required)
    def delete(self, request, *args, **kwargs):
        try:
            slot_list = request.GET.get('slots').split(",")
            for id in slot_list:
                slot_to_del = SelectionDiscussionSlot.objects.get(pk = int(id))
                slot_to_del.delete()
            return HttpResponse("OK")
        except ObjectDoesNotExist as de:
            print("ObjectDoesNotExist Exception  e", de); traceback.print_exc()
            return HttpResponseNotFound("404")
        except Exception as e:
            print("GET Exception  e", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        slots_to_publish = simplejson.loads(request.body)

        try:
            startdate = datetime.datetime.strptime(slots_to_publish["start_date"], '%Y-%m-%d')
            enddate = datetime.datetime.strptime(slots_to_publish["end_date"], '%Y-%m-%d')
            days = slots_to_publish["days"]
            slot_count = slots_to_publish["slots_counts"]
            group_slots = slots_to_publish["group_slots"]
            delta = enddate - startdate
        except Exception as e:
            print("POST Exception  e", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')

        added_count = 0
        duplicate_count = 0
        role_id =''
        print("slot_count:", slot_count)
        starttime = datetime.datetime.strptime(slots_to_publish["start_time"], "%I:%M%p")
        endtime = datetime.datetime.strptime(slots_to_publish["end_time"], "%I:%M%p")
        is_panelmember = False
        if has_role(request.user.userprofile, "TSD Panel Member") or has_pref_role(request.user.userprofile,
                                                                                "TSD Panel Member"):
            is_panelmember = True
            role_id = '7'
        if has_role(request.user.userprofile, "CSD Panel Member") or has_pref_role(request.user.userprofile,
                                                                                "CSD Panel Member"):
            is_csdpanelmember = True
            role_id = '17'

        startdate = startdate.replace(hour=starttime.time().hour, minute=starttime.time().minute)

        current_year = datetime.datetime.now()

        if startdate.year not in (current_year.year, current_year.year + 1):
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')
        if enddate.year not in (current_year.year, current_year.year + 1):
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')

        if group_slots:
            tot_slots = int(((endtime - starttime).total_seconds() / 60) / 60)
        else:
            tot_slots = int(((endtime - starttime).total_seconds() / 60) / 30)
        if startdate.date() == enddate.date():
            i = 0
            start = startdate
            
            while i < tot_slots:
                if group_slots:
                    slot_end = start + timedelta(minutes=60)
                else:
                    slot_end = start + timedelta(minutes=30)
                i = i + 1
                try:
                    for slot in range(0,int(slot_count)):
                        if is_panelmember or is_csdpanelmember:
                        
                            new_slot = SelectionDiscussionSlot(start_time=start, end_time=slot_end.time(),publisher_role_id=role_id,
                                                        tsd_panel_member=request.user.userprofile, outcome = 'Assigned', added_by=request.user)
                            new_slot.save()
                            added_count = added_count+1
                        else:
                            new_slot = SelectionDiscussionSlot(start_time=start, end_time=slot_end.time(), added_by=request.user)
                            new_slot.save()
                            added_count = added_count+1
                except:
                    traceback.print_exc()
                    duplicate_count = 1
                start = slot_end
        else:
            for single_date in daterange(startdate, enddate):
                if single_date.strftime("%A") in days:
                    i = 0
                    start = single_date.replace(hour=starttime.time().hour, minute=starttime.time().minute)
                    while i < tot_slots:
                        if group_slots:
                            slot_end = start + timedelta(minutes=60)
                        else:
                            slot_end = start + timedelta(minutes=30)
                        i = i + 1
                        try:
                            for slot in range(0,int(slot_count)):
                                if is_panelmember or is_csdpanelmember:
                                    new_slot = SelectionDiscussionSlot(tsd_panel_member=request.user.userprofile,outcome = 'Assigned',publisher_role_id=role_id,
                                                                    start_time=start, end_time=slot_end.time())
                                    new_slot.save()
                                    added_count = added_count + 1
                                else:
                                    new_slot = SelectionDiscussionSlot(start_time=start, end_time=slot_end.time())
                                    new_slot.save()
                                    added_count = added_count + 1
                        except:
                            import traceback
                            traceback.print_exc()
                            duplicate_count = duplicate_count + 1
                        start = slot_end

        return HttpResponse(simplejson.dumps({"added": added_count, "duplicate": duplicate_count}), content_type="application/json")



class ActivityTypes(View):
    @staticmethod
    def has_special_char(text):
        return any(c for c in text if not c.isalnum() and not c.isspace())

    @method_decorator(login_required)
    def delete(self, request,  *args, **kwargs):
        can_edit = False
        if has_role(request.user.userprofile, "Center Admin") or has_pref_role(request.user.userprofile, "Center Admin") or request.user.is_superuser:
            can_edit = True
        
        if not can_edit:
            return genUtility.getStandardErrorResponse(request, "You are not authorized to perform this action.")
        
        try:
            id = int(request.GET.get('id'))

            filter = CenterActivityType.objects.filter(id=id)

            for activity in filter:
                activity.delete()
            return genUtility.getSuccessApiResponse(request, 'Success')
        except:
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        can_edit = False
        if has_role(request.user.userprofile, "Center Admin") or has_pref_role(request.user.userprofile, "Center Admin") or request.user.is_superuser:
            can_edit = True
        
        if not can_edit:
            return genUtility.getStandardErrorResponse(request, "You are not authorized to perform this action.")

        try:
            body = json.loads(request.body)
        except:
            print("ActivityType Exception", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')
        
        try:
            # First check inputs
            for inp in body["inputs"]:
                if ActivityTypes.has_special_char(inp["name"]) or inp["name"].lower() == "other":
                    return genUtility.getStandardErrorResponse(request, 'Input name should not contain special characters or be "other".')
                if inp["type"] not in ("text", "number", "date"):
                    return genUtility.getStandardErrorResponse(request, 'Invalid input type.')

            if not body["name"].replace(" ", ""):
                return genUtility.getStandardErrorResponse(request, 'Activity name should not be empty.')

            activity_type = CenterActivityType.objects.filter(activity_type=body["name"])
            if len(activity_type) > 0:
                return genUtility.getStandardErrorResponse(request, 'Activity type already exists.')
            activity_type = CenterActivityType.objects.create(activity_type=body["name"], created_by=request.user, updated_by=request.user)

            for inp in body["inputs"]:
                CenterActivityTypeForm.objects.create(activity_type=activity_type, label=inp["name"], type=inp["type"], created_by=request.user, updated_by=request.user)

            return genUtility.getSuccessApiResponse(request, 'Success')
        except Exception as e:
            print("ActivityType Exception", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

class ActivitySystem(View):
    def to_json(self, s):
        flag = True
        while flag:
            if not isinstance(s, dict) and not isinstance(s, list):
                s = simplejson.loads(s)
            else:
                flag = False
        return s

    def to_form(self, activity_json):
        """Activity type is a str"""
        html = []

        id_map = {"other": "other"}

        id_name_map = {}

        select_activity = """
            <div class="form-group">
                <label>Select an activity</label>
                <span id="act-id" class="hidden"></span>
                <br/>
                <select id="act-activities" onchange="showOtherPopup()">
        """

        for activity_type in activity_json:
            activity_json = CenterActivityTypeForm.objects.filter(activity_type=activity_type)

            # Patch for login
            flag = False

            act_type_id = activity_type.activity_type.lower().replace(" ", "").replace("/", "-")

            id_map[act_type_id] = []

            id_name_map[act_type_id] = activity_type.activity_type

            select_activity += """
                <option value="{id}" id="{id}">{label}</option>
            """.format(id=act_type_id, label=activity_type.activity_type)

            html_c = """
                <div id="{id}-div" class="activity-specific" style="display: none">
            """.format(id=act_type_id)

            for activity in activity_json:
                print(activity)
                if not activity.type:
                    activity.type = "text"
                                
                id_map[act_type_id].append(activity.label.replace("/", "-").replace(" ", "-") + "-" + act_type_id)

                choices = []
                if activity.choices:
                    try:
                        choices = json.loads(activity.choices)
                    except:
                        choices = []

                if choices:
                    html_c += """
                    <div id="{id}" class="form-group">
                        <label>{label}</label>
                        <br/>
                        <select name="{id}-s" id="{id}-{act_type_id}">
                    """.format(
                        id=activity.label.replace(" ", "-").replace("/", "-"),
                        label=activity.label,
                        act_type_id=act_type_id
                    )
                    for choice in choices:
                        html_c += """
                        <option value="{choice}">{choice}</option>
                        """.format(choice=choice)
                    html_c += """
                        </select>
                        <br/>
                    </div>
                    """
                else:
                    html_c += """
                    <div id="{id}" class="form-group">
                        <label>{label}</label>
                        <br/>
                        <input type="{type}" id="{id}-{act_type_id}" />
                        <br/>
                    </div>
                    """.format(
                        id=activity.label.replace(" ", "-").replace("/", "-"),
                        label=activity.label,
                        type=activity.type,
                        act_type_id=act_type_id
                    )
            html.append(html_c + "</div>")
        
        select_activity += """
                </select>
                <br/>
            </div>
        """

        return {
            "id_map": simplejson.dumps(id_map),
            "html": "".join(html),
            "activity_select": select_activity,
            "id_name_map": simplejson.dumps(id_name_map)
        }

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        can_edit = False
        if has_role(request.user.userprofile, "Center Admin") or has_pref_role(request.user.userprofile, "Center Admin") or request.user.is_superuser:
            can_edit = True

        try:
            activity_form = CenterActivityType.objects.filter()

            activities = CenterActivity.objects.filter(center=request.GET.get("center"))
            activity_json = []
            for act in activities:
                print("here")
                imgs = CenterActivityImage.objects.filter(activity=act)
                img_json = []
                for img in imgs:
                    img_json.append({
                        "filename": img.image.file_name,
                        "url": img.image.url
                    })
                try:
                    date = act.activity_date.strftime("%d-%m-%Y") if act.activity_date else "Unknown"
                    date_browser = act.activity_date.strftime("%Y-%m-%d") if act.activity_date else datetime.datetime.now().strftime("%Y-%m-%d")
                except Exception as exc:
                    print(exc)
                    date = "Invalid date: {}".format(act.activity_date)
                    date_browser = datetime.datetime.now().strftime("%Y-%m-%d")
                
                values = self.to_json(act.values)

                if not isinstance(values, dict):
                    values = {}
                
                values_fixed = {}
                
                for key in values.keys():
                    values_fixed[key.strip()] = values[key]

                add = {
                    "id":act.id, 
                    "user": act.user.username, 
                    "comment": act.comment.replace("\n", "<br/>").replace("\r", "<br/>"), 
                    "activity": act.activity.activity_type,
                    "activity_type_parsed": act.activity.activity_type.replace(" ", "").lower(),
                    "status": act.status, 
                    "created_on": act.created_on.strftime("%d-%m-%Y"), 
		            "date": date,
                    "date_browser": date_browser,
                    "imgs": img_json,
                    "values": values_fixed
                }
                add["json"] = simplejson.dumps(add)
                activity_json.append(add)                
        except Exception as e:
            print("POST Exception  e", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')
        
        if request.GET.get("json") in ("true", "1"):
            return HttpResponse(simplejson.dumps({"data": activity_json}), content_type="application/json")

        acts = []

        for type in activity_form:
            form = CenterActivityTypeForm.objects.filter(activity_type=type)
            if not form:
                form = []
            acts.append({
                "type": type,
                "form": form
            })

        try:
            return render_response(request, 'center_activities.html', {
                "request": request, 
                "can_edit": can_edit, 
                "center_id": request.GET.get("center"), 
                'data': activity_json, 
                "activity_form": self.to_form(activity_form),
                "activity_types": acts,
		"date": datetime.datetime.now().strftime("%Y-%m-%d")
            })
        except Exception as e:
            print("POST Exception  e", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')
    
    @method_decorator(login_required)
    def delete(self, request, *args, **kwargs):
        can_edit = False
        if has_role(request.user.userprofile, "Center Admin") or has_pref_role(request.user.userprofile, "Center Admin") or request.user.is_superuser:
            can_edit = True

        if not can_edit:
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')

        try:
            id = int(request.GET.get("id"))  	
            act_to_del = CenterActivity.objects.get(id = id)
            if act_to_del:
                act_to_del.delete()
            else:
                return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')
            return genUtility.getSuccessApiResponse(self.request, 'Success')
        except Exception as e:
            print("POST Exception  e", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        activity = {
            "center_id": request.POST.get("center_id"),
            "activity": request.POST.get("activity"),
            "comments": request.POST.get("comments", "").replace("<", "&lt").replace(">", "&gt"),
            "date": request.POST.get("date")
        }

        can_edit = False
        if has_role(request.user.userprofile, "Center Admin") or has_pref_role(request.user.userprofile, "Center Admin") or request.user.is_superuser:
            can_edit = True


        print(activity, "can_edit=", can_edit)
        
        if self.request.GET.get('format', None) and self.request.GET.get('format', None) != "-1":
            try:
                intFormat = self.request.GET.get('format', None)        # png,jpg,pdf,doc,docx,jpeg
                intDocType = self.request.GET.get('doc_type', None)     # school_logo,school_banner,student_doubt etc
                if intFormat is None or intDocType is None:
                    return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')
                cloudFolderName = settings.CENTER_ACTIVITIES_STORAGE_FOLDER
                id = docUploadService.upload_user_document_s3(request, "teacher", None, cloudFolderName, None, "obj")
            except Exception as e:
                return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')
        else:
            id = None

        if len(activity["comments"]) > 2048:
            return genUtility.getStandardErrorResponse(self.request, 'kCustomErrorMsg, Comments should not be more than 2048 characters.')

        try:
            activity["date"] = dparser.parse(activity["date"])
        except Exception as e:
            return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')

        if activity["date"] > datetime.datetime.now():
            return genUtility.getStandardErrorResponse(self.request, 'kCustomErrorMsg, Date above current date.')	

        center = Center.objects.get(id=activity["center_id"])

        if not center:
            return genUtility.getStandardErrorResponse(self.request, 'kCustomErrorMsg, Center not found.')

        try:
            if request.POST.get("update"):
                if not can_edit:
                    return genUtility.getStandardErrorResponse(self.request, 'kCustomErrorMsg, You are not authorized to update this activity.')
                old_act = CenterActivity.objects.get(id=int(request.POST.get("update_id")))
                if not old_act:
                    return genUtility.getStandardErrorResponse(self.request, 'kCustomErrorMsg, Activity.')
                
                old_act.comment = activity["comments"]
                old_act.activity = CenterActivityType.objects.get(activity_type=activity["activity"])
                old_act.activity_date = activity["date"]
                if request.POST.get("ext_data"):
                    old_act.values = request.POST.get("ext_data")
                
                old_act.save()

                images = CenterActivityImage.objects.filter(activity=old_act)

                print(images)
                if request.POST.get("clear-img") == "true":
                    for img in images:
                        img.delete()

                if id:
                    img = CenterActivityImage(
                        activity=old_act,
                        image=id,
                        created_by=request.user
                    )
                    img.save()
            else: 
                act = CenterActivity(
                    center=center,
                    user=request.user,
                    comment=activity["comments"],
                    activity=CenterActivityType.objects.get(activity_type=activity["activity"]),
                    activity_date=activity["date"],
                    values=request.POST.get("ext_data")
                )
                act.save()
                if id:
                    img = CenterActivityImage(
                        activity=act,
                        image=id,
                        created_by=request.user
                    )
                    img.save()
        except Exception as e:
            print("POST Exception  e", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')
        
        return genUtility.getSuccessApiResponse(self.request, 'Success')

