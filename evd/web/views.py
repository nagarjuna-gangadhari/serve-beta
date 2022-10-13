from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.contrib.auth.models import User
from django.db.models import signals, Q, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core import serializers
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from templatetags.tags import crop, thumbnail
from django.utils.datetime_safe import strftime
from django.utils.http import int_to_base36
from django.contrib.auth.models import *
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.db.models.fields.files import FieldFile
import ast
# from django.http import Http404
from django.shortcuts import render
from django.conf import settings
import math
from django import http
from django.template import Context, loader
from django import template
from django.core import mail
from django.core.mail import send_mail, BadHeaderError
from django.core.mail import EmailMessage
from collections import Iterable
from django.forms.models import model_to_dict
from django.db.models import Avg, Max, Min, Sum
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa as new_pisa
from django.template.loader import render_to_string
from django.shortcuts import render as render_response
import operator
import simplejson
import notification.models as notification
import notification.views as notification
import datetime
import time
import traceback
# import Image as PIL
from PIL import Image as PIL
import xlwt
from xlwt import Workbook
import json
from dateutil import parser
from datetime import timedelta
from dateutil import tz
import MySQLdb
import calendar

import os
import zipfile
import re
import json
import requests
import StringIO as StringIO
import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from cgi import escape
from copy import deepcopy
from collections import OrderedDict

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from models import *
from signals import *
from registration.signals import user_activated
from django.core.mail import EmailMultiAlternatives
from django.template import Template

from dateutil.relativedelta import relativedelta
from django.utils.safestring import mark_safe
import xlrd
import collections
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tempfile
import urllib2
import urllib

from web.teachersday2016_data import *

import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from social_auth.models import UserSocialAuth
from web.models import Task
from configs.models import AppreciationReason, Stickers
from webext.models import Recognition, TeachingSoftwareDetails

from student.models import Quiz_History, Quiz_History_Detail

from django.db.models import Q

import requests

from partner.views import profile as partner_profile
from partner.views import deliverypartner_org, organization_details
import base64
from unicodedata import category
from web.utils import *
#from IPython.lib.tests.test_pretty import MyObj
from ast import literal_eval
from configs.views import has_mail_receive_accepted
import httplib
import thread

from threading import Thread

# HANGOUT MEETING GENERATION
import pickle
import os.path
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from multiprocessing import Process
from django.views.generic import View
from django.utils.decorators import method_decorator
from partner.views import deliverypartner_org, organization_details, create_school_api
from genutilities.uploadDocumentService import upload_user_document_s3
import genutilities.views as genUtility
import genutilities.logUtility as logService
from genutilities.views import has_role_preference


SCOPES = ['https://www.googleapis.com/auth/calendar']

# *****************************

WIKI_BASE_URL = 'http://wikividya.evidyaloka.org/'
WIKI_FAILURE_MESSAGE = 'Failure_wiki'
WIKI_PASS = '123'
WEB_BASE_URL = settings.WEB_BASE_URL

VALIDATE_PHONE_RE = '^(\\+91[\\-\\s]?)?[0]?(91)?[6789]\\d{9}$'


# If modifying these scopes, delete your previously saved credentials
CLIENT_SECRET_FILE = '/web/client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Webhook'


# HANGOUT MEETING API
def hangout_api_init():
    calendar_service = None
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    with open(os.getcwd() + '/web/token.pickle', 'rb') as token:
        log_error_messages("Token file read")
        try:
            creds = pickle.load(token)
        except Exception as exp:
            log_error_messages("EXCEPTION: " + str(exp))

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                log_error_messages("Credentials Expired, refreshing")
                creds.refresh(Request())
                log_error_messages("Credentials refreshed")
            else:
                log_error_messages("Manual Authentication Required")
                flow = InstalledAppFlow.from_client_secrets_file(os.getcwd() + CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_console()
        except Exception as exp:
            log_error_messages("EXCEPTION: " + str(exp))

        # Save the credentials for the next run
        with open(os.getcwd() + '/web/token.pickle', 'wb') as token:
            log_error_messages("Saving to token file")
            try:
                pickle.dump(creds, token)
            except Exception as exp:
                log_error_messages("EXCEPTION: " + str(exp))

    calendar_service = build('calendar', 'v3', credentials=creds)

    return calendar_service


def log_error_messages(msg):
    with open(os.getcwd() + "/web/meeting_creation_status_log.log", "a") as output_file:
        cur_date = str(datetime.datetime.now())
        output_file.write(cur_date + " : " + msg + "\n")


def meeting_creation_job(days, timings, start_date, end_date, offering_id, teacher_id):
    log_error_messages("MILESTONE: meeting_creation_job START")
    calendar_service = hangout_api_init()
    meet_id_testing = []

    try:
        day_now = datetime.datetime.now().date()
        class_days = days.upper().split(";")
        class_days = [each[:2] for each in class_days]
        class_timings = timings.split(";")

        log_error_messages("DEBUG: Class Days " + str(class_days))
        log_error_messages("DEBUG: Class Timings " + str(class_timings))

        temp = start_date.split("-")
        if len(temp[0]) < 2:
            temp[0] = "0" + temp[0]
        if len(temp[1]) < 2:
            temp[1] = "0" + temp[1]
        class_start_date = "{}-{}-{}".format(temp[-1], temp[1], temp[0])

        temp = end_date.split("-")
        if len(temp[0]) < 2:
            temp[0] = "0" + temp[0]
        if len(temp[1]) < 2:
            temp[1] = "0" + temp[1]
        class_end_date = "{}-{}-{}".format(temp[-1], temp[1], temp[0])

        recipients = []
        db_offer = Offering.objects.get(id=offering_id)
        db_center = Center.objects.get(id=db_offer.center.id)

        if teacher_id != "" and teacher_id is not None:
            try:
                db_user = User.objects.get(id=teacher_id)
            except Exception:
                pass
            else:
                recipients.append({'email': db_user.email})

        if db_center.delivery_coordinator:
            try:
                db_user = User.objects.get(id=db_center.delivery_coordinator)
            except Exception:
                pass
            else:
                recipients.append({'email': db_user.email})

        if db_center.field_coordinator:
            try:
                db_user = User.objects.get(id=db_center.field_coordinator)
            except Exception:
                pass
            else:
                recipients.append({'email': db_user.email})

        if db_center.assistant_id:
            try:
                db_user = User.objects.get(id=db_center.assistant_id)
            except Exception:
                pass
            else:
                recipients.append({'email': db_user.email})

        if class_timings[0] == class_timings[1]:
            log_error_messages("DEBUG: Both days timings are same")
            event = create_event_dict(class_timings[0], ",".join(class_days), class_start_date, class_end_date)
            event['attendees'] = recipients
            event['summary'] = "{}th {} Class for {}".format(db_offer.course.grade, db_offer.course.subject, db_center.name)

            hangout_links = []
            clevent = calendar_service.events().insert(calendarId='primary', body=event).execute()
            if clevent['status'] == 'confirmed':
                hangout_links.append(get_hangout_event_details(clevent))
                meet_id_testing.append(get_hangout_event_details(clevent))
                log_error_messages("SUCCESS: Event creation completed" + str(clevent))
                sessions = Session.objects.filter(
                    Q(offering_id=offering_id) & Q(status='scheduled') & Q(date_start__gte=day_now))
                for each_session in sessions:
                    Session.objects.filter(id=each_session.id).update(ts_link=hangout_links[0]['link'], vc_id=hangout_links[0]['id'])
            else:
                log_error_messages("ERROR: Event creation failed\n" + str(clevent))
        else:
            hangout_links = []

            event = create_event_dict(class_timings[0], class_days[0], class_start_date, class_end_date)
            event['attendees'] = recipients
            event['summary'] = "{}th {} Class for {}".format(db_offer.course.grade, db_offer.course.subject, db_center.name)

            clevent = calendar_service.events().insert(calendarId='primary', body=event).execute()
            if clevent['status'] == 'confirmed':
                hangout_links.append(get_hangout_event_details(clevent))
                meet_id_testing.append(get_hangout_event_details(clevent))
                log_error_messages("SUCCESS: Event creation completed" + str(clevent))
            else:
                log_error_messages("ERROR: Event creation failed (different timings)\n" + str(clevent))

            event = create_event_dict(class_timings[1], class_days[1], class_start_date, class_end_date)
            event['attendees'] = recipients
            event['summary'] = "{}th {} Class for {}".format(db_offer.course.grade, db_offer.course.subject, db_center.name)

            clevent = calendar_service.events().insert(calendarId='primary', body=event).execute()
            if clevent['status'] == 'confirmed':
                hangout_links.append(get_hangout_event_details(clevent))
                meet_id_testing.append(get_hangout_event_details(clevent))
                log_error_messages("SUCCESS: Event creation completed" + str(clevent))
            else:
                log_error_messages("ERROR: Event creation failed (different timings)\n" + str(clevent))

            if len(hangout_links) > 0:
                sessions = Session.objects.filter(Q(offering_id=offering_id) & Q(status='scheduled') & Q(date_start__gte=day_now)).order_by("date_start")
                for idx, session_data in enumerate(sessions):
                    index = idx % 2
                    Session.objects.filter(id=session_data.id).update(ts_link=hangout_links[index]['link'], vc_id=hangout_links[index]['id'])
    except Exception as exp:
        log_error_messages("EXCEPTION: " + str(exp))
    try:
        session_ids = Session.objects.values_list("id",flat = True).filter(offering_id = offering_id)
        for id in session_ids:
            meeting_id = Session.objects.values_list("ts_link",flat = True).filter(id = id)[0]
            if meeting_id == "":
                Session.objects.filter(id=id).update(ts_link=meet_id_testing[0]['link'], vc_id=meet_id_testing[0]['id'])
    except:
        pass

    

    log_error_messages("meeting" + str(meet_id_testing[0]['link']))
    log_error_messages("MILESTONE: meeting_creation_job END\n\n\n***********************************************")

def create_event_dict(class_time, class_days, class_start_date, class_end_date):
    event = {
        'summary': '',
        'location': 'User',
        'description': 'Online Classroom Session',
        'start': {
            'dateTime': '',
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': '',
            'timeZone': 'Asia/Kolkata',
        },
        ''
        'attendees': [
        ],
        'recurrence': [
            'RRULE:FREQ=WEEKLY;UNTIL={};WKST=SU;BYDAY='
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    recurrence_holder = 'RRULE:FREQ=WEEKLY;UNTIL={};WKST=SU;BYDAY='

    start_hour, end_hour = class_time.split("-")

    hour, minute = start_hour.split(":")
    start_hour = ("0" if len(hour) < 2 else "") + start_hour + ":00+05:30"

    hour, minute = end_hour.split(":")
    end_hour = ("0" if len(hour) < 2 else "") + end_hour + ":00+05:30"

    event['start']['dateTime'] = "{}T{}".format(class_start_date, start_hour)
    event['end']['dateTime'] = "{}T{}".format(class_start_date, end_hour)

    until = class_end_date.replace("-", "") + "T235959Z"
    temp = recurrence_holder
    temp = temp.format(until) + class_days

    event['recurrence'][0] = temp

    return event


def get_hangout_event_details(calender_event):
    vc_id = ''
    hangout_link = ''
    try:
        vc_id = calender_event['id']
    except (KeyError, Exception):
        pass

    try:
        hangout_link = calender_event['hangoutLink']
    except (KeyError, Exception):
        log_error_messages("WARNING: HTML Link Obtained instead of Hangout Link")
        hangout_link = calender_event['htmlLink']

    return {'id': vc_id, 'link': hangout_link}

# ************************************

# -------------------Content Auto Upload ------------#

# Authenticate with google Oauth2

def gdrive_authenticate():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("gdrive_creds.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("gdrive_creds.txt")
    gdrive = GoogleDrive(gauth)
    return gdrive


def create_folder(foldername, parentID, drive):
    file1 = drive.CreateFile({'title': foldername,
                              "parents": [{"id": parentID}],
                              "mimeType": "application/vnd.google-apps.folder"})
    file1.Upload()
    return file1['id']


def get_folder_contents(ID, drive):
    args = "in parents and mimeType = 'application/vnd.google-apps.folder' and trashed=false"
    arguments = '\'{0}\' {1}'.format(ID, args)
    file_list = drive.ListFile({'q': arguments}).GetList()
    return file_list


def find(name, parentID, drive):
    file_list0 = drive.ListFile({'q': "'{}' in parents and trashed = false".format(parentID)}).GetList()
    nameID = None
    for file0 in file_list0:
        if file0['title'] == name:
            nameID = file0['id']
    if nameID == None:
        return False
    else:
        return nameID


def find_else_makefolder(name, parentID, drive):
    found = find(name, parentID, drive)
    if found == False:
        return create_folder(name, parentID, drive)
    else:
        return found


def find_else_makestructure(system, date, experiment, filename):
    systemID = find_else_makefolder(system, PyCMDSdataID)
    dateID = find_else_makefolder(date, systemID)
    experimentID = find_else_makefolder(experiment, dateID)
    return find(filename, experimentID)


def get_or_create_driveContainer(path_dict, drive):
    base_folder = drive.CreateFile(
        {"id": '0B0WiysvR2DOlMzBsOVZna2RiM0U', "mimeType": "application/vnd.google-apps.folder"})
    p_folder_id = base_folder['id']
    for i, val in path_dict.iteritems():
        p_folder_id = find_else_makefolder(val, p_folder_id, drive)
    return p_folder_id


@csrf_exempt
def content_upload(request):
    files = request.FILES
    topicd_id = request.POST.get('topic_detail_id')
    up_type = request.POST.get('up_type')
    if topicd_id:
        topic_detail = TopicDetails.objects.filter(pk=topicd_id)
        if topic_detail:
            topic_detail = topic_detail[0]
            topic_course = topic_detail.topic.course_id
            if up_type == 'url':
                url_list = request.POST.getlist('draft_url_list[]')
                draft_url = ''
                up_urls = []
                for i, v in enumerate(url_list):
                    up_urls.append(v)
                    if i == 0:
                        draft_url += v
                    else:
                        draft_url += '#d7,8l#' + v
                topic_detail.drafturl = draft_url
                topic_detail.save()
            elif up_type == 'fil':
                path_dict = OrderedDict([
                    ('board', topic_course.board_name),
                    ('subject', topic_course.subject),
                    ('grade', make_number_verb(topic_course.grade)),
                    ('topic', topic_detail.topic.title),
                    ('stream', topic_detail.attribute.types),
                ])
                drive = gdrive_authenticate()
                upload_folder_id = get_or_create_driveContainer(path_dict, drive)
                up_urls = {}
                for i, filee in files.iteritems():
                    file1 = drive.CreateFile(
                        {'title': filee.name, 'mimeType': filee.content_type, "parents": [{"id": upload_folder_id}]})
                    output = tempfile.NamedTemporaryFile(delete=True)
                    output.write(filee.read())
                    output.flush()
                    file1.SetContentFile(output.name)
                    file1.Upload()
                    up_urls[file1['title']] = file1['alternateLink']
                    output.close()
                draft_url = ''
                for i, v in enumerate(up_urls):
                    if i == 0:
                        draft_url += up_urls[v]
                    else:
                        draft_url += '#d7,8l#' + up_urls[v]
                topic_detail.drafturl = draft_url
                topic_detail.save()
    return HttpResponse(simplejson.dumps({'created_links': up_urls}), mimetype='application/json')


# ------------------ End Content Auto Upload --------#

# -------------------Demand--------------------------#
def weekday_sorter(sort_list):
    day_sorter = {'Friday': 4, 'Thursday': 3, 'Wednesday': 2, 'Monday': 0, 'Tuesday': 1, 'Saturday': 5, 'Sunday': 6}
    sort_list = sorted(sort_list, key=day_sorter.get)
    return sort_list


def demand_new(request):
    # if request.user.is_authenticated():
    pref_med = ""
    usr_profile = UserProfile.objects.filter(id=request.user.id)
    for i in usr_profile:
        pref_med = i.pref_medium
    centers = Center.objects.all()
    states = []
    subjects = []
    for center in centers:
        states.append(center.state)
    states = list(set(states))
    states.sort()
    courses = Course.objects.all()
    for course in courses:
        subjects.append(course.subject)
    subjects = list(set(subjects))
    subjects.sort()
    medium = Demandslot.objects.values_list('center__language', flat=True).distinct()
    days = Demandslot.objects.values_list('day', flat=True).distinct()
    days = weekday_sorter(days)
    time_slots = Demandslot.objects.values('start_time', 'end_time').distinct()
    time_slotss = [(ent['start_time'].strftime('%H:%M'), ent['end_time'].strftime('%H:%M')) for ent in time_slots]

    status = ["Planned", "Active", "Inactive", "Closed"]
    curr_user = request.user
    user_details = {}
    is_teacher = True
    if curr_user.is_authenticated():
        is_authenticated = True
        save_user_activity(request, 'Viewed: Oppourtunities', 'Page Visit')
        is_teacher = has_pref_role(curr_user.userprofile, "Teacher")
        profile_completion_status = curr_user.userprofile.profile_completion_status
        user_details = {
            'profile_status': 'Filled' if profile_completion_status else 'Not Filled',
            'preferred_language': curr_user.userprofile.pref_medium
        }
    else:
        is_authenticated = False
    message = request.GET.get('message', '')
    return render_response(request, "demand_new.html",
                           {'centers': centers, 'time_slots': time_slotss, 'states': states, 'subjects': subjects,
                            'medium': medium, 'days': days, 'is_authenticated': is_authenticated,
                            "is_teacher": is_teacher, 'user_details': user_details, 'status': status,
                            "pref_med": pref_med, 'message': message})


def get_filters_api(request):
    medium = [str(medium) for medium in \
              Demandslot.objects.values_list('center__language', flat=True).distinct()]
    try:
        idx = medium.index('None')
    except Exception as exp:
        pass
    else:
        if idx >= 0:
            medium.pop(idx)

    states = Center.objects.values_list('state', flat=True).distinct().exclude(Q(state__isnull=True))
    try:
        idx = states.index(None)
    except Exception as exp:
        pass
    else:
        if idx >= 0:
            centers.pop(idx)
    states = [str(state.encode('utf-8')) for state in states]

    data = {}
    data['languages'] = medium
    data['states'] = states
    data['sessions_filters'] = ["scheduled", "completed", "cancelled"]
    admin_assigned_roles = ["TSD Panel Member", "Class Assistant"]
    roles = Role.objects.exclude(name__in=admin_assigned_roles)
    data['roles'] = [{role.id: role.name} for role in roles]

    return HttpResponse(json.dumps(data), content_type='application/json')


def get_demand(request):
    platform = request.POST.get('platform', '')
    if not platform:
        sel_days = json.loads(request.POST.get('sel_days', '[]'))
        sel_langs = json.loads(request.POST.get('sel_langs', '[]'))
        sel_states = json.loads(request.POST.get('sel_states', '[]'))
        sel_slots = json.loads(request.POST.get('sel_slots', '"9:00;17:00"'))
        if sel_slots == 'all' or sel_slots == '':
            sel_slots = '9:00;17:00'
        sel_times = sel_slots.split(';')
    else:
        sel_days = request.POST.get('sel_days', '')
        if sel_days:
            sel_days = sel_days.split(',')
        else:
            sel_days = sel_days.split()
        sel_langs = request.POST.get('sel_langs', '')
        if sel_langs:
            sel_langs = sel_langs.split(',')
        else:
            sel_langs = sel_langs.split()
        sel_states = request.POST.get('sel_states', '')
        if sel_states:
            sel_states = sel_states.split(',')
        else:
            sel_states = sel_states.split()
        sel_slots = request.POST.get('sel_slots', '9:00,17:00')
        sel_times = sel_slots.split(',')

        if len(sel_states) == 0:
            sel_states = Demandslot.objects.values_list('center__state', flat=True).distinct()

    if len(sel_days) == 0:
        sel_days = Demandslot.objects.values_list('day', flat=True).distinct()
    if len(sel_langs) == 0:
        sel_langs = Demandslot.objects.values_list('center__language', flat=True).distinct()
    centers_data = []
    today = datetime.datetime.now()
    if platform:
        filtered_centers = set(Demandslot.objects.filter(
            Q(day__in=sel_days) & Q(center__language__in=sel_langs) & Q(center__state__in=sel_states) & Q(
                start_time__gte=sel_times[0]) & Q(end_time__lte=sel_times[1])).values_list('center_id', flat=True))
    else:
        filtered_centers = set(Demandslot.objects.filter(
            Q(day__in=sel_days) & Q(center__language__in=sel_langs) & Q(start_time__gte=sel_times[0]) & Q(
                end_time__lte=sel_times[1])).values_list('center_id', flat=True))
    # And logic for Days Filter
    '''
    if len(sel_days) !=0:
        filtered_centers = Demandslot.objects.filter( Q(center__language__in=sel_langs) & Q(start_time__gte=sel_times[0]) & Q(end_time__lte=sel_times[1])).values_list('center_id',flat=True)
        day_filtered_centers=[]
        for ent in sel_days:
            day_filtered_centers.append(filtered_centers.filter(day=ent))
        day_centers = day_filtered_centers[0]
        for i,qset in enumerate(day_filtered_centers):
            if i < len(day_filtered_centers)-1:
                day_centers = set(day_centers) & set(day_filtered_centers[i+1])
        filtered_centers = set(day_centers)
    else:
        filtered_centers = Demandslot.objects.filter( Q(center__language__in=sel_langs) & Q(start_time__gte=sel_times[0]) & Q(end_time__lte=sel_times[1])).values_list('center_id',flat=True)
        filtered_centers = set(filtered_centers)
    '''
    # list(filtered_centers).sort()
    for ent in filtered_centers:
        temp = {}
        center = Center.objects.get(id=ent)
        center_image = "http://placehold.it/255x170/F15A22/fff/&text=" + center.name
        if center.photo:
            center_image = "/" + str(crop(center.photo, "255x170"))
            if platform:
                center_image = 'http://' + request.META['HTTP_HOST'] + center_image
        if center.description:
            center_desc = ((center.description)[
                           :70] + '.. <span style="color:#2EC7F0;cursor:pointer">Know more >></span>') if len(
                center.description) > 70 else center.description
        else:
            center_desc = 'No description available'
        center_offers = center.offering_set.all()
        running_offers = center_offers.filter(status='running')

        demand_slot_booked = Demandslot.objects.filter(center=center, status='Booked').values_list('offering',
                                                                                                   flat=True).distinct()

        current_ays = Ayfy.objects.filter(start_date__lte=today, end_date__gte=today,
                                          types='Academic Year').values_list('id', flat=True)

        if demand_slot_booked:
            pending_offers = center_offers.filter(status='pending', academic_year_id__in=current_ays).exclude(
                id__in=demand_slot_booked)
        else:
            pending_offers = center_offers.filter(status='pending', academic_year_id__in=current_ays)

        if not pending_offers:
            continue

        temp_buffer = pending_offers.values_list('id', 'course__grade', 'course__subject')
        pcourses_data = []
        for x in temp_buffer:
            p_dict = {}
            p_id, p_grade, p_sub = x[0], make_number_verb(x[1]), x[2]
            p_dict['id'] = p_id
            p_dict['grade'] = p_grade
            p_dict['subject'] = p_sub
            pcourses_data.append(p_dict)

        if not pcourses_data:
            continue

        tags = {}
        sub_list = list(pending_offers.values_list('course__subject', flat=True).distinct())
        tags['subjects'] = [i.replace(' ', '_') for i in sub_list]
        tags['months'] = [x.strftime('%B') for x in pending_offers.values_list('start_date', flat=True).distinct()]
        centers_data.append({'id': center.id,
                             'title': center.name,
                             'description': center_desc,
                             'image': center_image,
                             'pending_courses': pending_offers.count(),
                             'running_courses': running_offers.count(),
                             'tags': tags})
    if not platform:
        return HttpResponse(simplejson.dumps({'data': centers_data}), mimetype='application/json')
    else:
        rel_data = {}
        rel_data['status'] = 200
        rel_data['message'] = 'success'
        rel_data['data'] = centers_data
        return HttpResponse(simplejson.dumps(rel_data), mimetype='application/json')


@login_required
def demand_detail(request, center_id):
    if request.user.is_authenticated():
        userp = request.user.userprofile
        pref_roles = userp.pref_roles.values_list('name', flat='True')
        teacher_role = True if "Teacher" in pref_roles else False
    if center_id and teacher_role:
        center = Center.objects.get(pk=center_id)
        center_image = "http://placehold.it/640x480/F15A22/fff/&text=" + center.name
        if request.user.is_authenticated():
            userp = request.user.userprofile
            pref_roles = userp.pref_roles.values_list('name', flat='True')
            teacher_role = True if "Teacher" in pref_roles else False
            status = 'Started'
            profile_status = userp.profile_completion_status
            onboarding = userp.rolepreference_set.filter(role__name='Teacher')
            role_outcome = onboarding[0].role_outcome
            se_status = onboarding[0].onboardingstepstatus_set.filter(step__stepname='Self Evaluation')[0].status
            a_and_p_status = \
            onboarding[0].onboardingstepstatus_set.filter(step__stepname='Availability and Preferences')[0].status
            if userp:
                if profile_status:
                    status = 'Inprocess'
                    if profile_status and userp.evd_rep:
                        status = 'Selected'
                        teacher_onboard_status = userp.rolepreference_set.filter(role__name='Teacher')[
                            0].role_onboarding_status
                        if teacher_onboard_status == 100:
                            status = 'Ready'
                # add here
                is_centeradmin = False
                if has_role(userp, "Center Admin"):
                    is_centeradmin = True

        if center.photo:
            center_image = "/" + str(crop(center.photo, "640x480"))
        center_courses = center.offering_set.filter(
            (Q(course_type='C') and ~Q(status="not_approved")) | (Q(course_type='S') | Q(course_type='')))
        run_courses = center_courses.filter(status='running')
        run_courses_count = run_courses.count()

        demand_slot_booked = Demandslot.objects.filter(center=center, status='Booked').values_list('offering',
                                                                                                   flat=True).distinct()

        today = datetime.datetime.now()
        current_ays = Ayfy.objects.filter(start_date__lte=today, end_date__gte=today,
                                          types='Academic Year').values_list('id', flat=True)

        if demand_slot_booked:
            pending_courses = center_courses.filter(status='pending', academic_year_id__in=current_ays).exclude(
                id__in=demand_slot_booked)
        else:
            pending_courses = center_courses.filter(status='pending', academic_year_id__in=current_ays)

        temp_buffer = pending_courses.values_list('id', 'course__grade', 'course__subject')
        pcourses_data = [(x[0], make_number_verb(x[1]), x[2]) for x in temp_buffer]
        temp_buffer = []
        center_demand = Demandslot.objects.filter(center=center).filter(status='Unallocated')
        demand_days = center_demand.values_list('day', flat=True).distinct()
        grouped_slots = collections.OrderedDict()
        if demand_days:
            demand_days = weekday_sorter(demand_days)
            for ent in demand_days:
                temp_buffer = center_demand.filter(day=ent).values_list('id', 'day', 'start_time', 'end_time')
                grouped_slots[ent] = [(x[0], x[1], x[2].strftime("%I:%M %p"), x[3].strftime("%I:%M %p")) for x in
                                      temp_buffer]
        pending_courses_count = pending_courses.count()
        run_teacher_details = []
        for ent in run_courses:
            run_teacher_details += ent.session_set.values_list('teacher__first_name',
                                                               'teacher__userprofile__picture').annotate(
                sess_count=Count('id')).filter(status='Completed').distinct()
        if pending_courses_count > 0:
            course_percent = 100 - round(pending_courses_count / float(run_courses_count + pending_courses_count),
                                         2) * 100;
            course_ratio = 1 - (pending_courses_count / float(run_courses_count + pending_courses_count))
        else:
            course_percent = 100;
            course_ratio = 1;
        # user slots
        user_slots = Demandslot.objects.filter(user_id=request.user.id)
        slot_details = []
        if user_slots:
            slot_details = user_slots.values_list('center__name', 'day', 'start_time', 'end_time')
        centr = {
            'id': center.id,
            'name': center.name,
            'photo': center_image,
            'desc': center.description,
            'running_courses': run_courses_count,
            'pending_courses': pending_courses_count,
            'course_ratio': course_ratio,
            'current_teachers': run_teacher_details,
            'course_percent': course_percent,
            'pcourses_data': pcourses_data,
            'grouped_slots': grouped_slots,
            'user_slots': slot_details,
            'user_status': status,
            'profile_status': profile_status,
            'teacher_se_status': se_status,
            'teacher_role_outcome': role_outcome,
            'a_and_p_status': a_and_p_status,
            'teacher_role': teacher_role
        }
        save_user_activity(request, 'Choosed School To Teach:' + str(center.name), 'Page Visit')
        return render_response(request, "demand_detail.html", {'center': centr, 'is_centeradmin': is_centeradmin,
                                                               'is_superuser': request.user.is_superuser})
    else:
        return redirect('/demand/?message=Please,Change Role to Teacher.')


def demand_details_api(request, center_id):
    if center_id:
        center = Center.objects.get(pk=center_id)
        center_image = "http://placehold.it/640x480/F15A22/fff/&text=" + center.name
        if center.photo:
            center_image = 'http://' + request.META['HTTP_HOST'] + "/" + str(crop(center.photo, "640x480"))
        center_courses = center.offering_set.filter()
        run_courses = center_courses.filter(status='running')
        run_courses_count = run_courses.count()

        demand_slot_booked = Demandslot.objects.filter(center=center, status='Booked').values_list('offering',
                                                                                                   flat=True).distinct()
        if demand_slot_booked:
            pending_courses = center_courses.filter(status='pending').exclude(id__in=demand_slot_booked)
        else:
            pending_courses = center_courses.filter(status='pending')

        temp_buffer = pending_courses.values_list('id', 'course__grade', 'course__subject')
        pcourses_data = []
        for x in temp_buffer:
            p_dict = {}
            p_id, p_grade, p_sub = x[0], make_number_verb(x[1]), x[2]
            p_dict['id'] = p_id
            p_dict['grade'] = p_grade
            p_dict['subject'] = p_sub
            pcourses_data.append(p_dict)
        temp_buffer = []
        center_demand = Demandslot.objects.filter(center=center).filter(status='Unallocated')
        demand_days = center_demand.values_list('day', flat=True).distinct()
        grouped_slots = collections.OrderedDict()
        if demand_days:
            demand_days = weekday_sorter(demand_days)
            for ent in demand_days:
                temp_buffer = center_demand.filter(day=ent).values_list('id', 'day', 'start_time', 'end_time')
                grouped_slots[ent] = [(x[0], x[1], x[2].strftime("%I:%M %p"), x[3].strftime("%I:%M %p")) for x in
                                      temp_buffer]
        pending_courses_count = pending_courses.count()
        run_teacher_details = []
        admin_details = []
        admin_id = center.admin
        admin_details_list = []
        admin_details = {}
        admin_photo = ''
        admin_name = ''
        if admin_id:
            admin_name = admin_id.first_name
            admin_details['name'] = admin_name
            userdetails = UserProfile.objects.filter(user_id=admin_id)
            if userdetails:
                admin_photo = userdetails[0].picture
                admin_details['image'] = admin_photo
        if admin_details:
            admin_details_list.append(admin_details)

        conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                               user=settings.DATABASES['default']['USER'],
                               passwd=settings.DATABASES['default']['PASSWORD'],
                               db=settings.DATABASES['default']['NAME'],
                               charset="utf8",
                               use_unicode=True)
        cursor = conn.cursor()
        run_teacher_details = []
        query = "select teacher_id, date_end from web_session where offering_id = '%s' and status in ('completed', 'pending') order by date_end desc limit 3;" % center_id
        cursor.execute(query)
        rows = cursor.fetchall()
        teacher_dtl_list = []
        for row in rows:
            t_detls = {}
            t_name = ''
            date_end = ''
            t_image = ''
            t_id, date_end = row
            t_details = User.objects.filter(id=int(t_id))
            if t_details:
                t_name = t_details[0].first_name
            image_detls = UserProfile.objects.filter(id=int(t_id))
            if image_detls:
                t_image = image_detls[0].picture
            t_detls['name'] = t_name
            t_detls['class_date'] = str(date_end)
            t_detls['image'] = t_image
            teacher_dtl_list.append(t_detls)
        cursor.close()
        conn.close()

        for ent in run_courses:
            t_dict = {}
            teacher_details = ent.session_set.values_list('teacher__first_name',
                                                          'teacher__userprofile__picture').annotate(
                sess_count=Count('id')).filter(status='Completed').distinct()
            if teacher_details:
                t_name, t_image, t_id = teacher_details[0]
                t_dict['name'] = t_name
                t_dict['image'] = t_image
                t_dict['id'] = t_id
                run_teacher_details.append(t_dict)

        center_demand = Demandslot.objects.filter(center=center).filter(status='Unallocated')
        demand_days = center_demand.values_list('day', flat=True).distinct()
        grouped_slots = collections.OrderedDict()
        if demand_days:
            demand_days = weekday_sorter(demand_days)
            for ent in demand_days:
                temp_buffer = center_demand.filter(day=ent).values_list('id', 'day', 'start_time', 'end_time')
                # grouped_slots[ent] = [(x[0],x[2].strftime("%I:%M %p"),x[3].strftime("%I:%M %p")) for x in temp_buffer]
                ent_list = []
                for x in temp_buffer:
                    ent_dict = {}
                    ent_dict['id'] = x[0]
                    ent_dict['start_date'] = x[2].strftime("%I:%M %p")
                    ent_dict['end_date'] = x[3].strftime("%I:%M %p")
                    ent_list.append(ent_dict)
                grouped_slots[ent] = ent_list

        ass_id = center.assistant_id
        class_ass_dtls_list = []
        class_ass_dtls = {}
        class_ass = ''
        ass_image = ''
        if ass_id:
            class_ass = User.objects.filter(id=int(ass_id))
            if class_ass:
                class_ass = class_ass[0].first_name
                class_ass_dtls['name'] = class_ass
            cls_pro_details = UserProfile.objects.filter(id=int(ass_id))
            if cls_pro_details:
                ass_image = cls_pro_details[0].picture
                class_ass_dtls['image'] = ass_image
            class_ass_dtls_list.append(class_ass_dtls)

        user_slots = Demandslot.objects.filter(user=request.user.id)
        slot_details = []
        req_dict = {}
        if user_slots:
            details = user_slots.values_list('center__name', 'day', 'start_time', 'end_time')
            for det in details:
                detail = {}
                center_name, day, st_time, end_time = det
                detail['day'] = str(day)
                detail['start_time'] = str(st_time)
                detail['end_time'] = str(end_time)
                slot_details.append(detail)

            req_dict['center_id'] = center.id
            req_dict['center_name'] = center.name
            req_dict['slots_data'] = slot_details

        centr = {}
        data = {
            'id': center.id,
            'name': center.name,
            'photo': center_image,
            'desc': center.description,
            'current_teachers': run_teacher_details,
            'pcourses_data': pcourses_data,
            'admin': admin_details_list,
            'latest_classesdetails': teacher_dtl_list,
            'sponsor': center.donor_name,
            'class_assistant': class_ass_dtls_list,
            'grouped_slots': grouped_slots,
            'slot_details': req_dict
        }
        centr['status'] = 200
        centr['message'] = 'success'
        centr['data'] = data

    return HttpResponse(json.dumps(centr), content_type='application/json')


@login_required
def block_demand(request):
    block_response = {"status": 0, "message": "Success"}
    platform = request.POST.get('platform', '')
    center_id = request.POST.get('center_id')
    offer_id = request.POST.get('offer_id')
    slots = request.POST.get('slot_ids')
    user_id = request.POST.get('user_id') or request.user.id
    if center_id and offer_id and slots:
        slots = slots.split(';')
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
                if long(user_id) != request.user.id:
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
            # admins = User.objects.filter(is_superuser = True).filter(email__icontains = '@evidyaloka.org')
            pref_role_status = RolePreference.objects.filter(userprofile_id=User.objects.get(id=user_id).userprofile.id,
                                                             role__name='Teacher')
            if pref_role_status:
                pref_role_status = pref_role_status[0].role_outcome
            else:
                pref_role_status = ''

            center_state = centerobj.state.title().rstrip()
            center_admin_mail = centerobj.admin.email
            VA_coord_mail = ""

            state_coord=[]
            if center_state == "Karnataka":

                state_coord = Center.objects.filter(state="Karnataka",status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email',flat=True).distinct()
            elif center_state == "Tamil Nadu":

                state_coord = Center.objects.filter(state="Tamil Nadu",status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email',flat=True).distinct()
            elif center_state == "Jharkhand":

                state_coord = Center.objects.filter(state="Jharkhand",status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email',flat=True).distinct()
            elif center_state == "Andhra Pradesh":

                state_coord = Center.objects.filter(state="Andhra Pradesh",status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email',flat=True).distinct()
            elif center_state == "Telengana":

                state_coord = Center.objects.filter(state="Telengana",status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email',flat=True).distinct()
            elif center_state == "Maharashtra":

                state_coord = Center.objects.filter(state="Maharashtra",status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email',flat=True).distinct()
            elif center_state == "West Bengal":

                state_coord = Center.objects.filter(state="West Bengal",status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email',flat=True).distinct()

            args = {'user': userobj, 'slots': slot_objs, 'contxt': 'Blocked', 'role_status': pref_role_status, \
                    'confirm_url': WEB_BASE_URL + "centeradmin/?center_id=" + center_id}

            subject_template = 'mail/_demand_handle/short.txt'
            subject = get_mail_content(subject_template, args).replace('\n', '')
            if pref_role_status == 'Recommended':
                # recipients = [center_admin_mail, state_coord]
                recipients = state_coord.append(center_admin_mail)
                body_template = 'mail/_demand_handle/full_rft.txt'
            else:
                # recipients = [state_coord, VA_coord_mail]
                recipients = state_coord.append(VA_coord_mail)
                body_template = 'mail/_demand_handle/full_not_rft.txt'

            body = get_mail_content(body_template, args)
            # change it after testing
            # recipients.append('akhilraj@headrun.com') # headrun developer, should not get emailer
            # recipients.append('rini.jose@evidyaloka.org')
            userid = ''
            if userobj:
                userid = userobj.id
            user_mail_config = has_mail_receive_accepted(userobj,'Announcement')
            if user_mail_config['user_settings'] or user_mail_config['role_settings']:
                insert_into_alerts(subject, body, ','.join(recipients), userid, 'email')
            # _send_mail(recipients,'_demand_handle',{'user':request.user,'slots':slot_objs,'contxt' : 'Blocked', 'role_status': pref_role_status})
        except Exception as e:
            if platform:
                block_response = {"status": 1, "message": "Error"}
                return HttpResponse(json.dumps(block_response), content_type='application/json')
            else:
                return HttpResponse('Error')
    if platform:
        return HttpResponse(json.dumps(block_response), content_type='application/json')
    if centerobj and offering_obj and slots:
        timeSlot = ''
        for ent in slots:
            demandSlotObj = Demandslot.objects.get(pk=ent)
            timeSlot += str(demandSlotObj.day) + ":" + str(demandSlotObj.start_time) + " to " + str(
                demandSlotObj.end_time) + " and "
        timeSlot.rsplit(' ', 1)[0]
        corseObj = Course.objects.get(id=offering_obj.course_id)
        save_user_activity(request, 'Confirmed Oppourtunities:' + str(centerobj.name) + ',' + str(
            corseObj.subject) + ',' + timeSlot, 'Action')
    return HttpResponse('ok')


@login_required
def confirm_accept_or_reject_slot(request):
    btn_type = request.GET.get('btn_type')
    center_id = request.GET.get('center_id')
    offering_id = request.GET.get('offering_id')
    reason = request.GET.get('reason', '')
    user_id = None
    msg = confirm_reject_slot(user_id, btn_type, center_id, offering_id, reason, request)
    return HttpResponse(msg)


def confirm_reject_slot(user_id, btn_type, center_id, offering_id, reason, request):
    try:
        user_obj = None
        current_date = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30))
        if request.user.is_authenticated():
            user_obj = request.user
        else:
            user_obj = user_id
        msg = ''
        centerobj = Center.objects.get(id=center_id)
        # data_for_sess = {'center_id': center_id, 'offering_id': offering_id, 'msg': msg}
        slot_obj = Demandslot.objects.filter(status='Booked', center=centerobj, offering_id=offering_id)
        teacher_id = slot_obj[0].user.id

        args = {'user': slot_obj[0].user, 'slots': slot_obj, 'contxt': 'Blocked', 'reason': reason, \
                'confirm_url': WEB_BASE_URL + "centeradmin/?center_id=" + center_id,
                'subject': slot_obj[0].offering.course.subject, 'grade': slot_obj[0].offering.course.grade}

        
        center_state = centerobj.state
        if btn_type == 'confirm':
            for slot in slot_obj:
                slot.status = 'Allocated'
                slot.save()
            center_admin_email = ''
            if slot_obj[0].center.admin:
                user_mail_config = has_mail_receive_accepted(slot_obj[0].center.admin, 'Announcement')
                if user_mail_config['user_settings'] or user_mail_config['role_settings']:
                    center_admin_email = slot_obj[0].center.admin.email

            message = get_template('mail/_demand_handle/full_confirm_vol.txt').render(Context(args))

            state_coord=[]
            if center_state == "Karnataka":
                # state_coord = "ashwini.avanthi@evidyaloka.org"
                state_coord = Center.objects.filter(state="Karnataka", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Tamil Nadu":
                # state_coord = "gayathri.ramesh@evidyaloka.org"
                state_coord = Center.objects.filter(state="Tamil Nadu", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Jharkhand":
                # state_coord = "pratimac@evidyaloka.org,shubh.varshney@evidyaloka.org"
                state_coord = Center.objects.filter(state="Jharkhand", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Andhra Pradesh":
                # state_coord = "nikitha.madan@evidyaloka.org"
                state_coord = Center.objects.filter(state="Andhra Pradesh", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Telengana":
                # state_coord = "nikitha.madan@evidyaloka.org"
                state_coord = Center.objects.filter(state="Telengana", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "Maharashtra":
                # state_coord = "tejal.ranadive@evidyaloka.org"
                state_coord = Center.objects.filter(state="Maharashtra", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()
            elif center_state == "West Bengal":
                # state_coord = "rinki.chowdhury@evidyaloka.org"
                state_coord = Center.objects.filter(state="West Bengal", status="Active").exclude(delivery_coordinator__isnull=True).values_list('delivery_coordinator__email', flat=True).distinct()

            # change it after testing
            # recipients.append('akhilraj@headrun.com')
            # recipients.append('rini.jose@evidyaloka.org')
            subject = "Your allocation of the selected course is Confirmed"
            to = [slot_obj[0].user.email]
            from_email = settings.DEFAULT_FROM_EMAIL
            cc = [ center_admin_email].extend(state_coord)
            if centerobj.admin: cc.append(centerobj.admin.email)
            admin = AlertUser.objects.get(role__name='vol_admin')
            if admin: cc.extend([user.email for user in admin.user.all()])
            msg = EmailMessage(subject, message, to=to, from_email=from_email, cc=cc)
            msg.content_subtype = 'html'
            msg.send()
            center_dc = ''
            center_admin = ''
            if centerobj.admin:
                center_admin = centerobj.admin
            try:
                center_dc = centerobj.delivery_coordinator
            except:
                center_dc = ''
            assign_to = None
            if center_dc:
                assign_to =center_dc
            else:
                assign_to = center_admin

            # if center_dc:
                # user = User.objects.filter(username=center_dc)
            demand_tasks = Task.objects.filter(assignedTo=assign_to, performedOn_userId=teacher_id,
                                            taskStatus='Open').order_by('-taskCreatedDate')

            if len(demand_tasks) > 0:
                if request.user.first_name:
                    commentNew = 'Confirmed by ' + str(request.user.get_full_name()) + " :: " + str(request.user.id)

                Task.objects.filter(id=demand_tasks[0].id).update(taskStatus='Closed', comment=commentNew,
                                                                subject='Your allocation of the selected course is Confirmed',
                                                                taskUpdatedDate=current_date)
        else:
            center_dc = center_admin = ''
            if centerobj.admin: center_admin = centerobj.admin
            if centerobj.delivery_coordinator: center_dc = centerobj.delivery_coordinator

            cc = []
            admin = AlertUser.objects.get(role__name='vol_admin')
            if admin: cc.extend([user.email for user in admin.user.all()])
            to = [slot_obj[0].user.email]
            for slot in slot_obj:
                if slot.type==1: slot.offering=None
                slot.user=None
                slot.status='Unallocated'
                slot.date_booked=None
                slot.type=2
                slot.save()

            if center_admin: cc.append(center_admin.email)
            if center_dc: cc.append(center_dc.email)
            admin = AlertUser.objects.get(role__name='vol_admin')
            if admin: cc.extend([user.email for user in admin.user.all()])
            subject = "Your selection of course is Not Confirmed"
            from_email = settings.DEFAULT_FROM_EMAIL
            body_template = 'mail/_demand_handle/full_reject_vol.txt'
            body = get_mail_content(body_template, args)
            print(to, cc)
            msg = EmailMessage(subject, body, to=to, from_email=from_email, cc=cc)
            msg.content_subtype = 'html'
            msg.send()
            assign_to = None
            if center_dc: assign_to = center_dc
            else: assign_to = center_admin

            demand_tasks = Task.objects.filter(assignedTo=assign_to, performedOn_userId=teacher_id, taskStatus='Open').order_by('-taskCreatedDate')

            if len(demand_tasks) > 0:
                if request.user.first_name:
                    commentNew = 'Rejected by ' + str(request.user.get_full_name()) + " :: " + str(request.user.id)
                Task.objects.filter(id=demand_tasks[0].id).update(taskStatus='Closed', comment=commentNew,
                                                                subject='Your selection of course is Not Confirmed',
                                                                taskUpdatedDate=current_date)

        return "ok"
    except Exception as e:
        print("POST Exception  e", e)
        traceback.print_exc()
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


@login_required
def release_demand(request):
    platform = request.POST.get('platform', '')
    resp = release_slots(request.user)
    if platform:
        centr = {}
        if resp == True:
            centr['status'] = 200
            centr['message'] = 'success'
            centr['data'] = 'All your previous slots are released..'
        else:
            centr['status'] = 404
            centr['message'] = 'failed'
            centr['data'] = 'Some Error Occurred!.. Please try Again.'
        return HttpResponse(json.dumps(centr), content_type='application/json')

    else:
        if resp == True:
            return HttpResponse('All your previous slots are released..')
        else:
            return HttpResponse('Some Error Occurred!.. Please try Again.')


def release_slots(user):
    status = True
    user_slots = Demandslot.objects.filter(user_id=user.id)
    for ent in user_slots:
        ent.offering_id = None
        ent.user_id = None
        ent.status = 'Unallocated'
        ent.date_booked = None
        try:
            ent.save()
        except:
            status = status and False
    # admins = User.objects.filter(is_superuser = True).filter(email__icontains = '@evidyaloka.org')
    # _send_mail(admins,'_demand_handle',{'user':user,'slots': user_slots, 'contxt': 'Released'})
    return status


# -------------------End demand --------------------------#


# -------------------Campaigns--------------------------#

def campaign_don(request):
    count_date = datetime.datetime(2015, 11, 19)
    don = Donation.objects.filter(donation_type='Sponsor a Child Education').filter(
        donation_time__gte=count_date).count()
    print don
    don_count = 300 - don
    if don_count > 0:
        resp_text = ' children left'
    else:
        resp_text = 'Target Reached'
        don_count = ''
    return render_to_response('campaign_page.html', {'don_count': don_count, 'resp_text': resp_text},
                              context_instance=RequestContext(request))


# ------------------ End Campaigns----------------------#


# ---------------- Partner Onboarding ------------------#

def partner(request, partner_id):
    print partner_id
    return render_response(request, 'partner.html', {'partner': partner_id})


# ---------------- End Partner Onboarding --------------#


# --------------Demand Management-------------------#


def demand(request):
    username = request.GET.get('username', '')
    if username:
        user = User.objects.get(username=username)
        pref_lang = user.userprofile.pref_medium;
        if pref_lang not in ['Telugu', 'Tamil', 'Hindi', 'Kannada', '']:
            pref_lang = 'Hindi'
        user_full_name = user.first_name + ' ' + user.last_name
        if pref_lang:
            centers = Center.objects.filter(language=pref_lang)
        else:
            centers = Center.objects.all()
        center_list = []
        center_p_offers = {}
        for ent in centers:
            slots = Slot.objects.filter(center_id=ent).filter(user=None)
            if slots:
                p_offer = Offering.objects.filter(status='Pending')
                if p_offer:
                    p_offer_list = []
                    for ent1 in p_offer:
                        name = ent1.course.board_name + ' ' + ent1.course.grade + ' ' + ent1.course.subject + '( ' + ent1.center.name + ' )'
                        offer = {'offer_id': ent1.id, 'offer_name': name}
                        if ent1.center.id == ent.id:
                            p_offer_list.append(offer)
                    center_p_offers.update({ent.id: p_offer_list})
                cent = {'center_name': ent.name, 'center_id': ent.id, 'center_state': ent.state}
                center_list.append(cent)
                for ent in center_p_offers:
                    print  center_p_offers[ent]
        # offers = Offering.objects.filter(status='Pending')
        if center_list:
            # offerings = []
            # for ent in offers:
            #   name = ent.course.board_name +' '+ent.course.grade+' '+ent.course.subject+'('+ent.center.name+')'+'('+ent.language+')'
            #  off = { 'center_id':ent.center_id, 'name': name , 'offer_id':ent.id }
            # offerings.append(off)
            # print offerings
            json_center_p_offers = mark_safe(json.dumps(center_p_offers, ensure_ascii=True))
            return render_response(request, "avail_slots.html",
                                   {'centers': center_list, 'user_name': user_full_name, 'user_lang': pref_lang,
                                    'user_id': user.id, 'centers_p_offers': json_center_p_offers})
        else:
            return HttpResponse('No Slots in demand')
    else:
        return HttpResponse('Error')


@csrf_exempt
def get_slots(request):
    center = request.POST.get('center', '')
    if center:
        slot_list = []
        slots = Slot.objects.filter(center_id=center).filter(user=None)
        if slots:
            for ent in slots:
                slot_list.append({'id': ent.id, 'slot': ent.slot})
            print slot_list
            return HttpResponse(simplejson.dumps(slot_list), mimetype='application/json')
        else:
            return HttpResponse('No Slots Available')

    else:
        return HttpResponse('Error')


def grab_slot(request):
    slot1 = request.POST.get('slot1', '')
    slot2 = request.POST.get('slot2', '')
    user_id = request.POST.get('user_id', '')
    avail = request.POST.get('avail_from', '')
    sel_offer = request.POST.get('sel_offer', '')
    avail_flag = request.POST.get('avail_flag')
    coord_details = {'Telugu': ['praneeth', 'praneeth1249'], 'Tamil': ['praneeth', 'praneeth1249'],
                     'Kannada': ['praneeth', 'praneeth1249'], 'Hindi': ['praneeth', 'praneeth1249'], }
    if avail_flag == 'True':
        user = User.objects.get(pk=user_id)
        print user.username
        if avail:
            print avail
            avail_date = datetime.datetime.strptime(avail, '%m/%d/%Y')
            print avail_date
            userp = user.userprofile
            userp.from_date = avail_date
            userp.save()

    elif avail_flag == 'False':
        if user_id and slot1 and sel_offer:
            user = User.objects.get(pk=user_id)
            offering = Offering.objects.get(pk=sel_offer)
            offer_name = offering.course.grade + ' ' + offering.course.subject
            if slot2:
                slots = Slot.objects.filter(pk__in=[slot1, slot2])
            else:
                slots = Slot.objects.filter(pk__in=[slot1])
            print slots
            if avail:
                avail_date = datetime.datetime.strptime(avail, '%m/%d/%Y')
            for ent in slots:
                ent.user = user
                ent.select_offer = offering
                ent.avail_from = avail_date
                ent.save()

            emails = [4496, 1368, 5065, 1, 3468]
            email_list = User.objects.filter(pk__in=emails).values_list('email', flat=True)
            subject = 'Offering grabbed by %s:' % user_id
            message = ''
            if len(slots) == 2:
                timings = '%s , %s' % (slots[0].slot, slots[1].slot)
                message = 'Center : %s \n Offering : %s \n Slot1 : %s \n Slot2 : %s \n Available From : %s ' % (
                offering.center.name, offer_name, slots[0].slot, slots[1].slot, avail)
            elif len(slots) == 1:
                timings = '%s' % slots[0].slot
                message = 'Center : %s \n Offering : %s \n Slot1 : %s \n Available From : %s ' % (
                offering.center.name, offer_name, slots[0].slot, avail)
            send_mail(subject, message, "evlSystem@evidyaloka.org", email_list)
            if offering.language:
                try:
                    coord_det = coord_details[offering.language]
                except KeyError:
                    coord_det = ['', '']
            ack_dict = {'center': offering.center.name, 'map': offering.center.location_map,
                        'state': offering.center.village, 'offer_name': offer_name, 'timings': timings,
                        'coord': coord_det[0], 'skype': coord_det[1]}
            return HttpResponse(simplejson.dumps(ack_dict), mimetype='application/json')

    return HttpResponse('ok')


# --------------Demand Management-------------------#


# ---------------Training Module--------------------#
@login_required
def mytrainings(request):
    r_user = request.user
    temp_completed = TrainingStatus.objects.filter(user=r_user).filter(status=True).values_list('training_id')
    completed = []
    for i in temp_completed:
        completed.append(i[0])
    trainings = Training.objects.all().order_by('category')
    cat_list = trainings.values('category').distinct().order_by('category')
    training_lists = {}
    for ent in cat_list:
        training_lists[ent['category']] = trainings.filter(category=ent['category'])
    save_user_activity(request, 'Viewed Page: My Tranings - My Trainings', 'Page Visit')
    return render_response(request, "my_trainings.html",
                           {"trainings": collections.OrderedDict(sorted(training_lists.items())),
                            "completed": completed})


@login_required
def training_complete(request):
    trai_id = request.POST.get('training_id', "")
    user_id = request.user.id
    today = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
    try:
        if trai_id:
            traing_status, created = TrainingStatus.objects.get_or_create(user_id=user_id, training_id=trai_id)
            traing_status.status = True
            traing_status.date_completed = today
            traing_status.save()
    except Exception as e:
        print e
    status = complete_teacher_readiness(request.user)
    content_dev_status = complete_content_dev_readiness(request.user)
    return HttpResponse('Success')


def complete_teacher_readiness(user):
    essential_trainings = Training.objects.filter(category='L0 (Essential)').values_list('id', flat=True)
    user_completed_etrainings = user.trainingstatus_set.filter(training__category='L0 (Essential)').values_list(
        'training__id', flat=True)
    if set(essential_trainings) == set(user_completed_etrainings):
        userp = user.userprofile
        teacher_preference = userp.rolepreference_set.filter(role__name='Teacher')
        userp.trainings_complete = True
        userp.save()
        if teacher_preference:
            teacher_preference = teacher_preference[0]
            readiness = teacher_preference.onboardingstepstatus_set.filter(step__stepname='Readiness')[0]
            readiness.status = True
            try:
                readiness.save()
                return True
            except Exception as e:
                print e.message
    return False


def complete_content_dev_readiness(user):
    # content volunteer readiness step complete check
    content_dev_trainings = Training.objects.filter(category='L3 (Content Dev)').values_list('id', flat=True)
    content_dev_completed = user.trainingstatus_set.filter(training__category='L3 (Content Dev)').values_list(
        'training__id', flat=True)
    if set(content_dev_trainings) == set(content_dev_completed):
        userp = user.userprofile
        content_dev_preference = userp.rolepreference_set.filter(role__name='Content Developer')
        if content_dev_preference:
            content_dev_preference = content_dev_preference[0]
            readiness = content_dev_preference.onboardingstepstatus_set.filter(step__stepname='Readiness')[0]
            readiness.status = True

            # intimation mail
            args = {'user': user}
            subject_template = 'mail/se_submit/short.txt'
            subject = get_mail_content(subject_template, args)
            body_template = 'mail/se_submit/full.txt'
            body = get_mail_content(body_template, args)
            # recipients = ["kripa.subramony@evidyaloka.org", user.email]
            recipients = [user.email]
            # recipients.append('akhilraj@headrun.com') # he is Headrun Developer, should not send any emailer to him
            user_mail_config = has_mail_receive_accepted(user, 'Announcement')
            if user_mail_config['user_settings'] or user_mail_config['role_settings']:
                insert_into_alerts(subject, body, ','.join(recipients), user.id, 'email')

            try:
                readiness.save()
                return True
            except Exception as e:
                print e.message
    return False


# ---------------End Training Module ----------------#

# ----------------------Calender---------------------#


def get_calenders(request):
    offer = request.GET.get('offer', '')
    calender_list = []
    if offer:
        offering = Offering.objects.get(pk=offer)
        print offering.course.board_name
        board = offering.course.board_name
        calenders = Calender.objects.filter(board=board)
        print calenders
        calender_list = []
        for ent in calenders:
            cal = {'name': ent.name, 'cal_id': ent.id, 'offer_id': offer}
            calender_list.append(cal)
    return HttpResponse(simplejson.dumps(calender_list), mimetype='application/json')


@csrf_exempt
def apply_calender(request):
    offer_id = request.POST.get('offering', '')
    calender_id = request.POST.get('calender', '')
    submit = request.POST.get('submit', '')
    print submit
    print calender_id
    print offer_id
    if offer_id and calender_id:
        offering = Offering.objects.get(pk=offer_id)
        calender = Calender.objects.filter(pk=calender_id)
        session_list = offering.session_set.all()
        holidays = Holiday.objects.filter(calender=calender).values_list('day', flat=True)
        hol_dates = [x.date() for x in holidays]
        if submit == 'True':
            if session_list and holidays:
                errs = []
                for ent in session_list:
                    if ent.date_start.date() in hol_dates:
                        try:
                            ent.delete()
                        except Exception as e:
                            errs.append(e)
                if len(errs) != 0:
                    return HttpResponse('Some Error Occured')
                else:
                    return HttpResponse('Success')
        elif submit == 'False':
            print "hello"
            if session_list and holidays:
                sess_list = []
                for ent in session_list:
                    print ent.date_start.date()
                    if ent.date_start.date() in hol_dates:
                        sess = {
                            "teacher": ent.teacher.first_name if ent.teacher else '',
                            "time": (ent.date_start).strftime("%d/%m/%Y %I:%M %p"),
                        }
                        sess_list.append(sess)
                return HttpResponse(simplejson.dumps(sess_list), mimetype='application/json')
    return HttpResponse('Error')


# ------------------End Calender---------------------#


def get_refer(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        refers = User.objects.filter(first_name__icontains=q)[:20]
        results = []
        for ent in refers:
            refer_dict = {}
            refer_dict['id'] = ent.id
            userp = UserProfile.objects.get(user_id=ent.id)
            print userp.city
            refer_dict['label'] = ent.first_name + '  ' + ent.last_name
            if userp.city:
                refer_dict['label'] += ' ( ' + userp.city + ' ) '
            refer_dict['value'] = refer_dict['label']
            results.append(refer_dict)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


@csrf_exempt
def bulk_donate(request):
    if request.user.is_superuser:

        res = request.POST.get("res", "")
        print "Entered bulk_pledge"
        record_dict = []

        if 'excelfile' in request.FILES:
            input_excel = request.FILES['excelfile']
            book = xlrd.open_workbook(file_contents=input_excel.read())
            temp = book.sheet_names()
            sheet = book.sheet_by_index(0)
            for row_index in range(2, sheet.nrows):
                record_dict.append(
                    {"amount": sheet.cell(row_index, 8).value, "res_status": sheet.cell(row_index, 9).value,
                     "f_name": sheet.cell(row_index, 0).value, "l_name": sheet.cell(row_index, 1).value,
                     "email": sheet.cell(row_index, 2).value, "phno": sheet.cell(row_index, 12).value,
                     "address": sheet.cell(row_index, 13).value, "city": sheet.cell(row_index, 14).value,
                     "pincode": sheet.cell(row_index, 15).value, "state": sheet.cell(row_index, 16).value,
                     "country": sheet.cell(row_index, 17).value, "pan": sheet.cell(row_index, 10).value,
                     "passport": sheet.cell(row_index, 11).value, "references": sheet.cell(row_index, 18).value,
                     "channel": sheet.cell(row_index, 19).value, "payment_type": sheet.cell(row_index, 20).value,
                     "status": sheet.cell(row_index, 21).value, "donation_type": sheet.cell(row_index, 3).value,
                     "no_of_stud": sheet.cell(row_index, 4).value, "no_of_centers": sheet.cell(row_index, 6).value,
                     "no_of_classrooms": sheet.cell(row_index, 5).value,
                     "donation_time": sheet.cell(row_index, 22).value, "num_months": sheet.cell(row_index, 7).value,
                     "chequenumber": sheet.cell(row_index, 23).value, "chequedate": sheet.cell(row_index, 24).value,
                     "chequebank": sheet.cell(row_index, 25).value,
                     "chequedeposite_date": sheet.cell(row_index, 26).value,
                     "chequecredited_date": sheet.cell(row_index, 27).value,
                     "neft_bank_name": sheet.cell(row_index, 28).value,
                     "neft_transaction_id": sheet.cell(row_index, 29).value,
                     "neft_transaction_date": sheet.cell(row_index, 30).value,
                     "neft_credited_date": sheet.cell(row_index, 31).value})



        else:
            temp = "No File Found"
        print simplejson.dumps(record_dict)
        return render_response(request, 'bulk_donate.html', {"worksheet": temp, "records": record_dict,
                                                             "jrecords": mark_safe(
                                                                 json.dumps(record_dict, ensure_ascii=True))})
    else:
        return HttpResponse("You are not authorized to perform this action....")


@csrf_exempt
def b_pledge(request):
    if request.user.is_superuser:

        print "entered b_pledge"
        rem = request.POST.get("rem", "")
        print "printing rem"
        print rem
        res = request.POST.get("res", "")
        if res != "":
            crem = simplejson.loads(rem)
        else:
            crem = []
        if res != "":
            pres = simplejson.loads(res)
        else:
            pres = []

        # Skipping the selected records from record creation
        temp = []
        for entry in crem:
            temp.append(pres[entry])
        print temp
        print "############################################################################"
        totl_no_recs = len(pres)
        for ele in temp:
            if len(pres) != 0:
                pres.remove(ele)
        print pres
        up_recs = len(pres)
        # Getting batch number and appling it to current list of donations
        batch = get_batch()
        # Log file content updation
        now = (datetime.datetime.utcnow() + timedelta(hours=5, minutes=30))

        content = ["", "", "", ""]
        print len(pres)
        if len(pres) != 0:
            tmp = pres[0]
            content[3] += "\nUploaded Successfully - Channel: %s, Batch No: %s - Time: %s\n\n" % (
            tmp["channel"], str(batch), now.strftime("%d/%m/%Y %I:%M %p"))
            content[3] += "No of Records in the File : %d\n" % totl_no_recs
            content[3] += "No of Records Uploaded : %d\n\n\n\n" % up_recs
            content[
                3] += "###################################################   UPLOADED RECORDS ##########################################################\n"

        else:
            pass
        # End log file content updation
        for ent in pres:
            pledge_details = {}
            pledge_details_mail = {}
            pledge_details["address"] = ent["address"]
            pledge_details["address2"] = ""
            pledge_details["amount"] = int(ent["amount"])
            pledge_details["channel"] = ent["channel"]
            pledge_details["city"] = ent["city"]
            pledge_details["country"] = ent["country"]
            pledge_details["comments"] = ""
            pledge_details["donation_time"] = datetime.datetime.now()
            pledge_details["donation_type"] = ent["donation_type"]
            pledge_details["email"] = ent["email"]
            pledge_details["name"] = ent["f_name"]
            pledge_details["last_name"] = ent["l_name"]
            pledge_details["num_centers"] = ent["no_of_centers"]
            pledge_details["num_classrooms"] = ent["no_of_classrooms"]
            pledge_details["num_months"] = ent["num_months"]
            pledge_details["num_students"] = ent["no_of_stud"]
            pledge_details["num_subjects"] = 0
            pledge_details["pan_number"] = ent["pan"]
            pledge_details["passport_number"] = ent["passport"]
            pledge_details["payment_type"] = ent["payment_type"]
            pledge_details["phone"] = ent["phno"]
            pledge_details["pincode"] = ent["pincode"]
            pledge_details["reference"] = ent["references"]
            pledge_details["resident"] = ent["res_status"]
            pledge_details["state"] = ent["state"]
            pledge_details["status"] = "pending"
            pledge_details["batch_no"] = batch
            ayfy = Ayfy.objects.filter(types='Financial Year')
            for ent in ayfy:
                if pledge_details['donation_time'] >= ent.start_date and pledge_details[
                    'donation_time'] <= ent.end_date:
                    pledge_details['financial_year'] = ent
            try:
                email = pledge_details["email"]
                email_user = User.objects.filter(email=email)

                recipients = []
                is_existing_user = False
                password = ""

                if email_user:
                    email_user = email_user[0]
                    recipients.append(email_user)
                    is_existing_user = True
                else:
                    user = User(username=email, email=email)
                    # password = User.objects.make_random_password()
                    password = email.split("@")[0]
                    user.first_name = pledge_details["name"]
                    user.last_name = pledge_details["last_name"]
                    user.set_password(password)
                    user.is_active = True
                    user.save()

                    userProfile = user.userprofile
                    userProfile.email = email
                    userProfile.phone = pledge_details["phone"]
                    userProfile.city = pledge_details["city"]
                    userProfile.state = pledge_details["state"]
                    userProfile.country = pledge_details["country"]
                    userProfile.save()

                    wellwisher = Role.objects.get(name="Well Wisher")
                    teacher = Role.objects.get(name="Teacher")

                    userProfile.pref_roles.remove(teacher)
                    userProfile.pref_roles.add(wellwisher)

                    userProfile.role.add(wellwisher)
                    userProfile.save()

                    email_user = user

                pledge_details["user"] = email_user

                donation = Donation(**pledge_details)

                donation.save()

                content[
                    3] += "Donation by : %s  of Amount : %d   Type : %s    Through : %s    Created... With ID : %s \n" % (
                donation.name, int(donation.amount), donation.donation_type, donation.payment_type, int(donation.id))
                pledge_details["is_existing_user"] = is_existing_user
                pledge_details["password"] = password

                admins = User.objects.filter(is_superuser=True)
                pledge_details_mail["name"] = str(pledge_details["name"])
                pledge_details_mail["last_name"] = str(pledge_details["last_name"])
                pledge_details_mail["payment_type"] = str(pledge_details["payment_type"])
                pledge_details_mail["amount"] = int(pledge_details["amount"])
                pledge_details_mail["donation_type"] = str(pledge_details["donation_type"])
                pledge_details_mail["password"] = str(pledge_details["password"])
                pledge_details_mail["email"] = str(pledge_details["email"])
                if pledge_details["payment_type"] != "online":
                    _send_mail([email_user], '_pledge', pledge_details_mail)
                    print pledge_details_mail

                    # _send_mail(admins, '_pledge', pledge_details)
                elif password:
                    print pledge_details_mail
                    # if password is not empty a new user is created
                    _send_mail([email_user], '_pledge', pledge_details_mail)
                # return HttpResponse(json.dumps({"status": "success", "donation_id": donation.id}), mimetype="application/json", status=200)
            except Exception as e:
                print "Exception"
                print e
                # return HttpResponse(json.dumps({"status": "error", "message": str(e)}), mimetype="application/json", status=500)
        # log email content
        print "Entered log "
        print now
        content[0] = "Log of Bulk donation dated : %s" % now.strftime("%d/%m/%Y %I:%M %p")
        content[1] = "Please find the attachment for log details..."
        content[2] = "praneeth1249@evidyaloka.org"

        temp = "LOG-%s" % now.strftime("%d-%m-%Y_%I-%M_%p")
        result = send_log(temp, content)

        return HttpResponse("ok")
    else:
        return HttpResponse("You are not authorized to perform this action....")


@csrf_exempt
def bulk_pledge(request):
    if request.user.is_superuser:
        if 'excelfile' in request.FILES:
            don_status = []
            recpt_flg = request.POST.get('gen_recpt')
            input_excel = request.FILES['excelfile']
            print input_excel.name
            b_path = os.getcwd()
            path = b_path + '/web/tool/eReceipt/Process_Excels/' + input_excel.name
            dest = open(path, 'wb+')
            for chunk in input_excel.chunks():
                dest.write(chunk)
            dest.close()
            if recpt_flg == 'on':
                import subprocess
                file_path = os.path.join(os.getcwd(), 'web/tool/eReceipt/e-receipt.py')
                command = 'python   %s -f  %s' % (file_path, input_excel.name)
                msg = subprocess.check_output(command, shell=True)
                # code for marking donation status complete and updating receipient url
            else:
                import shutil
                dest = b_path + '/web/tool/eReceipt/Processed_Excels/' + input_excel.name
                shutil.move(path, dest)
            path2 = b_path + '/web/tool/eReceipt/Processed_Excels/' + input_excel.name
            book = xlrd.open_workbook(path2)
            temp = book.sheet_names()
            sheet = book.sheet_by_index(0)
            for row_index in range(1, sheet.nrows):
                print os.getcwd()
                rpt_pth = 'static/uploads/donation_receipts/pdf_files/%s_%s_donation_receipt.pdf' % (
                sheet.cell_value(row_index, 2).strip().replace(' ', '_'), str(int(sheet.cell_value(row_index, 1))))
                rpt_pth1 = os.getcwd() + "/" + rpt_pth
                print rpt_pth1
                if recpt_flg == 'on':
                    if os.path.isfile(rpt_pth1):
                        don_status.append({"id": int(sheet.cell(row_index, 0).value), "url": rpt_pth,
                                           "recpt_no": sheet.cell(row_index, 1).value})
                else:
                    don_status.append({"id": int(sheet.cell(row_index, 0).value), "url": rpt_pth,
                                       "recpt_no": sheet.cell(row_index, 1).value})
            print don_status
            for ent in don_status:
                print ent
                donation = Donation.objects.get(pk=ent["id"])
                if donation:
                    donation.status = 'completed'
                    print ent["url"]
                    donation.receipt_no = int(ent['recpt_no'])
                    print int(ent['recpt_no'])
                    donation.receipt = ent['url']
                    donation.save()
        return render_response(request, 'bulk_pledge.html', {})
    else:
        return HttpResponse("You are not authorized to perform this action...")


def get_batch():
    last_donation = Donation.objects.filter(~Q(batch_no="")).order_by('id').reverse()[0]
    if last_donation:
        batch = last_donation.batch_no
        batch = int(batch) + 1
    else:
        batch = 1
    return int(batch)


def send_log(file_name, content):
    file_nm = file_name
    module_dir = os.getcwd()
    file_path = module_dir + '/static/logs/bulk_donation/' + file_nm + '.txt'
    print file_path
    txt_file = open(file_path, 'w')
    if content[3]:
        txt_file.write(content[3])
        txt_file.close()
    else:
        txt_file.write("No log content written...")
        txt_file.close()
    # sending Email to uploader
    msg = EmailMultiAlternatives(content[0], content[1], settings.DEFAULT_FROM_EMAIL, content[2].split(','))
    msg.attach_file(file_path)
    msg.send()
    print "email sent"
    return "ok"


def recur_pledge(request):
    pledge_detailsc = {}
    nofpay = int(request.POST.get("noofpay", "1"))
    today = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    tempday = today
    date_list = []
    date_list.append(today)
    period = request.POST.get("period", "monthly")
    if period == "monthly":
        for i in range(1, nofpay):
            date_list.append(tempday + relativedelta(months=1))
            tempday += relativedelta(months=1)
    elif period == "quarterly":
        for i in range(1, nofpay):
            date_list.append(tempday + relativedelta(months=3))
            tempday += relativedelta(months=3)
    elif period == "halfyearly":
        for i in range(1, nofpay):
            date_list.append(tempday + relativedelta(months=6))
            tempday += relativedelta(months=6)
    elif period == "annually":
        for i in range(1, nofpay):
            date_list.append(tempday + relativedelta(years=1))
            tempday += relativedelta(years=1)
    print date_list
    print "noofpay:%d" % nofpay
    # Content of Log file to send to admin
    log = ["", "", "", ""]
    log[0] = "Recurring Donation Dated : %s" % (today.strftime('%d-%b-%y %H:%M %p'))
    log[1] = "Please find the attachment to view the log details..."
    # log[2] = "akhilraj@headrun.com"  # hard coded to avoid unnecessary emails to all admins
    log[2] = "venkat.sriraman@evidyaloka.org"  # hard coded to avoid unnecessary emails to all admins
    log[3] += "Total Records to be created : %d \n\n" % nofpay
    log[3] += "################################  Recurring Donation  By " + request.POST.get('first_name',
                                                                                             '') + "  ##################################\n\n\n"
    for i in range(1, nofpay + 1):
        pledge_details = {}
        print "entered pledge"
        pledge_details["amount"] = request.POST.get("emi")
        pledge_details["address"] = request.POST.get("address", "")
        pledge_details["address2"] = request.POST.get("address2", "")
        pledge_details["channel"] = request.POST.get("channel", "Others")
        pledge_details["city"] = request.POST.get("city", "")
        pledge_details["country"] = request.POST.get("country", "")
        pledge_details["comments"] = request.POST.get("comments", "")
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
        referer_id = request.POST.get("reference_id", "")
        recurr_donation = request.POST.get("recurr")
        print recurr_donation
        if referer_id:
            referer = User.objects.get(pk=referer_id)
            pledge_details["reference_id"] = referer
        pledge_details["state"] = request.POST.get("state", "")
        pledge_details["status"] = request.POST.get("status", "pending")
        pledge_details['donation_time'] = date_list[i - 1]
        try:
            email = pledge_details["email"]
            email_user = User.objects.filter(email=email)
            recipients = []
            is_existing_user = False
            password = ""
            if email_user:
                email_user = email_user[0]
                recipients.append(email_user)
                is_existing_user = True
            else:
                user = User(username=email, email=email)
                # password = User.objects.make_random_password()
                password = email.split("@")[0]
                user.first_name = pledge_details["name"]
                user.last_name = pledge_details["last_name"]
                user.set_password(password)
                user.is_active = True
                user.save()

                userProfile = user.userprofile
                userProfile.email = email
                userProfile.phone = pledge_details["phone"]
                userProfile.city = pledge_details["city"]
                userProfile.state = pledge_details["state"]
                userProfile.country = pledge_details["country"]
                userProfile.save()

                wellwisher = Role.objects.get(name="Well Wisher")
                teacher = Role.objects.get(name="Teacher")

                userProfile.pref_roles.remove(teacher)
                userProfile.pref_roles.add(wellwisher)

                userProfile.role.add(wellwisher)
                userProfile.save()

                email_user = user

            pledge_details["user"] = email_user

            donation = Donation(**pledge_details)

            donation.save()
            log[3] += "===>Donation record with id : %s and date : %s created successfully.\n" % (
            donation.id, donation.donation_time.strftime('%d-%b-%y %I:%M %p'))

            pledge_details["is_existing_user"] = is_existing_user
            pledge_details["password"] = password

            admins = User.objects.filter(is_superuser=True)
            pledge_detailsc = pledge_details
            if i == nofpay:
                pledge_detailsc['amount'] = request.POST.get('amount', "")
                if pledge_detailsc["payment_type"] != "online":
                    _send_mail([email_user], '_pledge', pledge_detailsc)
                    # _send_mail(admins, '_pledge', pledge_details)
                elif password:
                    # if password is not empty a new user is created
                    _send_mail([email_user], '_pledge', pledge_detailsc)
        except Exception as e:
            print "Exception"
            print e
            log[3] += '===> %s.\n' % e
    log_name = "/Recurringlogs/Recur donation" + today.strftime('%d-%b-%y %I:%M %p')
    send_log(log_name, log)
    return "ok"


def load_receipts(request):
    if request.user.is_superuser:
        try:
            for f in request.FILES.getlist('files'):
                print os.getcwd()
                base_path = os.getcwd()
                recpt_path = os.getcwd() + '/static/uploads/donation_receipts/pdf_files/' + f.name
                dest = open(recpt_path, 'wb+')
                for chunk in f.chunks():
                    dest.write(chunk)
                dest.close()
        except:
            return HttpResponse("Some Error occured while upload")
        return render_response(request, 'bulk_pledge.html', {})
    else:
        return HttpResponse('You are not authorized to perform this action')


def pledge(request):
    recurr_donation = request.POST.get("recurr")

    if recurr_donation == "onetime":
        pledge_details = {}
        print "entered pledge"
        pledge_details["address"] = request.POST.get("address", "")
        pledge_details["address2"] = request.POST.get("address2", "")
        pledge_details["amount"] = int(request.POST.get("amount", "0"))
        pledge_details["channel"] = request.POST.get("channel", "Others")
        pledge_details["city"] = request.POST.get("city", "")
        pledge_details["country"] = request.POST.get("country", "")
        pledge_details["comments"] = request.POST.get("comments", "")
        pledge_details["donation_time"] = datetime.datetime.now()
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
        referer_id = request.POST.get("reference_id", "")
        print recurr_donation
        if referer_id:
            referer = User.objects.get(pk=referer_id)
            pledge_details["reference_id"] = referer
        pledge_details["state"] = request.POST.get("state", "")
        pledge_details["status"] = request.POST.get("status", "pending")
        ayfy = Ayfy.objects.filter(types='Financial Year')
        for ent in ayfy:
            if pledge_details['donation_time'] >= ent.start_date and pledge_details['donation_time'] <= ent.end_date:
                pledge_details['financial_year'] = ent
        try:
            email = pledge_details["email"]
            email_user = User.objects.filter(email=email)
            recipients = []
            is_existing_user = False
            password = ""
            if email_user:
                email_user = email_user[0]
                recipients.append(email_user)
                is_existing_user = True
            else:
                user = User(username=email, email=email)
                # password = User.objects.make_random_password()
                password = email.split("@")[0]
                user.first_name = pledge_details["name"]
                user.last_name = pledge_details["last_name"]
                user.set_password(password)
                user.is_active = True
                user.save()

                userProfile = user.userprofile
                userProfile.email = email
                userProfile.phone = pledge_details["phone"]
                userProfile.city = pledge_details["city"]
                userProfile.state = pledge_details["state"]
                userProfile.country = pledge_details["country"]
                userProfile.save()

                wellwisher = Role.objects.get(name="Well Wisher")
                teacher = Role.objects.get(name="Teacher")

                userProfile.pref_roles.remove(teacher)
                userProfile.pref_roles.add(wellwisher)

                userProfile.role.add(wellwisher)
                userProfile.save()

                email_user = user

            pledge_details["user"] = email_user

            donation = Donation(**pledge_details)

            donation.save()

            pledge_details["is_existing_user"] = is_existing_user
            pledge_details["password"] = password

            admins = User.objects.filter(is_superuser=True)

            if pledge_details["payment_type"] != "online":
                _send_mail([email_user], '_pledge', pledge_details)
                print pledge_details

                # _send_mail(admins, '_pledge', pledge_details)
            elif password:
                print pledge_details
                # if password is not empty a new user is created
                _send_mail([email_user], '_pledge', pledge_details)
            return HttpResponse(json.dumps({"status": "success", "donation_id": donation.id}),
                                mimetype="application/json", status=200)
        except Exception as e:
            print "Exception"
            print e
            return HttpResponse(json.dumps({"status": "error", "message": str(e)}), mimetype="application/json",
                                status=500)
    else:
        py_type = request.POST.get("payment_type", "")
        if py_type != 'online':
            recur_pledge(request)
            return HttpResponse(json.dumps({"status": "success"}), mimetype="application/json", status=200)
        else:
            return HttpResponse('Online option is not available for recurring donation')


@login_required
def donate_dash(request):
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    try:
        if from_date and to_date:
            from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')
            to_date = to_date + timedelta(hours=23, minutes=59, seconds=59) 
            from_date = datetime.datetime.strftime(from_date, "%Y-%m-%d %H:%M:%S")
            to_date = datetime.datetime.strftime(to_date, "%Y-%m-%d %H:%M:%S")
            donations = Donation.objects.filter(donation_time__range=[from_date, to_date], is_deleted='no').order_by("id").reverse()
            return render_response(request, 'donate_dash.html', {"donations": donations})
        else:
            donations = Donation.objects.filter(is_deleted='no').order_by("id").reverse()
            return render_response(request, 'donate_dash.html', {"donations": donations})
    except Exception as e:
        print e


@login_required
def update_pledge_admin(request):
    post_data = request.POST

    donation_id = post_data.get("id")
    print donation_id
    if not donation_id:
        return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}),
                            mimetype="application/json", status=500)

    donation = Donation.objects.filter(id=donation_id)

    if not donation:
        print "no donation found"
        return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}),
                            mimetype="application/json", status=500)

    donation = donation[0]

    donation.chequenumber = post_data.get("chequenumber", "")
    donation.chequedate = post_data.get("chequedate", "")
    donation.chequebank = post_data.get("chequebank", "")
    donation.checkdeposite_date = post_data.get("checkdeposite_date", "")
    donation.cheque_credited_date = post_data.get("cheque_credited_date", "")
    donation.neft_bank_name = post_data.get("neft_bank_name", "")
    donation.neft_transaction_id = post_data.get("neft_transaction_id", "")
    donation.neft_transaction_date = post_data.get("neft_transaction_date", "")
    donation.neft_credited_date = post_data.get("neft_credited_date", "")
    donation.online_msg = post_data.get("online_msg", "")
    donation.online_resp_msg = post_data.get("online_resp_msg", "")
    donation.recipent_url = post_data.get("recipent_url", "")
    donation.transaction_key = post_data.get("transaction_key", "")

    try:
        donation.save()
        return HttpResponse(json.dumps({"status": "success"}), \
                            mimetype="application/json", \
                            status=200)
    except Exception as e:
        print e
        return HttpResponse(json.dumps({"status": "error", "message": str(e)}), \
                            mimetype="application/json", \
                            status=500)


def forum(request):
    user_state_forums = []
    user_subject_forums = []
    user_admin_forums = []
    user_center_forums = []
    curr_user = request.user
    usernam = ""

    general_forums = [{"name": "Teacher Discussion Forum", "url": "forum-tdf"},
                      {"name": "Content Development Forum", "url": "forum-cdf"},
                      {"name": "School Education in India", "url": "forum-sei"}]
    state_forums = [
        {"name": "Teachers of Jharkhand Centers", "url": "forum-tjc"},
        {"name": "Teachers of Andhra Pradesh", "url": "forum-tapc"},
        {"name": "Teachers of Tamil Nadu Centers", "url": "forum-ttnc"},
        {"name": "Teachers of Karnataka Centers", "url": "forum-tkc"}]

    subject_forums = [
        {"name": "English Teachers Forum", "url": "forum-etf"},
        {"name": "Science Teachers Forum", "url": "forum-stf"},
        {"name": "Maths Teachers Forum", "url": "forum-mtf"}]

    admin_forums = [{"name": "eVidyaloka Class Admins", "url": "evlclassadmins"}]

    center_forums = [
        {"name": "Bero Hira", "center_id": 20, "url": "evlbero-hira-teachers"},
        {"name": "Bero Moti", "center_id": 26, "url": "evlberomotiteachers"},
        {"name": "Chachgura Hira", "center_id": 18, "url": "evlcgura-hira-teachers"},
        {"name": "Chachgura Moti", "center_id": 19, "url": "evlcgura-moti-teachers"},
        {"name": "Tikratoli Hira", "center_id": 5, "url": "evltikratoliteachers"},
        {"name": "Tikratoli Moti", "center_id": 10, "url": "evlttolimotiteachers"},
        {"name": "Koyritola Hira", "center_id": 22, "url": "evl-koyritola-hira-teachers"},
        {"name": "Koyritola Moti", "center_id": 34, "url": "evl-koyritola-moti-teachers"},
        {"name": "Mirzaganj Hira", "center_id": 27, "url": "evl-mirzaganj-hira-teachers"},
        {"name": "Mirzaganj Moti", "center_id": 28, "url": "evl-mirzaganj-moti-teachers"},
        {"name": "Shitalpur", "center_id": 33, "url": "evl-shitalpur-teachers"},
        {"name": "Udnabad Hira", "center_id": 21, "url": "evl-udnabad-hira-teachers"},
        {"name": "Udnabad Moti", "center_id": 22, "url": "evl-udnabad-moti-teachers"},
        {"name": "Laxmipuram", "center_id": 30, "url": "evl-laxmipuram-teachers"},
        {"name": "Chittela", "center_id": 25, "url": "evlchittela-teachers"},
        {"name": "Juvvalapalem", "center_id": 3, "url": "evljpalemteachers"},
        {"name": "Kishkindapalem", "center_id": 13, "url": "evlkpalemteachers"},
        {"name": "Mallela - Mutyalu", "center_id": 24, "url": "evlmallela-mutyalu-teachers"},
        {"name": "Mallela - Vajralu", "center_id": 23, "url": "evlmallela-vajralu-teachers"},
        {"name": "Pesarlanka", "center_id": 12, "url": "evlplanka-v-teachers"},
        {"name": "Rolupadi", "center_id": 15, "url": "evlrolupaditeachers"},
        {"name": "Vamakuntla", "center_id": 32, "url": "evl-vamakuntla-teachers"},
        {"name": "TopSlip", "center_id": 9, "url": "evltopslipteachers"},
        {"name": "Vidhyashram", "center_id": 7, "url": "evlvidhyashramteachers"},
        {"name": "Vettuvanum", "center_id": 31, "url": "evlvettuvanam-teachers"}]
    lg_bttn = 0
    print user_admin_forums
    if curr_user.is_authenticated():
        usernam = curr_user.first_name
        lg_bttn = 1
        curr_user_p = curr_user.userprofile
        user_state_forums = state_forums
        user_subject_forums = subject_forums
        center_ids = []
        if has_role(curr_user_p, "Teacher"):
            teacher_centers = Session.objects.filter(teacher_id=curr_user.id).values_list(
                'offering__center__id').distinct()
            if len(teacher_centers) > 0:
                teach_cntr_ids = []
                for entryy in teacher_centers:
                    teach_cntr_ids.append(int(entryy[0]))
                for entr in center_forums:
                    if entr["center_id"] in teach_cntr_ids:
                        user_center_forums.append(entr)
        if has_role(curr_user_p, "Center Admin"):
            user_admin_forums = admin_forums
            user_centers = Center.objects.filter(admin=curr_user)
            if len(user_centers) > 0:
                center_ids = []
                for ent in user_centers:
                    center_ids.append(ent.id)
                for entry in center_forums:
                    if entry["center_id"] in center_ids:
                        user_center_forums.append(entry)
        if curr_user.is_superuser:
            user_admin_forums = admin_forums
            user_center_forums = center_forums
    state_count = len(user_state_forums)
    subject_count = len(user_subject_forums)
    admin_count = len(user_admin_forums)
    center_count = len(user_center_forums)
    uniq_user_center_forums = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in user_center_forums)]
    return render_response(request, 'forum.html', {"general_forums": general_forums, "state_forums": user_state_forums,
                                                   "subject_forums": user_subject_forums,
                                                   "admin_forums": user_admin_forums,
                                                   "center_forums": uniq_user_center_forums, "state_count": state_count,
                                                   "subject_count": subject_count, "admin_count": admin_count,
                                                   "center_count": center_count, "lg_bttn": lg_bttn,
                                                   "curr_user": usernam})


def volunteer_active(sender, user, request, **kwargs):
    admins = User.objects.filter(is_superuser=True).filter(email__icontains='@evidyaloka.org').values_list('email')
    recps = []
    if admins:
        for i in admins:
            recps.append(i[0])
    username = user.username
    # status= send_mail('New user Activated  - ' +  str(user.id), 'Hi,  \n'+username+ '  with id :  ' +str(user.id)+ '   has activated his/her account.\n\n' + 'Regards,\n' + 'eVidyaloka System', settings.DEFAULT_FROM_EMAIL, recps, fail_silently=False)
    sub = 'New user Activated  - ' + str(user.id)
    body = 'Hi,  \n' + username + '  with id :  ' + str(
        user.id) + '   has activated his/her account.\n\n' + 'Regards,\n' + 'eVidyaloka System'
    insert_into_alerts(sub, body, ','.join(recps), user.id, 'email')
    host = 'http://' + request.META['HTTP_HOST']
    try:
        UserSocialAuth.objects.get(user_id=user.id)
        fb_user = True
    except:
        fb_user = False
    _send_html_mail(user, '_volunteer_joined', {"username": user.username, "host": host, "fb_user": fb_user})


user_activated.connect(volunteer_active)


def _send_html_mail(users, template_dir, args):
    if not isinstance(users, Iterable):
        users = [users]

    users = set(users)

    recipients = []
    userid = ''
    for user in users:
        try:
            email = user.email
            userid = user.id
            user_mail_config = has_mail_receive_accepted(user, 'Announcement')
            if user_mail_config['user_settings'] or user_mail_config['role_settings']:
                recipients.append(email)
        except UserProfile.DoesNotExist:
            pass

    if not recipients:
        return
    subject_template = 'mail/%s/short.txt' % template_dir
    subject = get_mail_content(subject_template, args).replace('\n', '')

    body_template = 'mail/%s/full.txt' % template_dir
    body_template_html = 'mail/%s/fullhtml.html' % template_dir
    body_plain = get_mail_content(body_template, args)
    body_html = get_mail_content(body_template_html, args)

    insert_into_alerts(subject, body_html, ','.join(recipients), userid, 'email')


def get_mail_content(template_path, args):
    t = template.loader.get_template(template_path)
    c = Context(args)
    data = t.render(c)

    return data


def _send_mail(users, template_dir, args,mail_receive_text='Announcement'):
    if isinstance(users[0], unicode):
        pass
    if not isinstance(users, Iterable):
        users = [users]

    users = set(users)

    userid = ''
    recipients = []
    for user in users:
        try:
            email = user.email
            userid = user.id
            user_mail_config = has_mail_receive_accepted(user, mail_receive_text)
            if user_mail_config['user_settings'] or user_mail_config['role_settings']:
                recipients.append(email)
        except UserProfile.DoesNotExist:
            pass

    if not recipients:
        return

    subject_template = 'mail/%s/short.txt' % template_dir
    subject = get_mail_content(subject_template, args).replace('\n', '')

    body_template = 'mail/%s/full.txt' % template_dir
    body = get_mail_content(body_template, args)
    if mail_receive_text == "Reset_Password":
        status = 'Success'
    else:
        status = "pending"

    insert_into_alerts(subject, body, ','.join(recipients), userid, 'email',status=status)


def has_pref_role(self, role):
    if len(self.pref_roles.filter(name=role)) > 0:
        return True
    else:
        return False


def has_role(self, role):
    if len(self.role.filter(name=role)) > 0:
        return True
    else:
        return False


def render_response(request, template, data=None):
    data = data or {}
    r = RequestContext(request)
    data['ref_path'] = request.get_full_path()
    return render_to_response(template, data, context_instance=r)


def get_centers(location=None, subject=None, medium=None, status=None, center_id=None):
    centers = Center.objects.all()
    centers_set = set(centers)
    centers_by_location = centers_set
    centers_by_subject = centers_set
    centers_by_medium = centers_set
    centers_by_status = centers_set

    if location != "all":
        centers_by_location = set(centers.filter(state=location))
    if subject != "all":
        centers_by_subject = []
        for offering in Offering.objects.filter(course__subject=subject):
            centers_by_subject.append(offering.center)
        centers_by_subject = set(centers_by_subject)
    if medium != "all":
        centers_by_medium = set(centers.filter(language=medium))

    if status != "all":
        centers_by_status = set(centers.filter(status=status))

    centers = set.intersection(centers_by_location, centers_by_subject, centers_by_medium, centers_by_status)
    if center_id:
        centers = Center.objects.filter(id=center_id)

    return centers


# home page for the users
def home(request):
    sesstion_rating_flag = request.GET.get('session_rating_flag', '')
    sesstion_rating_session_id = request.GET.get('session_id', '')
    if request.user.is_authenticated():
        try:
            pref_med = request.user.userprofile.pref_medium
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect('/v2/update_no_profile/')
        centers_pending = Center.objects.filter(offering__status='pending', language=pref_med).annotate(
            Count('offering')) \
                              .values('id', 'name', 'offering__count').order_by('-offering__count')[:3]
    else:
        centers_pending = Center.objects.filter(offering__status='pending').annotate(Count('offering')) \
                              .values('id', 'name', 'offering__count').order_by('-offering__count')[:3]
    centers_data = []
    for cent in centers_pending:
        temp = {}
        center = Center.objects.get(id=cent['id'])
        center_image = "http://placehold.it/255x170/F15A22/fff/&text=" + center.name
        if center.photo:
            center_image = "/" + str(crop(center.photo, "255x170"))
        if center.description:
            center_desc = (
                        (center.description)[:70] + '.. <span style="color:#2EC7F0;cursor:pointer">Know more >></span>') \
                if len(center.description) > 70 else center.description
        else:
            center_desc = 'No description available'
        center_offers = center.offering_set.all()
        running_offers = center_offers.filter(status='running')

        demand_slot_booked = Demandslot.objects.filter(center=center, status='Booked').values_list('offering',
                                                                                                   flat=True).distinct()
        if demand_slot_booked:
            pending_offers = center_offers.filter(status='pending').exclude(id__in=demand_slot_booked)
        else:
            pending_offers = center_offers.filter(status='pending')

        if not pending_offers:
            continue

        temp_buffer = pending_offers.values_list('id', 'course__grade', 'course__subject')
        pcourses_data = []
        for x in temp_buffer:
            p_dict = {}
            p_id, p_grade, p_sub = x[0], make_number_verb(x[1]), x[2]
            p_dict['id'] = p_id
            p_dict['grade'] = p_grade
            p_dict['subject'] = p_sub
            pcourses_data.append(p_dict)

        if not pcourses_data:
            continue

        tags = {}
        sub_list = list(pending_offers.values_list('course__subject', flat=True).distinct())
        tags['subjects'] = [i.replace(' ', '_') for i in sub_list]
        tags['months'] = [x.strftime('%B') for x in pending_offers.values_list('start_date', flat=True).distinct()]
        centers_data.append({'id': center.id,
                             'title': center.name,
                             'description': center_desc,
                             'image': center_image,
                             'pending_courses': pending_offers.count(),
                             'running_courses': running_offers.count(),
                             'tags': tags})

    home_pg = request.GET.get('home', '')
    supply = demands = []
    show_popup = request.GET.get("show_popup", None)
    popup_type = request.GET.get("type", None)
    show_popup = {"show_popup": show_popup, "type": popup_type}
    if sesstion_rating_flag:
        active_users, total = None, None
        total_after_april, total_session = None, None
        active_students, total_students = None, None
        return render_response(request, 'new_home_temp.html',
                               {"demand": demand, "supply": supply, "show_popup": show_popup,
                                "active_users": active_users, "total": total, "total_after_april": total_after_april,
                                "total_session": total_session, 'active_students': active_students,
                                'total_students': total_students, 'centers_data': centers_data,
                                'session_rating_flag': sesstion_rating_flag, 'session_id': sesstion_rating_session_id})

    user = request.user
    if not home_pg:
        if user.is_authenticated():
            if request.user.partner_set.values():
                return HttpResponseRedirect(reverse('myevidyaloka'))
            if has_pref_role(user.userprofile, "Teacher") or has_role(user.userprofile,
                                                                      "Center Admin") or user.is_superuser:
                return HttpResponseRedirect(reverse('myevidyaloka'))
            elif has_pref_role(user.userprofile, "vol_admin") or has_role(user.userprofile,
                                                                          "vol_co-ordinator") or user.is_superuser:
                return redirect('/task_list/')

    active_users, total = None, None
    total_after_april, total_session = None, None
    active_students, total_students = None, None
    # home_new.html
    print "demand", demand, "supply", supply, "show_popup", show_popup, "active_users", active_users, "total", total, "total_after_april", total_after_april, "total_session", total_session, 'active_students', active_students, 'total_students', total_students, 'centers_data', centers_data
    return render_response(request, 'new_home_temp.html',
                           {"demand": demand, "supply": supply, "show_popup": show_popup, "active_users": active_users,
                            "total": total, "total_after_april": total_after_april, "total_session": total_session,
                            'active_students': active_students, 'total_students': total_students,
                            'centers_data': centers_data, 'session_rating_flag': sesstion_rating_flag,
                            'session_id': sesstion_rating_session_id})


def get_students_ratio():
    active_students = Student.objects.filter(status="Active")
    total_students = Student.objects.all()

    return len(active_students), len(total_students)


def get_active_user():
    userp = UserProfile.objects.all()
    role_teacher = Role.objects.get(name="Teacher")
    role_centeradmin = Role.objects.get(name="Center Admin")
    active = 0
    inactive = 0
    check = 0
    for user in userp:
        user_roles = user.role.all()
        if role_teacher in user_roles or role_centeradmin in user_roles:
            teacher_session = Session.objects.filter(teacher=user.user)
            admin_center = Center.objects.filter(admin=user.user)
            check += 1
            if len(teacher_session) > 0 or len(admin_center) > 0:
                active += 1
        else:
            inactive += 1

    return active, len(userp)


def get_class_ratio():
    april = datetime.datetime(day=1, month=4, year=2013)

    completed_sessions_after_april = Session.objects.filter(date_start__gt=april, status="completed")
    running_sessions_after_april = Session.objects.filter(date_start__gt=april, status="started")
    completed_total_sessions = Session.objects.filter(status="completed")
    running_total_sessions = Session.objects.filter(status="started")

    total_after_april = len(completed_sessions_after_april) + len(running_sessions_after_april)
    total_session = len(completed_total_sessions) + len(running_total_sessions)
    constant_value_since_2010 = 1400
    total_session = total_session + constant_value_since_2010
    return total_after_april, total_session


def activity(request):
    return HttpResponse("okay!")


wl_file = open("web/output.json", "r")

WHITE_LIST = json.loads(wl_file.read())


# user profile page, displaying unassigned offerings
def userprofile(request):
    if not request.user.is_authenticated():

        email_id = request.GET.get("email_id")
        user_id = str(request.GET.get("user_id"))
        if not email_id or not user_id:
            return HttpResponseRedirect("/")

        existing_user = None

        for entry in WHITE_LIST:

            if str(entry["id"]) == user_id and email_id == entry["email"]:
                existing_user = entry

        if not existing_user:
            return HttpResponseRedirect("/")

        user = User.objects.get(id=user_id)

        user.backend = 'django.contrib.auth.backends.ModelBackend'

        if not user.is_active:
            return HttpResponseRedirect("/")

        login(request, user)

        return HttpResponseRedirect("/user_profile/")

    sub, profile_percent = [], {'Incomplete': 10, 'Started': 35, 'Inprocess-1': 55, 'Selected': 75, 'Ready': 100}
    prf_status_des = {"Incomplete": "Please fill in the required personal information",
                      "Started": "Please proceed to onboarding",
                      "Inprocess": "Please complete your Self Evaluation and Selection Discussion",
                      "Selected": "Please update your Readiness requirements", "Ready": "Ready"}
    # offerings of the sessions that doesn't have a teacher and language equals to the user prefered medium
    unassigned_offerings = Offering.objects.filter(session__teacher=None, language=request.user.userprofile.pref_medium)
    count = len(unassigned_offerings)
    courses = Course.objects.all()
    for course in courses:
        sub.append(course.subject)
    subjects = list(set(sub))
    subjects.sort()
    subjects_len = len(subjects)

    curr_user = request.user

    user_profile, roles, pref_roles, unassigned_offering_arr, prof_per = [], [], [], [], 35
    user_profile = UserProfile.objects.filter(user=curr_user)
    if user_profile:
        user_profile = user_profile[0]
        usr_prf_status = user_profile.profile_complete_status

        roles = Role.objects.all()
        pref_roles = [role.id for role in user_profile.pref_roles.all()]
        for offering in unassigned_offerings:
            make_course(offering, unassigned_offering_arr, request.user)
        from_date_ts = int(time.mktime(user_profile.from_date.timetuple()) * 1000)
        to_date_ts = int(time.mktime(user_profile.to_date.timetuple()) * 1000)
        is_teacher = False
        is_centeradmin = False
        new_centeradmin = False
        if has_role(user_profile, "Center Admin") and (
                has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher")):
            is_centeradmin = True
            is_teacher = True
        elif has_role(user_profile, "Center Admin"):
            is_centeradmin = True
        elif has_pref_role(user_profile, "Center Admin"):
            new_centeradmin = True
        if has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher"):
            is_teacher = True
        if not curr_user.is_superuser:
            user_centers = Center.objects.filter(admin=curr_user)
        else:
            user_centers = Center.objects.all()

        if is_centeradmin: usr_prf_status = 'Ready'
        if (has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher")) and \
                user_profile.evd_rep and usr_prf_status == 'Inprocess':
            if user_profile.dicussion_outcome != 'Not Scheduled':
                usr_prf_status = 'Selected'
            else:
                usr_prf_status = 'Inprocess-1'

        prof_per = profile_percent.get(usr_prf_status, 0)
        prof_cm_status = "Inprocess" if "Inprocess" in usr_prf_status else usr_prf_status
        prof_cm_des = prf_status_des[prof_cm_status]

    show_error_msg = False
    if request.path == "/myevidyaloka/":
        show_error_msg = True
    now = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30))
    start_time = (datetime.time(9, 0))
    end_time = (datetime.time(18, 0))
    i_tsd = ""
    if now.time() >= start_time and now.time() <= end_time:
        if now.weekday() != 6:
            i_tsd = "intime"
        else:
            i_tsd = "outtime"
    else:
        i_tsd = "outtime"

    prof_list = ['Business and Financial Operations', 'Community and Social Service', 'Computer and Mathematical',
                 'Education, Training, and Library',
                 'Farming, Fishing, and Forestry', 'Healthcare Practitioners and Technical', 'Legal',
                 'Life, Physical, and Social Science', 'Management', 'Military Specific',
                 'Office and Administrative Support', 'Personal Care and Service', 'Production/Manufacturing',
                 'Sales and Related', 'Self-employed', 'Retd. Professional', 'Housewife', 'Others']

    return render_response(request, 'user_profile.html',
                           {"unassigned_offerings": unassigned_offering_arr, "pref_roles": pref_roles,
                            "subjects": subjects, "roles": roles, "user_profile": user_profile, "curr_user": curr_user,
                            "count": count, "i_tsd": i_tsd, "offerings_template": offerings_template,
                            "is_teacher": has_pref_role(request.user.userprofile, "Teacher"),
                            "from_date_ts": from_date_ts, "to_date_ts": to_date_ts, "accept": user_profile.code_conduct,
                            "subjects_len": subjects_len, "is_centeradmin": is_centeradmin, "is_teacher": is_teacher,
                            "user_centers": user_centers, "new_centeradmin": new_centeradmin,
                            "show_error_msg": show_error_msg, "purpose": user_profile.purpose, 'prof_per': prof_per,
                            'prof_cm_status': prof_cm_status, 'prof_cm_des': prof_cm_des, 'prof_list': prof_list});


@login_required
def offerings(request):
    sessions_none = Session.objects.filter(teacher=None)
    return render_response(request, 'offerings.html', {"sessions": sessions_none})


@login_required
def preferences(request):
    return render_response(request, 'preferences.html', {})


# the jquery template for the offerings displayed in userprofile second step
offerings_template = '''

            <tr>
                <td>${center}</td>
                <td>${course_offered}</td>
                <td>${language}</td>
                <td>${start_date}</td>
                <td>${end_date}</td>
                <td><input type="checkbox" value="${offering_id}" {{if is_assigned_offering}}checked="checked"{{/if}} data-subject="${subject}" data-start_date="${start_date_iso }" data-end_date="${end_date_iso}" data-medium="${language}"></td>
            </tr>


'''


# saves user profile and sends a notification to the admins
@login_required
def save_profile(request):
    if request.method == 'POST':
        admins = User.objects.filter(is_superuser=True)
        evladmins = User.objects.filter(is_superuser=True).filter(email__icontains='@evidyaloka.org')
        user = UserProfile.objects.get(user=request.user)
        step = request.POST['step']
        updated_offerings_arr = []
        loose_roles = ['Teacher', 'Content Developer', 'Well Wisher']

        loose_roles = [Role.objects.get(name=name) for name in loose_roles]

        if step == '1':
            request.user.first_name = request.POST['firstname']
            request.user.last_name = request.POST['lastname']
            '''
            #PHASE 2 stuff
            user_with_email = User.objects.filter(email = request.POST['primary_email'])
            if not request.user in user_with_email:
                request.user.email = request.POST['primary_email']
            else:
                return HttpResponse("email_exists", mimetype="text/plain")
            '''
            request.user.email = request.POST['primary_email']
            request.user.save()
            user.time_zone = request.POST['time_zone']
            user.secondary_email = request.POST['secondary_email']
            user.gender = request.POST['gender']
            user.age = str(request.POST['age'])
            user.profession = request.POST['profession']
            user.pref_medium = request.POST['prefered_medium']
            user.country = request.POST['country']
            user.state = request.POST['state']
            user.city = request.POST['city']
            user.referer = request.POST['reference']
            selected_roles = request.POST['prefered_roles']
            user.short_notes = request.POST['short_notes']
            user.referencechannel = request.POST['referencechannel']
            user.phone = request.POST['phone']
            user.skype_id = request.POST['skype_id']
            updated_offerings = Offering.objects.filter(session__teacher=None, language=request.POST['prefered_medium'])
            updated_offerings_arr = []
            for offering in updated_offerings:
                make_course(offering, updated_offerings_arr, request.user)

            if len(selected_roles):
                selected_roles = [Role.objects.get(pk=int(role)) for role in selected_roles.split(";")]
            user_centers = Center.objects.filter(admin=request.user)
            # user.role.clear()
            for role in user.role.filter(type='External'):
                if role.name == 'Partner Admin' or role.id == 10:
                    pass
                else:
                    user.role.remove(role)
            for role in selected_roles:
                if role in loose_roles:
                    user.role.add(role)
                if (role.name == 'Center Admin' or role.name == 'Class Assistant') and user_centers:
                    user.role.add(role)

            user.pref_roles.clear()

            for role in selected_roles:
                user.pref_roles.add(role)
            user.code_conduct = True
            if user.profile_complete_status == 'Incomplete' and request.user.first_name \
                    and request.user.last_name and request.user.email and user.city and user.pref_roles:
                user.profile_complete_status = 'Started'


        elif step == '3':
            user.purpose = request.POST['purpose'].strip()
            user.evd_rep = request.POST.get('evd_rep', '')
            user.self_eval = request.POST.get('self_eval', '')
            user.evd_rep_meet = request.POST.get('evd_rep_meet', '')
            print user.user.first_name

            admin_users = User.objects.filter(id__in=[6815, 9277])

            if user.self_eval:
                for entry in admin_users:
                    _send_mail(entry, '_se_complete',
                               {"firstname": user.user.first_name, "lastname": user.user.last_name,
                                "userid": user.user.id})
            if user.skype_id and user.phone and user.evd_rep and user.trainings_complete and user.computer and user.evd_rep \
                    and user.internet_connection and user.webcam and user.headset and user.profile_complete_status == 'Selected':
                user.profile_complete_status = 'Ready'

            if user.evd_rep and not user.profile_complete_status == 'Selected': user.profile_complete_status = 'Inprocess'
            if not user.evd_rep: user.profile_complete_status = 'Started'

        elif step == '2':
            pref_offerings_str = request.POST['prefered_offerings']
            pref_offerings_list = pref_offerings_str.split(";")
            user.pref_offerings.clear()
            if pref_offerings_str != '':
                query = Q()
                for pref_offer in pref_offerings_list:
                    query = query | Q(id=int(pref_offer))

                pref_offerings = Offering.objects.filter(query)
                user.from_date = datetime.datetime.today()
                user.to_date = datetime.datetime.today() + datetime.timedelta(weeks=6)
                for po in pref_offerings:
                    if po.start_date and user.from_date > po.start_date:
                        user.from_date = po.start_date
                    if po.end_date and user.to_date < po.end_date:
                        user.to_date = po.end_date
                    user.pref_offerings.add(po)

        elif step == '4':
            time_slots = request.POST['prefered_timings']
            pref_days = request.POST['prefered_days']
            if time_slots.endswith(';'):
                time_slots = time_slots[:-1]
            if pref_days.endswith(';'):
                pref_days = pref_days[:-1]
            user.pref_slots = time_slots
            user.from_date = request.POST['from_date']
            user.to_date = request.POST['to_date']
            user.pref_days = pref_days
            user.pref_subjects = request.POST['prefered_subjects']

            user.computer = request.POST.get('computer', '')
            user.internet_connection = request.POST.get('internet_connection', '')
            user.internet_speed = request.POST.get('internet_speed', '')
            user.webcam = request.POST.get('webcam', '')
            user.headset = request.POST.get('head_set', '')
            user.trainings_complete = request.POST.get('trainings_complete', '')
            user.review_resources = request.POST.get('reviwed_resources', '')
            user.trail_class = request.POST.get('trail_class', '')
            user.skype_id = request.POST['skypeid']
            if user.skype_id and user.evd_rep and user.trainings_complete and user.computer \
                    and user.internet_connection and user.webcam and user.headset and user.profile_complete_status == 'Selected':
                user.profile_complete_status = 'Ready'
            elif user.profile_complete_status == 'Ready' or user.profile_complete_status == 'Inprocess':
                user.profile_complete_status = 'Selected'

        user.save()

        offering = user.pref_offerings.all()
        if offering and step == '2':
            for offer in offering:
                admin_q = Q(center=offer.center) | Q(is_superuser=True);
                c_admins = User.objects.filter(admin_q)
                offer_title = make_number_verb(
                    offer.course.grade) + " grade " + offer.course.board_name + " board " + offer.course.subject
                _send_mail(c_admins, '_center_offer',
                           {'offer': offer_title, 'user': request.user, 'center': offer.center.name})
        _send_mail(evladmins, '_user_updated', {'user': request.user})

        if step == '1':

            if len(user.pref_roles.filter(name="Class Assistant")) > 0:
                return HttpResponse("centeradmin")
            if len(user.pref_roles.filter(name="Teacher")) > 0:
                return HttpResponse(simplejson.dumps(updated_offerings_arr), mimetype='application/json')
            elif len(user.pref_roles.filter(name="Center Admin")) > 0:
                return HttpResponse("centeradmin")
            elif len(user.pref_roles.filter(name="Content Developer")) > 0:
                return HttpResponse("contentdeveloper")
            elif len(user.pref_roles.filter(name="Well Wisher")) > 0:
                return HttpResponse("wellwisher")

        if step == '3':
            return HttpResponse(simplejson.dumps(updated_offerings_arr), mimetype='application/json')

    return HttpResponse("ok")


# check whether email exists in db or not
def verify_email(request):
    email = request.GET["email"]
    exists = False
    if len(User.objects.filter(email=email)) > 0:
        exists = True
    return HttpResponse(exists, mimetype="text/plain")


def profile(request):
    print("entering school admin into the profile ...")
    curr_user =  request.user
    user_profile, school_details = [], []
    try:
        curr_user =  request.user
        user_profile, schooladmin_details = [], []
        p_html = 'profile.html'
        user_profile = UserProfile.objects.filter(user = curr_user)
        if user_profile:
            user_profile = user_profile[0]
            prefer_roles = user_profile.pref_roles.all()
            for prefer_role in prefer_roles:
                if prefer_role.name == 'Teacher':
                    user_profile.pref_roles.remove(prefer_role)
                else:
                    pass
            user_location_info = {}
            user_profile_dict = user_profile.get_dict()
            location_fields = ['country', 'state', 'city']
            for k,v in user_profile_dict.iteritems():
                if k in location_fields and v:
                    user_location_info[k] = str(v)
            org = False
            if user_profile.profile_completion_status:
                org = True
        schooladmin_details = Partner.objects.filter(contactperson = curr_user)
        if schooladmin_details:
            schooladmin_details = schooladmin_details[0]
            ref_channel = schooladmin_details.partner_referencechannel
            if ref_channel:
                ref_channel = ref_channel.all()
                if len(ref_channel)>0:
                    ref_channel = ref_channel[0]
            else:
                ref_channel = ''
            # print(" user profile--------------------------------------------------------------", user_profile)
            # print ("partner details =====================================================", schooladmin_details)
            # print('org ==============================', org)
            # print('user location info ===============================', user_location_info)
            # print('reference channel ===========================================', ref_channel)
            # if partner_details.partnertype.values():
            #     p_type = partner_details.partnertype.values()[0]['name']
            #     p_html = 'profile.html'
        prof_list = ['Business and Financial Operations', 'Community and Social Service', 'Computer and Mathematical',
                 'Education, Training, and Library', \
                 'Farming, Fishing, and Forestry', 'Healthcare Practitioners and Technical', 'Legal',
                 'Life, Physical, and Social Science', 'Management', 'Military Specific', \
                 'Office and Administrative Support', 'Personal Care and Service', 'Production/Manufacturing',
                 'Sales and Related', 'Self-employed', 'Retd. Professional', 'Housewife', \
                 'Student - PG', 'Student', 'Others']
        return render(request, p_html, {"user_profile":user_profile,\
                            'schooladmin_details' : schooladmin_details, 'org' : org,\
                            'user_location_info': user_location_info,\
                            'ref_channel' : ref_channel, 'prof_list':prof_list})
    except Exception as e:
        print("Error reason =", e)
        print("Error at line no = ", traceback.format_exc())
    return HttpResponse('ok')


@login_required
def myevidyaloka(request):
    # import pdb; pdb.set_trace()
    user = request.user
    try:
         userp = user.userprofile
    except UserProfile.DoesNotExist:
         return HttpResponseRedirect('/v2/update_no_profile/')
    flag = request.GET.get('flag', '')
   
    if flag:
        save_user_activity(request, 'Logged In', 'Action')
    if request.user.partner_set.values() and request.user.partner_set.values()[0]['role_id'] == '16':
        if userp.organization_complete_status == 'Incomplete' or not userp.organization_complete_status or userp.organization_complete_status == 'False':
            return HttpResponseRedirect('/school/search')
        if not userp.profile_completion_status:
            return profile(request)
        else:
            return stats(request)
    if request.user.partner_set.values():
        if not userp.profile_completion_status:
            return partner_profile(request)
        if not userp.organization_complete_status or \
                user.partner_set.values()[0]['status'] == 'New':
            if request.user.partner_set.all()[0].partnertype.values() and request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 2:
                return deliverypartner_org(request)
            else:
                return organization_details(request)
        if user.partner_set.values()[0]['status'] == 'Approved':
            return stats(request)
        else :
            return role_dashboard(request, 'partneradmin')

    user_profile = UserProfile.objects.filter(user=request.user)[0]
    roles = user_profile.role.values_list('name', flat=True)
    if user.is_authenticated():
        # If user has not filled his profile, we'll render to settings page.
        if user.userprofile.profile_completion_status:
            print(userp.pref_roles.all())
            role_preferences = userp.rolepreference_set.all()
            if role_preferences:
                recommended_role_preferences = role_preferences.filter(role_outcome='Recommended').values_list('role__name', flat=True)
                print(recommended_role_preferences)                            
                try:
                    ordered_roles = ['Delivery co-ordinator', 'Field co-ordinator', 'Partner Account Manager', 'Partner Admin', 'Center Admin', 'Content Admin',
                                     'Content Reviewer', 'Teacher', 'Class Assistant', 'Facilitator Teacher', 'Content Developer']
                    
                    for role in ordered_roles:
                        if role in recommended_role_preferences:
                            role_short_name = role.lower().replace(' ', '').replace('-', '')
                            return role_dashboard(request, role_short_name)
                            
                except Exception as e: pass
                return HttpResponseRedirect('/v2/vLounge')
            
            else:
                if roles:
                    for role in roles:
                        if role == "Field co-ordinator" or role == "Delivery co-ordinator":
                            role_short_name = role.lower().replace(' ', '').replace('-', '')
                            return role_dashboard(request, role_short_name)
        return HttpResponseRedirect('/v2/vLounge')
    else:
        return redirect("/?show_popup=true&type=login")

# students for the selected course in teacherdash(My Students tab)
def mystudents(request):
    user = request.user
    offering_id = int(request.GET.get("id", None))
    if offering_id:
        offering = Offering.objects.filter(id=offering_id)[0]
        students = offering.enrolled_students.all()
        sessions = Session.objects.filter(offering=offering)

        students_json = []
        for stu in students:
            student = {
                "name": stu.name,
                "strengths": stu.strengths,
                "weakness": stu.weakness,
                "observation": stu.observation,
                "id": stu.id
            }
            students_json.append(student)
        return HttpResponse(simplejson.dumps(students_json), mimetype='application/json')


def make_number_verb(num):
    stripped_num = str(num)
    last_num = str(num)[-1]
    if stripped_num == "11":
        return stripped_num + "th"
    elif last_num == "1":
        return stripped_num + "st"
    elif last_num == "2":
        return stripped_num + "nd"
    elif last_num == "3":
        return stripped_num + "rd"
    else:
        return stripped_num + "th"


def make_hour(hour):
    if hour >= 12 and hour <= 23:
        if hour > 12:
            hour = hour - 12
        hour = str(hour) + " PM"
    else:
        hour = str(hour) + " AM"

    return hour


def make_date_time(date_time):
    month_map = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    date_time_arr = {"date": "", "time": ""}
    if not date_time:
        return date_time_arr
    time_str = ""
    mk_time = make_hour(date_time.hour).split(' ')
    # time_str = time_str + make_hour(date_time.hour)
    time_str = time_str + mk_time[0] + " : " + date_time.strftime('%M') + " " + mk_time[1]
    date_str = make_number_verb(date_time.day)
    '''
    if date_time.minute > 0:
        time_str = time_str +":"+ str(date_time.minute)
    else:
        time_str = time_str +":0"+ str(date_time.minute)
    '''

    date_str = date_str + " " + month_map[date_time.month - 1]

    date_time_arr["date"] = date_str
    date_time_arr["time"] = time_str
    date_time_arr["year"] = str(date_time.year)

    return date_time_arr


# dashboard for teachers displaying information on assigned and preferred offerings
@login_required
def teacherdash(request):
    # import pdb; pdb.set_trace()
    assigned_offerings = []
    user1 = request.user
    user_profile = user1.userprofile
    pref_lang = user_profile.pref_medium
    usr_prf_status = user_profile.profile_complete_status
    role_preferences = user_profile.rolepreference_set.all()
    role_status = ''
    if role_preferences:
        statuses = role_preferences.filter(role_id__in=[1,20]).values_list('role_status', flat=True)
        if 'Active' in statuses: role_status = 'Active'
        else:  role_status = 'New'
                
            
        print('role_status',role_status)
    pages_dict = {'Incomplete': '', 'Started': 'preferences', 'Inprocess': 'preferences', 'Selected': 'readiness'}

    if usr_prf_status != 'Ready' and "/user_profile/" in request.META.get("HTTP_REFERER", ''):
        forward_url = "/user_profile/"
        if pages_dict.get(usr_prf_status, ''): forward_url = "/user_profile/?%s" % (pages_dict.get(usr_prf_status, ''))
        return redirect(forward_url)

    is_teacher = False
    if has_role(user_profile, "Teacher") or has_pref_role(user_profile, "Teacher") or has_role(user_profile, 'Facilitator Teacher') or has_pref_role(user_profile, 'Facilitator Teacher'):
        is_teacher = True
    user_pref_offerings = user_profile.pref_offerings.all()
    has_notifications = False
    if not user1.is_superuser:
        user_centers = Center.objects.filter(admin=user1)
    else:
        user_centers = Center.objects.all()

    profile_percent = {'Incomplete': 10, 'Started': 35, 'Inprocess-1': 55, 'Selected': 75, 'Ready': 100}
    prf_status_des = {"Incomplete": "Please fill in the required personal information",
                      "Started": "Update your Onboarding details",
                      "Inprocess": "Please join a Scheduled Event for Orientation / Teacher Selection Discussion that suits you",
                      "Selected": "Please update your Readiness requirements", "Ready": "Ready"}

    if (has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher")) or (has_pref_role(user_profile, "Facilitator Teacher") or has_role(user_profile, "Facilitator Teacher")) and  \
            user_profile.evd_rep and usr_prf_status == 'Inprocess':
        if user_profile.dicussion_outcome != 'Not Scheduled':
            usr_prf_status = 'Selected'
        else:
            usr_prf_status = 'Inprocess-1'

    print usr_prf_status
    prof_per = profile_percent.get(usr_prf_status, 0)
    prof_cm_status = "Inprocess" if "Inprocess" in usr_prf_status else usr_prf_status
    prof_cm_des = prf_status_des[prof_cm_status]

    stack_objects = StackTeacher.objects.filter(teacher=user1)
    stack_arr = []
    if len(stack_objects) > 0:
        has_notifications = True
        for stack_obj in stack_objects:
            if stack_obj.status == "pending":
                notification = {
                    "subject": stack_obj.offering.course.subject,
                    "grade": make_number_verb(stack_obj.offering.course.grade),
                    "start": make_date_time(stack_obj.offering.start_date)["time"],
                    "date": make_date_time(stack_obj.offering.start_date)["date"],
                    "center": stack_obj.offering.center.name,
                    "end_date": make_date_time(stack_obj.offering.end_date)["date"],
                    "id": stack_obj.offering.id
                }
                stack_arr.append(notification)
    session_none = Session.objects.exclude(teacher=None)
    others_session = session_none.exclude(teacher=user1)

    offerings_arr = []
    sessions_arr = []
    user_sessions = Session.objects.filter(teacher=user1).exclude(offering__status='completed').order_by('-date_start')

    assigned_offerings = Offering.objects.filter(session__teacher=user1,center__status='Active').distinct()
    assigned_courses = []
    for assigned_offering in assigned_offerings:
        make_course(assigned_offering, assigned_courses)
    assigned_offerg = []
    offeringslist = assigned_offerings.filter(status='running') 
    start_date = request.POST.get('from','')
    end_date = request.POST.get('to','')
    
    if start_date== '' and end_date =='':
   
        for assigned_offering in offeringslist:
            center = Center.objects.get(pk=assigned_offering.center_id)   
            details = {
            'offeringIdVal': assigned_offering.id,
            'ay_id': assigned_offering.academic_year.id,
            'centerId': center.id,
            'centerIdVal': center.name,
            'digital_school': center.digital_school,
            'assigned_offering_id' : assigned_offering.course.grade+" "+ assigned_offering.course.subject,
            'planned_session' : Session.objects.filter(offering_id=assigned_offering.id ).distinct().count(),
            'completed_session' : Session.objects.filter(offering_id=assigned_offering.id ,status= 'completed').distinct().count(),
            'cancelled_session' : Session.objects.filter(offering_id=assigned_offering.id,status = 'cancelled' ).distinct().count(),
            'offline_session' : Session.objects.filter(offering_id=assigned_offering.id,status = 'offline' ).distinct().count(),
            'scheduled_session' : Session.objects.filter(offering_id=assigned_offering.id,status = 'scheduled' ).distinct().count() }
            assigned_offerg.append(details)

    else: 

        for assigned_offering in offeringslist:
            center = Center.objects.get(pk=assigned_offering.center_id) 
            details = {
            'offeringIdVal': assigned_offering.id,
            'ay_id': assigned_offering.academic_year.id,
            'centerId': center.id,
            'centerIdVal': center.name,
            'digital_school': center.digital_school,
            'assigned_offering_id' :  assigned_offering.course.grade+" "+ assigned_offering.course.subject,
            'planned_session' : Session.objects.filter(offering_id=assigned_offering.id ,date_start__gte=str(start_date)+' 00:00:00',date_end__lt=str(end_date)+' 23:59:59').distinct().count(),
            'completed_session' : Session.objects.filter(offering_id=assigned_offering.id ,status= 'completed',date_start__gte=str(start_date)+' 00:00:00',date_end__lt=str(end_date)+' 23:59:59').distinct().count(),
            'cancelled_session' : Session.objects.filter(offering_id=assigned_offering.id,status = 'cancelled',date_start__gte=str(start_date)+' 00:00:00',date_end__lt=str(end_date)+' 23:59:59').distinct().count(),
            'offline_session' : Session.objects.filter(offering_id=assigned_offering.id,status = 'offline' ,date_start__gte=str(start_date)+' 00:00:00',date_end__lt=str(end_date)+' 23:59:59').distinct().count(),
            'scheduled_session' : Session.objects.filter(offering_id=assigned_offering.id,status = 'scheduled' ,date_start__gte=str(start_date)+' 00:00:00',date_end__lt=str(end_date)+' 23:59:59').distinct().count() }
            assigned_offerg.append(details)
            #print "assigned_offerg",assigned_offerg
    today = datetime.datetime.now()
    indian_time = today + datetime.timedelta(minutes=530)
    upcomming_user_sessions = user_sessions.order_by("date_start").filter(date_start__gte=indian_time)
    for session in upcomming_user_sessions:
        my_class = {
            "subject": session.offering.course.subject,
            "grade": make_number_verb(session.offering.course.grade),
            "start": make_date_time(session.date_start)["time"],
            "date": make_date_time(session.date_start)["date"],
            "day": session.date_start.weekday(),
            "center": session.offering.center.name,
            "teacher": session.teacher.username if session.teacher else '',
            "id": session.id
        }
        sessions_arr.append(my_class)

    for offering in user_pref_offerings:
        my_pref_course = {
            "subject": offering.course.subject,
            "grade": make_number_verb(offering.course.grade),
            "center": offering.center.name,
            "start": make_date_time(offering.start_date)["date"],
            "end": make_date_time(offering.end_date)["date"]
        }

        offerings_arr.append(my_pref_course)

    my_offering_arr = []
    #offerings = []
    offerings = Offering.objects.filter(active_teacher=user1,center__status="Active").exclude(status='completed').order_by('start_date')
    """for session in user_sessions:
        offerings.append(session.offering)
    offerings = set(offerings)"""
    center_data = []
    center_ids = []
    for offering in offerings:
        students = offering.enrolled_students.all()
        students_list = [{'id': stu.id, 'name': stu.name} for stu in students]
        my_offering = {
            "subject": offering.course.subject,
            "grade": make_number_verb(offering.course.grade),
            "start": make_date_time(offering.start_date)["time"],
            "date": make_date_time(offering.start_date)["date"],
            "day": offering.start_date.weekday(),
            "center": offering.center.name,
            "id": offering.id,
            "students": students_list,
            "center_id": offering.center.id,
            'ay_id':offering.academic_year.id
        }
        my_offering_arr.append(my_offering)
        if offering.center.id not in center_ids:
            center_data.append({"id": offering.center.id, "name": offering.center.name})
            center_ids.append(offering.center.id)
    # mapping1 = get_students(assigned_offerings)
    teacher_center = None
    print center_ids
    if center_ids:
        teacher_center = Center.objects.get(id=center_ids[0])
    my_topics = []
    for session in user_sessions:
        planned_topics = session.offering.planned_topics.all()
        if planned_topics:
            for topic in planned_topics:
                my_topics.append(topic.title)
    my_topics = set(my_topics)
    my_sessions = Session.objects.filter(teacher=user1)
    my_comments = []
    for se in my_sessions:
        if se.comments:
            my_comments.append(se.comments.encode("utf-8"))

    booked_slots = Demandslot.objects.filter(user=request.user.id)
    slot_details = []
    if booked_slots:
        slot_details = booked_slots.values_list('center__name', 'day', 'start_time', 'end_time', 'date_booked',
                                                'offering__course__subject')

    teacher_status = False
    if is_teacher:
        teacher_preference = user_profile.rolepreference_set.filter(role__name__in=['Teacher', 'Facilitator Teacher'])
        if teacher_preference:
            teacher_preference = teacher_preference[0]
            teacher_status = teacher_preference.role_onboarding_status
    fbatwork = False
    if user_profile.fbatwork_id:
        fbatwork = True
    view_page = ''
    holidays_list = []
    ay_list = []
    if role_status in ('New', 'Inactive')  or teacher_center is None:
        view_page = 'landing.html'
    elif role_status == 'Active':
        if teacher_center:
            """current_ay  = None
            try:
                current_ay = Ayfy.objects.get(start_date__year = datetime.datetime.now().year, board = teacher_center.board)
            except:
                last_year = (datetime.datetime.now()+relativedelta(years=-1)).year
                current_ay = Ayfy.objects.get(start_date__year = last_year, board = teacher_center.board)"""
            teacher_boards = Center.objects.values_list('board',flat = True).filter(id__in = center_ids).distinct()
            ay_list = Ayfy.objects.filter(board__in = teacher_boards).values_list('id').order_by('-start_date')[:len(teacher_boards)]
        view_page = 'active_teacher_dash.html'
    ay_id = []
    if ay_list:
        for ay in ay_list:
            calendar_ids = Calender.objects.values_list('id', flat = True).filter(academic_year_id = int(ay[0]))
            holidays = Holiday.objects.filter(calender_id__in = calendar_ids).order_by('day')
            holidays_list.append({'holidays':holidays,'ay':int(ay[0])})
            ay_id.append(int(ay[0]))
    if teacher_center:
        school_headmaster = teacher_center.HM
        if school_headmaster is None:
            hm = {
                'name': 'Not available',
                'phone': ''
            }
            print 'none of hm'
        else:
            hm = {
                'name': school_headmaster
            }
        skype= teacher_center.skype_id
        if skype is None:
            skype_id = {
                'name': 'Not available'
            }
            print 'none of hm'
        else:
            skype_id = {
                'name': skype
            }

        fc_id = teacher_center.field_coordinator
        if fc_id is None:
            fc = {
                'name': 'Not available',
                'phone': ''
            }
        else:
            fc1 = username_and_phone_number(fc_id)
            fc = {
                'name': fc1[0],
                'phone': fc1[1]
            }

        dc_id = teacher_center.delivery_coordinator
        if dc_id is None:
            dc = {
                'name': 'Not available',
                'phone': ''
            }
        else:
            dc1 = username_and_phone_number(dc_id)
            dc = {
                'name': dc1[0],
                'phone': dc1[1]
            }

        admin_id = teacher_center.admin
        if admin_id is None:
            admin = {
                'name': 'Not available',
                'phone': ''
            }
        else:
            admin1 = username_and_phone_number(admin_id)
            admin = {
                'name': admin1[0],
                'phone': admin1[1]
            }
        assistant_id=teacher_center.assistant
        if assistant_id is None:
            assistant = {
                'name': 'Not available',
                'phone': ''
            }
        else:
            assistant1 = username_and_phone_number(assistant_id)
            assistant = {
                'name': assistant1[0],
                'phone': assistant1[1]
            }

        donor = {
            'name': teacher_center.donor_name if teacher_center.donor_name is not None else 'NA',
            'phone': ''
        }

        delivery_partner = {
            'name': 'NA',
            'phone': ''
        }
        dp_id = teacher_center.delivery_partner_id
        if dp_id is not None and dp_id != "":
            dp_data = Partner.objects.get(id=dp_id)
            delivery_partner['name'] = dp_data.name_of_organization
            delivery_partner['phone'] = dp_data.phone
    else:
        hm = {'name': 'Not available'}
        fc = {'name': 'Not available'}
        dc = {'name': 'Not available'}
        admin = {'name': 'Not available'}
        assistant={'name': 'Not available'}
        skype_id = {'name': 'Not available'}
        donor = {'name': 'Not available', 'phone': ""}
        delivery_partner = {'name': 'Not available', "phone": ""}
    get_stickets_for_volunteer = []; total_appreciation = 0
    if is_teacher:
        get_stickets_for_volunteer = Recognition.objects.filter(object_id=request.user.id,
                                        content_type=ContentType.objects.get(model='user')).values(
                                        'sticker__sticker_name', 'sticker__sticker_path').annotate(countofsticker=Count('sticker__sticker_name'))
        
        for  sticker in get_stickets_for_volunteer:
            total_appreciation += sticker["countofsticker"]    
    print "start_date",start_date,end_date 
    try: 
        topic_booked_id = SubTopics.objects.values_list("topic_id",flat=True).filter(~Q(status = "Published") & Q(author_id = request.user.id)).distinct()
        topic_booked = Topic.objects.values_list('title',flat=True).filter(id = topic_booked_id)[0]
        topic_status = Topic.objects.values_list('status',flat=True).filter(id = topic_booked_id)[0]
        if topic_status == "In Progress" or topic_status == "Submitted":
            submit_video = 1
        else:
            submit_video = 0
        if topic_status == "Completed":
            topic_booked = 0
    except:
        topic_booked = 0
        submit_video = 0
    try:
        topic_booked_id = SubTopics.objects.values_list("topic_id",flat=True).filter(~Q(status = "Published") & Q(author_id = request.user.id)).distinct()
        subtopic = SubTopics.objects.values().filter(topic_id = topic_booked_id)
        subtopic_count = subtopic.filter(~Q(status = "Inactive")).count()
        submitted = subtopic.filter(status = "In Review").count()
        approved = subtopic.filter(status = "Published").count()
    except:
        subtopic_count = 0
        submitted = 0
        approved = 0

    return render_response(request, view_page,
        {"user_pref_offerings": offerings_arr, "hm": hm,'skype_id':skype_id,'assistant':assistant, "fc": fc, "dc": dc,
            "admin": admin,"assigned_offerg":assigned_offerg,
            "user_profile": user_profile, "assigned_offerings": assigned_courses,
            "stack": stack_arr,
            "sessions": sessions_arr, "others_session": others_session,
            "offerings": offerings,
            "has_notifications": has_notifications, "my_offering": my_offering_arr,
            "user_centers": user_centers, "is_teacher": is_teacher,
            "my_topics": my_topics,"start_date":start_date,"end_date":end_date,
            'my_comments': my_comments, 'prof_per': prof_per,
            'prof_cm_status': prof_cm_status,
            'prof_cm_des': prof_cm_des, 'slot_details': slot_details,
            'teacher_role_status': teacher_status,
            'fbatwork_status': fbatwork, 'pref_lang': pref_lang,
            'role_status': role_status,
            'center_data': simplejson.dumps(center_data),
            'teacher_center': teacher_center, 'holidays_list': holidays_list,
            'ay_id':my_offering_arr,
            'get_stickets_for_volunteer':get_stickets_for_volunteer,
            'total_appreciation':total_appreciation,
            'donor': donor,
            'delivery_partner': delivery_partner,
            'topic_booked':topic_booked,
            'submit_video':submit_video,
            'subtopic_count':subtopic_count,
            'submitted':submitted,
            'approved':approved

        })


# event(s) for the calendar for the respective month in admindash and teacherdash

def offering_comment(request):
    offering_id = request.GET['offering_id']
    sessions = Session.objects.filter(offering__id=offering_id).order_by('date_start').reverse()
    Comments = []
    Teacher = ''
    for session in sessions:
        if session.teacher and session.comments:
            Comments.append(session.comments.encode("utf-8"))
    dict1 = {'teacher': session.teacher.first_name + " " + session.teacher.last_name, 'comments': []}
    if len(Comments) > 0:
        dict1['comments'] = Comments

    return HttpResponse(simplejson.dumps(dict1), mimetype='application/json')


def attendance_mystudents(request):
    sid = request.GET['id']
    student = Student.objects.get(id=sid)
    session_attendance = SessionAttendance.objects.filter(student=student)
    student_offerings = []
    for session in session_attendance:
        student_offerings.append(session.session.offering)

    offering_list = set(student_offerings)
    offering_list = list(offering_list)
    attendance_list = []
    for offer in offering_list:
        ins = SessionAttendance.objects.filter(student=student, session__offering=offer)
        present = 0
        absent = 0
        for attend in ins:
            if attend.is_present == "yes":
                present += 1
            else:
                absent += 1

        attendance_list.append(
            {'subject': offer.course.subject, 'present': present, 'absent': absent, 'total': len(ins)})

    return HttpResponse(simplejson.dumps(attendance_list), mimetype='application/json')


def get_events(request):
    events = [];
    user_sessions_arr = []
    other_sessions_arr = []
    curr_month = int(request.GET.get("month", "8"))
    if request.user.is_authenticated():
        user1 = request.user
        user_sessions = Session.objects.filter(teacher=user1, date_start__month=curr_month)
        for session in user_sessions:
            event = {
                "date": make_date_time(session.date_start)["date"],
                "day": session.date_start.weekday(),
                "color": "#46D150",
                "textColor": "black",
                "id": session.id
            }
            user_sessions_arr.append(event)

        other_sessions = Session.objects.exclude(teacher=user1).filter(date_start__month=curr_month)
        for session in other_sessions:
            event = {
                "date": make_date_time(session.date_start)["date"],
                "day": session.date_start.weekday(),
                "color": "#46D150",
                "textColor": "black",
                "id": session.id
            }
            other_sessions_arr.append(event)
        events.append({"user_sessions": user_sessions_arr, "other_sessions": other_sessions_arr})

    return HttpResponse(simplejson.dumps(events), mimetype="application/json")


def myclass(request):
    ay_id = request.GET.get('ay_id')
    return render_response(request, 'myclass.html', {'ay_id':ay_id})


@csrf_exempt
def getmy_events(request):
    try:
        print("get events called")
        events = []
        user_sessions_arr = []
        other_sessions_arr = []
        if has_role(request.user.userprofile, "Center Admin") or has_role(request.user.userprofile,
                                                                        "Class Assistant") or has_role(
                request.user.userprofile, "Field co-ordinator") or has_role(request.user.userprofile,
                                                                            "Delivery co-ordinator") or has_role(
            request.user.userprofile, "Partner Admin") or has_role(
            request.user.userprofile, "OUAdmin") or has_role(request.user.userprofile, "Partner Account Manager") or request.user.is_superuser:
            rolle = "admin"
            center_id = int(request.POST.get("center_id", ""))

        elif has_role(request.user.userprofile, "Teacher") or has_role(request.user.userprofile,"Facilitator Teacher") or has_pref_role(userprofile, "Facilitator Teacher"):
            rolle = "teacher"
            center_id = -1
        if request.user.is_authenticated():
            curr_month = int(request.POST.get("month", "8")) + 1
            curr_year = int(request.POST.get("year", "2015"))
            curr_day = int(request.POST.get("day", "29"))
            
            ay_id = request.POST.get('ay_id')
            currYear = datetime.datetime.now().year
            print("curr_day",int(request.POST.get("center_id", "")))
            that_day = datetime.date(year=curr_year, month=curr_month, day=curr_day)
            if ay_id:
                current_ay = Ayfy.objects.filter(id = int(ay_id))
            else:
                current_ay = Ayfy.objects.filter(start_date__lte=that_day, end_date__gte=that_day,
                                            types='Academic Year').values_list('id', flat=True)
            sessions = Session.objects.filter(date_start__gt = "2021-03-31 23:00:00" , offering__academic_year__id__in=current_ay,offering__center__status='Active',offering__center__id = int(request.POST.get("center_id", "")) ).exclude(teacher=None)
            all_sessions = Session.objects.filter(date_start__month=curr_month, date_start__year=curr_year,
                offering__academic_year__id__in=current_ay,offering__center__status='Active').exclude(teacher=None).order_by("date_start")
            user_sessions = get_resp_sessions(request, curr_month, curr_year, current_ay, center_id, all_sessions, True)
            other_sessions = get_resp_sessions(request, curr_month, curr_year, current_ay, center_id, all_sessions, False)
            if len(sessions) == 0:
                month = curr_month
                year = curr_year
                sessions = all_sessions
                if len(other_sessions) == 0:
                    for day in range(1,4):
                        curr_month = curr_month - 1
                        that_day = datetime.date(year=curr_year, month=curr_month, day=curr_day)
                        if ay_id:
                            current_ay = Ayfy.objects.filter(id = int(ay_id))
                        else:
                            current_ay = Ayfy.objects.filter(start_date__lte=that_day, end_date__gte=that_day,
                                                        types='Academic Year').values_list('id', flat=True)

                        all_sessions = Session.objects.filter(date_start__month=curr_month, date_start__year=curr_year,
                            offering__academic_year__id__in=current_ay,offering__center__status='Active').exclude(teacher=None).order_by("date_start")
                        user_sessions = get_resp_sessions(request, month, curr_year, current_ay, center_id, sessions, True)
                        other_sessions = get_resp_sessions(request, curr_month, curr_year, current_ay, center_id, all_sessions, False)
                        if len(other_sessions) > 0:
                            break
                if len(other_sessions) == 0:
                    curr_month = 13
                    curr_year = curr_year - 1
                    for day in range(1,13):
                        curr_month = curr_month - 1
                        that_day = datetime.date(year=curr_year, month=curr_month, day=curr_day)
                        if ay_id:
                            current_ay = Ayfy.objects.filter(id = int(ay_id))
                        else:
                            current_ay = Ayfy.objects.filter(start_date__lte=that_day, end_date__gte=that_day,
                                                        types='Academic Year').values_list('id', flat=True)

                        all_sessions = Session.objects.filter(date_start__month=curr_month, date_start__year=curr_year,
                            offering__academic_year__id__in=current_ay,offering__center__status='Active').exclude(teacher=None).order_by("date_start")
                        user_sessions = get_resp_sessions(request, month, year, current_ay, center_id, sessions, True)
                        other_sessions = get_resp_sessions(request, curr_month, curr_year, current_ay, center_id, all_sessions, False)
                        if len(other_sessions) > 0:
                            break
                events.append({"user_sessions": user_sessions, "other_sessions": other_sessions, "rolle": rolle})
            else:

                events.append({"user_sessions": user_sessions, "other_sessions": other_sessions, "rolle": rolle})
            
        return HttpResponse(simplejson.dumps(events), mimetype="application/json")
    except Exception as e:
        print("FT Exception", e)
        traceback.print_exc()
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest, 0, something went wrong.')


def get_resp_sessions(request, curr_month, curr_year, current_ay, center_id, sessions, is_user):
    responses = []
    if is_user:
        resp_sessions = sessions.filter(teacher=request.user).order_by("date_start")
    else:
        resp_sessions = sessions.filter(offering__center_id=center_id).order_by("date_start")
    for session in resp_sessions:
        topics = []
        actual_topics = session.actual_topics.all()
        if actual_topics:
            for topic in actual_topics:
                topics.append({"title": topic.title, "url": str(topic.url)})
        else:
            planned_topics = session.planned_topics.all()
            for topic in planned_topics:
                topics.append({"title": topic.title, "url": str(topic.url)})
        software = 'None'
        software_link = ''
        if session.teachingSoftware != None:
            software = session.teachingSoftware.id
            software_link = session.ts_link
        event = {
            "subject": session.offering.course.subject,
            "topics": topics,
            "grade": make_number_verb(session.offering.course.grade),
            "start": make_date_time(session.date_start)["time"],
            "datee": make_date_time(session.date_start)["date"] + " " + str(session.date_start.year),
            "day_num": session.date_start.strftime('%d'),
            "mont": session.date_start.strftime('%m'),
            "yearr": session.date_start.strftime('%Y'),
            "day_text": session.date_start.weekday(),
            "center": session.offering.center.name,
            "teacher": session.teacher.first_name if session.teacher else session.teacher,
            "color": "#46D150",
            "textColor": "black",
            "id": session.id,
            "software": software,
            "software_link": software_link
        }
        responses.append(event)
    return responses


# event(s) for the calendar for the respective day in teacherdash and admindash
def get_event(request):
    event = [{"user_sessions": [], "other_sessions": []}]
    # session_ids = [int(s_id) for s_id in request.GET.get("id",None).split(";")]
    curr_day = request.GET.get("day", None)
    curr_day = parser.parse(curr_day.split('GMT')[0]).strftime('%Y-%m-%d')
    sessions = Session.objects.filter(date_start__startswith=curr_day)
    for session in sessions:
        topics = []
        actual_topics = session.actual_topics.all()
        planned_topics = session.planned_topics.all()
        if actual_topics:
            for topic in actual_topics:
                # topics += topic.title + ", "
                topics.append({"title": topic.title, "url": topic.url})
        else:
            for topic in planned_topics:
                # topics += topic.title + ", "
                topics.append({"title": topic.title, "url": topic.url})
        session_teacher_id = None
        if session.teacher:
            session_teacher_id = session.teacher.id
        event_dict = {
            "subject": session.offering.course.subject,
            "topic": topics,
            "grade": make_number_verb(session.offering.course.grade),
            "start": make_date_time(session.date_start)["time"],
            "date": make_date_time(session.date_start)["date"],
            "center_language": session.offering.center.language,
            "center": session.offering.center.name,
            "center_id": session.offering.center.id,
            "teacher": session.teacher.first_name if session.teacher else '',
            "teacher_id": session_teacher_id,
            "color": "#46D150",
            "textColor": "black",
            "id": session.id,
            "session_status": session.status,
        }
        if session.teacher == request.user:
            event[0]["user_sessions"].append(event_dict)
        else:
            event[0]["other_sessions"].append(event_dict)

    return HttpResponse(simplejson.dumps(event), mimetype="application/json")


# event(s) for the calendar for the respective month in centeradmin
@csrf_exempt
def get_offerings(request):
    events = []
    running_courses = []
    pending_courses = []
    others_courses = []
    sessions = []
    current_date = datetime.datetime.today()
    center_id = int(request.POST['center_id'])
    print "cid==", center_id
    month = int(request.POST.get('month', current_date.month))
    year = int(request.POST.get('year', current_date.year))
    ay_id = request.POST.get('ay_id')
    center = Center.objects.get(id=center_id)
    that_day = datetime.date(year=year, month=month, day=1)

    if ay_id:
        current_ay = Ayfy.objects.get(id = int(ay_id))
    else:
        try:
            current_ay = Ayfy.objects.get(start_date__year = datetime.datetime.now().year, board = center.board)
        except:
            last_year = (datetime.datetime.now()+relativedelta(years=-1)).year
            current_ay = Ayfy.objects.get(start_date__year = last_year, board = center.board)

    # current_ay = Ayfy.objects.get(start_date__lte=that_day, end_date__gte=that_day, types='Academic Year', board=center.board)
    q_offering = Q()
    o_offering = Q()
    offerings = Offering.objects.filter(center=center, academic_year=current_ay)
    others_offerings = Offering.objects.exclude(center=center)
    for offering, other_offering in zip(offerings, others_offerings):
        if other_offering.start_date and other_offering.end_date:
            o_offering = o_offering | Q(start_date__month=other_offering.start_date.month)
        else:
            o_offering = o_offering | Q(start_date__month=current_date.month)

        if offering.start_date and offering.end_date:
            q_offering = q_offering | Q(start_date__month=offering.start_date.month)
        else:
            q_offering = q_offering | Q(start_date__month=current_date.month)
    offerings = offerings.filter(q_offering)
    others_offerings = others_offerings.filter(o_offering)

    if request.user.is_authenticated():
        for offering, others_offering in zip(offerings, others_offerings):
            running_sessions = offering.session_set.exclude(teacher=None).filter(date_start__month=month,
                                                                                 date_start__year=year)
            others_running_sessions = others_offering.session_set.exclude(teacher=None).filter(date_start__month=month,
                                                                                               date_start__year=year)
            for session in others_running_sessions:
                event = {
                    "date": make_date_time(session.date_start)["date"],
                    "day": session.date_start.weekday(),
                    "color": "#46D150",
                    "textColor": "black",
                    "id": session.id
                }
                others_courses.append(event)

            for session in running_sessions:
                event = {
                    "date": make_date_time(session.date_start)["date"],
                    "day": session.date_start.weekday(),
                    "color": "#46D150",
                    "textColor": "black",
                    "id": session.id
                }
                running_courses.append(event)

            pending_sessions = offering.session_set.filter(teacher=None)
            for session in pending_sessions:
                event = {
                    "date": make_date_time(session.date_start)["date"],
                    "day": session.date_start.weekday(),
                    "color": "#46D150",
                    "textColor": "black",
                    "id": session.id
                }
                pending_courses.append(event)

        events.append(
            {'running_courses': running_courses, 'pending_courses': pending_courses, 'others_courses': others_courses})

    return HttpResponse(simplejson.dumps(events), mimetype="application/json")


# event(s) for the calendar for the respective day in centeradmin
@csrf_exempt
def get_centeroffering(request):
    event = []
    event_no = []
    center_id = request.POST.get("center_id", None)
    curr_day = request.POST.get("day", None)
    curr_day = parser.parse(curr_day.split('GMT')[0]).strftime('%Y-%m-%d')
    sessions = Session.objects.filter(date_start__startswith=curr_day, offering__center__id=int(center_id)).exclude(
        teacher=None)
    for session in sessions:
        topics = []
        actual_topics = session.actual_topics.all()
        planned_topics = session.planned_topics.all()
        if actual_topics:
            for topic in actual_topics:
                # topics += topic.title + ", "
                topics.append({"title": topic.title, "url": topic.url})
        else:
            for topic in planned_topics:
                # topics += topic.title + ", "
                topics.append({"title": topic.title, "url": topic.url})

        event_dict = {
            "subject": session.offering.course.subject,
            "comments": session.comments,
            "topic": topics,
            "grade": make_number_verb(session.offering.course.grade),
            "start": make_date_time(session.date_start)["time"],
            "date": make_date_time(session.date_start)["date"],
            "center": session.offering.center.name,
            "center_language": session.offering.center.language,
            "center_id": session.offering.center.id,
            "teacher": session.teacher.first_name if session.teacher else '',
            "teacher_id": session.teacher.id,
            "color": "#46D150",
            "textColor": "black",
            "subject_id": session.offering.course.id,
            "language": session.offering.language,
            "id": session.id,
            "offering_id": session.offering.id,
            "session_status": session.status,
            "my_center": "Yes"
        }
        event.append(event_dict)
    return HttpResponse(simplejson.dumps(event), mimetype="application/json")


# attendance for the respective session in centeradmin
def get_attendance(request):
    centerId = request.GET.get("center_id", None)
    session = Session.objects.get(pk=int(request.GET.get("session", None)))
    session_attendance = []
    sessionattendance = SessionAttendance.objects.filter(session=session)
    if session.status == "scheduled" or "cancelled":
        for student in session.offering.enrolled_students.all():
            if student.status=='Active':
                is_present = "no"
                session_att_student = SessionAttendance.objects.filter(session=session, student=student).exclude(student__status='Alumni')
                if session_att_student:
                    is_present = session_att_student[0].is_present
                attend = {
                    "name": student.name,
                    "id": student.id,
                    "is_present": is_present
                }
                session_attendance.append(attend)
    else:
        for student in sessionattendance:
            attend = {
                    "name": Student.objects.values_list("name",flat=True).filter(id =student.student_id)[0],
                    "id": student.student_id,
                    "is_present": student.is_present
                }
            session_attendance.append(attend)
    all_present = []
    for attendence in session_attendance:
        if attendence['is_present'] == "no":
            all_present.append("no")
        else:
            all_present.append("yes")
    if "no" in all_present:
        all_yes = 0
    else:
        all_yes = 1

    context = {"session_attendance": session_attendance, "session": session.id,"all_yes":all_yes}

    if centerId:
        center = Center.objects.get(pk=int(centerId))
        context['center'] = center
    return render_response(request, "centeradmin_attendance.html", context)


# feedback for the respective session in centeradmin
def get_feedback(request):
    session = Session.objects.get(pk=int(request.GET.get("session", None)))
    course_id = session.offering.course.id
    offer_id = session.offering.id
    actual_subtopic = session.sub_topic
    offer = Offering.objects.filter(pk=offer_id)[0]
    plan_topics = offer.planned_topics.all()
    grades = set()

    for plan in plan_topics:
        grades.update(list(map(int,(plan.course_id.grade).split(','))))

    revision_grades = list(grades)
    actual_topics = session.actual_topics.all().order_by('priority')
    planned_topics = session.planned_topics.all().order_by('priority')
    actual_comment = session.comments
    status = session.status
    offering = Offering.objects.filter(course=course_id)[0]
    topics = Topic.objects.filter(course_id = course_id).exclude( status = 'Inactive').order_by('priority')#.exclude(id__in = complted_session_topic_id)
    #topics = session.offering.planned_topics.all().order_by('priority')
    actual_topics_arr = []; topics_json = []; planned_topic_json = []; sess_rating_json = []; sub_topic_json = []

    for topic in actual_topics:
        actual_topics_arr.append(topic.title)

    for topic in planned_topics:
        if not topic in actual_topics:
            planned_topic_json.append({"title":topic.title, "id":topic.id, "planned": False})
        else:
            planned_topic_json.append({"title":topic.title, "id":topic.id, "planned": True})

    for topic in topics:
        if not topic in planned_topics:
            if not topic in actual_topics:
                topics_json.append({"title": topic.title, "id": topic.id, "actual": False, "url": topic.url,"planned":False, 'status':topic.status})
            else:
                topics_json.append({"title": topic.title, "id": topic.id, "actual": True, "url": topic.url,"planned":False, 'status':topic.status})
        else:
            if not topic in actual_topics:
                topics_json.append({"title": topic.title, "id": topic.id, "actual": False, "url": topic.url,"planned":True, 'status':topic.status})
            else:
                topics_json.append({"title": topic.title, "id": topic.id, "actual": True, "url": topic.url,"planned":True, 'status':topic.status})

        sess_rating_json = []
        sess_ratings = session.sr_session_id.all()
        for sess_rat in sess_ratings:
            sess_rating_json.append({"stars": sess_rat.no_of_stars, "ques_no": sess_rat.question_no})

    topics_feed=[]
    for topic in plan_topics:
        if topic in planned_topics and topic in actual_topics:
            topics_feed.append({"title": topic.title, "id": topic.id, "actual": True, "url": topic.url,"planned":True, 'status':topic.status})

        elif topic in planned_topics and topic not in actual_topics:
            topics_feed.append({"title": topic.title, "id": topic.id, "actual": False, "url": topic.url,"planned":True, 'status':topic.status})

        elif topic in actual_topics and topic not in planned_topics:
            topics_feed.append({"title": topic.title, "id": topic.id, "actual": True, "url": topic.url,"planned":False, 'status':topic.status})
        else:
            topics_feed.append({"title": topic.title, "id": topic.id, "actual": False, "url": topic.url,"planned":False, 'status':topic.status})

    for topic_js in topics_feed:
        if topic_js["actual"]:
            sub_topic = SubTopics.objects.filter(topic_id=topic_js["id"])
            for stopic in sub_topic:
                if stopic.id == actual_subtopic.id:
                    dict1={"id":stopic.id,"name":stopic.name,'completed':True}
                else:
                    dict1={"id":stopic.id,"name":stopic.name,'completed':False}

                sub_topic_json.append(dict1)
            break
    return render_response(request, "centeradmin_feedback.html",
                           {"session": session.id, "topics": topics_feed, "status": status, 'revision_grades':revision_grades,
                            "actual_comment": actual_comment, 'session_ratings': simplejson.dumps(sess_rating_json),
                            'planned_topic':planned_topic_json,'sub_topic_json':sub_topic_json, "offering_id":offer_id})


@login_required
def get_planed_topics_by_grade(request):
    if request.method == 'POST':
        off_id = request.POST.get('offering_id', None)
        grade = request.POST.get('grade', None)
        offer = Offering.objects.filter(pk=off_id)[0]
        plan_topics = offer.planned_topics.all().order_by('priority')
        

        planed_topics_by_grade = []
        for plan in plan_topics:
            if int(plan.course_id.grade) == int(grade):
                planed_topics_by_grade.append(plan)
        
        course_topics =[]
        for course_topic in planed_topics_by_grade:
            course_topics.append({'id':course_topic.id,'url':course_topic.url,'title':course_topic.title, 'priority':course_topic.priority})
        print(course_topics)
        return HttpResponse(simplejson.dumps(course_topics))


'''
def get_students(offering):

    mapping = []
    for offer in offering:
        students = offer.offering.enrolled_students.all()
        mapping.append({"offering":offer, "students": students })
    return mapping
'''


# dashboard for admins, containg details about unassigned offering and recommendations
# upcomig offerings
@login_required
def admindash(request):
    print datetime.datetime.now()
    users = []
    center_admin_arr = []
    is_field_coordinator = False
    is_delivery_coordinator = False
    user_profiles = UserProfile.objects.all()
    is_delivery = False
    if request.user.partner_set.values():
        if request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 2:
            is_delivery = True
    role = Role.objects.filter(name='Center Admin')
    centers = list(Center.objects.exclude(admin=None).order_by("id"))
    assistant_centers = list(Center.objects.exclude(assistant=None).order_by("id"))
    center_admins = list(User.objects.filter(center__in=centers))
    center_assistants = list(User.objects.filter(assistant_center__in=assistant_centers))
    center_no_admin = list(Center.objects.filter(admin=None))
    center_no_assistant = list(Center.objects.filter(assistant=None))
    ca_unassigned = list(User.objects.filter(userprofile__pref_roles__name="Center Admin"))
    center_assistant_unassigned = list(User.objects.filter(userprofile__pref_roles__name="Class Assistant"))
    # center admins without duplicates
    center_admins_nodup = set(center_admins)
    center_assistants_nodup = set(center_assistants)
    center_partners = list(Center.objects.exclude(funding_partner=None).order_by("id"))
    partner_centers = []
    for center in center_partners:
        partners = Partner.objects.filter(funding_partner=center)
        for partner in partners:
            partner_centers.append(partner)
    "partner_centers = list(Partner.objects.filter(funding_partner__in = center_partners))"
    partner_unassigned = []
    partnerList = Partner.objects.all().order_by("id")
    if partnerList:
        for partner in partnerList:
            if partner not in partner_centers:
                partner_unassigned.append(partner)
    field_coordinator_centers = list(Center.objects.exclude(field_coordinator=None).order_by("id"))
    delivery_coordinator_centers = list(Center.objects.exclude(delivery_coordinator=None).order_by("id"))
    center_field_coordinator = list(User.objects.filter(field_coordinator_center__in=field_coordinator_centers))
    center_delivery_coordinator = list(
        User.objects.filter(delivery_coordinator_center__in=delivery_coordinator_centers))
    center_field_coordinator_unassigned = list(
        User.objects.filter(userprofile__pref_roles__name="Field co-ordinator").exclude(
            email__in=center_field_coordinator))
    center_delivery_coordinator_unassigned = list(
        User.objects.filter(userprofile__pref_roles__name="Delivery co-ordinator").exclude(
            email__in=center_delivery_coordinator))
    center_fieldCoordinator = set(center_field_coordinator)
    center_deliveryCoordinator = set(center_delivery_coordinator)
    center_partner = set(partner_centers)
    for user in center_admins:
        if user in ca_unassigned:
            ca_unassigned.remove(user)

    mapping = []
    user = request.user
    is_teacher, is_assistant = False, False
    if has_role(user.userprofile, "Teacher") or has_pref_role(user.userprofile, "Teacher"):
        is_teacher = True
    if has_role(user.userprofile, "Class Assistant") or has_pref_role(user.userprofile, "Class Assistant"):
        is_assistant = True

    for user in users:
        pref_offerings = user.pref_offerings.all()
        if len(pref_offerings) > 0:
            mapping.append({"teacher": user.user, "offerings": pref_offerings})
    user = request.user
    user_profile = UserProfile.objects.filter(user=request.user)[0]
    roles = user_profile.role.values_list('name', flat=True)
    if roles:
        user_role = roles[0]
        if "Field co-ordinator" in roles:
            is_field_coordinator = True
        else:
            is_field_coordinator = False
        if "Delivery co-ordinator" in roles:
            is_delivery_coordinator = True
        else:
            is_delivery_coordinator = False

    print 'Admins count ' + str(len(center_admins_nodup))
    center_admins_nodup = []

    print datetime.datetime.now()

    ######### For Partner Admin to get Org details
    is_partner_volunteer, is_partner_delivery, is_partner = [False] * 3
    try:
        org_partner = Partner.objects.get(contactperson=request.user,status='Approved')
        is_partner = True
        for ptype in org_partner.partnertype.all():
            print ptype
            if ptype.id == 1:
                is_partner_volunteer = True
            elif ptype.id == 2:
                is_partner_delivery = True
    except Partner.DoesNotExist:
        org_partner = []

    ### For updating User Role of Partner's Users
    admin_assigned_roles = ["TSD Panel Member","Content Reviewer","Content Admin", "Class Assistant", "vol_admin", "vol_co-ordinator", "Partner Admin"]
    roles = Role.objects.exclude(name__in=admin_assigned_roles)
    admin_assignedroles = ["Class Assistant","Content Reviewer", "Content Admin","TSD Panel Member", "vol_admin", "vol_co-ordinator", "Field co-ordinator", "Delivery co-ordinator", "support","Partner Account Manager",'CSD Panel Member', 'Digital School Manager']
    assign_roles = Role.objects.filter(name__in=admin_assignedroles)
    return render_response(request, 'admindash.html',
                           {"mapping": mapping, "centers": centers, "center_admins_nodup": center_admins_nodup,
                            "center_no_admin": center_no_admin, "center_admins": center_admins,
                            "ca_unassigned": ca_unassigned, "is_teacher": is_teacher,
                            "center_assistant_unassigned": center_assistant_unassigned,
                            "center_assistants_nodup": center_assistants_nodup, "center_assistants": center_assistants,
                            "assistant_centers": assistant_centers, 'is_delivery': is_delivery,
                            'partnerList': partnerList, 'center_field_coordinator': center_field_coordinator,
                            'center_delivery_coordinator': center_delivery_coordinator,
                            'center_field_coordinator_unassigned': center_field_coordinator_unassigned,
                            'center_delivery_coordinator_unassigned': center_delivery_coordinator_unassigned,
                            'field_coordinator_centers': field_coordinator_centers,
                            'center_fieldCoordinator': center_fieldCoordinator,
                            'center_deliveryCoordinator': center_deliveryCoordinator,
                            'delivery_coordinator_centers': delivery_coordinator_centers,
                            'is_field_coordinator': is_field_coordinator,'assign_roles':assign_roles,
                            'is_delivery_coordinator': is_delivery_coordinator, 'user': user,
                            'partner_centers': partner_centers, 'centerPartner': center_partner,
                            'partner_unassigned': partner_unassigned, 'center_partners': center_partners,
                            'org_partner': org_partner, 'is_partner_volunteer': is_partner_volunteer,
                            'is_partner_delivery': is_partner_delivery,'is_partner':is_partner,'roles':roles})


def get_recommendation(offering):
    mapping = []
    users = UserProfile.objects.filter(pref_offerings=offering)
    oid = offering.id
    for user in users:
        if user:
            pref_offering = user.pref_offerings.filter(id=oid)
            mapping.append({"teacher": user.user, "offerings": pref_offering})
    return mapping


# displays upcoming offerings, in the coming week
def recent(session):
    recent = []
    now = datetime.datetime.now()
    today = datetime.date.today()
    week = today + datetime.timedelta(days=7)
    for i in range(len(session)):
        date_start = session[i].date_start.date()
        if date_start > today:
            if date_start < week:
                recent.append(session[i])
    return recent

def username_and_phone_number(request):
    user = User.objects.get(id=request.id)
    name = user.first_name + ' '+ user.last_name
    phone = ""
    try:
        userp = UserProfile.objects.get(user_id = request.id);
    except UserProfile.DoesNotExist:
        pass
    else:
        userp = UserProfile.objects.get(user_id = request.id);
        phone = userp.phone
    return name, phone

# dashboard for cventeradmin, having details about unassigned session and thier recommendations
@login_required
def centeradmin(request, center_id_value=None):
    user_centers = []  # not using anywhere in view or html
    start_time = time.clock()
    # end debug
    html_reco = []
    topics = []
    has_recommendations = None
    if request.method == "GET":
        center_id1 = center_id_value
        center_id = request.GET.get('center_id', None)
        ay_id = request.GET.get('ay_id', None)

    if not center_id:
        center_id = center_id1
    offerings = []
    center = None
    if center_id_value:
        center = Center.objects.get(id=center_id)
    else:
        if request.user.is_superuser:
            center = Center.objects.get(id=center_id)
        else:
            usrprof = UserProfile.objects.get(user=request.user)
            uroles = usrprof.role.all()
            rolesrequired = uroles.filter( Q(name='Partner Admin') | Q(name='Partner Account Manager') | Q(name='Digital School Manager'))
            rolepreference_outcome = []
            for role in rolesrequired:
                try:
                    roleprefe = RolePreference.objects.get(userprofile_id=usrprof.id, role_id=role.id)
                    if roleprefe.role_status == 'New' or roleprefe.role_status == 'Active':
                        rolepreference_outcome.append(roleprefe.role_outcome)
                except RolePreference.DoesNotExist:
                    pass
            partner_count = Partner.objects.filter(contactperson=request.user, status='Approved').count()
            user_refchanel_partner = False
            if usrprof.referencechannel:
                if usrprof.referencechannel.partner_id:
                    user_refchanel_partner = True
            if (user_refchanel_partner and (rolesrequired.count() > 0) and ('Recommended' in rolepreference_outcome)) or partner_count > 0:
                if partner_count > 0:
                    if request.user.partner_set.all()[0].partnertype.filter(name='Organization Unit').count() > 0:
                        try:
                            center = Center.objects.get(id=center_id,orgunit_partner=request.user.partner_set.all()[0])
                        except Center.DoesNotExist:
                            print('11111111111111111')
                            return HttpResponseRedirect('/partner/centers/')
                    else:
                        try:
                            partner_id=Partner.objects.filter(contactperson=request.user, status='Approved').values_list('id',flat=True)
                            center = Center.objects.filter((Q(delivery_partner_id=partner_id) | Q(funding_partner_id=partner_id) | Q(digital_school_partner_id=partner_id)), id=center_id).get(id=center_id)
                        except Center.DoesNotExist:
                            print('222222222222222222222')
                            return HttpResponseRedirect('/partner/centers/')

                elif has_role(usrprof, "Partner Account Manager") or has_pref_role(usrprof, "Partner Account Manager"):
                    try:
                        db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
                        tot_user_cur = db.cursor()
                        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
                        query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                        dict_cur.execute(query)
                        partner_id = [str(each['value']) for each in dict_cur.fetchall()]
                        partner_id.sort()	   
                        center  = Center.objects.get(Q(id = center_id) &( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id)))
                        db.close()
                        dict_cur.close()
                    except Center.DoesNotExist:
                        return HttpResponseRedirect('/partner/centers/')
                else:
                    try:
                        center = Center.objects.get(id=center_id, partner_school__partner=request.user.userprofile.referencechannel.partner)
                    except Exception as e:
                        if has_role(usrprof, "Delivery co-ordinator") or has_pref_role(usrprof, "Delivery co-ordinator"):
                            center = Center.objects.filter(id = center_id)[0]
                        else:
                            return HttpResponseRedirect('/partner/centers/')
            else:
                if has_role(usrprof, "Center Admin") or has_pref_role(usrprof, "Center Admin"):
                    center = Center.objects.filter(id = center_id)[0]
                elif has_role(usrprof, "Partner Account Manager") or has_pref_role(usrprof, "Partner Account Manager"):
                    center = Center.objects.filter(id = center_id,status='Active')[0]
                elif has_role(usrprof, "Class Assistant") or has_pref_role(usrprof, "Class Assistant"):
                    center = Center.objects.filter(id = center_id,status='Active')[0]
                elif has_role(usrprof, "Field co-ordinator") or has_pref_role(usrprof, "Field co-ordinator"):
                    center = Center.objects.filter(id = center_id, status='Active')[0]
                elif has_role(usrprof, "Delivery co-ordinator") or has_pref_role(usrprof, "Delivery co-ordinator"):
                    center = Center.objects.filter(id = center_id)[0]
                else:
                    return HttpResponseRedirect('/myevidyaloka/')
    holidays = None
    if center:
        board = [center.board,'eVidyaloka']
        if center.photo:
            print('center phtot',center.photo)
            photopath = os.path.exists(center.photo.path)
            if not photopath:
                center.photo = 'static/images/no_image_thumb.gif'

    if center:
        current_ay = None
        try:
            current_ay = Ayfy.objects.get(start_date__year=datetime.datetime.now().year, board__in=board)
            if not ay_id: ay_id=current_ay.id
        except:
            last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
            current_ay = Ayfy.objects.get(start_date__year=last_year, board__in=board)
    calendar_ids = Calender.objects.values_list('id', flat=True).filter(board__in=board, academic_year=current_ay)
    holidays = Holiday.objects.filter(calender_id__in=calendar_ids).order_by('day')
    if center:
        school_headmaster = center.HM
        if school_headmaster is None:
            hm = {
                'name': 'Not available',
                'phone': ''
            }
        else:
            hm = {
                'name': school_headmaster
            }

        fc_id = center.field_coordinator

        if fc_id is None:
            fc = {
                'name': 'Not available',
                'phone': ''
            }
        else:
            fc1 = username_and_phone_number(fc_id)
            fc = {
                'name': fc1[0],
                'phone': fc1[1]
            }

        dc_id = center.delivery_coordinator
        if dc_id is None:
            dc = {
                'name': 'Not available',
                'phone': ''
            }
        else:
            dc1 = username_and_phone_number(dc_id)
            dc = {
                'name': dc1[0],
                'phone': dc1[1]
            }

        admin_id = center.admin
        if admin_id is None:
            admin = {
                'name': 'Not available',
                'phone': ''
            }
        else:
            admin1 = username_and_phone_number(admin_id)
            admin = {
                'name': admin1[0],
                'phone': admin1[1]
            }

        donor = {
            'name': center.funding_partner.name_of_organization if center.funding_partner and center.funding_partner.name_of_organization is not None else 'NA',
            'phone': ''
        }
        #print "******** DONOR \n", donor

        delivery_partner = {
            'name': 'NA',
            'phone': ''
        }
        dp_id = center.delivery_partner_id
        if dp_id is not None and dp_id != "":
            dp_data = Partner.objects.get(id=dp_id)
            delivery_partner['name'] = dp_data.name_of_organization
            delivery_partner['phone'] = dp_data.phone
        #print "******** DELIVERY PARTNER \n", delivery_partner

    else:
        hm = {'name': 'Not available'}
        fc = {'name': 'Not available'}
        dc = {'name': 'Not available'}
        admin = {'name': 'Not available'}

    ay_list = Ayfy.objects.filter(board=center.board).values_list('id', 'title', 'board').order_by('-start_date')
    ay_list1 = Ayfy.objects.values_list('id', 'title', 'board').order_by('-start_date')
    assigned_courses = []
    
    pending_offer_slots = {}
    backfill_offer_slots={}
    # unassigned_offerings = Offering.objects.filter(session__teacher = None, center = center)
    unassigned_offeringsForPending = []
    unassigned_offeringsForBackfill=[]
    try:
        unassigned_offeringsForPending = Offering.objects.filter(active_teacher=None, center=center, academic_year_id=ay_id,status='pending')
        unassigned_offeringsForBackfill=Offering.objects.filter(active_teacher=None, center=center, academic_year_id=ay_id,status='running')       
        
    except Exception as e:
        print e
        
    unassigned_coursesPending = []
    user_details = {}
    for offering in unassigned_offeringsForPending:
        print "pending_offerings==", offering.id
        make_course_centeradmin(offering, unassigned_coursesPending)
    
    unassigned_coursesBackfill= []
    for offering in unassigned_offeringsForBackfill:
        print "backfill_offering==",offering.id
        make_course_centeradmin(offering, unassigned_coursesBackfill)  
    
    topics = Topic.objects.all()
    teachers = User.objects.filter(userprofile__pref_roles__name="Teacher",
                                   userprofile__pref_medium=center.language).exclude(first_name="", last_name="")
    teacher_profiles_arr = []

    if unassigned_offeringsForPending:

        print 'centeradmin 2 unassinged offerings Len in pending section: ' + str(len(unassigned_offeringsForPending))
        for unassigned_offer in unassigned_offeringsForPending:
            pending_offer_slots[unassigned_offer.id] = []
            user_details[unassigned_offer.id] = {}
            slot_objs = Demandslot.objects.filter(status__in=['Booked','Unallocated'], center=center, offering_id=unassigned_offer.id)
            teacherObj = Role.objects.get(pk=1)
            print 'centeradmin 2 slot_objs Len in pending section: ' + str(len(slot_objs))
            for slot_obj in slot_objs:
                if slot_obj.status == 'Unallocated':
                    pending_offer_slots[unassigned_offer.id].append([slot_obj.day, slot_obj.start_time.strftime('%I:%M %p'), slot_obj.end_time.strftime('%I:%M %p'),'', '',slot_obj.status])
                    continue
                usrp = UserProfile.objects.filter(user=slot_obj.user)[0]
                tsd = SelectionDiscussionSlot.objects.filter(userp=usrp)
                tsdStatus = ''
                if len(tsd) > 0:
                    tsdStatus = tsd[0].status

                try :
                    role_preferences = RolePreference.objects.filter(userprofile=usrp, role_id__in=[1,20])
                    print('--------roles:',role_preferences.values('id','role_id'))
                except :
                    role_preferences=None
                
                if role_preferences:
                    role_outcome =role_preferences[0].role_outcome
                else:
                    role_outcome=''

                user_details[unassigned_offer.id] = {'id': slot_obj.user.id, 'email': slot_obj.user.email,
                                                     'username': slot_obj.user.username, \
                                                     'skype_id' : slot_obj.user.userprofile.skype_id, 'contact_num': slot_obj.user.userprofile.phone,\
                                                     'from': slot_obj.user.userprofile.from_date.strftime('%m/%d/%Y'), \
                                                     'to': slot_obj.user.userprofile.to_date.strftime('%m/%d/%Y'), \
                                                     'medium': slot_obj.user.userprofile.pref_medium, \
                                                     'course': slot_obj.offering.course.grade + "th " + slot_obj.offering.course.subject, \
                                                     'location': slot_obj.user.userprofile.city + ", " + slot_obj.user.userprofile.state, \
                                                     'tsd_status': tsdStatus, 'role_outcome': role_outcome}
                pending_offer_slots[unassigned_offer.id].append([slot_obj.day, slot_obj.start_time, slot_obj.end_time, (
                            slot_obj.user.first_name + " " + slot_obj.user.last_name), slot_obj.user.id])
        # getting users if they have Teacher as their preferred role, matches the language of the center, and excluding incomplete profiles

        
    if unassigned_offeringsForBackfill:

        print 'centeradmin 2 unassinged offerings Len in backfill section: ' + str(len(unassigned_offeringsForBackfill))
        for unassigned_offer in unassigned_offeringsForBackfill:
            print "bID==",unassigned_offer.id
            backfill_offer_slots[unassigned_offer.id] = []
            user_details[unassigned_offer.id] = {}
            slot_objs = Demandslot.objects.filter(status__in=['Booked','Unallocated'], center=center, offering_id=unassigned_offer.id)
            print "slot_objsB==",slot_objs
            teacherObj = Role.objects.get(pk=1)
            print 'centeradmin 2 slot_objs Len in backfill section: ' + str(len(slot_objs))
            for slot_obj in slot_objs:
                if slot_obj.status == 'Unallocated':
                    backfill_offer_slots[unassigned_offer.id].append([slot_obj.day, slot_obj.start_time.strftime('%I:%M %p'), slot_obj.end_time.strftime('%I:%M %p'),'', '',slot_obj.status])
                    continue
                usrp = UserProfile.objects.filter(user=slot_obj.user)[0]
                tsd = SelectionDiscussionSlot.objects.filter(userp=usrp)
                tsdStatus = ''
                if len(tsd) > 0:
                    tsdStatus = tsd[0].status
                try :
                    role_preferences = RolePreference.objects.filter(userprofile=usrp, role_id__in=[1,20])
                    print('--------roles:',role_preferences.values('id','role_id'))
                except :
                    role_preferences=None
                role_outcome=''
                if role_preferences:
                    role_outcome =role_preferences[0].role_outcome

                user_details[unassigned_offer.id] = {'id': slot_obj.user.id, 'email': slot_obj.user.email,
                                                     'username': slot_obj.user.username, \
                                                     'from': slot_obj.user.userprofile.from_date.strftime('%m/%d/%Y'), \
                                                     'to': slot_obj.user.userprofile.to_date.strftime('%m/%d/%Y'), \
                                                     'medium': slot_obj.user.userprofile.pref_medium, \
                                                     'course': slot_obj.offering.course.grade + "th " + slot_obj.offering.course.subject, \
                                                     'location': slot_obj.user.userprofile.city + ", " + slot_obj.user.userprofile.state, \
                                                     'tsd_status': tsdStatus, 'role_outcome': role_outcome}
                backfill_offer_slots[unassigned_offer.id].append([slot_obj.day, slot_obj.start_time, slot_obj.end_time, (
                            slot_obj.user.first_name + " " + slot_obj.user.last_name), slot_obj.user.id])

    user = request.user
    is_teacher = False
    is_assistant = False
    if has_pref_role(user.userprofile, "Teacher") or has_role(user.userprofile, "Teacher"): is_teacher = True
    if has_pref_role(user.userprofile, "Class Assistant") or has_role(user.userprofile,
                                                                      "Class Assistant"): is_assistant = True

    try:
        center_offerings = Offering.objects.filter(center__id=center_id, academic_year_id=ay_id,status='running').exclude(active_teacher_id__isnull=True);
    except:
        center_offerings = []
    center_courses = []
    for offering in center_offerings:
        make_course_centeradmin(offering, center_courses)

    print 'centeradmin 4 : ' + str(datetime.datetime.now())

    courses = Course.objects.filter(status='Active')
    all_centers = Center.objects.all()
    students = Student.objects.filter(center=center)

    center_unallocated_slots = []
    slot_unallocated_obj = Demandslot.objects.filter(center__id=center_id, status='Unallocated',offering = None).values_list('day',
                                                                                                             'start_time',
                                                                                                             'end_time')
    for slot in slot_unallocated_obj:
        center_unallocated_slots.append(
            {'day': slot[0], 'start_time': slot[1].strftime('%I:%M %p'), 'end_time': slot[2].strftime('%I:%M %p')})

    print 'centeradmin 5 : ' + str(datetime.datetime.now())

    center_sessions = []
    center_booked_slots = []
    for offering in center_offerings:
        sessions = Session.objects.filter(offering=offering)
        center_sessions.append(sessions)
    for sessions in center_sessions:
        if sessions:
            for session in sessions:
                slot = {
                    "day": make_weekday((session.date_start).weekday()),
                    "start_time": make_date_time(session.date_start)["time"],
                    "end_time": make_date_time(session.date_end)["time"]
                }
                center_booked_slots.append(slot)
    try:
        n_running_courses = Offering.objects.filter(center=center, status="running", academic_year_id=ay_id).exclude(
            active_teacher=None)
    except:
        n_running_courses = []
    print 'centeradmin 6 : ' + str(datetime.datetime.now())

    run_courses = []
    for offer in n_running_courses:
        drop_check = True
        curr_date_forDrop = datetime.datetime.now().date()
        sessionsAll = offer.session_set.all().order_by('date_start')
        if sessionsAll:
            for eachsession in sessionsAll:
                if eachsession.date_start.date()>= curr_date_forDrop and eachsession.teacher_id is None:
                    offer.active_teacher = None
                    offer.save()
                    drop_check = False
                    continue
        # make_course_centeradmin(offer,run_courses)
        if drop_check:
            running_courses(offer, run_courses)
    try:
        n_bachfill_courses = Offering.objects.filter(center=center, status="running", academic_year_id=ay_id,
                                                     active_teacher=None)
    except:
        n_bachfill_courses = []
    back_courses = []
    for offer in n_bachfill_courses:
        backfill_courses(offer, back_courses)

    try:
        n_completed_courses = Offering.objects.filter(center=center, status="completed", academic_year_id=ay_id)
    except:
        n_completed_courses = []
    offerings = set(center_offerings)
    my_offering_arr = []

    print 'centeradmin 7 : ' + str(datetime.datetime.now())

    for offering in center_offerings:
        students = offering.enrolled_students.all()
        students_list = [{'id': stu.id, 'name': stu.name} for stu in students]
        my_offering = {
            "subject": offering.course.subject,
            "grade": make_number_verb(offering.course.grade),
            "start": make_date_time(offering.start_date)["time"],
            "date": make_date_time(offering.start_date)["date"],
            "day": offering.start_date.weekday(),
            "center": offering.center.name,
            "id": offering.id,
            "students": students_list
        }
        my_offering_arr.append(my_offering)

    print 'centeradmin 8 : ' + str(datetime.datetime.now())

    comp_courses = []
    for offer in n_completed_courses:
        make_course(offer, comp_courses)

    print 'centeradmin 9 : ' + str(datetime.datetime.now())

    if center:
        center_list = Offering.objects.filter(Q(center=center.id), Q(status='running'), (
                    (Q(course_type='C') | Q(course_type='c')) and ~Q(status="not_approved")) | (
                                                          (Q(course_type='S') | Q(course_type='s')) | Q(
                                                      course_type=''))).distinct()
    running_teacher_data = []
    for ent in center_list:
        poc_obj = Session.objects.values_list('teacher__userprofile__phone', 'teacher__first_name',
                                              'teacher__last_name').filter(offering=ent.id,
                                                                           status='Completed').distinct()
        for poc in poc_obj:
            data = {'phone': poc[0],
                    'first_name': poc[1],
                    'last_name': poc[2]
                    }
            running_teacher_data.append(data)
    if center:
        save_user_activity(request, 'Selected Center: My center ' + str(center.name), 'Page Visit')

    print 'centeradmin 10 : ' + str(datetime.datetime.now())

    is_partner = False
    is_superuser = False
    if request.user.partner_set.values():
        is_partner = True
    if request.user.is_superuser:
        is_superuser = True
    is_centeradmin = False
    is_delivery_coordinator = False
    is_field_coordinator = False
    is_class_assistant = False
    user_profile = UserProfile.objects.filter(user = request.user)[0]
    roles = user_profile.role.values_list('name',flat=True)
    # print 'roles', roles
    if roles:
        if "Center Admin" in roles:
            is_centeradmin = True
        if "Delivery co-ordinator" in roles:
            is_delivery_coordinator = True
        if "Field co-ordinator" in roles:
            is_field_coordinator = True
        if "Class Assistant" in roles:
            is_class_assistant = True
    softwares = TeachingSoftwareDetails.objects.all().order_by('software_name')

    print 'centeradmin 11 : ' + str(datetime.datetime.now())
    admin_assigned_center = False
    dc_assigned_center = False
    if center.admin == request.user:
        admin_assigned_center = True

    if center.delivery_coordinator == request.user:
        dc_assigned_center = True

    if not ay_id:
        if len(ay_list)>0:
            ay_id = ay_list[0][0] 

    ###### for ADD Course dropdown based on center getting dropdowns #######
    add_course_dropdown_courses = courses.filter(board_name__in=board, status='Active')
    add_course_dropdown_courses_list = []
    for cour in add_course_dropdown_courses:
        add_course_dropdown_courses_dict = {}
        add_course_dropdown_courses_dict['id'] = int(cour.id)
        add_course_dropdown_courses_dict['language'] = str(cour.language)
        add_course_dropdown_courses_dict['board_name'] = str(cour.board_name) + '::' + str(cour.subject) + '::' + str(cour.grade) 
        add_course_dropdown_courses_list.append(add_course_dropdown_courses_dict)

    add_course_dropdown_academic_year = Ayfy.objects.filter(board__in=board,types__icontains='Academic Year').order_by('-start_date')

    add_course_dropdown_academic_year_list = []
    for acyr in add_course_dropdown_academic_year:
        add_course_dropdown_academic_year_dict = {}
        add_course_dropdown_academic_year_dict['id'] = int(acyr.id)
        add_course_dropdown_academic_year_dict['academic_year'] = str(acyr.title) + '-' + str(acyr.board)
        add_course_dropdown_academic_year_list.append(add_course_dropdown_academic_year_dict)

    map_location_link=Center.objects.get(id=center_id).location_map
    if map_location_link:
        map_location_link=map_location_link.replace("'"," ")

    student_list ={}
    get_stickers_for_students =[]
    student_ids = Student.objects.values_list('id', flat ='True').filter(center__id = center.id).distinct()
    board_name = Center.objects.get(id=center_id).board
    # Fetching all the academic year for a center
    ayfy_data = Ayfy.objects.filter(board=board_name).values('title', 'start_date', 'end_date').order_by('-id')
    academic_year_date_month_dict = OrderedDict()
    check_field_added_in_dict = True
    now = datetime.datetime.now()
    current_academic_year_available = False
    for _ayfy_data in ayfy_data:
        academic_year_date_month_dict[_ayfy_data['title']] = list()

        start_year = _ayfy_data['start_date'].year
        start_month = _ayfy_data['start_date'].month
        end_year = _ayfy_data['end_date'].year
        end_month = _ayfy_data['end_date'].month
        current_month = now.month
        if now > _ayfy_data['start_date'] and now < _ayfy_data['end_date']:
            current_academic_year_available = True
            if start_month == 1:
                while current_month >= 1:
                    academic_year_date_month_dict[_ayfy_data['title']].append(calendar.month_name[current_month])
                    current_month -= 1
            else:
                if now.year == start_year:
                    while current_month >= start_month:
                        academic_year_date_month_dict[_ayfy_data['title']].append(calendar.month_name[current_month])
                        current_month -= 1   
                else:
                    while current_month >= 1:
                        academic_year_date_month_dict[_ayfy_data['title']].append(calendar.month_name[current_month])
                        current_month -= 1
                    month = 12
                    while month >= start_month:
                        academic_year_date_month_dict[_ayfy_data['title']].append(calendar.month_name[month])
                        month -= 1
        else:
            selected_year = now.year
            if start_month == 1:
                month = 12
                while month >= start_month:
                    academic_year_date_month_dict[_ayfy_data['title']].append(calendar.month_name[month])
                    month -= 1
            else:                
                while end_month >= 1:
                    academic_year_date_month_dict[_ayfy_data['title']].append(calendar.month_name[end_month])
                    end_month -= 1

                month = 12
                while (start_month) <= month:
                    academic_year_date_month_dict[_ayfy_data['title']].append(calendar.month_name[month])
                    month -= 1
    academic_years = list(academic_year_date_month_dict.keys())
    selected_year = now.year
    selected_month = now.month
    selected_academic_year = None
    if len(academic_years):
        if current_academic_year_available ==  False:
            selected_year = ayfy_data[0]['end_date'].year
            selected_month = ayfy_data[0]['end_date'].month
        selected_academic_year = academic_years[0]
    print("selected year {} and selected month = {}".format(selected_year, selected_month))
    if len(ayfy_data) and student_ids:
        students = Recognition.objects.filter(object_id__in = student_ids,content_type = ContentType.objects.get(model='student'), added_on__year = selected_year, added_on__month = selected_month).values('object_id').annotate(
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


    teacher_list = {}
    get_stickers_for_teachers = []
    teacher_ids = Session.objects.values_list('teacher_id',flat = 'True').filter(offering__center_id = str(center.id),offering__academic_year_id = str(ay_id)).distinct()

    if teacher_ids:
        teacher_sticker = Recognition.objects.filter(object_id__in = teacher_ids,content_type = ContentType.objects.get(model='user')).values('object_id').annotate(
                                countofreg=Count('object_id')).order_by('-countofreg')[:3]

        for teach in teacher_sticker:
            teach_name = User.objects.get(id = teach['object_id'])
            teach_obj = UserProfile.objects.get(user_id = teach['object_id'])
            get_stick_count = Recognition.objects.filter(object_id=teach['object_id'],
                                        content_type=ContentType.objects.get(model='user')).values(
                                        'sticker__sticker_name', 'sticker__sticker_path').annotate(countofsticker=Count('sticker__sticker_name'))
            teacher_list = {"teach_name":teach_name.first_name,"teach_pic":teach_obj.picture,"teach_sub":teach_obj.pref_subjects, "get_stick_count": get_stick_count,'gender':teach_obj.gender}
            get_stickers_for_teachers.append(teacher_list)
    # print 'get_stickers_for_teachers ' , get_stickers_for_teachers

    return render_response(request, 'centeradmin.html',{"center":center,"hm":hm,"fc":fc, "dc":dc,
          "admin": admin,"n_running_courses":n_running_courses, "holidays":holidays,
          "is_field_coordinator": is_field_coordinator,"is_class_assistant": is_class_assistant,
          "started_courses": run_courses,"completed_courses":comp_courses, "pending_courses": unassigned_coursesPending,
          "teachers": teachers, "topics": topics, "user_centers": user_centers, "teacher_profiles": teacher_profiles_arr, 
          "topics": topics, "is_teacher": is_teacher, "center_courses":center_courses, "courses":courses, "donor": donor, "delivery_partner": delivery_partner,
          "all_centers":all_centers, "students":students, "center_booked_slots": center_booked_slots,
          "my_offering":my_offering_arr, 'is_assistant': is_assistant, 'center_unallocated_slots': center_unallocated_slots,
          'pending_offer_slots': pending_offer_slots, 'user_details': user_details ,'running_teacher_data':running_teacher_data, 
          'is_partner' : is_partner, 'ay_list': ay_list,'softwares':softwares,'backfill_courses':unassigned_coursesBackfill,
          'is_superuser':is_superuser,'is_centeradmin':is_centeradmin,'is_delivery_coordinator':is_delivery_coordinator,'backfill_offer_slots':backfill_offer_slots,
          'admin_assigned_center':admin_assigned_center,'dc_assigned_center':dc_assigned_center,'ay_id':ay_id,'get_stickers_for_teachers':get_stickers_for_teachers,
          'get_stickers_for_students':get_stickers_for_students, 'current_ay':current_ay,
          'add_course_dropdown_courses':simplejson.dumps(add_course_dropdown_courses_list),'add_course_dropdown_academic_year':simplejson.dumps(add_course_dropdown_academic_year_list),'map_location_link':map_location_link,
          'academic_year_data' : dict(academic_year_date_month_dict),
          'center_id' : center_id,
          'academic_years' : academic_years,
          'selected_month' : calendar.month_name[selected_month],
          "selected_year" : selected_year,
          "selected_academic_year" : selected_academic_year,
          "current_academic_year_available" : current_academic_year_available
          })








def myteachers(request):
    if request.GET.get('drop_teacher') == "category":
        reason = {}
        reason_category = DropTeacherReason.objects.values_list("category",flat = True).distinct()
        reason['category'] = list(reason_category)

        return HttpResponse(json.dumps(reason), content_type='application/json')
    elif request.GET.get('drop_teacher') == "reason":
        category_selected = request.GET.get('category_selected')
        reason = {}
        reason_list = DropTeacherReason.objects.values_list("reason",flat = True).filter(category = category_selected).distinct()
        reason['reason'] = list(reason_list)
        return HttpResponse(json.dumps(reason), content_type='application/json')
    
    elif request.user.is_authenticated():
        user_profile = UserProfile.objects.filter(user=request.user)[0]
        roles = user_profile.role.values_list('name', flat=True)
        if roles:
            user_role = roles[0]
            if "Center Admin" in roles:
                is_centeradmin = True
            else:
                is_centeradmin = False
            if 'Delivery co-ordinator' in roles:
                is_dc = True
            else:
                is_dc = False


        if request.user.is_superuser or is_centeradmin or request.user.partner_set.all() or is_dc:
            center_id = request.GET.get('center_id')
            teacher_id = request.GET.get('teacher_id')
            center = Center.objects.get(id=center_id)
            past_teacher_obj = None
            if teacher_id:
                teacher_obj = Offering.objects.filter(center=center, status='running',
                                                      active_teacher_id=teacher_id).values('active_teacher__id',
                                                                                           'active_teacher__first_name',
                                                                                           'active_teacher__last_name',
                                                                                           'active_teacher__email',
                                                                                           'course')
                if teacher_obj.count() < 1:
                    past_teacher_obj = Session.objects.filter(offering__status='running', teacher_id=teacher_id).values(
                        'teacher__id', 'teacher__first_name', 'teacher__last_name', 'teacher__email',
                        'offering__course')
            else:
                teacher_obj = Offering.objects.filter(center=center, status='running').values('active_teacher__id',
                                                                                              'active_teacher__first_name',
                                                                                              'active_teacher__last_name',
                                                                                              'active_teacher__email',
                                                                                              'course')
            active_teachers = {}
            if teacher_obj:
                for active_teacher in teacher_obj:
                    if active_teacher['active_teacher__id']:
                        active_teachers[active_teacher['active_teacher__id']] = {}
                        active_teachers[active_teacher['active_teacher__id']]['name'] = str(
                            active_teacher['active_teacher__first_name']) + " " + str(
                            active_teacher['active_teacher__last_name'])
                        active_teachers[active_teacher['active_teacher__id']]['email'] = active_teacher[
                            'active_teacher__email']
                        active_teachers[active_teacher['active_teacher__id']]['course'] = active_teacher['course']
                        teacher_obj_pro = \
                        UserProfile.objects.filter(user_id=active_teacher['active_teacher__id']).values('phone', 'city',
                                                                                                   'pref_medium',
                                                                                                   'role', 'from_date',
                                                                                                   'to_date', 'picture',
                                                                                                   'skype_id',
                                                                                                   'short_notes')[0]
                        active_teachers[active_teacher['active_teacher__id']]['phone'] = teacher_obj_pro['phone']
                        active_teachers[active_teacher['active_teacher__id']]['city'] = teacher_obj_pro['city']
                        active_teachers[active_teacher['active_teacher__id']]['medium'] = teacher_obj_pro['pref_medium']
                        active_teachers[active_teacher['active_teacher__id']]['picture'] = teacher_obj_pro['picture']
                        active_teachers[active_teacher['active_teacher__id']]['skype'] = teacher_obj_pro['skype_id']
                        active_teachers[active_teacher['active_teacher__id']]['short_notes'] = teacher_obj_pro[
                            'short_notes']
                        active_teachers[active_teacher['active_teacher__id']]['from_date'] = teacher_obj_pro[
                            'from_date'].strftime('%m/%d/%Y') if teacher_obj_pro['from_date'] else ''
                        active_teachers[active_teacher['active_teacher__id']]['to_date'] = teacher_obj_pro[
                            'to_date'].strftime('%m/%d/%Y') if teacher_obj_pro['to_date'] else ''
                return HttpResponse(json.dumps(active_teachers), content_type='application/json')
            elif past_teacher_obj:
                for active_teacher in past_teacher_obj:
                    if active_teacher['teacher__id']:
                        active_teachers[active_teacher['teacher__id']] = {}
                        active_teachers[active_teacher['teacher__id']]['name'] = str(
                            active_teacher['teacher__first_name']) + " " + str(active_teacher['teacher__last_name'])
                        active_teachers[active_teacher['teacher__id']]['email'] = active_teacher['teacher__email']
                        active_teachers[active_teacher['teacher__id']]['course'] = active_teacher['offering__course']
                        past_teacher_obj_pro = \
                        UserProfile.objects.filter(id=active_teacher['teacher__id']).values('phone', 'city',
                                                                                            'pref_medium', 'role',
                                                                                            'from_date', \
                                                                                            'to_date', 'picture',
                                                                                            'skype_id', 'short_notes')[
                            0]
                        active_teachers[active_teacher['teacher__id']]['phone'] = past_teacher_obj_pro['phone']
                        active_teachers[active_teacher['teacher__id']]['city'] = past_teacher_obj_pro['city']
                        active_teachers[active_teacher['teacher__id']]['medium'] = past_teacher_obj_pro['pref_medium']
                        active_teachers[active_teacher['teacher__id']]['picture'] = past_teacher_obj_pro['picture']
                        active_teachers[active_teacher['teacher__id']]['skype'] = past_teacher_obj_pro['skype_id']
                        active_teachers[active_teacher['teacher__id']]['short_notes'] = past_teacher_obj_pro[
                            'short_notes']
                        active_teachers[active_teacher['teacher__id']]['from_date'] = past_teacher_obj_pro[
                            'from_date'].strftime('%m/%d/%Y') if past_teacher_obj_pro['from_date'] else ''
                        active_teachers[active_teacher['teacher__id']]['to_date'] = past_teacher_obj_pro[
                            'to_date'].strftime('%m/%d/%Y') if past_teacher_obj_pro['to_date'] else ''

                return HttpResponse(json.dumps(active_teachers), content_type='application/json')
            else:
                return HttpResponse(active_teachers)
    else:
        return HttpResponse("You are not authenticated")


def get_students(request):
    pathname = request.GET.get("pathname", "/myevidyaloka/")
    center_id = request.GET.get("center_id", "")
    course_id = request.GET.get("course_id", None)

    if request.user.is_superuser and pathname == "/myevidyaloka/":
        return HttpResponse("Failed")

    if pathname == "/centeradmin/" or pathname == "/myevidyaloka/":
        course = None; students = []; students_list = []
        if course_id is not None:
            course = get_object_or_none(Course, id=course_id)
        if course is not None and len(course.grade) <= 2:
            students = Student.objects.filter(center_id=center_id, grade=int(course.grade), status="Active")
        else:
            students = Student.objects.filter(center_id=center_id, status="Active")

        for student in students:
            students_list.append({"id": student.id, "name": student.name})

        return HttpResponse(simplejson.dumps(students_list), mimetype='application/json')
    else:
        return HttpResponse("Failed")


def make_weekday(weekday):
    if weekday == 0:
        day = "Mon"
    elif weekday == 1:
        day = "Tue"
    elif weekday == 2:
        day = "Wed"
    elif weekday == 3:
        day = "Thur"
    elif weekday == 4:
        day = "Fri"
    elif weekday == 5:
        day = "Sat"
    elif weekday == 6:
        day = "Sun"
    return day


# recommendations for the respective pending course in centeradmin
def centeradmin_reco(request):
    offering_id = request.GET.get("offering_id", None)
    unassigned_offerings = Offering.objects.filter(id=offering_id)
    html_reco = []
    has_recommendations = False
    for offer in unassigned_offerings:
        reco1, user_ids = get_reco1(offer)
        reco2, user_ids1 = get_reco2(offer, user_ids)
        user_ids.extend(user_ids1)
        reco3 = get_reco3(offer, user_ids)
        reco = {"reco1": reco1, "reco2": reco2, "reco3": reco3}
        has_recommendations = True

        if not bool(reco1 or reco2 or reco3):
            has_recommendations = False

        start_date = offer.start_date if offer.start_date else datetime.datetime.today()
        end_date = offer.end_date if offer.end_date else datetime.datetime.today() + datetime.timedelta(weeks=6)

        html_reco.append({"offer": make_number_verb(offer.course.grade) + " " + offer.course.subject, "reco": reco,
                          "offer_id": offer.id, "subject": offer.course.subject, "start_date": start_date,
                          "end_date": end_date, "medium": offer.language})

    return render_response(request, 'centeradmin_reco.html',
                           {"html_reco": html_reco, "has_recommendations": has_recommendations})

from django.contrib import messages
def add_course(request):
    try:
        course_id = request.POST['course_id']
        ay_id = request.POST['ay_id']
        center_id = request.POST['center_id']
        langauge = request.POST['language']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        batch = request.POST['batch']
        program_type = request.POST['program_type']
        
        print(start_date)
        print(end_date)

        status = 'pending'
        planned_topics = request.POST['planned_topics'].split(";")
        students = request.POST['students'].split(";")
        start_date = datetime.datetime.strptime(start_date.strip(), "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date.strip(), "%Y-%m-%d")
        cur_date = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
        course = Course.objects.get(id=course_id)
        ay = Ayfy.objects.get(id=ay_id)
        center = Center.objects.get(id=center_id)
        course_type = course.type
        if course_type:
            course_type = course_type.lower()
        if course_type is not None and course_type == 'c':
            status = 'not_approved'
        offering = Offering.objects.create(course=course, academic_year=ay, center=center, language=langauge, batch=int(batch),
                                        start_date=start_date, end_date=end_date, status=status, course_type=course_type,
                                        created_date = cur_date,created_by = request.user, program_type = str(program_type))
        if planned_topics:
            for topic in planned_topics:
                if topic:
                    planned_topic = Topic.objects.filter(id=topic)
                    offering.planned_topics.add(topic)
        if students:
            for student in students:
                if student:
                    s = Student.objects.get(id=student)
                    offering.enrolled_students.add(s)
                    Offering_Enrolled_Students_History.objects.create(student=s, offering=offering, assignment_status=1, created_by=request.user, updated_by=request.user)
        save_user_activity(request, 'Added Course:' + str(course), 'Action')
        offering.save()
        
        if status == 'not_approved':
            messages.info(request, "You have added " + str(course) + ", An approval is needed or wait till the team approves the course")
        return HttpResponse("success")
    except Exception as e:
        logService.logException("ContentDemand PUT Exception error", e.message)
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


def get_planned_topics(request):
    course_id = request.GET.get('course_id', None)
    course = Course.objects.filter(id=course_id)
    planned_topics = Topic.objects.filter(course_id=course).order_by('priority')
    planned_topics_arr = []
    for topic in planned_topics:
        planned_topic = {
            "topic_id": topic.id,
            "title": topic.title
        }
        planned_topics_arr.append(planned_topic)

    return HttpResponse(simplejson.dumps(planned_topics_arr), mimetype='application/json')


@csrf_exempt
def current_sessions(request):
    offering_id = request.GET.get("offering_id", None)
    sessions = Session.objects.filter(offering_id=offering_id).order_by('date_start')
    course_id = Offering.objects.get(id=offering_id).course.id
    center_language = Offering.objects.get(id=offering_id).center.language
    user_profiles = UserProfile.objects.filter(pref_medium=center_language)
    users = []
    for profile in user_profiles:
        user = {"id": profile.user.id, "name": profile.user.first_name + " " + profile.user.last_name}
        users.append(user)
    sessions_arr = []
    topics = Topic.objects.filter(course_id=course_id).order_by('priority')
    topics_list = []
    for topic in topics:
        topics_list.append(topic.title)
    for session in sessions:
        planned_topics = session.planned_topics.all()
        planned_topic = ""
        if planned_topics:
            for topic in planned_topics:
                planned_topic = topics = topic.title
        weekday = session.date_start.weekday()
        day = make_weekday(weekday)
        cur_session = {
            "course_offered": make_number_verb(
                session.offering.course.grade) + ' ' + session.offering.course.subject + ', ' + session.offering.center.name + ' - ' +
                              make_date_time(session.date_start)["date"] + ', ' + make_date_time(session.date_start)[
                                  "time"] + ' to ' + make_date_time(session.date_end)["time"],
            # "start_date": session.date_start,
            # "end_date": session.date_end,
            "subject": session.offering.course.subject,
            "day": day,
            "start_time": session.date_start.strftime('%H:%M'),  # modify to return min also
            "end_time": session.date_end.strftime('%H:%M'),  # modify to return min also
            "planned_topic": planned_topic,
            "session_id": session.id,
            "teacher": session.teacher.first_name + " " + session.teacher.last_name,
        }

        teacher = session.teacher.id
        sessions_arr.append(cur_session)
    temp_resp = {'sessions': sessions_arr, 'offering_id': offering_id, 'teacher': teacher, 'users': users,
                 'topics': topics_list}
    return HttpResponse(simplejson.dumps(temp_resp), mimetype='application/json')
    # return render_response(request, 'current_sessions.html', {"sessions": sessions_arr, "offering_id": offering_id, "teacher":teacher, "users":users, "topics":topics_list })


def modify_session(request):
    try:
        session_ids = request.POST['sessions'].split(";")
        start_times = request.POST['start_time'].split(";")
        end_times = request.POST['end_time'].split(";")
        removed_sessions = request.POST['removed_sessions'].split(";")
        dates = request.POST['dates'].split(";")
        planned_topics = request.POST['planned_topics'].split(";")
        new_sessions = int(request.POST['new_sessions'])
        teacher_ids = request.POST['teacher_ids'].split(";")
        offering_id = request.POST['offering_id']
        software_link = request.POST['software_link'].split(";")
        software = request.POST['software'].split(";")
        modes = request.POST['modes'].split(";")
        video_urls = request.POST['video_links'].split(';')
        print request.POST
        offering = Offering.objects.filter(id=offering_id)[0]
        curr_date = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
        offering_update = ''
        next_sess = 0
        count = 0
        offering_new_session = Offering.objects.get(id=offering_id)
        session_id_new_creation = session_ids
        session_id_selected = session_ids
        for session in session_id_selected:
            if session_id_selected[-1] == "":
                session_id_selected = session_id_selected[:-1]

        start_time_new = start_times[:-1]
        end_time_new = end_times[:-1]
        dates_new = dates[:-1]
        teacher_new = teacher_ids[:-1]
        software_new = software[:-1]
        software_link_new = software_link[:-1]
        diff = len(dates_new) - len(session_id_selected)
        if diff >0:
            start_times_new_session = start_time_new[-diff:]
            end_times_new_session = end_time_new[-diff:]
            dates_new_session = dates_new[-diff:]
            teacher_new_session = teacher_new[-diff:]
            software_new_session = software_new[-diff:]
            software_link_new_session = software_link_new[-diff:]

            index = 0
            for date in dates_new_session:
                date_start = datetime.datetime.strptime(dates_new_session[index], "%d-%m-%Y").strftime("%Y-%m-%d") + " " + str(start_times_new_session[index])
                date_end = datetime.datetime.strptime(dates_new_session[index], "%d-%m-%Y").strftime("%Y-%m-%d") + " " + str(end_times_new_session[index])
                s = Session.objects.create(teacher=User.objects.get(id=teacher_new_session[index].split(":")[0]), date_start=date_start,
                                                    date_end= date_end, offering=offering_new_session, teachingSoftware=TeachingSoftwareDetails.objects.get(id = software_new_session[index]),
                                                        ts_link=software_link_new_session[index],dt_added = curr_date,created_by =User.objects.get(id = request.user.id), video_link=video_urls[index],mode=modes[index])
                s.save()
                index += 1
        # session_id_selected = request.POST['sessions'].split(";")[:-1]
        print software,software_link, video_urls,modes 
        for session in session_id_selected:
            offering_id = Session.objects.get(id = session)
            try:
                session_link = Session.objects.values_list('ts_link',flat=True).filter(~Q(ts_link = '') & Q(offering_id = offering_id.offering_id))[0]
            except:
                session_link = ""
            ts_link = software_link[count]
            teachingSoftware = software[count]
            if ts_link == '':
                ts_link = session_link
            if teachingSoftware == '':
                teachingSoftware = '2'
            Session.objects.filter(id= session).update(teachingSoftware = teachingSoftware,ts_link = ts_link, video_link=video_urls[count],mode=modes[count])
            count += 1
        session_ids = session_id_selected
        for index, session_id in enumerate(session_ids):
            if session_id:
                session = Session.objects.get(id=session_id)
                s_hour = int(start_times[index].split(":")[0])
                e_hour = int(end_times[index].split(":")[0])
                try:
                    s_min = int(start_times[index].split(":")[1])
                    e_min = int(end_times[index].split(":")[1])
                except IndexError:
                    s_min = 0
                    e_min = 0

                date = datetime.datetime.strptime(str(dates[index]).strip(), "%d-%m-%Y")
                planned_topics_arr = []
                topics = planned_topics[index]
                for topic in session.planned_topics.all():
                    session.planned_topics.remove(topic)
                for topic in topics.split(","):
                    if topic:
                        try:
                            planned_topic = Topic.objects.filter(id=topic)
                        except:
                            planned_topic = []
                    if planned_topic:
                        planned_topics_arr.append(planned_topic[0])
                for topic in planned_topics_arr:
                    session.planned_topics.add(topic)
                session.date_start = datetime.datetime(date.year, date.month, date.day, s_hour, s_min)
                session.date_end = datetime.datetime(date.year, date.month, date.day, e_hour, e_min)
                if (len(teacher_ids) > index and teacher_ids[index] != ''):
                    teacher_id = teacher_ids[index].split('::')
                    tchr = User.objects.get(id=int(teacher_id[0]))
                    session.teacher = tchr
                    if session.date_start >= curr_date and next_sess == 0:
                        offering_update = tchr
                        next_sess = 1
                if len(software_link) > index and software_link[index] != '':
                    tsd = TeachingSoftwareDetails.objects.filter(id=int(software[index]))[0]
                    session.teachingSoftware = tsd
                    session.ts_link = software_link[index]
                if len(video_urls) > index and video_urls[index] != '':
                    session.video_link = video_urls[index]

                if len(modes) > index and modes[index] != '':
                    session.mode = modes[index]
                try:
                    session.dt_updated = curr_date
                    session.updated_by = request.user
                    session.save()
                except:
                    pass
        Offering.objects.filter(id=offering.id).update(active_teacher=offering_update,updated_by = request.user, updated_date = curr_date)
        rs = [int(x) for x in removed_sessions if x]
        ses = Session.objects.filter(id__in=rs).delete()
        new_start_times = request.POST['new_start_time'].split(";")
        new_end_times = request.POST['new_end_time'].split(";")
        new_dates = request.POST['new_dates'].split(";")
        new_planned_topics = request.POST['new_planned_topics'].split(";")
        new_teacher_ids = request.POST['new_teacher_ids'].split(";")
        for index in range(new_sessions):
            noDuplicateSession=True
            s_hour = int(new_start_times[index].split(":")[0])
            e_hour = int(new_end_times[index].split(":")[0])
            try:
                s_min = int(new_start_times[index].split(":")[1])
                e_min = int(new_end_times[index].split(":")[1])
            except IndexError:
                s_min = 0
                e_min = 0
            teacher_id = new_teacher_ids[index].split('::')
            teacher = User.objects.get(id=int(teacher_id[0]))
            date = datetime.datetime.strptime(str(new_dates[index]).strip(), "%d-%m-%Y")
            startdate = datetime.datetime(date.year, date.month, date.day, s_hour, s_min)
            enddate = datetime.datetime(date.year, date.month, date.day, e_hour, e_min)
            new_planned_topics_arr = []
            topics = new_planned_topics[index]

            #new code
            sesionObjects=Session.objects.filter(offering__id=offering_id.offering_id)
            for eachsession in sesionObjects:
                if startdate >= eachsession.date_start and startdate < eachsession.date_end:
                    noDuplicateSession=False
                    break
            if  noDuplicateSession == False:
                if startdate <= offering.academic_year.end_date:
                    session = Session.objects.create(offering = offering, date_start = startdate, date_end = enddate, teacher = teacher,created_by = request.user )
            #end code

            for topic in topics.split(","):
                if topic != '':
                    planned_topic = Topic.objects.filter(title=topic)
                    if planned_topic:
                        new_planned_topics_arr.append(planned_topic[0])

            for topic in new_planned_topics_arr:
                session.planned_topics.add(topic)
            session.save()

        return HttpResponse("success")
    except Exception as e:
        print("Error reason =================================", e)
        print "Error at line no ==============================", traceback.format_exc()



def get_offering(center, session):
    offering = []
    sessions = []
    for s in session:
        if s.offering.center == center:
            offering.append(s.offering)
    return offering


# Best recommendations, contains exact match of offering from the teachers database
def get_reco1(offering):
    mapping = []
    users = UserProfile.objects.filter(pref_offerings=offering).exclude(user__last_name='', user__first_name='')
    stack_teachers = UserProfile.objects.filter(user__stackteacher__offering=offering)
    user_ids = []

    for user in users:
        pref_offering = user.pref_offerings.all()

        # by default status of the recommendation is None, representing that centeradmin has not sent any request to the teacher
        status = None

        # if centeradmin has already requested the teacher, the status of that request is stored in the status
        if user in stack_teachers:
            st = StackTeacher.objects.filter(teacher=user.user, offering=offering)
            if st:
                status = st[0].status
        pref_offering_arr = []

        for offering in pref_offering:
            pref_offering_arr.append(make_number_verb(
                offering.course.grade) + " " + offering.course.subject + ", " + offering.center.name + ", " +
                                     make_date_time(offering.start_date)["date"] + "-" +
                                     make_date_time(offering.end_date)["date"])

        user_ids.append(user.user.id)
        pref_days = user.pref_days.split(";")
        pref_slots = user.pref_slots.split(";")
        pref_days_arr = []

        if user.pref_days:
            for day_index, day in enumerate(pref_days):
                slots = pref_slots[day_index].split("-")
                slot = make_hour(slots[0].split(':')[0]) + "-" + make_hour(slots[1].split(':')[0])
                # slot = make_hour(slots[0]) + "-" + make_hour(slots[1])
                pref_day = day + " ( " + slot + " )"
                pref_days_arr.append(pref_day)

        pref_medium = user.pref_medium
        from_date = make_date_time(user.from_date)["date"]
        to_date = make_date_time(user.to_date)["date"]

        mapping.append(
            {"teacher": user.user, "offerings": pref_offering_arr, "status": status, "pref_days": pref_days_arr,
             "pref_medium": pref_medium, "from_date": from_date, "to_date": to_date,
             "pref_subjects": user.pref_subjects})
    return mapping, user_ids


# Second best recommendations,conatins similar match of the offering irrespective of the offering centers,
# and also checks the availability of the teachers for the offering period
def get_reco2(offering, user_ids):
    mapping = []
    teachers = []
    user_ids1 = []
    users = []

    sub = offering.course.subject
    lan = offering.language
    sub_offers = Offering.objects.filter(course__subject=sub, language=lan)

    for sub_offer in sub_offers:
        start_date = sub_offer.start_date.date() if sub_offer.start_date else ""
        users = User.objects.exclude(pk__in=user_ids)
        users = UserProfile.objects.filter(user__in=users).filter(
            pref_offerings=sub_offer)  # .exclude(user__stackteacher__offering = offering)
        stack_teachers = UserProfile.objects.filter(user__stackteacher__offering=offering)

    for user in users:
        if not start_date == "":
            if start_date > user.from_date.date():
                teachers.append(user)
                user_ids1.append(user.user.id)

        # by default status of the recommendation is None, representing that centeradmin has not sent any request to the teacher
        status = None

        # if centeradmin has already requested the teacher, the status of that request is stored in the status
        if user in stack_teachers:
            st = StackTeacher.objects.filter(teacher=user.user, offering=offering)
            if st:
                status = st[0].status

        pref_offering_arr = []
        for offering in user.pref_offerings.all():
            pref_offering_arr.append(make_number_verb(
                offering.course.grade) + " " + offering.course.subject + ", " + offering.center.name + ", " +
                                     make_date_time(offering.start_date)["date"] + "-" +
                                     make_date_time(offering.end_date)["date"])

        pref_days = user.pref_days.split(";")
        pref_slots = user.pref_slots.split(";")
        pref_days_arr = []
        if user.pref_days:
            for day_index, day in enumerate(pref_days):
                slots = pref_slots[day_index].split("-")
                # slot = make_hour(slots[0]) + "-" + make_hour(slots[1])
                slot = make_hour(slots[0].split(':')[0]) + "-" + make_hour(slots[1].split(':')[0])
                pref_day = day + " ( " + slot + " )"
                pref_days_arr.append(pref_day)

        pref_medium = user.pref_medium
        from_date = make_date_time(user.from_date)["date"]
        to_date = make_date_time(user.to_date)["date"]
        mapping.append(
            {"teacher": user.user, "offerings": pref_offering_arr, "status": status, "pref_days": pref_days_arr,
             "pref_medium": pref_medium, "from_date": from_date, "to_date": to_date,
             "pref_subjects": user.pref_subjects})

    return mapping, user_ids1


# Third Best recommendations, contains a match of offering subject and medium from user prefrences
def get_reco3(offering, user_ids):
    mapping = []
    sub = offering.course.subject
    lan = offering.center.language
    users = User.objects.exclude(pk__in=user_ids)
    users = UserProfile.objects.filter(user__in=users).filter(pref_subjects__contains=sub,
                                                              pref_medium__contains=lan)  # .exclude(user__stackteacher__offering = offering)
    stack_teachers = UserProfile.objects.filter(user__stackteacher__offering=offering)
    for user in users:

        # by default status of the recommendation is None, representing that centeradmin has not sent any request to the teacher
        status = None

        # if centeradmin has already requested the teacher, the status of that request is stored in the status
        if user in stack_teachers:
            st = StackTeacher.objects.filter(teacher=user.user, offering=offering)
            if st:
                status = st[0].status

        pref_offering_arr = []
        for offering in user.pref_offerings.all():
            pref_offering_arr.append(make_number_verb(
                offering.course.grade) + " " + offering.course.subject + ", " + offering.center.name + ", " +
                                     make_date_time(offering.start_date)["date"] + "-" +
                                     make_date_time(offering.end_date)["date"])
        pref_days = user.pref_days.split(";")
        pref_slots = user.pref_slots.split(";")
        pref_days_arr = []
        if user.pref_days:
            for day_index, day in enumerate(pref_days):
                slots = pref_slots[day_index].split("-")
                print slots
                # slot = make_hour(slots[0]) + "-" + make_hour(slots[1])
                if len(slots) == 2:
                    slot = make_hour(slots[0].split(':')[0]) + "-" + make_hour(slots[1].split(':')[0])
                else:
                    slot = ''

                pref_day = day + " ( " + slot + " )"
                pref_days_arr.append(pref_day)

        pref_medium = user.pref_medium
        from_date = make_date_time(user.from_date)["date"]
        to_date = make_date_time(user.to_date)["date"]
        mapping.append(
            {"teacher": user.user, "offerings": pref_offering_arr, "status": status, "pref_days": pref_days_arr,
             "pref_medium": pref_medium, "from_date": from_date, "to_date": to_date,
             "pref_subjects": user.pref_subjects})
    return mapping


# session attendace by the teacher
def attendance(request):
    if request.method == "POST":
        offering_id = request.POST['offering']
        offering = Offering.objects.filter(id=offering_id)[0]
        students = offering.enrolled_students.all()
        sessions = Session.objects.filter(offering=offering)

    return render_response(request, 'attendance.html', {"sessions": sessions, "students": students})


# search for teachers according to the mentioned parameters
@login_required
def lookup(request):
    cur_subject = request.GET.get('subject', "all")
    cur_medium = request.GET.get('medium', 'all')
    cur_role = request.GET.get('role', 'all')
    cur_from_date = request.GET.get('from', 'all')
    cur_to_date = request.GET.get('to', 'all')
    teacher_id = request.GET.get('teacher_id', None)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    subjects = []
    roles = []

    # jquery template for rendering user block in lookup page
    TEACHER_TEMPLATE = '''
                                        <div class='user-block' style='float:left;width:470px' rel='tooltip' title='${short_notes}' data-placement='left'>
                                            <div style='width:460px;border:1px solid #8E8B8A;min-height:260px;overflow:hidden;clear:both;margin-top:10px;'>
                                                <div style='overflow:hidden;position:absolute;'>
                                                    <form ='/save_remarks/' method='POST' id='remarks-form' data-userid='${id}'>
                                                    <div style='overflow:hidden;background:#E6E6FA'>
                                                          <img alt="userPic" class='user-pic' src='${picture}' style='float:left;width:100px;height:100px'>
                                                          <div class='general-information'>
                                                              <p class='username'>${name}</p>
                                                              <p style='float:right'>
                                                                <select name='status' style='float:right'>
                                                                    <option{{if status == "New"}} selected="selected"{{/if}}>New</option>
                                                                    <option{{if status == "Ready"}} selected="selected"{{/if}}>Ready</option>
                                                                    <option{{if status == "Active"}} selected="selected"{{/if}}>Active</option>
                                                                    <option{{if status == "Dormant"}} selected="selected"{{/if}}>Dormant</option>
                                                                    <option{{if status == "Non-Active"}} selected="selected"{{/if}}>Non-active</option>
                                                                </select>
                                                              </p>
                                                              <p style='clear:both;margin-top:0px;width:340px;'>${role}</p>
                                                              <p style='clear:both;'><label>Medium: </label>${medium}</p>
                                                              <p><label>Location: </label>${location}</p>
                                                              <p><label>Avail From: </label>${from}</p>
                                                              <p><label>Avail To: </label>${to}</p>
                                                          </div>
                                                      </div>
                                                      <div style='width:440px;min-height:50px;font-size:small;padding:0px 10px;'>
                                                        <div class='info'>
                                                          <p class='email'><label>Email: </label>${email}</p>
                                                          <p class='phone'><label>Phone: </label>${phone}</p>
                                                          <p class='skypeid'><label>SkypeId: </label>${skype_id}</p>


                                                        </div>
                                                        <p style='margin-top:5px;'><label>Current courses: </label>${current_courses}</p>
                                                      </div>
                                                      <div class='general_info preferences'>
                                                          <p><label>Hours Contributed: </label>${hrs_contributed}</p>
                                                          <p style='float:left'><label>Remarks: </label></p>
                                                          <p style='float:left;padding-left:10px;'>
                                                                <input type='hidden' name='step' value=5 />
                                                                <input type='hidden' name='user_id' value='${id}' />
                                                                <textarea class='enabled' name='remarks' rows=2 cols=50 style='width:100%'>${remarks}</textarea>
                                                          </p>
                                                            <a class='btn hide' data-userid='${id}' rel='submit' pre-call="pre_save" callback='after_save' href='#remarks-form' style='cursor:pointer;width:50px;font-size:12px;float:right;line-height:18px;height:20px;'><span class='ajax-button-label' data-loading='wait'>Save</span></a>
                                                      </div>
                                                    </form>
                                                  </div>
                                                  <div class='preferences' style='padding:10px;float:left;width:440px;display:none'>
                                                      <p><label>Preferred Courses: </label></p>
                                                      <p>${courses}</p>
                                                  </div>
                                        </div>
                                    </div>
    '''

    courses = Course.objects.all()
    rol = Role.objects.all()
    seea_all_details = False
    for course in courses:
        subjects.append(course.subject)
    subjects = list(set(subjects))
    subjects.sort()
    for rl in rol:
        roles.append(rl.name)
    roles = list(set(roles))
    roles.sort()
    medium = ["Bengali", "Gujarathi", "Hindi", "Kannada", "Malayalam", "Marathi", "Oriya", "Punjabi", "Tamil", "Telugu",
              "Urdu"]

    if request.user.is_staff:
        return render_response(request, 'lookup.html',
                               {"days": days, "subjects": subjects, "medium": medium, "roles": roles,
                                "cur_subject": cur_subject, "cur_medium": cur_medium, "cur_role": cur_role,
                                "cur_from_date": cur_from_date, "cur_to_date": cur_to_date,
                                "TEACHER_TEMPLATE": TEACHER_TEMPLATE, "teacher_id": teacher_id})
    else:
        return HttpResponseRedirect(reverse('myevidyaloka'))


@login_required
def lookup1(request):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    subjects = []
    courses = Course.objects.all()
    for course in courses:
        subjects.append(course.subject)
    subjects = list(set(subjects))
    medium = ["Bengali", "Gujarathi", "Hindi", "Kannada", "Malayalam", "Marathi", "Oriya", "Punjabi", "Tamil", "Telugu",
              "Urdu"]

    return render_response(request, 'lookup1.html', {"days": days, "subjects": subjects, "medium": medium})


def transpose(course_table):
    today = datetime.datetime.now()
    course_table_tr = []
    month6 = []
    month6.append(1)
    month6.append(0)
    month7 = []
    month7.append(2)
    month7.append(5)
    month8 = []
    month8.append(3)
    month8.append(10)
    month9 = []
    month9.append(4)
    month9.append(15)
    month10 = []
    month10.append(5)
    month10.append(20)
    month11 = []
    month11.append(6)
    month11.append(22)
    month12 = []
    month12.append(7)
    month12.append(25)
    month1 = []
    month1.append(8)
    month1.append(28)
    month2 = []
    month2.append(9)
    month2.append(32)
    month3 = []
    month3.append(10)
    month3.append(36)
    month4 = []
    month4.append(11)
    month4.append(40)
    for entry in course_table:
        month6.append(entry['plot'][0])
        month7.append(entry['plot'][1])
        month8.append(entry['plot'][2])
        month9.append(entry['plot'][3])
        month10.append(entry['plot'][4])
        month11.append(entry['plot'][5])
        month12.append(entry['plot'][6])
        month1.append(entry['plot'][7])
        month2.append(entry['plot'][8])
        month3.append(entry['plot'][9])
        month4.append(entry['plot'][10])

    course_table_tr = [month6, month7, month8, month9, month10, month11, month12, month1, month2, month3, month4]
    # currmonth = today.month
    # if currmonth > 5:
    #     index = currmonth - 6
    # elif currmonth < 5:
    #     index = currmonth + 6
    # else:
    #     index = 10

    # for k in range(len(course_table_tr)):
    #     if k > index:
    #         for ent in range(len(course_table_tr[k])):
    #             if ent > 1:
    #                 course_table_tr[k][ent] = None

    return course_table_tr


def cummulative(course_table):
    for entry in course_table:
        for i in range(0, 10):
            temp = entry['plot'][i]
            entry['plot'][i + 1] = temp + entry['plot'][i + 1]

    return course_table


def getAllCenters(request):
    centers_all = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return None
    roles = user_profile.role.values_list('name', flat=True)

    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
        user=settings.DATABASES['default']['USER'],
        passwd=settings.DATABASES['default']['PASSWORD'],
        db=settings.DATABASES['default']['NAME'],
        charset="utf8",
        use_unicode=True)

    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    if len(user_profile.role.filter(name = "School Admin")) > 0:
        centers_all = Center.objects.filter(Q(delivery_partner_id=request.user.partner_set.values()[0]['id']))
    elif request.user.partner_set.values():
        if request.user.partner_set.all()[0].partnertype.values() and request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 2:
            if roles:
                if "Delivery co-ordinator" in roles and 'OUAdmin' in roles or request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 4:
                    centers_all = Center.objects.filter(Q(delivery_coordinator_id=request.user.id) | Q(delivery_partner_id=request.user.partner_set.all()[0].id) | Q(Q(orgunit_partner_id=request.user.partner_set.all()[0].id)))
                elif "Delivery co-ordinator" in roles:
                    centers_all = Center.objects.filter(
                        delivery_coordinator_id=request.user.id) | Center.objects.filter(
                        delivery_partner_id=request.user.partner_set.all()[0].id)
                elif 'Partner Account Manager' in roles:
                        query = "select partner_id  as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                        dict_cur.execute(query)
                        partner_id = [str(each['value']) for each in dict_cur.fetchall()]
                        partner_id.sort()
                        partner_id= tuple(partner_id)
                        partner_id= partner_id[0]
                        #print "partner_id",partner_id
                        centers_all = Center.objects.filter(Q(delivery_partner_id__in=partner_id) | Q(funding_partner_id__in=partner_id))
                elif 'OUAdmin' in roles or request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 4:
                    centers_all = Center.objects.filter(Q(delivery_partner_id=request.user.partner_set.all()[0].id) | Q(orgunit_partner_id=request.user.partner_set.all()[0].id))
                else:
                    centers_all = Center.objects.filter(delivery_partner_id=request.user.partner_set.all()[0].id)
                try:
                    centers_all = centers_all.filter(status='Active')
                except:
                    centers_all = None
        else:
            if roles:
                if "Delivery co-ordinator" in roles and 'OUAdmin' in roles or request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 4:
                    centers_all = Center.objects.filter(Q(delivery_coordinator_id=request.user.id) | Q(funding_partner_id=request.user.partner_set.all()[0].id) | Q(orgunit_partner_id=request.user.partner_set.all()[0].id))
                elif "Delivery co-ordinator" in roles:
                    centers_all = Center.objects.filter(
                        delivery_coordinator_id=request.user.id) | Center.objects.filter(
                        funding_partner_id=request.user.partner_set.all()[0].id)
                elif 'Partner Account Manager' in roles:
                        query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                        dict_cur.execute(query)
                        partner_id = [str(each['value']) for each in dict_cur.fetchall()]
                        partner_id.sort()
                        partner_id= tuple(partner_id)
                        partner_id= partner_id[0]
                        centers_all = Center.objects.filter(Q(delivery_partner_id__in=partner_id) | Q(funding_partner_id__in=partner_id))
                elif 'OUAdmin' in roles or request.user.partner_set.all()[0].partnertype.values()[0]['id'] == 4:
                    centers_all = Center.objects.filter(Q(funding_partner_id=request.user.partner_set.all()[0].id) | Q(orgunit_partner_id=request.user.partner_set.all()[0].id))
                else:
                    centers_all = Center.objects.filter(Q(funding_partner_id=request.user.partner_set.all()[0].id) | Q(delivery_partner_id=request.user.partner_set.all()[0].id))
                try:
                    if centers_all is None or len(centers_all) <= 0:
                        centers_all = Center.objects.filter(Q(digital_school_partner_id=request.user.partner_set.all()[0].id))
                    else:
                        pass

                    centers_all = centers_all.filter(status='Active')
                except:
                    centers_all = None

    elif not request.user.is_superuser:
        if roles:
            filters = {}
            if 'Partner Account Manager' in roles:
                query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                dict_cur.execute(query)
                partner_id = [str(each['value']) for each in dict_cur.fetchall()]
                partner_id.sort()
                centers_all = Center.objects.filter(Q(delivery_partner_id__in=partner_id) | Q(funding_partner_id__in=partner_id)).filter(status='Active')
            else:
                centers_all = Center.objects.filter(Q(delivery_coordinator_id = request.user.id)|Q(field_coordinator_id=request.user.id)|Q(admin_id=request.user.id)|Q(assistant_id=request.user.id)).filter(status='Active')
        try:
             centers_all = centers_all.filter(status='Active')
        except:
            centers_all = None
    else:
        centers_all = Center.objects.filter(status='Active')
    dict_cur.close()
    db.close()
    return centers_all.filter(is_test=False) if centers_all else centers_all


@login_required
def stats(request):
    return multi_stat(request)
    time_start = request.GET.get("from_time"," ")
    time_end = request.GET.get("to_time"," ")
    if len(time_end)==1 and len(time_end)==1:
        print "fff"
        time_start = '07:00' 
        time_end =  '21:00'
    print "sssssss",len(time_end),len(time_end),time_start ,time_end
    profile = UserProfile.objects.get(user=request.user)
    is_partner=False
    is_school_admin = False
    partner = None
    if profile:
        if len(profile.role.filter(name = "Partner Admin")) > 0 or len(profile.role.filter(name = "OUAdmin")):
            partner = Partner.objects.get(contactperson=request.user)
            is_partner=True
        elif len(profile.role.filter(name = "School Admin")) > 0:
            schooladmin = Partner.objects.get(contactperson=request.user)
            is_school_admin = True
        else :
            partner = None
    # center_id = int(request.GET.get("center_id", "-1"))
    center_id = request.GET.getlist("center_id",-1)

    try:
        if int(center_id[0]) == -1:
            center_id = -1
    except:
        pass
    if center_id != -1:
        center_id_list =[]
        for center in center_id:
            center_id_list.append(int(center.encode("utf-8")))
        center_list = center_id_list
    else:
        center_list = -1
        center_id = -1
    partner_id = int(request.GET.get("partner_id", "-1"))
    funding_partner_id=int(request.GET.get("funding_partner_id", "-1"))
    # print 'funding_partner_id : ',funding_partner_id
    state = request.GET.get("state_id", "-1")
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    ay_id  = request.GET.get("ay_id")
    is_funding_partner = ""
    is_funding_partner= False
    if partner:
        try:
            is_funding_partner = Partner.objects.filter(contactperson=request.user,partnertype=3)
            if is_funding_partner:
                is_funding_partner= True
        except:
            is_funding_partner = ""
    else:
        is_funding_partner = ""
    global_data = {'center_name': 'ALL Centers', 'offerings_count': 0, 'total_sessions': 0, 'completed_sessions': 0,
                   'total_students': 0, 'attended_students': 0, 'from_date': from_date, 'to_date': to_date,"active":1,"is_funding_partner":is_funding_partner,"centername":"All Centers"}
    new_data = {'no_of_children': 0, 'planvsact': 0, 'offering_attendance': 0, 'center_attendance': 0,
                'child_attend': 0}
    all_centers = getAllCenters(request)
    # print "all_centersaaaaaaaaaaaaaa",all_centers
    ayfys = Ayfy.objects.filter(board__isnull = False).order_by('-title')
    ayfys_titles = ayfys.values_list('title', flat=True).distinct()
    # print all_centers, "all_centersaaaaaaaaaaaaaaa"
    all_states = ''
    if all_centers is not None and len(all_centers) > 0:
        all_states = all_centers.values_list('state', flat=True).distinct().order_by('state')
    if funding_partner_id != -1:
        all_states = all_centers.filter(funding_partner_id=funding_partner_id).values_list('state', flat=True).distinct().order_by('state')
    if all_states != '' and all_states[0] is None:
        all_states = all_states[1:]
    center_name = 'All Centers'
    partner_name = 'All Centers'
    fundingpartner_name='All Centers'
    if center_id != -1:
        center = Center.objects.values_list("name",flat=True).filter(id__in=center_id)
        center_name = center
    if partner_id != -1:
        center = Center.objects.filter(delivery_coordinator=partner_id)
        if center:
            partner_name = center[0].delivery_coordinator.name
    if funding_partner_id != -1:
        center = Center.objects.filter(funding_partner_id=funding_partner_id)
        if center:
            fundingpartner_name = center[0].funding_partner.name_of_organization
    is_partner_account_manager= False
    if has_role(request.user.userprofile, "Partner Account Manager"):
        is_partner_account_manager=True
    if all_centers != None:
        if center_name != "All Centers" and len(center_name) != 1:
            centername = "Multiple Centers"
        elif center_name != "All Centers" and len(center_name) == 1:
            centername = center_name[0]
        else:
            centername = center_name
        if center_name == "All Centers":
            center_seleceted = ""
        else:
            center_seleceted = center_id
        print("all states --------------------------- ",all_states)
        return render_response(request, 'statsv2.html',
                               {'center_id': center_list,'time_start':time_start,'time_end':time_end, 'center_name': center_name,'partner_id': partner_id, 'partner_name': partner_name, 'state_name': state,"is_partner_account_manager":is_partner_account_manager,"active":1,
                                'from_date': from_date, 'to_date': to_date, 'all_states': all_states,'ayfys_titles':ayfys_titles,'ay_id':ay_id,'partner':partner,'is_partner':is_partner,"is_funding_partner":is_funding_partner,'funding_partnerid':funding_partner_id,'fundingpartner_name':fundingpartner_name,'centername':centername,'center_seleceted':center_seleceted, 'is_school_admin':is_school_admin, 'is_dashboard':True})
    else:
        return render_response(request, 'statsv2.html', {'msg': 'There is no center for current user.', 'is_school_admin':is_school_admin, 'is_dashboard':True})


@login_required
def projectsummary(request):
    db = evd_getDB()

    if request.method == 'GET':
        summery = {'center_count': 0, 'teachers_count': 0, 'active_teachers_count': 0, 'offering_count': 0, 'toal_childrean_count' : 0, 'boys_count': 0 , "girls_count": 0}
        states_list = Center.objects.filter(funding_partner__contactperson=request.user, status='Active').distinct().values('state')
        centers_list = Center.objects.filter(funding_partner__contactperson=request.user, status='Active').distinct().values('name')

        ay_id = request.GET.get("ay_id", "")
        db = evd_getDB()
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)

        centers = []
        orgunit_partner_count = request.user.partner_set.filter(status='Approved', partnertype__id=4).count()
        delivery_parnter_count = Partner.objects.filter(contactperson=request.user, status='Approved',
                                                        partnertype__id=2).count()
        funding_parnter_count = Partner.objects.filter(contactperson=request.user, status='Approved',
                                                       partnertype__id=3).count()

        partner = request.user.partner_set.all()
        partner_count = partner.count()
        if partner:
            partner_types = partner[0].partnertype.values()
            for partnerty in partner_types:
                if partnerty['name'] == 'Organization Unit': is_orgUnit = True
                if partnerty['name'] == 'Funding Partner': is_funding_partner = True
            centers = Center.objects.filter(funding_partner__contactperson=request.user, status='Active').distinct().values('state').annotate(district=Count('district'), name=Count('name'))
            center_count = Center.objects.filter(Q(orgunit_partner__contactperson=request.user, status='Active') | Q(
                delivery_partner__contactperson=request.user, status='Active') | Q(
                funding_partner__contactperson=request.user, status='Active')).count()

            teachers_count = User.objects.filter(is_staff=True).count()
        else:
            centers = Center.objects.filter(funding_partner__contactperson=request.user, status='Active').distinct().values('state').annotate(
                district=Count('district'), name=Count('name'))
            center_count = Center.objects.all().count()
        for cen in centers:
            student_count =0
            languages =[]
            teacher_count = 0
            boys_count =0
            girls_count = 0
            boys_count_5=0
            boys_count_6=0
            boys_count_7=0
            boys_count_8=0
            girls_count_5=0
            girls_count_6=0
            girls_count_7=0
            girls_count_8=0
            if partner:
                partner_types = partner[0].partnertype.values()
                for partnerty in partner_types:
                    if partnerty['name'] == 'Organization Unit': is_orgUnit = True
                    if partnerty['name'] == 'Funding Partner': is_funding_partner = True
                cen_list = Center.objects.filter(Q(funding_partner__contactperson=request.user, status='Active', state=cen['state']))
                #print "cen_list",cen_list
            else:
                cen_list = Center.objects.filter(state=cen['state'])

            for c in cen_list:

                student_count += Student.objects.filter(center=c.id,status ='Active').count()
                boys_count += Student.objects.filter((Q(gender='Male') | Q(gender='Boy')), status='Active', center=c.id,grade__in=(5,6,7,8)).count()
                girls_count += Student.objects.filter((Q(gender='Female') | Q(gender='Girl')), status='Active', center=c.id,grade__in=(5,6,7,8)).count()
                boys_count_5 += Student.objects.filter((Q(gender='Male') | Q(gender='Boy')), status='Active', center=c.id,grade=5).count()
                boys_count_6 +=  Student.objects.filter((Q(gender='Male') | Q(gender='Boy')), status='Active', center=c.id,grade=6).count()
                boys_count_7 +=  Student.objects.filter((Q(gender='Male') | Q(gender='Boy')), status='Active', center=c.id,grade=7).count()
                boys_count_8 +=  Student.objects.filter((Q(gender='Male') | Q(gender='Boy')), status='Active', center=c.id,grade=8).count()
                girls_count_5 += Student.objects.filter((Q(gender='Female') | Q(gender='Girl')), status='Active', center=c.id,grade=5).count()
                girls_count_6 += Student.objects.filter((Q(gender='Female') | Q(gender='Girl')), status='Active', center=c.id,grade=6).count()
                girls_count_7 += Student.objects.filter((Q(gender='Female') | Q(gender='Girl')), status='Active', center=c.id,grade=7).count()
                girls_count_8 += Student.objects.filter((Q(gender='Female') | Q(gender='Girl')), status='Active', center=c.id,grade=8).count()
                languages.append(Center.objects.get(pk=c.id).language)
                query = "select count(distinct(active_teacher_id)) as unique_teachers_count from web_offering wo  where " \
                        "wo.center_id = "+str(c.id)+" and wo.status='running'and (active_teacher_id is not null or active_teacher_id != '' )"
                dict_cur.execute(query)
                unique_teachers_count = dict_cur.fetchall()
                teacher_count += unique_teachers_count[0]['unique_teachers_count']
                summery['active_teachers_count'] += Offering.objects.filter(active_teacher__isnull=False,center = c.id,status='running').distinct().values(
                    'active_teacher').count()
                offering_count = Offering.objects.filter(center=c.id).distinct().values().count()
                summery['offering_count'] += offering_count
            cen['boys_count'] = boys_count
            cen['girls_count'] = girls_count
            cen['boys_count_5'] = boys_count_5
            cen['boys_count_6'] = boys_count_6
            cen['boys_count_7'] = boys_count_7
            cen['boys_count_8'] = boys_count_8
            cen['girls_count_5'] = girls_count_5
            cen['girls_count_6'] = girls_count_6
            cen['girls_count_7'] = girls_count_7
            cen['girls_count_8'] = girls_count_8
            cen['student_count'] =cen['boys_count'] +cen['girls_count']
            cen['languages'] = list(dict.fromkeys(languages))
            cen['teacher_count'] = teacher_count
            #print "student_count", student_count
            summery['boys_count'] += cen['boys_count']
            summery['girls_count'] += cen['girls_count']
            summery['teachers_count'] += cen['teacher_count']
        summery['center_count'] = center_count
        summery['toal_childrean_count']= summery['boys_count'] +summery['girls_count']
        ayfys = Ayfy.objects.filter(board__isnull=False).order_by('-title')
        ayfys_titles = ayfys.values_list('title', flat=True).distinct()
        try:
            partner = Partner.objects.get(contactperson=request.user)
            is_partner = True
        except:
            partner = ""
        is_funding_partner = ""
        if partner:
            try:
                is_funding_partner = Partner.objects.values("partnertype").filter(contactperson=request.user,partnertype=3)
            except:
                is_funding_partner = ""
        else:
            is_funding_partner = ""

        return render_response(request, 'projectsummery.html',
                                   {'centers': centers,"states_list": states_list, 'centers_list': centers_list,'summery': summery,
                                    'ayfys_titles':ayfys_titles,"active":1,"partner":partner,"is_partner":is_partner,"is_funding_partner":is_funding_partner})


def X(data):
    try:
        if isinstance(data, int):
            return data
        return ''.join([chr(ord(x)) for x in data]).decode('utf8').encode('utf8')
    except:
        try:
            return ''.join([chr(ord(x)) for x in data]).decode('cp1252').encode("utf-8")
        except:
            return data.encode('utf8')


def donor_update(request):
    save_user_activity(request, 'Viewed Page: My Contributions - Donor Update', 'Page Visit')
    return render_response(request, "donor_updates.html")


def donor_updates(request, q):
    #print q
    save_user_activity(request, 'Viewed Page: My Contributions - Donations', 'Page Visit')
    if int(q) == 1:
        return render_response(request, "donor_update.html")
    elif int(q) == 4:
        return render_response(request, "update_Q3_14_15.html")
    elif int(q) == 2:
        return render_response(request, "update_Q1_13_14.html")
    else:
        return render_response(request, "donor_updates.html")


def policies_terms_conditions(request):
    return render_response(request, 'pg_policies_new.html', {})


# filtering the teachers with subject, medium, role, week day, from date and to date in lookup
def get_teachers(request):
    profiles = UserProfile.objects.all()
    day = request.GET.get("day", "all")
    subject = request.GET.get("subject", "all")
    medium = request.GET.get("medium", "all")
    role = request.GET.get("role", "all")
    date_from = request.GET.get("from", "all")
    date_to = request.GET.get("to", "all")
    teacher_id = request.GET.get("teacher_id", None)
    profiles_set = set(profiles)
    profiles_by_day = profiles_set
    profiles_by_subject = profiles_set
    profiles_by_medium = profiles_set
    profiles_by_role = profiles_set
    profiles_by_from_date = profiles_set
    profiles_by_to_date = profiles_set

    if day != "all":
        day = day.capitalize()
        profiles_by_day = set(profiles.filter(pref_days__contains=day))
    if subject != "all":
        profiles_by_subject = set(profiles.filter(pref_subjects__contains=subject))
    if medium != "all":
        profiles_by_medium = set(profiles.filter(pref_medium__contains=medium))
    if role != "all":
        profiles_by_role = []
        for profile in profiles:
            if profile.pref_roles.filter(name=role):
                profiles_by_role.append(profile)
        profiles_by_role = set(profiles_by_role)
    if date_from != "all":
        from_date = datetime.datetime.strptime(date_from, "%d-%m-%Y")
        profiles_by_from_date = set(profiles.filter(from_date__lte=from_date, to_date__gte=from_date))
    if date_to != "all":
        to_date = datetime.datetime.strptime(date_to, "%d-%m-%Y")
        profiles_by_to_date = set(profiles.filter(from_date__lte=to_date, to_date__gte=to_date))

    profiles = set.intersection(profiles_by_day, profiles_by_subject, profiles_by_medium, profiles_by_role,
                                profiles_by_from_date, profiles_by_to_date)
    if not teacher_id == "None":
        profiles = UserProfile.objects.filter(user_id=teacher_id)
    teachers = []
    for profile in profiles:
        picture = "/static/images/user_small.png"
        if profile.picture:
            picture = profile.picture
        skype_id = ""
        if profile.skype_id:
            skype_id = profile.skype_id
        medium = ""
        if profile.pref_medium:
            medium = ",".join(profile.pref_medium.split(";"))

        pref_offerings = profile.pref_offerings.all()
        pref_courses = []
        for offering in pref_offerings:
            make_course(offering, pref_courses)
        tmp = []
        for course in pref_courses:
            tmp.append(course["course"])
        pref_courses = ", ".join(tmp)

        location = []
        if profile.city:
            location.append(profile.city)
        if profile.state:
            location.append(profile.state)
        if profile.country:
            location.append(profile.country)
        location = ', '.join(location)

        if profile.pref_roles:
            pref_role_name = ""
            pref_roles = profile.pref_roles.all()
            for pref_role in pref_roles:
                if pref_role == pref_roles[len(pref_roles) - 1]:
                    pref_role_name = pref_role_name + pref_role.name
                else:
                    pref_role_name = pref_role_name + pref_role.name + ", "

        is_centeradmin = False
        if request.user.is_authenticated():
            user1 = request.user
            user_profile = UserProfile.objects.filter(user=user1)[0]
            if user_profile.role.all():
                user_role = user_profile.role.all()[0]
                if "Center Admin" in user_role.name:
                    is_centeradmin = True

        try:
            if profile.user.first_name and profile.user.last_name:
                teacher_sessions = Session.objects.filter(teacher=profile.user)
                current_courses = []
                teacher_courses = ""
                if teacher_sessions:
                    for index, session in enumerate(teacher_sessions):
                        course = make_number_verb(
                            session.offering.course.grade) + " " + session.offering.course.subject + " " + session.offering.center.name
                        current_courses.append(course)
                    current_courses = set(current_courses)
                    for index, course in enumerate(current_courses):
                        if index == len(current_courses) - 1:
                            teacher_courses += course
                        else:
                            teacher_courses += course + ", "

                teacher = {
                    "id": profile.user.id,
                    "name": profile.user.first_name,
                    "location": location,
                    "from": make_date_time(profile.from_date)["date"],
                    "to": make_date_time(profile.to_date)["date"],
                    "email": profile.user.email,
                    "phone": profile.phone,
                    "medium": medium,
                    "role": pref_role_name,
                    "picture": picture,
                    "short_notes": profile.short_notes,
                    "status": profile.status,
                    "hrs_contributed": profile.hrs_contributed,
                    "remarks": profile.remarks,
                    "courses": pref_courses,
                    "current_courses": teacher_courses,
                    "is_centeradmin": is_centeradmin,
                    "skype_id": skype_id
                }
                teachers.append(teacher)
        except User.DoesNotExist:
            pass
    return HttpResponse(simplejson.dumps(teachers), mimetype="application/json")


def search(request):
    return render_response(request, 'lookup.html', {})


def create_student_attendance(student_id, absent_list, session):
    attendance = SessionAttendance()
    attendance.session = session
    student = Student.objects.get(id=student_id)
    attendance.student = student
    attendance.is_present = "yes"
    if student_id in absent_list:
        attendance.is_present = "no"
    return attendance


def submit_attendance(request):
    session_id = int(request.POST['session'])
    is_flm = int(request.POST.get('is_flm_session', 0))
    student = request.POST['student']
    attend = str(request.POST['attend'])
    
    if is_flm: is_flm = True
    else: is_flm = False

    session = Session.objects.get(id=session_id)
    session.is_flm = is_flm
    session.save()

    students = student.split(";")
    attends = attend.split(";")
    attendance = SessionAttendance.objects.filter(session__id=session_id)
    if len(attendance) != 0:
        for student_id in students:
            student_attendance = attendance.filter(student__id=student_id)
            if student_attendance:
                student_attendance = student_attendance[0]
                student_attendance.is_present = 'yes'
                if str(student_attendance.student.id) in attends:
                    student_attendance.is_present = 'no'
            else:
                student_attendance = create_student_attendance(student_id, attends, session)

            student_attendance.save()
        
    else:
        for student_id in students:
            if student_id:
                attendance = create_student_attendance(student_id, attends, session)
                attendance.save()

    return HttpResponse("success")


# assigning teacher to a offering from centeradmin dashboard,sends a request for acceptance or rejection to teacehr dashboard
def assign_offer(request):
    offer_id = request.POST.get('offering', '')
    user_id = int(request.POST['user'])
    center_id = request.POST['center_id']
    center_id = int(center_id)
    user1 = User.objects.get(id=user_id)
    offering = Offering.objects.get(pk=offer_id)
    offering1 = make_number_verb(offering.course.grade) + " " + offering.course.subject + " at " + offering.center.name
    startdate = offering.start_date
    enddate = offering.end_date

    stack = StackTeacher()
    stack.offering = offering
    stack.teacher = user1
    stack.status = "pending"
    stack.save()
    user1.userprofile.from_date = datetime.datetime.today()
    user1.userprofile.to_date = datetime.datetime.today() + datetime.timedelta(weeks=6)

    if offering.start_date and offering.start_date < user1.userprofile.from_date:
        user1.userprofile.from_date = offering.start_date
    if offering.end_date and offering.end_date > user1.userprofile.to_date:
        user1.userprofile.to_date = offering.end_date

    user1.userprofile.save()

    # notification.send([user1], '_offer_assigned', {'offer': offering1, 'start_date': startdate, 'end_date': enddate})
    site = request.get_host()
    _send_mail([user1], '_offer_assigned',
               {'offer': offering1, 'start_date': startdate, 'end_date': enddate, 'site': site})

    return HttpResponse('ok')


# takes the response of acceptance or rejection from teacher for the proposal of offering
def response(request):
    reply = request.GET['reply']
    offer_id = int(request.GET.get('offering', ''));
    user1 = request.user
    offering = Offering.objects.get(id=offer_id)
    center = offering.center
    center_admin = center.admin
    admin_q = Q(center=offering.center) | Q(is_superuser=True);
    admins = User.objects.filter(admin_q)
    offer_title = make_number_verb(
        offering.course.grade) + " grade " + offering.course.board_name + " board " + offering.course.subject

    if reply == 'accept':
        sessions = offering.session_set.all()
        teacher = user1
        teacher_offering = teacher.userprofile.pref_offerings.filter(id=offer_id)
        '''
        if teacher_offering:
            for offers in teacher_offering:
                teacher.userprofile.pref_offerings.remove(offers)
        '''
        stack = StackTeacher.objects.filter(offering=offering, teacher=teacher)[0]
        stack.status = "accepted"
        stack.save()
        _send_mail(admins, '_offer_accepted', {'offer_title': offer_title, 'user': user1, "offer": offering})

    if reply == 'reject':
        teacher = user1
        teacher_profile = UserProfile.objects.filter(user=teacher)[0]
        teacher_offering = teacher_profile.pref_offerings.filter(id=offer_id)
        '''
        if teacher_offering:
            for offers in teacher_offering:
                teacher_profile.pref_offerings.remove(offers)
        '''
        stack = StackTeacher.objects.filter(offering=offering, teacher=teacher)[0]
        stack.status = "rejected"
        stack.save()
        _send_mail(admins, '_offer_rejected', {'offer_title': offer_title, 'offer': offering, 'user': user1})

    return HttpResponse("success")


# creates offering from centeradmin dashboard
def create_offering(request):
    center_id = request.POST.get('center', '')
    center = Center.objects.filter(id=center_id)[0]
    courses = Course.objects.all()
    topics = Topic.objects.all()
    students = Student.objects.filter(center=center)
    return render_response(request, 'create_offering.html',
                           {'center': center, 'courses': courses, 'topics': topics, 'students': students})


def remove_admin(user, center, remove_role):
    center.admin = None

    # if flag is passed to remove the role as centeradmin
    if remove_role:
        role = Role.objects.filter(name='Center Admin')[0]
        group = Group.objects.get(name="Center Admin")

        userp = user.userprofile
        userp.role.remove(role)

        # if not root
        if user != User.objects.get(pk=1):
            user.groups.remove(group)
            user.is_staff = False

    _send_mail([user], '_center_removed', {'center': center})


# assign center to particular user as centeradmin requested by admin from admin admindashboard
def assign_center(request):
    center_id = request.GET.get('center_id', '')
    flag = request.GET.get('flag', '')
    center_id = int(center_id)
    center = Center.objects.filter(id=center_id)[0]
    role = Role.objects.filter(name='Center Admin')[0]
    assistant_role = Role.objects.filter(name='Class Assistant')[0]
    group = Group.objects.get(name="Center Admin")
    user_post = request.GET.get('user_id', 'None')
    assistant_id = request.GET.get('assistant_id', 'None')
    fieldCoordinator_role = Role.objects.filter(name='Field co-ordinator')[0]
    fieldCoordinator_id = request.GET.get('fieldCoordinator_id', 'None')
    deliveryCoordinator_role = Role.objects.filter(name='Delivery co-ordinator')[0]
    deliveryCoordinator_id = request.GET.get('deliveryCoordinator_id', 'None')
    partner_id = request.GET.get('partner_id', 'None')
    orgpartner_id = request.GET.get('orgpartner_id', 'None')
    partner_role = Role.objects.filter(name='Partner Admin')[0]
    resp = ""
    # if a user is selected to assign to center
    if flag == "Admin" and user_post != "None" and user_post != "undefined" and (
            (center.admin and int(user_post) != center.admin.id) or not center.admin):
        user = User.objects.filter(id=int(user_post))[0]
        userp = UserProfile.objects.filter(user=user)[0]
        userp.role.add(role)
        user.groups.add(group)

        old_admin = center.admin

        if old_admin:
            old_admin_centers = old_admin.center_set.all().exclude(id=center.id)  # excluding the current center
            remove_role = True

            # if the old admin has more than one centers, donot remove his role as centeradmin
            if len(old_admin_centers) > 0: remove_role = False

            remove_admin(old_admin, center, remove_role)

        center.admin = user
        user.is_staff = True

        _send_mail([user], '_center_assigned', {'center': center})
        resp = 'added'
        userp.save()

        # if a user is not selected to assign to center(remove admin)
        user.save()
    elif flag == "Admin" and user_post == "None":
        user = center.admin
        remove_role = True
        if user:
            # if the admin has more than one centers, donot remove his role as centeradmin
            if len(user.center_set.all().exclude(id=center.id)) > 0:
                remove_role = False

            resp = "removed"
            remove_admin(user, center, remove_role)
    if flag == "Assistant" and assistant_id != "None" and assistant_id != "undefined" and (
            (center.assistant and int(assistant_id) != center.assistant.id) or not center.assistant):
        assistant_user = User.objects.filter(id=int(assistant_id))[0]
        assistant_profile = UserProfile.objects.filter(user=assistant_user)[0]
        assistant_profile.role.add(assistant_role)
        old_assistant = center.assistant
        if old_assistant:
            old_assistant_centers = old_assistant.assistant_center.all().exclude(id=center.id)
            if not len(old_assistant_centers) > 0:
                old_assistant.userprofile.role.remove(assistant_role)
                old_assistant.is_staff = False
                old_assistant.save()
        center.assistant = assistant_user
        assistant_user.is_staff = True
        if resp == "added":
            resp = "Both-added"
        elif resp == "removed":
            resp = "removed"
        elif resp == "":
            resp = "Assistant-added"
        assistant_user.save()

    elif flag == "Assistant" and assistant_id == "None":
        old_assistant = center.assistant
        if old_assistant:
            if len(old_assistant.assistant_center.all().exclude(id=center.id)) > 0:
                old_assistant.userprofile.role.remove(assistant_role)
                old_assistant.save()
        if resp == "added":
            resp = "added"
        elif resp == "removed":
            resp = "Both-removed"
        elif resp == "":
            resp = "Assistant-removed"
        center.assistant = None
    if flag == "FieldCoordinator" and fieldCoordinator_id != "None" and fieldCoordinator_id != "undefined" and ((
                                                                                                                        center.field_coordinator and int(
                                                                                                                    fieldCoordinator_id) != center.field_coordinator.id) or not center.field_coordinator):
        fieldCoord_user = User.objects.filter(id=int(fieldCoordinator_id))[0]
        fieldCoord_profile = UserProfile.objects.filter(user=fieldCoord_user)[0]
        fieldCoord_profile.role.add(fieldCoordinator_role)
        center.field_coordinator = fieldCoord_user
        fieldCoord_user.is_staff = True
        if resp == "added":
            resp = "Both-added"
        elif resp == "removed":
            resp = "removed"
        elif resp == "":
            resp = "FieldCoordinator-added"
        fieldCoord_user.save()

    elif flag == "FieldCoordinator" and fieldCoordinator_id == "None":
        if resp == "added":
            resp = "added"
        elif resp == "removed":
            resp = "Both-removed"
        elif resp == "":
            resp = "FieldCoordinator-removed"
        center.field_coordinator = None
    if flag == "DeliveryCoordinator" and deliveryCoordinator_id != "None" and deliveryCoordinator_id != "undefined" and (
            (center.delivery_coordinator and int(
                    deliveryCoordinator_id) != center.delivery_coordinator.id) or not center.delivery_coordinator):
        deliveryCoord_user = User.objects.filter(id=int(deliveryCoordinator_id))[0]
        deliveryCoord_profile = UserProfile.objects.filter(user=deliveryCoord_user)[0]
        deliveryCoord_profile.role.add(deliveryCoordinator_role)
        center.delivery_coordinator = deliveryCoord_user
        if center.digital_school:
            role = Role.objects.get(id=18)
            digital_center_staff = get_object_or_none(DigitalCenterStaff, center=center, role=role)
            if digital_center_staff: 
                digital_center_staff.user=deliveryCoord_user
                digital_center_staff.save()
            else: DigitalCenterStaff.objects.create(user=deliveryCoord_user, center=center, digital_school=center.digital_school, role=role, status='Active', created_by=request.user)
            
        deliveryCoord_user.is_staff = True
        if resp == "added":
            resp = "Both-added"
        elif resp == "removed":
            resp = "removed"
        elif resp == "":
            resp = "DeliveryCoordinator-added"
        deliveryCoord_user.save()
    elif flag == "DeliveryCoordinator" and deliveryCoordinator_id == "None":
        print('deliveryCoordinator_id:', deliveryCoordinator_id)
        if resp == "added":
            resp = "added"
        elif resp == "removed":
            resp = "Both-removed"
        elif resp == "":
            resp = "DeliveryCoordinator-removed"
        center.delivery_coordinator = None
        if center.digital_school:
            role = Role.objects.get(id=18)
            digital_center_staff = get_object_or_none(DigitalCenterStaff, center=center, role=role)
            if digital_center_staff: digital_center_staff.delete()
            
    if flag == "Partner" and partner_id != "None" and partner_id != "undefined" and (
            (center.funding_partner and int(partner_id) != center.funding_partner.id) or not center.funding_partner):
        partner_user = Partner.objects.filter(id=int(partner_id))[0]
        center.funding_partner = partner_user
        if resp == "added":
            resp = "Both-added"
        elif resp == "removed":
            resp = "removed"
        elif resp == "":
            resp = "PartnerAdmin-added"
        partner_user.save()
    elif flag == "Partner" and partner_id == "None":
        if resp == "added":
            resp = "added"
        elif resp == "removed":
            resp = "Both-removed"
        elif resp == "":
            resp = "Partner-removed"
        center.funding_partner = None
    if flag == "OrgPartner" and orgpartner_id != "None" and orgpartner_id != "undefined" and (
            (center.orgunit_partner and int(orgpartner_id) != center.orgunit_partner.id) or not center.orgunit_partner):
        partner_user = Partner.objects.filter(id=int(orgpartner_id))[0]
        center.orgunit_partner = partner_user
        if resp == "added":
            resp = "Both-added"
        elif resp == "removed":
            resp = "removed"
        elif resp == "":
            resp = "orgPartnerAdmin-added"
        partner_user.save()
    elif orgpartner_id == "None" and flag == "OrgPartner":
        if resp == "added":
            resp = "added"
        elif resp == "removed":
            resp = "Both-removed"
        elif resp == "":
            resp = "orgPartner-removed"
        center.orgunit_partner = None
    center.save()
    return HttpResponse(resp)


# view gets called when user says save offering from create_offering.html
def save_offering(request):
    topic_ids = request.GET.get("topic_ids", None)
    status = request.GET.get("status", "scheduled")
    comment = request.GET.get("comment", "")
    session_id = int(request.GET.get("session_id", None))
    reason = request.GET.get("reason", "")
    sub_topic = request.GET.get("sub_topic", "")
    is_lesson_plan = request.GET.get("lesson_plan", "")
    session = Session.objects.get(id=session_id)
    offering_id = session.offering_id
    active_teacher_id = Offering.objects.get(id=offering_id).active_teacher_id
    #offering = session.offering
    if sub_topic:
        subTopics = SubTopics.objects.filter(id=sub_topic)
        if len(sub_topic)>0:
            session.sub_topic = subTopics[0]
    if is_lesson_plan:
        session.used_lesson_plan = is_lesson_plan
    session.comments = comment
    session.status = status
    session.cancel_reason = reason
    session.actual_topics.clear()


    topic_names = []
    if topic_ids:
        topic_ids = topic_ids.split(";")
        for topic in topic_ids:
            curr_topic = Topic.objects.get(id=int(topic))
            topic_names.append(curr_topic.title)
            #session.planned_topics.add(curr_topic)
            session.actual_topics.add(curr_topic)
            #offering.planned_topics.add(curr_topic)
    #offering.save()
    session.save()
    if active_teacher_id is None:
        offering_obj = Offering.objects.get(id=offering_id)
        offering_obj.active_teacher_id = None
        offering_obj.save()

    if status == 'Completed' and request.user.userprofile.fbatwork_id:
        center_name = session.offering.center.name
        sub_name = session.offering.course.subject
        mem_data = {}
        mem_data['member_id'] = request.user.userprofile.fbatwork_id
        mem_data['member_token'] = request.user.userprofile.fb_member_token
        mem_data = json.dumps(mem_data)
        message = "Today i have complete %s class in %s " % (sub_name, center_name)
        sub = ''
        userid = request.user.id
        # insert_into_alerts(sub, message, mem_data, userid, "workplace")

    return HttpResponse("success")


def vision(request):
    return render_response(request, 'vision.html', {})


def operating_principles(request):
    return render_response(request, 'operating_principles.html', {})


def contact_us(request):
    return render_response(request, 'contact_us.html', {})


def partners(request):
    return render_response(request, 'partners.html', {})


def about_us(request):
    return render_response(request, 'new_about_us_temp.html', {})


def learn_more(request):
    return render_response(request, 'new_learn_more_temp.html', {})


def who_we_are(request):
    return render_response(request, 'who_we_are.html', {})


def privacypolociesandtc(request):
    return render_response(request, 'privacypolociesandtc.html', {})


def under_construction(request):
    return render_response(request, 'temp_page.html', {})


def newsletter(request):
    return render_response(request, 'newsletter.html', {})


def test_page(request):
    return render_response(request, 'new_volunteer_temp.html', {})


@csrf_exempt
def donation_response(request):
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

    return render_response(request, "donation_response.html", {})


@csrf_exempt
def donation_online_response(request):
    '''
    only for Tes setup of payment gateway
    '''

    message = request.POST.get("msg")

    if message:
        donation_id = message.split("|")[1]

        donation = Donation.objects.filter(id=donation_id)

        if donation:
            donation = donation[0]
            donation.online_resp_msg = message
            donation.online_txn_status = 'completed'
            donation.save()

    return render_response(request, "donation_response.html")


@login_required
def my_contributions(request):
    donations = Donation.objects.filter(user=request.user).order_by("donation_time").reverse()
    save_user_activity(request, 'Viewed Page: My Contributions - Donations', 'Page Visit')
    return render_response(request, "my_contributions.html", {"donations": donations})


def donations(request):
    is_loggedin, user_details = False, {}
    if request.user.id:
        is_loggedin = True
        user_details = UserProfile.objects.filter(user=request.user.id)[0]

    now = datetime.datetime.now()

    present_month = now.month
    present_year = now.year
    march = 3
    april = 4

    year_start = present_year
    year_end = present_year

    if present_month <= march:
        year_start = present_year - 1
    elif present_month >= april:
        year_end = present_year + 1

    start_date = datetime.datetime(day=1, month=april, year=year_start)
    end_date = datetime.datetime(day=31, month=march, year=year_end)

    child_edu_donations = Donation.objects.filter(donation_type="Sponsor a Child Education", \
                                                  donation_time__gte=start_date, \
                                                  donation_time__lte=end_date)

    # monthly_class_donations = Donation.objects.filter(donation_type = "Sponsor Monthly Class Operations")
    # furniture_donations = Donation.objects.filter(donation_type = "Sponsor Classroom FUrniture")

    digital_class_donations = Donation.objects.filter(donation_type="Adopt Digital Classroom", \
                                                      donation_time__gte=start_date, \
                                                      donation_time__lte=end_date)

    full_center_donations = Donation.objects.filter(donation_type="Sponsor a Full Center", \
                                                    donation_time__gte=start_date, \
                                                    donation_time__lte=end_date)

    child_edu_pledges = 0
    for donation in child_edu_donations:
        if donation.num_subjects and donation.num_students:
            child_edu_pledges = child_edu_pledges + (int(donation.num_students))

    digital_class_pledges = 0
    for donation in digital_class_donations:
        if donation.num_classrooms:
            digital_class_pledges = digital_class_pledges + int(donation.num_classrooms)

    full_center_pledges = 0
    for donation in full_center_donations:
        if donation.num_centers:
            full_center_pledges = full_center_pledges + int(donation.num_centers)

    centers = Center.objects.all()
    return render_response(request, 'donations_new_temp_3.html', {"child_edu": child_edu_pledges, \
                                                                "digital_class": digital_class_pledges, \
                                                                "full_center": full_center_pledges, \
                                                                "centers": centers, \
                                                                'user_details': user_details, \
                                                                'is_loggedin': is_loggedin})

def faq(request):
    
    if request.method == 'POST':
        # import pdb;pdb.set_trace()
        common_words= ('a','in','to','the','of','and','for','by','on','is','i','all','this','with','it','at',
                        'from','or','you','as','your','an','are','be','that','do','not','have','one','can','was',
                        'if','we','but','what','which','there','when','use','their','they','how','he','were','his',
                        'had','each','said','she','word','evidyaloka')

        question = str(request.POST.get('text', None))
        input_keys = question.lower().split()
        keys1 = set(input_keys) - set(common_words)
        keywords = Faq.objects.filter(status=True, language__name='English' ).values_list('id','question')
        ids = [int(x[0]) for x in keywords if set(str((x[1]).encode('ascii', 'ignore')).lower().split()).intersection(keys1)]
 
        data1  =[]
        dd = Faq.objects.filter(pk__in=ids)

        for d in dd:
            ff = {}
            ff['title'] = d.question
            ff['answer'] = d.answer
            data1.append(ff)

        data = {'answers':data1}
        
        return HttpResponse(simplejson.dumps(data), content_type='application/json')
    
    if 'lan' in request.GET:
        language = request.GET['lan']
    else:
        language = 'en'
    if 'user' in request.GET:
        user = request.GET['user']
    else:
        user = False
    question = Faq.objects.all().order_by('category')
    return render_response(request, 'faq2.html', {'user1':user, 'questions_list':question, 'language':language })

def faq_answer(request, id):
    if 'lan' in request.GET:
        language = request.GET['lan']
    else:
        language = 'en'
    if 'user' in request.GET:
        user = request.GET['user']
    else:
        user = False

    q = Faq.objects.filter(id = id)[0]
    if q:
        q = q
    else:
        return HttpResponse('<h1>Post Not Found</h1>')
    question = Faq.objects.all()
    return render_response(request, 'faq_answer.html', {'user1':user,'answer':q,'language':language, 'id':id, 'questions_list':question,})






def conduct(request):
    return render_response(request, 'conduct.html', {})


def code_conduct(request):
    return render_response(request, 'code_conduct.html', {})


def intro(request):
    return render_response(request, 'intro.html', {})


def aidsntools(request):
    save_user_activity(request, 'Viewed Page: My Tranings - Aids and Tools', 'Page Visit')
    return render_response(request, 'aidsntools.html', {})


def curriculumreview(request):
    save_user_activity(request, 'Viewed Page: My Tranings - Curriculum', 'Page Visit')
    return render_response(request, 'curriculumreview.html', {})


def mybook(request):
    return render_response(request, 'mybook.html', {})


def selfpaced(request):
    return render_response(request, 'selfpaced.html', {})


def skype(request):
    return render_response(request, 'skype.html', {})


# def error_500(request):
#    return render_response(request, '500error.html', {})
# def error_404(request):
#    return render_response(request, '404error.html', {})
def centeradmin_temp(request):
    user = request.user
    is_teacher = False
    is_assistant = False
    if has_role(user.userprofile, "Teacher") or has_pref_role(user.userprofile, "Teacher"): is_teacher = True
    if has_role(user.userprofile, "Class Assistant") or has_pref_role(user.userprofile,
                                                                      "Class Assistant"): is_assistant = True

    return render_response(request, 'centeradmin_temp.html', {"is_teacher": is_teacher, 'is_assistant': is_assistant})

def register_dummy_method(request):
    print "**** Account Registration Attempt ***** (DUMMY NOW)\n\n{}\n\n".format(request)
    return HttpResponse(simplejson.dumps({'status': '1'}), mimetype='application/json')

def well_wisher(request):
    user = request.user
    is_teacher = False
    if has_role(user.userprofile, "Teacher") or has_pref_role(user.userprofile, "Teacher"):
        is_teacher = True

    return render_response(request, 'well_wisher.html', {"is_teacher": is_teacher})


def donor(request):
    user = request.user
    is_donor = True
    is_teacher = False

    return render_response(request, 'well_wisher.html', {"is_teacher": is_teacher, "is_donor": is_donor})


def content_developer(request):
    user = request.user
    is_teacher = False
    if has_role(user.userprofile, "Teacher") or has_pref_role(user.userprofile, "Teacher"):
        is_teacher = True

    return render_response(request, 'content_developer.html', {"is_teacher": is_teacher})


'''def fund_raiser(request):
    user = request.user
    is_teacher = False
    if has_role(user.userprofile, "Teacher") or has_pref_role(user.userprofile, "Teacher"):
        is_teacher = True

    return render_response(request, 'fund_raiser.html', {})

def it_developer(request):
    return render_response(request, 'it_developer.html', {})
'''


def error_404(request):
    t = loader.get_template('404error.html')
    context = RequestContext(request, {})
    context['ref_path'] = '/'
    return http.HttpResponseServerError(t.render(context))


def schools(request):
    cur_location = request.GET.get('location', "all")
    cur_subject = request.GET.get('subject', "all")
    cur_medium = request.GET.get('medium', 'all')
    cur_center_id = request.GET.get('center_id', None)
    cur_center_status = request.GET.get('status', 'Active')
    centers = Center.objects.all()
    if cur_center_id:
        centers = Center.objects.filter(id=int(cur_center_id))
    states = []
    subjects = []
    for center in centers:
        states.append(center.state)
    states = list(set(states))
    states.sort()
    courses = Course.objects.all()
    for course in courses:
        subjects.append(course.subject)
    subjects = list(set(subjects))
    subjects.sort()
    medium = ["Bengali", "Gujarathi", "Hindi", "Kannada", "Malayalam", "Marathi", "Oriya", "Punjabi", "Tamil", "Telugu",
              "Urdu"]
    status = ["Planned", "Active", "Inactive", "Closed"]
    is_teacher = True
    if request.user.is_authenticated():
        is_authenticated = True
        is_teacher = has_pref_role(request.user.userprofile, "Teacher")
    else:
        is_authenticated = False

    return render_response(request, 'centers.html',
                           {'centers': centers, 'states': states, 'subjects': subjects, 'medium': medium,
                            'cur_medium': cur_medium, 'cur_location': cur_location, 'cur_subject': cur_subject,
                            'is_authenticated': is_authenticated, "is_teacher": is_teacher,
                            "cur_center_id": cur_center_id, "cur_center_status": cur_center_status, 'status': status})


def make_course(offering, courses, user=None):
    sessions = offering.session_set.all()
    teachers = []
    is_assigned_offering = False
    session_id = None

    for session in sessions:
        if session.teacher:
            teachers.append(session.teacher.first_name)
        session_id = session.id
    # look wether the given offering is in user pref_offerings
    if user:
        try:
            user.userprofile.pref_offerings.get(id=offering.id)
            is_assigned_offering = True
        except Offering.DoesNotExist:
            is_assigned_offering = False

    if len(teachers) > 0:
        teachers = teachers[0]
    else:
        teachers = None

    start_date_ts = int(time.mktime(offering.start_date.timetuple()) * 1000) if offering.start_date else ''
    end_date_ts = int(time.mktime(offering.end_date.timetuple()) * 1000) if offering.end_date else ''

    planned_topics_arr = []
    planned_topics = offering.planned_topics.all()
    if planned_topics:
        for topic in planned_topics:
            planned_topics_arr.append(topic.title)

    courses.append({"course": make_number_verb(
        offering.course.grade) + " grade " + offering.course.board_name + " board " + offering.course.subject,
                    "teachers": teachers, "start_date": make_date_time(offering.start_date)["date"],
                    "end_date": make_date_time(offering.end_date)["date"], "start_date_ts": start_date_ts,
                    "end_date_ts": end_date_ts, "offering_id": offering.id, "batch":offering.batch,
                    "is_assigned_offering": is_assigned_offering, "session_id": session_id,
                    "subject": offering.course.subject, "center": offering.center.name, "language": offering.language,
                    "course_offered": make_number_verb(offering.course.grade) + " " + offering.course.subject,
                    "planned_topics": planned_topics_arr, "center_language": offering.center.language,
                    "grade": make_number_verb(offering.course.grade), "program":offering.program_type})


def make_course_centeradmin(offering, courses, user=None):
    sessions = Session.objects.filter(offering=offering)
    teachers = []
    is_assigned_offering = False
    session_id = None
    teachers_id = None
    if len(sessions)>0:
        for session in sessions:
            if session.teacher:
                teachers.append(session.teacher.first_name)
                teachers_id = session.teacher_id
            session_id = session.id
        
    # look wether the given offering is in user pref_offerings
    if user:
        try:
            user.userprofile.pref_offerings.get(id=offering.id)
            is_assigned_offering = True
        except Offering.DoesNotExist:
            is_assigned_offering = False

    if len(teachers) > 0:
        teachers = teachers[0]
    else:
        teachers = None

    start_date_ts = int(time.mktime(offering.start_date.timetuple()) * 1000) if offering.start_date else ''
    end_date_ts = int(time.mktime(offering.end_date.timetuple()) * 1000) if offering.end_date else ''

    planned_topics_arr = []
    planned_topics = offering.planned_topics.all()
    if planned_topics:
        for topic in planned_topics:
            planned_topics_arr.append(topic.title)

    courses.append({"course": make_number_verb(
        offering.course.grade) + " grade " + offering.course.board_name + " board " + offering.course.subject, \
                    "teachers": teachers, "teachers_id": teachers_id,
                    "start_date": make_date_time(offering.start_date)["date"] + ", " +
                                  make_date_time(offering.start_date)["year"], \
                    "end_date": make_date_time(offering.end_date)["date"] + ", " + make_date_time(offering.end_date)[
                        "year"], "start_date_orig": offering.start_date, \
                    'end_date_orig': offering.end_date, "start_date_ts": start_date_ts, "end_date_ts": end_date_ts,
                    "offering_id": offering.id, "batch":offering.batch, \
                    "is_assigned_offering": is_assigned_offering, "session_id": session_id,
                    "subject": offering.course.subject, "center": offering.center.name, \
                    "language": offering.language,
                    "course_offered": make_number_verb(offering.course.grade) + " " + offering.course.subject, \
                    "planned_topics": planned_topics_arr, "center_language": offering.center.language,
                    "grade": make_number_verb(offering.course.grade), "program":offering.program_type})


def get_ongoing_courses(center, user=None):
    assigned_courses = []
    empty_courses = []
    other_lang_courses = []
    # empty_offerings = center.offering_set.filter(session__teacher=None)
    empty_offerings = center.offering_set.filter(status="pending")
    # offerings = center.offering_set.exclude(session__teacher=None)
    offerings = center.offering_set.filter(status="running")
    other_lang_offerings = None

    if user:
        other_lang_offerings = empty_offerings.exclude(language=user.userprofile.pref_medium)
        empty_offerings = empty_offerings.filter(language=user.userprofile.pref_medium)

        for offering in other_lang_offerings:
            make_course(offering, other_lang_courses, user)

    for offering in empty_offerings:
        make_course(offering, empty_courses, user)

    for offering in offerings:
        make_course(offering, assigned_courses, user)

    return empty_courses, assigned_courses, other_lang_courses


def getcenters(request):
    location = request.GET.get('location', None)
    subject = request.GET.get('subject', None)
    medium = request.GET.get('medium', None)
    center_id = request.GET.get('center_id', None)
    status = request.GET.get('status', None)
    centers_data = []
    centers = get_centers(location, subject, medium, status, center_id)
    centers = sorted(centers, key=lambda x: x.name)
    counts = []
    centre_names = []

    user = None
    if request.user and request.user.is_authenticated():
        user = request.user

    for center in centers:
        empty_courses, assigned_courses, other_lang_courses = get_ongoing_courses(center, user)
        counts.append(len(empty_courses))
        center_image = "http://placehold.it/133x133/F15A22/fff/&text=" + center.name
        length = len(empty_courses) + len(other_lang_courses)
        if center.photo:
            if crop(center.photo, "250x250"):
                center_image = "/" + crop(center.photo, "250x250")
        if center.ops_donor_name:
            ops_donor = center.ops_donor_name
        else:
            ops_donor = '<a href="/donors/" class="donors-list" style="color:#505050;">Donors</a>'
        centers_data.append({"title": center.name, "description": center.description, "image": center_image,
                             "empty_courses": empty_courses, "assigned_courses": assigned_courses,
                             "other_lang_courses": other_lang_courses, "grades": center.grades,
                             "subjects_covered": center.subjectscovered, "location": center.classlocation,
                             "noofchildren": center.noofchildren, "launch_date": center.launchdate,
                             "ops_donor": ops_donor, "donor": center.donor_name, "length": length})

    counts.sort()
    counts.reverse()
    '''
    _centres_data = []
    for count in counts:
        for centre in centers_data:
            if count == len(centre['empty_courses']):
                if centre['title'] not in centre_names:
                    _centres_data.append(centre)
                    centers_data.remove(centre)

    _centres_data.sort(key=operator.itemgetter("length"))
    _centres_data.reverse()
    centers_data = _centres_data
    '''

    return HttpResponse(simplejson.dumps(centers_data), mimetype='application/JSON')


def add_pref_course(request):
    user = request.user
    if user and user.is_authenticated():
        if has_pref_role(user.userprofile, "Teacher"):
            user_profile = UserProfile.objects.filter(user=user)[0]
            existing_pref_courses = ''
            course_id = request.GET.get("course_id", None)
            if course_id:
                course_id = int(course_id)
                new_pref_course = Offering.objects.get(id=course_id)
                user_profile.pref_offerings.add(new_pref_course)
                user_profile.save()
                admin_q = Q(center=new_pref_course.center) | Q(is_superuser=True, email__icontains='@evidyaloka.org');
                # notification.send(centre_admin, '_center_offer',{'offer':new_pref_course, 'user':request.user})
                admins = User.objects.filter(admin_q)

                new_pref_course_title = make_number_verb(
                    new_pref_course.course.grade) + " grade " + new_pref_course.course.board_name + " board " + new_pref_course.course.subject
                _send_mail(admins, '_center_offer',
                           {'offer': new_pref_course_title, 'user': user, "center": new_pref_course.center.name})
            return HttpResponse("success", mimetype="text/html")

        else:
            return HttpResponse("not_teacher", mimetype="text/plain")

    else:
        return HttpResponse("fail", mimetype="text/html")


@login_required
def test(request):
    user1 = request.user
    user_profile = UserProfile.objects.filter(user=user1)[0]
    user_pref_offerings = user_profile.pref_offerings.all()
    sessions = Session.objects.filter(teacher=user1)
    # for i in range(len(session)):
    #   assigned_offerings.append(session[i].offering)
    session_none = Session.objects.exclude(teacher=None)
    others_session = session_none.exclude(teacher=user1)
    offerings = Offering.objects.all()

    return render_response(request, 'test.html',
                           {"offerings": offerings, "sessions": sessions, "others_session": others_session})


def footerlinks(request):
    return render_response(request, 'footer_base.html', {})


# Update/Add New Session
def add_session(request):
    if request.method == "POST":
        offering_id = request.POST['offering_id']
        session_id = request.POST.get('session_id', 0)
        teacher_id = request.POST['teacher_id']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        act_topics = request.POST.getlist('actual_topics')
        plan_topics = request.POST.getlist('planned_topics')

        actual_topics = [Topic.objects.get(pk=int(t)) for t in act_topics]
        planned_topics = [Topic.objects.get(pk=int(t)) for t in plan_topics]
        start_date_dt = datetime.datetime.strptime(start_date.strip(), "%Y-%m-%dT%H:%M:%S")
        end_date_dt = datetime.datetime.strptime(end_date.strip(), "%Y-%m-%dT%H:%M:%S")
        try:
            offering_obj = Offering.objects.get(pk=offering_id)
            teacher_obj = User.objects.get(pk=teacher_id)
            if session_id:
                session_id = int(session_id)
                session_update = Session.objects.get(pk=session_id)
                session_update.offering = offering_obj
                session_update.teacher = teacher_obj
                session_update.planned_topics = planned_topics
                session_update.actual_topics = actual_topics
                session_update.date_start = start_date_dt
                session_update.date_end = end_date_dt
                session_update.save()
                return HttpResponse(session_id)
            else:
                session = Session.objects.create(offering=offering_obj, teacher=teacher_obj,
                                                 date_start=start_date_dt, date_end=end_date_dt)
                session.planned_topics.add(*planned_topics)
                session.actual_topics.add(*actual_topics)
                session.save()
                return HttpResponse(session.pk)
        except:
            tr = traceback.format_exc()
            return HttpResponse("Failed")
    else:  # GET
        return HttpResponse('Only POST accepted')


# to eset password
def password_reset(request):
    if request.method == "POST":

        # email = self.cleaned_data["email"]
        email = request.POST['email']
        user = User.objects.filter(email__iexact=email, is_active=True)
        if not user:
            data = [{"status": "error", "message": "Email id provided does not match database"}]
            return HttpResponse(content=simplejson.dumps(data), mimetype="application/json")

        else:
            token_generator = default_token_generator
            site_name = 'evd.cloudlibs.com'
            email_id = user[0].email
            site_name = site_name
            uid = int_to_base36(user[0].id)
            user = user
            token = token_generator.make_token(user[0])
            # protocol = use_https and 'https' or 'http'
            # send_mail(_("Password reset on %s") % site_name
            # notification.send(user, '_password_reset', {'user':user, 'email_id':email_id,'token':token,'uid':uid })
            site = request.get_host()
            site += '/v2/reset_password/?uid=' + uid + '&token=' + token

            _send_mail(user, '_password_reset',
                       {'user': user[0], 'email_id': email_id, 'token': token, 'uid': uid, 'site': site},mail_receive_text='Reset_Password')

            from_email = settings.DEFAULT_FROM_EMAIL
            subject = "Password Reset for eVidyaloka account"
            body_template = 'mail/_password_reset/full.txt'
            args = {'user': user[0], 'email_id': email_id, 'token': token, 'uid': uid, 'site': site}
            body = get_mail_content(body_template, args)
            message = body
            if email_id:
                msg = EmailMessage(subject, message, to=[email_id], from_email=from_email)
                msg.send()
            data = [{"status": "success", "message": "The Change Password Confirmation is sent to your mail"}]
            return HttpResponse(content=simplejson.dumps(data), mimetype="application/json")

    return render_response(request, 'registration/_password_reset_form.html', {})


def upload_profilepic(request):
    if request.method == 'POST':
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')

        # getting file data for farther manipulations

        image = request.FILES[u'files[]']
        user = request.user
        try:
            user_profile = user.get_profile()
        except:
            user_profile = UserProfile(user=user)

        f_path = '/var/www/evd'
        f_name = '/static/profile_images/' + request.user.username + '_' + image.name + '.jpg'
        f = open(f_path + f_name, 'w+')
        f.write(image.read())
        f.close()

        image = PIL.open(f_path + f_name)
        image.thumbnail([150, 150], PIL.ANTIALIAS)
        image.save(f_path + f_name, image.format, quality=90)
        user_profile.picture = f_name
        user_profile.save()

        # cfile = ContentFile(image.read())
        # img = user.userprofile.picture = user.username+".jpg", cfile, save=True)

        # generating json response array
        result = []
        result.append({
            "url": user_profile.picture
        })
        response_data = simplejson.dumps(result)

        # checking for json data type
        # big thanks to Guy Shapiro
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, mimetype=mimetype)
    else:  # GET
        return HttpResponse('Only POST accepted')


def create_hangout_meetings(days, timings, start_date, end_date, offering_id, teacher_id):
    try:
        meeting_process = Process(target=meeting_creation_job, args=(days, timings, start_date, end_date, offering_id, teacher_id,))
        meeting_process.start()
        # meeting_thread = Thread(None, meeting_creation_job, "meeting_creation_job", (days, timings, start_date, end_date, offering_id, teacher_id))
        # meeting_thread.start()
        #thread.start_new_thread(meeting_creation_job, (days, timings, start_date, end_date, offering_id, teacher_id))
    except:
        log_error_messages("Process failed for hangout link creation")
    else:
        log_error_messages("Creating hangout link is done by another Process")


def add_dynamic_session(request):
    try:
        user_id = request.POST['user_id']
        user_id = user_id.split('::')[0]
        offering_id = request.POST['offering_id']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        software = request.POST['software']
        software_link = request.POST['softwareLink']

        # _pref_days = request.POST['prefered_days']
        # pref_slots = request.POST['prefered_timings']

        pref_days_list = request.POST['prefered_days'].split(";")
        pref_slots_list = request.POST['prefered_timings'].split(";")
        slots = {}
        n = 0
        for days in pref_days_list:
            slots[days] = pref_slots_list[n]
            n += 1

        days_ordered = ["Mon", "Tue", "Wed", "Thu", "Fri","Sat","Sun"]
        sorted_days = sorted(pref_days_list, key=days_ordered.index)
        sorted_time = []

        # for day in sorted_days:
        n=0
        for slot in sorted_days:
            sorted_time.append(pref_slots_list[n])
            n+= 1

        _pref_days = ''
        pref_slots = ''
        for day in sorted_days:
            _pref_days= _pref_days + day + ";"

        for time in sorted_time:
            pref_slots = pref_slots + time + ";"
        _pref_days = _pref_days[:-1]
        ajax = request.POST['ajax']
        session_arr = add_dynamic_session_accept(user_id, offering_id, start_date, end_date, software, software_link,
                                                _pref_days, pref_slots, ajax, request)

        offering = Offering.objects.get(pk=offering_id)
        teacher = User.objects.get(id=user_id)
        onboarding_alert(request, teacher, offering)

        if ajax == 'true':
            return HttpResponse(simplejson.dumps({"sessions": session_arr, 'offering_id': offering_id}),
                                mimetype='application/json')
        else:
            # if int(software) == 2 and software_link == "":
            #     create_hangout_meetings(_pref_days, pref_slots, start_date, end_date, offering_id, user_id)
            return render_response(request, 'dynamic_sessions_result.html', {"sessions": session_arr})
    except Exception as e:
        print("FT Exception", e)
        traceback.print_exc()


def add_dynamic_session_accept(user_id, offering_id, start_date, end_date, software, software_link, _pref_days, pref_slots, ajax, request):
    status = 'running'
    user = User.objects.get(pk=user_id)
    offering = Offering.objects.get(pk=offering_id)
    board = offering.center.board
    holiday_dates = get_holidays(board)
    if ajax == 'true':
        _pref_days = _pref_days.split(',')
        see_del = Session.objects.filter(offering = offering_id,teacher = None)
        see_del.delete()
    else:
        _pref_days = _pref_days.split(';')

    if ajax == 'true':
        pref_slots = pref_slots.split(',')
    else:
        pref_slots = pref_slots.split(';')
    '''
    removing session from teacher's preffered offerings as it is being assigned
    to him and no more required to be in the users(teacher here) preffered offerings list
    '''

    user.userprofile.pref_offerings.remove(offering)
    start_date = datetime.datetime.strptime(start_date.strip(), "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date.strip(), "%Y-%m-%d")
    days_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    pref_days = [days_mapping[day] for day in _pref_days]
    # print "after pref_days :",pref_days
    today_date = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30))
    if offering.start_date and offering.end_date:
        if ajax == 'true':
            sessions_count = (offering.end_date - today_date).days
            today_date = today_date.strftime("%Y-%m-%d")
            today_date = datetime.datetime.strptime(today_date.strip(), "%Y-%m-%d")
            if str(offering.start_date) >=str(today_date) :
                start_date = offering.start_date
            else:
                start_date = today_date
        else:
            sessions_count = (offering.end_date - offering.start_date).days

        sessions = []
        for session in range(sessions_count):
            if not session == 0:
                start_date = start_date + datetime.timedelta(days=1)
            # to handle the case where the current weekday has multiple sessions in same day
            day_indexes = [i for i, k in enumerate(pref_days) if k == start_date.weekday()]
            if start_date.weekday() not in pref_days:
                continue
            if holiday_dates:
                if start_date.date() in holiday_dates:
                    continue
            for day_index in day_indexes:
                timings = pref_slots[day_index].split('-')
                s_hours = timings[0].split(':')[0]
                s_mins = timings[0].split(':')[1]
                e_hours = timings[1].split(':')[0]
                e_mins = timings[1].split(':')[1]
                start_time = start_date + datetime.timedelta(hours=int(s_hours), minutes=int(s_mins))
                end_time = start_date + datetime.timedelta(hours=int(e_hours), minutes=int(e_mins))
                sessions.append({'start_time': start_time, 'end_time': end_time})

        topics = offering.planned_topics.all().order_by('priority')
        count = 0
        tsd = None
        if software:
            tsd = TeachingSoftwareDetails.objects.filter(id=software)[0]
        else:
            tsd = TeachingSoftwareDetails.objects.filter(id=2)[0]
        topic_count = 0
        for sess in range(count,len(sessions)):
            topic_sessions = 1
            topic = None
            if len(topics)>topic_count:
                topic = topics[topic_count]
                topic_sessions = topic.num_sessions or 1
                topic_count+=1
            for topic_session in range(topic_sessions):
                # creating sessions if gets index error will save up to that sessions
                try:
                    session = sessions[count]
                    count += 1
                    s = Session.objects.create(teacher=user, date_start=session['start_time'],
                                           date_end=session['end_time'], offering=offering, teachingSoftware=tsd,
                                               ts_link=software_link,dt_added = today_date,created_by = user)
                    if topic:
                        s.planned_topics.add(topic)
                    s.save()
                    
                except IndexError:
                    break
    else:
        startdate = datetime.datetime.today()
        enddate = datetime.datetime.today() + datetime.timedelta(weeks=6)
        s = Session.objects.create(teacher=user, date_start=startdate, date_end=enddate, offering=offering,dt_added = today_date,created_by = user)
        topics = offering.planned_topics.all()
        for topic in topics:
            s.planned_topics.add(topic)
        s.save()

    session_arr = []
    for session in Session.objects.filter(offering=offering).order_by('date_start'):
        session_arr.append(make_number_verb(session.offering.course.grade) + ' ' + session.offering.course.subject + ', ' + session.offering.center.name + ' - ' +
                           make_date_time(session.date_start)["date"] + ' ' + make_date_time(session.date_start)["time"])

    offering.status = status
    offering.save()
    return session_arr


def compute_demand(pending_sessions):
    demand_hours = 0

    unassigned_offerings = Offering.objects.filter(session__teacher=None)
    for offering in unassigned_offerings:
        num_weeks = ((offering.end_date - offering.start_date).days) / 7
        demand_hours += num_weeks * 2

    running_sessions = Session.objects.exclude(teacher=None)
    sessions_delivered_hours = 0
    for session in running_sessions:
        if session.date_end < datetime.datetime.now():
            duration = session.date_end.hour - session.date_start.hour
            sessions_delivered_hours = sessions_delivered_hours + duration
    demand = {
        "demand_hours": demand_hours,
        "sessions_delivered_hours": sessions_delivered_hours
    }
    return demand


def compute_supply(profiles):
    hours = 0
    for profile in profiles:
        from_date = profile.from_date
        to_date = profile.to_date
        num_days = ((profile.to_date - profile.from_date).days) / 7
        # num_pref_days = len(profile.pref_days.split(";"))
        for day in range(num_days):
            # for d in range(num_pref_days):
            hours = hours + 2
    volunteers = len(UserProfile.objects.exclude(user__first_name='', user__last_name=''))
    students = len(Student.objects.all())
    supply = {
        "supply_hours": hours,
        "volunteers": volunteers,
        "students": students
    }

    return supply


def save_center_timings(request):
    center_id = request.POST['center_id']
    working_days = request.POST['prefered_days']
    working_slots = request.POST['prefered_timings']
    center = Center.objects.get(id=center_id)
    center.working_days = working_days
    center.working_slots = working_slots
    center.save()

    return HttpResponse("success")


def save_students(request):
    student_ids = request.POST.get('student_ids', None).split(";")
    strengths = request.POST.get('strengths', None).split(";")
    weakness = request.POST.get('weakness', None).split(";")
    observation = request.POST.get('observation', None).split(";")

    for index, stu_id in enumerate(student_ids):
        student = Student.objects.get(id=stu_id)
        student.strengths = strengths[index]
        student.weakness = weakness[index]
        student.observation = observation[index]
        student.save()

    return HttpResponse("success")


def save_remarks(request):
    user_id = request.POST['user_id']
    user = UserProfile.objects.get(user_id=user_id)
    user.remarks = request.POST['remarks']
    user.status = request.POST['status']
    user.save()

    return HttpResponse("ok")


def get_user_emails(request):
    profiles = UserProfile.objects.all()
    day = request.GET.get("day", "all")
    subject = request.GET.get("subject", "all")
    medium = request.GET.get("medium", "all")
    role = request.GET.get("role", "all")
    date_from = request.GET.get("from", "all")
    date_to = request.GET.get("to", "all")
    teacher_id = request.GET.get("teacher_id", None)
    profiles_set = set(profiles)
    profiles_by_day = profiles_set
    profiles_by_subject = profiles_set
    profiles_by_medium = profiles_set
    profiles_by_role = profiles_set
    profiles_by_from_date = profiles_set
    profiles_by_to_date = profiles_set

    if day != "all":
        day = day.capitalize()
        profiles_by_day = set(profiles.filter(pref_days__contains=day))
    if subject != "all":
        profiles_by_subject = set(profiles.filter(pref_subjects__contains=subject))
    if medium != "all":
        profiles_by_medium = set(profiles.filter(pref_medium__contains=medium))
    if role != "all":
        profiles_by_role = []
        for profile in profiles:
            if profile.pref_roles.filter(name=role):
                profiles_by_role.append(profile)
        profiles_by_role = set(profiles_by_role)
    if date_from != "all":
        from_date = datetime.datetime.strptime(date_from, "%d-%m-%Y")
        profiles_by_from_date = set(profiles.filter(from_date__lte=from_date, to_date__gte=from_date))
    if date_to != "all":
        to_date = datetime.datetime.strptime(date_to, "%d-%m-%Y")
        profiles_by_to_date = set(profiles.filter(from_date__lte=to_date, to_date__gte=to_date))

    profiles = set.intersection(profiles_by_day, profiles_by_subject, profiles_by_medium, profiles_by_role,
                                profiles_by_from_date, profiles_by_to_date)
    if not teacher_id == "None":
        profiles = UserProfile.objects.filter(user_id=teacher_id)
    emails = ""
    # emails_list = []
    # users_data =  {}
    for index, profile in enumerate(profiles):
        try:
            if profile.user.email:
                # users_data.update({index:{'username':profile.user.username,'email':profile.user.email}})
                if index == len(profiles) - 1:
                    emails += profile.user.email
                else:
                    emails += profile.user.email + ";"
        except User.DoesNotExist:
            pass
    return HttpResponse(emails)
    # return HttpResponse(simplejson.dumps(users_data))


def send_email(request):
    emails = request.POST['user_emails'].split(";")
    emails_list = []
    for email in emails:
        emails_list.append(email.strip())
    subject = request.POST.get('subject', "")
    message = request.POST.get('message', "")
    send_mail(subject, message, "evlSystem@evidyaloka.org", emails_list)

    return HttpResponse("success")


# Download XSL File format
def create_xls_header_part(ws):
    style0 = xlwt.easyxf('font: name Times New Roman size 20, color-index black, bold on')
    headers_list = ['Name', 'Pref Roles', 'Medium', 'Location', 'Avail From', 'Avail To', 'Email', 'Phone',
                    'Short notes'
                    'Current Courses', 'Hours Contributed', 'Remarks', 'Status']

    for i, header in enumerate(headers_list):
        ws.write(0, i, header, style0)

    return ws


def write_testresults_to_xls(ws, result_objs):
    i = 1
    for k, result_obj in enumerate(result_objs):
        teacher = result_obj[0]
        name = teacher['name']
        role = teacher['role']
        xls_values_list = [teacher['name'], teacher['role'], teacher['medium'], teacher['location'], teacher['from'],
                           teacher['to'], teacher['email'], teacher['phone'],
                           teacher['short_notes'], teacher['current_courses'], teacher['hrs_contributed'],
                           teacher['remarks'], teacher['status']]

        for j, xls_value in enumerate(xls_values_list):
            ws.write(i, j, xls_value)

        i = i + 1

    return ws


@login_required
def download(request):
    result_objs = []

    if not request.user.is_staff:
        return HttpResponseRedirect('/myevidyaloka/')

    profiles = UserProfile.objects.all()
    day = request.GET.get("day", "all")
    subject = request.GET.get("subject", "all")
    medium = request.GET.get("medium", "all")
    role = request.GET.get("role", "all")
    date_from = request.GET.get("from", "all")
    date_to = request.GET.get("to", "all")
    teacher_id = request.GET.get("teacher_id", None)
    profiles_set = set(profiles)
    profiles_by_day = profiles_set
    profiles_by_subject = profiles_set
    profiles_by_medium = profiles_set
    profiles_by_role = profiles_set
    profiles_by_from_date = profiles_set
    profiles_by_to_date = profiles_set

    if day != "all":
        day = day.capitalize()
        profiles_by_day = set(profiles.filter(pref_days__contains=day))
    if subject != "all":
        profiles_by_subject = set(profiles.filter(pref_subjects__contains=subject))
    if medium != "all":
        profiles_by_medium = set(profiles.filter(pref_medium__contains=medium))
    if role != "all":
        profiles_by_role = []
        for profile in profiles:
            if profile.pref_roles.filter(name=role):
                profiles_by_role.append(profile)
        profiles_by_role = set(profiles_by_role)
    if date_from != "all":
        from_date = datetime.datetime.strptime(date_from, "%d-%m-%Y")
        profiles_by_from_date = set(profiles.filter(from_date__lte=from_date, to_date__gte=from_date))
    if date_to != "all":
        to_date = datetime.datetime.strptime(date_to, "%d-%m-%Y")
        profiles_by_to_date = set(profiles.filter(from_date__lte=to_date, to_date__gte=to_date))

    profiles = set.intersection(profiles_by_day, profiles_by_subject, profiles_by_medium, profiles_by_role,
                                profiles_by_from_date, profiles_by_to_date)
    if not teacher_id == "None":
        profiles = UserProfile.objects.filter(user_id=teacher_id)
    for profile in profiles:
        medium = ""
        if profile.pref_medium:
            medium = ",".join(profile.pref_medium.split(";"))

        pref_offerings = profile.pref_offerings.all()
        pref_courses = []
        for offering in pref_offerings:
            make_course(offering, pref_courses)
        tmp = []
        for course in pref_courses:
            tmp.append(course["course"])
        pref_courses = ", ".join(tmp)

        location = []
        if profile.city:
            location.append(profile.city)
        if profile.state:
            location.append(profile.state)
        if profile.country:
            location.append(profile.country)
        location = ', '.join(location)

        if profile.pref_roles:
            pref_role_name = ""
            pref_roles = profile.pref_roles.all()
            for pref_role in pref_roles:
                if pref_role == pref_roles[len(pref_roles) - 1]:
                    pref_role_name = pref_role_name + pref_role.name
                else:
                    pref_role_name = pref_role_name + pref_role.name + ", "

        try:
            if profile.user.first_name and profile.user.last_name:
                teacher_sessions = Session.objects.filter(teacher=profile.user)
                current_courses = []
                teacher_courses = ""
                if teacher_sessions:
                    for index, session in enumerate(teacher_sessions):
                        course = make_number_verb(
                            session.offering.course.grade) + " " + session.offering.course.subject + " " + session.offering.center.name
                        current_courses.append(course)
                    current_courses = set(current_courses)
                    for index, course in enumerate(current_courses):
                        if index == len(current_courses) - 1:
                            teacher_courses += course
                        else:
                            teacher_courses += course + ", "

                teacher = {
                    "id": profile.user.id,
                    "name": profile.user.first_name,
                    "location": location,
                    "from": make_date_time(profile.from_date)["date"],
                    "to": make_date_time(profile.to_date)["date"],
                    "email": profile.user.email,
                    "phone": profile.phone,
                    "medium": medium,
                    "role": pref_role_name,
                    "short_notes": profile.short_notes,
                    "status": profile.status,
                    "hrs_contributed": profile.hrs_contributed,
                    "remarks": profile.remarks,
                    "courses": pref_courses,
                    "current_courses": teacher_courses,
                }

                result_objs.append([teacher])
        except User.DoesNotExist:
            pass

    sheet_name = "teachers"
    wb = Workbook()

    ws = wb.add_sheet("first_sheet")
    ws = create_xls_header_part(ws)
    ws = write_testresults_to_xls(ws, result_objs)

    fname = '%s.xls' % sheet_name
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % fname

    wb.save(response)

    return response


'''
def donate(request):
    amount = request.POST.get("donation-amount", None)
    number = request.POST.get("number", 1)
    donation = request.POST.get("donation", "")
    donate_for = request.POST.get("donate_for", "")
    name = request.POST.get("name", "")
    #address = request.POST.get("address", "")
    contact_num = request.POST.get("contact_num", "")
    email = request.POST.get("email", "")
    #city = request.POST.get("city", "")
    state = request.POST.get("state", "")
    country = request.POST.get("country", "")

    if int(number) > 1 :
       donate_for += "s"

    admins = User.objects.filter(is_superuser = True)

    _send_mail(admins, '_donate', {'amount':amount, 'number':number, 'donate_for': donate_for, 'name': name, 'contact_num': contact_num, 'email': email, 'state': state, 'country': country, "donation": donation })

    return HttpResponse("success")
'''
'''
def payment_details(request):

    if request.method == 'GET':
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    print "POST", request.POST
    amount = int(request.POST.get('amount', "0"))
    donation_type = request.POST.get('donation_type', "")
    children = request.POST.get('children', "")
    #OMG!, number means number of classrooms
    number = request.POST.get("number", "")
    centres = request.POST.get("centres", "")
    num_subjects = request.POST.get("num_subjects", "")

    total_amount = amount

    if children:
        children = int(children)
        total_amount = total_amount * children
    elif number:
        number = int(number)
        total_amount = total_amount * number
    elif centres:
        centres = int(centres)
        total_amount = total_amount * centres

    print "donation type", donation_type
    print "children", children
    print "amount", total_amount

    return render_response(request, "donation_payment_details.html",\
                                         {"amount": total_amount,\
                                         "children": children,\
                                         "number": number,\
                                         "centres": centres,\
                                         "donation_type": donation_type,\
                                         "num_subjects": num_subjects})


@login_required
def update_pledge(request):

    post_data = request.POST

    donation_id = post_data.get("id")

    if not donation_id:
        return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}), mimetype="application/json", status=500)

    donation = Donation.objects.filter(id=donation_id, user=request.user)

    if not donation:
         return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}), mimetype="application/json", status=500)


    donation = donation[0]

    donation.chequenumber = post_data.get("chequenumber", "")
    donation.chequedate = post_data.get("chequedate", "")
    donation.chequebank = post_data.get("chequebank", "")
    donation.checkdeposite_date = post_data.get("checkdeposite_date", "")
    donation.cheque_credited_date = post_data.get("cheque_credited_date", "")
    donation.neft_bank_name = post_data.get("neft_bank_name", "")
    donation.neft_transaction_id = post_data.get("neft_transaction_id", "")
    donation.neft_transaction_date = post_data.get("neft_transaction_date", "")
    donation.neft_credited_date = post_data.get("neft_credited_date", "")
    donation.online_msg = post_data.get("online_msg", "")
    donation.online_resp_msg = post_data.get("online_resp_msg", "")
    donation.recipent_url = post_data.get("recipent_url", "")
    donation.transaction_key = post_data.get("transaction_key", "")

    try:
        donation.save()
        return HttpResponse(json.dumps({"status": "success"}),\
                            mimetype="application/json",\
                            status=200)
    except Exception as e:

        return HttpResponse(json.dumps({"status": "error", "message": str(e)}),\
                                       mimetype="application/json",\
                                       status=500)

'''


def payment_details(request):
    if request.method == 'GET':
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    from_ = request.POST.get('from_', '')
    if from_ == 'nad' or from_ == 'new_year':
        is_logged_in_user = False
        if request.user.is_authenticated():
            is_logged_in_user = True
        data = {}
        data['amount'] = int(request.POST.get('amount', "0"))
        data['email'] = request.POST.get('email', "")
        data['f_name'] = request.POST.get('first_name', "")
        data['l_name'] = request.POST.get('last_name', "")
        data['donate_to'] = request.POST.get('donate_to', "")
        data['honor'] = request.POST.get('honor', "")
        data['honor_name'] = request.POST.get('full_name', "")
        data['from_'] = from_
        data['is_loggedin'] = is_logged_in_user

        return render_response(request, "donation_payment_details.html", data)

    else:
        amount = int(request.POST.get('amount', "0"))
        donation_type = request.POST.get('donation_type', "")
        children = request.POST.get('children', "")
        # OMG!, number means number of classrooms
        number = request.POST.get("number", "")
        centres = request.POST.get("centres", "")
        num_subjects = request.POST.get("num_subjects", "")

        total_amount = amount

        if children:
            children = int(children)
            total_amount = total_amount * children
        elif number:
            number = int(number)
            total_amount = total_amount * number
        elif centres:
            centres = int(centres)
            total_amount = total_amount * centres

        is_logged_in_user = False
        if request.user.is_authenticated():
            is_logged_in_user = True

        return render_response(request, "donation_payment_details.html", \
                               {"amount": total_amount, \
                                "children": children, \
                                "number": number, \
                                "centres": centres, \
                                "donation_type": donation_type, \
                                "num_subjects": num_subjects,\
                                "is_loggedin": is_logged_in_user})

@csrf_exempt
def donate_online(request):
    if request.method == "GET":
        return HttpResponse("Only POST is Accepted")
    print(request.POST)
    donation_id = request.POST.get("id")
    amount = request.POST.get("amount")

    if not donation_id or not amount:
        return HttpResponse("Invalid Params")

    donation = Donation.objects.filter(id=donation_id)

    if not donation:
        return HttpResponse("Donation not found")

    donation = donation[0]
    donation.online_txn_status = 'started'

    import subprocess

    file_path = os.path.join(os.getcwd(), 'web/payment_gateway/payment.py')
    command = 'jython %s  %s  %s' % (file_path, donation_id, amount)
    donations_msg = subprocess.check_output(command, shell=True).strip()

    donation.online_msg = donations_msg
    donation.save()

    return render_response(request, "donation_online_payment.html", {"message": donations_msg, "amount": amount})


@login_required
def update_pledge(request):
    post_data = request.POST

    donation_id = post_data.get("id")

    if not donation_id:
        return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}),
                            mimetype="application/json", status=500)

    donation = Donation.objects.filter(id=donation_id, user=request.user)

    if not donation:
        return HttpResponse(json.dumps({"status": "error", "message": "donation id not found"}),
                            mimetype="application/json", status=500)

    donation = donation[0]

    donation.chequenumber = post_data.get("chequenumber", "")
    donation.chequedate = post_data.get("chequedate", "")
    donation.chequebank = post_data.get("chequebank", "")
    donation.checkdeposite_date = post_data.get("checkdeposite_date", "")
    donation.cheque_credited_date = post_data.get("cheque_credited_date", "")
    donation.neft_bank_name = post_data.get("neft_bank_name", "")
    donation.neft_transaction_id = post_data.get("neft_transaction_id", "")
    donation.neft_transaction_date = post_data.get("neft_transaction_date", "")
    donation.neft_credited_date = post_data.get("neft_credited_date", "")
    donation.online_msg = post_data.get("online_msg", "")
    donation.online_resp_msg = post_data.get("online_resp_msg", "")
    donation.recipent_url = post_data.get("recipent_url", "")
    donation.transaction_key = post_data.get("transaction_key", "")

    try:
        donation.save()
        return HttpResponse(json.dumps({"status": "success"}), \
                            mimetype="application/json", \
                            status=200)
    except Exception as e:

        return HttpResponse(json.dumps({"status": "error", "message": str(e)}), \
                            mimetype="application/json", \
                            status=500)

def notify_user(email, name, amount):
    args = {'name': str(name), 'amount': str(amount)}
    mail = ''
    body = ''
    subject = 'eVidyaloka - Donation Confirmation'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [email]
    cc=["donate@evidyaloka.org"]
    body = get_template('donor_regards_mail.html').render(Context(args))
    mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
    mail.content_subtype = 'html'
    mail.send()


@csrf_exempt
def pledge(request):
    print(request.POST)
    pledge_details = {}
    pledge_details["address"] = request.POST.get("address", "")
    pledge_details["address2"] = request.POST.get("address2", "")
    pledge_details["amount"] = int(request.POST.get("amount", "0"))
    pledge_details["channel"] = request.POST.get("channel", "Others")
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
    pledge_details["status"] = request.POST.get("status", "pending")

    try:

        email = pledge_details["email"]
        email_user = User.objects.filter(email=email)

        recipients = []
        is_existing_user = False
        password = ""

        if email_user:
            email_user = email_user[0]
            recipients.append(email_user)
            is_existing_user = True
        else:
            user = User(username=email, email=email)
            # password = User.objects.make_random_password()
            password = email.split("@")[0]
            user.first_name = pledge_details["name"]
            user.last_name = pledge_details["last_name"]
            user.set_password(password)
            user.is_active = True
            user.save()

            userProfile = user.userprofile
            userProfile.email = email
            userProfile.phone = pledge_details["phone"]
            userProfile.city = pledge_details["city"]
            userProfile.state = pledge_details["state"]
            userProfile.country = pledge_details["country"]
            userProfile.save()

            wellwisher = Role.objects.get(name="Well Wisher")
            teacher = Role.objects.get(name="Teacher")

            userProfile.pref_roles.remove(teacher)
            userProfile.pref_roles.add(wellwisher)

            userProfile.role.add(wellwisher)
            userProfile.save()

            email_user = user

        pledge_details["user"] = email_user

        # if 'status' in pledge_details and pledge_details['status'] is 'pending' and 'amount' in pledge_details and 'name' in pledge_details:
        #     try:
        #         notify_user(email, pledge_details['name'], pledge_details['amount'])
        #     except Exception as e:
        #         print "Error reason = ", e
        #         print "Error at line no = ", traceback.format_exc()

        donation = Donation(**pledge_details)

        donation.save()

        pledge_details["is_existing_user"] = is_existing_user
        pledge_details["password"] = password

        # admins = User.objects.filter(is_superuser = True)
        admins = User.objects.filter(email__in=['Nandini.sarkar@evidyaloka.org', 'venkat.sriraman@evidyaloka.org'])

        # if pledge_details["payment_type"] != "online":
        #     _send_mail([email_user], '_pledge', pledge_details)

        #     _send_mail(admins, '_pledge', pledge_details)
        # elif password:
        #     # if password is not empty a new user is created
        #     _send_mail([email_user], '_pledge', pledge_details)

        return HttpResponse(json.dumps({"status": "success", "donation_id": donation.id, "amount" : donation.amount}), mimetype="application/json",
                            status=200)
    except Exception as e:
        return HttpResponse(json.dumps({"status": "error", "message": str(e)}), mimetype="application/json", status=500)


def donors(request):
    donations = Donation.objects.all()

    return render_response(request, 'donors.html', {"donations": donations})


def spread_word(request):
    return render_response(request, 'spread_the_word.html', {})


def spend_some_Time(request):
    return render_response(request, 'new_volunteer_temp.html', {})


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def download_view(request):
    template = request.GET.get("template", "")
    return render_to_pdf(template, {'pagesize': 'A4'})


def complete_offering(request):
    if request.method == "GET":
        offering_id = request.GET.get("offering_id", None)
        sessions = Session.objects.values('id','date_start').filter(offering=offering_id, date_start__gte=datetime.datetime.now())
        sessions = [{'id':ses['id'], 'date':ses['date_start'].isoformat()} for ses in sessions ]
        return HttpResponse(simplejson.dumps(sessions), mimetype="application/json")

    if request.method =='POST':
        offering_id = request.POST.get("offering_id", None)
        status = 'fail'
        message = 'No offering mark as complete and No feature sessions were deleted'
        if offering_id:
            obj = get_object_or_none(Offering, pk=offering_id)
            if obj:
                obj.status = 'completed'
                obj.save()
                Session.objects.filter(offering=offering_id, date_start__gte=datetime.datetime.now()).delete()
                print(obj.active_teacher.id)
                release_slots(obj.active_teacher)
                status = 'success'
                message = 'offering mark as complete and feature sessions were deleted'
                
        return HttpResponse(simplejson.dumps([{'status':status, 'message':message}]), mimetype="application/json")




def active_cities_map(request):
    active_cities = dict1 = {
        'rows': [{'c': [{'f': None, 'v': 28.6100}, {'f': None, 'v': 77.2300}, {'f': None, 'v': 'Delhi'}]},
                 {'c': [{'f': None, 'v': 12.9667}, {'f': None, 'v': 77.5667}, {'f': None, 'v': 'Bangalore'}]},
                 {'c': [{'f': None, 'v': 13.0839}, {'f': None, 'v': 80.2700}, {'f': None, 'v': 'Chennai'}]},
                 {'c': [{'f': None, 'v': 18.9750}, {'f': None, 'v': 72.8258}, {'f': None, 'v': 'Mumbai'}]},
                 {'c': [{'f': None, 'v': 40.6700}, {'f': None, 'v': -73.9400}, {'f': None, 'v': 'New York'}]},
                 {'c': [{'f': None, 'v': 43.7000}, {'f': None, 'v': -79.4000}, {'f': None, 'v': 'Toronto'}]},
                 {'c': [{'f': None, 'v': 44.4758}, {'f': None, 'v': -73.2119}, {'f': None, 'v': 'Burlington'}]},
                 {'c': [{'f': None, 'v': 18.5203}, {'f': None, 'v': 73.8567}, {'f': None, 'v': 'Pune'}]},
                 {'c': [{'f': None, 'v': 9.9197}, {'f': None, 'v': 78.1194}, {'f': None, 'v': 'Madhurai'}]},
                 {'c': [{'f': None, 'v': 17.3660}, {'f': None, 'v': 78.4760}, {'f': None, 'v': 'Hyderabad'}]},
                 {'c': [{'f': None, 'v': 12.5576}, {'f': None, 'v': 80.1754}, {'f': None, 'v': 'Kalpakkam'}]},
                 {'c': [{'f': None, 'v': 11.5000}, {'f': None, 'v': 79.5000}, {'f': None, 'v': 'Nevyeli'}]},
                 {'c': [{'f': None, 'v': 11.0813}, {'f': None, 'v': 76.9725}, {'f': None, 'v': 'Coimbatore'}]},
                 {'c': [{'f': None, 'v': 40.8994}, {'f': None, 'v': -74.0457}, {'f': None, 'v': 'Hackensack'}]},
                 {'c': [{'f': None, 'v': -33.8600}, {'f': None, 'v': 151.2111}, {'f': None, 'v': 'Sydney'}]},
                 {'c': [{'f': None, 'v': 50.8500}, {'f': None, 'v': 4.3500}, {'f': None, 'v': 'Brussels'}]},
                 {'c': [{'f': None, 'v': 52.2333}, {'f': None, 'v': 21.0167}, {'f': None, 'v': 'Warsaw'}]},
                 {'c': [{'f': None, 'v': 28.1800}, {'f': None, 'v': 76.6200}, {'f': None, 'v': 'Rewari'}]},
                 {'c': [{'f': None, 'v': 55.6761}, {'f': None, 'v': 12.5683}, {'f': None, 'v': 'Copenhagen'}]},
                 {'c': [{'f': None, 'v': 28.6700}, {'f': None, 'v': 77.4200}, {'f': None, 'v': 'Gahziabad'}]},
                 {'c': [{'f': None, 'v': 45.5200}, {'f': None, 'v': -122.6819}, {'f': None, 'v': 'Portland'}]},
                 {'c': [{'f': None, 'v': 51.9000}, {'f': None, 'v': -0.4333}, {'f': None, 'v': 'Luton'}]},
                 {'c': [{'f': None, 'v': 17.4500}, {'f': None, 'v': 78.5000}, {'f': None, 'v': 'Secunderabad'}]},
                 {'c': [{'f': None, 'v': 27.9710}, {'f': None, 'v': -82.4560}, {'f': None, 'v': 'Tampa'}]},
                 {'c': [{'f': None, 'v': 48.8567}, {'f': None, 'v': 2.3508}, {'f': None, 'v': 'Paris'}]},
                 {'c': [{'f': None, 'v': 26.2167}, {'f': None, 'v': 50.5833}, {'f': None, 'v': 'Manama'}]},
                 {'c': [{'f': None, 'v': 39.9500}, {'f': None, 'v': -75.1700}, {'f': None, 'v': 'Philadelphia'}]},
                 {'c': [{'f': None, 'v': 51.0572}, {'f': None, 'v': -0.1257}, {'f': None, 'v': 'London'}]},
                 {'c': [{'f': None, 'v': 59.3294}, {'f': None, 'v': 18.0686}, {'f': None, 'v': 'Stockholm'}]},
                 {'c': [{'f': None, 'v': 10.4504}, {'f': None, 'v': 77.5104}, {'f': None, 'v': 'Palani'}]}, ],
        'cols': [{'pattern': '', 'type': 'number', 'id': '', 'label': 'Longitude'},
                 {'pattern': '', 'type': 'number', 'id': '', 'label': 'Latitude'},
                 {'pattern': '', 'type': 'string', 'id': '', 'label': 'Place'}]}

    return HttpResponse(simplejson.dumps(active_cities), mimetype="application/json")


def contentadmin(request):
    if request.method == 'GET':
        topics = Topic.objects.values_list('id').distinct()
        subjects = Topic.objects.values_list('course_id__subject').distinct()
        boards = Topic.objects.values_list('course_id__board_name').distinct()
        grades = Topic.objects.values_list('course_id__grade').distinct()
        # status = TopicDetails.objects.values_list('status').distinct()
        # attributes = Attribute.objects.values_list('types').distinct()
        # print('topics',topics)
        topics = [topic[0] for topic in topics]
        subjects = [subject[0] for subject in subjects]
        boards = [board[0] for board in boards]
        grades = [grade[0] for grade in grades]
        # status = [statuses[0] for statuses in status]
        # attributes = [attribute[0] for attribute in attributes]
        status_dropdown = ['Submitted','Under Review','Approved']
        status = ['In Review','Under Review','Approved']
        attributes = ['Lesson Plan','Worksheets','Videos','TextBook']
        user_detail = request.GET.get('user_id','')

        if user_detail:
            id =  UserProfile.objects.get(user_id = user_detail)
            name = id.user.first_name + " " + id.user.last_name
            user_id = id.user.id
            lang = id.pref_medium
            print('id',name, user_id,lang)
            response = {'user_id':user_id,'name':name,'lang':lang}
            return HttpResponse(simplejson.dumps(response), mimetype='application/json')   

        # print('user_detail user_detail',user_detail)
        save_user_activity(request, 'Viewed Page: My Book - Manage Contents', 'Page Visit')
        # Topic_details = TopicDetails.objects.filter(~Q(author=None)).filter(topic__course_id__grade__in = grade,attribute__types__in = attribute,topic__course_id__board_name__in=board,status__in=status,topic__course_id__subject__in=subject)
        subtopic_details = SubTopics.objects.filter(~Q(author_id=None)).filter(status__in=status)
        topic_data =[]

        for topic_deatil in subtopic_details :
            # print('reviewer_name',topic_deatil.reviewer)
            try:
                workstream =TopicDetails.objects.filter(topic=topic_deatil.topic.id, status__in=status, author=topic_deatil.author_id)[0].attribute.types
            except:
                workstream = 'NA'
            if topic_deatil.reviewer :
                print('scdsc',topic_deatil.author_id)
                
                
                # print('kkkkkkkkkkkkkkkkkkkkk',k,topic_deatil.topic)
                subtopic_details = {
                            'board':topic_deatil.topic.course_id.board_name,   
                            'grade':topic_deatil.topic.course_id.grade,
                            'subject':topic_deatil.topic.course_id.subject,
                            'topic': topic_deatil.topic.title,
                            'subtopic': topic_deatil.name,
                            'status':topic_deatil.status,
                            'author':topic_deatil.author_id.first_name+" "+topic_deatil.author_id.last_name,
                            'author_id': topic_deatil.author_id,
                            'workstream':workstream,
                            'id':topic_deatil.id,
                            'reviewer_name':topic_deatil.reviewer.first_name+" "+topic_deatil.reviewer.last_name
                            
                        }
            else:
                subtopic_details = {
                            'board':topic_deatil.topic.course_id.board_name,   
                            'grade':topic_deatil.topic.course_id.grade,
                            'subject':topic_deatil.topic.course_id.subject,
                            'topic': topic_deatil.topic.title,
                            'subtopic': topic_deatil.name,
                            'status':topic_deatil.status,
                            'author':topic_deatil.author_id.first_name+" "+topic_deatil.author_id.last_name,
                            'author_id': topic_deatil.author_id.id,
                            'workstream':workstream,
                            'id':topic_deatil.id,
                            'reviewer_name':' ',
                            
                        }

            topic_data.append(subtopic_details)
        print(topic_data)
        reviewer_list = {}
        reviewers_obj = RolePreference.objects.filter(role=19)
        for reviewer in reviewers_obj:
                # print(reviewer.userprofile_id)
                # print "'language'",reviewer.userprofile.user.first_name
                reviewer_list[reviewer.id] = {'name': reviewer.userprofile.user.first_name + " " + reviewer.userprofile.user.last_name,'id':reviewer.userprofile.user.id,'language':reviewer.userprofile.pref_medium}
        
        # print('topic_data',  len(topic_data))
        return render_to_response('content_lookup.html',
                              {"reviewer_list":reviewer_list,"topics": topics,"subjects": subjects,'attributes':attributes, "boards": boards, "grades": grades,"status":status_dropdown,"topic_data":topic_data},
                              context_instance=RequestContext(request))

    elif request.method == 'POST':
        board = request.POST.get('board', '').split(",")[0]
        grade = request.POST.get('grade', '').split(",")[0]
        subject = request.POST.get('subject', '').split(",")[0]
        status = request.POST.get('status', '')
        attribute = request.POST.get('workstream','')
        user_detail = request.POST.get('user_id','')
        status_dropdown = ['Submitted','Under Review','Approved']
        topic_data =[]
        reviewer_list = {}
        reviewers_obj = RolePreference.objects.filter(role=19)
        
        if board == 'All':
            board = Course.objects.values_list('board_name').distinct()
        else:
            board = [board]
        if grade == 'All' :
            grade = [5,6,7,8]
        else:
            grade = [grade]
        
        if subject == 'All':
            subject = ['Maths','Science']
        else:
            subject = [subject]
        if attribute == 'All':
            attribute = ['Videos','Lesson Plan','TextBook','Worksheets']
        if status == 'All':          
            status = ['In Review','Under Review','Approved']                  
        elif status == 'Submitted':
            status = ['In Review']
        else:
            status = [status]    
        # print('gradehvcndbncv',grade)
        
        # print "reviewers_obj",reviewers_obj
        for reviewer in reviewers_obj:
                # print(reviewer.userprofile_id)
                # print "'language'",reviewer.userprofile.user.first_name
                reviewer_list[reviewer.id] = {'name': reviewer.userprofile.user.first_name + " " + reviewer.userprofile.user.last_name,'id':reviewer.userprofile.user.id,'language':reviewer.userprofile.pref_medium}
        # Topic_details = TopicDetails.objects.filter(~Q(author=None)).filter(topic__course_id__grade__in = grade,attribute__types__in = attribute,topic__course_id__board_name__in=board,status__in=status,topic__course_id__subject__in=subject)
        subtopic_details = SubTopics.objects.filter(~Q(author_id=None)).filter(topic__course_id__grade__in = grade,topic__course_id__board_name__in=board,status__in=status,topic__course_id__subject__in=subject)
        
        for topic_deatil in subtopic_details :
            # print('reviewer_name',topic_deatil.reviewer)

            if topic_deatil.reviewer :
                subtopic_details = {
                            'board':topic_deatil.topic.course_id.board_name,   
                            'grade':topic_deatil.topic.course_id.grade,
                            'subject':topic_deatil.topic.course_id.subject,
                            'topic': topic_deatil.topic.title,
                            'subtopic': topic_deatil.name,
                            'status':topic_deatil.status,
                            'author':topic_deatil.author_id.first_name+" "+topic_deatil.author_id.last_name,
                            'author_id': topic_deatil.author_id,
                            'workstream':TopicDetails.objects.filter(topic=topic_deatil.topic.id, status__in=status, author=topic_deatil.author_id)[0].attribute.types,
                            'id':topic_deatil.id,
                            'reviewer_name':topic_deatil.reviewer.first_name+" "+topic_deatil.reviewer.last_name
                            
                        }
            else:
                subtopic_details = {
                            'board':topic_deatil.topic.course_id.board_name,   
                            'grade':topic_deatil.topic.course_id.grade,
                            'subject':topic_deatil.topic.course_id.subject,
                            'topic': topic_deatil.topic.title,
                            'subtopic': topic_deatil.name,
                            'status':topic_deatil.status,
                            'author':topic_deatil.author_id.first_name+" "+topic_deatil.author_id.last_name,
                            'author_id': topic_deatil.author_id,
                            'workstream':TopicDetails.objects.filter(topic=topic_deatil.topic.id, status__in=status, author=topic_deatil.author_id)[0].attribute.types,
                            'id':topic_deatil.id,
                            'reviewer_name':' ',
                            
                        }

                # subtopic_details = {
                #             'board':topic_deatil.topic.course_id.board_name,
                #             'grade':topic_deatil.topic.course_id.grade,
                #             'subject':topic_deatil.topic.course_id.subject,
                #             'status':topic_deatil.status,
                #             'author':topic_deatil.author.first_name+" "+topic_deatil.author.last_name,
                #             'author_id':topic_deatil.author_id,
                #             'topic_name':topic_deatil.topic.title,
                #             'workstream':None,
                #             'id':topic_deatil.id,   
                #         }

            topic_data.append(subtopic_details)
        # print "ssss",board[0],grade,subject,status,attribute,Topic_details.query,Topic_details,topic_data
        topics = Topic.objects.values_list('title').distinct()
        subjects = Topic.objects.values_list('course_id__subject').distinct()
        boards = Topic.objects.values_list('course_id__board_name').distinct()
        grades = Topic.objects.values_list('course_id__grade').distinct()
        # status = TopicDetails.objects.values_list('status').distinct()
        # attributes = Attribute.objects.values_list('types').distinct()
        topics = [topic[0] for topic in topics]
        subjects = [subject[0] for subject in subjects]
        boards = [board[0] for board in boards]
        grades = [grade[0] for grade in grades]
        # status = [statuses[0] for statuses in status]
        # attributes = [attribute[0] for attribute in attributes]
        status = ['In Review','Under Review','Approved']
        attributes = ['Lesson Plan','Worksheets','Videos','TextBook']
    # print("reveeee = = = ",reviewer_list)

    return render_to_response('content_lookup.html',
                              {"topics": topics,"reviewer_list":reviewer_list, "topic_data":topic_data,"subjects": subjects,'attributes':attributes, "boards": boards, "grades": grades,"status":status_dropdown},
                              context_instance=RequestContext(request))
    
def contentreviwer(request):
    
        topics_count = SubTopics.objects.filter(status= "Under Review", reviewer_id = request.user.id).count()
        print "topics_count",topics_count
        save_user_activity(request, 'Viewed Page: My Book - Manage Contents', 'Page Visit')
        return render_response(request,'contentreview_myevidyalokapage.html',
                              {"topics_count": topics_count})

    

        
    
def contentvolunteer(request):
    user = request.user
    userp = UserProfile.objects.filter(user=user)[0]
    assigned_topics = TopicDetails.objects.filter(author=user, status="Assigned")
    inprogress_topics = TopicDetails.objects.filter(author=user, status="In Progress")
    completed_topic = TopicDetails.objects.filter(author=user, status="In Review")
    is_pref_role_content_admin = has_pref_role(userp, "Content Admin")
    is_booked = False
    topic_detail = SubTopics.objects.filter(author_id=request.user, status = 'Not Started')

    print "topic_detail",topic_detail
    topic_title =''
    topic_id = ''
    attribute_type=''
    if topic_detail:
        is_booked = True
        topic_id = SubTopics.objects.values_list('topic_id').filter(author_id=request.user,status = 'Not Started').distinct()
        topic_id = list(topic_id [0])[0]
    # (tuple(map (int,topic_id)))
        topic = Topic.objects.filter(id=topic_id).distinct()
        print "topic" ,topic
        topic_title =topic[0].title 
        topic_id = topic[0].id
        print "topics",topic,topic_id,topic_title
        topic_details_workstream = TopicDetails.objects.values_list("attribute_id").filter(topic_id = topic_id,author = request.user,status='Booked').distinct()
        try:
            attribute_id = list(topic_details_workstream [0])[0]
            topic_workstream = Attribute.objects.filter(id=attribute_id)
            attribute_type = topic_workstream[0].types
            print "ddddddd",attribute_type
        except:
            attribute_type = "NA"
            print("sacdfdscdtdcdtxf")
    is_assigned = False
    topic_detail = SubTopics.objects.filter(author_id=request.user, status = 'Assigned')
    if topic_detail:
        is_assigned = True
    topic_id_id = topic_id
    topic_id = SubTopics.objects.values_list('topic_id').filter(author_id=request.user,status__in=( 'Not Started','In Review')).distinct()
    print "topickkkkkkkkkkkkkkkkkkkkk",topic_id
    if topic_id :
        topic_id = list(topic_id [0])[0]
    # print "topic_id",topic_id
    is_videoassign = False
    
    video_assignment = VideoAssignments.objects.filter(topic = topic_id,status= 'Submitted',added_by_id = request.user )
    print('video_assignment',video_assignment,topic_id,request.user)
    # print "video_assignment", video_assignment.query
    if video_assignment :
        if SubTopics.objects.filter(author_id=request.user, status = 'Assigned'):
            is_videoassign = False
        else:
            is_videoassign = True
    # print "video_assignment",is_videoassign,is_assigned
    Topic_details = TopicDetails.objects.filter(author=request.user.id).distinct()
    # print'Topic_details',Topic_details
    topic_data=[]
    workstream_type = ''
    for topic_deatil in Topic_details :
            workstream_type = topic_deatil.attribute.types
            subtopic_details = {
                        'board':topic_deatil.topic.course_id.board_name,
                        'grade':topic_deatil.topic.course_id.grade,
                        'subject':topic_deatil.topic.course_id.subject,
                        'status':topic_deatil.status,
                        'author':topic_deatil.author.first_name+" "+topic_deatil.author.last_name,
                        'author_id':topic_deatil.author_id,
                        'workstream':topic_deatil.attribute.types,
                        'topic_name':topic_deatil.topic.title,
                        
                    }
            topic_data.append(subtopic_details)
    print ""        
    print"topic_data",topic_data
    print'is_videoassign',is_videoassign
    print'attribute_type',workstream_type
    print 'is_assigned',is_assigned
    print 'is_booked',is_booked
    
    return render_response(request, 'contentvolunteer.html',
                           {'topic_id_id':topic_id_id,'assigned_topics': assigned_topics,"topic_data":topic_data,'topic_id':topic_id,'topic_title':topic_title,'is_assigned':is_assigned,"attribute_type":attribute_type, "is_pref_role": is_pref_role_content_admin,'is_booked':is_booked,
                            'inprogress_topics': inprogress_topics,'is_videoassign':is_videoassign, 'completed_topics': completed_topic,'workstream_type':workstream_type})

@csrf_exempt
def claim_topic(request):
    user = request.user
    topic_details_id = request.POST.get('topic_id', '')
    submit_type = request.POST.get('submit_type', '')
    recvr = User.objects.filter(id__in=[4547, 224])
    if not submit_type or not topic_details_id: return HttpResponse('Failed')
    topic_details = TopicDetails.objects.get(id=topic_details_id)
    if submit_type == 'claim-it':
        topic_details.status = "In Progress"
    elif submit_type == 'mark-it-complete':
        topic_details.status = "In Review"
        topic_details.updated_by = user
        topic_details.last_updated_date = datetime.datetime.now()

    try:
        topic_details.save()
        if submit_type == 'mark-it-complete':
            inreview_topics = TopicDetails.objects.filter(status="In Review")
            _send_mail(recvr, '_topic_complete', {'inreview_topics': inreview_topics})
        elif submit_type == 'claim-it':
            date1 = datetime.datetime.today().strftime("%d/%m/%Y")
            _send_mail(recvr, '_topic_accepted',
                       {'Topic': topic_details.topic.title, 'author': topic_details.author.first_name, 'Date': date1,
                        'Board': topic_details.topic.course_id.board_name,
                        'Subject': topic_details.topic.course_id.subject, 'Grade': topic_details.topic.course_id.grade,
                        'Type': topic_details.attribute.types})
        else:
            pass
    except:
        return HttpResponse('Failed')

    return HttpResponse('Success');


def careers(request):
    return render_to_response('careers.html', {}, context_instance=RequestContext(request))


@login_required
def content_lookup(request):
    if request.method == 'GET':
        topics = Topic.objects.values_list('title').distinct()
        subjects = Topic.objects.values_list('course_id__subject').distinct()
        boards = Topic.objects.values_list('course_id__board_name').distinct()
        grades = Topic.objects.values_list('course_id__grade').distinct()
        status = TopicDetails.objects.values_list('status').distinct()
        attributes = Attribute.objects.values_list('types').distinct()
        topics = [topic[0] for topic in topics]
        subjects = [subject[0] for subject in subjects]
        boards = [board[0] for board in boards]
        grades = [grade[0] for grade in grades]
        status = [statuses[0] for statuses in status]
        attributes = [attribute[0] for attribute in attributes]
        save_user_activity(request, 'Viewed Page: My Book - Manage Contents', 'Page Visit')
        topic_data =[]
        # print "board",board,grade,subject,status,attribute
        Topic_details = TopicDetails.objects.all()
        print "dddddddd",Topic_details.query
        for topic_deatil in Topic_details :
            try:
                board = topic_deatil.topic.course_id.board_name
                grade = topic_deatil.topic.course_id.grade
                subject = topic_deatil.topic.course_id.subject
            except:
                board = "NA" 
                grade = "NA"
                subject = "NA"  
            subtopic_details = {
                        'board':board,
                        'grade':grade,
                        'subject':subject,
                        'status':topic_deatil.status,
                        'author':topic_deatil.author.first_name+" "+topic_deatil.author.last_name,
                        'author_id':topic_deatil.author_id,
                        'topic_name':topic_deatil.topic.title,
                        'workstream':topic_deatil.attribute.types,
                        'id':topic_deatil.id,
                        'url':topic_deatil.drafturl
                        
                    }
            topic_data.append(subtopic_details)
        return render_to_response('content_lookup.html',
                              {"topics": topics,"topic_data":topic_data,"subjects": subjects,'attributes':attributes, "boards": boards, "grades": grades,"status":status},
                              context_instance=RequestContext(request))

    elif request.method == 'POST':
        board = request.POST.get('board', '').split(",")[0]
        grade = request.POST.get('grade', '').split(",")[0]
        subject = request.POST.get('subject', '').split(",")[0]
        status = request.POST.get('status', '')
        attribute = request.POST.get('workstream','')
        topic_data =[]
        reviewer_list = {}
        reviewers_obj = UserProfile.objects.filter(role=19)
  

      
        for reviewer in reviewers_obj:
            reviewer_list[reviewer.id] = {'name': reviewer.user.first_name + " " + reviewer.user.last_name,'id':reviewer.user.id,'language':reviewer.user.userprofile.pref_medium}

        Topic_details = TopicDetails.objects.filter(topic__course_id__grade =grade,attribute__types = attribute,topic__course_id__board_name=board,status=status,topic__course_id__subject=subject).distinct()
        for topic_deatil in Topic_details :
            subtopic_details = {
                        'board':board,
                        'grade':grade,
                        'subject':subject,
                        'status':status,
                        'author':topic_deatil.author.first_name+" "+topic_deatil.author.last_name,
                        'author_id':topic_deatil.author_id,
                        'topic_name':topic_deatil.topic.title,
                        'workstream':attribute,
                        'id':topic_deatil.id
                        
                    }
            topic_data.append(subtopic_details)
        print "ssss",board[0],grade,subject,status,attribute,Topic_details.query,Topic_details,topic_data
        topics = Topic.objects.values_list('title').distinct()
        subjects = Topic.objects.values_list('course_id__subject').distinct()
        boards = Topic.objects.values_list('course_id__board_name').distinct()
        grades = Topic.objects.values_list('course_id__grade').distinct()
        status = TopicDetails.objects.values_list('status').distinct()
        attributes = Attribute.objects.values_list('types').distinct()
        topics = [topic[0] for topic in topics]
        subjects = [subject[0] for subject in subjects]
        boards = [board[0] for board in boards]
        grades = [grade[0] for grade in grades]
        status = [statuses[0] for statuses in status]
        attributes = [attribute[0] for attribute in attributes]

    topics = [topic[0] for topic in topics]
    subjects = [subject[0] for subject in subjects]
    boards = [board[0] for board in boards]
    grades = [grade[0] for grade in grades]
    save_user_activity(request, 'Viewed Page: My Book - Manage Contents', 'Page Visit')
    return render_to_response('content_lookup.html',
                              {"topics": topics,"reviewer_list":reviewer_list, "topic_data":topic_data,"subjects": subjects,'attributes':attributes, "boards": boards, "grades": grades,"status":status},
                              context_instance=RequestContext(request))


@login_required
def get_topics(request):
    grade = request.GET.get("grade")
    board = request.GET.get("board")
    subject = request.GET.get("subject")

    topics = Topic.objects.all()

    if grade:
        topics = topics.filter(course_id__grade=grade)

    if board:
        topics = topics.filter(course_id__board_name=board)

    if subject:
        topics = topics.filter(course_id__subject=subject)

    topics = topics.values_list('title').distinct()
    topics = [topic[0] for topic in topics]

    return HttpResponse(simplejson.dumps({'topics': topics}), mimetype='application/json')


@login_required
@csrf_exempt
def get_content_lookup(request):
    data = eval(request.POST.get('data', ''))
    topic_details = TopicDetails.objects.all()

    boards = data.get('boards', '')
    subject = data.get('subject', '')
    attribute = data.get('attribute', '')
    grade = data.get('grade', '')
    topic_title = data.get('topic_title', '')
    topic_status = data.get('topic_status', '')
    topic_details_status = data.get('topic_details_status', '')
    show_action = ''
    topic_detail_stat = ''

    if boards: topic_details = topic_details.filter(topic__course_id__board_name=boards)
    if attribute: topic_details = topic_details.filter(attribute__types=attribute)
    if subject: topic_details = topic_details.filter(topic__course_id__subject=subject)
    if grade: topic_details = topic_details.filter(topic__course_id__grade=grade)
    if topic_title: topic_details = topic_details.filter(topic__title=topic_title)
    if topic_status: topic_details = topic_details.filter(topic__status=topic_status)
    if topic_details_status:
        topic_details = topic_details.filter(status=topic_details_status)
        show_action = 1
        topic_detail_stat = topic_details_status

    usr = UserProfile.objects.filter(user=request.user)[0]
    if not (usr and (has_role(usr, 'Content Admin') or request.user.is_superuser)): show_action = ''

    content_volunteer = Role.objects.get(name="Content Developer")
    user_pref_cv = UserProfile.objects.filter(pref_roles=content_volunteer)
    lookup_dict = []

    paginator = Paginator(topic_details, 25)
    page = data.get('page', 1)
    try:
        topic_details = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        topic_details = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        topic_details = paginator.page(paginator.num_pages)
    for topic in topic_details:
        if topic.status == "Not Started" or topic.status == 'Assigned' or topic.status == 'Published':
            content_volunteer = get_content_volunteer(topic.id)
        else:
            content_volunteer = []

        if topic.author:
            author = {'id': topic.author.id, 'name': topic.author.first_name + " " + topic.author.last_name}
        else:
            author = {'id': '', 'name': ""}

        if topic.updated_by:
            updated_by = topic.updated_by.username
        else:
            updated_by = ''

        # Draft_url Calculation
        draft_url_list = topic.drafturl

        lookup_dict.append({'id': topic.id, 'topic': topic.topic.title, 'attribute': topic.attribute.types,
                            'url': topic.url or topic.topic.url, 'type': topic.types, 'status': topic.status,
                            'date': str(topic.last_updated_date), 'board': topic.topic.course_id.board_name,
                            'author': author, 'updated_by': updated_by, 'content_volunteer': content_volunteer,
                            'grade': topic.topic.course_id.grade, 'draft_url': draft_url_list})

    return HttpResponse(
        simplejson.dumps({'topic_details': lookup_dict, 'is_authenticated': request.user.is_authenticated(),
                          "show_action": show_action, 'topic_detail_stat': topic_detail_stat,
                          "prev": topic_details.previous_page_number(),
                          "next": topic_details.next_page_number(), "current": topic_details.number,
                          "total": topic_details.paginator.num_pages}),
        mimetype='application/json')


def get_content_volunteer(topic_details_id):
    td = TopicDetails.objects.get(id=topic_details_id)
    board = td.topic.course_id.board_name
    content_volunteer = Role.objects.get(name="Content Developer")
    teacher_role = Role.objects.get(name="Teacher")

    if board == "NCERT":
        user_pref_cv = UserProfile.objects.filter(pref_roles=content_volunteer, pref_medium="Hindi")
    elif board == "TNSB":
        user_pref_cv = UserProfile.objects.filter(pref_roles=content_volunteer, pref_medium="Tamil")
    elif board == "APSB":
        user_pref_cv = UserProfile.objects.filter(pref_roles=content_volunteer, pref_medium="Telugu")
    elif board == "DSERT":
        user_pref_cv = UserProfile.objects.filter(pref_roles=content_volunteer, pref_medium="Kannada")
    elif board == "MHSB":
        user_pref_cv = UserProfile.objects.filter(pref_roles=content_volunteer, pref_medium="Hindi")
    elif board == "WBSED":
        user_pref_cv = UserProfile.objects.filter(pref_roles=content_volunteer, pref_medium="Bengali")
    else:
        user_pref_cv = []

    if user_pref_cv: user_pref_cv = [{"id": obj.user.id, "username": obj.user.first_name + " " + obj.user.last_name} for
                                     obj in user_pref_cv]
    return user_pref_cv


@login_required
@csrf_exempt
def allocate(request):
    user = request.user
    topic_details = eval(request.POST.get('data', ''))
    for topic_detail in topic_details:
        topic_detail_obj = TopicDetails.objects.get(id=topic_detail['topic_id'])
        user_id = topic_detail['user_id']
        grade = topic_detail['grade']
        if user_id:
            author = User.objects.get(id=user_id)
            topic_detail_obj.status = "Assigned"
            topic_detail_obj.author = author
            topic_detail_obj.updated_by = user
            topic_detail_obj.last_updated_date = datetime.datetime.now()
            _topic = topic_detail_obj.topic
            _topic.status = "In Progress"
            _topic.save()
            try:
                topic_detail_obj.save()
                _send_mail([author], '_topic_allotted', {'Board': topic_detail_obj.topic.course_id.board_name,
                                                         'Subject': topic_detail_obj.topic.course_id.subject,
                                                         'Grade': topic_detail_obj.topic.course_id.grade,
                                                         'Title': topic_detail_obj.topic.title,
                                                         'Type': topic_detail_obj.attribute.types})
            except:

                return HttpResponse("Failed")
    return HttpResponse("Success")


@login_required
@csrf_exempt
def publish(request):
    user = request.user
    topic_details = eval(request.POST.get('data', ''))
    for topic_detail in topic_details:
        topic_details = TopicDetails.objects.get(id=topic_detail['topic_id'])
        topic_details.status = "Published"
        topic_details.updated_by = user
        topic_details.last_updated_date = datetime.datetime.now()
        _topic = topic_details.topic
        _topic.status = "Partially Complete"
        try:
            topic_details.save()
            _topic.save()
            _send_mail([topic_details.author], '_topic_published',
                       {'Board': _topic.course_id.board_name, 'Subject': _topic.course_id.subject,
                        'Grade': _topic.course_id.grade, 'Title': _topic.title, 'Type': topic_details.attribute.types,
                        'Url': topic_details.url})
        except:
            return HttpResponse("Failed")
        non_published_topicdetails = TopicDetails.objects.filter(~Q(status='Published'), topic__id=_topic.id)
        if len(non_published_topicdetails) == 0:
            _topic.status = "Complete"
            _topic.save()

    return HttpResponse("Success");


@csrf_exempt
def get_volunteers_topics(request):
    user = request.user
    status_filter = request.POST.get('filter', '')
    if not status_filter: return HttpResponse("Failed")

    volunteer_topics = TopicDetails.objects.filter(author=user, status=status_filter)
    results = []
    for obj in volunteer_topics:
        topic_obj = {}
        url = obj.url or obj.topic.url or '#'
        results.append({"topic": obj.topic.title, "subject": obj.topic.course_id.subject, "url": url,
                        'grade': obj.topic.course_id.grade,
                        'board': obj.topic.course_id.board_name, 'workstream': obj.attribute.types})

    return HttpResponse(simplejson.dumps({"topic_details": results, 'username': request.user.username}),
                        mimetype='application/json')


def teachersday14(request):
    return render_response(request, 'teachersday14.html', {})


def draw_map(request):
    return render_to_response('map.html', {}, context_instance=RequestContext(request))


def news_events(request):
    return render_to_response('news_events.html', {}, context_instance=RequestContext(request))


def governance(request):
    return render_to_response('governance.html', {}, context_instance=RequestContext(request))


def privacy_policies(request):
    return render_to_response('privacy_terms.html', {}, context_instance=RequestContext(request))

def rfp(request):
    return render_to_response('rfp.html', {}, context_instance=RequestContext(request))


# ------------------------------------   Student Module -----------------------------------#


# Reports Generation


def get_report_data(id, center_id, start_date=datetime.datetime(2016, 04, 15, 0, 0),
                    end_date=datetime.datetime(2017, 04, 14, 0, 0), aytitle='AY 16 - 17'):
    if id:
        student = Student.objects.get(pk=id)
        # Basic details
        basic_details1 = OrderedDict()
        basic_details2 = OrderedDict()
        basic_details1['name'] = student.name
        basic_details1['age'] = '-'
        basic_details1['gender'] = student.gender
        basic_details1['grade'] = make_number_verb(student.grade)
        basic_details2['school'] = student.center.name
        basic_details2['village'] = student.center.village
        basic_details2['state'] = student.center.state
        # Student photo
        photo = '/static/images/report_placeh_all.png'
        if student.photo:
            photo_path = os.getcwd() + '/' + student.photo.url
            if os.path.isfile(photo_path):
                photo = '/' + student.photo.url

        # Attendance details
        attend = student.sessionattendance_set.filter(session__date_start__gte=start_date,
                                                      session__date_end__lt=end_date).values_list(
            'session__offering__id')
        pre = dict(attend.filter(is_present='Yes').annotate(present=Count('id')))
        abst = dict(attend.filter(is_present='No').annotate(present=Count('id')))
        final_attend = []
        for k, v in pre.items():
            offerin = Offering.objects.get(pk=k)
            if (offerin.center.id != center_id):
                continue
            offer_name = make_number_verb(offerin.course.grade) + ' ' + offerin.course.subject
            if k in abst:
                final_attend.append({'id': k, 'name': offer_name, 'present': v, 'absent': abst[k]})
            else:
                if v != 1:
                    final_attend.append({'id': k, 'name': offer_name, 'present': v, 'absent': 0})

        # Learning records
        lrs = student.learningrecord_set.all()
        ac_lrs = lrs.filter(date_created__gte=start_date, date_created__lte=end_date)
        # Scholastic detsils
        scholastic_det = ac_lrs.filter(category=1)
        scholastic_details = []
        for ent in scholastic_det:
            scholastic_recs = Scholastic.objects.filter(learning_record_id=ent.id)
            if scholastic_recs:
                scholastic_rec = scholastic_recs[0]
                schol = {
                    'subject': ent.offering.course.subject,
                    'is_present': scholastic_rec.is_present,
                    'obtained_marks': scholastic_rec.obtained_marks,
                    'total_marks': scholastic_rec.total_marks,
                    'eval_date': ent.date_created.strftime('%b %Y')
                }
                scholastic_details.append(schol)
        # Co-Scholastic Details
        coschol = ac_lrs.filter(category=2)
        coschol_details = []
        for ent in coschol:
            coschol_recs = CoScholastic.objects.filter(learning_record_id=ent.id)
            if coschol_recs:
                coschol_rec = coschol_recs[0]
                coschol_rec_final = {
                    'Attentiveness': coschol_rec.pr_attentiveness,
                    'Self Confidence': coschol_rec.pr_self_confidence,
                    'Curious': coschol_rec.pr_curious,
                    'Courteousness': coschol_rec.bh_courteousness,
                    'Positive Attitude': coschol_rec.bh_positive_attitude,
                    'Initiativeness': coschol_rec.lr_initiativeness,
                    'Responsibility': coschol_rec.lr_responsibility,
                    'Supportiveness': coschol_rec.lr_supportiveness,
                    'Emotional Connect': coschol_rec.ee_emotional_connect,
                    'Wider Perspective': coschol_rec.ee_widerperspective,
                    'Technology Exposure': coschol_rec.ee_technology_exposure,
                    'teacher': make_number_verb(ent.offering.course.grade) + ' ' + ent.offering.course.subject,
                }
                coschol_details.append(coschol_rec_final)
        trans_coschol_dict = {}
        teachers_list = []
        for record in coschol_details:
            teachers_list.append(record['teacher'])
            for key in record.keys():
                if key not in ['teacher', 'id', 'learning_record']:
                    trans_coschol_dict.setdefault(key, {})
                    trans_coschol_dict[key][record['teacher']] = record[key]
        # Unique Charactersitcs
        comments = []
        lr_uc = ac_lrs.filter(category=4).order_by('-id')
        if lr_uc:
            lr_uc = lr_uc
        for ent in lr_uc:
            uniquec_rec = UniqueC.objects.get(learning_record_id=ent.id)
            if uniquec_rec:
                comments.append(uniquec_rec.strengths)
                comments.append(uniquec_rec.weaknesses)
        # Diagnostic details
        diags = student.diagnostic_set.filter(date_created__gte=start_date, date_created__lte=end_date)
        diag_details = []
        for ent in diags:
            eval_date = ent.date_created.strftime('%b %Y')
            diag = {
                'subject': ent.offering.course.subject,
                'eval_date': eval_date,
                'agg_level': ent.aggregate_level
            }
            diag_details.append(diag)

        final_attend = final_attend[:5]

        resp = {
            'basic1': basic_details1,
            'basic2': basic_details2,
            'attendance': final_attend,
            'schol': scholastic_details,
            'diag': diag_details,
            'teachers': teachers_list,
            'coschol': trans_coschol_dict,
            'comments': comments,
            'photo': photo,
            'aytitle': aytitle
        }
        return resp


def write_pdf(context_dict, student):
    template = get_template('report_generation/report_card.html')
    today = datetime.datetime.now()
    filename = (X_clean(student.name) + str(student.id) + today.strftime('%d_%m_%y%H_%M') + '.pdf').replace(' ', '')
    context = Context(context_dict)
    html = template.render(context)
    result = open('static/uploads/student_reports/' + filename, 'wb')
    pdf = new_pisa.pisaDocument(StringIO.StringIO(
        html.encode("UTF-8")), dest=result, link_callback=fetch_resources)
    result.close()
    report = ProgressReport(student_id=student.id, report_card=result.name, generated_date=today)
    report.save()


def X_clean(line):
    line = X(line).decode('ascii', 'ignore')
    return line


def get_reports(request):
    stud_id = request.POST.get('stud_id', '')
    if stud_id:
        student = Student.objects.get(pk=stud_id)
        reports = ProgressReport.objects.filter(student_id=stud_id).order_by('-id')
        data = []
        for ent in reports:
            temp = {
                'gen_date': (ent.generated_date).strftime('%d/%b/%Y %H:%M %p'),
                'link': '/' + ent.report_card.url,
            }
            data.append(temp)
        return HttpResponse(simplejson.dumps({'data': data}), mimetype='application/json')
    else:
        return 'Invalid Request'


@csrf_exempt
def get_active_centers(request):
    centers = ''
    try:
        partner = Partner.objects.values_list("id").filter(contactperson = request.user.id)
    except:
        partner = ""
    userprofile_id =  UserProfile.objects.values_list("id",flat = True).filter(user_id = request.user.id)
    role_id = RolePreference.objects.filter(userprofile_id = userprofile_id,role_id =3,role_status = "Active",role_outcome = "Recommended")
    if request.user.is_superuser:
        centers = Center.objects.filter(status='Active').order_by('name')
    elif role_id:
        center_list = Center.objects.filter(status="Active").distinct().order_by("name")
    elif len(centers) == 0:
        centers = Center.objects.filter(status='Active').filter(Q(delivery_coordinator = request.user.id) | Q(admin_id = request.user.id) |
                                Q(field_coordinator = request.user.id) | Q(assistant_id = request.user.id) | Q(funding_partner_id= partner) |
                                Q(delivery_partner= partner) | Q(orgunit_partner=partner)).order_by('name')
    elif  has_role(request.user.userprofile, "Teacher") or has_pref_role(request.user.userprofile, "Teacher"):

        center_name = Offering.objects.filter(active_teacher__id=request.user.id).values_list("center__name",flat=True).distinct()
        centers = Center.objects.filter(status='Active',name__in = center_name).order_by('name')
    data = []
    for ent in centers:
        temp = {
            'grade_list': list(ent.student_set.filter(status='Active').values_list('grade', flat=True).distinct()),
            'center_id': ent.id,
            'center_name': ent.name,
            'ayfy': list(
                Offering.objects.filter(center_id=ent.id).values_list('academic_year__title', flat=True).distinct())
        }
        data.append(temp)
    return HttpResponse(simplejson.dumps({'data': data}), mimetype='application/json')


def download_report_card(request):
    center_id = request.POST.get('center_id')
    grade = request.POST.get('grade')
    action = request.POST.get('action')
    ay = request.POST.get('ay')

    # For zip name
    center = Center.objects.get(pk=center_id)
    offering = Offering.objects.filter(center_id=center_id, academic_year__title=ay);
    aylist = Ayfy.objects.filter(id=offering[0].academic_year_id)
    zip_name = (center.name + 'Grade:' + grade).replace(' ', '')
    curr_dir = os.getcwd()
    if center_id and grade and action:
        studs = Student.objects.filter(center_id=center_id).filter(grade=grade).filter(status='Active')
    file_list = []
    for ent in studs:
        student = ent
        if action == 'generate':
            if student:
                try:
                    report_data = get_report_data(ent.id, int(center_id), aylist[0].start_date, aylist[0].end_date,
                                              aylist[0].title)
                except:
                    report_data = get_report_data(ent.id, int(center_id))
                write_pdf(report_data, student)
        pcards = ProgressReport.objects.filter(student=student)
        if pcards:
            latest = pcards.latest('generated_date')
            file_list.append(curr_dir + '/' + latest.report_card.url)
    if len(file_list) == 0:
        resp = HttpResponse('No Progress Reports available..!', mimetype="text")
        resp['Content-Disposition'] = 'attachment; filename=NO GENERATED REPORTS AVAILABLE.txt'
        return resp
    else:
        return render_zip(file_list, zip_name)


def render_zip(file_list, zip_name):
    filenames = file_list

    curr_dir = os.getcwd()
    zip_subdir = zip_name
    zip_filename = "%s.zip" % zip_subdir

    s = StringIO.StringIO()

    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        try:
            zf.write(fpath, zip_path)
        except OSError:
            continue

    zf.close()
    resp = HttpResponse(s.getvalue(), mimetype="application/zip")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


def fetch_resources(uri, rel):
    cwd = os.getcwd()
    path = cwd + uri
    return path


# Below code can be used for rendering of report card in the browser
# Note : Also enable url in urls.py.

def report_card(request, student_id):
    student = Student.objects.get(pk=student_id)
    if student:
        report_data = get_report_data(student_id)
    # write_pdf(report_data,student)
    return render_pdf('report_generation/report_card.html', report_data)


def render_pdf(template_src, context_dict):
    filename = context_dict['basic1']['name']
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = new_pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result, link_callback=fetch_resources)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="' + filename + '"'
        return response
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


# End Reports Generation
def my_students(request, tab_id):
    tab_id = request.GET.get('tab_id')
    print "1"
    print "tab_id == ",tab_id
    return render_response(request, 'my_students.html', {'tab_id':tab_id})


from django.db import connection


@csrf_exempt
def get_uniquec(request):
    offer_id = request.POST.get('offer_id', '')
    stud_id = request.POST.get('stud_id', '')
    unique = []
    unic = UniqueC.objects.filter(learning_record__student=stud_id)
    lrs = LearningRecord.objects.filter(student=stud_id)
    # Unique C
    if unic:
        for ent4 in unic:
            temp3 = {}
            temp3['id'] = ent4.id
            temp3['strengths'] = ent4.strengths
            temp3['weaknesses'] = ent4.weaknesses
            temp3['assessed_by'] = ent4.learning_record.created_by.first_name
            temp3['date'] = (ent4.learning_record.date_created).strftime('%d/%m/%Y')
            unique.append(temp3)
    return HttpResponse(simplejson.dumps({'data': unique}), mimetype='application/json')


@csrf_exempt
def add_diagnostic(request):
    student_id = request.POST.get('student_id', '')
    offering_id = request.POST.get('offering_id', '')
    agg_level = request.POST.get('agg_level', '')
    date_created = datetime.datetime.strptime(request.POST.get('date_created'), '%m/%d/%Y')
    param_data = json.loads(request.POST.get('child_data'))
    offer = Offering.objects.get(pk=offering_id)
    diag_data = {'offering_id': offering_id,
                 'student_id': student_id,
                 'aggregate_level': agg_level,
                 'date_created': date_created, 'subject': offer.course.subject, 'grade': offer.course.grade}
    diag = Diagnostic(**diag_data)
    diag.save()
    for key, value in param_data.iteritems():
        diag_param = DiagParameter.objects.get(param_code=key)
        diag_det = {'actual_marks': value, 'parameter_id': diag_param.id, 'diagnostic_id': diag.id}
        diag_detail = DiagDetails(**diag_det)
        diag_detail.save()
    diag.aggregate_level = calculate_agg_level(diag)
    diag.save()
    return HttpResponse('Success')


def calculate_agg_level(diag):
    diag_dets = diag.diagdetails_set.all().order_by('parameter')
    print diag.id
    print diag_dets
    course = diag.offering.course
    subject = course.subject
    grade = int(course.grade)
    levels = diag_dets.values_list('parameter__level', flat=True).distinct()
    print "levels now  ", levels
    print subject
    level_percents = {}
    assigned_level = ''
    for ent in levels:
        temp_dict = diag_dets.filter(parameter__level=ent).aggregate(actual_sum=Sum('actual_marks'),
                                                                     total_sum=Sum('parameter__total_marks'))
        level_percents[ent] = float(temp_dict['actual_sum'] / temp_dict['total_sum']) * 100
    print "percent level1 ", level_percents['L1']
    # print " level2 ",level_percents['L2']
    # print " level3 ",level_percents['L3']
    # print " level4 ",level_percents['L4']
    if diag_dets:
        if subject == 'Maths':
            if grade in [5, 6]:
                if level_percents['L1'] < float(66):
                    assigned_level = 'L1'
                    print "In 5 and 6 if L1"
                else:
                    print "here "
                    if level_percents['L2'] < float(66):
                        print "In 5 and 6 if1 L1"
                        assigned_level = 'L1'
                    else:
                        print "In 5 and 6 else1 L1"
                        assigned_level = 'L2'
            elif grade in [7, 8]:
                print "grade in 7 and 8 L1"
                if level_percents['L1'] < float(60):
                    print "grade in 7 and 8 if1"
                    assigned_level = 'L1'
                else:
                    print "grade in 7 and 8 else1"
                    if level_percents['L2'] < float(66):
                        assigned_level = 'L1'
                    else:
                        if level_percents['L3'] < float(75):
                            assigned_level = 'L2'
                        else:
                            if level_percents['L4'] < float(50):
                                assigned_level = 'L3'
                            else:
                                assigned_level = 'L4'
        elif subject == 'English Foundation':
            if grade in [5, 6]:
                if level_percents['L1'] < float(66):
                    assigned_level = 'L1'
                else:
                    if level_percents['L2'] < float(66):
                        assigned_level = 'L1'
                    else:
                        if level_percents['L3'] < float(75):
                            assigned_level = 'L2'
                        else:
                            assigned_level = 'L3'
            elif grade in [7, 8]:
                if level_percents['L1'] < float(66):
                    assigned_level = 'L1'
                else:
                    if level_percents['L2'] < float(66):
                        assigned_level = 'L1'
                    else:
                        if level_percents['L3'] < float(75):
                            assigned_level = 'L2'
                        else:
                            if level_percents['L4'] < float(80):
                                assigned_level = 'L3'
                            else:
                                assigned_level = 'L4'
    print assigned_level
    return assigned_level


@csrf_exempt
def add_lr(request):
    student_id = request.POST.get('student_id', '')
    offering_id = request.POST.get('offering_id', '')
    category = LRCategory.objects.filter(name=request.POST.get('category'))[0]
    cat = request.POST.get('category')
    created_by_id = request.user.id
    child_data = json.loads(request.POST.get('child_data'))
    date_created = datetime.datetime.strptime(child_data.pop('date_created'), '%m/%d/%Y')
    lr_dict = {'student_id': student_id, 'offering_id': offering_id, 'category_id': category.id,
               'created_by_id': created_by_id, 'date_created': date_created}
    if cat == 'Scholastic':
        print child_data, lr_dict
        child_data.pop('subject');
        lr = LearningRecord(**lr_dict)
        lr.save()
        schol = Scholastic(learning_record_id=lr.id, **child_data)
        schol.save()
    elif cat == 'Co-scholastic':
        lr = LearningRecord(**lr_dict)
        lr.save()
        coschol = CoScholastic(learning_record_id=lr.id, **child_data)
        coschol.save()
    elif cat == 'Activity':
        lr = LearningRecord(**lr_dict)
        lr.save()
        act = Activity(learning_record_id=lr.id, **child_data)
        act.save()
    elif cat == 'Uniquec':
        lr = LearningRecord(**lr_dict)
        lr.save()
        uc = UniqueC(learning_record_id=lr.id, **child_data)
        uc.save()
    return HttpResponse('ok')


@csrf_exempt
def get_co_schol(request):
    stud_id = request.POST.get('stud_id', '')
    # coschola = LearningRecord.objects.filter(student=stud_id).filter(category__name='Co-scholastic')
    if has_role(request.user.userprofile, "Teacher") and not (
            has_role(request.user.userprofile, "Center Admin") or has_role(request.user.userprofile,
                                                                           "Class Assistant") or has_role(
            request.user.userprofile, "Field co-ordinator") or has_role(request.user.userprofile,
                                                                        "Delivery co-ordinator") or has_role(
            request.user.userprofile, "Partner Admin") or request.user.is_superuser):
        coschola = CoScholastic.objects.filter(learning_record__student=stud_id).filter(
            learning_record__category__name='Co-scholastic').filter(learning_record__created_by=request.user)
    else:
        coschola = CoScholastic.objects.filter(learning_record__student=stud_id).filter(
            learning_record__category__name='Co-scholastic')
    coscholastic = []
    if coschola:
        for ent2 in coschola:
            temp2 = {}
            # temp = ent2.__dict__
            temp = model_to_dict(ent2)
            temp2.update(temp)
            temp2['id'] = ent2.id
            temp2['assessed_by'] = ent2.learning_record.created_by.first_name
            temp2['date'] = (ent2.learning_record.date_created).strftime('%d/%m/%Y')

            coscholastic.append(temp2)
            #print temp2
    return HttpResponse(simplejson.dumps({'data': coscholastic}), mimetype='application/json')


@csrf_exempt
def update_cosch(request):
    rec = json.loads(request.POST.get('rec'))
    if rec:
        # co= LearningRecord.objects.get(pk=rec['id']).co_scholastic
        co = CoScholastic.objects.get(pk=rec['id'])
        co.pr_curious = rec['Curious']
        co.pr_attentiveness = rec['Attentiveness']
        co.pr_self_confidence = rec['Self confidence']
        co.lr_responsibility = rec['Responsibility']
        co.lr_supportiveness = rec['Supportiveness']
        co.lr_initiativeness = rec['Initiativeness']
        co.bh_positive_attitude = rec['Positive Attitude']
        co.bh_courteousness = rec['Courteousness']
        co.ee_widerperspective = rec['Wider Perspective']
        co.ee_emotional_connect = rec['Emotional Connect']
        co.ee_technology_exposure = rec['Technology Exposure']
        try:
            co.save()
        except e:
            pass
            #print e.message
        return HttpResponse('Success')
    return HttpResponse('No records to update')


@csrf_exempt
def update_lrs(request):
    up_list = request.POST.get('up_list')
    up_list = json.loads(up_list)
    today = datetime.datetime.now()
    #print today
    #print up_list
    if up_list:
        for ent in up_list:
            schola = Scholastic.objects.get(pk=ent['id'])
            schola.total_marks = ent['total']
            schola.obtained_marks = ent['actual']
            schola.save()
        return HttpResponse('Success')
    return HttpResponse('No records to update')


@csrf_exempt
def update_act(request):
    up_list = request.POST.get('up_list')
    up_list = json.loads(up_list)
    #print up_list
    if up_list:
        for ent in up_list:
            act = Activity.objects.get(pk=ent['id'])
            act.notes = ent['notes']
            act.grading = ent['grading']
            act.save()
        return HttpResponse('Success')
    return HttpResponse('No records to update')


@csrf_exempt
def update_uc(request):
    up_list = request.POST.get('up_list')
    up_list = json.loads(up_list)
    #print up_list
    if up_list:
        for ent in up_list:
            uc = UniqueC.objects.get(pk=ent['id'])
            uc.strengths = ent['strengths']
            uc.weaknesses = ent['weaknesses']
            uc.save()
        return HttpResponse('Success')
    return HttpResponse('No records to update')


@csrf_exempt
def update_diag(request):
    up_list = request.POST.get('up_list')
    up_list = json.loads(up_list)
    if up_list:
        for ent in up_list:
            diag_detail = DiagDetails.objects.get(pk=ent['id'])
            diag_detail.actual_marks = ent['actual_marks']
            diag_detail.save()
        diag = diag_detail.diagnostic
        diag.aggregate_level = calculate_agg_level(diag)
        diag.save()
        #print diag.aggregate_level
        return HttpResponse('Success')
    return HttpResponse('No records to update')


@csrf_exempt
def get_diagnostics(request):
    offer_id = request.POST.get('offer_id', '')
    #print "ofidd= ", offer_id
    stud_id = request.POST.get('stud_id', '')
    #print "sidd= ", stud_id
    diagnostics = []
    diag = Diagnostic.objects.filter(student=stud_id).filter(offering=offer_id)
    if diag:
        for ent in diag:
            details = ent.diagdetails_set.all().order_by('parameter__id')
            temp = model_to_dict(ent)
            temp['date_created'] = ent.date_created.strftime('%d/%m/%Y')
            temp['subject'] = ent.offering.course.subject
            details_list = []
            for ent2 in details:
                temp2 = model_to_dict(ent2)
                temp2['actual_marks'] = float(temp2['actual_marks'])
                temp2['param_name'] = ent2.parameter.name
                temp2['param_level'] = ent2.parameter.level
                temp2['total_marks'] = ent2.parameter.total_marks
                details_list.append(temp2)
            temp['details'] = details_list
            diagnostics.append(temp)
    return HttpResponse(simplejson.dumps({'data': diagnostics}), mimetype='application/json')


@csrf_exempt
def get_scholastic_lfh(request):
    data = {}
    offer_id = request.POST.get('offer_id', '')
    stud_id = request.POST.get('stud_id', '')
    lfh_data = LFH_Scholatics.objects.filter(offering_id = offer_id).filter(student_id = stud_id)
    offering_details = Offering.objects.get(id=offer_id)
    topics_details = Topic.objects.filter(course_id=offering_details.course_id).values('id','title')
    topics = list()
    for _topic in topics_details:
        topics.append({'id' : _topic['id'], 'title' : _topic['title']})
    if len(lfh_data):
        count = 0
        for _lfh_data in lfh_data:
            topic_details = Topic.objects.get(id=_lfh_data.topic_id)
            if count == 0:
                data[_lfh_data.subject] = list()
                count += 1
            data[_lfh_data.subject].append({
                "outcome" :(_lfh_data.outcome),
                "topic" : topic_details.title,
                "is_present" : _lfh_data.is_present,
                "record_type" : _lfh_data.record_type,
                "record_date" : (_lfh_data.record_date).strftime('%Y-%m-%d'),
                "subject" : _lfh_data.subject,
                "offer_id" : offer_id,
                "lfh_id" : _lfh_data.id
            })

    data['all_topics'] = topics
    return HttpResponse(simplejson.dumps({'data': data}), mimetype='application/json')


@csrf_exempt
def get_scholastic(request):
    offer_id = request.POST.get('offer_id', '')
    stud_id = request.POST.get('stud_id', '')
    stud = Student.objects.get(pk=stud_id)
    if has_role(request.user.userprofile, "Teacher") and not (
            has_role(request.user.userprofile, "Center Admin") or has_role(request.user.userprofile,
                                                                           "Class Assistant") or has_role(
            request.user.userprofile, "Field co-ordinator") or has_role(request.user.userprofile,
                                                                        "Delivery co-ordinator") or has_role(
            request.user.userprofile, "Partner Admin") or request.user.is_superuser):
        stud_center_offers = stud.center.offering_set.all().filter(id=offer_id)
    else:
        stud_center_offers = stud.center.offering_set.all()
    sel_offer = Offering.objects.get(id=offer_id)
    data = {}
    for offerc in stud_center_offers:
        enroll_studs = offerc.enrolled_students.all()
        scholastic = []
        if stud in enroll_studs:
            schola = Scholastic.objects.filter(learning_record__student=stud_id).filter(
                learning_record__offering=offerc.id).filter(learning_record__category__name='Scholastic')
            if schola:
                for ent1 in schola:
                    temp = {}
                    temp['subject'] = ent1.learning_record.offering.course.subject
                    temp['total'] = ent1.total_marks
                    temp['actual'] = float(ent1.obtained_marks)
                    temp['assessed_by'] = ent1.learning_record.created_by.first_name
                    temp['is_present'] = ent1.is_present
                    temp['date'] = (ent1.learning_record.date_created).strftime('%d/%m/%Y')
                    temp['category'] = ent1.category
                    temp['id'] = ent1.id
                    #print temp
                    scholastic.append(temp)
                #print "Scholastic"
                #print scholastic
            data[offerc.id] = {'offer': offerc.id, 'sel_offer': sel_offer.id, 'sub': offerc.course.subject,
                               'details': scholastic}
    if data:
        return HttpResponse(simplejson.dumps({'data': data}), mimetype='application/json')
    else:
        return HttpResponse('No Data Available for the Selected Offering...')


@csrf_exempt
def get_month_attend(request):
    offer_id = request.POST.get('offer_id', '')
    stud_id = request.POST.get('stud_id', '')

    offer = Offering.objects.get(id=offer_id)
    sa = SessionAttendance.objects.filter(session__offering=offer).filter(student_id=stud_id)
    month_list = []
    month_word = []
    stud_attend = []
    diff = relativedelta(offer.end_date, offer.start_date)
    for ent in range(diff.months + 1):
        dt = offer.start_date + relativedelta(months=ent)
        month_list.append(dt.month)
        month_word.append(dt.strftime('%B'))
    for ent2 in range(len(month_list)):
        sa_fil = sa.filter(session__date_start__month=month_list[ent2])
        temp = {'month': month_word[ent2], 'present': sa_fil.filter(is_present='yes').count(),
                'absent': sa_fil.filter(is_present='no').count(), 'total': sa_fil.count()}
        stud_attend.append(temp)

    return HttpResponse(simplejson.dumps({'data': stud_attend}), mimetype='application/json')

@csrf_exempt
def get_appreciation_reason(request):
    offer_id = request.POST.get('offer_id', '')
    stud_id = request.POST.get('stud_id', '')
    details = []
    stickers1 = Stickers.objects.filter(sticker_type='appreciation',for_whom ='student')
    if stickers1:
        for stic in stickers1:
            temp  = {"stic_ids": Recognition.objects.filter(offering=offer_id, object_id=stud_id, sticker = stic.id).count(), "stic_name":stic.sticker_name , "sticker_path": str(stic.sticker_path)}
            details.append(temp)
    # print "details ", details

    appreciation_reasons = AppreciationReason.objects.filter(reason_type='appreciation', for_whom ='student')
    stickers = Stickers.objects.filter(sticker_type='appreciation',for_whom ='student')
    # print "stickers ",stickers
    # print "appreciation_reasons ", appreciation_reasons[1]
    if appreciation_reasons:
        for app_reason in appreciation_reasons:
            temp ={'reason':app_reason.reason, 'appreciation_id': app_reason.id}
            details.append(temp)
    if stickers:
        for sticker in stickers:
            temp = {'sticker_name':sticker.sticker_name , 'sticker_path':str(sticker.sticker_path) ,'sticker_id': sticker.id }
            details.append(temp)
    # print "details ", details
    return HttpResponse(simplejson.dumps({'data': details}), mimetype='application/json')




@csrf_exempt
def get_activities(request):
    offer_id = request.POST.get('offer_id', '')
    stud_id = request.POST.get('stud_id', '')
    activity = []
    # lrs = LearningRecord.objects.filter(student=stud_id)
    act = Activity.objects.filter(learning_record__student=stud_id)
    # act = lrs.filter(category__name='Activity')
    if act:
        for ent3 in act:
            temp2 = {}
            temp2['id'] = ent3.id
            temp2['notes'] = ent3.notes
            temp2['grading'] = ent3.grading
            temp2['assessed_by'] = ent3.learning_record.created_by.first_name
            temp2['date'] = (ent3.learning_record.date_created).strftime('%d/%m/%Y')
            activity.append(temp2)
    return HttpResponse(simplejson.dumps({'data': activity}), mimetype='application/json')


@csrf_exempt
def get_off_stud(request):
    start_time = time.clock()
    start_wall = time.time()
    centerid = request.POST.get('center_id', None)
    ay_id  = request.POST.get('ay_id', None)
    offer_count = 0
    offerings = []
    ay_list = []
    offer = []
    current_ay = []
    if centerid:
        center_access = Center.objects.filter(
            Q(id=centerid) & Q(admin=request.user) | Q(assistant=request.user) | Q(field_coordinator=request.user) | Q(
                delivery_coordinator=request.user))
        if request.user.is_superuser or len(center_access) > 0:
            offer = Offering.objects.filter(center_id=centerid).exclude(academic_year=None)
        else:
            offering_list = Session.objects.values_list('offering_id', flat=True).filter(teacher=request.user).distinct()
            offer = Offering.objects.filter(center_id=centerid, id__in=offering_list).exclude(academic_year=None)
        board = Center.objects.get(id=centerid).board
        ay_objs = Ayfy.objects.filter(board=board, types='Academic Year')
        if ay_id:
            current_ay = ay_id
        else:
            try:
                 current_ay_obj = Ayfy.objects.get(start_date__year = datetime.datetime.now().year, board = board)
            except:
                last_year = (datetime.datetime.now()+relativedelta(years=-1)).year
                current_ay_obj = Ayfy.objects.get(start_date__year = last_year, board = board)
            current_ay = current_ay_obj.id

        for ay in ay_objs:
            ay_temp = {
                "ay_id": ay.id,
                "ay_title": ay.title,
                "ay_board": ay.board
            }
            ay_list.append(ay_temp)

        offer_count = offer.count()
        if offer_count == 0:
            return HttpResponse('No Running offerings for the selected center.')
    else:
        temp = []
        board_list = []
        ay_data = []
        " board = Offering.objects.filter(active_teacher=request.user)[1].course.board_name"
        offering_data = Offering.objects.filter(active_teacher=request.user)
        for off in offering_data:
            board_frmcourse = Course.objects.filter(id=off.course_id)
            for board in board_frmcourse:
                board_list.append(board.board_name)
        for board in board_list:
            ay_objs = Ayfy.objects.filter(board=board, types='Academic Year')
            try:
                current_ay = Ayfy.objects.get(board=board, start_date__year=datetime.datetime.now().year,
                                            types='Academic Year').id
            except:
                ay_year = Ayfy.objects.values_list('start_date').filter(board = board).order_by('-start_date')[0]
                ay_year = ay_year[0].strftime('%Y')
                current_ay = Ayfy.objects.get(board=board, start_date__year=ay_year,
                                            types='Academic Year').id
                
            for ayData in ay_objs:
                ay_data.append(ayData)
        for ay in ay_data:
            ay_temp = {
                "ay_id": ay.id,
                "ay_title": ay.title,
                "ay_board": ay.board
            }
            ay_list.append(ay_temp)
        user_sessions = Session.objects.filter(teacher=request.user)
        for sess in user_sessions:
            """offer_list = Offering.objects.filter(id = sess.offering.id , active_teacher_id = request.user)
            for off in offer_list :
                temp.append(off)"""
            temp.append(sess.offering)
        offer = set(temp)
        offer_count = len(offer)
        if offer_count == 0:
            return HttpResponse('No Running course under your course list.')
    if offer_count != 0:
        for ent in offer:
            stud_list = []
            center = Center.objects.get(id=int(ent.center_id))
            center_id_list = []
            center_list = []
            if center.board[:4] == "JACB" and ent.course.subject[:3] == "LFH" and (center.name[-4:] == "Hira" or center.name[-4:] == "Moti"):
                if (center.name[-4:]) == "Hira":
                    center_list.append(center.name)
                    center_list.append(str(center.name[:-7])+" " + "-" + " " + "Moti")
                    center_id_list = Center.objects.values_list("id",flat=True).filter(name__in = center_list)
                elif (center.name[-4:]) == "Moti":
                    center_list.append(center.name)
                    center_list.append(str(center.name[:-7])+" " + "-" + " " + "Hira")
                    center_id_list = Center.objects.values_list("id",flat=True).filter(name__in = center_list)
            if center_id_list:
                enroll_stud = ent.enrolled_students.all().exclude(center=None).filter(center__id__in=center_id_list).distinct()
            else:
                enroll_stud = ent.enrolled_students.all().exclude(center=None).filter(center__id=ent.center_id).distinct()
            for ent1 in enroll_stud:
                if ent1.dob:
                    stud_dob = ent1.dob.strftime('%d/%m/%Y')
                else:
                    stud_dob = ""
                if ent1.photo:
                    if not 'static' in str(ent1.photo):
                        photo_url = 'static/uploads/student/' + ent1.photo.url
                    else:
                        photo_url = ent1.photo.url

                else:
                    photo_url = "static/images/noimage.jpg"
                # getting attendance month wise
                sa = SessionAttendance.objects.filter(session__offering=ent).filter(student=ent1)
                # sa_list = get_month_attend(ent,sa)
                sa_list = []
                stud = {
                    "stud_id": ent1.id,
                    "stud_name": ent1.name,
                    "stud_grade": ent1.grade,
                    "stud_dob": stud_dob,
                    "stud_gender": ent1.gender,
                    "stud_sch_rollno": ent1.school_rollno,
                    "stud_photo": photo_url,
                    "stud_fath_occ": ent1.father_occupation,
                    "stud_moth_occ": ent1.mother_occupation,
                    "stud_status": ent1.status,
                    "stud_center": ent1.center.name,
                    "stud_att": sa_list
                }
                stud_list.append(stud)
                
            offer_status = 'Pending'

            if str(ent.status) =='running' and (ent.active_teacher is None or ent.active_teacher==''):
                offer_status = 'Backfill' 
            elif str(ent.status) =='running' and (ent.active_teacher is not None or ent.active_teacher !=''):
                offer_status = 'Running' 

            temp = {
                "offer_id": ent.id,
                "offer_name": str(ent.id) + ' - '  + str(ent.course.grade) + 'th ' + str(ent.course.subject) + ' - ' +  offer_status,
                "offer_stud_count": ent.enrolled_students.count(),
                "offer_ay_id": ent.academic_year.id,
                "offer_en_stud": stud_list
            }
            offerings.append(temp)
        return HttpResponse(simplejson.dumps(
            {"offer_count": offer_count, "offerings": offerings, "ay_list": ay_list, 'current_ay': current_ay}),
                            mimetype='application/json')
    else:
        return HttpResponse('No data')


@csrf_exempt
def get_diag_params(request):
    offer = request.POST.get('offer')
    stud = request.POST.get('stud')
    if offer:
        offering = Offering.objects.get(pk=offer)
        if offering.course.subject in ['Maths', 'English Foundation']:
            param_list = []
            params = DiagParameter.objects.filter(grade=offering.course.grade).filter(subject=offering.course.subject)
            for par in params:
                param_list.append(model_to_dict(par))
            return HttpResponse(simplejson.dumps({'param_list': param_list}), mimetype='application/json')
        else:
            return HttpResponse('At this point of time we are not capturing Diagnostics for Science..')


@login_required
@csrf_exempt
def lr_bulk_upload(request):
    user = request.user
    version_list = DiagParameter.objects.values_list('version', flat=True).distinct()
    if user.is_superuser:
        user_centers = Center.objects.filter(status='Active')

    elif has_role(request.user.userprofile, "Teacher"):
        center_id_teacher = Offering.objects.values_list("center_id",flat=True).filter(active_teacher_id = request.user.id,status = "running").distinct()
        user_centers = Center.objects.filter(id__in = center_id_teacher,status='Active')

    elif  has_role(request.user.userprofile, "Center Admin")  or has_role(request.user.userprofile, "Field co-ordinator") or has_role(request.user.userprofile, "Delivery co-ordinator") or has_role(request.user.userprofile, "Partner Account Manager"):
        db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
        user=settings.DATABASES['default']['USER'],
        passwd=settings.DATABASES['default']['PASSWORD'],
        db=settings.DATABASES['default']['NAME'],
        charset="utf8",
        use_unicode=True)
        try:
            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query = "select partner_id  as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
            dict_cur.execute(query)
            partner_id = [str(each['value']) for each in dict_cur.fetchall()]
            partner_id.sort()
            partner_id= tuple(partner_id)
            partner_id= partner_id[0]

            db.close()
            dict_cur.close()
        except:
            pass

        user_centers = Center.objects.filter(Q(delivery_coordinator_id=user.id) | Q(field_coordinator_id=user.id) | Q(admin_id=user.id)|Q(delivery_partner_id__in=partner_id)|Q(funding_partner_id__in=partner_id) & Q(status='Active'))
    else :
        user_centers=""
        
    save_user_activity(request, 'Viewed Page:My Student - Bulk Upload Assessments', 'Page Visit')
    ays = Ayfy.objects.filter(board__isnull = False).order_by('-title').values_list('title', flat=True).distinct()
    return render_response(request, "lr_bulk_upload.html", {'centers': user_centers, 'versions': ["V-2"], 'ays':ays})


@csrf_exempt
def get_offers(request):
    offer_list = []
    print(request.POST)
    try:
        requestParams = json.loads(request.body)
        print(requestParams)
        centers = requestParams.get('centers', None)
        ay = requestParams.get('ay', None)
        
        
        if centers is not None:
            for center_id in centers:
                center = Center.objects.get(pk=int(center_id))
                ay_id = Ayfy.objects.filter(title=ay, board=center.board).values_list('id', flat=True)[0]
                print(ay_id)
                offers = Offering.objects.filter(center=center).filter(academic_year=ay_id).filter(status='running').order_by('course__board_name', 'course__grade', 'course__subject')

                if request.user.is_superuser:
                    offers = center.offering_set.all().filter(status__in=('Running','Pending'), academic_year=ay_id) 
                elif has_role(request.user.userprofile, "Teacher"):
                    offers = center.offering_set.all().filter(status__in=('Running','Pending'),active_teacher_id = request.user.id)
                else:
                    offers = center.offering_set.all().filter(status__in=('Running','Pending'))
                
                for offer in offers:
                    if not offer.active_teacher_id and str(offer.status)=='running':
                        name = center.name + '--'+ offer.course.grade + ' ' + offer.course.subject +'--Backfill'
                    else:
                        name = center.name + '--'+ offer.course.grade + ' ' + offer.course.subject +'--'+str(offer.status)
                    temp = {'id': offer.id, 'name': name}
                    offer_list.append(temp)
            return HttpResponse(simplejson.dumps(offer_list), mimetype='application/json')
    except Exception as e:
        print("check kyc  e", e)
        traceback.print_exc()
        return HttpResponse("Error")


@csrf_exempt
def get_temp(request):
    try:
        # center = request.GET.get('center', '')
        # center_name = Center.objects.get(id = center).name
        offer = request.GET.get('offer', '')
        offer_list = offer.split(",")
        temp_type = int(request.GET.get('type', ''))
        schol_type = request.GET.get('scol_type', '')
        version = request.GET.get('version', '')
        sheet = ''
        if temp_type == 1:
            sheet = 'Scholastic'
        elif temp_type == 2:
            sheet = 'Coscholastic'
        elif temp_type == 3:
            sheet = 'Diagnostic'
        sheet_name = sheet
        wb = Workbook()
        for offer in offer_list:
            offering = Offering.objects.get(id = offer)
            offer_name = '%.15s' % offering.center.name + '_' + '%.15s' % offering.course.subject + "_" + offering.course.grade
            try:
                ws = wb.add_sheet( str(offer_name))
            except:
                ws = wb.add_sheet( str(offering.center.id)+ "(" +str(offer)+")")
            ws = create_xls_header_type(sheet, ws, offer, version)
            res_objs, file_name = get_offer_data(offer, temp_type, schol_type)
            ws = write_data_to_xls(ws, res_objs)
            fname = sheet_name+'.xls'
            response = HttpResponse(mimetype="application/ms-excel")
            response['Content-Disposition'] = 'attachment; filename=%s' % fname

            wb.save(response)

        return response
    except Exception as e:
        print(e)
        traceback.print_exc()
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


def create_xls_header_type(type, ws, offer, version):
    style0 = xlwt.easyxf('font: name Times New Roman size 20, color-index black, bold on')
    if type == 'Scholastic':
        headers_list = ['Student Id', 'Offering Id', 'Course Name', 'Student Name', 'Category', 'Total Marks',
                        'Obtained Marks', 'Is Present(Yes/No)']
    elif type == 'Coscholastic':
        headers_list = ['Student Id', 'Offering Id', 'Course Name', 'Student Name', 'Curious', 'Attentiveness',
                        'Self Confidence', 'Responsibility', 'Supportiveness', 'Initiativeness', 'Positive Attitude',
                        'Mannerism', 'Wider Perspective', 'Emotional Connect', 'Technology Exposure']
    elif type == 'Diagnostic':
        offr = Offering.objects.get(pk=offer)
        headers_list = get_header(offr, version)

    for i, header in enumerate(headers_list):
        ws.write(0, i, header, style0)

    return ws


def get_header(offr, version):
    headers_list = ['Student Id', 'Offering Id', 'Course Name', 'Student Name', 'Aggregate level', 'category']
    grd = offr.course.grade
    sub = offr.course.subject
    param_list = DiagParameter.objects.filter(subject=sub).filter(grade=grd).filter(version=version).values_list(
        'param_code', flat=True)
    headers_list = headers_list + list(param_list)
    return headers_list


def write_data_to_xls(ws, result_objs):
    i = 1
    for k, result_obj in enumerate(result_objs):
        student = result_obj[0]
        if student['aggregate_level']:
            xls_values_list = [student['stud_id'], student['offer_id'], student['offer_name'], student['stud_name'],student['aggregate_level'],student['category']]
        else:
            xls_values_list = [student['stud_id'], student['offer_id'], student['offer_name'], student['stud_name'],student['category']]
        j= 1
        for j, xls_value in enumerate(xls_values_list):
            ws.write(i, j, xls_value)

        i = i + 1
    return ws


def get_offer_data(offer, temp_type, schol_type):
    offer = Offering.objects.get(pk=offer)
    en_stud = offer.enrolled_students.all()
    offer_name = offer.course.grade + ' ' + offer.course.subject
    center = Center.objects.get(pk=offer.center_id)
    res_objs = []
    for ent in en_stud:
        stud = {
            'stud_id': ent.id,
            'offer_id': offer.id,
            'offer_name': offer_name,
            'stud_name': ent.name
        }
        if temp_type == 1:
            stud['category'] = schol_type
            stud['aggregate_level'] = ''
        elif temp_type == 3:
            category=Diagnostic.objects.filter(Q(student_id=ent.id ) & Q (offering_id=offer.id))

            if category:
                category=category[0].category
            else:
                category = ''
            stud.update({'category':category, 'aggregate_level':'Lx'})
        else:
            stud['category'] = ''
            stud['aggregate_level'] = ''
        res_objs.append([stud])
    file_name = center.name + '_' + offer_name
    return res_objs, file_name


@csrf_exempt
def process_excel(request):
    uploadFlag = request.POST.get('uploadFlag', '')
    input_excel = request.FILES['filee']
    offer = request.POST.get('offer', '')
    offer_list = offer.split(",")
    print('offer_list', offer_list)
    typee = request.POST.get('type', '')
    asses_date = request.POST.get('asses_date')
    version = request.POST.get('version')
    book = xlrd.open_workbook(file_contents=input_excel.read())
    page = 0
    data_list = []
    hdr = []
    resultList = []
    stud_list = Student.objects.values_list('id', flat=True)
    for offer in offer_list:
        sheet = book.sheet_by_index(page)
        
        # try:
        #     if int(offer) != int(sheet.cell_value(1, 1)):
        #         return HttpResponse('Please select matching file for particular center and offering')
        # except:
        #     return HttpResponse('No record present in file')
        if typee == str(1):
            testTypes = Scholastic._meta.get_field('category').choices
            testTypes = list(testTypes)
            testTypes_list = []
            for i in range(len(testTypes)):
                testTypes_list.append(testTypes[i][0])
            hdr = ['id', 'offer', 'offer_name', 'student', 'category', 'total', 'actual', 'is_present']
            if sheet.cell_value(0, 4) == 'Category':
                resultList = preview_data(8, hdr, sheet, stud_list, typee, testTypes_list,data_list,resultList)
                data_list = resultList[0]
                rowValue = str(resultList[1])
                colValue = str(resultList[2])
                if len(data_list) != 0:
                    up_type = 'Scholastic'
                else:
                    result = 'It seems, your file either have Incorrect data or missing fields or no data available at  \' row ', rowValue, ' col ', colValue, ' \' . Please check again..'
                    return HttpResponse(result)
            else:
                return HttpResponse('Hey!..It seems that you have uploaded an Incorrect template.. Try again..')
        elif typee == str(2):
            hdr = ['id', 'offer', 'offer_name', 'student', 'curious', 'attentiveness', 'self_confidence', 'responsibility',
                'supportiveness', 'initiativeness', 'positive_attitude', 'mannerism', 'wider_perspective',
                'emotional_connect', 'technology_exposure']
            if sheet.cell_value(0, 4) == 'Curious':
                resultList = preview_data(15, hdr, sheet, stud_list, typee, None,data_list,resultList)
                data_list = resultList[0]
                rowValue = str(resultList[1])
                colValue = str(resultList[2])
                if len(data_list) != 0:
                    up_type = 'Coscholastic'
                else:
                    result = 'It seems, your file either have Incorrect data or missing fields or no data available at  \' row ', rowValue, ' col ', colValue, ' \' . Please check again..'
                    return HttpResponse(result)
            else:
                return HttpResponse('Hey!..It seems that you have uploaded an Incorrect template.. Try again..')
        elif typee == str(3):
            if sheet.cell_value(0, 4) == 'Aggregate level':
                offr = Offering.objects.get(pk=offer)
                hdr = get_header(offr, version)
                if offr.course.subject in ['Maths', 'English Foundation']:
                    resultList = preview_data_list(sheet.ncols, hdr, sheet, stud_list,data_list,resultList)
                    data_list = resultList[0]
                    rowValue = str(resultList[1])
                    colValue = str(resultList[2])
                    if len(data_list) != 0:
                        up_type = 'Diagnostic'
                    else:
                        result = 'It seems, your file either have Incorrect data or missing fields or no data available at  \' row ', rowValue, ' col ', colValue, ' \' . Please check again..'
                        return HttpResponse(result)
                else:
                    return HttpResponse(
                        'At this point, we are capturing diagnostics for Maths,English Foundation. Please check the course again.. ')
            else:
                return HttpResponse('Hey!..It seems that you have uploaded an Incorrect template.. Try again..')
        nrows = sheet.nrows
        if typee == str(1) or typee == str(3):
            if uploadFlag != 'Yes':
                for i in range(1, nrows):
                    student_id = sheet.cell_value(i, 0)
                    offering_id = sheet.cell_value(i, 1)
                    # print "offering_id ", offering_id
                    student = Student.objects.get(pk=student_id)
                    lrs = student.learningrecord_set.all()
                    if typee == str(1):
                        category_type = sheet.cell_value(i, 4)
                        print "category_type ", category_type
                        scholastic_details = lrs.filter(category=1, offering=offering_id)
                        for ent in scholastic_details:
                            records = Scholastic.objects.filter(learning_record_id=ent.id, category=category_type)
                            print "scholastic_records ", records
                            if records:
                                return HttpResponse('File already present do you want to update the file')
                    elif typee == str(3):
                        category_type = sheet.cell_value(i, 5)
                        print "category_type ", category_type
                        records = student.diagnostic_set.filter(offering=offering_id, category=category_type)
                        """for ent in diagnostic_details :
                                records = ent.objects.filter(category = category_type)
                                print "scholastic_records ",records """
                        print "diagnostic_records ", records
                        # for ent in records:
                        # print "diag nos ",ent.category," id ",ent.id," st_id ",ent.student_id," offer_id ",ent.offering_id
                        if records:
                            return HttpResponse('File already present do you want to update the file')
        page+=1
    print(data_list)
    return HttpResponse(simplejson.dumps(
        {'type': up_type, 'data': data_list, 'hdr': hdr, 'asses_date': asses_date, 'uploadFlag': uploadFlag}),
                        mimetype='application/json')


def preview_data(cols, hdr, sheet, stud_list, typee, testTypes_list,data_list,resultList):
    data_list = data_list
    resultList = resultList
    _row_index = 1
    _i = 1

    
    for row_index in range(1, sheet.nrows):
        discard_row = False
        student_id = sheet.cell_value(row_index, 0)
        if student_id in stud_list:
            data = {}
            if typee == '1':
                for i in range(cols):
                    cellValue = sheet.cell_value(row_index, i)
                    if i > 4 and i < 7:
                        if cellValue == '':
                            discard_row = True
                            data_list[:] = []
                            resultList = [data_list, row_index, i + 1]
                            print('1')
                            return resultList
                        else:
                            data[hdr[i]] = int(sheet.cell_value(row_index, i))
                    else:
                        # cellValue = str(cellValue)
                        # print "printngg cellvalue schooooo",cellValue," ",i
                        if sheet.cell_value(row_index, i) == '' or (
                                i == 4 and str(sheet.cell_value(row_index, i)) not in testTypes_list) or (i == 7 and (
                                not str(sheet.cell_value(row_index, i)).replace(' ', '').isalpha() or str(
                            sheet.cell_value(row_index, i)).lower().strip() not in ('yes', 'no'))):
                            discard_row = True
                            data_list[:] = []
                            resultList = [data_list, row_index, i + 1]
                            print('2')
                            return resultList
                        else:
                            data[hdr[i]] = sheet.cell_value(row_index, i)
                if discard_row == False:
                    data_list.append(data)
                    _row_index = row_index
                    _i = 1
            else:
                for i in range(cols):
                    if i > 3:
                        cellValue = sheet.cell_value(row_index, i)
                        cellValue = str(cellValue)
                        print(row_index, cols, cellValue)
                        if cellValue == '' or not cellValue.replace(' ', '').isalpha():
                            discard_row = True
                            data_list[:] = []
                            resultList = [data_list, row_index, i + 1]
                            print('3')
                            return resultList
                        else:
                            data[hdr[i]] = sheet.cell_value(row_index, i)
                    else:
                        if sheet.cell_value(row_index, i) == '':
                            discard_row = True
                            data_list[:] = []
                            resultList = [data_list, row_index, i + 1]
                            print('4')
                            return resultList
                        else:
                            data[hdr[i]] = sheet.cell_value(row_index, i)
                if discard_row == False:
                    data_list.append(data)
                    _row_index = row_index
                    _i = 1

    resultList = [data_list, _row_index, _i + 1]
    print('5')
    return resultList


def preview_data_list(cols, hdr, sheet, stud_list,data_list,resultList):
    data_list = data_list
    resultList = resultList
    for row_index in range(1, sheet.nrows):
        discard_row = False
        student_id = sheet.cell_value(row_index, 0)
        if student_id in stud_list:
            data = OrderedDict()
            for i in range(cols):
                if i > 5:
                    if sheet.cell_value(row_index, i) == '' or sheet.cell_value(row_index, i) not in (0, 1):
                        discard_row = True
                        data_list[:] = []
                        resultList = [data_list, row_index, i + 1]
                        return resultList
                    else:
                        data[hdr[i]] = sheet.cell_value(row_index, i)
                else:
                    if sheet.cell_value(row_index, i) == '':
                        discard_row = True
                        data_list[:] = []
                        resultList = [data_list, row_index, i + 1]
                        return resultList
                    else:
                        data[hdr[i]] = sheet.cell_value(row_index, i)
            if discard_row == False:
                data_list.append(data)
    resultList = [data_list, row_index, i + 1]
    return resultList


@csrf_exempt
def bulk_schol(request):
    try:
        up_data = request.POST.get('up_data', '')
        up_data_p = json.loads(up_data)
        asses_date = request.POST.get('asses_date')
        category = LRCategory.objects.filter(name='Scholastic')[0]
        today = datetime.datetime.now()
        uploadFlag = request.POST.get('uploadFlag', '')
        if uploadFlag == 'Yes':
            update_list = update_file_records(request, up_data_p, asses_date, today, category)
            msg = '%s learning records updated , %s learning records created and %s records rejected ' % (update_list[0], update_list[2],update_list[1])
            return HttpResponse(msg)
        created_recs = []
        teacher_id = ''
        for i, ent in enumerate(up_data_p):
            # creat_date  = datetime.datetime.strptime(ent['dte'],'%d/%m/%Y')
            creat_date = datetime.datetime.strptime(asses_date, '%m/%d/%Y')
            # getting offering for teacher
            if i == 0:
                teach_offer = Offering.objects.get(pk=ent['offer'])
                teachers = teach_offer.session_set.all().filter(date_start__lte=today).exclude(teacher=None).order_by('date_start').reverse()
                if len(teachers)>0: 
                    teacher_id = teachers[0].teacher.id
                else: teacher_id = request.user.id

            lr_dict = {'student_id': ent['id'], 'offering_id': ent['offer'], 'category_id': category.id,
                    'created_by_id': teacher_id, 'date_created': creat_date}
            child_dict = {'category': ent['category'], 'total_marks': ent['total'], 'obtained_marks': ent['actual'],
                        'is_present': ent['is_present']}
            lr = LearningRecord(**lr_dict)
            lr.save()
            schol = Scholastic(learning_record_id=lr.id, **child_dict)
            schol.save()
            created_recs.append(schol.id)
        if created_recs:
            tmp = str(len(created_recs))
            msg = '%s learning records created' % tmp
        else:
            msg = "No records created"
        return HttpResponse(msg)
    except Exception as e:
        print(e)
        traceback.print_exc()


@csrf_exempt
def bulk_coschol(request):
    up_data = request.POST.get('up_data', '')
    up_data_p = json.loads(up_data)
    asses_date = request.POST.get('asses_date')
    category = LRCategory.objects.filter(name='Co-scholastic')[0]
    created_recs = []
    today = datetime.datetime.now()
    teacher_id = ''
    for i, ent in enumerate(up_data_p):
        # creat_date  = datetime.datetime.strptime(ent['dte'],'%d/%m/%Y')
        creat_date = datetime.datetime.strptime(asses_date, '%m/%d/%Y')
        if i == 0:
            teach_offer = Offering.objects.get(pk=ent['offer'])
            print "print teahcer name ", \
            teach_offer.session_set.all().filter(date_start__lte=today).order_by('date_start').reverse()[0]
            teacher_id = teach_offer.session_set.all().filter(date_start__lte=today).exclude(teacher=None).order_by(
                'date_start').reverse()[0].teacher.id

        lr_dict = {'student_id': ent['id'], 'offering_id': ent['offer'], 'category_id': category.id,
                   'created_by_id': teacher_id, 'date_created': creat_date}
        child_dict = {'pr_attentiveness': ent['attentiveness'], 'pr_self_confidence': ent['self_confidence'],
                      'pr_curious': ent['curious'], 'bh_courteousness': ent['mannerism'],
                      'bh_positive_attitude': ent['positive_attitude'], 'lr_initiativeness': ent['initiativeness'],
                      'lr_responsibility': ent['responsibility'], 'lr_supportiveness': ent['supportiveness'],
                      'ee_widerperspective': ent['wider_perspective'], 'ee_emotional_connect': ent['emotional_connect'],
                      'ee_technology_exposure': ent['technology_exposure']}
        lr = LearningRecord(**lr_dict)
        lr.save()
        coschol = CoScholastic(learning_record_id=lr.id, **child_dict)
        coschol.save()
        created_recs.append(coschol.id)
    if created_recs:
        tmp = str(len(created_recs))
        msg = '%s learning records created' % tmp
    else:
        msg = "No records created"
    return HttpResponse(msg)


@csrf_exempt
def bulk_diag(request):
    up_data = request.POST.get('up_data', '')
    up_data_p = json.loads(up_data)
    asses_date = request.POST.get('asses_date')
    ver = request.POST.get('version')
    uploadFlag = request.POST.get('uploadFlag', '')
    if uploadFlag == 'Yes':
        update_list = update_diag_file_records(up_data_p, asses_date, ver)
        print "returned"
        msg = '%s learning records updated, %s learning records created %s records rejected ' % (update_list[0], update_list[2],update_list[1])
        return HttpResponse(msg)
    created_recs = []
    for ent in up_data_p['data']:
        # creat_date  = datetime.datetime.strptime(ent['Assessment Date'],'%d/%m/%Y')
        creat_date = datetime.datetime.strptime(asses_date, '%m/%d/%Y')
        ent_cpy = ent
        stud_id = ent_cpy.pop('Student Id')
        offer_id = ent_cpy.pop('Offering Id')
        offer = Offering.objects.get(pk=offer_id)
        grade = offer.course.grade
        sub = offer.course.subject
        agg_level = ent_cpy.pop('Aggregate level')
        category = ent_cpy.pop('category')
        print "category  ", category
        del ent_cpy['Course Name'], ent_cpy['Student Name']
        diag_dict = {'student_id': stud_id, 'offering_id': offer_id, 'grade': grade, 'subject': sub,
                     'aggregate_level': agg_level, 'date_created': creat_date, 'category': category}
        diag = Diagnostic(**diag_dict)
        diag.save()
        for k, v in ent_cpy.items():
            p_obj = DiagParameter.objects.get(param_code=k, version=ver)
            dd_dict = {'diagnostic_id': diag.id, 'parameter_id': p_obj.id, 'actual_marks': v}
            dd_obj = DiagDetails(**dd_dict)
            dd_obj.save()
        created_recs.append(diag.id)
        diag.aggregate_level = calculate_agg_level(diag)
        diag.save()
    msg = '%s Records Created Successfully' % str(len(created_recs))
    return HttpResponse(msg)


# ------------------------------------   End Student Module -------------------------------#


# ------------------------------------   Volunteer Management -----------------------------#

@login_required
def volunteer_search(request):
    is_partner=False
    partner=''
    if request.user.is_superuser or has_role(request.user.userprofile, "Delivery co-ordinator") :
        save_user_activity(request, 'Viewed Page:Dashboard - Volunteer Dashboard', 'Page Visit')
        return render_response(request, 'volunteer_mgmt.html', {})

    elif  has_role(request.user.userprofile, "School Admin"):
        save_user_activity(request, 'Viewed Page:Dashboard - Volunteer Dashboard', 'Page Visit')
        school_admin = Partner.objects.get(contactperson=request.user)
        return render_response(request, 'volunteer_mgmt.html', {"is_school_admin":True, "is_show_volunteer" : True, 'partner' : school_admin})
    
    elif  has_role(request.user.userprofile, "Partner Account Manager"):
        save_user_activity(request, 'Viewed Page:Dashboard - Volunteer Dashboard', 'Page Visit')

        return render_response(request, 'volunteer_mgmt.html', {})
    elif request.user.partner_set.all().count()>0 and request.user.partner_set.all()[0].status=="Approved":
        profile = UserProfile.objects.get(user=request.user)
        if profile:
            if len(profile.role.filter(name = "Partner Admin")) > 0 or len(profile.role.filter(name = "OUAdmin")): 
                partner = Partner.objects.get(contactperson=request.user)
                is_partner=True
            else :
                partner = None
        save_user_activity(request, 'Viewed Page:Dashboard - Volunteer Dashboard', 'Page Visit')
        is_funding_partner = ""
        if is_partner:
            try:
                is_funding_partner = Partner.objects.values("partnertype").filter(contactperson=request.user,partnertype=3)
            except:
                is_funding_partner = ""
        else:
            is_funding_partner = ""

        return render_response(request, 'volunteer_mgmt.html', {'partner':partner,'is_partner':is_partner,"active":1,"is_funding_partner":is_funding_partner})
    else:
        return HttpResponse('You are not authorized')


def parse_datatable_request_params(request):
    request_params = {
        'search_columns': {}, 'order_by_columns': {}, 'search_value': '',
        'start': 0, 'per_page_length': 20, 'searchable_fields': [],
        'download_excel': "false"
    }

    data = request.POST
    for key, value in data.iteritems():
        order_column_re = re.search('order\[(\d+)\]\[column\]', key)
        search_column_re = re.search('columns\[(\d+)\]\[search\]\[value\]', key)
        searchable_column_re = re.search('columns\[(\d+)\]\[searchable\]', key)

        if search_column_re and value:
            column_index = re.findall(search_column_re.re, key)
            if not column_index:
                continue
            column_index = column_index[0]
            field = data['columns[{}][data]'.format(column_index)]
            search_columns = request_params['search_columns']
            search_columns[field] = value
        elif order_column_re and value:
            order_index = re.findall(order_column_re.re, key)
            if not order_index:
                continue
            order_index = order_index[0]
            column_index = value
            field = data['columns[{}][data]'.format(column_index)]
            order_by_columns = request_params['order_by_columns']
            order_by_columns[field] = data['order[{}][dir]'.format(order_index)]
        elif key == 'search[value]':
            request_params['search_value'] = value
        elif key == 'start':
            request_params['start'] = value
        elif key == 'length':
            request_params['per_page_length'] = value
        elif searchable_column_re and value == 'true':
            column_index = re.findall(searchable_column_re.re, key)
            if not column_index:
                continue
            column_index = column_index[0]
            field = data['columns[{}][data]'.format(column_index)]
            request_params['searchable_fields'].append(field)
        elif key == "download_excel":
            request_params["download_excel"] = value

    return request_params


def get_base_query():
    as_seperator = " as "
    auth_user = [
        'id', 'username', 'email', 'first_name', 'last_name',
        'last_login', 'date_joined', 'is_active'
    ]

    web_userprofile = [
        'id{}up_id'.format(as_seperator), 'status', 'skype_id',
        'self_eval', 'pref_medium', 'city', 'phone', 'referencechannel_id',
        'profile_completion_status', 'remarks', 'evd_rep',
        'code_conduct', 'computer', 'trainings_complete',
        'review_resources', 'from_date', 'to_date', 'pref_days',
        'pref_slots', 'short_notes','age','profession','referred_user_id',
        'profile_complete_status',
        'time_zone','pref_subjects','pref_center','internet_connection',
        'internet_speed','webcam','headset','trail_class','hrs_contributed',
        'purpose','old_reference_channel','evd_rep_meet','referer','country',
        'state','secondary_email','gender','fbatwork_id','unavailability_reason',
        'fb_member_token','organization_complete_status'
    ]

    web_role = ['name']
    userprofile_role = ['role_id']
    web_rolepreference = ['role_status', 'role_outcome', 'role_onboarding_status', 'availability', 'recommended_date']
    web_offering = ['status{}is_active_teacher'.format(as_seperator)]
    web_center = ['name{}center_name'.format(as_seperator)]
    web_referencechannel = ['name{}reference_channel'.format(as_seperator)]
    web_volunteerprocessing = ['outcome {}vp_outcome'.format(as_seperator)]

    field_table_alias_name = OrderedDict()
    field_table_alias_name.update(dict((i.strip(), "U") for i in auth_user))
    field_table_alias_name.update(dict((i.strip(), "UP") for i in web_userprofile))
    field_table_alias_name.update(dict((i.strip(), "R") for i in web_role))
    field_table_alias_name.update(dict((i.strip(), "UR") for i in userprofile_role))
    field_table_alias_name.update(dict((i.strip(), "RP") for i in web_rolepreference))
    field_table_alias_name.update(dict((i.strip(), "WOF") for i in web_offering))
    field_table_alias_name.update(dict((i.strip(), "WC") for i in web_center))
    field_table_alias_name.update(dict((i.strip(), "RC") for i in web_referencechannel))
    field_table_alias_name.update(dict((i.strip(), "VP") for i in web_volunteerprocessing))

    select_fields_list = []
    for k, v in field_table_alias_name.iteritems():
        if k in web_role or k in userprofile_role or k in web_rolepreference:
            select_fields_list.append("GROUP_CONCAT({}.{} SEPARATOR ',') as {}".format(v, k, k))
        else:
            select_fields_list.append("{}.{}".format(v, k))

    select_fields = ",".join(select_fields_list)
    base_query = ["SELECT {} FROM auth_user U".format(select_fields)]

    left_join_tables = [
        "LEFT JOIN web_userprofile UP ON U.id = UP.user_id",
        "LEFT JOIN web_userprofile_role UR ON UP.id = UR.userprofile_id",
        "LEFT JOIN web_role R ON UR.role_id = R.id",
        "LEFT JOIN web_rolepreference RP ON RP.userprofile_id = UR.userprofile_id AND RP.role_id = UR.role_id",
        "LEFT JOIN web_offering WOF ON U.id = WOF.active_teacher_id",
        "LEFT JOIN web_center WC ON WOF.center_id = WC.id",
        "LEFT JOIN web_referencechannel RC ON UP.referencechannel_id = RC.id",
        "LEFT JOIN web_volunteerprocessing VP ON UP.user_id = VP.user_id"
    ]

    base_query.append(" ".join(left_join_tables))
    base_query = " ".join(base_query)

    # Generating Field Alias mapping dict
    field_alias_to_db = {}
    for k, v in field_table_alias_name.iteritems():
        if as_seperator not in k:
            continue

        db_field, alias_name = k.split(as_seperator)
        dict_value = field_table_alias_name.pop(k)
        field_table_alias_name[alias_name] = dict_value
        field_alias_to_db[alias_name.strip()] = db_field.strip()

    return base_query, field_table_alias_name, field_alias_to_db


def get_total_matched_count(cursor, final_query):
    total_count = 0

    # replacing select fields by count to get the matching count
    re_search = re.search("select (.*?)from ", final_query, re.IGNORECASE)
    if not re_search:
        return total_count

    matched_string = "".join(re.findall(re_search.re, final_query))
    count_query = final_query.replace(matched_string, 'count(*) as count ')

    # Remove Limit
    re_search = re.search("limit \d+,\d+", count_query, re.IGNORECASE)
    if re_search:
        matched_string = "".join(re.findall(re_search.re, count_query))
        count_query = count_query.replace(matched_string, '')

    try:
        cursor.execute(count_query)
    except Warning:
        pass
    data = cursor.fetchall()
    total_count = len(data)
    return total_count


def generate_volunteerdb_excel(user_id, response_data):
    resp_data = {"excel_link": ""}
    download_path = ""
    for index, file_path in enumerate(settings.STATICFILES_DIRS):
        if index != 0:
            continue

        download_path = os.path.join(file_path, 'downloads')
        if not os.path.isdir(download_path):
            os.mkdir(download_path)

    if not download_path:
        return resp_data

    wb = Workbook()

    ws = wb.add_sheet("first_sheet")

    style0 = xlwt.easyxf('font: name Times New Roman size 20, color-index black, bold on')
    # Please Maintian the same order as in volunteer_mgmt.html template DataTable columns
    headers_list = [
       {"name": "ID", "data": "id"},
            {"name": "User Name", "data": "username"},
            {"name": "Email", "data": "email"},
            {"name": "First Name", "data": "first_name"},
            {"name": "Last Name", "data": "last_name"},
            {"name": "Is Active", "data": "is_active"},
            {"name": "Language", "data": "pref_medium"},
            {"name": "City", "data": "city"},
            {"name": "Phone", "data": "phone"},
            {"name": "Center", "data": "center_name"},
            {"name": "Preferred Roles", "data": "prefered_roles"},
            {"name": "Role Status", "data": "role_status"},
            {"name": "Role Outcome", "data": "role_outcome"},
            {"name": "Active Teacher", "data": "is_active_teacher"},
            {"name": "Role Completion Status", "data": "role_onboarding_status"},
            {"name": "Recommended Date", "data": "recommended_date"},
            {"name": "Skype ID", "data": "skype_id"},
            {"name": "Reference Channel", "data": "reference_channel"},
            {"name": "Orientation", "data": "evd_rep"},
            {"name": "Computer", "data": "computer"},
            {"name": "Availability", "data": "availability"},
            {"name":"Preferred Subjects","data":"pref_subjects"},
            {"name": "Preferred Day","data":"pref_days"},
            {"name": "Preferred Slots","data":"pref_slots"},
            {"name": "Available From", "data": "from_date"},
            {"name": "Available Till", "data": "to_date"},
            {"name": "Last Login", "data": "last_login"},
            {"name": "Joined Date", "data": "date_joined"},
            {"name": "Short Notes", "data": "short_notes"},
            {"name": "Age", "data": "age"},
            {"name": "Profession", "data": "profession"},
            {"name": "Referred user id", "data": "referred_user_id"},
            {"name": "VP Outcome", "data": "vp_outcome"},
            {"name": "Remarks","data":"remarks"},
               ]

    for i, header_info in enumerate(headers_list):
        header = header_info.get("name")
        ws.write(0, i, header, style0)

    roles_fields = ["prefered_roles", "role_status", "role_outcome", "role_onboarding_status", "availability",
                    "recommended_date"]
    for i, data in enumerate(response_data.get("aaData", [])):
        for j, header_info in enumerate(headers_list):
            header = header_info.get("name")
            field = header_info.get("data")
            value = data.get(field, "")
            if field in roles_fields:
                if field == "prefered_roles":
                    value = ",".join("{}: {}".format(i['role_id'], i['name']) for i in value)
                else:
                    value = "\n".join("{}: {}".format(k, v) for k, v in value.iteritems())
            if type(value) == list:
                value = ",".join(value)
            ws.write(i + 1, j, value)

    fname = os.path.join(download_path, 'volunteerdb_data_{}.xls'.format(user_id))
    if os.path.isfile(fname):
        os.remove(fname)

    download_link = fname.replace(settings.PROJECT_DIR, "")
    wb.save(fname)
    return {"excel_link": download_link}


@login_required
@csrf_exempt
def get_vol_data(request):
    try:
        if request.user.is_superuser or (request.user.partner_set.all().count()>0 and request.user.partner_set.all()[0].status=="Approved") or has_role(request.user.userprofile, "Partner Account Manager") or has_role(request.user.userprofile, "School Admin") or has_role(request.user.userprofile, "Delivery co-ordinator") or has_role(request.user.userprofile, "vol_admin"):
            search_params = parse_datatable_request_params(request)

            db = evd_getDB()
            users_cur = db.cursor(MySQLdb.cursors.DictCursor)

            equal_to_fields = ["id","referred_user_id"]
            date_fields = ["last_login", "date_joined", "from_date", "to_date", "recommended_date"]
            boolean_fields = [
                "is_active", "profile_completion_status", "self_eval",
                "computer", "evd_rep", "trainings_complete",
                "code_conduct", "review_resources", "availability",
                "evd_rep_meet", "trail_class","headset",
                "webcam","internet_connection",
            ]
            text_fields = ["short_notes", "age","profession"]
            params_to_db_field = {'prefered_roles': 'name'}
            fields_values = {
                "is_active_teacher": {
                    "true": "running",
                    "false": ["pending", "completed"]
                }
            }

            response_data = {"iTotalRecords": 0, "iTotalDisplayRecords": 0, "aaData": []}
            start = time.clock()
            data = []
            data_dict = {}

            _base_query, field_table_alias_name, field_alias_to_db = get_base_query()
            base_query = [_base_query]

            newline_seperator = "</br>"
            if search_params.get("download_excel", 'false') == 'true':
                newline_seperator = "\n"

            search_value_query = ''
            if search_params.get("search_value"):
                value = search_params.get("search_value").strip()
                search_query = []
                for db_field in search_params.get("searchable_fields"):
                    if db_field in search_params.get("search_columns"):
                        continue
                    db_field = params_to_db_field.get(db_field, db_field)
                    table_alias_name = field_table_alias_name.get(db_field)
                    if not table_alias_name:
                        continue

                    search_value = value
                    if db_field in boolean_fields:
                        if value.lower().startswith('t'):
                            search_value = 1
                        elif value.lower().startswith('f'):
                            search_value = 0

                    if db_field == 'is_active_teacher':
                        if value.lower().startswith('t'):
                            search_value = fields_values.get(db_field, {}).get("true")
                        elif value.lower().startswith('f'):
                            search_value = fields_values.get(db_field, {}).get("false")

                    alias_name = db_field
                    db_field = field_alias_to_db.get(db_field, db_field)
                    if isinstance(search_value, list):
                        search_value = ",".join("\"{}\"".format(i) for i in search_value)
                        search_query.append("{}.{} in ({})".format(table_alias_name, db_field, search_value))
                    elif db_field in equal_to_fields or alias_name in equal_to_fields:
                        search_query.append("{}.{} = \"{}\"".format(table_alias_name, db_field, search_value))
                    else:
                        search_query.append("{}.{} like \"%{}%\"".format(table_alias_name, db_field, search_value))

                if search_query:
                    search_value_query = "({})".format(" OR ".join(search_query))

            search_columns_query = ''
            if search_params.get("search_columns"):
                search_query = []
                search_columns = search_params.get("search_columns", {})
                for db_field, value in search_columns.iteritems():
                    db_field = params_to_db_field.get(db_field, db_field)
                    table_alias_name = field_table_alias_name.get(db_field)
                    if not table_alias_name:
                        continue
                    if db_field in boolean_fields:
                        if value.lower().startswith('t'):
                            value = 1
                        else:
                            value = 0

                    if db_field == 'is_active_teacher':
                        if value.lower().startswith('t'):
                            value = fields_values.get(db_field, {}).get("true")
                        elif value.lower().startswith('f'):
                            value = fields_values.get(db_field, {}).get("false")

                    alias_name = db_field
                    db_field = field_alias_to_db.get(db_field, db_field)
                    if isinstance(value, list):
                        value = ",".join("\"{}\"".format(i) for i in value)
                        search_query.append("{}.{} in ({})".format(table_alias_name, db_field, value))
                    elif db_field in equal_to_fields or alias_name in equal_to_fields:
                        search_query.append("{}.{} = \"{}\"".format(table_alias_name, db_field, value))
                    else:
                        search_query.append("{}.{} like \"%{}%\"".format(table_alias_name, db_field, value))

                if search_query:
                    search_columns_query = " AND ".join(search_query)
                    
            partner_is_user = False
            if request.user.partner_set.all().count()>0 and not has_role(request.user.userprofile, "School Admin"):
                ref_ids= ReferenceChannel.objects.filter(partner_id=request.user.partner_set.all()[0].id).values_list('id',flat=True)
                reff_ids = ','.join(map(str,ref_ids))
                if len(ref_ids) >0:
                    partner_is_user=True
                    base_query.append(" WHERE RC.id in ('"+reff_ids+"')")

            # For school admin
            if has_role(request.user.userprofile, "School Admin"):
                school_admin_details = Partner.objects.filter(contactperson=request.user)
                partner_is_user = True
                ref_ids = ReferenceChannel.objects.filter(partner_id=school_admin_details[0].id).values_list('id',flat=True)
                reff_ids = ','.join(map(str,ref_ids))
                if len(ref_ids) >0:
                    base_query.append(" WHERE RC.id in ('"+reff_ids+"')")

            if search_value_query or search_columns_query:
                if not partner_is_user:
                    base_query.append(" WHERE ")
                    search_final_query = " AND ".join(i for i in [search_value_query, search_columns_query] if i)
                else:
                    search_final_query = " AND "
                    search_final_query += "".join(i for i in [search_value_query, search_columns_query] if i)
                    
                base_query.append(search_final_query)
            
            base_query.append(' AND is_active=1 ')
            base_query.append("GROUP BY U.id")
            if search_params.get("order_by_columns"):
                order_column = search_params["order_by_columns"]
                if order_column:
                    db_field = order_column.keys()[0]
                    table_alias_name = field_table_alias_name.get(db_field)
                    db_field = field_alias_to_db.get(db_field, db_field)
                    order_by = order_column[order_column.keys()[0]]
                    base_query.append("ORDER BY {}.{} {}".format(table_alias_name, db_field, order_by))

            start_offset = search_params.get("start", 0)
            page_limit = search_params.get("per_page_length", "-1")
            if page_limit != "-1":
                base_query.append("LIMIT {},{};".format(start_offset, page_limit))

            final_query = " ".join(base_query)
            # print "uuu==",final_query
            response_data["iTotalRecords"] = get_total_matched_count(users_cur, final_query)
            response_data["iTotalDisplayRecords"] = response_data["iTotalRecords"]
            try:
                users_cur.execute(final_query)
            except Warning:
                pass
            users = users_cur.fetchall()
            # for user in users :
            #     # print "******* User ", user
            #     is_testing_user = False
            #     if user['role_status']=='Active' and user['role_outcome']=='Recommended':
            #         print "Active & Recommended"
            #         print "User ID ", user['id']
            #         try:
            #             for pref_role in user['prefered_roles']:
            #                 if  pref_role['name'] == 'Teacher':
            #                     user['center_name'] = Offering.objects.filter(active_teacher__id=user['id']).values_list("center__name",flat=True).distinct()
            #         except AttributeError as err:
            #             is_testing_user = True
            #             pass
            #     else:
            #         user['center_name']= None
            #     print "user - center_name ", is_testing_user, user['center_name']
            
            data = response_data["aaData"]
            for user_index, user in enumerate(users):
                user_profile_id = ''
                roles_data = []
                role_status_dict = {}
                role_outcome_dict = {}
                role_onboarding_status_dict = {}
                role_recommended_date_dict = {}
                role_availability_dict = {}

                removed_none = dict((k, "") for k, v in user.iteritems() if v is None)
                if removed_none:
                    user.update(removed_none)

                for boolean_field in boolean_fields:
                    if user.has_key(boolean_field):
                        if boolean_field == "availability":
                            user[boolean_field] = ",".join(
                                ['True' if x == '1' else 'False' for x in user[boolean_field].split(',')])
                        else:
                            b_value = user[boolean_field]
                            if b_value == 0:
                                user[boolean_field] = 'False'
                            else:
                                user[boolean_field] = 'True'

                for text_field in text_fields:
                    if user.has_key(text_field):
                        t_value = user[text_field]
                        if search_params.get("download_excel", 'false') == 'true':
                            user[text_field] = t_value
                        elif t_value:
                            user[text_field] = "<div style='width:300px;overflow:auto'>" + t_value + "</div>"
                used = set()
                
                role_id = []
                role_status = []
                role_outcome = []
                # temp = user.get('role_id', "").split(',')
                # print "temprole_id",temp
                # for idx in range(0, len(temp), 2):
                #     role_id.append(temp[idx])
                # print "role_id",role_id
            
                role_id = ([i.strip() for i in user.get('role_id', "").split(',')])
                role_ids = [x for x in role_id if x not in used and (used.add(x) or True)]
                uses=set()
                role_name =([i.strip() for i in user.get('name', "").split(',')])
                role_names=[x for x in role_name if x not in uses and (uses.add(x) or True)]
                temp = user.get('role_status', "").split(',')
                for idx in range(0, len(temp), len(role_ids)):
                    role_status.append(temp[idx])
                temp = user.get('role_outcome', "").split(',')
                for idx in range(0,len(temp),len(role_ids)):
                    role_outcome.append(temp[idx])
                # role_outcome = [i.strip() for i in user.get('role_outcome', "").split(',')]
                # role_status = [i.strip() for i in user.get('role_status', "").split(',')]
                role_onboarding_status = [i.strip() for i in user['role_onboarding_status'].split(',')]
                role_recommended_date = [i.strip() for i in user['recommended_date'].split(',')]
                role_availability = [i.strip() for i in user['availability'].split(',')]

                for index, role_id in enumerate(role_ids):
                    roles_dict = {}
                    if not role_id:
                        continue

                    roles_dict["role_id"] = role_id
                    if len(role_names) >= (index + 1):
                        roles_dict["name"] = role_names[index]
                    else:
                        roles_dict["name"] = ""

                    if len(role_outcome) >= (index + 1):
                        role_outcome_dict[role_id] = role_outcome[index]
                    else:
                        role_outcome_dict[role_id] = ""

                    if len(role_status) >= (index + 1):
                        role_status_dict[role_id] = role_status[index]
                    else:
                        role_status_dict[role_id] = ""

                    if len(role_onboarding_status) >= (index + 1):
                        role_onboarding_status_dict[role_id] = role_onboarding_status[index]
                    else:
                        role_onboarding_status_dict[role_id] = ""

                    if len(role_recommended_date) >= (index + 1):
                        role_recommended_date_dict[role_id] = role_recommended_date[index]
                    else:
                        role_recommended_date_dict[role_id] = ""

                    if len(role_availability) >= (index + 1):
                        role_availability_dict[role_id] = role_availability[index]
                    else:
                        role_availability_dict[role_id] = ""

                    if roles_dict:
                        roles_data.append(roles_dict)
                    # print "roles_data",roles_data
                dates_fields = {}
                select_fields = field_table_alias_name.keys()
                record = dict((k, user[k]) for k in select_fields if user.has_key(k) and k not in date_fields)
                for date_field in date_fields:
                    if not user.has_key(date_field):
                        continue
                    if isinstance(user[date_field], datetime.datetime):
                        dates_fields[date_field] = user[date_field].isoformat(" ").split(".")[0]
                    else:
                        dates_fields[date_field] = ""

                if dates_fields:
                    record.update(dates_fields)
                # print "record",record
                if record.has_key('is_active_teacher'):
                    values_dict = fields_values.get('is_active_teacher', {})
                    db_value = record['is_active_teacher']
                    final_value = "False"
                    if db_value:
                        m_value = [k for k, v in values_dict.iteritems() if db_value in v]
                        if m_value:
                            final_value = "".join(m_value).capitalize()
                    record['is_active_teacher'] = final_value

                record['prefered_roles'] = roles_data
                record['role_status'] = role_status_dict
                record['role_outcome'] = role_outcome_dict
                record['role_onboarding_status'] = role_onboarding_status_dict
                record['recommended_date'] = role_recommended_date_dict
                record['availability'] = role_availability_dict
                
                record['center_name'] = None
                is_active_role = False
                is_role_outcome_recommended = False

                for role_id, role_status in (record['role_status']).items():
                    if role_id == '1' and role_status == 'Active':
                        is_active_role = True
                        break
                
                for role_id, role_outcome in (record['role_outcome']).items():
                    if role_id == '1' and role_outcome == 'Recommended':
                        is_role_outcome_recommended = True
                        break
                if is_active_role and is_role_outcome_recommended:
                    try:
                        
                        record['center_name'] =list(Offering.objects.filter(Q(active_teacher__id=record['id']) & Q(status="running")).values_list("center__name",flat=True).distinct())
                    except Offering.DoesNotExist:
                        pass
                data.append(record)
                # print "dssssssssssssssssata",data
            # print("response data =================================", response_data)
            users_cur.close()
            if search_params.get("download_excel", 'false') == 'true':
                excel_reponse_data = generate_volunteerdb_excel(request.user.id, response_data)
                dump_json = simplejson.dumps(excel_reponse_data)
            else:
                dump_json = simplejson.dumps(response_data)
            return HttpResponse(dump_json, mimetype='application/json')
        else:
            return HttpResponse('Unauthorized Request')
    except Exception as e:
        print("Error reason =============================", e)
        print("Error at line no ---------------------------------", traceback.format_exc())


@login_required
@csrf_exempt
def get_master_db(request):
    sheet_name = 'master_vol_db'
    wb = Workbook()

    ws = wb.add_sheet("first_sheet")
    ws = create_xls_header(ws)
    res_objs = get_master_vol_db_data(request)
    ws = write_data_to_xl(ws, res_objs)
    fname = '%s.xls' % sheet_name
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % fname

    wb.save(response)

    return response


def create_xls_header(ws):
    style0 = xlwt.easyxf('font: name Times New Roman size 20, color-index black, bold on')
    headers_list = ['ID', 'User Name', 'Email', 'First Name', 'Last Name', 'Last Login', 'Joined Date', 'Activation',
                    'Profile Completion Status', 'Language', 'Preferred Roles', 'Status', 'Skype ID', 'Self Eval',
                    'City', 'Phone', 'Reference Channel ID', 'Remarks', 'Orientation', 'Code Conduct',
                    'Computer Trainings Complete', 'Review Resources', 'Available From', 'Available Till',
                    'Preferred Days', 'Preferred Slots', 'Short Notes', 'Age', 'Profession', 'Referred user id',
                    'Profile Complete Status','Time Zone','Pref Subjects','Pref Center','Internet Connection',
                    'Internet Speed', 'Webcam', 'Headset','Trail Class','Hrs Contributed', 'Purpose','Old Ref Channel',
                    'Evd Rep Meet', 'Referer','Country','State','Secondary Email','Gender','Fb Atwork','Unavailability Reason',
                    'FB Member Token', 'Organization Complete Status' ]
    for i, header in enumerate(headers_list):
        ws.write(0, i, header, style0)

    return ws


def write_data_to_xl(ws, result_objs):
    i = 1

    for k, result_obj in enumerate(result_objs):
        # print 'age ',result_obj['age']
        xls_values_list = [result_obj['id'], result_obj['username'], result_obj['email'], result_obj['first_name'], \
                           result_obj['last_name'], result_obj['last_login'], \
                            result_obj['date_joined'], result_obj['is_active'], result_obj['profile_completion_status'],
                           result_obj['pref_medium'], \
                           result_obj['pref_roles__name'], result_obj['status'], result_obj['skype_id'],
                           result_obj['self_eval'], result_obj['city'], result_obj['phone'], \
                           result_obj['referencechannel_id'], result_obj['remarks'], result_obj['evd_rep'],
                           result_obj['code_conduct'], result_obj['computer'], \
                           result_obj['review_resources'], result_obj['from_date'], result_obj['to_date'], \
                           result_obj['pref_days'], result_obj['pref_slots'], result_obj['short_notes'], \
                           result_obj['age'], result_obj['profession'], result_obj['referred_user_id'], \
                           result_obj['profile_complete_status'],result_obj['time_zone'], \
                           result_obj['pref_subjects'],result_obj['pref_center'],result_obj['internet_connection'], \
                           result_obj['internet_speed'],result_obj['webcam'], result_obj['headset'], \
                           result_obj['trail_class'], result_obj['hrs_contributed'], result_obj['purpose'], \
                           result_obj['old_reference_channel'], result_obj['evd_rep_meet'],result_obj['referer'],\
                           result_obj['country'],result_obj['state'],result_obj['secondary_email'], \
                           result_obj['gender'],result_obj['fbatwork_id'],result_obj['unavailability_reason'],
                           result_obj['fb_member_token'],result_obj['organization_complete_status']]

        for j, xls_value in enumerate(xls_values_list):
            ws.write(i, j, xls_value)

        i = i + 1
    return ws


def get_master_vol_db_data(request):
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                         user=settings.DATABASES['default']['USER'],
                         passwd=settings.DATABASES['default']['PASSWORD'],
                         db=settings.DATABASES['default']['NAME'],
                         charset="utf8",
                         use_unicode=True)
    userp_cur = db.cursor(MySQLdb.cursors.DictCursor)
    roles_cur = db.cursor()
    role_pref_cur = db.cursor()
    prefered_roles_cur = db.cursor()
    users_cur = db.cursor(MySQLdb.cursors.DictCursor)
    users =[]

    if request.user.is_superuser or has_role(request.user.userprofile, "Delivery co-ordinator") :
        start = time.clock()
        data = []
        data_dict = {}
        users_cur.execute(
            "select id,username,email,first_name,last_name,last_login,date_joined,is_active from auth_user order by id")
        users = list(users_cur.fetchall())
        for user in users:
            prefered_roles_cur.execute(
                "select name from web_role where id in (SELECT role_id FROM `web_userprofile_pref_roles` where userprofile_id=" + str(
                    user['id']) + ")")
            prefered_role_list = [item[0] for item in prefered_roles_cur.fetchall()]
            prefered_roles = ",".join(prefered_role_list)
            usr_dict = user
            usr_dict['is_active'] = 'True' if usr_dict['is_active'] == 1 or usr_dict['is_active'] == 'True' else 'False'
            sorter = ['id', 'username', 'email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active',
                      'profile_completion_status', 'pref_medium', 'pref_roles__name', 'status', 'skype_id', 'self_eval',
                      'city', 'phone', 'referencechannel', 'remarks', 'evd_rep', 'code_conduct', 'computer',
                      'trainings_complete', 'review_resources', 'from_date', 'to_date', 'pref_days', 'pref_slots',
                      'short_notes', 'age', 'profession', 'referred_user_id','profile_complete_status',
                        'time_zone','pref_subjects','pref_center','internet_connection',
                        'internet_speed','webcam','headset','trail_class','hrs_contributed',
                        'purpose','old_reference_channel','evd_rep_meet','referer','country',
                        'state','secondary_email','gender','fbatwork_id','unavailability_reason',
                        'fb_member_token','organization_complete_status']
            try:
                userp = None
                userp_cur.execute(
                    "select status,skype_id,self_eval,pref_medium,city,phone,referencechannel_id,profile_completion_status,remarks,evd_rep,code_conduct,"\
                    "computer,trainings_complete,review_resources,from_date,to_date,pref_days,pref_slots,short_notes,age,profession,referred_user_id ," \
                    "profile_complete_status,time_zone,pref_subjects,pref_center,internet_connection,internet_speed,webcam,headset,"\
                    "trail_class,hrs_contributed,purpose,old_reference_channel,evd_rep_meet,referer,country,state," \
                    "secondary_email,gender,fbatwork_id,unavailability_reason,fb_member_token,organization_complete_status " \
                    "from web_userprofile where id=" + str(user['id']) )
                userp_rcd = userp_cur.fetchall()

                if len(userp_rcd) > 0:
                    userp = userp_rcd[0]
                    usr_dict.update(userp)
                    usr_dict['self_eval'] = 'True' if usr_dict['self_eval'] == 1 or usr_dict[
                        'self_eval'] == 'True' else 'False'
                    usr_dict['profile_completion_status'] = 'Filled' if usr_dict['profile_completion_status'] == 1 or \
                                                                        usr_dict[
                                                                            'profile_completion_status'] == 'Filled' else 'Not Filled'
                    usr_dict['evd_rep'] = 'True' if usr_dict['evd_rep'] == 1 or usr_dict[
                        'evd_rep'] == 'True' else 'False'
                    usr_dict['code_conduct'] = 'True' if usr_dict['code_conduct'] == 1 or usr_dict[
                        'code_conduct'] == 'True' else 'False'
                    usr_dict['computer'] = 'True' if usr_dict['computer'] == 1 or usr_dict[
                        'computer'] == 'True' else 'False'
                    usr_dict['trainings_complete'] = 'True' if usr_dict['trainings_complete'] == 1 or usr_dict[
                        'trainings_complete'] == 'True' else 'False'
                    usr_dict['review_resources'] = 'True' if usr_dict['review_resources'] == 1 or usr_dict[
                        'review_resources'] == 'True' else 'False'
                    # print 'prefered rolesss  ',prefered_roles
                    usr_dict['pref_roles__name'] = prefered_roles
                    usr_dict['last_login'] = str(usr_dict['last_login'])
                    usr_dict['date_joined'] = str(usr_dict['date_joined'])
                    usr_dict['from_date'] = str(usr_dict['from_date'])
                    usr_dict['to_date'] = str(usr_dict['to_date'])
                    usr_dict['to_date'] = str(usr_dict['to_date'])
                    usr_dict['age'] =  usr_dict['age']
                    usr_dict['profession'] = usr_dict['profession']
                    usr_dict['referred_user_id'] = str(usr_dict['referred_user_id'])
                    usr_dict['profile_complete_status'] = usr_dict['profile_complete_status']
                    usr_dict['time_zone'] = usr_dict['time_zone']
                    usr_dict['pref_subjects'] = usr_dict['pref_subjects']
                    usr_dict['pref_center'] = usr_dict['pref_center']
                    usr_dict['internet_connection'] = str(usr_dict['internet_connection'])
                    usr_dict['internet_speed'] = usr_dict['internet_speed']
                    usr_dict['webcam'] = usr_dict['webcam']
                    usr_dict['headset'] = usr_dict['headset']
                    usr_dict['trail_class'] = usr_dict['trail_class']
                    usr_dict['hrs_contributed'] = usr_dict['hrs_contributed']
                    usr_dict['purpose'] = usr_dict['purpose']
                    usr_dict['old_reference_channel'] =usr_dict['old_reference_channel']
                    usr_dict['evd_rep_meet'] = usr_dict['evd_rep_meet']
                    usr_dict['referer'] = usr_dict['referer']
                    usr_dict['country'] = usr_dict['country']
                    usr_dict['state'] = usr_dict['state']
                    usr_dict['secondary_email'] = usr_dict['secondary_email']
                    usr_dict['gender'] = usr_dict['gender']
                    usr_dict['fbatwork_id'] = usr_dict['fbatwork_id']
                    usr_dict['unavailability_reason'] = usr_dict['unavailability_reason']
                    usr_dict['fb_member_token'] = usr_dict['fb_member_token']
                    usr_dict['organization_complete_status'] = usr_dict['organization_complete_status']
                    # usr_dict[''] = str(usr_dict[''])

                else:
                    usr_dict['profile_completion_status'] = usr_dict['pref_medium'] = usr_dict['pref_roles__name'] = \
                    usr_dict['status'] = usr_dict['skype_id'] = \
                        usr_dict['self_eval'] = usr_dict['city'] = usr_dict['phone'] = usr_dict['referencechannel_id'] = \
                    usr_dict['remarks'] = usr_dict['evd_rep'] = \
                        usr_dict['code_conduct'] = usr_dict['computer'] = usr_dict['trainings_complete'] = usr_dict[
                        'review_resources'] = usr_dict['from_date'] = \
                        usr_dict['to_date'] = usr_dict['pref_days'] = usr_dict['pref_slots'] = usr_dict[
                        'short_notes'] = usr_dict['age'] = usr_dict['profession'] = usr_dict['referred_user_id']= \
                        usr_dict['profile_complete_status'] =usr_dict['time_zone']= usr_dict['pref_subjects'] = \
                        usr_dict['pref_center'] = usr_dict['internet_connection'] = usr_dict['internet_speed'] = usr_dict['webcam'] = usr_dict['headset'] = \
                        usr_dict['trail_class'] = usr_dict['hrs_contributed'] = usr_dict['purpose'] = \
                        usr_dict['old_reference_channel'] = usr_dict['evd_rep_meet'] = usr_dict['referer'] = \
                        usr_dict['country'] =  usr_dict['state'] = usr_dict['secondary_email'] = usr_dict['gender'] = \
                        usr_dict['fbatwork_id'] = usr_dict['unavailability_reason'] = usr_dict['fb_member_token'] = \
                        usr_dict['organization_complete_status'] = ""
            except:
                traceback.print_exc()
                print 'exception block'
                pass
        endd = time.clock()
        userp_cur.close()
        roles_cur.close()
        role_pref_cur.close()
        prefered_roles_cur.close()
        users_cur.close()
        print "%.2gs" % (endd - start)
    return users


@csrf_exempt
@login_required
def get_vol_details(request):
    # if request.user.is_superuser:
    vol_id = request.POST.get('id', '')
    if vol_id:
        user = User.objects.get(id=vol_id)
        user_p = UserProfile.objects.filter(user=user)
    if vol_id and len(user_p) > 0:
        user = User.objects.get(id=vol_id)
        user_p = UserProfile.objects.filter(user=user)
        user_p_dict = user_p.values('id', 'dicussion_outcome', 'status', 'profile_complete_status', 'remarks',
                                    'picture', 'city', 'skype_id', 'phone', \
                                    'short_notes', 'pref_days', 'from_date', 'pref_slots', 'to_date',
                                    'unavailability_reason', 'pref_subjects','age','profession','referred_user_id',
                                    'self_eval','pref_medium','referencechannel_id','profile_completion_status',
                                    'evd_rep','code_conduct', 'computer', 'trainings_complete',
                                    'review_resources','pref_days','age', 'profession', 'referred_user_id',
                                    'time_zone', 'pref_center', 'internet_connection',
                                    'internet_speed', 'webcam', 'headset', 'trail_class', 'hrs_contributed',
                                    'purpose', 'old_reference_channel', 'evd_rep_meet', 'referer', 'country',
                                    'state', 'secondary_email', 'gender', 'fbatwork_id',
                                    'fb_member_token', 'organization_complete_status'
                                    )

        unavilable_reasons_list = [x for x in dict(UserProfile._meta.get_field('unavailability_reason').choices)]
        pref_sub_list = user_p_dict[0]['pref_subjects'].split(";")
        unavail_list_ = ["Interested, but not now", "Interested, but Occupied with Professional commitments",
                         "Interested, but Occupied with Personal commitments"]
        availability = 0
        follow_up_date = None

        pref_roles = user_p[0].pref_roles.all()
        roles = {}
        for pref_role in pref_roles:
            roles[pref_role.name] = {}

            # vol_processing
            vp_obj, created = VolunteerProcessing.objects.get_or_create(user=user, role=pref_role)
            roles[pref_role.name]["vp_outcome"] = vp_obj.outcome.replace(" ", "_")

            if pref_role.name == "Teacher":
                role = Role.objects.filter(name='Teacher')
                onboarding = user_p[0].rolepreference_set.filter(role=role)
                availability = RolePreference.objects.get(id=onboarding[0].id).availability if onboarding else False
                follow_up_date = RolePreference.objects.get(id=onboarding[0].id).follow_up_date if onboarding else None

            role_pref = user_p[0].rolepreference_set.filter(role=pref_role)
            if role_pref:
                roles[pref_role.name]['onboard_stat'] = role_pref[0].role_onboarding_status
                roles[pref_role.name]['status'] = role_pref[0].role_status
                if roles[pref_role.name]['status'] == 'Active':
                    center_obj = Offering.objects.filter(active_teacher=user).values_list('center__name', flat=True)
                    if center_obj:
                        roles[pref_role.name]['center'] = center_obj[0]
                else:
                    roles[pref_role.name]['center'] = ''
                roles[pref_role.name]['outcome'] = role_pref[0].role_outcome.replace(" ", "_")
                roles[pref_role.name]['remarks'] = role_pref[0].notes
        if len(user_p_dict) != 0:
            user_p_dict = user_p_dict[0]
            user_p_dict['to_date'] = (user_p_dict['to_date']).strftime('%Y-%m-%d')
            user_p_dict['from_date'] = (user_p_dict['from_date']).strftime('%Y-%m-%d')
            user_p_dict['username'] = user.username
            user_p_dict['name'] = user.first_name + " " + user.last_name
            user_p_dict['email']=user.email
            channel=list(ReferenceChannel.objects.filter(id=user_p_dict['referencechannel_id']).values_list('name', flat=True))
            user_p_dict['Reference_Channel_name']=channel

            if user_p_dict['picture'] == '':
                user_p_dict['picture'] = '/static/images/user_small.png'

            user_p_dict['roles'] = roles
            preferred_slots=user_p_dict['pref_slots']
            print "preferred_slots",preferred_slots
            avail_data = {
                'availability': availability,
                'follow_up_date': follow_up_date.strftime('%d/%m/%Y') if follow_up_date else follow_up_date,
                'unavilable_reasons_list': unavilable_reasons_list,
                'pref_sub_list': pref_sub_list,
                'preferred_slots':preferred_slots,
                'unavail_list_': unavail_list_
            }
            user_p_dict['availability_data'] = avail_data
            # print "user_p_dict",user_p_dict
            return HttpResponse(simplejson.dumps(user_p_dict), mimetype='application/json')
    else:
        return HttpResponse('ID does not Exist')


# else:
# return HttpResponse('Unauthorized request')

@login_required
def update_vol_status(request):
    # print "status_form",request
    if request.user.is_superuser or has_role(request.user.userprofile, "Delivery co-ordinator"):
        vol_id = request.POST.get('id', '')
        # print "vol Id : " + str(vol_id)
        role = request.POST.get('role', '')
        role_status = request.POST.get('role_status', '')
        o_come = request.POST.get('o_come', '').replace("_", " ")
        role_outcome = o_come
        computer= request.POST.get('computer', '')
        webcam= request.POST.get('Webcam', '')
        Internet= request.POST.get('Internet', '')
        Headset= request.POST.get('Headset', '')
        remarks =  request.POST.get('remarks', '')
        # print 'computer',computer
        vpo_come = request.POST.get('vpo_come', '').replace("_", " ")
        # pc_status = request.POST.get('pc_status','')
        # status = request.POST.get('status','')
        remarks = request.POST.get('remarks', '')
        user_p = UserProfile.objects.get(id=vol_id)
        if computer == 'YES':
            user_p.computer=True
        else:
            user_p.computer=False
        if webcam == 'YES':
            user_p.webcam=True
        else:
            user_p.webcam=False
        if Internet == 'YES':
            user_p.internet_connection=True
        else:
            user_p.internet_connection=False
        if Headset == 'YES':
            user_p.headset=True
        else:
            user_p.headset=False

        user_p.remarks=remarks
        user_p.save()
        if vol_id and o_come and role:

            pref_role = user_p.pref_roles.filter(name=role)
            role_pref = user_p.rolepreference_set.filter(role=pref_role)
            old_role_outcome = None
            if role_pref:
                role_pref = role_pref[0]
                old_role_outcome = role_pref.role_outcome
            role_pref.role_status = role_status
            role_pref.role_outcome = o_come
            role_pref.notes = remarks
            # vp outcome
            if vpo_come:
                vp_obj, created = VolunteerProcessing.objects.get_or_create(role=pref_role, user=user_p.user)
                old_vpo_come = vp_obj.outcome
                vp_obj.update_counter += 1
                vp_obj.last_outcome = old_vpo_come
                vp_obj.last_updated = vp_obj.dt_updated
                if vpo_come:
                    vp_obj.outcome = vpo_come
                if old_vpo_come == "Not Started" and vpo_come != "Not Started":
                    vp_obj.status = "Processed"
                    vp_obj.modified_by = request.user
                vp_obj.save()
            if old_role_outcome != o_come and o_come == "Recommended":
                role_pref.recommended_date = datetime.datetime.now()
            try:
                if role_pref:
                    role_pref.save()
                if old_role_outcome != o_come:
                    if role_pref.role_outcome == 'Recommended':
                        template_dir = '_volunteer_recommended'
                    elif role_pref.role_outcome == 'Recommended for Alternate Role':
                        template_dir = '_volunteer_rfa'
                    elif role_pref.role_outcome == 'Not Eligible':
                        template_dir = '_volunteer_not_eligible'
                    _send_mail([user_p.user], template_dir,
                               {'first_name': user_p.user.first_name, 'last_name': user_p.user.last_name,
                                'role': pref_role[0].name})
            except Exception as e:
                print e.message

            if role in ['Teacher', 'Center Admin', 'Content Admin', 'Facilitator Teacher']:
                if o_come not in ['Not Started', 'Inprocess'] and role_pref:
                    role_pref_obj = role_pref.onboardingstepstatus_set.filter(
                        step__stepname__in=['Teacher Selection Discussion', 'Admin Selection Discussion', 'Facilitator Teacher Selection Discution'])
                    if role_pref_obj:
                        role_pref_obj[0].status = True
                        role_pref_obj[0].save()
            if role_outcome == 'Recommended' and role in ['Teacher', 'Center Admin', 'Content Developer',
                                                          'Content Admin', 'Facilitator Teacher']:
                username = user_p.user.username.split("@")[0] + str(user_p.user.id)
                passw = base64.b64encode(WIKI_PASS)
                try:
                    create_wiki_account(user_p.user, username, passw)
                except:
                    print None
            if role_outcome == 'Recommended' and role in ['Teacher','Facilitator Teacher']:
                userp = UserProfile.objects.get(pk=vol_id)
                userObj = User.objects.get(username=userp.user)
                demandSlots = Demandslot.objects.filter(user=userObj)
                subject = "Congratulations ! You're an eVidyaloka Volunteer Teacher "
                url = ''
                name_url = ''
                vol_name = ''
                dc_mail = ''
                if len(demandSlots) > 0:
                    url = 'www.evidyaloka.org/myevidyaloka/'
                    name_url = 'View Booked Demand'
                    center = demandSlots[0].center
                    if center.delivery_coordinator:
                        dc_mail = center.delivery_coordinator.email
                else:
                    url = 'www.evidyaloka.org/v2/demand/'
                    name_url = 'Select your Class'
                print "Vol Username : " + str(userObj.username)

                if userObj.first_name:
                    vol_name = str(userObj.first_name) + ' ' + str(userObj.last_name)
                else:
                    vol_name = userObj.username

                to = [userObj.email]
                from_email = settings.DEFAULT_FROM_EMAIL
                cc = [ dc_mail]
                ctx = {'username': vol_name, 'url': url, 'name_url': name_url}
                message = get_template('mail/volunteer_rft.html').render(Context(ctx))
                msg = EmailMessage(subject, message, to=to, from_email=from_email, cc=cc)
                msg.content_subtype = 'html'
                msg.send()
            return HttpResponse('Profile updated successfully')
        else:
            return HttpResponse('Some error occured')
    else:
        return HttpResponse('Unauthorized request')


# ------------------------------------   End Volunteer Management -----------------------------#

def create_wiki_account(curr_user, username, passw):
    try:
        wiki_user = UserWikividya.objects.get(wiki_username=username)

    except UserWikividya.DoesNotExist:
        createdDate = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30))
        wiki_user = UserWikividya(user=curr_user, user_password=passw, wiki_username=username,
                                  created_by=curr_user.username, created_date=createdDate).save()
    wiki_user = UserWikividya.objects.get(wiki_username=username)
    if wiki_user:
        final_response = auto_login_wikividya(WIKI_BASE_URL, username, WIKI_PASS, False)
        result = final_response.json()['login']['result']
        # print "result", result
        if result == 'NotExists':
            create_wikividya_account(WIKI_BASE_URL, username, WIKI_PASS)


def create_wikividya_account(baseUrl, username, passw):
    params = '?action=createaccount&name=%s&password=%s&format=json' % (username, passw)
    r1 = requests.post(baseUrl + 'api.php' + params)
    token = r1.json()['createaccount']['token']
    params2 = params + '&token=%s' % token
    r2 = requests.post(baseUrl + 'api.php' + params2, cookies=r1.cookies)


def auto_login_wikividya(baseUrl, username, passw, flag):
    params = '?action=login&lgname=%s&lgpassword=%s&format=json' % (username, passw)
    final_response = requests.post(baseUrl + 'api.php' + params)
    if flag:
        return final_response
    token = final_response.json()['login']['token']
    params2 = params + '&lgtoken=%s' % token
    final_response = requests.post(baseUrl + 'api.php' + params2, cookies=final_response.cookies)
    return final_response


@csrf_exempt
def get_ofr_sess(request):
    start_date = request.POST.get('from_date', '')
    end_date = request.POST.get('to_date', '')
    end_date = (datetime.datetime.strptime(end_date, "%d-%m-%Y") + (timedelta(days=1))).strftime('%d-%m-%Y')
    offering_id = request.POST.get('offer', '')
    print offering_id
    offering_obj = Offering.objects.get(id=offering_id)
    course_id = offering_obj.course.id
    center_language = Offering.objects.get(id=offering_id).center.language
    user_profiles = UserProfile.objects.filter(pref_medium=center_language)
    users = []
    for profile in user_profiles:
        try:
            user = {"id": profile.user.id, "name": profile.user.first_name + " " + profile.user.last_name}
            users.append(user)
        except Exception as exp:
            #print "***ERROR - ", exp
			pass
    topics = offering_obj.planned_topics.all()
    topics_list_sess = []
    for topic in offering_obj.planned_topics.all():
        topics_list_sess.append({'id' : topic.id,'title': topic.title, 'num_sess': topic.num_sessions})
    topics = Topic.objects.filter(course_id=course_id).order_by('priority')
    topics_list = []
    for topic in topics:
        topics_list.append({'title': topic.title, 'num_sess': topic.num_sessions})
    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y')
        end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y')
        offering = Offering.objects.get(id=int(offering_id))
        in_range_sess = offering.session_set.filter(date_start__gte=start_date).filter(date_end__lte=end_date).order_by(
            'date_start')
        sess_list = []
        for session in in_range_sess:
            planned_topics = session.planned_topics.all()
            planned_topic = ""
            if planned_topics:
                for topic in planned_topics:
                    planned_topic = topics = topic.title
            weekday = session.date_start.weekday()
            ts_link = ''
            teachingSoftware_id = ''
            software_name = []
            software_name_selected = ''
            software_id = []
            software_id_selected = ''
            video_link = ''
            mode = ''
            day = make_weekday(weekday)
            ts_link = session.ts_link
            if session.teachingSoftware != None:
                video_link = session.video_link
                mode = session.mode
                software_name_selected = session.teachingSoftware.software_name
                software_id_selected = session.teachingSoftware.id
                teachingSoftware_id = session.teachingSoftware.id
            software_name.append(software_name_selected)
            total_software_name = TeachingSoftwareDetails.objects.values_list("software_name",flat= True).distinct()
            for software in total_software_name:
                if software != software_name[0]:
                    software_name.append(software)
            software_id.append(software_id_selected)
            total_software_id = TeachingSoftwareDetails.objects.values_list("id",flat= True).distinct()
            for id in total_software_id:
                if id != software_id[0]:
                    software_id.append(id)
            teacher_first_name = ''
            teacher_last_name = ''
            teacher_id = ''
            if session.teacher != None:
                teacher_first_name = session.teacher.first_name
                teacher_last_name = session.teacher.last_name
                teacher_id = session.teacher.id
            cur_session = {
                "course_offered": make_number_verb(
                    session.offering.course.grade) + ' ' + session.offering.course.subject + ', ' + session.offering.center.name + ' - ' +
                                  make_date_time(session.date_start)["date"] + ', ' +
                                  make_date_time(session.date_start)["time"] + ' to ' +
                                  make_date_time(session.date_end)["time"],
                "start_date": (session.date_start).strftime('%d-%m-%Y'),
                "end_date": (session.date_end).strftime('%d-%m-%Y'),
                "subject": session.offering.course.subject,
                "day": day,
                "start_time": session.date_start.strftime('%H:%M'),
                "end_time": session.date_end.strftime('%H:%M'),
                "planned_topic": planned_topic,
                "session_id": session.id,
                "teacher": teacher_first_name + " " + teacher_last_name,
                "teacher_id": teacher_id,
                "software_name": software_name,
                "software_id_selected":software_id,
                "software_id": teachingSoftware_id,
                "software_link": ts_link,
                "video_link" : video_link,
                "mode" : mode
            }
            sess_list.append(cur_session)
    temp_resp = {'sessions': sess_list, 'offering_id': offering_id, 'teacher': None, 'users': users,
                 'topics': topics_list,'topics_list_sess':topics_list_sess}
    return HttpResponse(simplejson.dumps(temp_resp), mimetype='application/json')


def getAcademicYear(board):
    today = datetime.datetime.now()
    ay = Ayfy.objects.filter(types='Academic Year').filter(start_date__lte=today).filter(end_date__gte=today,
                                                                                         board=board)
    if ay.count() > 1:
        return ay.latest('id')
    elif ay.exists():
        return ay[0]
    return 'No objects matched'


def get_holidays(board):
    try:
        holiday_dates = []
        # Getting Calender data
        ay = getAcademicYear(board)
        cal = Calender.objects.filter(board=board, academic_year=ay)
        if cal: cal = cal[0]
        holiday_list = Holiday.objects.filter(calender=cal).values_list('day', flat=True)
        if holiday_list: holiday_dates = [x.date() for x in holiday_list]
        else: holiday_list = []
        return holiday_dates
    except Exception as e:
        traceback.print_exc()
        return holiday_dates


@csrf_exempt
def reschedule_course(request):
    try:
        user_id = request.POST.get('user_id')
        user_id = user_id.split("::")[0]
        offering_id = request.POST.get('offering_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        del_confirm = request.POST.get('del_confirm')
        software = request.POST.get('software')
        software_link = request.POST.get('software_link', '')
        status = 'running'
        topics_list = request.POST.getlist('topics[]')
        user = User.objects.get(pk=user_id)
        offering = Offering.objects.get(pk=offering_id)
        board = offering.course.board_name
        holiday_dates = get_holidays(board)
        del_count = 0
        teaching_software = get_object_or_none(TeachingSoftwareDetails, id=software)


        '''
        removing session from teacher's preffered offerings as it is being assigned
        to him and no more required to be in the users(teacher here) preffered offerings list
        '''
        user.userprofile.pref_offerings.remove(offering)

        start_date = datetime.datetime.strptime(start_date.strip(), "%d-%m-%Y")
        end_date = datetime.datetime.strptime(end_date.strip(), "%d-%m-%Y")

        days_mapping = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
        _pref_days = request.POST.get('prefered_days').split(';')
        pref_days = [days_mapping[day] for day in _pref_days]
        pref_slots = request.POST.get('prefered_timings').split(';')
        # topics = [ Topic.objects.filter(title=top)[0] for top in topics_list]
        topics = []
        for top in topics_list:
            topic = Topic.objects.filter(title=top, course_id=offering.course)
            if topic:
                topics.append(topic[0])

        # remove sessions in the selected range
        if del_confirm == 'true':
            offer_inrange_sess = offering.session_set.filter(date_start__gte=start_date, date_end__lte=end_date)
            del_count = offer_inrange_sess.count()
            offer_inrange_sess.delete()
            offering.save

        if start_date and end_date:
            sessions_count = (end_date - start_date).days

            sessions = []
            for session in xrange(sessions_count):

                if not session == 0: start_date = start_date + datetime.timedelta(days=1)
                if start_date.weekday() not in pref_days:
                    continue
                if holiday_dates:
                    if start_date.date() in holiday_dates:
                        continue

                # to handle the case where the current weekday has multiple sessions in same day
                day_indexes = [i for i, k in enumerate(pref_days) if k == start_date.weekday()]

                for day_index in day_indexes:
                    timings = pref_slots[day_index].split('-')
                    s_hours = timings[0].split(':')[0]
                    s_mins = timings[0].split(':')[1]
                    e_hours = timings[1].split(':')[0]
                    e_mins = timings[1].split(':')[1]
                    start_time = start_date + datetime.timedelta(hours=int(s_hours), minutes=int(s_mins))
                    end_time = start_date + datetime.timedelta(hours=int(e_hours), minutes=int(e_mins))
                    sessions.append({'start_time': start_time, 'end_time': end_time})

            # topics = offering.planned_topics.all().order_by('priority')
            # import pdb;pdb.set_trace()
            count = 0
            for topic in topics:
                topic_sessions = topic.num_sessions or 1
                for topic_session in range(topic_sessions):
                    # creating sessions if gets index error will save up to that sessions
                    try:
                        session = sessions[count]
                        s = Session.objects.get_or_create(teacher=user, date_start=session['start_time'],
                                                        date_end=session['end_time'], offering=offering,
                                                        ts_link=software_link, teachingSoftware=teaching_software
                                                        )
                        s[0].planned_topics.add(topic)
                        s[0].save
                        count += 1
                    except IndexError:
                        break
        else:
            startdate = datetime.datetime.today()
            enddate = datetime.datetime.today() + datetime.timedelta(weeks=6)
            s = Session.objects.create(teacher=user, date_start=startdate, date_end=enddate, offering=offering, ts_link=software_link, teachingSoftware=teaching_software)
            topics = offering.planned_topics.all()
            for topic in topics:
                s.planned_topics.add(topic)
            s.save()

        session_arr = []
        for session in Session.objects.filter(offering=offering).order_by('date_start'):
            session_arr.append(make_number_verb(
                session.offering.course.grade) + ' ' + session.offering.course.subject + ', ' + session.offering.center.name + ' - ' +
                            make_date_time(session.date_start)["date"] + ' ' + make_date_time(session.date_start)[
                                "time"])

        offering.status = status
        offering.save()
        
        onboarding_alert(request, user, offering)
        
        resp_txt = "%d Classes Deleted and %d Classes Created." % (del_count, count)
        return HttpResponse(resp_txt)
    except Exception as e:
        traceback.print_exc()
        logService.logException("OfferingReport POST Exception error", e.message)
        return genUtility.getStandardErrorResponse(self.request, 'kInvalidRequest')
    


# --------------------  bulk user generation -----------------#

@login_required
def bulk_usergen(request):
    if request.user.is_superuser:
        return render_response(request, 'bulk_user_generation.html', {})
    else:
        return HttpResponse('You are not Authorized to access this functionality.')


@login_required
def bulk_usergen_xlrd(request):
    if request.user.is_superuser:
        input_excel = request.FILES['filee']
        book = xlrd.open_workbook(file_contents=input_excel.read())
        sheet = book.sheet_by_index(0)
        data_list = []
        hdr = ['email_id', 'email_id2', 'first_name', 'last_name', 'language', 'phone']
        for row_index in range(1, sheet.nrows):
            discard_row = False
            data = {}
            for i in range(sheet.ncols):
                if sheet.cell_value(row_index, i) == '' and i < 1:
                    discard_row = True
                else:
                    data[hdr[i]] = sheet.cell_value(row_index, i)
            usernamee = sheet.cell_value(row_index, 0)
            emaill = sheet.cell_value(row_index, 0)
            if User.objects.filter(Q(username=usernamee) | Q(email=emaill)).exists() or (' ' in usernamee) or len(
                    usernamee) > 30:
                data['duplicate'] = 'Yes'
            else:
                data['duplicate'] = 'No'
            if discard_row == False:
                data_list.append(data)
        return HttpResponse(simplejson.dumps({'data': data_list}), mimetype='application/json')
    else:
        return HttpResponse('You are not Authorized to access this functionality.')


@login_required
def bulk_user_create(request):
    if request.user.is_superuser:
        up_data = request.POST.get('up_data', '')
        up_data_p = json.loads(up_data)
        created_recs = []
        if len(up_data_p) > 0:
            for ent in up_data_p:
                pwd = (ent['email']).split('@')[0]
                user_dict = {'username': ent['username'], 'first_name': ent['first_name'],
                             'last_name': ent['last_name'], 'email': ent['email']}
                try:
                    usr = User(**user_dict)
                    usr.set_password(pwd)
                    usr.save()
                    userp = UserProfile.objects.get(user=usr)
                    userp.secondary_email = ent['email2']
                    userp.pref_medium = ent['language']
                    userp.phone = ent['phone']
                    userp.save()
                    _send_html_mail(usr, '_volunteer_joined', {"username": usr.username})
                    created_recs.append({'id': usr.id, 'username': usr.username, 'password': pwd})
                except Exception as e:
                    file_name, content = write_to_log(created_recs)
                    send_log('user_generation/' + file_name, content)
                    return HttpResponse(
                        'Duplicate email id/id\'s exist in the current records. Hence Aborting user creation.')
            msg = '%s Records Created Successfully' % str(len(created_recs))
            file_name, content = write_to_log(created_recs)
            send_log('user_generation/' + file_name, content)
        else:
            msg = 'No Data Suplied for User creation'
        return HttpResponse(msg)
    else:
        return HttpResponse('You are not Authorized to access this functionality.')


def write_to_log(created_records):
    today = datetime.datetime.now()
    file_name = "Log dated :" + today.strftime('%d-%m-%Y::%H:%M')
    content = ['', '', '', '']
    content[0] = "Bulk User Generation Log dated : " + today.strftime('%d-%m-%Y::%H:%M')
    content[1] = "Please find the attachment."
    content[2] = "rishi@evidyaloka.org  "
    content[3] = 'Total records generated : ' + str(len(created_records)) + '\n'
    content[3] += 'User ID\tUsername\tPassword\n'
    for ent in created_records:
        content[3] += str(ent["id"]) + '\t' + ent['username'] + '\t' + ent['password'] + '\n'
    return file_name, content


# --------------------  End bulk user generation -----------------#


# ----------------------- Teachers Day 2016 -----------------------#

def teachers_day2016(request):
    user_id = request.GET.get('volunteer')
    if user_id:
        user = User.objects.filter(id=user_id)
        if user:
            user = user[0]
            userp = user.userprofile
            user_details = USER_DATA_TEACHERS_DAY_2016.get(str(user.id))
            if user_details:
                pic_path = user_details['state'] + '/' + user_details['center'] + '/' + user_details['pic']
                base_path = os.getcwd()
                file_rel_path = '/static/img_new/teachers_day/' + pic_path
                if not os.path.isfile(base_path + file_rel_path):
                    file_rel_path = '/static/img_new/teachers_day/AP/Vamakuntala/7th.jpg'
                user_details.update({'photo': file_rel_path})
                return render_response(request, "teachers_day16.html", user_details)
        return HttpResponse('You are not Authorized to access this functionality.')
    else:
        return HttpResponse('Please use the link you have recieved through email.')


# ----------------------- End Teachers Day 2016 -----------------------#

# ------------------- My eVidyaloka Rewamp ---------------#



def new_profile(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/myevidyaloka')
    else:
        user_location_info = {'country': '', 'state': '', 'city': ''}
        ''' message = request.GET.get('message', '')
        if request.user.partner_set.values():
            return partner_profile(request)

        if not request.user.is_authenticated():

            email_id = request.GET.get("email_id")
            user_id = str(request.GET.get("user_id"))
            if not email_id or not user_id:
                return HttpResponseRedirect("/")

            existing_user = None

            for entry in WHITE_LIST:

                if str(entry["id"]) == user_id and email_id == entry["email"]:
                    existing_user = entry

            if not existing_user:
                return HttpResponseRedirect("/")

            user = User.objects.get(id=user_id)

            user.backend = 'django.contrib.auth.backends.ModelBackend'

            if not user.is_active:
                return HttpResponseRedirect("/")
            login(request, user)

            return HttpResponseRedirect("/user_profile/")

        sub, profile_percent = [], {'Incomplete': 10, 'Started': 35, 'Inprocess-1': 55, 'Selected': 75, 'Ready': 100}
        prf_status_des = {"Incomplete": "Please fill in the required personal information",
                          "Started": "Please proceed to onboarding",
                          "Inprocess": "Please complete your Self Evaluation and Selection Discussion",
                          "Selected": "Please update your Readiness requirements", "Ready": "Ready"}
        # offerings of the sessions that doesn't have a teacher and language equals to the user prefered medium

        curr_user = request.user

        ref_channels = ReferenceChannel.objects.filter(partner__status='Approved')

        user_profile, roles, pref_roles, unassigned_offering_arr, prof_per = [], [], [], [], 35
        refchannel = ''
        user_profile = UserProfile.objects.filter(user=curr_user)
        if user_profile:
            user_profile = user_profile[0]
            user_profile_dict = user_profile.get_dict()
            location_fields = ['country', 'state', 'city']
            user_location_info = {'country': '', 'state': '', 'city': ''}
            for k, v in user_profile_dict.iteritems():
                if k in location_fields and v:
                    user_location_info[k] = str(v)

            refchannel = ReferenceChannel.objects.filter(id=user_profile.referencechannel_id)
            if refchannel: refchannel = refchannel[0]

            usr_prf_status = user_profile.profile_complete_status

            admin_assigned_roles = ["TSD Panel Member", "Class Assistant", "vol_admin", "vol_co-ordinator", "Partner Admin"]
            roles = Role.objects.exclude(name__in=admin_assigned_roles)
            pref_roles = [role.id for role in user_profile.pref_roles.exclude(name__in=admin_assigned_roles)]
            from_date_ts = int(time.mktime(user_profile.from_date.timetuple()) * 1000)
            to_date_ts = int(time.mktime(user_profile.to_date.timetuple()) * 1000)
            is_teacher = False
            is_centeradmin = False
            new_centeradmin = False
            if has_role(user_profile, "Center Admin") and (
                    has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher")):
                is_centeradmin = True
                is_teacher = True
            elif has_role(user_profile, "Center Admin"):
                is_centeradmin = True
            elif has_pref_role(user_profile, "Center Admin"):
                new_centeradmin = True
            if has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher"):
                is_teacher = True
            if not curr_user.is_superuser:
                user_centers = Center.objects.filter(admin=curr_user)
            else:
                user_centers = Center.objects.all()

            if is_centeradmin: usr_prf_status = 'Ready'
            if (has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher")) and \
                    user_profile.evd_rep and usr_prf_status == 'Inprocess':
                if user_profile.dicussion_outcome != 'Not Scheduled':
                    usr_prf_status = 'Selected'
                else:
                    usr_prf_status = 'Inprocess-1'

            prof_per = profile_percent.get(usr_prf_status, 0)
            prof_cm_status = "Inprocess" if "Inprocess" in usr_prf_status else usr_prf_status
            prof_cm_des = prf_status_des[prof_cm_status]

        show_error_msg = False
        if request.path == "/myevidyaloka/":
            show_error_msg = True
        prof_list = ['Business and Financial Operations', 'Community and Social Service', 'Computer and Mathematical',
                     'Education, Training, and Library', \
                     'Farming, Fishing, and Forestry', 'Healthcare Practitioners and Technical', 'Legal',
                     'Life, Physical, and Social Science', 'Management', 'Military Specific', \
                     'Office and Administrative Support', 'Personal Care and Service', 'Production/Manufacturing',
                     'Sales and Related', 'Self-employed', 'Retd. Professional', 'Housewife', \
                     'Student - PG', 'Student', 'Others']
        save_user_activity(request, 'Viewed page: My Profile - Profile', 'Page Visit')'''

        return render_response(request, 'new_profile_page.html',
                               { 'user_location_info': user_location_info });

"""@login_required
def new_profile(request):
    message = request.GET.get('message', '')
    if request.user.partner_set.values():
        return partner_profile(request)

    if not request.user.is_authenticated():

        email_id = request.GET.get("email_id")
        user_id = str(request.GET.get("user_id"))
        if not email_id or not user_id:
            return HttpResponseRedirect("/")

        existing_user = None

        for entry in WHITE_LIST:

            if str(entry["id"]) == user_id and email_id == entry["email"]:
                existing_user = entry

        if not existing_user:
            return HttpResponseRedirect("/")

        user = User.objects.get(id=user_id)

        user.backend = 'django.contrib.auth.backends.ModelBackend'

        if not user.is_active:
            return HttpResponseRedirect("/")
        login(request, user)

        return HttpResponseRedirect("/user_profile/")

    sub, profile_percent = [], {'Incomplete': 10, 'Started': 35, 'Inprocess-1': 55, 'Selected': 75, 'Ready': 100}
    prf_status_des = {"Incomplete": "Please fill in the required personal information",
                      "Started": "Please proceed to onboarding",
                      "Inprocess": "Please complete your Self Evaluation and Selection Discussion",
                      "Selected": "Please update your Readiness requirements", "Ready": "Ready"}
    # offerings of the sessions that doesn't have a teacher and language equals to the user prefered medium

    curr_user = request.user

    ref_channels = ReferenceChannel.objects.filter(partner__status='Approved')

    user_profile, roles, pref_roles, unassigned_offering_arr, prof_per = [], [], [], [], 35
    refchannel = ''
    user_profile = UserProfile.objects.filter(user=curr_user)
    if user_profile:
        user_profile = user_profile[0]
        user_profile_dict = user_profile.get_dict()
        location_fields = ['country', 'state', 'city']
        user_location_info = {}
        for k, v in user_profile_dict.iteritems():
            if k in location_fields and v:
                user_location_info[k] = str(v)

        refchannel = ReferenceChannel.objects.filter(id=user_profile.referencechannel_id)
        if refchannel: refchannel = refchannel[0]

        usr_prf_status = user_profile.profile_complete_status

        admin_assigned_roles = ["TSD Panel Member", "Class Assistant", "vol_admin", "vol_co-ordinator", "Partner Admin"]
        roles = Role.objects.exclude(name__in=admin_assigned_roles)
        pref_roles = [role.id for role in user_profile.pref_roles.exclude(name__in=admin_assigned_roles)]
        from_date_ts = int(time.mktime(user_profile.from_date.timetuple()) * 1000)
        to_date_ts = int(time.mktime(user_profile.to_date.timetuple()) * 1000)
        is_teacher = False
        is_centeradmin = False
        new_centeradmin = False
        if has_role(user_profile, "Center Admin") and (
                has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher")):
            is_centeradmin = True
            is_teacher = True
        elif has_role(user_profile, "Center Admin"):
            is_centeradmin = True
        elif has_pref_role(user_profile, "Center Admin"):
            new_centeradmin = True
        if has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher"):
            is_teacher = True
        if not curr_user.is_superuser:
            user_centers = Center.objects.filter(admin=curr_user)
        else:
            user_centers = Center.objects.all()

        if is_centeradmin: usr_prf_status = 'Ready'
        if (has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher")) and \
                user_profile.evd_rep and usr_prf_status == 'Inprocess':
            if user_profile.dicussion_outcome != 'Not Scheduled':
                usr_prf_status = 'Selected'
            else:
                usr_prf_status = 'Inprocess-1'

        prof_per = profile_percent.get(usr_prf_status, 0)
        prof_cm_status = "Inprocess" if "Inprocess" in usr_prf_status else usr_prf_status
        prof_cm_des = prf_status_des[prof_cm_status]

    show_error_msg = False
    if request.path == "/myevidyaloka/":
        show_error_msg = True
    prof_list = ['Business and Financial Operations', 'Community and Social Service', 'Computer and Mathematical',
                 'Education, Training, and Library', \
                 'Farming, Fishing, and Forestry', 'Healthcare Practitioners and Technical', 'Legal',
                 'Life, Physical, and Social Science', 'Management', 'Military Specific', \
                 'Office and Administrative Support', 'Personal Care and Service', 'Production/Manufacturing',
                 'Sales and Related', 'Self-employed', 'Retd. Professional', 'Housewife', \
                 'Student - PG', 'Student', 'Others']
    save_user_activity(request, 'Viewed page: My Profile - Profile', 'Page Visit')

    return render_response(request, 'new_profile.html',
                           {"pref_roles": pref_roles, "roles": roles, "user_profile": user_profile,
                            "curr_user": curr_user, "from_date_ts": from_date_ts, "to_date_ts": to_date_ts,
                            "accept": user_profile.code_conduct, "is_centeradmin": is_centeradmin,
                            "is_teacher": is_teacher, "new_centeradmin": new_centeradmin,
                            "show_error_msg": show_error_msg, "purpose": user_profile.purpose, 'prof_per': prof_per,
                            'prof_cm_status': prof_cm_status, 'prof_cm_des': prof_cm_des, 'prof_list': prof_list,
                            'user_location_info': user_location_info, 'message': message, 'ref_channels': ref_channels,
                            'referencechannel': refchannel})
"""


def save_profilepic(request):
    files = request.FILES
    user = request.user
    up_file = files['file']
    try:
        user_profile = user.get_profile()
    except:
        user_profile = UserProfile(user=user)

    f_path = os.getcwd()
    up_file_name, extension = os.path.splitext(up_file.name)
    f_name = '/static/profile_images/' + request.user.username + extension
    f = open(f_path + f_name, 'w+')
    f.write(up_file.read())
    f.close()

    image = PIL.open(f_path + f_name)
    image.thumbnail([150, 150], PIL.ANTIALIAS)
    image.save(f_path + f_name, image.format, quality=90)
    user_profile.picture = f_name
    user_profile.save()

    # generating json response array
    result = []
    result.append({
        "url": user_profile.picture
    })
    response_data = simplejson.dumps(result)

    if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
        mimetype = 'application/json'
    else:
        mimetype = 'text/plain'
    platform = request.POST.get('platform', '')
    if platform:
        return HttpResponse(simplejson.dumps({'status': 'sucess'}), mimetype='application/json')
    return HttpResponse('ok')


def save_base_profile(request):
    fname = request.user.first_name
    user = request.user
    userp = user.userprofile
    step = request.POST.get('step')
    referral_notification = True
    if userp.gender:
        referral_notification = False

    if step == 'base_profile':
        request_to_db = {
            'prefered_medium': 'pref_medium',
            'alt_email': 'secondary_email'
        }
        user_fields = [i.name for i in User._meta.fields]
        user_fields.remove('id')

        userp_fields = [i.name for i in UserProfile._meta.fields]
        userp_fields.remove('id')

        user_update_fileds = {}
        userp_update_fileds = {}
        for k, v in request.POST.iteritems():
            k = request_to_db.get(k, k)
            if isinstance(v, list):
                v = ",".join(v)
            if k in user_fields:
                user_update_fileds[k] = v
            elif k in userp_fields:
                userp_update_fileds[k] = v

        if user_update_fileds:
            for key, value in user_update_fileds.items():
                setattr(user, key, value)
            user.save()

        if userp_update_fileds:
            userp.__dict__.update(userp_update_fileds)
            userp.save()
        if referral_notification and userp.referred_user:
            subject = 'Thank you for referring ' + str(user.first_name) + ' ' + str(user.last_name) + ' to eVidyaloka'
            from_email = settings.DEFAULT_FROM_EMAIL
            cc = ['volunteer@evidyaloka.org']
            ctx = {'user_name': str(user.first_name) + ' ' + str(user.last_name),
                   'referral_user': userp.referred_user.first_name, 'subject': subject}
            message = get_template('mail/referral.txt').render(Context(ctx))
            msg = EmailMessage(subject, message, to=[userp.referred_user.email], from_email=from_email, cc=cc)
            msg.content_subtype = 'html'
            msg.send()

        ref_ch_name = str(request.POST.get('reference_channel'))
        ref_channel = ReferenceChannel.objects.filter(name=ref_ch_name)
        if len(ref_channel) == 1:
            userp.referencechannel = ref_channel[0]

        userp.profile_completion_status = True
        code_conduct = request.POST.get('code_conduct')
        if code_conduct:
            userp.code_conduct = code_conduct

        roles = request.POST.get('roles')
        if roles:
            selected_roles = [Role.objects.get(pk=int(role)) for role in roles.split(";") if role]
        else:
            selected_roles = []

        # Maintaining admin assigned roles state
        admin_assigned_roles = ["TSD Panel Member", "Class Assistant", "Field co-ordinator", "Delivery co-ordinator"]
        admin_assigned_role_objs = [Role.objects.get(name=name) for name in admin_assigned_roles]
        selected_roles.extend(userp.role.filter(name__in=admin_assigned_roles))

        user_centers = Center.objects.filter(admin=request.user)
        userp.role.clear()
        for role in selected_roles:
            if (
                    role.name == 'Center Admin' or role.name == 'Class Assistant' or role.name == 'Field co-ordinator' or role.name == 'Delivery co-ordinator') and user_centers:
                userp.role.add(role)
            else:
                userp.role.add(role)

        userp.pref_roles.clear()

        for role in selected_roles:
            userp.pref_roles.add(role)

        # Role onboarding
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
    elif step == 'orientation':
        userp.evd_rep = True
    elif step == 'role_select':
        roles = request.POST.getlist('role_list[]')
        selected_roles = [Role.objects.get(pk=int(role)) for role in roles]

        # Maintaining admin assigned roles state
        admin_assigned_roles = ["TSD Panel Member", "Class Assistant", "Field co-ordinator", "Delivery co-ordinator"]
        admin_assigned_role_objs = [Role.objects.get(name=name) for name in admin_assigned_roles]
        selected_roles.extend(userp.role.filter(name__in=admin_assigned_roles))

        user_centers = Center.objects.filter(admin=request.user)
        userp.role.clear()

        for role in selected_roles:
            if (
                    role.name == 'Center Admin' or role.name == 'Class Assistant' or role.name == 'Field co-ordinator' or role.name == 'Delivery co-ordinator') and user_centers:
                userp.role.add(role)
            else:
                userp.role.add(role)

        userp.pref_roles.clear()

        for role in selected_roles:
            userp.pref_roles.add(role)

        # Role onboarding
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

    response_dict = {'status': 0, 'message': ''}
    platform = request.POST.get('platform', '')
    try:
        flag = False
        if fname:
            flag = True
        user.save()
        userp.save()
        if flag:
            save_user_activity(request, 'Updated Profile', 'Update')
        else:
            save_user_activity(request, 'Completed Profile', 'Action')

    except Exception as e:
        print e

        if platform:
            response_dict['status'] = 1
            return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

        return HttpResponse('Error')

    if platform:
        return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')

    return HttpResponse('Success')


@login_required
def onboarding(request):
    total_status = 0
    userp = request.user.userprofile
    if has_pref_role(userp, "vol_admin") or has_pref_role(userp, "vol_co-ordinator") or has_pref_role(userp, "support"):
        if has_pref_role(userp, "Teacher") or has_pref_role(userp, "Center Admin") or has_pref_role(userp,
                                                                                                    "Content Developer") or has_pref_role(
                userp, "Well Wisher") or has_pref_role(userp, "Content Admin") or has_pref_role(userp,
                                                                                                "Class Assistant") or has_pref_role(
                userp, "TSD Panel Member"):
            print "Have other roles too"
        else:
            return redirect('/task_list/')
    orientation_status = userp.evd_rep
    onboardings = userp.rolepreference_set.filter(role__in=userp.pref_roles.all())
    onboarding_dicts = []
    selectionDescussion = []
    for onboarding in onboardings:
        if onboarding.role.name == 'Teacher':
            selectionDescussion = SelectionDiscussion.objects.filter(userp=userp).values_list("start_time", "end_time")
        next_step = onboarding.onboardingstepstatus_set.filter(status=False).order_by('id')
        total_status += onboarding.role_onboarding_status
        onboarding_dict = model_to_dict(onboarding)
        onboarding_dict['role_short_name'] = onboarding.role.name.lower().replace(' ', '')
        onboarding_dict['role_id'] = onboarding.role.id
        onboarding_dict['role_name'] = onboarding.role.name
        onboarding_dict['role_outcome'] = onboarding.role_outcome
        if next_step:
            onboarding_dict['next_step'] = next_step[0].step.stepname
        onboarding_dicts.append(onboarding_dict)
    member_token = get_facebook_member_token()
    if len(onboarding_dicts) == 1:
        if onboarding.role.name == 'Field co-ordinator' or onboarding.role.name == 'Delivery co-ordinator':
            return HttpResponseRedirect('/myevidyaloka/')
        uriName = onboarding_dicts[0]['role_short_name']
        save_user_activity(request, "Role:" + str(uriName).title() + ",Viewed page, Onboarding Status", "Page Visit")
        return redirect("/role_onboarding/" + uriName);
    else:
        save_user_activity(request, "Viewed page, Onboarding Status", "Page Visit")
        return render_response(request, 'onboarding.html',
                               {'onboardings': onboarding_dicts, 'total_status': total_status,
                                'member_token': member_token, 'selection_descussion': selectionDescussion,
                                'orientation_status': orientation_status})


def role_dashboard(request, role_name):
    print(role_name, role_name)
    if request.POST.get('flagMail') == 'yes':
        org_name = str(request.POST.get('org_name'))
        ref_channel = ReferenceChannel.objects.get(name = org_name)
        if str(ref_channel.mail_status) == 'unmuted':
            ref_channel.mail_status = 'muted'
        else:
            ref_channel.mail_status = 'unmuted'
        ref_channel.save()
    user = request.user
    role = get_role_title(role_name)
    print(role_name, role)
    # import pdb; pdb.set_trace()
    if user.is_authenticated():
        # user = User.objects.filter(username =  user1)[0]
        user_profile = UserProfile.objects.filter(user=user)[0]
        if user.is_superuser or role_name == "fieldcoordinator" or role_name == "deliverycoordinator":
            return admindash(request)

        elif role_name == 'partneradmin':
            from partner.views import partner_admin_defaultpage
            request.method = 'GET'
            return partner_admin_defaultpage(request)

        # If user has not filled his profile, we'll render to settings page.
        elif user_profile.profile_completion_status:
            userp = UserProfile.objects.filter(user=user)[0]
            user_roles = RolePreference.objects.filter(userprofile=userp, role_outcome='Recommended')
            print('user_roles',user_roles)
            role = role[0]
            if user_roles:
                if role.name == 'Center Admin':
                    if has_role(userp, "Center Admin") or has_pref_role(userp, "Center Admin"):
                        # user_main = User.objects.filter(username = userp.user)[0]
                        center = Center.objects.filter(admin=user)
                        if center: return centeradmin(request, center[0].id)
                    return centeradmin_temp(request)
                elif role.name == 'Class Assistant':
                    if has_role(userp, "Class Assistant") or has_pref_role(userp, "Class Assistant"):
                        center = Center.objects.filter(assistant=user,status='Active')
                        if center: return centeradmin(request, center[0].id)
                    return centeradmin_temp(request)
                elif role.name == 'Content Admin' and has_role_preference(request.user, "Content Admin"): 
                    return  ContentAdminView.as_view()(request)
                
                elif role.name == 'Content Reviewer' and has_role_preference(request.user, "Content Reviewer"): 
                    return  ContentReviwerView.as_view()(request)

                elif role.name == 'Content Reviewer':
                    if has_role(userp, "Content Reviewer") or has_pref_role(userp, "Content Reviewer"): return contentreviwer(request)
                    #return role_onboarding(request, role_name)
                    return HttpResponseRedirect('/v2/vLounge')
                elif role.name == 'Teacher':
                    return teacherdash(request)
                    # return role_onboarding(request, role_name)
                elif role.name=='Facilitator Teacher':
                    return teacherdash(request)
                    
                elif role.name == 'Partner Account Manager':
                    if has_role(userp, "Partner Account Manager") or has_pref_role(userp, "Partner Account Manager"):
                        db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
                        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
                        query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                        dict_cur.execute(query)
                        partner_id = [str(each['value']) for each in dict_cur.fetchall()]
                        partner_id.sort()	
                        partners=Partner.objects.filter(id__in =partner_id)
                        mail_status_list=[]
                        for pname in partners:
                            try:
                                organization = str(Partner.objects.get(name = pname).name_of_organization)
                            except:
                                pass
                            try:
                                mail_status_list.append(str(ReferenceChannel.objects.get(name = organization).mail_status))
                            except:
                                pass
                        zippedList = zip(partners, mail_status_list)
                        dict_cur.close()
                        return render_response(request, 'partneraccountmanager.html',{"partners":partners,"zipped_list":zippedList})               
                    return HttpResponseRedirect('/v2/vLounge')
                elif role.name == 'Content Developer':
                    if has_role_preference(request.user, "Content Developer"): 
                        return  ContentVolunteerView.as_view()(request)
                    return HttpResponseRedirect('/v2/vLounge')

                elif role.name == 'Well Wisher':
                    if has_role(userp, "Well Wisher") or has_pref_role(userp, "Well Wisher"): return well_wisher(
                        request)
                    #return role_onboarding(request, role_name)
                    return HttpResponseRedirect('/v2/vLounge')
                # elif has_pref_role(userp, "Center Admin"): return centeradmin_temp(request)
                # elif has_pref_role(userp, "Class Assistant"): return centeradmin_temp(request)
                else:
                    return redirect("/");
            else:
                return role_onboarding(request, role_name)
                # return HttpResponseRedirect('/v2/vLounge')

        else:
            return new_profile(request)
    else:
        return redirect("/?show_popup=true&type=login")


def get_role_title(short_role_name):
    roles = Role.objects.all()
    roles_dict = {name.lower().replace(' ', '').replace('-', ''): id for name, id in roles.values_list('name', 'id')}
    role = roles.filter(pk=roles_dict[short_role_name])
    return role


@login_required
def role_onboarding(request, role_name):
    return HttpResponseRedirect('/v2/vLounge')
    userp = request.user.userprofile
    role = get_role_title(role_name)
    selectionDescussion = []
    unavilable_reasons_list = [x for x in dict(UserProfile._meta.get_field('unavailability_reason').choices)]
    pref_sub_list = userp.pref_subjects.split(";")
    unavailable_reason_selected = userp.unavailability_reason
    unavail_list_ = ["Interested, but not now", "Interested, but Occupied with Professional commitments",
                     "Interested, but Occupied with Personal commitments"]
    availability = 0
    follow_up_date = None
    if role:
        onboarding = userp.rolepreference_set.filter(role=role)
        evd_rep_check = userp.evd_rep
        if onboarding and role[0].name == "Teacher":
            availability = RolePreference.objects.get(id=onboarding[0].id).availability
            follow_up_date = RolePreference.objects.get(id=onboarding[0].id).follow_up_date
            selectionDescussion = SelectionDiscussion.objects.filter(userp=userp).values_list("start_time", "end_time")
        if onboarding and userp.profile_completion_status:
            onboarding = onboarding[0]
            stepstatuses = onboarding.onboardingstepstatus_set.all().order_by('step__order')
            modif_step_status = []
            for stepstatus in stepstatuses:
                step_dict = model_to_dict(stepstatus)
                step_dict['step_name'] = stepstatus.step.stepname
                step_dict['desc'] = stepstatus.step.description
                step_dict['short_name'] = (stepstatus.step.stepname).replace(' ', '_')
                step_dict['repeatable'] = stepstatus.step.repeatable
                # step_dict['role_stat'] = stepstatus.role_preference.role_status
                prerequisite = stepstatus.step.prerequisite
                if prerequisite:
                    pre_step_status = stepstatuses.filter(step=prerequisite)
                    if pre_step_status:
                        step_dict['prerequisite'] = pre_step_status[0].status
                modif_step_status.append(step_dict)
        else:
            return myevidyaloka(request)
    else:
        return HttpResponse('Invalid Request')
    member_token = get_facebook_member_token()
    demandslots = Demandslot.objects.filter(user=request.user.id)
    slot_details = []
    if demandslots:
        slot_details = demandslots.values_list('center__name', 'day', 'start_time', 'end_time', 'date_booked',
                                               'offering__course__subject')

    if not request.user.is_superuser and role[0].name == 'Class Assistant':
        centers = Center.objects.filter(assistant = request.user).exclude(status = 'Closed')
        if len(centers)>0:
            center_board = centers[0].board
            try:
                current_ay = Ayfy.objects.get(start_date__year=datetime.datetime.now().year, board=center_board)
            except:
                last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
                current_ay = Ayfy.objects.get(start_date__year=last_year, board=center_board)
            return redirect("/centeradmin/?center_id="+ str(centers[0].id)+ "&ay_id="+ str(current_ay.id))

    save_user_activity(request, "Role:" + str(role_name).title() + ",Viewed page, Onboarding Status", "Page Visit")
    return render_response(request, role_name + 'onboarding.html',
                           {'user_profile': userp, 'onboarding': onboarding, 'steps': modif_step_status, \
                            'member_token': member_token, 'selection_descussion': selectionDescussion,
                            'unavilable_reasons_list': unavilable_reasons_list, \
                            'unavailable_reason_selected': unavailable_reason_selected, 'availability': availability,
                            'pref_sub_list': pref_sub_list,
                            'follow_up_date': follow_up_date, 'unavail_list_': unavail_list_,
                            'evd_rep_check': evd_rep_check, 'slot_details': slot_details})


@login_required
def selfeval_response(request):
    userp = request.user.userprofile
    se_form = request.POST.get('form_dump')
    date_submited = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
    onboard_id = request.POST.get('onboard_id')
    onboard = RolePreference.objects.get(id=int(onboard_id))
    try:
        se, created = SelfEvaluation.objects.get_or_create(userp=userp, role_preference=onboard)
        se.se_form = se_form
        se.date_submited = date_submited
        se.save()
        onboard_string = '' + str(onboard)
        onboard_name = ''
        if len(onboard_string) > 1:
            onboard_name = onboard_string.split(' ', 1)[1]
        save_user_activity(request,
                           "Role:" + str(onboard_name).title() + ",Completed Onboarding Step 1: Self Evaluation",
                           'Action')
        step_status = save_step_status(onboard.id, 'Self Evaluation')
        """if onboard.role.name == "Content Developer":

            #intimation mail
            args = {'user':request.user}
            subject_template = 'mail/se_submit/short.txt'
            subject = get_mail_content(subject_template, args)
            body_template = 'mail/se_submit/full.txt'
            body = get_mail_content(body_template, args)
            #recipients = ["kripa.subramony@evidyaloka.org", request.user.email]
            recipients = []
            recipients.append('akhilraj@headrun.com')
            insert_into_alerts(subject, body, ','.join(recipients), request.user.id, 'email')"""

    except Exception as e:
        print e.message
        return HttpResponse('Error')
    return HttpResponse('Success')


def save_availability(request):
    print "save_availability",request
    availability = request.POST.get('availability')
    source = request.POST.get("source")
    pref_slots=request.POST.get("pref_slots")
    pref_days=request.POST.get("pref_days")

    if source == "onboard":
        '''onboard_id = request.POST.get('onboard_id')
        onboard = RolePreference.objects.get(id=int(onboard_id))
    else:'''
        userp = request.user.userprofile
        onboard_id = request.POST.get('onboard_id')
        onboard = RolePreference.objects.get(id=int(onboard_id))
    else:
        user_id = request.POST.get("user_id")
        userp = UserProfile.objects.get(id=int(user_id))
        role = Role.objects.filter(name="Teacher")
        onboard = userp.rolepreference_set.get(role=role)
    userp.pref_slots=pref_slots
    userp.pref_days=pref_days
    if availability == 'available':
        onboard.availability = True
        if source == "onboard":
            userp.pref_days = request.POST.get('pref_days')
            userp.pref_slots = request.POST.get('pref_times')
        userp.pref_subjects = request.POST.get('pref_sub')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        if from_date and to_date:
            from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')
        date_submited = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
        userp.from_date = from_date
        userp.to_date = to_date
        userp.pref_slots=pref_slots
        step_status = save_step_status(onboard.id, 'Availability and Preferences')
    else:
        onboard.availability = False
        follow_up_date = request.POST.get('follow_up_date')
        if follow_up_date:
            follow_up_date = datetime.datetime.strptime(follow_up_date, '%Y-%m-%d')
        onboard.follow_up_date = follow_up_date
        userp.unavailability_reason = request.POST.get('reason')
    onboard_string = '' + str(onboard)
    onboard_name = ''
    if len(onboard_string) > 1:
        onboard_name = onboard_string.split(' ', 1)[1]
    try:
        userp.save()
        onboard.save()
        save_user_activity(request,
                           "Role:" + str(onboard_name) + ",Completed Onboarding Step 3: Availability and Preferences",
                           'Action')
    except Exception as e:
        print e.message
        return HttpResponse('Error')
    return HttpResponse('Success')


@csrf_exempt
def save_step(request):
    # import pdb;pdb.set_trace()
    # onboard_id = int(request.user.id)
    # step_name = "Orientation"
    onboard_id = request.POST.get('onboard_id')
    step_name = request.POST.get('step_name')
    if step_name == "Orientation":
        userp = UserProfile.objects.filter(user=request.user)
        userp.update(evd_rep=True)
        # onboarding = userp.rolepreference_set.filter(role=step_name)
        # onboarding.onboardingstepstatus_set.all().filter(step__order = 1).update(status=True)
        step_status = 'Success'
    else:
        step_status = 'Error'
        if onboard_id and step_name:
            step_status = save_step_status(onboard_id, step_name)
    return HttpResponse(step_status)


def save_step_status(onboard_id, step_name):
    onboard = RolePreference.objects.get(id=int(onboard_id))
    date_submited = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
    step = onboard.onboardingstepstatus_set.all().filter(step__stepname=step_name)[0]
    step.status = True
    step.date_completed = date_submited
    try:
        step.save()
    except Exception as e:
        print e.message
        return 'Error'
    return 'Success'


def get_short_state_name(state):
    if state:
        words = state.strip().split()
        short_name = ''
        if len(words) > 1:
            for ent in words:
                short_name += ent[0]
        else:
            short_name = state[:2]
        return short_name.upper()
    return 'N/A'


@login_required
def render_demand(request):
    userp = request.user.userprofile
    demand = Demandslot.objects.filter(status='Unallocated')
    pref_medium = userp.pref_medium
    pref_slots = userp.pref_slots
    demand_reco1 = Demandslot.objects.none()
    if pref_medium and pref_medium != 'None':
        demand_reco1 = demand.filter(center__language=pref_medium)
    '''
    if userp.pref_days:
        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pref_d = userp.pref_days.split(';')
        pref_days = map((lambda x : [ y for y in week_days if x in y][0] ),pref_d)
        if not demand_reco1:
            demand_reco1 = demand
        demand_reco2 = demand_reco1.filter(day__in=pref_days)
    if pref_slots:
        pref_slots = pref_slots.split(';')
        for i,ent in enumerate(pref_slots):
            slot = ent.split('-')
            if not demand_reco2:
                demand_reco2 = demand
            if i==0:
                demand_reco3 = demand_reco2.filter(Q(start_time__gte=slot[0]) & Q(end_time__lte=slot[1]))
            else:
                demand_reco3 = demand_reco3 | demand_reco2.filter(Q(start_time__gte=slot[0]) & Q(end_time__lte=slot[1]))
    if demand_reco3.count() > 1:
        resp_demand = random.sample(demand_reco3,2)
    elif demand_reco2.count() > 1:
        resp_demand = random.sample(demand_reco2,2)
    elif demand_reco1.count() > 1:
        resp_demand = random.sample(demand_reco1,2)
    else:
        resp_demand = random.sample(demand,2)
    '''
    if demand_reco1.count() > 1:
        resp_demand = random.sample(demand_reco1, 2)
    else:
        resp_demand = random.sample(demand, 2)
    # Inserting custom attributes and conversion to JSON
    resp = []
    for ent in resp_demand:
        demand_dict = model_to_dict(ent)
        demand_dict['center_name'] = ent.center.name
        demand_dict['center_short_name'] = get_short_state_name(ent.center.state)
        demand_dict['start_time'] = ent.start_time.strftime('%I:%M %P')
        demand_dict['end_time'] = ent.end_time.strftime('%I:%M %P')
        demand_dict['language'] = ent.center.language
        resp.append(demand_dict)

    return HttpResponse(simplejson.dumps({'demand': resp}), mimetype='application/json')


def get_facebook_member_token(member_id='100011607874861'):
    admin_token = '1756803257874199|6qdzMuw3ZJDfICOTw5ICKy17o0c'
    member_token = ''
    values = {
        'access_token': 'DQVJ0ay1hUXhUb3otdnFPVmJEeGdfX3d3REpPclJzdlVVUUxUN1hIbXhfcXVDdDZAlRDJzWGpaMlc0aG9HcEIwdDBBZA3BWOHFLS0phblRickRnMVg1cXhYbUxVWG96Nk5TVjN2MG5JeHpuQ0xWaklpVXNVMFNtcjl1b3dpZADF2czNFa05CcG8wSHFMTlkzNC1ZAbDg3TFhkaDN6NURSSVl0LWc0eUZAXM3RzenlBZAWJJNWpSekhKQnJBa25tY19aMGNiTWNPS3ZAMaUt5WnVLVkZAjXwZDZD',
        'fields': 'impersonate_token',
    }
    request_url = 'https://graph.facebook.com/' + member_id + '/?fields=' + values['fields'] + '&access_token=' + \
                  values['access_token']
    try:
        response = urllib2.urlopen(request_url).read()
    except urllib2.HTTPError as e:
        return member_token

    if response:
        response = json.loads(response)
        member_token = response['id']
    return member_token


def evd_fb_feed(request):
    member_token = get_facebook_member_token()
    fbatwork_id = ''
    mem_data = {}
    if request.user.is_authenticated():
        userp = request.user.userprofile
        fbatwork_id = userp.fbatwork_id
        if fbatwork_id:
            mem_fb_id = request.user.userprofile.fbatwork_id
            mem_token = get_facebook_member_token(mem_fb_id)
            if mem_token:
                mem_data['fb_id'] = mem_fb_id
                mem_data['member_token'] = mem_token
            else:
                request.user.userprofile.fbatwork_id = ""
                request.user.userprofile.fb_member_token = ""
                request.user.userprofile.save()

    _data = [{'member_token': member_token, 'fb_id': '100011607874861'}]
    if mem_data:
        _data.append(mem_data)
    save_user_activity(request, 'Joined Community', 'Page Visit')
    return render_response(request, 'new_evidyaloka_fb_feed.html',
                           {'mem_data': simplejson.dumps(_data), 'fb_id': fbatwork_id})


def se_response_sheet(request):
    SeObjects = SelfEvaluation.objects.filter().order_by("-id")
    
    SeDetails = OrderedDict()

    for SeObject in SeObjects:
        SeDetails[SeObject.id] = {}
        try:
            SeDetails[SeObject.id]['name'] = SeObject.userp.user.username
            SeDetails[SeObject.id]['userid'] = SeObject.userp.user.id
            SeDetails[SeObject.id]['role'] = SeObject.role_preference.role.name
            SeDetails[SeObject.id]['email'] = SeObject.userp.user.email
            SeDetails[SeObject.id]['date_submitted'] = SeObject.date_submited
            SeDetails[SeObject.id]['se_form'] = SeObject.se_form
        except:
            SeDetails[SeObject.id]['name'] = ""
            SeDetails[SeObject.id]['userid'] = ""
            SeDetails[SeObject.id]['role'] = ""
            SeDetails[SeObject.id]['email'] = ""
            SeDetails[SeObject.id]['date_submitted'] = ""
            SeDetails[SeObject.id]['se_form'] = ""
    if request.user.is_authenticated:
        save_user_activity(request, 'Viewed Page:Dashboard - Self Evaluation Responses', 'Page Visit')
    return render_response(request, 'self_evaluation_response.html', {'SeDetails': SeDetails})


# -------------- Edit My eVidyaloka Rewamp ---------------#

# -----------Calender Api web_hook -------------#


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    flags = None
    credential_path = 'calendar-python-creds.json'
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if credentials.access_token_expired:
        access_token = credentials.get_access_token()
        print 'Storing creds'
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_gcal_events():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    try:
        eventObj = SelectionDiscussion.objects.latest('updated_at')
        nextSyncToken = eventObj.nextSyncToken
    except:
        nextSyncToken = None
    eventsResult = service.events().list(
        calendarId='primary', singleEvents=True, syncToken=nextSyncToken
    ).execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start)
    result = {'events': events, 'nextSyncToken': eventsResult['nextSyncToken']}
    return result


@csrf_exempt
def gcalender_api_callback(request):
    with open('cal_log.txt', 'w') as f:
        channel_expiry = request.META.get('HTTP_X_GOOG_CHANNEL_EXPIRATION')
        resource_id = str(request.META.get('HTTP_X_GOOG_RESOURCE_ID'))
        channel_id = str(request.META.get('HTTP_X_GOOG_CHANNEL_ID'))
        if channel_expiry:
            channel_expiry = datetime.datetime.strptime(channel_expiry, '%a, %d %b %Y %H:%M:%S GMT')
        f.write(str(request))
        events_ = get_gcal_events()
        nextSyncToken = events_['nextSyncToken']
        for events in events_['events']:
            status = events['status']
            start_time = events['start']
            end_time = events['end']
            event_id = events['id']
            updated_at = events['updated']
            try:
                description = events['description']
                description = description.split('\n')
                description = filter(None, description)
                item_list = []
                for item in description:
                    if "Booking made at" in item:
                        booked_at = item.replace("Booking made at ", "")
                    else:
                        temp = item.split(':')
                        item_list.append(temp)
                desc = {ent[0]: ent[1] for ent in item_list}
                first_name = desc['First Name']
                last_name = desc['Last Name']
                email = desc['Email'].replace(' ', '')
                skype_id = desc['Skype id']
                link_ref = desc['YCBM link ref']
                ref = desc['Ref']
                user = User.objects.get(id=656)
                userp = user.userprofile
                obj, created = SelectionDiscussion.objects.get_or_create(event_id=event_id, userp=userp)
                obj.nextSyncToken = nextSyncToken
                obj.status = status
                obj.start_time = datetime.datetime.strptime(start_time['dateTime'], "%Y-%m-%dT%H:%M:%S+05:30")
                obj.end_time = datetime.datetime.strptime(end_time['dateTime'], "%Y-%m-%dT%H:%M:%S+05:30")
                obj.email = email
                obj.first_name = first_name
                obj.last_name = last_name
                obj.skype_id = skype_id
                obj.link_ref = link_ref
                obj.updated_at = datetime.datetime.strptime(updated_at[:19], "%Y-%m-%dT%H:%M:%S")
                obj.channel_expiry = channel_expiry
                obj.channel_id = channel_id
                obj.resource_id = resource_id
                obj.save()
                f.write(str(obj.id) + '\n')
            except:
                pass

    return HttpResponse('Success')


# -----------Calender Api web_hook -------------#

# rubaru
def rubaru_main(request):
    return render_response(request, 'rubaru_17.html')


def rubaru_register(request):
    data = json.loads(request.GET.get('data'))
    new_reg_obj = EventRegistration(event_name=data['event'], name=data['name'], email=data['email'],
                                    phone=data['mobile'], number_of_participants=data['persons'],
                                    organisation=data['organisation'], referred_by=data['referred_by'])
    new_reg_obj.save()

    subject = "Thank You for registering your participation in Rubaru '16 by eVidyaloka."
    content = "Dear " + data[
        'name'] + " ,<br><p>Thank you for registering your participation in Rubaru '16 on December 3rd 2016!</p>" + \
              "<p><strong>" + str(
        new_reg_obj.id) + "</strong> is your registration number. Please quote this number at " + \
              "the registration counter in the Venue, prior to the entry.</p><p>For any queries, please contact Dhathri P," + \
              "via &lt;dhathrip@evidyaloka.org&gt;,with your full name and registration number.</p>" + \
              "<p>For regular updates please visit this page:" + WEB_BASE_URL + "rubaru/ </p>" + \
              "<p>Best Regards,<br>Team eVidyaloka</p>"

    recipients = "dhathrip@evidyaloka.org,%s" % data['email']
    userid = ''
    if request.user:
        userid = request.user.id
    insert_into_alerts(subject, content, ','.join(recipients), userid, 'email')

    return HttpResponse("success")


# manage slots UI

def save_slots(request):
    added_slots = json.loads(request.GET.get('data'))
    center = request.GET.get('center')
    offering_ID = request.GET.get('offering_id', None)
    is_new_slot = request.GET.get('is_new_slot', None)
    center_obj = Center.objects.get(id=int(center))
    offering_obj = None
    if offering_ID: offering_obj = get_object_or_none(Offering, pk=int(offering_ID))
    type = 2 if offering_obj else 1
    slot_count = 0
    for slot in added_slots:
        ampm1 = slot['start_time'][-2:]
        slot['start_time'] = slot['start_time'][:-2]
        slot['start_time'] = slot['start_time'] + " " + ampm1.upper()
        ampm2 = slot['end_time'][-2:]
        slot['end_time'] = slot['end_time'][:-2]
        slot['end_time'] = slot['end_time'] + " " + ampm2.upper()
        
        if is_new_slot == 'true':
            new_slot = Demandslot(center=center_obj, day=slot['day'], created_by=request.user, updated_by=request.user,
                    start_time=datetime.datetime.strptime(slot['start_time'], '%I:%M %p').time(), type=type,
                    end_time=datetime.datetime.strptime(slot['end_time'], '%I:%M %p').time(),offering = offering_obj)
            new_slot.save()
        else:
            old_slot = Demandslot.objects.filter(center=center_obj, day=slot['day'], created_by=request.user, updated_by=request.user,
                            start_time=datetime.datetime.strptime(slot['start_time'], '%I:%M %p').time(),
                            end_time=datetime.datetime.strptime(slot['end_time'], '%I:%M %p').time())
            if old_slot:
                old_slot[0].offering = offering_obj
                old_slot[0].type = type
                old_slot[0].save()
        slot_count+=1
        if offering_obj and slot_count>=2:break

    return HttpResponse(slot_count)


@login_required
def delete_slots(request):
    slot_list = json.loads(request.GET.get('data'))
    center = request.GET.get('center')
    offering_id = request.GET.get('offering_id')
    center_obj = Center.objects.get(id=int(center))
    offerObj = None
    if offering_id:
        try:
            offerObj = Offering.objects.get(pk=int(offering_id))
        except:
            pass

    for slot in slot_list:
        slot_to_del = Demandslot.objects.filter(center=center_obj, day=slot['day'],
                                                start_time=datetime.datetime.strptime(slot['start_time'],
                                                                                    '%I:%M %p').time(), \
                                                end_time=datetime.datetime.strptime(slot['end_time'],
                                                                                    '%I:%M %p').time(),offering = offerObj)
        if offerObj:
            slot_to_del.update(offering = None)
        else:
            slot_to_del[0].delete()

    return HttpResponse("Success")


@login_required
def publish_slots(request):
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

    # if request.user.is_superuser:
    #     slots_obj = SelectionDiscussionSlot.objects.filter(status="Booked")
    # elif request.user.partner_set.all():
    #     slots_obj = SelectionDiscussionSlot.objects.filter(status="Booked",userp__in=UserProfile.objects.filter(referencechannel__partner=request.user.partner_set.all()[0]))
    # else:
    #     slots_obj = SelectionDiscussionSlot.objects.filter(status="Booked",userp=request.user.userprofile)
    # publish_slots = slots_obj.values('start_time', 'end_time', 'status').order_by('-start_time')

    publish_slots_list = []
    for publish_slot in publish_slots:
        publish_slot['start_time'] = datetime.datetime.strftime(publish_slot['start_time'], '%b %d %Y %I:%M%p')
        publish_slot['end_time'] = datetime.time.strftime(publish_slot['end_time'], '%I:%M%p')
        publish_slots_list.append({"start_date": publish_slot['start_time'].rsplit(' ', 1)[0],
                                   "start_time": publish_slot['start_time'].rsplit(' ', 1)[1], \
                                   "end_time": publish_slot['end_time'],"role":publish_slot['publisher_role_id'], "status": publish_slot['status'],"id": publish_slot['id']})
    return HttpResponse(simplejson.dumps(publish_slots_list), mimetype='application/json')
    # return HttpResponse(simplejson.dumps(user_p_dict),mimetype='application/json')


@login_required
def save_publish_slots(request):
    # date_range = request.GET.get('date_range').split(' - ')
    startdate = datetime.datetime.strptime(request.GET.get('start_date'), '%m/%d/%Y')
    enddate = datetime.datetime.strptime(request.GET.get('end_date'), '%m/%d/%Y')
    days = json.loads(request.GET.get("days"))
    slot_count = request.GET.get('slots_counts')
    group_sots = request.GET.get('group_sots')
    print "group_sots",group_sots
    delta = enddate - startdate
    added_count = 0
    duplicate_count = 0
    role_id =''
    print "slot_count",slot_count
    starttime = datetime.datetime.strptime(request.GET.get("start_time"), "%I:%M%p")
    endtime = datetime.datetime.strptime(request.GET.get("end_time"), "%I:%M%p")
    is_panelmember = False
    if has_role(request.user.userprofile, "TSD Panel Member") or has_pref_role(request.user.userprofile,
                                                                               "TSD Panel Member"):
        is_panelmember = True
        role_id = '7'
    if has_role(request.user.userprofile, "CSD Panel Member") or has_pref_role(request.user.userprofile,
                                                                               "CSD Panel Member"):
        is_csdpanelmember = True
        role_id = '17'
    # starttime = datetime.datetime.fromtimestamp(float(request.GET.get("start_time"))/1000.0)+ datetime.timedelta(minutes = -30)
    # endtime  = datetime.datetime.fromtimestamp(float(request.GET.get("end_time"))/1000.0)+ datetime.timedelta(minutes = -30)

    startdate = startdate.replace(hour=starttime.time().hour, minute=starttime.time().minute)

    # endtime = enddate
    # endtime = endtime.replace(year=startdate.year,day=startdate.day,month=startdate.month)
    if group_sots :
        tot_slots = int(((endtime - starttime).total_seconds() / 60) / 60)
        print "tot_slots11",tot_slots
    else:
        tot_slots = int(((endtime - starttime).total_seconds() / 60) / 30)
        print "tot_slots22",tot_slots
    if startdate.date() == enddate.date():
        i = 0
        start = startdate
        
        while i < tot_slots:
            if group_sots:
                print("yesss")
                slot_end = start + timedelta(minutes=60)
                print "fffffff",slot_end
            else:
                slot_end = start + timedelta(minutes=30)
                print "fffffff22222",slot_end
            i = i + 1
            try:
                for slot in range(0,int(slot_count)):
                    print "sssssaaaaaasss",slot
                    if is_panelmember or is_csdpanelmember:
                    
                        new_slot = SelectionDiscussionSlot(start_time=start, end_time=slot_end.time(),publisher_role_id=role_id,
                                                       tsd_panel_member=request.user.userprofile,outcome = 'Assigned')
                        new_slot.save()
                        added_count = added_count+1
                    else:
                        new_slot = SelectionDiscussionSlot(start_time=start, end_time=slot_end.time())
                        new_slot.save()
                        added_count = added_count+1
            except:
                import traceback
                traceback.print_exc()
                duplicate_count = 1
            start = slot_end
    else:
        for single_date in daterange(startdate, enddate):
            if single_date.strftime("%A") in days:
                i = 0;
                start = single_date.replace(hour=starttime.time().hour, minute=starttime.time().minute)
                while i < tot_slots:
                    if group_sots:
                        slot_end = start + timedelta(minutes=60)
                    else:
                        slot_end = start + timedelta(minutes=30)
                    i = i + 1;
                    try:
                        for slot in range(0,int(slot_count)):
                            print "ssssss",slot
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

    # datetime.datetime.strptime(startdate, '%m/%d/%Y %I:%M %p')
    # datetime.datetime.strptime(endtime, '%I:%M %p')

    return HttpResponse(
        str(added_count) + " Slot(s) Added Successfully<br>" + str(duplicate_count) + " Duplicate(s) found")


def daterange(start_date, end_date):
    for n in range(int((end_date.date() - start_date.date()).days) + 1):
        yield start_date + timedelta(n)


@login_required
def delete_publish_slots(request):
    slot_list = json.loads(request.GET.get('data'))
    for slot in slot_list:
        id = slot['id']
        slot_to_del = SelectionDiscussionSlot.objects.get(pk = int(id))
        slot_to_del.delete()
    return HttpResponse("Success")


@login_required
def book_sd_slots(request):
    role = request.GET.get('slots_role')
    role_active = request.GET.get('role_name')
    taskId = request.GET.get('id')
    performedOn_userId = request.GET.get('uid')
    tabName = request.GET.get('tab')
    is_teacher=False; is_content_developer=False; is_flt_teacher=False
    
    if has_pref_role(request.user.userprofile, "Content Developer"):is_content_developer = True
    if has_pref_role(request.user.userprofile, 'Facilitator Teacher'):is_flt_teacher = True
    if has_pref_role(request.user.userprofile, "Teacher"):is_teacher = True
    
    if role==' ' or role is None:
        is_content_developer = False; is_teacher = False
        if has_pref_role(request.user.userprofile, "Content Developer"): is_content_developer = True; role = "Content Developer"
        if has_pref_role(request.user.userprofile, "Teacher"): is_teacher = True; role = "Teacher"
        if has_pref_role(request.user.userprofile, 'Facilitator Teacher'):is_flt_teacher = True; role = "Facilitator Teacher"
    elif role_active ==  "Content Developer":
        role =   "Content Developer"
    elif role_active ==  "Facilitator Teacher":
        role =   "Facilitator Teacher"
        
    TSD_status = ''
    today = datetime.datetime.now()
    
    print "role",request.user.userprofile.role.values_list("name",flat=True)
    ref = ReferenceChannel.objects.get(id = request.user.userprofile.referencechannel.id)
    without_partner = False
   
    if role == "Content Developer": role_id = '19'
    elif role == 'Facilitator Teacher': role_id = '20'
    else: 
        role == 'Teacher' 
        role_id = '7'

    print(role, role_id)
    
    if request.user.is_superuser or ref is None:
        without_partner = True

    elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
        partner = None
        if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
            partner = Partner.objects.get(contactperson = request.user)
        else:
            partner = ref.partner

        if partner and len(partner.partnertype.filter(name = 'Delivery Partner')) > 0: 
            if role_id:
                publish_slots = list(SelectionDiscussionSlot.objects.filter(userp = None,
                        tsd_panel_member__referencechannel__partner = partner).filter(publisher_role_id = role_id,
                        start_time__gte=today).values_list('start_time', flat=True).dates('start_time', 'month', order='DESC'))
            else:
                publish_slots = list(SelectionDiscussionSlot.objects.filter(userp = None,

                        tsd_panel_member__referencechannel__partner = partner).filter(
                        start_time__gte=today).values_list('start_time', flat=True).dates('start_time', 'month', order='DESC'))
            
        else:
            without_partner = True
    if without_partner:
        if role_id:
            
            publish_slots = list(SelectionDiscussionSlot.objects.values_list('start_time', flat=True).filter(userp = None).filter(publisher_role_id = role_id,
                        start_time__gte=today).dates('start_time', 'month', order='DESC'))
            if not publish_slots:
                publish_slots = list(SelectionDiscussionSlot.objects.values_list('start_time', flat=True).filter(userp = None).filter(
                        start_time__gte=today).dates('start_time', 'month', order='DESC'))
        else:
            publish_slots = list(SelectionDiscussionSlot.objects.values_list('start_time', flat=True).filter(userp = None).filter(
                        start_time__gte=today).dates('start_time', 'month', order='DESC'))
    publish_slots[:] = [datetime.datetime.strftime(publish_slot, '%b %Y') for publish_slot in publish_slots]
    pub_role =''
    try:
        if performedOn_userId is not None:
            user = User.objects.get(pk=performedOn_userId)
            currently_booked = SelectionDiscussionSlot.objects.filter(userp=request.user.userprofile)
        else:
            currently_booked = SelectionDiscussionSlot.objects.filter(userp=request.user.userprofile)
            for r in currently_booked:
                if str(r.publisher_role.id) == str(role_id):
                    start_time = r.start_time
                    end_time = r.end_time
                    TSD_status = r.outcome
                    pub_role = str(r.publisher_role.id)
        
    except:
        start_time = ''
        end_time = ''

    if role_id != pub_role:
        TSD_status = None
        start_time = None
        end_time = None    
    
    save_user_activity(request, 'Viewed Page:Selection Discussion Slot ', 'Page Visit')
    return render_response(request, 'book_sd_slots.html',
                           {'month_list': publish_slots,'role':role, 'start_time': start_time, 'end_time': end_time,'is_teacher':is_teacher, 'is_flt_teacher':is_flt_teacher,
                            'taskId': taskId,'is_content_developer':is_content_developer, 'performedOn_userId': performedOn_userId, 'tab': tabName,
                            'TSD_status': TSD_status})


@login_required
def get_sd_slot_details(request):
    typ = request.GET.get("type")
    role = request.GET.get("role")
    print "rolqqqqqqqqqqqe",role,typ
    if role =='Content Developer':
        role_id= '19'
    else:
        role_id = '7'
    today = datetime.datetime.now()
    ref = ReferenceChannel.objects.get(id = request.user.userprofile.referencechannel.id)
    without_partner = False
    if typ == "month":
        date = datetime.datetime.strptime(request.GET.get("data"), "%b %Y")

        if request.user.is_superuser or ref is None:
            without_partner = True
        elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
            partner = None
            if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
                partner = Partner.objects.get(contactperson = request.user)
            else:
                partner = ref.partner
            if partner and len(partner.partnertype.filter(name = 'Delivery Partner')) > 0:
                date_list = list(SelectionDiscussionSlot.objects.filter(status="Not Booked",publisher_role_id = role_id,
                        start_time__year=date.year,start_time__month=date.month,tsd_panel_member__referencechannel__partner = partner).filter(
                        start_time__gte=today).values_list('start_time', flat=True).dates('start_time', 'day', order='DESC'))
               
            else:
                without_partner = True
        if without_partner:

            date_list = list(SelectionDiscussionSlot.objects.values_list('start_time', flat=True).filter(status="Not Booked",publisher_role_id =role_id,
                            start_time__year=date.year,start_time__month=date.month).filter(
                            start_time__gte=today).dates('start_time', 'day', order='DESC'))

        date_list[:] = [datetime.datetime.strftime(date, '%b %d') for date in date_list]
       
        return HttpResponse(simplejson.dumps(date_list), mimetype='application/json')
    elif typ == "date":
        year = request.GET.get("month").split()[1]
        date = datetime.datetime.strptime(request.GET.get("data"), "%b %d")
        if request.user.is_superuser or ref is None:
            without_partner = True
        elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
            if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
                partner = Partner.objects.get(contactperson = request.user)
            else:
                partner = ref.partner
            if partner and len(partner.partnertype.filter(name = 'Delivery Partner')) > 0:

                slot_obj = SelectionDiscussionSlot.objects.filter(status="Not Booked",publisher_role_id =role_id,
                         start_time__year=year,start_time__month=date.month,tsd_panel_member__referencechannel__partner = partner,
                            start_time__day=date.day).values('start_time', 'end_time','id').filter(
                            start_time__gte=datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)).order_by("start_time")
               
            else:
                without_partner = True
        if without_partner:
            slot_obj = SelectionDiscussionSlot.objects.values('start_time', 'end_time','id').filter(status="Not Booked",publisher_role_id = role_id,
                                                                                            start_time__year=year,
                                                                                            start_time__month=date.month, \
                                                                                            start_time__day=date.day).filter(
                            start_time__gte=datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)).order_by("start_time")

        print "slot_obj"  ,slot_obj  

        slot_list = []
        tot_slot = []
        count_slot_tot = []
        count_slot = []
        for slot in slot_obj:
            slot_time = str(datetime.datetime.strftime(slot['start_time'], "%I:%M %p")) + str(datetime.time.strftime(slot['end_time'], "%I:%M %p"))
            count_slot_tot.append(slot_time)
            if slot_time not in tot_slot:
                tot_slot.append(slot_time)
                slot_list.append({'start_time':datetime.datetime.strftime(slot['start_time'], "%I:%M %p"),
                                'end_time':datetime.time.strftime(slot['end_time'], "%I:%M %p"),'id':slot['id']})
        for slot in tot_slot:
            count_slot.append(count_slot_tot.count(slot))
        print("dare",slot_list)
        print("dare",count_slot)
        slot_list_tot = {}
        slot_list_tot['slot_list'] = slot_list
        slot_list_tot['count_slot'] = count_slot
        return HttpResponse(simplejson.dumps(slot_list_tot), mimetype='application/json')


@login_required
def book_or_release_sd_slot(request):
    typ = request.GET.get("type")
    user_id =''
    if  request.user.is_superuser:
        user_id = request.GET.get("user_id")
    role = request.GET.get("role")

    print "role",role
    id = request.GET.get("id")
    role_id = request.GET.get("role_id", "")
    slot_id = request.GET.get("slot_id", "")
    platform = request.GET.get('platform', '')
    performedOn_userId = request.GET.get('performedOn_userId', '')
 
    mobile_response = {"status": 0, "message": "", "data": {}}
    if performedOn_userId is not None and performedOn_userId != 'None' and performedOn_userId != 'None ' and performedOn_userId != '':
        user = User.objects.get(pk=performedOn_userId)

        userpId = user.userprofile.id
        userEmail = user.email
        userPhone = user.userprofile.phone
    else:
        # userpId = request.user.id
        userpId = request.user.userprofile.id

        user = request.user
        userEmail = request.user.email
        userPhone = request.user.userprofile.phone
    ref = ReferenceChannel.objects.get(id = request.user.userprofile.referencechannel.id)
    if typ == "book":
        if slot_id:
            try:
                slot_obj = SelectionDiscussionSlot.objects.get(id=slot_id)

            except SelectionDiscussionSlot.DoesNotExist:
                message = "SelectionDiscussionSlot with slot_id: {}, Does Not Exist".format(slot_id)
                if platform:
                    mobile_response["status"] = 1
                    mobile_response["message"] = message
                    return HttpResponse(json.dumps(mobile_response), content_type='application/json')
                else:
                    return HttpResponse(message)
        else:
            try:
                slot_obj = SelectionDiscussionSlot.objects.get(pk = int(id))

            except SelectionDiscussionSlot.DoesNotExist:
                return HttpResponse("Error")
        if user_id and request.user.is_superuser:
            user_id = User.objects.get(id = user_id)
            history_obj = SelectionDiscussionSlotHistory.objects.create(slot=slot_obj, userp=user_id.userprofile, booked_date=datetime.datetime.utcnow() + timedelta(hours=5, minutes=30))
        else:
            history_obj = SelectionDiscussionSlotHistory.objects.create(slot=slot_obj, userp=user.userprofile, booked_date=datetime.datetime.utcnow() + timedelta(hours=5, minutes=30))
        if role_id:
            try:
                role_obj = Role.objects.get(id=role_id)
            except Role.DoesNotExist:
                message = "Role entry with role_id: {}, Does Not Exist".format(role_id)
                if platform:
                    mobile_response["status"] = 1
                    mobile_response["message"] = message
                    return HttpResponse(json.dumps(mobile_response), content_type='application/json')
                else:
                    return HttpResponse(message)
        else:
            try:
               role_obj = Role.objects.get(name=role.replace("_", " "))
            except Role.DoesNotExist:
                message = "Role entry with Name: {}, Does Not Exist".format(role)
                return HttpResponse(message)

        # userp = UserProfile.objects.filter(id=request.user.id)
        
        
        if performedOn_userId is not None and performedOn_userId != 'None' and performedOn_userId != 'None ':
            
                slot_obj.userp_id = userpId 
          
        else:
            if user_id and request.user.is_superuser:
                print "fghdrfsrdfsd"
                # user_id = User.objects.get(id = user_id)
                print "saewas",user_id.userprofile.id
                slot_obj.userp_id= user_id.userprofile.id
            else:
                slot_obj.userp_id = request.user.userprofile.id

        slot_obj.role = role_obj
        slot_obj.booked_date = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
        slot_obj.status = "Booked"
        date_slot = str(slot_obj.start_time.date())
        time_slot = str(slot_obj.start_time.time())
        userp_id = str(slot_obj.userp_id)
        print("status - - - -",slot_obj.status,user_id,date_slot,time_slot,userp_id)
        if (slot_obj.status == "Booked"):
            try:
                print("Commenting temporarily")
                pass
                #thread.start_new_thread(confrirm_booking, (userp_id,date_slot,time_slot))
            except Exception:
                pass
        slot_obj.save()
        userProfileObj = get_object_or_none(UserProfile, user = request.user)
        if userProfileObj:
            userProfileObj.dicussion_outcome = 'Scheduled'
            userProfileObj.save()
        recipients = []
        if slot_obj.tsd_panel_member:
            recipients = [slot_obj.tsd_panel_member.user.email]
        # intimation mail
        start_time = slot_obj.start_time.strftime("%B %d %Y, From %I:%M %p")
        end_time = slot_obj.end_time.strftime("%I:%M %p")
        slot_details = "{} to {}".format(start_time, end_time)
        host = 'http://' + request.META['HTTP_HOST']
        args = {'user': user, 'role': role, 'slot': slot_details, 'type': 'Booking', 'host': host}
        subject_template = 'mail/_tsd_slot_book/short.txt'
        subject = get_mail_content(subject_template, args).replace('\n', '')
        recipients.extend(["discussions@evidyaloka.org",userEmail])
        body_template = 'mail/_tsd_slot_book/full.html'
        body = get_mail_content(body_template, args)
        for m_type in ['email', 'sms']:
            if m_type == 'sms':
                subject = 'Booking confirmed for Selection Discussion with eVidyaloka.\n'
                subject += 'Time: %s\n' % slot_details
                subject += 'Call +91 80 46808983 or Email : discussions@evidyaloka.org for any queries'
                body = ''
                phone = userPhone
                if phone and re.search(VALIDATE_PHONE_RE, phone):
                    recipients = [phone]
                else:
                    recipients = []
            if recipients:
                print("Commenting temporarily")
                pass
                #insert_into_alerts(subject, body, ','.join(recipients), userpId, m_type,'book_tsd')

        if platform:
            return HttpResponse(json.dumps(mobile_response), content_type='application/json')
        else:
            save_user_activity(request, "Slot Booked Successfully", "Action")
            return HttpResponse("Slot Booked Successfully")

    else:
        if slot_id:
            try:
                slot_obj = SelectionDiscussionSlot.objects.get(id=slot_id)
            except SelectionDiscussionSlot.DoesNotExist:
                message = "SelectionDiscussionSlot with slot_id: {}, Does Not Exist".format(slot_id)
                if platform:
                    mobile_response["status"] = 1
                    mobile_response["message"] = message
                    return HttpResponse(json.dumps(mobile_response), content_type='application/json')
                else:
                    return HttpResponse(message)
        else:
            try:
                if request.user.is_superuser:
                    print "user_id",user_id
                    user_id = User.objects.get(id = user_id)
                    slot_obj = SelectionDiscussionSlot.objects.filter(userp_id=user_id.userprofile)
                    print "qqqqqqqqqqqslot_obj",slot_obj,user_id
                else:
                    slot_obj = SelectionDiscussionSlot.objects.filter(userp_id=userpId)
                print "slot_obj",slot_obj
                if slot_obj:
                    slot_obj = slot_obj[0]
                print (" slot_obj", slot_obj)
            except SelectionDiscussionSlot.DoesNotExist:
                message = "SelectionDiscussionSlot with the Logged in User, Does Not Exist"
                return HttpResponse(message)

        try:
            history_obj = SelectionDiscussionSlotHistory.objects.filter(slot=slot_obj, userp=user.userprofile).latest(
                'booked_date')
            history_obj.released_date = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
            history_obj.status = 'Released'
            history_obj.save()
            userProfileObj = get_object_or_none(UserProfile, id = request.user.userprofile.id)
            if userProfileObj:
                userProfileObj.dicussion_outcome = 'Not Scheduled'
                userProfileObj.save()
        except SelectionDiscussionSlotHistory.DoesNotExist:
            pass

        slot_obj.userp = None
        slot_obj.booked_date = None
        slot_obj.status = "Not Booked"
        slot_obj.save()

        # intimation mail
        slot_details = datetime.datetime.strftime(slot_obj.start_time,
                                                  "%b %d, %Y From %I:%M %p to ") + datetime.time.strftime(
            slot_obj.end_time, "%I:%M %p")
        args = {'user': user, 'role': role, 'slot': slot_details, 'type': 'Releasing'}
        subject_template = 'mail/_tsd_slot_book/short.txt'
        subject = get_mail_content(subject_template, args)
        body_template = 'mail/_tsd_slot_book/full.txt'
        body = get_mail_content(body_template, args)
        recipients = ["discussions@evidyaloka.org",
                      userEmail]
        # recipients.append('akhilraj@headrun.com') # he is headrun developer, he should not get emailer
        #insert_into_alerts(subject, body, ','.join(recipients), userpId, 'email','release_tsd')

        if platform:
            return HttpResponse(json.dumps(mobile_response), content_type='application/json')
        else:
            save_user_activity(request, "Slot Released Successfully", "Action")
            return HttpResponse("Slot Released Successfully")

def confrirm_booking(user_id,booking_date,booking_time):
    from django.conf import settings
    user_details = User.objects.get(id = user_id)    
    name = str(user_details.first_name) + str(user_details.last_name)
    sub = " eVidyaloka - Selection Discussion Booking confirmed -" + user_id
    body = "Dear " + name +",\n\
\n\
Thank you for progressing with the on-boarding process to start content development.\n\
\n\
Your booking for Selection Discussion is confirmed:\n\
\n\
Date : "+ booking_date+"\n\
\n\
Time:  "+ booking_time+"\n\
\n\
Duration: 30 Mins\n\
\n\
Skype ID for discussion: eVidyaloka content / (live:.cid.e9b84d9b9583f663)\n\
\n\
We will have our Panel member awaiting online on Skype on the booked time. Please add eVidyaloka content to your Skype contacts, and we will reach out to you. \n\
\n\
Note: Discussion will be taken on laptop and not through phone.\n\
\n\
For any change of booking, please do log in and visit Manage Booking and Change your discussion slot.\n\
\n\
https://www.evidyaloka.org//book_sd_slots/#teacher\n\
\n\
Manage Booking\n\
\n\
For any queries, please do write back to submitcontent@evidyaloka.org\n\
\n\
\n\
Regards,\n\
eVidyaloka content development team\n\
"
    settings = settings.DEFAULT_FROM_EMAIL
    to = user_details.email
    recipients = to.split(",")
    send_mail(sub, body,settings,recipients)
    

# @login_required
def volunteer_heatmap(request):
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                         user=settings.DATABASES['default']['USER'],
                         passwd=settings.DATABASES['default']['PASSWORD'],
                         db=settings.DATABASES['default']['NAME'],
                         charset="utf8",
                         use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)

    dict_cur.execute("SELECT distinct(pref_medium) from web_userprofile where pref_medium !='' and pref_medium!='None'")
    language_list = [item['pref_medium'] for item in dict_cur.fetchall()]
    dict_cur.execute("SELECT distinct(name) as referencechannel,id from web_referencechannel")
    ref_channel_list=[]
    for item in dict_cur.fetchall():
        ref_channel_list.append(item)
    dict_cur.execute("SELECT name from web_role where name != \"TSD Panel Member\"")
    role_list = [item['name'] for item in dict_cur.fetchall()]

    date_filter = request.GET.get("type")
    today = datetime.datetime.now()
    before_one_month = today - datetime.timedelta(days=30)
    from_date = str(datetime.datetime.strptime(request.GET.get("from_date"), "%d-%m-%Y").date()) if request.GET.get(
        "from_date") else \
        datetime.datetime.strftime(before_one_month, "%Y-%m-%d")  # "2016-01-10"
    to_date = str(datetime.datetime.strptime(request.GET.get("to_date"), "%d-%m-%Y").date()) if request.GET.get(
        "to_date") else \
        datetime.datetime.strftime(today, "%Y-%m-%d")  # "2016-01-11"
    language = "" if request.GET.get("language") == "all" else request.GET.get("language")
    ref_channel = "" if request.GET.get("ref_channel") == "all" else request.GET.get("ref_channel")
    role = "" if request.GET.get("role") == "all" else request.GET.get("role")

    if not request.GET.get("role"):
        role="Teacher"
    teacher = role == "Teacher"

    registred_users_query = ["SELECT COUNT(*) FROM auth_user U, web_userprofile UP where U.id = UP.user_id"]
    registred_users_query_joined_date = ["SELECT COUNT(*) FROM auth_user U, web_userprofile UP where U.id = UP.user_id and " \
    "DATE(U.date_joined) >= '{}'".format(from_date) + " and  DATE(U.date_joined) <= '{}'".format(to_date)]
    prof_comp_querry = ["SELECT DATE(U.date_joined), COUNT(DATE(U.date_joined)) FROM auth_user U, web_userprofile UP\
                                where U.id = UP.user_id and UP.profile_completion_status = 1"]
    orient_comp_querry = ["SELECT DATE(U.date_joined), COUNT(DATE(U.date_joined)) FROM auth_user U, web_userprofile UP where U.id = UP.user_id\
                                and UP.evd_rep = 1"]
    timeline_registered = ["SELECT DATE(U.date_joined), COUNT(DATE(U.date_joined)) FROM auth_user U, web_userprofile UP where U.id = UP.user_id"]

    recommended_query = [" SELECT COUNT(distinct((U.id)) as count FROM web_rolepreference RP,auth_user U,\
                                       web_userprofile UP where U.id = UP.user_id and RP.userprofile_id=UP.id \
                                       and RP.role_outcome='Recommended' and  " \
                         "DATE(RP.recommended_date) >= '{}'".format(
        from_date) + " and  DATE(RP.recommended_date) <= '{}'".format(to_date)]

    recommended_query_joined_date = [" SELECT COUNT(distinct((U.id))as count FROM web_rolepreference RP,auth_user U,\
                                       web_userprofile UP where U.id = UP.user_id and RP.userprofile_id=UP.id \
                                       and RP.role_outcome='Recommended' and  " \
                         "DATE(RP.recommended_date) >= '{}'".format(
        from_date) + " and  DATE(RP.recommended_date) <= '{}'".format(to_date)+"and DATE(U.date_joined) >= '{}'".format(
        from_date) + " and  DATE(U.date_joined) <= '{}'".format(to_date)]

    tsd_querry = ["SELECT COUNT(distinct((U.id))as count from auth_user U,web_selectiondiscussionslothistory SSH,\
                           web_userprofile UP where U.id = UP.user_id and UP.id = SSH.userp_id \
                           and SSH.status='Booked' and   DATE(SSH.booked_date) >= '{}'".format(
        from_date) + " and  DATE(SSH.booked_date) <= '{}'".format(to_date)]

    tsd_querry_joined_date=  ["SELECT COUNT(distinct((U.id)) as count from auth_user U,web_selectiondiscussionslothistory SSH,\
                           web_userprofile UP where U.id = UP.user_id and UP.id = SSH.userp_id \
                           and SSH.status='Booked' and   DATE(SSH.booked_date) >= '{}'".format(
        from_date) + " and  DATE(SSH.booked_date) <= '{}'".format(to_date)+ "and DATE(U.date_joined) >= '{}'".format(
        from_date) + " and  DATE(U.date_joined) <= '{}'".format(to_date)]

    demand_booked_query="SELECT COUNT(offteachmap.id) as count from web_offeringteachermapping offteachmap, web_offering off, auth_user U,\
        web_userprofile UP where U.id=UP.user_id and off.id=offteachmap.offering_id and offteachmap.teacher_id= U.id \
                        and DATE(offteachmap.booked_date) >= '{}'".format(
        from_date) + " and  DATE(offteachmap.booked_date) <= '{}'".format(to_date)

    demand_booked_query_joined_date="SELECT COUNT(offteachmap.id) as count from web_offeringteachermapping offteachmap, web_offering off, auth_user U,\
        web_userprofile UP where U.id=UP.user_id and off.id=offteachmap.offering_id and offteachmap.teacher_id= U.id \
                        and DATE(offteachmap.booked_date) >= '{}'".format(
        from_date) + " and  DATE(offteachmap.booked_date) <= '{}'".format(to_date)+"and DATE(U.date_joined) >= '{}'".format(
        from_date)+" and DATE(U.date_joined) <= '{}'".format(to_date)

    demand_assigned_query="SELECT COUNT(offteachmap.id) as count from web_offeringteachermapping offteachmap, web_offering off, auth_user U,\
        web_userprofile UP where U.id=UP.user_id and off.id=offteachmap.offering_id and offteachmap.teacher_id= U.id \
                         and DATE(offteachmap.assigned_date) >= '{}'".format(
        from_date) + " and  DATE(offteachmap.assigned_date) <= '{}'".format(to_date)

    demand_assigned_query_joined_date="SELECT COUNT(offteachmap.id) as count from web_offeringteachermapping offteachmap, web_offering off, auth_user U,\
        web_userprofile UP where U.id=UP.user_id and off.id=offteachmap.offering_id and offteachmap.teacher_id= U.id \
                         and DATE(offteachmap.assigned_date) >= '{}'".format(
        from_date) + " and  DATE(offteachmap.assigned_date) <= '{}'".format(to_date)+"and DATE(U.date_joined) >= '{}'".format(
        from_date)+" and DATE(U.date_joined) <= '{}'".format(to_date)

    demand_dropped_query="SELECT COUNT(distinct(offmap.offering_id)) as count from  web_offering off, auth_user U,\
            web_userprofile UP,web_offeringteachermapping offmap where U.id=UP.user_id and off.id=offmap.offering_id and offmap.teacher_id= U.id \
                            and   DATE(offmap.dropped_date) >= '{}'".format(
        from_date) + " and  DATE(offmap.dropped_date) <= '{}'".format(to_date)

    demand_dropped_query_joined_date="SELECT COUNT(distinct(offmap.offering_id)) as count from  web_offering off, auth_user U,\
            web_userprofile UP,web_offeringteachermapping offmap where U.id=UP.user_id and off.id=offmap.offering_id and offmap.teacher_id= U.id \
                            and   DATE(offmap.dropped_date) >= '{}'".format(
        from_date) + " and  DATE(offmap.dropped_date) <= '{}'".format(to_date)+" and DATE(U.date_joined) >= '{}'".format(
        from_date) + " and  DATE(U.date_joined) <= '{}'".format(to_date)


    if language:
        recommended_query.append(" and UP.pref_medium = \"{}\"".format(language))

        recommended_query_joined_date.append(" and UP.pref_medium = \"{}\"".format(language))

        tsd_querry.append(" and UP.pref_medium = \"{}\"".format(language))

        tsd_querry_joined_date.append(" and UP.pref_medium = \"{}\"".format(language))

        demand_booked_query=demand_booked_query +" and off.language = \"{}\"".format(language)

        demand_booked_query_joined_date=demand_booked_query_joined_date +" and off.language = \"{}\"".format(language)

        demand_assigned_query=demand_assigned_query +" and off.language = \"{}\"".format(language)

        demand_assigned_query_joined_date=demand_assigned_query_joined_date +" and off.language = \"{}\"".format(language)

        demand_dropped_query = demand_dropped_query +" and off.language = \"{}\"".format(language)

        demand_dropped_query_joined_date= demand_dropped_query_joined_date +" and off.language = \"{}\"".format(language)


    if ref_channel:
        recommended_query.append(" and UP.referencechannel_id =  \"{}\"".format(ref_channel))

        recommended_query_joined_date.append(" and UP.referencechannel_id =  \"{}\"".format(ref_channel))

        tsd_querry .append(" and UP.referencechannel_id =  \"{}\"".format(ref_channel))

        tsd_querry_joined_date.append(" and UP.referencechannel_id =  \"{}\"".format(ref_channel))

        demand_booked_query = demand_booked_query +" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

        demand_booked_query_joined_date = demand_booked_query_joined_date +" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

        demand_assigned_query = demand_assigned_query+" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

        demand_assigned_query_joined_date = demand_assigned_query_joined_date+" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

        demand_dropped_query = demand_dropped_query+" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

        demand_dropped_query_joined_date = demand_dropped_query_joined_date+" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

    if role:
        registred_users_query = ["SELECT COUNT(*) FROM auth_user U, web_userprofile UP, web_role R, web_rolepreference RP where U.id = UP.user_id \
                                  and RP.userprofile_id = UP.id and RP.role_id = R.id"]
        registred_users_query_joined_date= ["SELECT COUNT(*) FROM auth_user U, web_userprofile UP, web_role R, web_rolepreference RP where U.id = UP.user_id \
                                  and RP.userprofile_id = UP.id and RP.role_id = R.id and "\
                                  "DATE(U.date_joined) >= '{}'".format(
        from_date) + " and  DATE(U.date_joined) <= '{}'".format(to_date)]
        prof_comp_querry = ["SELECT DATE(U.date_joined), COUNT(DATE(U.date_joined)) FROM auth_user U, web_userprofile UP, web_role R, web_rolepreference RP \
                                  where U.id = UP.user_id and RP.userprofile_id = UP.id and RP.role_id = R.id and UP.profile_completion_status = 1"]
        orient_comp_querry = ["SELECT DATE(U.date_joined), COUNT(DATE(U.date_joined)) FROM auth_user U, web_userprofile UP, web_role R, web_rolepreference RP \
                                  where U.id = UP.user_id and RP.userprofile_id = UP.id and RP.role_id = R.id and UP.evd_rep = 1"]
        timeline_registered = ["SELECT DATE(U.date_joined), COUNT(DATE(U.date_joined)) FROM auth_user U, web_userprofile UP, web_rolepreference RP, \
                                  web_role R where U.id = UP.user_id and RP.userprofile_id = UP.id and RP.role_id = R.id"]

        recommended_query = [" SELECT count(distinct(U.id))as count FROM web_rolepreference RP,auth_user U,web_role R,\
                                        web_userprofile UP where U.id = UP.user_id and RP.userprofile_id=UP.id \
                                        and RP.role_outcome='Recommended' and RP.role_id = R.id  and  " \
                             "DATE(RP.recommended_date) >= '{}'".format(from_date)+ " \
                             and  DATE(RP.recommended_date) <= '{}'".format(to_date) + " and R.name = \"{}\"".format(role)]

        recommended_query_joined_date = [" SELECT count(distinct(U.id))as count FROM web_rolepreference RP,auth_user U,web_role R,\
                                        web_userprofile UP where U.id = UP.user_id and RP.userprofile_id=UP.id \
                                        and RP.role_outcome='Recommended' and RP.role_id = R.id  and  " \
                             "DATE(RP.recommended_date) >= '{}'".format(from_date)+ " \
                             and  DATE(RP.recommended_date) <= '{}'".format(to_date) + "and DATE(U.date_joined) >= '{}'".format(from_date)+ " \
                             and  DATE(U.date_joined) <= '{}'".format(to_date) + " and R.name = \"{}\"".format(role)]

        tsd_querry = ["SELECT count(distinct(U.id))as count from auth_user U,web_selectiondiscussionslothistory SSH,web_role R, web_rolepreference RP,\
                        web_userprofile UP where U.id = UP.user_id and UP.id = SSH.userp_id and RP.userprofile_id = UP.id and RP.role_id = R.id \
                        and SSH.status='Booked' and   DATE(SSH.booked_date) >= '{}'".format(from_date) +"\
                         and  DATE(SSH.booked_date) <= '{}'".format(to_date) + " and  R.name = \"{}\"".format(role)]

        tsd_querry_joined_date = ["SELECT count(distinct(U.id))as count from auth_user U,web_selectiondiscussionslothistory SSH,web_role R, web_rolepreference RP,\
                        web_userprofile UP where U.id = UP.user_id and UP.id = SSH.userp_id and RP.userprofile_id = UP.id and RP.role_id = R.id \
                        and SSH.status='Booked' and   DATE(SSH.booked_date) >= '{}'".format(from_date) +"\
                         and  DATE(SSH.booked_date) <= '{}'".format(to_date) + " and DATE(U.date_joined) >= '{}'".format(from_date) +"\
                         and  DATE(U.date_joined) <= '{}'".format(to_date) + " and R.name = \"{}\"".format(role)]

        demand_booked_query="SELECT COUNT(offteachmap.id) as count from web_offeringteachermapping offteachmap, web_offering off, auth_user U,web_role R, web_rolepreference RP,\
            web_userprofile UP where U.id=UP.user_id and off.id=offteachmap.offering_id and offteachmap.teacher_id= U.id   and RP.userprofile_id = UP.id and RP.role_id = R.id \
                           and  DATE(offteachmap.booked_date) >= '{}'".format(
        from_date) + " and  DATE(offteachmap.booked_date) <= '{}'".format(to_date)  + " and R.name = \"{}\"".format(role)

        demand_booked_query_joined_date="SELECT COUNT(offteachmap.id) as count from web_offeringteachermapping offteachmap, web_offering off, auth_user U,web_role R, web_rolepreference RP,\
            web_userprofile UP where U.id=UP.user_id and off.id=offteachmap.offering_id and offteachmap.teacher_id= U.id   and RP.userprofile_id = UP.id and RP.role_id = R.id \
                           and  DATE(offteachmap.booked_date) >= '{}'".format(
        from_date) + " and  DATE(offteachmap.booked_date) <= '{}'".format(to_date)+"and DATE(U.date_joined) >= '{}'".format(
        from_date)+" and DATE(U.date_joined) <= '{}'".format(to_date)  + " and R.name = \"{}\"".format(role)

        demand_assigned_query="SELECT count(offteachmap.id) as count from web_offeringteachermapping offteachmap, web_offering off, auth_user U,web_role R, web_rolepreference RP,\
                web_userprofile UP where U.id=UP.user_id and off.id=offteachmap.offering_id and offteachmap.teacher_id= U.id and RP.userprofile_id = UP.id and RP.role_id = R.id \
                                and DATE(offteachmap.assigned_date) >= '{}'".format(
            from_date) + " and  DATE(offteachmap.assigned_date) <= '{}'".format(to_date) + " and R.name = \"{}\"".format(role)

        demand_assigned_query_joined_date="SELECT count(offteachmap.id) as count from web_offeringteachermapping offteachmap, web_offering off, auth_user U,web_role R, web_rolepreference RP,\
                web_userprofile UP where U.id=UP.user_id and off.id=offteachmap.offering_id and offteachmap.teacher_id= U.id  and RP.userprofile_id = UP.id and RP.role_id = R.id \
                               and DATE(offteachmap.assigned_date) >= '{}'".format(
            from_date) + " and  DATE(offteachmap.assigned_date) <= '{}'".format(to_date)+"and DATE(U.date_joined) >= '{}'".format(
            from_date)+" and DATE(U.date_joined) <= '{}'".format(to_date) + " and R.name = \"{}\"".format(role)

        demand_dropped_query="SELECT count(distinct(offmap.offering_id)) as count from  web_offering off, auth_user U,web_role R, web_rolepreference RP,\
                web_userprofile UP,web_offeringteachermapping offmap where U.id=UP.user_id and off.id=offmap.offering_id and offmap.teacher_id= U.id  and RP.userprofile_id = UP.id and RP.role_id = R.id\
                                and   DATE(offmap.dropped_date) >= '{}'".format(
            from_date) + " and  DATE(offmap.dropped_date) <= '{}'".format(to_date) + " and R.name = \"{}\"".format(role)

        demand_dropped_query_joined_date="SELECT count(distinct(offmap.offering_id)) as count from  web_offering off, auth_user U,web_role R, web_rolepreference RP,\
                web_userprofile UP,web_offeringteachermapping offmap where U.id=UP.user_id and off.id=offmap.offering_id and offmap.teacher_id= U.id and RP.userprofile_id = UP.id and RP.role_id = R.id \
                                and   DATE(offmap.dropped_date) >= '{}'".format(
            from_date) + " and  DATE(offmap.dropped_date) <= '{}'".format(to_date)+" and DATE(U.date_joined) >= '{}'".format(
            from_date) + " and  DATE(U.date_joined) <= '{}'".format(to_date) + " and R.name = \"{}\"".format(role)

        if language:
            recommended_query.append(" and UP.pref_medium = \"{}\"".format(language))

            recommended_query_joined_date.append(" and UP.pref_medium = \"{}\"".format(language))

            tsd_querry.append(" and UP.pref_medium = \"{}\"".format(language))

            tsd_querry_joined_date.append(" and UP.pref_medium = \"{}\"".format(language))

            demand_booked_query=demand_booked_query +" and off.language = \"{}\"".format(language)

            demand_booked_query_joined_date=demand_booked_query_joined_date +" and off.language = \"{}\"".format(language)

            demand_assigned_query=demand_assigned_query +" and off.language = \"{}\"".format(language)

            demand_assigned_query_joined_date=demand_assigned_query_joined_date +" and off.language = \"{}\"".format(language)

            demand_dropped_query = demand_dropped_query +" and off.language = \"{}\"".format(language)

            demand_dropped_query_joined_date= demand_dropped_query_joined_date +" and off.language = \"{}\"".format(language)

        if ref_channel:
            recommended_query.append(" and UP.referencechannel_id =  \"{}\"".format(ref_channel))

            recommended_query_joined_date.append(" and UP.referencechannel_id =  \"{}\"".format(ref_channel))

            tsd_querry.append(" and UP.referencechannel_id =  \"{}\"".format(ref_channel))

            tsd_querry_joined_date.append(" and UP.referencechannel_id =  \"{}\"".format(ref_channel))

            demand_booked_query = demand_booked_query +" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

            demand_booked_query_joined_date = demand_booked_query_joined_date +" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

            demand_assigned_query = demand_assigned_query+" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

            demand_assigned_query_joined_date = demand_assigned_query_joined_date+" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

            demand_dropped_query = demand_dropped_query+" and UP.referencechannel_id =  \"{}\"".format(ref_channel)

            demand_dropped_query_joined_date = demand_dropped_query_joined_date+" and UP.referencechannel_id =  \"{}\"".format(ref_channel)


    onboard_started_querry = ["select count(distinct U.id) as y from auth_user U, web_userprofile UP, web_onboardingstepstatus OSS, \
                                web_rolepreference RP, web_role R, web_onboardingstep OS where U.id = UP.user_id and UP.id = RP.userprofile_id and \
                                RP.id = OSS.role_preference_id and RP.role_id = R.id and RP.role_outcome = \"inprocess\""]
    onboard_compl_querry = ["select DATE(U.date_joined), count(distinct U.id) as y from auth_user U, web_userprofile UP,web_rolepreference RP, \
                                web_role R where U.id = UP.user_id and RP.userprofile_id = UP.id and RP.role_id = R.id and \
                                (RP.role_onboarding_status = 100 OR RP.role_outcome like \"Recommended%\")"]
    atleast_one_step_query = ["select count(distinct(U.id)) from web_userprofile_pref_roles PR, web_userprofile UP, auth_user U \
                               where U.id = UP.user_id and PR.userprofile_id = UP.id"]
    completed_all_query = ["SELECT count(*) FROM web_rolepreference RP, auth_user U, web_userprofile UP, web_userprofile_pref_roles PR,\
                               web_role R WHERE RP.userprofile_id = UP.id and U.id = UP.user_id AND UP.id = PR.userprofile_id AND PR.role_id = R.id \
                               and (RP.role_onboarding_status = 100 OR RP.role_outcome like \"Recommended%\")"]
    rolewise_reg_query = ["SELECT R.name,R.id, COUNT( U.id ) FROM auth_user U, web_userprofile UP, web_rolepreference RP, web_role R WHERE \
                                U.id = UP.user_id AND UP.id = RP.userprofile_id AND RP.role_id = R.id"]
    rolewise_allsteps_query = ["SELECT R.id, R.name, count(*) as count FROM web_rolepreference RP, auth_user U, web_userprofile UP,web_role R \
                                WHERE RP.userprofile_id = UP.id and U.id = UP.user_id AND RP.role_id = R.id  and (RP.role_onboarding_status = 100 OR \
                                RP.role_outcome = \"Recommended\") "]
    stepwise_query = ["SELECT OS.id, OS.stepname, OS.weightage, count(SS.id) as count from web_onboardingstep OS, web_onboardingstepstatus SS, \
                                web_rolepreference RP, auth_user U, web_userprofile UP where U.id = UP.user_id AND OS.id = SS.step_id AND SS.status = 1 AND \
                                SS.role_preference_id = RP.id AND RP.userprofile_id = UP.id "]
    timeline_all_steps = ["SELECT DATE(U.date_joined), COUNT(DATE(U.date_joined)) FROM web_rolepreference RP, auth_user U, web_userprofile UP, \
                               web_userprofile_pref_roles PR, web_role R WHERE RP.userprofile_id = UP.id and U.id = UP.user_id AND UP.id = PR.userprofile_id \
                               AND PR.role_id = R.id and (RP.role_onboarding_status = 100 OR RP.role_outcome like \"Recommended%\")"]

    ref_channel_querry = ["SELECT WR.name,COUNT(distinct(U.id)) as y FROM web_referencechannel WR, web_userprofile UP, auth_user U, web_rolepreference RP, web_role R\
                                where U.id = UP.user_id and RP.userprofile_id = UP.id and RP.role_id = R.id and UP.referencechannel_id=WR.id and UP.referencechannel_id != \"\""]
    language_querry = ["SELECT pref_medium as name, COUNT(distinct(U.id)) as y FROM web_userprofile UP, auth_user U, web_rolepreference RP, web_role R\
                                where U.id=UP.user_id and RP.userprofile_id = UP.id and RP.role_id = R.id  and UP.pref_medium not in (\"\", \"None\")"]
    role_wise_querry = ["select R.name as name, count(role_id) as y from web_rolepreference RP, web_role R, auth_user U, web_userprofile UP \
                                where RP.userprofile_id=UP.id and U.id = UP.user_id and R.id = RP.role_id and R.name !=\"TSD Panel Member\""]
    role_outcome_querry = ["SELECT RP.role_outcome as name, count(RP.role_outcome) as y from web_rolepreference RP, web_role R, auth_user U, web_userprofile UP \
                                where RP.userprofile_id=UP.id and U.id = UP.user_id and R.id = RP.role_id and R.name !=\"TSD Panel Member\""]
    if role:
        first_step_querry = ["select DATE(U.date_joined) as name, count(*) as y from auth_user U, web_userprofile UP, web_onboardingstepstatus OSS, \
                                web_rolepreference RP, web_role R, web_onboardingstep OS where U.id = UP.user_id and UP.id = RP.userprofile_id and \
                                RP.id = OSS.role_preference_id and RP.role_id = R.id and OSS.step_id = OS.id and OS.role_id = R.id and OS.order = 1 and OSS.status = 1"]
        onboard_comp = ["select DATE(U.date_joined) as name, count(distinct U.id) as y from auth_user U, web_userprofile UP, web_onboardingstepstatus OSS, \
                                web_rolepreference RP where RP.userprofile_id = UP.id and RP.role_id = R.id and OSS.step_id = OS.id and OS.role_id = R.id \
                                and RP.role_outcome != \"Not Started\""]

    def append(data):
        registred_users_query.append(data)
        registred_users_query_joined_date.append(data)
        atleast_one_step_query.append(data)
        completed_all_query.append(data)
        rolewise_reg_query.append(data)
        rolewise_allsteps_query.append(data)
        stepwise_query.append(data)
        timeline_registered.append(data)
        timeline_all_steps.append(data)
        ref_channel_querry.append(data)
        language_querry.append(data)
        role_wise_querry.append(data)
        role_outcome_querry.append(data)
        prof_comp_querry.append(data)
        orient_comp_querry.append(data)
        onboard_started_querry.append(data)
        onboard_compl_querry.append(data)
        if role:
            first_step_querry.append(data)

    if from_date:
        frm = "DATE(U.date_joined) >= '{}'".format(from_date)
        append(frm)

    if to_date:
        to = "DATE(U.date_joined) <= '{}'".format(to_date)
        append(to)


    if language:
        lang = "UP.pref_medium = \"{}\"".format(language)
        append(lang)

    if ref_channel:
        ref = "UP.referencechannel_id =  \"{}\"".format(ref_channel)
        append(ref)

    if role:
        rol = "R.name = \"{}\"".format(role)
        role_wise_querry.append(rol)
        completed_all_query.append(rol)
        ref_channel_querry.append(rol)
        # rolewise_reg_query.append(rol)
        language_querry.append(rol)
        role_outcome_querry.append(rol)
        onboard_started_querry.append(rol)
        prof_comp_querry.append(rol)
        timeline_registered.append(rol)
        # prof_comp_querry.append(rol + " and RP.role_id = R.id and RP.userprofile_id = UP.id")
        # orient_comp_querry.append(rol)
        first_step_querry.append(rol)
        onboard_compl_querry.append(rol)
        first_step_querry = " AND ".join(first_step_querry)
        registred_users_query.append(rol)
        registred_users_query_joined_date.append(rol)
        orient_comp_querry.append(rol)


    registred_users_query = " AND ".join(registred_users_query)
    registred_users_query_joined_date=" AND ".join(registred_users_query_joined_date)
    recommended_query = " ".join(recommended_query)
    recommended_query_joined_date = " ".join(recommended_query_joined_date)
    tsd_querry = "  ".join(tsd_querry)
    tsd_querry_joined_date = "  ".join(tsd_querry_joined_date)
    atleast_one_step_query = " AND ".join(atleast_one_step_query)
    onboard_started_querry = " AND ".join(onboard_started_querry)
    onboard_compl_querry = " AND ".join(onboard_compl_querry)
    completed_all_query = " AND ".join(completed_all_query)
    rolewise_reg_query = " AND ".join(rolewise_reg_query)
    rolewise_allsteps_query = " AND ".join(rolewise_allsteps_query)
    stepwise_query = " AND ".join(stepwise_query)
    timeline_registered = " AND ".join(timeline_registered)
    timeline_all_steps = " AND ".join(timeline_all_steps)
    ref_channel_querry = " AND ".join(ref_channel_querry)

    language_querry = " AND ".join(language_querry)
    role_wise_querry = " AND ".join(role_wise_querry)
    role_outcome_querry = " AND ".join(role_outcome_querry)
    prof_comp_querry = " AND ".join(prof_comp_querry)
    orient_comp_querry = " AND ".join(orient_comp_querry)
    # print "onboard_started_querry == ", onboard_started_querry
    dict_cur.execute(registred_users_query)
    total_registred = dict_cur.fetchall()[0]['COUNT(*)']

    dict_cur.execute(registred_users_query_joined_date)
    total_registred_joined_date= dict_cur.fetchall()[0]['COUNT(*)']

    def get_percentage(value):
        return "(" + str(
            round((float(value) / float(total_registred)) * 100, 2)) + " %)" if total_registred != 0 else " "

    if teacher :
        dict_cur.execute(recommended_query)
        total_rec = dict_cur.fetchall()[0]['count']

        dict_cur.execute(recommended_query_joined_date)
        total_rec_joined_date = dict_cur.fetchall()[0]['count']

        dict_cur.execute(tsd_querry )
        total_tsd = dict_cur.fetchall()[0]['count']

        dict_cur.execute(tsd_querry_joined_date )
        total_tsd_joined_date = dict_cur.fetchall()[0]['count']

        dict_cur.execute(demand_booked_query)
        total_demand_booked=dict_cur.fetchall()[0]['count']

        dict_cur.execute(demand_booked_query_joined_date)
        total_demand_booked_joined_date=dict_cur.fetchall()[0]['count']

        dict_cur.execute(demand_assigned_query)
        total_demand_assigned=dict_cur.fetchall()[0]['count']

        dict_cur.execute(demand_assigned_query_joined_date)
        total_demand_assigned_joined_date=dict_cur.fetchall()[0]['count']

        dict_cur.execute(demand_dropped_query)
        total_demand_dropped=dict_cur.fetchall()[0]['count']

        dict_cur.execute(demand_dropped_query_joined_date)
        total_demand_dropped_joined_date=dict_cur.fetchall()[0]['count']

        rec_percent=get_percentage(total_rec)
        total_rec_percent=get_percentage(total_rec_joined_date)
        total_tsd_percent=get_percentage(total_tsd)
        total_tsd_joined_percent=get_percentage(total_tsd_joined_date)
    else :
        total_rec=''
        total_rec_joined_date = ''
        total_tsd=''
        total_tsd_joined_date =''
        total_demand_booked=''
        total_demand_booked_joined_date=''
        total_demand_assigned=''
        total_demand_assigned_joined_date=''
        total_demand_dropped=''
        total_demand_dropped_joined_date=''
        rec_percent=''
        total_rec_percent=''
        total_tsd_percent=''
        total_tsd_joined_percent=''

    dict_cur.execute(registred_users_query + " AND U.is_active = 1")
    total_active = dict_cur.fetchall()[0]['COUNT(*)']

    dict_cur.execute(orient_comp_querry)
    orient_comp_all = dict_cur.fetchall()[0]['COUNT(DATE(U.date_joined))']

    dict_cur.execute(prof_comp_querry)
    profile_comp_all = dict_cur.fetchall()[0]['COUNT(DATE(U.date_joined))']

    dict_cur.execute(onboard_started_querry)
    onboard_started_all = dict_cur.fetchall()[0]['y']

    dict_cur.execute(onboard_compl_querry)
    onboard_compl_all = dict_cur.fetchall()[0]['y']

    dict_cur.execute(atleast_one_step_query)
    atleast_one_step = dict_cur.fetchall()[0]['count(distinct(U.id))']

    dict_cur.execute(completed_all_query)
    completed_all = dict_cur.fetchall()[0]['count(*)']

    dict_cur.execute(rolewise_reg_query + " GROUP BY R.name order by R.id")
    rolewise_registration = dict_cur.fetchall()

    dict_cur.execute(rolewise_allsteps_query + " group by R.id order by count desc")
    rolewise_allsteps = dict_cur.fetchall()

    dict_cur.execute(ref_channel_querry + " GROUP BY WR.id")
    ref_channel_pie = dict_cur.fetchall()
    ref_channel_pie = [item for item in ref_channel_pie]
    ref_channel_pie_series = simplejson.dumps([{
        'name': 'Reference Channel',
        'colorByPoint': 'true',
        'data': ref_channel_pie}])

    dict_cur.execute(language_querry + " GROUP BY UP.pref_medium")
    pref_medium_pie = dict_cur.fetchall()
    pref_medium_pie = [item for item in pref_medium_pie]
    pref_medium_pie_series = simplejson.dumps([{
        'name': 'Language',
        'colorByPoint': 'true',
        'data': pref_medium_pie}])

    dict_cur.execute(role_wise_querry + " GROUP BY R.name")
    role_pie = dict_cur.fetchall()
    role_pie = [item for item in role_pie]
    role_pie_series = simplejson.dumps([{
        'name': 'Role',
        'colorByPoint': 'true',
        'data': role_pie}])

    dict_cur.execute(role_outcome_querry + " GROUP BY RP.role_outcome")
    role_outcome_pie = dict_cur.fetchall()
    role_outcome_pie = [item for item in role_outcome_pie]
    role_outcome_pie_series = simplejson.dumps([{
        'name': 'Role Outcome',
        'colorByPoint': 'true',
        'data': role_outcome_pie}])

    dict_cur.execute(timeline_registered + " GROUP BY DATE(U.date_joined)")
    timeline_reg = dict_cur.fetchall()

    dict_cur.execute(timeline_registered + " AND U.is_active = 1 GROUP BY DATE(U.date_joined)")
    timeline_active = dict_cur.fetchall()

    # new timeline req
    dict_cur.execute(prof_comp_querry + " GROUP BY DATE(U.date_joined)")
    prof_comp = dict_cur.fetchall()

    dict_cur.execute(onboard_compl_querry + " GROUP BY DATE(U.date_joined)")
    onboard_comp = dict_cur.fetchall()

    prof_comp_data = []
    import calendar
    for item in prof_comp:
        prof_comp_data.append(
            [calendar.timegm(item['DATE(U.date_joined)'].timetuple()) * 1000, item['COUNT(DATE(U.date_joined))']])
        # prof_comp_data.append([item['DATE(U.date_joined)'].strftime('%d-%m-%Y'), item['COUNT(DATE(U.date_joined))']])

    dict_cur.execute(orient_comp_querry + " GROUP BY DATE(U.date_joined)")
    orient_comp = dict_cur.fetchall()

    orient_comp_data = []
    for item in orient_comp:
        orient_comp_data.append(
            [calendar.timegm(item['DATE(U.date_joined)'].timetuple()) * 1000, item['COUNT(DATE(U.date_joined))']])
        # orient_comp_data.append([item['DATE(U.date_joined)'].strftime('%d-%m-%Y'), item['COUNT(DATE(U.date_joined))']])

    activated_user_data = []
    for item in timeline_active:
        activated_user_data.append(
            [calendar.timegm(item['DATE(U.date_joined)'].timetuple()) * 1000, item['COUNT(DATE(U.date_joined))']])
    onboard_comp_data = []
    for item in onboard_comp:
        onboard_comp_data.append([calendar.timegm(item['DATE(U.date_joined)'].timetuple()) * 1000, item['y']])

    timeline_series = [
        {
            'name': 'Profile Completed',
            'data': prof_comp_data
        },
        {
            'name': 'Orientation Completed',
            'data': orient_comp_data
        },
        {
            'name': 'Activated',
            'data': activated_user_data
        }
    ]
    if role:
        dict_cur.execute(first_step_querry + " GROUP BY DATE(U.date_joined)")
        first_step = dict_cur.fetchall()
        first_step_data = []
        for item in first_step:
            first_step_data.append([calendar.timegm(item['name'].timetuple()) * 1000, item['y']])

        timeline_series.append(
            {
                'name': 'Onboarding Started',
                'data': first_step_data
            }
        )

    # end new timeline req

    stepwise_all = {}
    for i in range(1, 7):
        dict_cur.execute(stepwise_query + " AND OS.role_id = " + str(i) + " group by  OS.stepname order by count desc")
        stepwise_all[i] = dict_cur.fetchall()

    roles = Role.objects.values('id', 'name').filter(id__lte=5)
    roles_temp = []
    roles_temp1 = []
    for role_count in rolewise_registration:
        roles_temp.append(role_count['name'])
    for role_count in rolewise_allsteps:
        roles_temp1.append(role_count['name'])
    for role in roles:
        if role['name'] not in roles_temp:
            rolewise_registration = rolewise_registration + (
            {'name': role['name'], 'id': role['id'], 'COUNT( U.id )': 0},)
        if role['name'] not in roles_temp1:
            rolewise_allsteps = rolewise_allsteps + ({'name': role['name'], 'id': role['id'], 'count': 0},)

    rolewise_registration = sorted(rolewise_registration, key=operator.itemgetter('id'))
    rolewise_allsteps = sorted(rolewise_allsteps, key=operator.itemgetter('id'))
    rolewise_reg = {}

    for role_count, role_complete in zip(rolewise_registration, rolewise_allsteps):
        rolewise_reg[role_count['id']] = {'name': role_count['name'], 'reg_count': role_count['COUNT( U.id )'],
                                          'completed_count': role_complete['count']}

    tot_user_cur.close()
    dict_cur.close()

    resp = {'total_registred': [total_registred,get_percentage(total_registred)], 'total_tsd':[total_tsd,total_tsd_percent],'total_rec': [total_rec,rec_percent],
            'atleast_one_step': [atleast_one_step, get_percentage(atleast_one_step)] \
        ,   'completed_all': [completed_all, get_percentage(completed_all)],
            'rolewise_count': rolewise_reg,
            'teacher_stepwise': stepwise_all[1], \
            'centeradmin_stepwise': stepwise_all[2], \
            'contentdeveloper_stepwise': stepwise_all[3], 'wellwisher_stepwise': stepwise_all[4], \
            'contentadmin_stepwise': stepwise_all[5], 'classassistant_stepwise': stepwise_all[6],
            'language_list': language_list, \
            'ref_channel_list': ref_channel_list, 'timeline_series': simplejson.dumps(timeline_series), \
            'role_list': role_list, 'ref_channel_pie_series': ref_channel_pie_series,
            'pref_medium_pie_series': pref_medium_pie_series, \
            'role_pie_series': role_pie_series, 'role_outcome_pie_series': role_outcome_pie_series,
            'from_date': from_date, 'to_date': to_date,'total_registred_joined_date':[total_registred_joined_date,get_percentage(total_registred_joined_date)],\
            'total_tsd_joined_date':[total_tsd_joined_date,total_tsd_joined_percent],\
            'total_rec_joined_date':[total_rec_joined_date,total_rec_percent],\
            'total_demand_booked':total_demand_booked,\
            'total_demand_booked_joined_date':total_demand_booked_joined_date,\
            'total_demand_assigned':total_demand_assigned,\
            'total_demand_assigned_joined_date':total_demand_assigned_joined_date,'teacher':teacher,\
            'total_demand_dropped':total_demand_dropped,'total_demand_dropped_joined_date':total_demand_dropped_joined_date}

    if date_filter:
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
    else:
        return render_response(request, 'heatmap2.html', resp)


def insert_into_alerts(sub, body, recipients, user, _type, category = None, status = 'pending'):
    conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                           user=settings.DATABASES['default']['USER'],
                           passwd=settings.DATABASES['default']['PASSWORD'],
                           db=settings.DATABASES['default']['NAME'],
                           charset="utf8",
                           use_unicode=True)

    cur_time = datetime.datetime.now()
    cursor = conn.cursor()
    if _type == 'sms':
        mes = sub
    elif _type == 'workplace':
        mes = body
    else:
        mes = sub + '#<>#' + body
    # status = 'pending'

    query = "insert into Alerts(message, type, status, recipients, user, dt_added, dt_updated,category) values('%s', '%s', '%s', '%s', '%s', '%s', '%s','%s')"
    values = (mes, _type, status, recipients, user, cur_time, cur_time,category)
    cursor.execute(query % values)
    conn.commit()

    cursor.close()
    conn.close()
    # send_reset_password_link(recipients, body)

# def send_reset_password_link(recipients="",body=""):
#     ''' for seset password email sending '''
#     recipient_list = recipients.split(',')
#     from_email = settings.DEFAULT_FROM_EMAIL
#     subject = "Password Reset for eVidyaloka account"
#     message = body
#     if len(recipient_list)>0:
#         msg = EmailMessage(subject, message, to=recipient_list, from_email=from_email)
#         msg.send()

def url_redirect(request):
    url = request.GET.get("url", "/")

    return redirect(url)


def get_session_details(request):
    #print "\t*** get_session_details ", request.GET
    session_id = request.GET.get('id', '')
    rel_data = {}
    rel_data['status'] = 1
    rel_data['message'] = 'fail'
    rel_data['data'] = {}
    if session_id:
        session = Session.objects.filter(id=session_id)
        if session:
            session = session[0]
            topics = []
            actual_topics = session.actual_topics.all()
            planned_topics = session.planned_topics.all()
            if len(actual_topics) > 0:
                for topic in actual_topics:
                    topics.append({"title": topic.title, "url": topic.url, 'id': topic.id})
            else:
                for topic in planned_topics:
                    topics.append({"title": topic.title, "url": topic.url, 'id': topic.id})

            event = {}
            event["subject"] = session.offering.course.subject
            event["topics"] = topics
            event["grade"] = make_number_verb(session.offering.course.grade)
            event["start"] = make_date_time(session.date_start)["time"]
            event["date"] = make_date_time(session.date_start)["date"] + " " + str(session.date_start.year)
            event["day_num"] = session.date_start.strftime('%d')
            event["month"] = session.date_start.strftime('%m')
            event["year"] = session.date_start.strftime('%Y')
            event["day_text"] = session.date_start.weekday()
            event["center"] = session.offering.center.name
            event["teacher"] = session.teacher.username if session.teacher else ''
            event["color"] = "#46D150"
            event["textColor"] = "black"
            event["ts_link"] = session.ts_link if (session.ts_link != "" and session.ts_link != None) else "NA"

            center_image = session.offering.center.photo

            if isinstance(center_image, FieldFile):
                try:
                    _path = center_image.file.name.split('static')
                    if len(_path) == 2:
                        center_image = "static" + _path[-1]
                except Exception as exp:
                    center_image = ''

            if center_image and not center_image.startswith("http://"):
                event["center_image"] = 'http://' + request.META['HTTP_HOST'] + "/" + str(center_image)

            session_attendance = []
            #sessionattendance = SessionAttendance.objects.filter(session=session_id)
            enrolled_students = session.offering.enrolled_students.all()
            for student in enrolled_students:
                attend = {
                    "name": (student.name).upper(),
                    "id": student.id,
                    "is_present": "no"
                }
                session_att_student = SessionAttendance.objects.filter(session=session, student=student)
                if session_att_student:
                    attend['is_present'] = session_att_student[0].is_present

                session_attendance.append(attend)

            event['session_attandance'] = session_attendance

            session = Session.objects.get(pk=session_id)
            #course_id = session.offering.course.id
            actual_topics = session.actual_topics.all()
            #planned_topics = session.planned_topics.all()
            actual_comment = session.comments
            status = session.status
            topics = session.offering.planned_topics.all().order_by('priority')
            topics_json = []

            for topic in topics:
                if not topic in actual_topics:
                    topics_json.append({"title": topic.title, "id": topic.id, "actual": False})
                else:
                    topics_json.append({"title": topic.title, "id": topic.id, "actual": True})

            event['feedback_details'] = topics_json
            event['session_status'] = status
            event['comments'] = actual_comment

            rel_data['status'] = 0
            rel_data['message'] = 'success'
            rel_data['data'] = event

    return HttpResponse(json.dumps(rel_data), content_type='application/json')


@login_required
def task_list(request):
    if request.user.is_authenticated:
        db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                             user=settings.DATABASES['default']['USER'],
                             passwd=settings.DATABASES['default']['PASSWORD'],
                             db=settings.DATABASES['default']['NAME'],
                             charset="utf8",
                             use_unicode=True)
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query = "select au.id,au.username from web_userprofile_role wupr, web_userprofile wup, web_role wr, auth_user au where wupr.userprofile_id = wup.id and wr.id = wupr.role_id and wr.name = 'vol_co-ordinator' and wup.user_id = au.id order by(wup.id)"
        dict_cur.execute(query)
        vol_coordinatordata = dict_cur.fetchall()
        tot_user_cur.close()
        dict_cur.close()
        message = request.GET.get('message', '')
        tabName = request.GET.get('tab', '')
        demand_flag = request.GET.get('filter', '')
        is_allocate_role = False
        is_pam = False
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect('/v2/update_no_profile/')
        if has_role(user_profile, "vol_admin") or has_pref_role(user_profile, "vol_admin"):
            is_allocate_role = True
        elif has_role(user_profile, "Partner Account Manager")or has_pref_role(user_profile, "Partner Account Manager"):
            is_pam = True
        vol_coordinators = simplejson.dumps(vol_coordinatordata)
        save_user_activity(request, 'Viewed Page:Task List', 'Page Visit')
        return render_response(request, "task/taskList.html",
                               {'vol_coordinatordata': vol_coordinators, 'is_allocate_role': is_allocate_role,
                                'user': request.user, 'message': message, 'tabName': tabName,'is_pam':is_pam,
                                'demand_flag': demand_flag})
    else:
        return redirect("/?show_popup=true&type=login")


@csrf_exempt
def getTaskListData(request):
    if request.is_ajax():
        selectedTab = request.GET.get('selectedTab', '')
        filterParam = request.GET.get('filterParam', '')
        searchParam = request.GET.get('searchParam', '')
        message = request.GET.get('message', '')
        today = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
        due_date = today.date()
        status = None
        allTask = None
        if filterParam:
            if filterParam == 'Open' or filterParam == 'Resolved' or filterParam == 'Closed':
                status = filterParam
        allTask, message = getAllTaskDataForParams(request, selectedTab, filterParam, searchParam, due_date, status,
                                                   message)
        return HttpResponse(simplejson.dumps({'allTask': allTask, 'message': message}, default=myconverter),
                            mimetype='application/json')
    else:
        return HttpResponse('No Centers Available')


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def getAllTaskDataForParams(request, selectedTab, filterParam, searchParam, due_date, status, message):
    userp = request.user.userprofile
    user_name = request.user.username
    # print 'selectedTab',selectedTab,'filterParam',filterParam
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                         user=settings.DATABASES['default']['USER'],
                         passwd=settings.DATABASES['default']['PASSWORD'],
                         db=settings.DATABASES['default']['NAME'],
                         charset="utf8",
                         use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select * from web_task where subject !='null' "
    if selectedTab:
        if selectedTab == 'myTask':
            query += " and assignedTo='" + user_name + "' "
            if has_pref_role(userp, "vol_admin") or has_pref_role(userp, "vol_co-ordinator"):
                query += " and (taskType='MANUAL' or taskType='SYSTEM' or taskType='OTHER' or taskType='HELP' or taskType='ISSUE' or taskType='FEEDBACK') "
            else:
                query += " and (taskType='MANUAL' or taskType='OTHER' or taskType='HELP' or taskType='ISSUE' or taskType='FEEDBACK') "
        elif selectedTab == 'taskByMe':
            query += " and taskCreatedBy_userId='" + user_name + "' "
            if has_pref_role(userp, "vol_admin") or has_pref_role(userp, "vol_co-ordinator"):
                query += " and (taskType='MANUAL' or taskType='SYSTEM' or taskType='HELP' or taskType='ISSUE' or taskType='FEEDBACK') "
            else:
                query += " and (taskType='MANUAL' or taskType='HELP' or taskType='ISSUE' or taskType='FEEDBACK') "
        elif selectedTab == 'allTask':
            if has_pref_role(userp, "vol_admin") or has_pref_role(userp, "vol_co-ordinator"):
                query += " and (taskType='MANUAL' or taskType='SYSTEM' or taskType='HELP' or taskType='ISSUE' or taskType='FEEDBACK') "
            else:
                query += " and (taskType='MANUAL' or taskType='HELP' or taskType='ISSUE' or taskType='FEEDBACK') "
        elif selectedTab == 'allocateTask':
            query += " and assignedTo='" + user_name + "' and taskType='SYSTEM' "
        elif selectedTab == 'other':
            query += " and taskType='OTHER' "
        if status is not None:
            if status == 'Open':
                query += " and (taskStatus='open' or taskStatus='WIP') "
            elif status == 'Resolved' or status == 'Closed':
                query += " and taskStatus='" + status + "' "
        else:
            if filterParam:
                if filterParam == 'today':
                    query += " and dueDate='" + str(due_date) + "' and (taskStatus='open' or taskStatus='WIP') "
                elif filterParam == 'overdue':
                    query += " and dueDate <'" + str(due_date) + "' and (taskStatus='open' or taskStatus='WIP') "
                elif filterParam == 'overdueToday':
                    query += " and dueDate <='" + str(due_date) + "' and (taskStatus='open' or taskStatus='WIP') "
                elif filterParam == 'tommorrow':
                    new_date = due_date + timedelta(1)
                    query += " and dueDate ='" + str(new_date) + "' and (taskStatus='open' or taskStatus='WIP') "
                elif filterParam == 'yesterday':
                    new_date = due_date - timedelta(1)
                    query += " and dueDate ='" + str(new_date) + "' and (taskStatus='open' or taskStatus='WIP') "
                elif filterParam == 'lastSevenDays':
                    start_date = due_date - timedelta(7)
                    query += " and dueDate >'" + str(start_date) + "' and dueDate<='" + str(
                        due_date) + "' and (taskStatus='open' or taskStatus='WIP') "
        if searchParam:
            query += "and (subject like '%" + searchParam + "%' or assignedTo like '%" + searchParam + "%' or performedOn_name like '%" + searchParam + "%') "
    else:
        query += " and assignedTo='" + user_name + "'  and (taskStatus='open')"
    query += " order by case when taskUpdatedDate is not null then taskUpdatedDate  else taskCreatedDate end desc "
    dict_cur.execute(query)
    data_list = dict_cur.fetchall()
    tot_user_cur.close()
    dict_cur.close()
    return data_list, message


def saveTask(request):
    if request.method == 'POST':
        dd = request.POST.get('dueDate', '')
        task_type = request.POST.get('type', '')
        message = request.POST.get('message', '')
        tabName = request.POST.get('tabName', '')
        comment = request.POST.get('editor1', '')
        subject = request.POST.get('taskName', '')
        userId = request.POST.get('prfm_id', '')
        taskStatus = request.POST.get('statusId', '')
        priority = request.POST.get('priorityId', '')
        assignedTo = request.POST.get('assign_name_id', '')
        performedOn_name = request.POST.get('prfm_name', '')
        category = request.POST.get('categoryId', '')
        taskCreatedBy_userId = request.user.username
        taskCreatedDate = datetime.datetime.now()
        dueDate = datetime.datetime.strptime(dd, "%d-%m-%Y").date()
        date_joined = None
        todayDate = datetime.datetime.today()
        todayDay = calendar.day_name[todayDate.weekday()]
        if userId:
            user = User.objects.get(id=userId)
            date_joined = user.date_joined
        task_other_status = ''
        if task_type and task_type == 'OTHER':
            task_other_status = 'pending'
        if category and task_type == 'OTHER':
            task = Task(comment=comment, subject=subject, assignedTo='', dueDate=dueDate, priority=priority,
                        taskCreatedBy_userId=taskCreatedBy_userId, taskStatus=taskStatus, performedOn_userId='',
                        taskCreatedDate=taskCreatedDate, user_date_joined=date_joined, performedOn_name='',
                        taskType=task_type, task_other_status=task_other_status, category=category)
        else:
            task = Task(comment=comment, subject=subject, assignedTo=assignedTo, dueDate=dueDate, priority=priority,
                        taskCreatedBy_userId=taskCreatedBy_userId, taskStatus=taskStatus, performedOn_userId=userId,
                        taskCreatedDate=taskCreatedDate, user_date_joined=date_joined,
                        performedOn_name=performedOn_name, taskType=task_type, task_other_status=task_other_status)
        task.save()
        recipients = []
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
                # user_mail_config = has_mail_receive_accepted(user, 'Announcement')
                # if user_mail_config['user_settings'] or user_mail_config['role_settings']:
                #     recipients.append(email)
                recipients.append(email)
                args = {'user': name, 'date': taskCreatedDate, 'subject': subject, 'comment': comment, \
                        'confirm_url': WEB_BASE_URL + "edit_task/?id=" + str(task.id), 'todayDay': todayDay}
                body_template = 'mail/task/task_full.txt'
                body = get_mail_content(body_template, args)
                send_mail("New Task has been Assigned to you.", body, settings.DEFAULT_FROM_EMAIL, recipients)
        return redirect('/task_list/?message=' + message + '&tabName=' + tabName)


def updateTask(request):
    if request.method == 'POST':
        taskId = request.POST.get('taskId')
        subject = request.POST.get('taskName', '')
        dd = request.POST.get('dueDate', '')
        taskStatus = request.POST.get('statusId', '')
        performedOn_name = request.POST.get('prfm_name', '')
        message = request.POST.get('message', '')
        performedOn_userId = request.POST.get('prfm_id', '')
        priority = request.POST.get('priorityId', '')
        assignedTo = request.POST.get('assign_name_id', '')
        comment = request.POST.get('editor1', '')
        tabName = request.POST.get('tabName')
        task_type = request.POST.get('type');
        taskUpdatedBy_userId = request.user.username
        taskUpdatedDate = datetime.datetime.now()
        dueDate = datetime.datetime.strptime(dd, "%d-%m-%Y").date()
        category = request.POST.get('categoryId', '')
        if not request.user.is_superuser:
            task_type = request.POST.get('task_type');
        dateJoined = None
        task_other_status = ''
        if task_type and task_type == 'OTHER':
            task_other_status = 'pending'
        if performedOn_userId:
            loggUser = User.objects.get(id=performedOn_userId)
            if loggUser:
                dateJoined = loggUser.date_joined
        message = 'Task Updated Successfully'
        if category and task_type == 'OTHER':
            Task.objects.filter(id=taskId).update(comment=comment, subject=subject, assignedTo='', dueDate=dueDate,
                                                  priority=priority, taskUpdatedBy_userId=taskUpdatedBy_userId,
                                                  taskStatus=taskStatus, performedOn_userId='',
                                                  taskUpdatedDate=taskUpdatedDate, user_date_joined=dateJoined,
                                                  performedOn_name='', taskType=task_type,
                                                  task_other_status=task_other_status, category=category)
        else:
            Task.objects.filter(id=taskId).update(comment=comment, subject=subject, assignedTo=assignedTo,
                                                  dueDate=dueDate, priority=priority,
                                                  taskUpdatedBy_userId=taskUpdatedBy_userId, taskStatus=taskStatus,
                                                  performedOn_userId=performedOn_userId,
                                                  taskUpdatedDate=taskUpdatedDate, user_date_joined=dateJoined,
                                                  performedOn_name=performedOn_name, taskType=task_type,
                                                  task_other_status=task_other_status, category='')
        return redirect('/task_list/?message=' + message + '&tab=' + tabName)
    # return redirect('/task_list','task/taskList.html',{'successMessage':successMessage})
    # return "%s?%s" % (redirect('/task_list', args=(successMessage,)))


def create_task(request):
    tabName = request.GET.get('tab')
    users = User.objects.values('username', 'first_name', 'last_name', 'id').filter(is_active=True)
    logged_in_username = request.user.username
    logged_in_id = request.user.id
    message = 'Task Created Successfully'
    filterUsers = User.objects.values('username').filter((Q(is_staff=True) | Q(is_superuser=True) | Q(is_active=True)))
    return render_response(request, 'task/create_task.html',
                           {'users': users, 'staffUsers': filterUsers, 'logged_in_username': logged_in_username,
                            'message': message, 'tabName': tabName, 'logged_in_id': logged_in_id})


@login_required
def edit_task(request):
    if request.user.is_authenticated:
        role_id = request.GET.get('role')
        user_profile = request.user.userprofile
        vol_co_ordinator_role = False
        user_profile = request.user.userprofile
        isActive = request.user.is_active
        isSuperuser = request.user.is_superuser
        # delivery_co_ordinator_flag = False
        if has_role(user_profile, "vol_co-ordinator") or has_pref_role(user_profile, "vol_co-ordinator") or (
                isActive == True and isSuperuser == False):
            vol_co_ordinator_role = True
        if has_role(user_profile,'Delivery co-ordinator') or has_pref_role(user_profile,'Delivery co-ordinator'):
            # delivery_co_ordinator_flag = True
    
            vol_co_ordinator_role = False
        staffUsers = User.objects.values('username').filter(
            (Q(is_staff=True) | Q(is_superuser=True) | Q(is_active=True)))
        taskId = request.GET.get('id')
        tabName = request.GET.get('tab')
        booking_flag = request.GET.get('flag')
        assignedId = ''
        if taskId and taskId is not None:
            task = Task.objects.get(id=taskId)
            users = users = User.objects.values('first_name', 'last_name', 'username', 'id').filter(is_active=True)
            if task:
                users = User.objects.values('first_name', 'last_name', 'username', 'id').filter(is_active=True)
                if task.assignedTo:
                    userId = User.objects.values('id').filter(username=task.assignedTo)
                    for userid in userId:
                        assignedId = userid['id']
                if task.taskType == 'SYSTEM' and task.performedOn_userId is not None:
                    roles = Role.objects.all()
                    user = User.objects.get(pk=task.performedOn_userId)
                    pref_roles = [role.name for role in user.userprofile.pref_roles.all()]
                    message = 'Task Updated Successfully'
                    save_user_activity(request, "Updated Task", "Update")
                    return render_response(request, 'task/edit_task.html',
                                           {'task': task, 'users': users, 'staffUsers': staffUsers, 'system_user': user,
                                            'role_id': role_id, 'roles': roles, 'pref_roles': pref_roles,
                                            'message': message, 'tabName': tabName, 'isSuperuser': isSuperuser,
                                            'booking_flag': booking_flag, 'assignedId': assignedId})
                save_user_activity(request, "Updated Task", "Update")
                return render_response(request, 'task/edit_task.html',
                                       {'task': task, 'users': users, 'staffUsers': staffUsers, 'tabName': tabName,
                                        'vol_co_ordinator_role': vol_co_ordinator_role, 'isSuperuser': isSuperuser,
                                        'assignedId': assignedId})
    else:
        return redirect("/?show_popup=true&type=login")


@login_required
def students_dashboard(request):
    try:
        statenames = request.GET.getlist('stateId', '')
        centernames = request.GET.getlist('centerId', '')
        delivery_partner = request.GET.getlist('partner_id', '')
        funding_partner = request.GET.getlist('fund_partner_id', '')
        front_centerNames = centernames
        centerNames = []
        grade_list = []
        if centernames:
            for centerName in centernames:
                center = centerName.replace("%20", " ")
                centerNames.append(center)
                centernames = centerNames
        grades = request.GET.getlist('gradeId', '')
        active = None
        start_date = request.GET.get('startDate', '')
        end_date = request.GET.get('endDate', '')
        flag = request.GET.get('flag', '')
        terms = request.GET.getlist('categoryId', '')
        diagTerms = request.GET.getlist('diagCategory', '')
        if statenames == '' or None:
            statenames = ['All']
        if delivery_partner == '' or None:
            delivery_partner = ['All']
        if funding_partner == '' or None:
            funding_partner = ['All']
        if centernames == '' or None:
            centernames = ['All']
        if grades == '' or None:
            grades = ['All']
        if terms == '' or None:
            terms = ['All']
        if diagTerms == '' or None:
            diagTerms = ['All']
        if start_date == '' and end_date == '':
            today = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
            end_date = str(today.date())
            start_date = str(today.date() - timedelta(30))
        diag_category_list = ['All']
        is_funding_partner = False
            
        try:
            ref = ReferenceChannel.objects.get(id=request.user.userprofile.referencechannel.id)
        except:
            ref = None
        without_partner = False

        if request.user.is_superuser or ref is None:
            without_partner = True

        elif has_role(request.user.userprofile,"Delivery co-ordinator"):
            states = Center.objects.filter(delivery_coordinator=request.user,status='Active').order_by('state').values('state').distinct()
            centers = Center.objects.filter(delivery_coordinator=request.user,status='Active').order_by('name').values('name').distinct()
        elif has_role(request.user.userprofile, "Partner Account Manager") or has_pref_role(request.user.userprofile, "Partner Account Manager"):
                                db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                                user=settings.DATABASES['default']['USER'],
                                passwd=settings.DATABASES['default']['PASSWORD'],
                                db=settings.DATABASES['default']['NAME'],
                                charset="utf8",
                                use_unicode=True)
                                tot_user_cur = db.cursor()
                                dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
                                query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                                dict_cur.execute(query)
                                partner_id = [str(each['value']) for each in dict_cur.fetchall()]
                                partner_id.sort()
                                states = Center.objects.filter(( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id))).order_by('state').values('state').distinct()
                                centers =Center.objects.filter(( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id))).order_by('name').values('name').distinct()
                                print "centers",centers
                                db.close()
                                dict_cur.close()
        elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
            partner = None
            if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
                try:
                    partner = Partner.objects.get(contactperson=request.user)
                    if partner:
                        is_funding_partner = Partner.objects.filter(contactperson=request.user,partnertype=3)
                    if is_funding_partner:
                        is_funding_partner= True
                    active = 1
                except:
                    partner= None
            else:
                partner = ref.partner
            if partner and len(partner.partnertype.filter(name='Delivery Partner')) > 0:
                states = Center.objects.filter(partner_school__partner=partner).order_by('state').values('state').distinct()
                centers = Center.objects.filter(partner_school__partner=partner).order_by('name').values('name').distinct()
            else:
                without_partner = True
        if without_partner:
            states = Center.objects.order_by('state').values('state').distinct()
            centers = Center.objects.order_by('name').values('name').distinct()
        if centers:
            center_delivery_partner = Center.objects.filter(name__in = centers)
            if center_delivery_partner:  
                print "delivery_partner",delivery_partner,funding_partner
                if delivery_partner == -1 :
                    if center_delivery_partner[0].delivery_partner != None :
                        delivery_partner = center_delivery_partner[0].delivery_partner.name
                if funding_parter == -1:
                    if center_delivery_partner[0].funding_partner != None :
                        funding_partner = center_delivery_partner[0].funding_partner.name 


            
        try:
            partner = Partner.objects.get(contactperson=request.user)
        except:
            partner = None   
        if partner:
            for ptype in partner.partnertype.all():
                if ptype.id == 1:
                    center_obj = Center.objects.filter(partner_school__partner_id = partner.id,status="Active")
                elif ptype.id == 2:
                    center_obj = Center.objects.filter(partner_school__partner_id = partner.id,delivery_partner_id=partner.id,status="Active")
                elif ptype.id == 3:
                    center_obj = Center.objects.filter(partner_school__partner_id = partner.id,funding_partner_id=partner.id,status="Active")
                elif ptype.id == 4:
                    center_obj = Center.objects.filter(orgunit_partner_id = partner.id,status="Active")
            if center_obj:
                grade_set =set()
                for eachCenter in center_obj:
                    course_id = eachCenter.offering_set.values_list("course_id",flat=True).distinct()
                    each_grade = Course.objects.filter(id__in = course_id).values_list("grade",flat=True).distinct()
                    for gd in each_grade:
                        if len(gd)==1:
                            grade_set.add(gd)
                grade_list = sorted(list(grade_set))
        else:
            grade_list = ['5', '6', '7', '8']

        total_attendance_from_query = get_total_attendance(statenames,delivery_partner,funding_partner, centernames, start_date, end_date)
        total_attendance_perc = 0
        if total_attendance_from_query:
            if total_attendance_from_query['Absent'] and total_attendance_from_query['Present'] and \
                    total_attendance_from_query['Absent'] != 0:
                total_attendance = total_attendance_from_query['Present'] + total_attendance_from_query['Absent']
                total_attendance_perc = (total_attendance_from_query['Present'] * 100) / total_attendance

        attendance_trends_data = get_attendance_trends(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date)

        grade_wise_json_data = get_attendance_courses_per_grade(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date)
        total_aggregate_level_subject_wise = get_aggregate_level_subject_wise(statenames,delivery_partner,funding_partner, centernames, grades, start_date,
                                                                            end_date, diag_category_list)
        diagonostic_outcome = get_diagonostic_outcome(statenames, delivery_partner,funding_partner,centernames, grades, start_date, end_date,
                                                    diag_category_list)
        diagonostic_outcome_json_data = []
        diagonostic_outcome_english = get_data_for_diagonostic(diagonostic_outcome, "English Foundation",
                                                            total_aggregate_level_subject_wise)
        diagonostic_outcome_maths = get_data_for_diagonostic(diagonostic_outcome, "Maths",
                                                            total_aggregate_level_subject_wise)
        diagonostic_outcome_science = get_data_for_diagonostic(diagonostic_outcome, "Science",
                                                            total_aggregate_level_subject_wise)
        diagonostic_outcome_json_data.append(diagonostic_outcome_english)
        diagonostic_outcome_json_data.append(diagonostic_outcome_maths)
        diagonostic_outcome_json_data.append(diagonostic_outcome_science)

        final_scholastic_outcome = get_scholastic_outcome(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date, terms)

        co_scholastic_outcome = get_co_scholastic_outcome(statenames,delivery_partner, funding_partner,centernames, grades, start_date, end_date)
        co_scholastic_outcome_json_data = []
        co_scholastic_outcome_data = []
        remark_list = ['Curious', 'Attentiveness', 'Self Confidence', 'Responsibility', 'Supportiveness',
                    'Positive Attitude', 'Wider Perspective', 'Courteousness']
        for list_rmk in remark_list:
            co_scholastic_outcome_data = get_data_for_co_scholastic_outcome(co_scholastic_outcome, list_rmk)
            co_scholastic_outcome_json_data.append(co_scholastic_outcome_data)

        data_for_trends_attendance = simplejson.dumps(attendance_trends_data)
        data_for_grade_attendance = simplejson.dumps(grade_wise_json_data)
        data_for_diagonostic_outcome = simplejson.dumps(diagonostic_outcome_json_data)
        data_for_scholastic_outcome = simplejson.dumps(final_scholastic_outcome)
        data_for_co_scholastic_outcome = simplejson.dumps(co_scholastic_outcome_json_data)
        if flag:
            statename = ''
            centereName = ''
            statename = (','.join(statenames)).replace(u'\xa0', u' ')
            # for st in statenames:
                
            #     statename += str(st) + ","
            for cen in centernames:
                centereName += str(cen) + ","
            save_user_activity(request,
                            'Searched:My Students - Students Dashboard - Dashboard: ' + string.replace(statename, "%20",
                                                                                                        " ") + ' ' + string.replace(
                                centereName, "%20", " ") + ' ' + str(start_date) + ' to ' + str(end_date), 'Action')
        else:
            save_user_activity(request, 'Viewed Page:My Student - Students Dashboard', 'Page Visit')
        category = Scholastic.objects.filter(Q(category__in=['Term1', 'Term2','Term3', 'Class Test', 'Worksheet', 'Quiz'])).values('category').distinct().order_by("category")

        diag_category = Diagnostic.objects.values('category').distinct()

        category_list = []
        diag_category_list = []
        for cat in category:
            category_list.append(cat['category'])
        for cat in diag_category:
            diag_category_list.append(cat['category'])

        return render_response(request, 'students_dashboard.html',
                            {'active':active,'is_partner':partner, 'is_funding_partner':is_funding_partner, 'partner':partner,'states': states, 'grade_list': grade_list, 'attendance_perc': total_attendance_perc,
                                'attendance_trends_data': data_for_trends_attendance,"delivery_partner":delivery_partner,"funding_partner":funding_partner,
                                'grade_wise_json_data': data_for_grade_attendance, 'statenames': statenames,
                                'grades': grades, 'data_for_diagonostic_outcome': data_for_diagonostic_outcome,
                                'data_for_scholastic_outcome': data_for_scholastic_outcome,
                                'data_for_co_scholastic_outcome': data_for_co_scholastic_outcome,
                                'centernames': simplejson.dumps(front_centerNames), 'start_date': start_date,
                                'end_date': end_date, 'category_list': sorted(set(category_list)), 'terms': terms,
                                'diagTerms': diagTerms, 'diag_category_list': sorted(set(diag_category_list))})
    except Exception as e:
        print("Error at line  --------------------------------------------", traceback.format_exc())
        print("Reason =====================================", e)
        return HttpResponse('ok')



def get_total_attendance(statenames,delivery_partner,funding_partner, centernames, start_date, end_date):

    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    print "delivery_partner",delivery_partner
    query = "select count(case when wsa.is_present = 'yes' then 1 end) Present, count(case when wsa.is_present = 'no' then 1 end) Absent from web_center wc, web_course wco, web_offering wo, web_session ws, web_sessionattendance wsa, web_student wstu where wsa.student_id=wstu.id and wsa.session_id=ws.id and ws.offering_id=wo.id and wo.course_id=wco.id and wo.center_id=wc.id and ws.date_start>='" + start_date + "' and ws.date_end<'" + end_date + "' "
    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = apply_filter_to_query(query, statenames, 'state_param')
    if delivery_partner != '' and len(delivery_partner) > 0 and delivery_partner[0] != 'All':
        query = apply_filter_to_query(query, delivery_partner, 'delivery_param')
    if funding_partner != '' and len(funding_partner) > 0 and funding_partner[0] != 'All':
        query = apply_filter_to_query(query, funding_partner, 'funding_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = apply_filter_to_query(query, centernames, 'center_param')
    if start_date != '' and len(start_date) > 0:
        query += " and wo.start_date >='" + start_date + "'"
    if end_date != '' and len(end_date):
        query += " and wo.end_date <='" + end_date + "'"
    dict_cur.execute(query)
    total_attendance_from_query = dict_cur.fetchall()[0]
    db.close()
    dict_cur.close()
    return total_attendance_from_query


def get_attendance_trends(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date):
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select count(case when wsa.is_present = 'yes' then 1 end) Present, count(case when wsa.is_present = 'no' then 1 end) Absent, date(ws.date_start) startDate from web_center wc, web_course wco, web_offering wo, web_session ws, web_sessionattendance wsa, web_student wstu where wsa.student_id=wstu.id and wsa.session_id=ws.id and ws.offering_id=wo.id  and wo.course_id=wco.id and wo.center_id=wc.id and ws.date_start>='" + start_date + "' and  ws.date_end<'" + end_date + "' "
    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = apply_filter_to_query(query, statenames, 'state_param')
    if delivery_partner != '' and len(delivery_partner) > 0 and delivery_partner[0] != 'All':
        query = apply_filter_to_query(query, delivery_partner, 'delivery_param')
    if funding_partner != '' and len(funding_partner) > 0 and funding_partner[0] != 'All':
        query = apply_filter_to_query(query, funding_partner, 'funding_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = apply_filter_to_query(query, centernames, 'center_param')
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = apply_filter_to_query(query, grades, 'grade_param')
    if start_date != '' and len(start_date) > 0:
        query += " and wo.start_date >='" + start_date + "'"
    if end_date != '' and len(end_date):
        query += " and wo.end_date <='" + end_date + "'"
    query += " group by date(ws.date_start) order by ws.date_start asc "
    dict_cur.execute(query)
    total_attendance_trends = dict_cur.fetchall()
    db.close()
    dict_cur.close()
    attendance_trends_data = []
    if total_attendance_trends:
        for attendance_trends in total_attendance_trends:
            present = attendance_trends['Present']
            absent = attendance_trends['Absent']
            day = str(attendance_trends['startDate'])
            if present and absent and absent != 0:
                trends_perc = (present * 100) / (present + absent)
                data = {'value': trends_perc, 'day': day}
                attendance_trends_data.append(data)

    return attendance_trends_data


def get_attendance_courses_per_grade(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date):
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select wco.grade,count(case when wco.subject='Maths' and wsa.is_present='yes' then 1 end) as mathspresent," \
            " count(case when wco.subject='Science' and wsa.is_present='yes' then 1 end) as sciencepresent," \
            "count(case when wco.subject='English Foundation' and wsa.is_present='yes' then 1 end) as englishpresents, " \
            "count(case when wsa.is_present='yes' then 1 end) as total_presents from web_sessionattendance wsa, web_session ws,web_offering wo,web_course wco," \
            " web_center wc where wsa.session_id=ws.id and ws.offering_id=wo.id and wo.course_id=wco.id and wo.center_id=wc.id " \
            "and wco.subject in ('Maths','Science','English Foundation') and ws.date_start>='" + start_date + "' and ws.date_end<'" + end_date + "' "
    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = apply_filter_to_query(query, statenames, 'state_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = apply_filter_to_query(query, centernames, 'center_param')
    if delivery_partner != '' and len(delivery_partner) > 0 and delivery_partner[0] != 'All':
        query = apply_filter_to_query(query, delivery_partner, 'delivery_param')
    if funding_partner != '' and len(funding_partner) > 0 and funding_partner[0] != 'All':
        query = apply_filter_to_query(query, funding_partner, 'funding_param')
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = apply_filter_to_query(query, grades, 'grade_param')
    if start_date != '' and len(start_date) > 0:
        query += " and wo.start_date >='" + start_date + "'"
    if end_date != '' and len(end_date):
        query += " and wo.end_date <='" + end_date + "'"
    query += " group by wco.grade "
    dict_cur.execute(query)
    total_attendance_grade_and_course_wise = list(dict_cur.fetchall());
    grade_wise_json_data = []
    tot_user_cur.close()
    db.close()
    dict_cur.close()
    if total_attendance_grade_and_course_wise:
        for attendance in total_attendance_grade_and_course_wise:
            if attendance['total_presents'] > 0:
                """maths = (round(((float(attendance['mathspresent'])/attendance['total_presents'])*100 ),2))
                science = (round(((float(attendance['sciencepresent'])/attendance['total_presents'])*100 ),2))
                english = (round(((float(attendance['englishpresents'])/attendance['total_presents'])*100 ),2))
                attendance_data = {'grade':'Grade'+attendance['grade'],'maths':maths,'science':science,'english':english}"""
                maths = float(attendance['mathspresent']) / attendance['total_presents'] * 100
                science = float(attendance['sciencepresent']) / attendance['total_presents'] * 100
                english = float(attendance['englishpresents']) / attendance['total_presents'] * 100
                number_list = [maths, science, english]
                round_list = round_to_100(number_list)
                maths_perc = round_list[0]
                science_perc = round_list[1]
                english_perc = round_list[2]
                attendance_data = {'grade': 'Grade' + attendance['grade'], 'maths': maths_perc, 'science': science_perc,
                                   'english': english_perc}
                grade_wise_json_data.append(attendance_data)

    return grade_wise_json_data


def get_scholastic_outcome(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date, category):
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select wco.subject, count(case when ((ws.obtained_marks*100)/ws.total_marks)>=90 then 1 end) as excellent," \
            " count(case when ((ws.obtained_marks*100)/ws.total_marks)<90 and ((ws.obtained_marks*100)/ws.total_marks)>=70 then 1 end) " \
            "as very_good,count(case when ((ws.obtained_marks*100)/ws.total_marks)<70 and ((ws.obtained_marks*100)/ws.total_marks)>=50 " \
            "then 1 end) as good,count(case when ((ws.obtained_marks*100)/ws.total_marks)<50 and " \
            "((ws.obtained_marks*100)/ws.total_marks)>=35 then 1 end) as average,count(case when ((ws.obtained_marks*100)/ws.total_marks)<35 then 1 end) as poor, " \
            "count(is_present) as total_present from web_scholastic ws,web_learningrecord wl,web_offering wo,web_course wco, web_center wc where ws.learning_record_id=wl.id " \
            "and wl.offering_id=wo.id and wo.course_id=wco.id and wo.center_id=wc.id and ws.is_present='yes' "
    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = apply_filter_to_query(query, statenames, 'state_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = apply_filter_to_query(query, centernames, 'center_param')
    if delivery_partner != '' and len(delivery_partner) > 0 and delivery_partner[0] != 'All':
        query = apply_filter_to_query(query, delivery_partner, 'delivery_param')
    if funding_partner != '' and len(funding_partner) > 0 and funding_partner[0] != 'All':
        query = apply_filter_to_query(query, funding_partner, 'funding_param')
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = apply_filter_to_query(query, grades, 'grade_param')
    if category != '' and len(category) > 0 and category[0] != 'All':
        query = apply_filter_to_query(query, category, 'category_param')
    if start_date != '' and len(start_date) > 0:
        query += " and wo.start_date >='" + start_date + "'"
    if end_date != '' and len(end_date):
        query += " and wo.end_date <='" + end_date + "'"
    query += " group by wco.subject "
    dict_cur.execute(query)
    scholastic_outcome = list(dict_cur.fetchall());
    tot_user_cur.close()
    db.close()
    dict_cur.close()
    final_scholastic_outcome = []
    if scholastic_outcome:
        for outcome in scholastic_outcome:
            if outcome['total_present'] > 0:
                totalSum = outcome['poor'] + outcome['average'] + outcome['good'] + outcome['very_good'] + outcome[
                    'excellent']
                if outcome['total_present'] != totalSum:
                    outcome['total_present'] = totalSum
                """poor_perc = (round(((float(outcome['poor'])/outcome['total_present'])*100 ),2))
                average_perc = (round(((float(outcome['average'])/outcome['total_present'])*100 ),2))
                good_perc = (round(((float(outcome['good'])/outcome['total_present'])*100 ),2))
                very_good_perc = (round(((float(outcome['very_good'])/outcome['total_present'])*100 ),2))
                excellent_perc = (round(((float(outcome['excellent'])/outcome['total_present'])*100 ),2))"""
                poor_perc = float(outcome['poor']) / outcome['total_present'] * 100
                average_perc = float(outcome['average']) / outcome['total_present'] * 100
                good_perc = float(outcome['good']) / outcome['total_present'] * 100
                very_good_perc = float(outcome['very_good']) / outcome['total_present'] * 100
                excellent_perc = float(outcome['excellent']) / outcome['total_present'] * 100
                number_list = [poor_perc, average_perc, good_perc, very_good_perc, excellent_perc]
                round_list = round_to_100(number_list)
                poor_perc = round_list[0]
                average_perc = round_list[1]
                good_perc = round_list[2]
                very_good_perc = round_list[3]
                excellent_perc = round_list[4]
                outcome_data = {'poor': poor_perc, 'average': average_perc, 'good': good_perc,
                                'veryGood': very_good_perc, 'excellent': excellent_perc, 'subject': outcome['subject']}
                final_scholastic_outcome.append(outcome_data)

    return final_scholastic_outcome


def get_co_scholastic_outcome(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date):
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT wcos.pr_curious as Curious,wcos.pr_attentiveness as Attentiveness,wcos.pr_self_confidence as " \
            "'Self Confidence',wcos.lr_responsibility as Responsibility ,wcos.lr_supportiveness as " \
            "Supportiveness,wcos.bh_positive_attitude as 'Positive Attitude' ,wcos.ee_widerperspective as " \
            "'Wider Perspective',wcos.bh_courteousness as Courteousness  FROM web_coscholastic wcos," \
            "web_learningrecord wlr,web_offering wo,web_course wco,web_center wc where " \
            "wcos.learning_record_id=wlr.id and wlr.offering_id=wo.id and wo.course_id=wco.id and " \
            "wo.center_id=wc.id and wco.grade in ('5','6','7','8') " \
            "and wcos.pr_curious  in ('Very Good','Good','Average','Needs Improvement') " \
            "and wcos.pr_attentiveness  in ('Very Good','Good','Average','Needs Improvement') " \
            "and wcos.pr_self_confidence  in ('Very Good','Good','Average','Needs Improvement') " \
            "and wcos.lr_responsibility  in ('Very Good','Good','Average','Needs Improvement') " \
            "and wcos.lr_supportiveness  in ('Very Good','Good','Average','Needs Improvement') " \
            "and wcos.bh_positive_attitude  in ('Very Good','Good','Average','Needs Improvement') " \
            "and wcos.ee_widerperspective  in ('Very Good','Good','Average','Needs Improvement') " \
            "and wcos.bh_courteousness  in ('Very Good','Good','Average','Needs Improvement') ";
    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = apply_filter_to_query(query, statenames, 'state_param')
    if delivery_partner != '' and len(delivery_partner) > 0 and delivery_partner[0] != 'All':
        query = apply_filter_to_query(query, delivery_partner, 'delivery_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = apply_filter_to_query(query, centernames, 'center_param')
    if funding_partner != '' and len(funding_partner) > 0 and funding_partner[0] != 'All':
        query = apply_filter_to_query(query, funding_partner, 'funding_param')
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = apply_filter_to_query(query, grades, 'grade_param')
    if start_date != '' and len(start_date) > 0:
        query += " and wo.start_date >='" + start_date + "'"
    if end_date != '' and len(end_date):
        query += " and wo.end_date <='" + end_date + "'"
    dict_cur.execute(query)
    co_scholastic_outcome = list(dict_cur.fetchall());
    tot_user_cur.close()
    db.close()
    dict_cur.close()
    return co_scholastic_outcome


def get_aggregate_level_subject_wise(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date, diag_category_list):
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT count(wd.aggregate_level) as level,wd.subject FROM web_diagnostic wd ,web_offering wo,web_course" \
            " wco,web_center wc where wd.offering_id=wo.id and wo.course_id=wco.id and wo.center_id=wc.id and " \
            "wco.grade in ('5','6','7','8') "
    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = apply_filter_to_query(query, statenames, 'state_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = apply_filter_to_query(query, centernames, 'center_param')
    if delivery_partner != '' and len(delivery_partner) > 0 and delivery_partner[0] != 'All':
        query = apply_filter_to_query(query, delivery_partner, 'delivery_param')
    if funding_partner != '' and len(funding_partner) > 0 and funding_partner[0] != 'All':
        query = apply_filter_to_query(query, funding_partner, 'funding_param')
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = apply_filter_to_query(query, grades, 'grade_param')
    if diag_category_list != '' and len(diag_category_list) > 0 and diag_category_list[0] != 'All':
        query = apply_filter_to_query(query, diag_category_list, 'diag_grade_param')
    if start_date != '' and len(start_date) > 0:
        query += " and wo.start_date >='" + start_date + "'"
    if end_date != '' and len(end_date):
        query += " and wo.end_date <='" + end_date + "'"
    query += " group by subject"
    dict_cur.execute(query)
    total_aggregate_level_subject_wise = list(dict_cur.fetchall());
    tot_user_cur.close()
    db.close()
    dict_cur.close()
    return total_aggregate_level_subject_wise


def get_diagonostic_outcome(statenames,delivery_partner,funding_partner, centernames, grades, start_date, end_date, diag_category_list):
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT wd.aggregate_level,wd.subject FROM web_diagnostic wd ,web_offering wo,web_course wco,web_center wc" \
            " where wd.offering_id=wo.id and wo.course_id=wco.id and wo.center_id=wc.id and wco.grade in ('5','6','7','8') "
    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = apply_filter_to_query(query, statenames, 'state_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = apply_filter_to_query(query, centernames, 'center_param')
    if delivery_partner != '' and len(delivery_partner) > 0 and delivery_partner[0] != 'All':
        query = apply_filter_to_query(query, delivery_partner, 'delivery_param')
    if funding_partner != '' and len(funding_partner) > 0 and funding_partner[0] != 'All':
        query = apply_filter_to_query(query, funding_partner, 'funding_param')
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = apply_filter_to_query(query, grades, 'grade_param')
    if diag_category_list != '' and len(diag_category_list) > 0 and diag_category_list[0] != 'All':
        query = apply_filter_to_query(query, diag_category_list, 'diag_grade_param')
    if start_date != '' and len(start_date) > 0:
        query += " and wo.start_date >='" + start_date + "'"
    if end_date != '' and len(end_date):
        query += " and wo.end_date <='" + end_date + "'"
    dict_cur.execute(query)
    diagonostic_outcome = list(dict_cur.fetchall());
    tot_user_cur.close()
    db.close()
    dict_cur.close()
    return diagonostic_outcome


def get_data_for_co_scholastic_outcome(co_scholastic_outcome, remark):
    count = 0
    v_good = 0.0
    gd = 0.0
    avg = 0.0
    pr = 0.0
    v_good_per = 0.0
    gd_per = 0.0
    avg_per = 0.0
    pr_per = 0.0
    for co_scholastic_list in co_scholastic_outcome:
        count = count + 1
        if co_scholastic_list[remark].replace(' ', '').lower() == 'verygood':
            v_good = v_good + 1
        elif co_scholastic_list[remark].replace(' ', '').lower() == 'good':
            gd = gd + 1
        elif co_scholastic_list[remark].replace(' ', '').lower() == 'average':
            avg = avg + 1
        elif co_scholastic_list[remark].replace(' ', '').lower() == 'needsimprovement':
            pr = pr + 1
    if count != 0:
        v_good_per = (v_good * 100) / count
        avg_per = (avg * 100) / count
        gd_per = (gd * 100) / count
        pr_per = (pr * 100) / count
    if co_scholastic_outcome:
        number_list = [v_good_per, avg_per, gd_per, pr_per]
        round_list = round_to_100(number_list)
        v_good_per = round_list[0]
        avg_per = round_list[1]
        gd_per = round_list[2]
        pr_per = round_list[3]

    data = {"remark": remark, "veryGood": v_good_per, "good": avg_per, "average": gd_per, "poor": pr_per}
    return data


def error_gen(actual, rounded):
    divisor = math.sqrt(1.0 if actual < 1.0 else actual)
    return abs(rounded - actual) ** 2 / divisor


def round_to_100(percents):
    n = len(percents)
    rounded = [int(x) for x in percents]
    up_count = 100 - sum(rounded)
    errors = [(error_gen(percents[i], rounded[i] + 1) - error_gen(percents[i], rounded[i]), i) for i in range(n)]
    rank = sorted(errors)
    for i in range(up_count):
        if i >= len(rank):
            continue
        rounded[rank[i][1]] += 1
    return rounded


def get_data_for_diagonostic(diagonostic_outcome, subject, total_aggregate_leve_subject):
    l1_percentage = 0.0
    l2_percentage = 0.0
    l3_percentage = 0.0
    l4_percentage = 0.0
    l1 = 0.0
    l2 = 0.0
    l3 = 0.0
    l4 = 0.0
    count = 0
    l1_per = 0.0
    l2_per = 0.0
    l3_per = 0.0
    l4_per = 0.0
    if diagonostic_outcome:
        for total_outcome in diagonostic_outcome:
            if total_outcome['aggregate_level'] == 'L1' and total_outcome['subject'] == subject:
                l1 = l1 + 1
            if total_outcome['aggregate_level'] == 'L2' and total_outcome['subject'] == subject:
                l2 = l2 + 1
            if total_outcome['aggregate_level'] == 'L3' and total_outcome['subject'] == subject:
                l3 = l3 + 1
            if total_outcome['aggregate_level'] == 'L4' and total_outcome['subject'] == subject:
                l4 = l4 + 1
    for subject_total in total_aggregate_leve_subject:
        if subject_total['subject'] == subject:
            count = subject_total['level']
    if count != 0:
        l1_percentage = (l1 * 100) / count
        l2_percentage = (l2 * 100) / count
        l3_percentage = (l3 * 100) / count
        l4_percentage = (l4 * 100) / count
        number_list = [l1_percentage, l2_percentage, l3_percentage, l4_percentage]
        round_list = round_to_100(number_list)
        l1_per = round_list[0]
        l2_per = round_list[1]
        l3_per = round_list[2]
        l4_per = round_list[3]
    data = {"subject": subject, "l1": l1_per, "l2": l2_per, "l3": l3_per, "l4": l4_per}
    return data


def apply_filter_to_query(query, filter_list_param, query_param):
    if query_param == 'grade_param':
        filter_list_param = str(filter_list_param).replace('th', '')
        filter_list_param = filter_list_param.split(",")
    list_length = len(filter_list_param)
    param_for = ''
    i = 0
    for param in filter_list_param:
        param_for += "'" + param + "'"
        if list_length - 1 != i:
            param_for += ','
        i += 1
    if param_for != '':
        if query_param == 'state_param':
            query += 'and wc.state in (' + param_for + ')'
        elif query_param == 'delivery_param':
            query += ' and wc.delivery_partner_id in (' + param_for + ')'
        elif query_param == 'funding_param':
            query += ' and wc.funding_partner_id in (' + param_for + ')'
        elif query_param == 'center_param':
            query += 'and wc.name in (' + param_for + ')'
        elif query_param == 'grade_param':
            query += 'and wco.grade in (' + param_for + ')'
        elif query_param == 'category_param':
            query += 'and ws.category in (' + param_for + ')'
        elif query_param == 'diag_grade_param':
            query += 'and wd.category in (' + param_for + ')'
    return query


@login_required
def activities(request):
    if request.user.is_authenticated:
        userId = request.GET.get('user_id', '')
        username = request.GET.get('ass_username', '')
        flag = request.GET.get('set_flag', '')
        cur_user = request.user
        if username:
            user = User.objects.get(username=username)
            userDetails = UserProfile.objects.get(user=user)
            openActivity = Task.objects.filter(taskStatus='Open', assignedTo=username)
            history = Task.objects.filter(assignedTo=username).exclude(taskStatus='Open')
            return render_response(request, 'task/performed_on.html',
                                   {'openActivity': openActivity, 'history': history, 'flag': flag, 'user': user,
                                    'userDetails': userDetails, 'cur_user': cur_user})
        elif userId:
            user = User.objects.get(id=userId)
            userDetails = UserProfile.objects.get(user=user)
            openActivity = Task.objects.filter(taskStatus='Open', performedOn_userId=userId)
            history = Task.objects.filter(performedOn_userId=userId).exclude(taskStatus='Open')
            return render_response(request, 'task/performed_on.html',
                                   {'openActivity': openActivity, 'history': history, 'flag': flag, 'user': user,
                                    'userDetails': userDetails, 'cur_user': cur_user})
    else:
        return redirect("/?show_popup=true&type=login")


@csrf_exempt
def students_progress_report(request):
    print "print in students"
    statenames = request.GET.getlist('stateName', '')
    centernames = request.GET.getlist('centerName', '')
    grades = request.GET.getlist('grade', '')
    delivery_partner = request.GET.getlist('partner_id', '')
    funding_partner = request.GET.getlist('fund_partner_id', '')
    AssessmentYears = request.GET.getlist('AssessmentYear', '')
    assessment_id = request.GET.get('assessment_id', '')
    coursenames = request.GET.getlist('course', '')
    term_category = request.GET.getlist('termId', '')
    print "term_category ", term_category
    redio_filter = request.GET.get('rediobtn', '')
    flag = request.GET.get('flag', '')
    if statenames == '' or None:
        statenames = ['All']
    if delivery_partner == '' or None:
        delivery_partner = ['All']
    if funding_partner == '' or None:
        funding_partner = ['All']
    if centernames == '' or None:
        centernames = ['All']
    if grades == '' or None:
        grades = ['All']
    if AssessmentYears == '' or None:
        AssessmentYears = ['All']
    if coursenames == '' or None:
        coursenames = ['All']
    if term_category == '' or None:
        term_category = ['All']

    try:
        ref = ReferenceChannel.objects.get(id=request.user.userprofile.referencechannel.id)
    except:
        ref = None
    without_partner = False

    if request.user.is_superuser or ref is None:
        without_partner = True

    elif has_role(request.user.userprofile,"Delivery co-ordinator"):
        states = Center.objects.filter(delivery_coordinator=request.user,status='Active').order_by('state').values('state').distinct()
        centers = Center.objects.filter(delivery_coordinator=request.user,status='Active').order_by('name').values('name').distinct()
    elif has_role(request.user.userprofile, "Partner Account Manager") or has_pref_role(request.user.userprofile, "Partner Account Manager"):
        db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
        user=settings.DATABASES['default']['USER'],
        passwd=settings.DATABASES['default']['PASSWORD'],
        db=settings.DATABASES['default']['NAME'],
        charset="utf8",
        use_unicode=True)
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query = "select partner_id  as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
        dict_cur.execute(query)
        partner_id = [str(each['value']) for each in dict_cur.fetchall()]
        partner_id.sort()
        states = Center.objects.filter(( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id))& Q(status='Active') ).order_by('state').values('state').distinct()
       
        centers  =Center.objects.filter(( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id))& Q(status='Active')).order_by('name').values('name').distinct()
        db.close()
        dict_cur.close()
    elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
        partner = None
        if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
            try:
                partner = Partner.objects.get(contactperson=request.user)
            except:
                partner = None
        else:
            partner = ref.partner
        if partner and len(partner.partnertype.filter(name='Delivery Partner')) > 0:
            states = Center.objects.filter(partner_school__partner=partner).order_by('state').values('state').distinct()
            centers = Center.objects.filter(partner_school__partner=partner).order_by('name').values('name').distinct()
        else:
            without_partner = True
    if without_partner:
        states = Center.objects.order_by('state').values('state').distinct()
        centers = Center.objects.order_by('name').values('name').distinct()
    if centers:
        center_delivery_partner = Center.objects.filter(name__in = centers)
        if center_delivery_partner:  
            if center_delivery_partner[0].delivery_partner != None :
                delivery_partner = center_delivery_partner[0].delivery_partner.name_of_organization
            if center_delivery_partner[0].funding_partner != None :
                funding_partner = center_delivery_partner[0].funding_partner.name_of_organization 
    courses = Course.objects.order_by('subject').values('subject').filter(
        Q(subject='Maths') | Q(subject='Science') | Q(subject='English Foundation')).distinct()
    terms = Scholastic.objects.values('category').distinct()
    diag_terms = Diagnostic.objects.values('category').distinct().exclude(category=None)


    if has_role(request.user.userprofile,"Partner Admin"):
        center_board=Center.objects.filter(Q(delivery_partner__contactperson=request.user) | Q(funding_partner__contactperson=request.user)).values('board').distinct()
        ayfy =  Ayfy.objects.filter(types='Academic Year',board__in=center_board).values('id', 'title', 'board',
                                                             'start_date')
    elif has_role(request.user.userprofile,"OUAdmin"):
        center_board=Center.objects.filter(orgunit_partner__contactperson=request.user).values('board').distinct()
        ayfy = Ayfy.objects.filter(types='Academic Year',board__in=center_board).values('id', 'title', 'board',
                                                             'start_date')
    else:
        ayfy = Ayfy.objects.filter(types='Academic Year').values('id', 'title', 'board',
                                                             'start_date')  # .order_by('-start_date')
    progress_report_data = ""
    if assessment_id and assessment_id == 'coscholastic':
        progress_report_data = get_student_progress_report_for_coscholastic(statenames, centernames, grades,
                                                                            coursenames, AssessmentYears, redio_filter)
    elif assessment_id and assessment_id == 'diagnostic':
        user=request.user
        progress_report_data = get_student_progress_report_for_diagnostic(statenames, centernames, grades, coursenames,
                                                                          AssessmentYears, redio_filter, term_category, user)
    else:
        progress_report_data = get_progress_report_data_for_scholastic(statenames, centernames, grades, coursenames,
                                                                       AssessmentYears, redio_filter, term_category)

    students_reports = ""
    if flag:
        ayear = ''
        statess = ''
        center = ''
        course = ''
        grade = ''
        term = ''
        if AssessmentYears:
            for ay in AssessmentYears:
                ayear = ay
        statess = (','.join(statenames)).replace(u'\xa0', u' ')
        for cen in centernames:
            center += cen + ","
        for crs in coursenames:
            course += crs + ","
        for grd in grades:
            grade += grd + ","
        for ctg in term_category:
            term += ctg + ","
        save_user_activity(request, 'Searched:My Students - Students Dashboard - students Progress Report:' + str(
            statess) + ' ' + str(center) + ' ' + str(grade) + ' ' + str(ayear) + ' ' + str(course) + ' ' + str(
            assessment_id) + ',' + term, 'Action')
        jsondata = simplejson.dumps(progress_report_data)
        return HttpResponse(jsondata, mimetype='application/json')
    else:
        if progress_report_data:
            students_reports = simplejson.dumps(progress_report_data)
        save_user_activity(request, 'Viewed Page: My Students - Students Dashboard - students Progress Report',
                           'Page Visit')
        return render_response(request, 'report_generation/progress_report.html',
                               {'states': states, 'centers': centers,'delivery_partner':delivery_partner,'funding_partner':funding_parter, 'courses': courses, 'terms': terms,
                                'students_reports': students_reports, 'statenames': statenames, 'ayfy': ayfy,
                                'diag_terms': diag_terms})

def get_progress_report_data_for_scholastic(statenames, centernames, grades, coursenames, AssessmentYears, redio_filter,
                                            term_category):
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                         user=settings.DATABASES['default']['USER'],
                         passwd=settings.DATABASES['default']['PASSWORD'],
                         db=settings.DATABASES['default']['NAME'],
                         charset="utf8",
                         use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select ws.id,ws.name,wc.name as centername,wco.grade,wsc.category,wo.academic_year_id,DATE_FORMAT(wlr.date_created , '%d/%m/%Y') AS date_created,  sum(case when wco.subject='Math' " \
            "then wsc.total_marks end) as totalMaths, sum(case when wco.subject='Math' " \
            "then wsc.obtained_marks end) as maths,sum(case when wco.subject='science' then wsc.total_marks end) as toalScience, sum(case when wco.subject='science' then wsc.obtained_marks end) as science," \
            "sum(case when wco.subject='English Foundation' then wsc.total_marks end) as totalEnglish, sum(case when wco.subject='English Foundation' then wsc.obtained_marks end) as english, " \
            "sum(case when wco.subject='Math' or wco.subject='Science' or wco.subject='English Foundation' then total_marks end) " \
            "as sumOfTotal,sum(case when wco.subject='Math' or wco.subject='Science' or wco.subject='English Foundation' then obtained_marks end) " \
            "as total from web_scholastic wsc,web_learningrecord wlr,web_student ws, web_offering wo,web_course wco, web_center wc " \
            "where wsc.learning_record_id=wlr.id and wlr.student_id=ws.id and wlr.offering_id=wo.id and wo.course_id=wco.id and " \
            "wo.center_id=wc.id and wsc.is_present='yes' and (ws.status='Active' or ws.status='Alumni') "

    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = filter_for_query(query, statenames, 'state_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = filter_for_query(query, centernames, 'center_param')
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = filter_for_query(query, grades, 'grade_param')
    if coursenames != '' and len(coursenames) > 0 and coursenames[0] != 'All':
        query = filter_for_query(query, coursenames, 'course_param')
    if AssessmentYears != '' and len(AssessmentYears) > 0 and AssessmentYears[0] != 'All':
        query += 'and wo.academic_year_id = ' + AssessmentYears[0]
    if term_category != '' and len(term_category) > 0 and term_category[0] != 'All':
        query = filter_for_query(query, term_category, 'term')

    query += " group by wsc.category,wco.grade,ws.id "
    if redio_filter and redio_filter == 'top10':
        query += " order by total desc limit 10 "
    elif redio_filter and redio_filter == 'btm10':
        query += " order by total asc limit 10 "
    else:
        query += " order by total desc "
    print "print scholatic query ", query
    dict_cur.execute(query)
    listdata = dict_cur.fetchall()
    tot_user_cur.close()
    dict_cur.close()
    data = simplejson.dumps(listdata)
    return data


def get_student_progress_report_for_diagnostic(statenames, centernames, grades, coursenames, AssessmentYears,
                                             redio_filter, term_category, user):

    try:
        partner = Partner.objects.get(contactperson=user)
    except:
        partner =  None
    final_data = []
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select ws.id,ws.name,wsc.subject,wsc.aggregate_level,wco.grade,wc.name as centername," \
            " wo.academic_year_id,DATE_FORMAT(wsc.date_created , '%d/%m/%Y') AS date_created, wsc.category " \
            " FROM web_diagnostic wsc, web_student ws , web_offering wo, web_center wc, web_course wco, " \
            " web_learningrecord wlr where wsc.student_id=ws.id and wsc.offering_id=wo.id " \
            " and wo.course_id=wco.id and wo.center_id=wc.id and wlr.student_id=ws.id " \
            " and (ws.status='Active' or ws.status='Alumni') and wc.status='Active'"
    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = filter_for_query(query, statenames, 'state_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = filter_for_query(query, centernames, 'center_param')
    if partner:
        for ptype in partner.partnertype.all():
            if ptype.id == 1:
               query+= " and wc.partner_school_id in (select id from partner_myschool where partner_id ='"+str(partner.id)+"'"
            elif ptype.id == 2:
               query+=" and wc.partner_school_id in (select id from partner_myschool where partner_id ='"+str(partner.id)+"') and delivery_partner_id='"+str(partner.id)+"'"
            elif ptype.id == 3:
                query+=" and wc.partner_school_id in (select id from partner_myschool where partner_id ='"+str(partner.id)+"' and funding_partner_id='"+str(partner.id)+"'"
            elif ptype.id == 4:
                query+=" and wc.orgunit_partner_id='"+str(partner.id)+"'"
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = filter_for_query(query, grades, 'grade_param')
    if coursenames != '' and len(coursenames) > 0 and coursenames[0] != 'All':
        query = filter_for_query(query, coursenames, 'course_param')
    if AssessmentYears != '' and len(AssessmentYears) > 0 and AssessmentYears[0] != 'All':
        query += ' and wo.academic_year_id = ' + AssessmentYears[0]
    if term_category != '' and len(term_category) > 0 and term_category[0] != 'All':
        query = filter_for_query(query, term_category, 'diag_term')
    query += " group by wsc.id "
    if redio_filter and redio_filter == 'top10':
        query += " order by wsc.aggregate_level asc limit 10 "
    elif redio_filter and redio_filter == 'btm10':
        query += " order by wsc.aggregate_level desc limit 10 "
    else:
        query += " order by wsc.aggregate_level asc "

    dict_cur.execute(query)
    listdata = dict_cur.fetchall()
    tot_user_cur.close()
    dict_cur.close()
    if listdata:
        i = 0
        list_length = len(listdata)
        for data in listdata:
            if list_length != i:
                local_data = {"student_id": data['id'], "Student Name": data['name'], "Center": data['centername'],
                              "Subject": data['subject'], "Aggregate Level": data['aggregate_level'],
                              "Grade": data['grade'], "date_created": data['date_created'],
                              "academic_year_id": data['academic_year_id'], "Category": data['category']}
                final_data.append(local_data)
                i += 1
    return final_data


def get_student_progress_report_for_coscholastic(statenames, centernames, grades, coursenames, AssessmentYears,
                                                 redio_filter):
    final_data = []
    db = evd_getDB()
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)

    query = "select distinct(ws.id),ws.name,wco.subject,wc.name as centername,wco.grade,wo.academic_year_id,DATE_FORMAT(wlr.date_created , '%d/%m/%Y') AS date_created, \
            wsc.pr_curious, \
            wsc.pr_attentiveness, \
            wsc.pr_self_confidence,  \
            wsc.lr_supportiveness, \
            wsc.lr_initiativeness, \
            wsc.bh_positive_attitude, \
            wsc.bh_courteousness, \
            wsc.ee_widerperspective, \
            wsc.ee_emotional_connect, \
            wsc.ee_technology_exposure \
            FROM web_coscholastic wsc," \
            "web_learningrecord wlr, web_offering wo, web_lrcategory wlc, web_center wc,web_course wco, web_student ws " \
            "where wsc.learning_record_id=wlr.id and wlr.student_id=ws.id and wlr.category_id=wlc.id and wlr.offering_id=wo.id" \
            " and wo.course_id=wco.id and wo.center_id=wc.id and (ws.status='Active' or ws.status='Alumni')"

    if statenames != '' and len(statenames) > 0 and statenames[0] != 'All':
        query = filter_for_query(query, statenames, 'state_param')
    if centernames != '' and len(centernames) > 0 and centernames[0] != 'All':
        query = filter_for_query(query, centernames, 'center_param')
    if grades != '' and len(grades) > 0 and grades[0] != 'All':
        query = filter_for_query(query, grades, 'grade_param')
    if coursenames != '' and len(coursenames) > 0 and coursenames[0] != 'All':
        query = filter_for_query(query, coursenames, 'course_param')
    if AssessmentYears != '' and len(AssessmentYears) > 0 and AssessmentYears[0] != 'All':
        query += 'and wo.academic_year_id = ' + AssessmentYears[0]

    dict_cur.execute(query)
    listdata = dict_cur.fetchall()
    tot_user_cur.close()
    dict_cur.close()
    local_data = ""
    if listdata:
        i = 0
        list_length = len(listdata)
        for data in listdata:
            curious = data['pr_curious']

            if list_length != i:
                local_data = {"student_id": data['id'],
                              "Student Name": data['name'],
                              "centername": data['centername'],
                              "grade": data['grade'],
                              "subject": data['subject'],
                              "date_created": data['date_created'],
                              "academic_year_id": data['academic_year_id'],
                              "curious": data['pr_curious'],
                              "attentiveness": data['pr_attentiveness'],
                              "self_confidence": data['pr_self_confidence'],
                              "supportiveness": data['lr_supportiveness'],
                              "positive_attitude": data['bh_positive_attitude'],
                              "initiativeness": data['lr_initiativeness'],
                              "courteousness": data['bh_courteousness'],
                              "widerperspective": data['ee_widerperspective'],
                              "emotional_connect": data['ee_emotional_connect'],
                              "technology_exposure": data['ee_technology_exposure'],
                              "total": 0}
                final_data.append(local_data)
                i += 1
        if redio_filter != 'all':
            if final_data:
                final_dat_list = []
                for final_list in final_data:
                    remark_list = ['curious', 'attentiveness', 'self_confidence', 'supportiveness', 'positive_attitude']
                    data_list = get_coscholastic_data(final_list, remark_list)
                    final_dat_list.append(data_list)
            if redio_filter and redio_filter == 'top10':
                short_list = sorted(final_dat_list, key=operator.itemgetter('total'), reverse=True)
            else:
                short_list = sorted(final_dat_list, key=operator.itemgetter('total'))
            if short_list:
                first_ten_list = short_list[:10]
                final_data = first_ten_list

    return final_data


def get_coscholastic_data(final_list, remark):
    excellent = 0
    veryGood = 0
    good = 0
    average = 0
    needsImprovement = 0
    notObserved = 0
    if final_list:
        total = 0
        temp = 0
        for data in remark:
            if final_list[data] == "Excellent":
                excellent = 10
                temp = temp + excellent
            elif final_list[data] == "Very Good":
                veryGood = 8
                temp = temp + veryGood
            elif final_list[data] == "V Good":
                veryGood = 8
                temp = temp + veryGood
            elif final_list[data] == "Good":
                good = 6
                temp = temp + good
            elif final_list[data] == "Average":
                average = 4
                temp = temp + average
            elif final_list[data] == "Needs Improvement":
                needsImprovement = 2
                temp = temp + needsImprovement
            elif final_list[data] == "Not Observed":
                notObserved = 0
            total = temp
    local_data = {"student_id": final_list['student_id'], "Student Name": final_list['Student Name'],
                  "centername": final_list['centername'], "grade": final_list['grade'],
                  "curious": final_list['curious'], "attentiveness": final_list['attentiveness'],
                  "self_confidence": final_list['self_confidence'], "supportiveness": final_list['supportiveness'],
                  "positive_attitude": final_list['positive_attitude'], "total": total}
    return local_data


def get_student_progress_report(student, statenames, centernames, grades, coursenames, AssessmentYears):
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                         user=settings.DATABASES['default']['USER'],
                         passwd=settings.DATABASES['default']['PASSWORD'],
                         db=settings.DATABASES['default']['NAME'],
                         charset="utf8",
                         use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select ws.id,ws.name, wlr.date_created,wco.subject, wco.grade,wc.name as centername,sum(wsc.obtained_marks), sum(wsc.total_marks)" \
            " FROM web_scholastic wsc,web_learningrecord wlr, web_offering wo, web_lrcategory wlc, web_center wc,web_course wco," \
            " web_student ws  where wsc.learning_record_id=wlr.id and wlr.student_id=ws.id and wlr.category_id=wlc.id and " \
            "wlr.offering_id=wo.id and wo.course_id=wco.id and wo.center_id=wc.id and ws.id='" + str(
        student['id']) + "'"
    '''if statenames != '' and len(statenames)>0 and statenames[0]!='All':
        query = filter_for_query(query, statenames, 'state_param')
    if centernames != '' and len(centernames)>0 and centernames[0]!='All':
        query = filter_for_query(query, centernames, 'center_param')
    if grades != '' and len(grades)>0 and grades[0]!='All': 
        query = filter_for_query(query, grades, 'grade_param')
    if coursenames != '' and len(coursenames)>0 and coursenames[0]!='All':
        query = filter_for_query(query, coursenames, 'course_param')'''
    # if AssessmentYears != '' and len(AssessmentYears)>0 and AssessmentYears[0]!='All':
    # query = filter_for_query(query, AssessmentYears, 'ay_param')
    query += " group by wco.subject order by ws.id,wco.subject "
    dict_cur.execute(query)
    data = ""
    listdata = dict_cur.fetchall()
    tot_user_cur.close()
    dict_cur.close()
    local_data = ""

    math_obtained = 0
    english_obtained = 0
    science_obtained = 0
    dlp_obtained = 0
    jor_obtained = 0
    extras_obtained = 0
    total_marks = 0
    list_length = len(listdata)
    total_marks = 0
    for data in listdata:
        if data['subject'] == 'Maths':
            math_obtained = data['sum(wsc.obtained_marks)']
            total_marks += data['sum(wsc.total_marks)']
        elif data['subject'] == 'Science':
            science_obtained = data['sum(wsc.obtained_marks)']
            total_marks += data['sum(wsc.total_marks)']
        elif data['subject'] == 'English Foundation':
            english_obtained = data['sum(wsc.obtained_marks)']
            total_marks += data['sum(wsc.total_marks)']
        local_data = {"student_id": data['id'], "Student Name": data['name'], "Center": data['centername'],
                      "Grade": data['grade'], "Math": math_obtained, "English": english_obtained,
                      "Science": science_obtained, "Total Marks": total_marks}

    return local_data


def filter_for_query(query, filter_list_param, query_param):
    param_list = []
    param_for = ''
    i = 0
    for param in filter_list_param:
        param_list.append(param.split(","))
        for params in param_list:
            list_length = len(params)
            for param_name in params:
                param_for += "'" + param_name + "'"
                if list_length - 1 != i:
                    param_for += ','
                i += 1
    if param_for != '':
        if query_param == 'state_param':
            query += ' and wc.state in (' + param_for + ')'
        if query_param == 'delivery_param':
            query += ' and wc.delivery_partner in (' + param_for + ')'
        if query_param == 'funding_param':
            query += ' and wc.funding_partner_id in (' + param_for + ')'
        if query_param == 'center_param':
            query += ' and wc.name in (' + param_for + ')'
        if query_param == 'grade_param':
            query += ' and wco.grade in (' + param_for + ')'
        if query_param == 'course_param':
            query += ' and wco.subject in (' + param_for + ')'
        if query_param == 'ay_param':
            query += ' and year(wlr.date_created) in (' + param_for + ')'
        if query_param == 'term':
            query += ' and wsc.category in (' + param_for + ')'
        if query_param == 'diag_term':
            query += ' and wsc.category in (' + param_for + ')'
    return query


def reportCard(request):
    student_id = request.GET.get('studentName', '')
    studentGrade = request.GET.get('gradeId', '')
    statenames = request.GET.getlist('stateId', '')
    centernames = request.GET.getlist('centerId', '')
    delivery_partner = request.GET.getlist('partner_id', '')
    funding_partner = request.GET.getlist('fund_partner_id', '')
    grades = request.GET.get('gradeId', '')
    centerNames = []
    if centernames:
        for centerName in centernames:
            center = centerName.replace('%20-%20', ' - ')
            centerNames.append(center)
            centernames = centerNames
    assessmentYears = request.GET.getlist('yearpicker', '')
    ayfy = Ayfy.objects.filter(types='Academic Year').values('id', 'title', 'board', 'start_date')
    flag1 = request.GET.get('flag1', '')
    if assessmentYears:
        assessmentYears = assessmentYears[0]
    from_progress_report = request.GET.get('flag', '')
    if from_progress_report:
        assessmentYears = request.GET.get('year', '')
        studentGrade = request.GET.get('grade', '')
        if student_id:
            student_progress_data = Student.objects.get(pk=student_id)
            centernames_for_progress = \
            Center.objects.values('id', 'name', 'state').filter(pk=student_progress_data.center_id)[0]
            centerss = []
            centerss.append(centernames_for_progress['name'])
            centernames = centerss
            statess = []
            statess.append(centernames_for_progress['state'])
            statenames = statess
    else:
        if statenames == '' or None:
            statenames = ['All']
        if centernames == '' or None:
            centernames = ['All']
        if delivery_partner == '' or None:
            delivery_partner = ['All']
        if funding_partner == '' or None:
            funding_partner = ['All']
        '''if grades == '' or None:
            grades = ['All']'''
    if student_id == '':
        student_id = Student.objects.order_by('name').values('id').filter(Q(status='Active') | Q(status='Alumni'))[0][
            'id']
    photo = ""
    student = Student.objects.get(pk=student_id)
    studentGrade = student.grade
    if student:
        if student.photo:
            photo_path = os.getcwd() + '/' + student.photo.url
            if os.path.isfile(photo_path):
                photo = '/' + student.photo.url

    sticker_list = []
    sticker_obj = Recognition.objects.filter(object_id=student.id,
                                             content_type=ContentType.objects.get(
                                                 model='student')).values(
        'sticker__sticker_name', 'sticker__sticker_path').annotate(
        countofreg=Count('sticker__sticker_name'))

    if sticker_obj:
        for i in sticker_obj:
            sticker_list.append(i)

    try:
        ref = ReferenceChannel.objects.get(id=request.user.userprofile.referencechannel.id)
    except:
        ref = None
    without_partner = False

    if request.user.is_superuser or ref is None:
        without_partner = True

    elif has_role(request.user.userprofile,'Delivery co-ordinator'):
        states = Center.objects.filter(delivery_coordinator=request.user,status='Active').order_by('state').values('state').distinct()
    elif has_role(request.user.userprofile, "Partner Account Manager") or has_pref_role(request.user.userprofile, "Partner Account Manager"):
        db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
        user=settings.DATABASES['default']['USER'],
        passwd=settings.DATABASES['default']['PASSWORD'],
        db=settings.DATABASES['default']['NAME'],
        charset="utf8",
        use_unicode=True)
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query = "select partner_id  as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
        dict_cur.execute(query)
        partner_id = [str(each['value']) for each in dict_cur.fetchall()]
        partner_id.sort()
        states = Center.objects.filter( (Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id))& Q(status='Active')).order_by('state').values('state').distinct()
        db.close()
        dict_cur.close()       
    elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
        partner = None
        if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
            try:
                partner = Partner.objects.get(contactperson=request.user)
            except:
                partner = None
        else:
            partner = ref.partner
        if partner and len(partner.partnertype.filter(name='Delivery Partner')) > 0:
            states = Center.objects.filter(partner_school__partner=partner).order_by('state').values('state').distinct()
        else:
            without_partner = True
    if without_partner:
        states = Center.objects.order_by('state').values('state').distinct()

    studentnames = Student.objects.order_by('name').values('id', 'name', 'school_rollno').filter(
        Q(status='Active') | Q(status='Alumni')).distinct()
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                         user=settings.DATABASES['default']['USER'],
                         passwd=settings.DATABASES['default']['PASSWORD'],
                         db=settings.DATABASES['default']['NAME'],
                         charset="utf8",
                         use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select wco.subject,count(case when wsa.is_present = 'yes' then 1 end) Present, count(case when wsa.is_present = 'no' then 1 end) Absent from web_center wc, web_course wco, web_offering wo, web_session ws, web_sessionattendance wsa, web_student wstu where wsa.student_id=wstu.id and wsa.session_id=ws.id and ws.offering_id=wo.id and wo.course_id=wco.id and wo.center_id=wc.id and wstu.id='" + str(
        student_id) + "' group by wco.subject"
    dict_cur.execute(query)
    stuendent_attendance_subject_wise = list(dict_cur.fetchall());
    diags = student.diagnostic_set.all()
    if assessmentYears != '' and assessmentYears != 'All':
        diags_lrs = diags.filter(offering__academic_year=assessmentYears)
    else:
        diags_lrs = student.diagnostic_set.all()
    diag_details = []
    for ent in diags_lrs:
        eval_date = ent.date_created.strftime('%b %Y')
        diag = {
            'subject': ent.offering.course.subject,
            'eval_date': eval_date,
            'agg_level': ent.aggregate_level
        }
        diag_details.append(diag)
    lrs = student.learningrecord_set.all()
    print "lrs records ", lrs
    if assessmentYears != '' and assessmentYears != 'All':
        scholastic_det = lrs.filter(category=1, offering__academic_year=assessmentYears)
    else:
        scholastic_det = lrs.filter(category=1)
    scholastic_details = []
    for ent in scholastic_det:
        scholastic_recs = Scholastic.objects.filter(learning_record_id=ent.id)
        if scholastic_recs:
            scholastic_rec = scholastic_recs[0]
            schol = {
                'subject': ent.offering.course.subject,
                'is_present': scholastic_rec.is_present,
                'obtained_marks': scholastic_rec.obtained_marks,
                'total_marks': scholastic_rec.total_marks,
                'eval_date': ent.date_created.strftime('%b %Y')
            }
            scholastic_details.append(schol)

    if assessmentYears != '' and assessmentYears != 'All':
        coschol = lrs.filter(category=2, offering__academic_year=assessmentYears)
    else:
        coschol = lrs.filter(category=2)
    coschol_details = []
    comments = []
    lr_uc = lrs.filter(category=4).order_by('-id')
    if lr_uc:
        lr_uc = lr_uc
        for ent in lr_uc:
            uniquec_rec = UniqueC.objects.get(learning_record_id=ent.id)
            if uniquec_rec:
                comments.append(uniquec_rec.strengths)
                comments.append(uniquec_rec.weaknesses)
    for ent in coschol:
        coschol_recs = CoScholastic.objects.filter(learning_record_id=ent.id)
        if coschol_recs:
            coschol_rec = coschol_recs[0]
            coschol_rec_final = {
                'Attentiveness': coschol_rec.pr_attentiveness,
                'Self Confidence': coschol_rec.pr_self_confidence,
                'Curious': coschol_rec.pr_curious,
                'Courteousness': coschol_rec.bh_courteousness,
                'Positive Attitude': coschol_rec.bh_positive_attitude,
                'Initiativeness': coschol_rec.lr_initiativeness,
                'Responsibility': coschol_rec.lr_responsibility,
                'Supportiveness': coschol_rec.lr_supportiveness,
                'Emotional Connect': coschol_rec.ee_emotional_connect,
                'Wider Perspective': coschol_rec.ee_widerperspective,
                'Technology Exposure': coschol_rec.ee_technology_exposure,
                'teacher': make_number_verb(ent.offering.course.grade) + ' ' + ent.offering.course.subject,
            }
            coschol_details.append(coschol_rec_final)
    '''trans_coschol_dict = {}
    teachers_list =[]
    for record in coschol_details:
        teachers_list.append(record['teacher'])
        for key in record.keys():
            if key not in ['teacher','id','learning_record']:
                trans_coschol_dict.setdefault(key, {})
                trans_coschol_dict[key][record['teacher']] = record[key]
    print "teacher list"
    print teachers_list '''
    '''states_all = simplejson.dumps(statenames)'''
    query = " select DISTINCT YEAR(wo.start_date) as start_date ,wo.end_date from web_offering wo,web_learningrecord wlr,web_student wstd where " \
            "wlr.student_id=wstd.id and wlr.offering_id=wo.id and wstd.id=" + str(student_id)
    dict_cur.execute(query)
    student_ay1 = list(dict_cur.fetchall());
    tot_user_cur.close
    student_ay = []
    for ay in student_ay1:
        start_date = ay['start_date']
        end_date = ay['end_date']
        data = {'start_date': str(start_date), 'end_date': str(end_date)}
        student_ay.append(data)
    query = ""
    endYear = ''
    startYear = ''
    if assessmentYears and assessmentYears != 'All':
        query = "select DISTINCT YEAR(wo.end_date) as end_date,YEAR(wo.start_date) as start_date from web_offering wo,web_learningrecord wlr,web_student wstd" \
                " where wlr.student_id=wstd.id and wlr.offering_id=wo.id and academic_year_id=" + str(
            assessmentYears) + " and wstd.id=" + str(student_id)
        dict_cur.execute(query)
        endDateForStudent = list(dict_cur.fetchall());
        for end in endDateForStudent:
            endYear = end['end_date']
            startYear = end['start_date']
        tot_user_cur.close
    grade_progressreport = []
    if from_progress_report:
        if student_id:
            query = "select DISTINCT wc.grade from web_offering_enrolled_students woes,web_offering wo,web_course wc,web_learningrecord wlr where woes.offering_id=wo.id and wo.course_id=wc.id and woes.student_id='" + str(
                student_id) + "'and wlr.offering_id=wo.id and year(wlr.date_created)='" + str(
                assessmentYears) + "' order by wc.grade"
            dict_cur.execute(query)
            gradeFromProgressReport = dict_cur.fetchall();
            if gradeFromProgressReport:
                for grade_pr in gradeFromProgressReport:
                    grades_pr = grade_pr['grade']
                    grade_progressreport.append(grades_pr)
                tot_user_cur.close
    if flag1:
        studentName = ''
        if student_id:
            studentObj = Student.objects.get(id=student_id)
            if studentObj:
                studentName = studentObj.name
        statename = ''
        for state in statenames:
            statename += str(state) + ","
        center = ''
        for cntr in centernames:
            center += cntr + ","
        save_user_activity(request,
                           'Searched:My Students - Students Dashboard - Report Card:' + string.replace(statename, "%20",
                                                                                                       " ") + ' ' + str(
                               center) + ' ' + str(studentName) + ',' + str(studentGrade) + ',' + str(assessmentYears),
                           'Action')
    else:
        save_user_activity(request, 'Viewed Page:My Students - Students Dashboard - Report Card', 'Page Visit')
    return render_response(request, 'report_generation/reportCard.html',
                           {'states': states, 'studentNames': studentnames, 'student': student, 'photo': photo,
                            'student_attendance': stuendent_attendance_subject_wise, 'delivery_partner':delivery_partner,'funding_partner':funding_partner, 'diag_details': diag_details,
                            'scholastic_details': scholastic_details, 'coschol_details': coschol_details,
                            'statenames': statenames, 'centernames': simplejson.dumps(centernames), 'grades': grades,
                            'assessmentYears': assessmentYears, 'student_id': student_id, 'student_grade': studentGrade,
                            'comments': comments, 'student_ay': simplejson.dumps(student_ay),
                            'endDateForStudent': endYear, 'startDateForStudent': startYear,
                            'grade_progressreport': grade_progressreport, 'from_progress_report': from_progress_report,
                            'flag': flag1, 'ayfy': ayfy, 'stickers':sticker_list})



@csrf_exempt
def get_Courses(request):
    if request.is_ajax():
        statenames = request.GET.get('state', '')
        print "statenames",statenames
        partner_id = (request.GET.get("partner", ''))
        fund_partner=(request.GET.get("funding_partner_id", ""))
        # print "partner_partner_id_id",funding_partner,partner_id
        
        state_list = []
        center_list = []
        statesList = []
        if statenames != '':
            statesList = statenames.split(",")
        myState = ''
        i = 0
        if len(statesList) > 0:
            for statess in statesList:
                myState += "'" + statess + "'"
                i = i + 1
                if i < len(statesList):
                    myState += ","
        state_list.append(statenames.split(","))
        db = evd_getDB()
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query = "SELECT year(ayfy.start_date) as year,ayfy.title,ayfy.board,ayfy.id FROM web_center wc,web_offering wo," \
                "web_ayfy ayfy where wc.id=wo.center_id and wo.academic_year_id=ayfy.id"
        if statenames != '' and len(statenames) > 0 and statesList[0] != 'All':
            query += " and wc.state in (" + myState + ") and ayfy.board in (select board from web_center where state in (" + myState + "))" 
        else:
            try:
                partner = Partner.objects.get(contactperson=request.user)
            except:
                 partner = None   
            if partner:
                for ptype in partner.partnertype.all():
                    statename_list =[]
                    if ptype.id == 1:
                        statename_list = Center.objects.filter(partner_school__partner_id = partner.id,status="Active").values_list("state",flat=True)
                    elif ptype.id == 2:
                        statename_list = Center.objects.filter(partner_school__partner_id = partner.id,delivery_partner_id=partner.id,status="Active").values_list("state",flat=True)
                        
                    elif ptype.id == 3:
                        statename_list = Center.objects.filter(partner_school__partner_id = partner.id,funding_partner_id=partner.id,status="Active").values_list("state",flat=True)
                    elif ptype.id == 4:
                        statename_list = Center.objects.filter(orgunit_partner_id = partner.id,status="Active").values_list("state",flat=True)
                    statename_list=list(set(statename_list))
                    myState = ''
                    i = 0 
                    for statess in statename_list:
                        if statess is not None :
                            myState += "'" + statess + "'" 
                            i = i + 1
                            if i < len(statesList):
                                myState += ","
                query += " and wc.state in (" + myState + ") and ayfy.board in (select board from web_center where state in (" + myState + "))" 
        query += " group by ayfy.id"
        dict_cur.execute(query)
        listdata = dict_cur.fetchall()

        tot_user_cur.close()
        dict_cur.close()

        try:
            ref = ReferenceChannel.objects.get(id=request.user.userprofile.referencechannel.id)
        except:
            ref = None
        without_partner = False

        for state_name in state_list:
            if state_name != '' and state_name != "null" and state_name != "undefined":
                for state in state_name:
                    if state == "All":
                        if request.user.is_superuser or ref is None:
                            without_partner = True

                        elif has_role(request.user.userprofile, "Delivery co-ordinator"):
                            centers=Center.objects.filter(delivery_coordinator=request.user,status='Active')

                        elif has_role(request.user.userprofile, "OUAdmin"):
                            centers=Center.objects.filter(orgunit_partner__contactperson=request.user,status='Active')
                        elif has_role(request.user.userprofile, "Partner Account Manager") or has_pref_role(request.user.userprofile, "Partner Account Manager"):
                            db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)
                            tot_user_cur = db.cursor()
                            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
                            query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                            dict_cur.execute(query)
                            partner_id = [str(each['value']) for each in dict_cur.fetchall()]
                            partner_id.sort()
                            centers = Center.objects.filter(( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id)),status='Active')
                            db.close()
                            dict_cur.close()
                        elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
                            partner = None
                            if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
                                try:
                                    partner = Partner.objects.get(contactperson=request.user)
                                except:
                                    partner= None
                            else:
                                partner = ref.partner
                            if partner and len(partner.partnertype.filter(name='Delivery Partner')) > 0 and len(partner.partnertype.filter(name='Organization Unit')) > 0:
                                centers = Center.objects.filter(Q(partner_school__partner=partner) | Q(orgunit_partner=partner),status='Active')
                            elif partner and len(partner.partnertype.filter(name='Delivery Partner')) > 0:
                                centers = Center.objects.filter(partner_school__partner=partner,status='Active')
                            elif partner and len(partner.partnertype.filter(name='Organization Unit')) > 0:
                                centers = Center.objects.filter(orgunit_partner=partner,status='Active')
                            else:
                                without_partner = True
                        if without_partner:
                            centers = Center.objects.all()
                            centers= centers.filter(status='Active')
                    else:
                        if request.user.is_superuser or ref is None:
                            without_partner = True
                        elif has_role(request.user.userprofile, "Partner Account Manager") or has_pref_role(request.user.userprofile, "Partner Account Manager"):
                            db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)
                            tot_user_cur = db.cursor()
                            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
                            query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                            dict_cur.execute(query)
                            partner_id = [str(each['value']) for each in dict_cur.fetchall()]
                            partner_id.sort()
                            centers  =Center.objects.filter(state=state).filter(( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id)),status='Active')
                            db.close()
                            dict_cur.close() 
                        elif has_role(request.user.userprofile, "Delivery co-ordinator"):
                            centers=Center.objects.filter(state=state).filter(delivery_coordinator=request.user,status='Active')

                        elif has_role(request.user.userprofile, "OUAdmin"):
                            centers=Center.objects.filter(state=state).filter(orgunit_partner__contactperson=request.user,status='Active')

                        elif len(request.user.userprofile.role.filter(name="Partner Admin")) > 0 or ref:
                            partner = None
                            if len(request.user.userprofile.role.filter(name="Partner Admin")) > 0:
                                partner = Partner.objects.get(contactperson=request.user)
                            else:
                                partner = ref.partner
                            if partner and len(partner.partnertype.filter(name='Delivery Partner')) > 0 and len(partner.partnertype.filter(name='Organization Unit')) > 0:
                                centers = Center.objects.filter(state=state).filter(Q(partner_school__partner=partner) | Q(orgunit_partner=partner),status='Active')
                            elif partner and len(partner.partnertype.filter(name='Delivery Partner')) > 0:
                                centers = Center.objects.filter(state=state, partner_school__partner=partner,status='Active')
                            elif partner and len(partner.partnertype.filter(name='Organization Unit')) > 0:
                                centers = Center.objects.filter(state=state, orgunit_partner=partner,status='Active')
                            else:
                                without_partner = True
                        if without_partner:
                            centers = Center.objects.filter(state=state,status='Active')
                    if centers:
                        if partner_id !=str('-1') and partner_id !='All' and partner_id !='' :
                            centers = centers.filter(delivery_partner_id__in = partner_id.split(','))
                        if fund_partner != str('-1') and fund_partner !='All'and fund_partner !='':
                            centers = centers.filter(funding_partner_id__in=fund_partner.split(','))
                        for center in centers:
                            delivery_partner_id=''
                            delivery_partner=''
                            funding_partner = ''
                            funding_partner_id=''
                            if center.funding_partner is not None or center.funding_partner=='':
                                funding_partner = center.funding_partner.name_of_organization
                                funding_partner_id = center.funding_partner.id
                            if center.delivery_partner is not None or center.delivery_partner=='' :
                                delivery_partner = center.delivery_partner.name_of_organization
                                delivery_partner_id = center.delivery_partner.id

                            if state == "All":
                                center_name = {'state': '', 'label': center.name, 'value': center.name,'funding_partner':funding_partner,'funding_partner_id':funding_partner_id,'delivery_partner':delivery_partner,"delivery_partner_id":delivery_partner_id}
                            else:
                                center_name = {'state': state, 'label': center.name, 'value': center.name,'funding_partner':funding_partner,'funding_partner_id':funding_partner_id,'delivery_partner':delivery_partner,'delivery_partner_id':delivery_partner_id}
                            center_list.append(center_name)
            data = {'center_list': center_list, 'listdata': listdata}
            return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    else:
        return HttpResponse('No Centers Available')

@csrf_exempt
def get_Students_for_report_card(request):
    if request.is_ajax():
        centerIds = request.GET.get('center_id', '')
        states = request.GET.get('states', '')
        if states == '' or None:
            states = 'All'
        student_list = []
        center_list = centerIds.split(",")
        state_list = states.split(",")
        presize_state_list = []
        if state_list:
            for state in state_list:
                presize_state_list.append(str(state))
        all_students = []
        print "center_list ", center_list
        print "presize_state_list ", presize_state_list
        if presize_state_list and center_list:
            if 'All' in presize_state_list and 'All' in center_list:
                students = Student.objects.order_by('name').values('id', 'name', 'school_rollno').filter(
                    Q(status='Active') | Q(status='Alumni'))
                all_students.append(students)
            elif 'All' not in presize_state_list and 'All' in center_list:
                center_ids = Center.objects.values('id').filter(state__in=presize_state_list)
                print "center_ids in elif", center_ids
                if center_ids:
                    students = Student.objects.order_by('name').values('id', 'name', 'school_rollno').filter(
                            center_id__in = center_ids)
                    all_students.append(students)
            else:
                if center_list:
                    centerId = Center.objects.values('id').filter(name__in = center_list)
                    print "centerId ", centerId
                    students = Student.objects.order_by('name').values('id', 'name', 'school_rollno').filter(
                        center_id__in = centerId)
                    all_students.append(students)
            if all_students and len(all_students) > 0 and len(all_students[0]) > 0:
                for student in all_students[0]:
                    name = student['name']
                    rollno = student['school_rollno']
                    if rollno != None and rollno != '':
                        name += '-'
                        name += rollno
                    student_data = {'label': name, 'value': student['id']}
                    student_list.append(student_data)

        return HttpResponse(simplejson.dumps(student_list), mimetype='application/json')

    else:
        return HttpResponse('No Student Available')


@csrf_exempt
def getgradeforReortCard(request):
    if request.is_ajax():
        grade_list = []
        studentId = request.GET.get('student_id', '')
        db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                             user=settings.DATABASES['default']['USER'],
                             passwd=settings.DATABASES['default']['PASSWORD'],
                             db=settings.DATABASES['default']['NAME'],
                             charset="utf8",
                             use_unicode=True)
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query = "select DISTINCT wc.grade from web_offering_enrolled_students woes,web_offering wo,web_course wc where woes.offering_id=wo.id and wo.course_id=wc.id and woes.student_id='" + str(
            studentId) + "' order by wc.grade"
        dict_cur.execute(query)
        studentGrades = dict_cur.fetchall();
        if studentGrades:
            for studentGrade in studentGrades:
                grade_data = {'label': studentGrade['grade'], 'value': studentGrade['grade']}
                grade_list.append(grade_data)
        return HttpResponse(simplejson.dumps(grade_list), mimetype='application/json')
    else:
        return HttpResponse('No Student Available')


@login_required
def get_award_nominees(request):
    offer_id = request.POST.get('offer_id', '')
    stud_id = request.POST.get('stud_id', '')
    data = {}
    awards = list(Award.objects.values('name', 'description'))
    stud_nominations = AwardDetail.objects.filter(student_id=stud_id, offering_id=offer_id)
    stud_nominations_by_teacher = AwardDetail.objects.filter(student_id=stud_id, offering_id=offer_id,
                                                             teacher_id=request.user.id)
    data['selected_list'] = [nomination.award.name for nomination in stud_nominations_by_teacher]
    data['stud_nominations'] = []
    for nomination in stud_nominations:
        data['stud_nominations'].append({'award': nomination.award.name,
                                         'teacher': nomination.teacher.first_name + nomination.teacher.last_name,
                                         'description': nomination.award.description
                                         })
    data['award_list'] = awards

    return HttpResponse(json.dumps({'data': data}), content_type='application/json')


@login_required
def save_nomination(request):
    type_ = request.GET.get("type") or "nomination"
    if type_ == "nomination":
        student_id = request.GET.get("student_id")
        offer_id = request.GET.get("offer_id")
        selected_list = request.GET.getlist("selected_list[]")

        AwardDetail.objects.filter(student_id=student_id, offering_id=offer_id, teacher_id=request.user.id).exclude(
            award__name__in=selected_list).delete()
        for award in selected_list:
            award_obj = Award.objects.get(name=award)
            nomination, created = AwardDetail.objects.get_or_create(student_id=student_id, offering_id=offer_id,
                                                                    teacher_id=request.user.id, award=award_obj)

            nomination.modified_by = request.user
            nomination.status = 'Nominated'
    else:
        approve_list = json.loads(request.GET.get("approve_list"))
        for item in approve_list:
            nomination = AwardDetail.objects.get(student_id=item['stud_id'], offering_id=item['offer_id'],
                                                 teacher_id=item['teacher_id'], award=item['award_id'])
            nomination.status = "Approved"
            nomination.modified_by = request.user
            nomination.save()

    return HttpResponse("Success")


@login_required
def review_awards(request):
    center_id = request.GET.get("center_id")
    stud_nominations = AwardDetail.objects.filter(offering__center_id=center_id)
    data = {'stud_nominations': stud_nominations}

    return render_response(request, 'review_awards.html', data)


@csrf_exempt
def get_location_data(request):
    url = request.GET['url']
    data = requests.get(url).text

    return HttpResponse(data)


def update_user_Role_or_status(request):
    role_name = request.GET.get('role')
    user_id = request.GET.get('id')
    status_flag = request.GET.get('status')
    message = ""
    status = ""
    if user_id and user_id is not None:
        if status_flag and status_flag is not None:
            user_result = User.objects.filter(id=user_id).update(is_active=0)
            if user_result == 1:
                message = 'Status updated successfully'
                status = "success"
            else:
                message = 'Error'
                status = "error"
        elif role_name and role_name is not None:
            user = User.objects.get(pk=user_id)
            if user and user.is_active == 1:
                userp = user.userprofile
                role = Role.objects.get(name=role_name)
                userp.role.clear()
                userp.role.add(role)
                userp.pref_roles.clear()
                userp.pref_roles.add(role)
                user.save()
                userp.save()
                message = 'Role Updated Successfully'
                status = "success"
            else:
                message = 'User does not exist or InActive'
                status = "error"
        else:
            message = 'Data is missing'
            status = "error"
    else:
        message = 'UserId can not be null'
        status = "error"
    userMessage = {'message': message, 'status': status, 'role': role_name}
    return HttpResponse(simplejson.dumps(userMessage), mimetype='application/json')


@login_required
def userActivity(request):
    if request.user.is_authenticated:
        activityType = ActivityType.objects.all()
        userId = request.GET.get('user_id')
        if userId:
            start_date = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)).date()
            end_date = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30) + datetime.timedelta(
                days=1)).date()
            user = User.objects.get(pk=userId)
            userDetails = UserProfile.objects.get(user=user)
            openActivity = Task.objects.filter(Q(taskStatus='Open') | Q(taskStatus='WIP'), performedOn_userId=userId)
            history = Task.objects.filter(performedOn_userId=userId).exclude(Q(taskStatus='Open') | Q(taskStatus='WIP'))
            pref_roles = [role.name for role in user.userprofile.pref_roles.all()]
            activity_activity_name = UserActivityHistory.objects.values('activity_name').filter(
                user_id=userId).distinct()
            last_logged_in = UserActivityHistory.objects.values('activity_date_time').filter(activity_name='Logged In',
                                                                                             user_id=userId).order_by(
                '-activity_date_time')
            last_logged_out = UserActivityHistory.objects.values('activity_date_time').filter(
                activity_name='Logged Out', user_id=userId).order_by('-activity_date_time')
            lastLoginDateTime = None
            if last_logged_in and len(last_logged_in) > 0:
                lastLoginDateTime = last_logged_in[0]
            lastLoggedoutDateTime = None
            if last_logged_out and len(last_logged_out) > 0:
                lastLoggedoutDateTime = last_logged_out[0]
            return render_response(request, 'userActivityHistory.html',
                                   {'user': user, 'pref_roles': pref_roles, 'start_date': start_date,
                                    'end_date': end_date, 'activityType': activityType, 'userDetails': userDetails,
                                    'openActivity': openActivity, 'history': history,
                                    'activity_activity_name': activity_activity_name,
                                    'last_logged_in': lastLoginDateTime, 'last_logged_out': lastLoggedoutDateTime})
        else:
            start_date = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30) + datetime.timedelta(
                days=-2)).date()
            end_date = (datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)).date()
            return render_response(request, 'user_activity.html',
                                   {'activityType': activityType, 'start_date': start_date, 'end_date': end_date})
    else:
        return redirect("/?show_popup=true&type=login")


@login_required
def my_setting(request):
    message = request.GET.get('message', '')
    taskSetting = Setting.objects.values('name', 'duration')
    settings = []
    for taskSetting in taskSetting:
        setting = {taskSetting['name']: taskSetting['duration']}
        settings.append(setting)
    settingJson = simplejson.dumps(settings)
    return render_response(request, 'mySetting.html', {'settingJson': settingJson, 'message': message})


def saveSettings(request):
    if request.method == 'POST':
        name = request.POST.getlist('taskName')
        duration = request.POST.getlist('taskDuration')
        if name and duration:
            message = "Setting Duration Updated Successfully"
            for dataName, dataDuration in zip(name, duration):
                if dataName == "Profile Completion":
                    Setting.objects.filter(name=dataName).update(duration=dataDuration)
                elif dataName == "Self Evaluation":
                    Setting.objects.filter(name=dataName).update(duration=dataDuration)
                else:
                    Setting.objects.filter(name=dataName).update(duration=dataDuration)
            return redirect("/setting/?message=" + message)


@csrf_exempt
def getyearfor_student(request):
    if request.is_ajax():
        selectedYear = request.GET.get('selectedYear', '')
        statenames = request.GET.get('state', '')
        statesList = []
        if statenames != '':
            statesList = statenames.split(",")
        myState = ''
        i = 0
        if len(statesList) > 0:
            for states in statesList:
                myState += "'" + states + "'"
                i = i + 1
                if i < len(statesList):
                    myState += ","
                    # studentId = request.GET.get('student_id', '')
        try:
            db = evd_getDB()
            tot_user_cur = db.cursor()
            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query = "SELECT year(ayfy.start_date) as year,ayfy.title,ayfy.board,ayfy.id FROM web_center wc,web_offering wo," \
                    "web_ayfy ayfy where wc.id=wo.center_id and wo.academic_year_id=ayfy.id"
            if statenames != '' and len(statenames) > 0 and statesList[0] != 'All':
                query += " and wc.state in (" + myState + ") and ayfy.board in (select board from web_center where state in (" + myState + "))"
            query += " group by ayfy.id"
            dict_cur.execute(query)
            listdata = dict_cur.fetchall()

        except Exception as e:
            return HttpResponse(e.message)
        data = {'ayfyData': listdata, 'selectedYear': selectedYear}
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    else:
        return HttpResponse('No Year Available')


@csrf_exempt
def save_user_activity(request, activity_name, activity_type):
    if request.user.is_authenticated:
        if activity_type:
            activityType_id = ActivityType.objects.values('id').filter(activity_type=activity_type)
            if len(activityType_id) > 0:
                id_activity = activityType_id[0]['id']
                cur_date = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
                username = request.user.username
                try:
                    activity = UserActivityHistory(created_date=cur_date, user_id=request.user.id,
                                                   activity_date_time=cur_date, activity_name=activity_name,
                                                   activity_type=activity_type, activity_type_id=id_activity,
                                                   username=username,
                                                   name=request.user.first_name + " " + request.user.last_name)
                    activity.save()
                except  Exception as e:
                    print e.message


def system_generated_task(request):
    task_name = request.GET.get('task_name', '')
    db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                         user=settings.DATABASES['default']['USER'],
                         passwd=settings.DATABASES['default']['PASSWORD'],
                         db=settings.DATABASES['default']['NAME'],
                         charset="utf8",
                         use_unicode=True)
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)

    if task_name == "Profile Completion":
        query = "select  au.id,au.first_name,au.last_name,au.username,au.date_joined from auth_user au,web_userprofile wup where au.id=wup.user_id and wup.profile_completion_status=False and au.is_active=True"
        dict_cur.execute(query)
        datas = dict_cur.fetchall();
        days = Setting.objects.values('duration').filter(name=task_name)
        for day in days:
            duration = day['duration']
    elif task_name == "Self Evaluation":
        query = "select au.id,au.first_name,au.last_name,au.username,au.date_joined from auth_user au,web_userprofile wup where au.id=wup.user_id and wup.profile_completion_status=True and wup.self_eval=False and au.is_active=True"
        dict_cur.execute(query)
        datas = dict_cur.fetchall();
        days = Setting.objects.values('name', 'duration').filter(name=task_name)
        for day in days:
            duration = day['duration']
    else:
        query = "select au.id,au.first_name,au.last_name,au.username,au.date_joined from auth_user au,web_userprofile wup where au.id=wup.user_id and wup.profile_completion_status=True and wup.self_eval=True and au.is_active=True and dicussion_outcome='Not Scheduled'"
        dict_cur.execute(query)
        datas = dict_cur.fetchall();
        days = Setting.objects.values('name', 'duration').filter(name=task_name)
        for day in days:
            duration = day['duration']
    today = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
    duedate = today.date()
    count = 0
    query = "select au.username,au.id,wup.user_id,wr.id,wr.name from web_userprofile_role wupr, web_userprofile wup, web_role wr, auth_user au where wupr.userprofile_id = wup.id and wr.id = wupr.role_id and wr.name = 'vol_admin' and wup.user_id = au.id  order by wup.id "
    dict_cur.execute(query)
    totalListOfUser = dict_cur.fetchall();
    db.close()
    dict_cur.close()
    assignee_length = len(totalListOfUser)
    if datas:
        count = 0
        for data in datas:
            if totalListOfUser:
                if data['date_joined'] + timedelta(days=int(duration)) < datetime.datetime.now():
                    assignee = totalListOfUser[count]
                    name_assingee = assignee['username']
                    first_name = data['first_name']
                    last_name = data['last_name']
                    user_id = str(data['id'])
                    if task_name == "Profile Completion":
                        taskName = "Profile complete reminder call/message for"
                        taskName += ' ' + first_name + ' ' + last_name
                    elif task_name == "Self Evaluation":
                        taskName = "SE completion reminder c a l l / m e s s a g e for"
                        taskName += ' ' + first_name + ' ' + last_name
                    else:
                        taskName = " TSD booking remainder email / phone for"
                        taskName += ' ' + first_name + ' ' + last_name
                    comment = 'need to call' + ' ' + first_name + ' ' + last_name
                    if first_name:
                        first_name += ','
                        first_name += last_name
                        first_name += '-'
                        first_name += user_id
                    else:
                        first_name = ' '
                        first_name = data['username']
                performedOn_name = first_name

                systemTaskid = SystemTaskHistory.objects.values('user_id').filter(
                    Q(user_id=data['id']) & Q(type=task_name))
                id = ''
                if systemTaskid and len(systemTaskid) > 0:
                    id = systemTaskid[0]
                if id is None or id == '':
                    task = Task(comment=comment, subject=taskName, assignedTo=name_assingee, dueDate=duedate,
                                priority="high", taskCreatedBy_userId=data['id'], taskStatus="open",
                                performedOn_userId=data['id'], taskCreatedDate=duedate,
                                user_date_joined=data['date_joined'], performedOn_name=performedOn_name,
                                taskType='SYSTEM')
                    task.save()
                    sysTask = SystemTaskHistory(user_id=data['id'], task_id=task.id, type=task_name)
                    sysTask.save();
                flag = 0
                if assignee_length - 1 == count:
                    flag = 1
                if flag == 0:
                    count += 1
                else:
                    count = 0
        return redirect('/setting/')


def update_assignee(request):
    if request.is_ajax():
        task_id = request.GET.get('id')
        assignee_id = request.GET.get('assigneeId')
        data_list = request.GET.get('data', '')
        today = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
        cur_date = today.date()
        message = ""
        status = ""
        if data_list and data_list is not None:
            jdata = json.loads(data_list)
            if jdata and jdata is not None:
                for d in jdata:
                    assignee_id = d['assignee']
                    taskId = d['id']
                    filterUser = User.objects.get(id=assignee_id)
                    assigneeName = filterUser.username
                    task_result = Task.objects.filter(id=taskId).update(assignedTo=assigneeName,
                                                                        performedOn_userId=filterUser.id,
                                                                        taskUpdatedDate=cur_date,
                                                                        taskUpdatedBy_userId=request.user.username)
                message = 'All Task updated successfully'
                status = 'success'
            if message and message is None:
                message = 'Task or Assigne does not exist.'
                status = 'error'
            userMessage = {'message': message, 'status': status}
            return HttpResponse(simplejson.dumps(userMessage), mimetype='application/json')

        if task_id and task_id is not None and assignee_id and assignee_id is not None:
            task = Task.objects.filter(id=task_id)
            filterUser = User.objects.get(id=assignee_id)
            assigneeName = filterUser.username
            task_result = Task.objects.filter(id=task_id).update(assignedTo=assigneeName,
                                                                 performedOn_userId=filterUser.id,
                                                                 taskUpdatedDate=cur_date,
                                                                 taskUpdatedBy_userId=request.user.username)
            if task_result == 1:
                message = task[0].subject + " Updated"
                status = "success"
            else:
                message = "Task does not Updated"
                status = "error"
        userMessage = {'message': message, 'status': status}
    return HttpResponse(simplejson.dumps(userMessage), mimetype='application/json')


@login_required
def my_certificate(request):
    user_profile = request.user.userprofile
    is_teacher = False
    is_centeradmin = False
    is_contentdev = False
    if has_role(user_profile, "Center Admin") and (
            has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher")):
        is_centeradmin = True
        is_teacher = True
    elif has_role(user_profile, "Center Admin") or has_pref_role(user_profile, "Center Admin"):
        is_centeradmin = True
    if has_pref_role(user_profile, "Teacher") or has_role(user_profile, "Teacher"):
        is_teacher = True
    if has_pref_role(user_profile, "Content Developer") or has_role(user_profile, "Content Developer"):
        is_contentdev = True

    save_user_activity(request, 'Viewed Page: My Contributions - My Certificate', 'Page Visit')

    return render_response(request, 'teacher_certificate.html',
                           {'is_teacher': is_teacher, 'is_centeradmin': is_centeradmin, 'is_contentdev': is_contentdev})


@login_required
def get_certificate(request):
    role = request.GET.get('role')
    from django.core.servers.basehttp import FileWrapper
    path = 'static/uploads/certificates/2017/' + role + '/' + str(request.user.id) + '.pdf'
    if not os.path.isfile(path):
        path = 'static/uploads/certificates/nofile.pdf'
    certificate = open(path, "r")
    response = HttpResponse(FileWrapper(certificate), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + role + '_certificate.pdf'
    return response


@csrf_exempt
def userActivityHistoryFilter(request):
    if request.is_ajax():
        searchItm = request.GET.get('searchItem')
        activityType = request.GET.get('type')
        startDate = request.GET.get('start_date')
        startDate = datetime.datetime.strptime(startDate, "%d-%m-%Y").date()
        endDate = request.GET.get('end_date')
        endDate = datetime.datetime.strptime(endDate, "%d-%m-%Y").date()
        alphabatesActivityName = request.GET.get('alphabatesActivityName')
        activityName = request.GET.get('activityName')
        user_id = request.GET.get('user_id')
        logon_tab = request.GET.get('tab', '')
        page = request.GET.get('page', 1)
        db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                             user=settings.DATABASES['default']['USER'],
                             passwd=settings.DATABASES['default']['PASSWORD'],
                             db=settings.DATABASES['default']['NAME'],
                             charset="utf8",
                             use_unicode=True)
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        listActivity = []
        allActivityList = []
        flag = False
        number = False
        message = ''
        query = "select * from web_useractivityhistory "
        if (searchItm and searchItm is not None) or (activityType is not None) or (startDate is not None) or (
                endDate is not None) or (alphabatesActivityName is not None) or activityName is not None:
            query += " where "
        if searchItm and searchItm is not None:
            query += " name like '" + str(searchItm) + "%'"
            flag = True
        if alphabatesActivityName and alphabatesActivityName is not None:
            query += " activity_name like '" + str(alphabatesActivityName) + "%'"
            flag = True
        if activityType is not None and activityType != 'All':
            if flag:
                query += " and "
            query += " activity_type like '" + str(activityType) + "%'"
            flag = True
        if startDate is not None and endDate is not None:
            if flag:
                query += " and "
            query += " activity_date_time >='" + str(startDate) + " 00:00:00' and activity_date_time <= '" + str(
                endDate) + " 23:59:59'"
            flag = True
        if activityName is not None:
            if flag:
                query += " and "
            query += " activity_name like '" + str(activityName) + "%'"
            flag = True
        elif logon_tab:
            if flag:
                query += " and "
            query += " activity_name in('Logged Out','Logged In')"
            flag = True
        if user_id is not None:
            if flag:
                query += " and "
            query += " user_id =" + user_id
        query += " order by activity_date_time desc "
        dict_cur.execute(query)
        listActivity = dict_cur.fetchall();
        db.close()
        dict_cur.close()
        allActivity = listActivity;
        if len(allActivity) > 0:
            for activity in allActivity:
                user_name = activity['name']
                useractivity_date_time = str(activity['activity_date_time'])
                useractivity_name = activity['activity_name']
                useractivity_last_login = str(activity['last_login'])
                data = {'user_id': activity['user_id'], 'name': user_name, 'activity_date_time': useractivity_date_time,
                        'activity_name': useractivity_name, 'last_login': useractivity_last_login}
                allActivityList.append(data)
        else:
            message = 'No activity found.'
        activity_history = []
        paginator = Paginator(listActivity, 50)
        try:
            listActivity = paginator.page(page)
        except PageNotAnInteger:
            listActivity = paginator.page(1)
        except EmptyPage:
            listActivity = paginator.page(paginator.num_pages)
        for activity in listActivity:
            user_name = activity['name']
            useractivity_date_time = str(activity['activity_date_time'])
            useractivity_name = activity['activity_name']
            useractivity_last_login = str(activity['last_login'])
            data = {'user_id': activity['user_id'], 'name': user_name, 'activity_date_time': useractivity_date_time,
                    'activity_name': useractivity_name, 'last_login': useractivity_last_login}
            activity_history.append(data)
        return HttpResponse(simplejson.dumps(
            {"activity_history": activity_history, 'prev': listActivity.previous_page_number(),
             'next': listActivity.next_page_number(), 'current': listActivity.number,
             'total': listActivity.paginator.num_pages, 'count': len(allActivity), 'allActivity': allActivityList,
             'errorMsg': message}), mimetype='application/json')
    else:
        return HttpResponse("Invalid Action")


@csrf_exempt
def getActivityNameByActivityType(request):
    if request.is_ajax():
        activityType = request.GET.get('activityType')
        user_list = []
        UniqueUserId = UserActivityHistory.objects.values('user_id').all().distinct()
        for UniqueId in UniqueUserId: user_list.append(UniqueId['user_id'])
        userIds = User.objects.values('id').filter(id__in=user_list)
        userId = request.GET.get('user_id')
        if activityType != 'All':
            if userId:
                activityName = UserActivityHistory.objects.values('activity_name').filter(activity_type=activityType,
                                                                                          user_id=userId).distinct()
            else:
                activityName = UserActivityHistory.objects.values('activity_name').filter(activity_type=activityType,
                                                                                          user_id__in=userIds).distinct()
        else:
            if userId:
                activityName = UserActivityHistory.objects.values('activity_name').filter(user_id=userId).distinct()
            else:
                activityName = UserActivityHistory.objects.values('activity_name').filter(
                    user_id__in=userIds).distinct()
        activity_history = []
        for activity in activityName:
            name = activity['activity_name']
            data = {'activity_name': name}
            activity_history.append(data)
        return HttpResponse(simplejson.dumps(activity_history), mimetype='application/json')
    else:
        return HttpResponse("data not found")


def userActivityFilter(request):
    if request.is_ajax():
        alphabateSearch = request.GET.get('searchItem')
        searchName = request.GET.get('searchName')
        activityType = request.GET.get('type')
        startDate = request.GET.get('start_date')
        startDate = datetime.datetime.strptime(startDate, "%d-%m-%Y").date()
        endDate = request.GET.get('end_date')
        endDate = datetime.datetime.strptime(endDate, "%d-%m-%Y").date()
        alphabatesActivityName = request.GET.get('alphabatesActivityName')
        activityName = request.GET.get('activityName')
        page = request.GET.get('page', '')
        message = ''
        db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                             user=settings.DATABASES['default']['USER'],
                             passwd=settings.DATABASES['default']['PASSWORD'],
                             db=settings.DATABASES['default']['NAME'],
                             charset="utf8",
                             use_unicode=True)
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        user_list = []
        activity_history = []
        user_activity_pagination = []
        user_activity_without_pagination = []
        user_activity_allData = []
        flag = False
        listActivity = []
        activity_date_time_list = []
        query = "select max(activity_date_time) as activity_date_time from web_useractivityhistory "
        query = apply_filter_useractivity(query, alphabateSearch, alphabatesActivityName, activityType, searchName,
                                          activityName, startDate, endDate, flag, True)
        dict_cur.execute(query)
        list_Activity_date_time = dict_cur.fetchall();
        if len(list_Activity_date_time) > 0:
            for date_time in list_Activity_date_time:
                activity_date_time_list.append(str(date_time['activity_date_time']))
        if len(activity_date_time_list) > 0:
            activity_date_time_str = str(activity_date_time_list)
            activity_date_time_str = activity_date_time_str.replace('[', '')
            activity_date_time_str = activity_date_time_str.replace(']', '')
            query = "select * from web_useractivityhistory where activity_date_time in (" + activity_date_time_str + ") "
            flag = True
            query = apply_filter_useractivity(query, alphabateSearch, alphabatesActivityName, activityType, searchName,
                                              activityName, startDate, endDate, flag, False)
            dict_cur.execute(query)
            listActivity = dict_cur.fetchall();
        if len(listActivity) > 0:
            for activity in listActivity:
                user_activity_pagination.append(activity)
                user_activity_without_pagination.append(activity)
        if len(user_activity_without_pagination) > 0:
            for activities in user_activity_without_pagination:
                id = activities['user_id']
                try:
                    usrObj = User.objects.get(pk=id)
                    user_name = usrObj.username
                except:
                    user_name = None
                if user_name is not None:
                    useractivity_date_time = str(activities['activity_date_time'])
                    useractivity_name = activities['activity_name']
                    useractivity_last_login = str(activities['last_login'])
                    data = {'user_id': activities['user_id'], 'name': user_name,
                            'activity_date_time': useractivity_date_time, 'activity_name': useractivity_name,
                            'last_login': useractivity_last_login}
                    user_activity_allData.append(data)
        else:
            message = 'No activity found.'
        dict_cur.close()
        db.close()
        paginator = Paginator(user_activity_pagination, 50)
        try:
            user_activity_pagination = paginator.page(page)
        except PageNotAnInteger:
            user_activity_pagination = paginator.page(1)
        except EmptyPage:
            user_activity_pagination = paginator.page(paginator.num_pages)
        if len(user_activity_pagination) > 0:
            for activity in user_activity_pagination:
                id = activity['user_id']
                try:
                    usrObj = User.objects.get(pk=id)
                    user_name = usrObj.username
                except:
                    user_name = None
                if user_name is not None:
                    useractivity_date_time = str(activity['activity_date_time'])
                    useractivity_name = activity['activity_name']
                    useractivity_last_login = str(activity['last_login'])
                    data = {'user_id': activity['user_id'], 'name': user_name,
                            'activity_date_time': useractivity_date_time, 'activity_name': useractivity_name,
                            'last_login': useractivity_last_login}
                    activity_history.append(data)
        json = simplejson.dumps({'user_activity_allData': user_activity_allData, 'activity_history': activity_history,
                                 'alphabateSearch': alphabateSearch,
                                 'prev': user_activity_pagination.previous_page_number(),
                                 'next': user_activity_pagination.next_page_number(),
                                 'current': user_activity_pagination.number,
                                 'total': user_activity_pagination.paginator.num_pages,
                                 'count': len(user_activity_without_pagination), 'errorMsg': message})
        return HttpResponse(json, mimetype='application/json')
    else:
        return HttpResponse("Invalid Action")


def apply_filter_useractivity(query, alphabateSearch, alphabatesActivityName, activityType, searchName, activityName,
                              startDate, endDate, flag, is_last):
    if (alphabateSearch and alphabateSearch is not None) or (activityType is not None) or (searchName is not None) or (
            alphabatesActivityName is not None) or activityName is not None or (
            startDate is not None and endDate is not None):
        if is_last:
            query += " where "
    if alphabateSearch and alphabateSearch is not None:
        if flag:
            query += " and "
        query += " name like '" + str(alphabateSearch) + "%'"
        flag = True
    if alphabatesActivityName and alphabatesActivityName is not None:
        query += " activity_name like '" + str(alphabatesActivityName) + "%'"
        flag = True
    if activityType is not None and activityType != 'All':
        if flag:
            query += " and "
        query += " activity_type like '" + str(activityType) + "%'"
        flag = True
    if searchName is not None:
        if flag:
            query += " and "
        try:
            int(searchName)
            query += " user_id ='" + str(searchName) + "'"
        except ValueError:
            query += " name like '%" + str(searchName) + "%'"
        flag = True
    if activityName is not None:
        if flag:
            query += " and "
        query += " activity_name like '" + str(activityName) + "%'"
        flag = True
    if startDate is not None and endDate is not None:
        if flag:
            query += " and "
        query += " activity_date_time >='" + str(startDate) + " 00:00:00' and activity_date_time <= '" + str(
            endDate) + " 23:59:59'"
        flag = True
    if is_last:
        query += " group by user_id "
    else:
        query += " order by activity_date_time desc"
    return query


def get_grade(request):
    if request.is_ajax():
        grades = request.GET.get('grade', '');
        statenames = request.GET.get('stateName', '')
        centernames = request.GET.get('centerName', '')
        start_date = request.GET.get('startDate', '')
        end_date = request.GET.get('endDate', '')
        flag = request.GET.get('flag', '')
        category = request.GET.get('categoryId', '')
        diag_category = request.GET.get('diagCategory', '')
        category_list = []
        diag_category_list = []
        if statenames == '' or None:
            statenames = 'All'
        if diag_category == '' or None:
            diag_category = 'All'
        if centernames == '' or None:
            centernames = 'All'
        if grades == '' or None:
            grades = ['All']
        if category == '' or None:
            category = 'All'
        if start_date == '' and end_date == '':
            today = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
            end_date = str(today.date())
            start_date = str(today.date() - timedelta(30))
        data = []
        state_list = []
        state_list.append(statenames.split(","))
        center_list = []
        center_list.append(centernames.split(","))
        category_list.append(category.split(","))
        diag_category_list.append(diag_category.split(","))
        diag_category_list = diag_category_list[0]
        if "All" in grades:
            grades = ['All']
        for stateName, centerName in zip(state_list, center_list):
            if flag == "AttendanceTrend":
                attendance_trends_data = get_attendance_trends(stateName, centerName, grades, start_date, end_date)
                data = attendance_trends_data
            elif flag == "Attendance_Courses_Per_Grade":
                grade_wise_json_data = get_attendance_courses_per_grade(stateName, centerName, grades, start_date,
                                                                        end_date)
                data = grade_wise_json_data
            elif flag == "Diagnostic_Outcome":
                total_aggregate_level_subject_wise = get_aggregate_level_subject_wise(stateName, centerName, grades,
                                                                                      start_date, end_date,
                                                                                      diag_category_list)
                diagonostic_outcome = get_diagonostic_outcome(stateName, centerName, grades, start_date, end_date,
                                                              diag_category_list)
                diagonostic_outcome_json_data = []
                diagonostic_outcome_english = get_data_for_diagonostic(diagonostic_outcome, "English Foundation",
                                                                       total_aggregate_level_subject_wise)
                diagonostic_outcome_maths = get_data_for_diagonostic(diagonostic_outcome, "Maths",
                                                                     total_aggregate_level_subject_wise)
                diagonostic_outcome_science = get_data_for_diagonostic(diagonostic_outcome, "Science",
                                                                       total_aggregate_level_subject_wise)
                diagonostic_outcome_json_data.append(diagonostic_outcome_english)
                diagonostic_outcome_json_data.append(diagonostic_outcome_maths)
                diagonostic_outcome_json_data.append(diagonostic_outcome_science)
                data = diagonostic_outcome_json_data
            elif flag == "Scholastic_Outcome":
                for category in category_list:
                    final_scholastic_outcome = get_scholastic_outcome(stateName, centerName, grades, start_date,
                                                                      end_date, category)
                    data = final_scholastic_outcome
            else:
                co_scholastic_outcome = get_co_scholastic_outcome(stateName, centerName, grades, start_date, end_date)
                co_scholastic_outcome_json_data = []
                co_scholastic_outcome_data = []
                remark_list = ['Curious', 'Attentiveness', 'Self Confidence', 'Responsibility', 'Supportiveness',
                               'Positive Attitude', 'Wider Perspective', 'Courteousness']
                for list_rmk in remark_list:
                    co_scholastic_outcome_data = get_data_for_co_scholastic_outcome(co_scholastic_outcome, list_rmk)
                    co_scholastic_outcome_json_data.append(co_scholastic_outcome_data)
                    data = co_scholastic_outcome_json_data

        return HttpResponse(simplejson.dumps(data), mimetype='application/json')


@csrf_exempt
def save_user_activity_by_ajax(request):
    if request.user.is_authenticated:
        activity_name = request.GET.get('activity_name')
        activity_type = request.GET.get('activity_type')
        if activity_type:
            activityType_id = ActivityType.objects.values('id').filter(activity_type=activity_type)
            if len(activityType_id) > 0:
                id_activity = activityType_id[0]['id']
                cur_date = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
                if request.user.id is not None:
                    username = request.user.username
                    activity = UserActivityHistory(created_date=cur_date, user_id=request.user.id,
                                                   activity_date_time=cur_date, activity_name=activity_name,
                                                   activity_type=activity_type, activity_type_id=id_activity,
                                                   username=username,
                                                   name=request.user.first_name + " " + request.user.last_name)
                    activity.save()
                    message = 'User Activity History Saved Successfully'
                else:
                    message = 'User Activity History Not Saved Please Login Again'
            else:
                message = 'Action not Found'
        else:
            message = 'Action not Found'
        userMessage = {'message': message}
        return HttpResponse(simplejson.dumps(userMessage), mimetype='application/json')


def approve_offering(request):
    tabName = request.GET.get('tab')
    if request.user.is_superuser:
        offerings = Offering.objects.filter(status='not_approved')
    if has_role(request.user.userprofile, "Partner Account Manager"):
        db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
            user=settings.DATABASES['default']['USER'],
            passwd=settings.DATABASES['default']['PASSWORD'],
            db=settings.DATABASES['default']['NAME'],
            charset="utf8",
            use_unicode=True)
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query = "select partner_id  as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
        dict_cur.execute(query)
        partner_id = [str(each['value']) for each in dict_cur.fetchall()]
        partner_id.sort()
        partner_id= tuple(partner_id)
        partner_id= partner_id[0]
        centers  =Center.objects.filter( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id)).values_list("id",flat=True)
        offerings = Offering.objects.filter(status='not_approved',center_id__in=centers)
        db.close()
        dict_cur.close()
    otherTasks = Task.objects.filter(Q(taskType='OTHER') & Q(task_other_status='not_approved'))
    print 'otherTasks.taskfor', otherTasks
    message = request.GET.get('message', '')
    return render_response(request, "approve_offering.html",
                           {'offerings': offerings, 'message': message, 'otherTasks': otherTasks, 'tabName': tabName})


@csrf_exempt
def updateOfferingOrOthersStatus(request):
    if request.is_ajax():
        flag = request.GET.get('flag')
        demand_page = request.GET.get('demand');
        task_id = request.GET.get('id')
        userId = request.GET.get('userId')
        message = ''
        status = ''
        user = request.user
        if user:
            if demand_page and demand_page is not None:
                if task_id and task_id is not None:
                    task_demand = Task.objects.filter(id=task_id).update(task_other_status='not_approved',
                                                                         taskFor=user.username, assignedTo='')
                    if task_demand == 1:
                        message = 'Your request successfully submitted, someone will be reaching to you shortly via email.'
                        status = 'success'
                    else:
                        status = 'failure'
                        message = 'Request rejected.'
                message_data = {'message': message, 'status': status}
                return HttpResponse(simplejson.dumps(message_data), mimetype='application/json')
        if flag:
            if flag == 'offering':
                offering_id = request.GET.get('offering_id', '')
                if offering_id:
                    check_update = Offering.objects.filter(id=offering_id).update(status='pending')
                    if check_update == 1:
                        message = 'Offering approved successfully.'
                        status = 'success'
                        offering = Offering.objects.get(pk=offering_id)
                        if offering:
                            center_admin = offering.center.admin
                            if center_admin and center_admin.email:
                                email = center_admin.email
                                recipients = []
                                name = center_admin.first_name + ' ' + center_admin.last_name
                                if not name:
                                    name = center_admin.username
                                recipients.append(email)
                                args = {'user': name, 'boardName': offering.course.board_name,
                                        'subject': offering.course.subject, 'grade': offering.course.grade,
                                        'startDate': offering.start_date, 'endDate': offering.end_date,
                                        'confirm_url': "www.evidyaloka.org//centeradmin/?center_id=" + str(
                                            offering.center_id) + ""}
                                body_template = 'mail/custom_offering_email.txt'
                                body = get_mail_content(body_template, args)
                                send_mail(" Your request has been Approved for New Custom offering", body,
                                          settings.DEFAULT_FROM_EMAIL, recipients)
                    else:
                        message = 'Offering can not be approved.'
                        status = 'failure'
                else:
                    message = 'Offering Id can not be null.'
                    status = 'failure'
            elif flag == 'other':
                task_id = request.GET.get('task_id')
                if task_id:
                    task = Task.objects.get(pk=task_id)
                    check_task_update = Task.objects.filter(id=task_id).update(task_other_status='approved',
                                                                               assignedTo=task.taskFor)
                    if check_task_update == 1:
                        task = Task.objects.get(pk=task_id)
                        try:
                            assign_user = User.objects.get(username=task.assignedTo)
                        except:
                            assign_user = ''
                        if assign_user and assign_user.email:
                            recipients = [assign_user.email]
                            name = assign_user.first_name + ' ' + assign_user.last_name
                            if not name:
                                name = assign_user.username
                            args = {'user': name, 'subject': task.subject, 'category': task.category}
                            body_template = 'mail/task/other_skill_confirm_full.txt'
                            body = get_mail_content(body_template, args)
                            send_mail("Your request has been Approved for Other Skills offerings.", body,
                                      settings.DEFAULT_FROM_EMAIL, recipients)
                        message = 'Task approved successfully.'
                        status = 'success'
                    else:
                        message = 'Task can not be approved.'
                        status = 'failure'
                else:
                    message = 'Task Id can not be null.'
                    status = 'failure'
            elif flag == 'reject':
                task_id = request.GET.get('task_id')
                if task_id:
                    check_task_update = Task.objects.filter(id=task_id).update(task_other_status='pending')
                    if check_task_update == 1:
                        task = Task.objects.get(pk=task_id)
                        try:
                            taskFor_user = User.objects.get(username=task.taskFor)
                        except:
                            taskFor_user = ''
                        if taskFor_user and taskFor_user.email:
                            recipients = [taskFor_user.email]
                            name = taskFor_user.first_name + ' ' + taskFor_user.last_name
                            if not name:
                                name = taskFor_user.username
                            args = {'user': name, 'subject': task.subject, 'category': task.category}
                            body_template = 'mail/task/other_skill_reject_full.txt'
                            body = get_mail_content(body_template, args)
                            send_mail("Your request has been Rejected for Other Skills offerings.", body,
                                      settings.DEFAULT_FROM_EMAIL, recipients)
                        message = 'Task rejected successfully.'
                        status = 'success'
                    else:
                        message = 'Task can not be rejected.'
                        status = 'failure'
                else:
                    message = 'Task Id can not be null.'
                    status = 'failure'
        message_data = {'message': message, 'status': status}
        return HttpResponse(simplejson.dumps(message_data), mimetype='application/json')


@csrf_exempt
def verifyUserForTSD(request):
    if request.is_ajax():
        message = ''
        status = ''
        userId = request.GET.get('userId', '')
        print userId
        if userId:
            user = User.objects.get(pk=userId)
            userp = user.userprofile
            if not has_pref_role(userp, "Teacher"):
                print "1"
                message = 'Preferred Role must be Teacher'
                status = 'failure'
            elif not userp.profile_completion_status:
                print "2"
                message = 'Profile is not completed'
                status = 'failure'
            else:
                if userp.skype_id and userp.phone:
                    message = 'success'
                    status = 'success'
                else:
                    message = 'skype Id and Phone can not be empty'
                    status = 'failure'
            final_message = {'message': message, 'status': status}
            return HttpResponse(simplejson.dumps(final_message), mimetype='application/json')


def funding_parter(request):
    return render_response(request, 'funding_parter.html')


def volunteer_partner(request):
    return render_response(request, 'volunteer_partner.html')


def running_courses(offering, courses, user=None):
    curr_date = datetime.datetime.utcnow() + relativedelta(hours=5, minutes=30)
    sessions = offering.session_set.all().order_by('date_start').exclude(teacher=None)
    """if len(sessions)==0:
        Offering.objects.filter(id = offering.id).update(active_teacher=None)"""
    teachers_first_name = None
    teachers_last_name = None
    is_assigned_offering = False
    session_id = None
    teachers_id = None
    next_sess = 0
    if sessions:
        for session in sessions:
            if session.teacher:
                if session.date_start >= curr_date and next_sess == 0:
                    next_sess = 1
                teachers_first_name = (session.teacher.first_name)
                teachers_last_name = (session.teacher.last_name)
                teachers_id = session.teacher_id
            session_id = session.id
    past_teacher_name = None
    past_teachers_id = None
    past_teachers = offering.session_set.filter(status='Completed').exclude(teacher=offering.active_teacher_id)
    if len(past_teachers) > 0:
        for past_teacher in past_teachers:
            if past_teacher.teacher:
                past_teacher_name = (past_teacher.teacher.first_name)
                past_teachers_id = past_teacher.teacher_id
    if past_teacher_name is None:
        past_teacher_name = ''
    # look wether the given offering is in user pref_offerings
    if user:
        try:
            user.userprofile.pref_offerings.get(id=offering.id)
            is_assigned_offering = True
        except Offering.DoesNotExist:
            is_assigned_offering = False

    start_date_ts = int(time.mktime(offering.start_date.timetuple()) * 1000) if offering.start_date else ''
    end_date_ts = int(time.mktime(offering.end_date.timetuple()) * 1000) if offering.end_date else ''

    planned_topics_arr = []
    planned_topics = offering.planned_topics.all()
    if planned_topics:
        for topic in planned_topics:
            planned_topics_arr.append(topic.title)

    courses.append({"course": make_number_verb(
        offering.course.grade) + " grade " + offering.course.board_name + " board " + offering.course.subject, \
                    "teachers_first_name": offering.active_teacher.first_name,
                    "teachers_last_name": offering.active_teacher.last_name, "teachers_id": offering.active_teacher.id,
                    'past_teacher_name': past_teacher_name, 'past_teachers_id': past_teachers_id,
                    "start_date": make_date_time(offering.start_date)["date"] + ", " +
                                  make_date_time(offering.start_date)["year"], \
                    "end_date": make_date_time(offering.end_date)["date"] + ", " + make_date_time(offering.end_date)[
                        "year"], "start_date_orig": offering.start_date, \
                    'end_date_orig': offering.end_date, "start_date_ts": start_date_ts, "end_date_ts": end_date_ts,
                    "offering_id": offering.id, "batch":offering.batch, \
                    "is_assigned_offering": is_assigned_offering, "session_id": session_id,
                    "subject": offering.course.subject, "center": offering.center.name, \
                    "language": offering.language,
                    "course_offered": make_number_verb(offering.course.grade) + " " + offering.course.subject, \
                    "planned_topics": planned_topics_arr, "center_language": offering.center.language,
                    "grade": make_number_verb(offering.course.grade), "program":offering.get_program_type_display()})


def backfill_courses(offering, courses, user=None):
    sessions = offering.session_set.all()
    if len(sessions)>=0:
        is_assigned_offering = False
        session_id = None
        if sessions:
            for session in sessions:
                session_id = session.id
        if user:
            try:
                user.userprofile.pref_offerings.get(id=offering.id)
                is_assigned_offering = True
            except Offering.DoesNotExist:
                is_assigned_offering = False

        start_date_ts = int(time.mktime(offering.start_date.timetuple()) * 1000) if offering.start_date else ''
        end_date_ts = int(time.mktime(offering.end_date.timetuple()) * 1000) if offering.end_date else ''
        planned_topics_arr = []
        planned_topics = offering.planned_topics.all()
        if planned_topics:
            for topic in planned_topics:
                planned_topics_arr.append(topic.title)
        courses.append({"course": make_number_verb(
            offering.course.grade) + " grade " + offering.course.board_name + " board " + offering.course.subject, \
                        "start_date": make_date_time(offering.start_date)["date"] + ", " +
                                      make_date_time(offering.start_date)["year"], \
                        "end_date": make_date_time(offering.end_date)["date"] + ", " +
                                    make_date_time(offering.end_date)["year"], "start_date_orig": offering.start_date, \
                        'end_date_orig': offering.end_date, "start_date_ts": start_date_ts, "end_date_ts": end_date_ts,
                        "offering_id": offering.id, "batch":offering.batch, \
                        "is_assigned_offering": is_assigned_offering, "session_id": session_id,
                        "subject": offering.course.subject, "center": offering.center.name, \
                        "language": offering.language,
                        "course_offered": make_number_verb(offering.course.grade) + " " + offering.course.subject, \
                        "planned_topics": planned_topics_arr, "center_language": offering.center.language,
                        "grade": make_number_verb(offering.course.grade), "program":offering.program_type})


def campaign(request):
    return render_response(request, 'vol_signup.html')


def evschool(request):
    return render_response(request,'eschool_mobile.html')


def digitalSchool(request):
    return render_response(request, 'digitalschool.html')

@csrf_exempt
def campaign_signup(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    email = request.POST.get("email")
    phone = request.POST.get("phone", '')
    password = request.POST.get("password")
    referal = request.POST.get('referal')
    referal_p = request.POST.get('referal_p')
    reference_channel = ''
    if referal_p:
        try:
            referal_partner = ReferenceChannel.objects.filter(partner_id = referal_p)
            if len(referal_partner)>0:
                reference_channel = referal_partner[0]
        except:
            pass

    referal_name = ''
    referalUser = None
    if referal:
        try:
            referalUser = User.objects.get(pk=referal)
            referal_name = str(referalUser.first_name) + " " + str(referalUser.last_name)
        except:
            pass

    if email:
        existing_user = User.objects.filter(email=email)
        if existing_user:
            response_data = {}
            response_data['status'] = 1
            response_data['message'] = 'User exists already, please login'
            return HttpResponse(json.dumps(response_data), mimetype="application/json")

        if email:
            new_user = User.objects.create_user(email=email, username=email)
            new_user.set_password(password)
            new_user.save()
            user = authenticate(username=email, password=password)
            login(request, user)
            userp = user.userprofile
            user.first_name = first_name
            user.last_name = last_name
            userp.phone = phone
            if referal_name and referalUser != None:
                userp.referer = referal_name
                userp.referred_user = referalUser
            if reference_channel:
                userp.referencechannel  = reference_channel
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
            return HttpResponse("Welcome to eVidyaloka. Let us get started.")
        # except:
        #     pass
    else:
        return HttpResponse("Error")


def nad_campaign(request):
    return render_response(request, 'campaign_newyear.html')


def rubaru_base(request):
    return render_response(request, 'rubaru_base.html')


def create_task_for_EVD(request,dueDate,comment,category,subject,mail_subject,assign_to,perfomed_usr,task_subject,taskCreatedBy_userId):
    performedOn_name = ''
    perfomed_usr_id = ''
    if perfomed_usr:
        performedOn_name = str(perfomed_usr.first_name) +'  '+ str(perfomed_usr.last_name) +'-'+str(perfomed_usr.id)
        perfomed_usr_id = perfomed_usr.id
    taskCreatedDate = (datetime.datetime.utcnow()+relativedelta(hours=5, minutes=30))
    date_joined = None
    todayDate=datetime.datetime.today()
    todayDay=calendar.day_name[todayDate.weekday()]
    try:
        usrobj = User.objects.get(pk=assign_to)
        date_joined = usrobj.date_joined
    except:
        usrobj = None
    task = Task(comment=comment,subject=task_subject,assignedTo=usrobj,dueDate=dueDate,priority="Normal",
               taskCreatedBy_userId=taskCreatedBy_userId,taskStatus="Open",performedOn_userId = perfomed_usr_id,
                taskCreatedDate=taskCreatedDate, user_date_joined=date_joined,performedOn_name=performedOn_name,
                taskType="MANUAL")
    task.save()
    task_id = Task.objects.filter(assignedTo = usrobj).order_by('-id')[0]
    print task_id.id
    recipients = []
    user = request.user
    if usrobj:
        email = usrobj.email
        print "Vol-admin mail :"+str(email)
        if email:
            name = usrobj.first_name+' '+usrobj.last_name
            if not name:
                name = usrobj.username
            recipients.append(email)
            args = {'user':name,'date':taskCreatedDate,'subject' : subject, 'comment': comment, \
                        'confirm_url':WEB_BASE_URL + "edit_task/?id=" + str(task.id),'todayDay':todayDay }
            body_template = 'mail/task/task_full.txt'
            body = get_mail_content(body_template, args)
            send_mail(mail_subject, body, settings.DEFAULT_FROM_EMAIL, recipients)
    return task_id.id


def evplus(request):
    return render_response(request, 'evplus.html')


def update_file_records(request, up_data_p, asses_date, today, category):
    updated_count = 0
    rejected_count = 0
    create_count = 0
    update_list = []
    teacher_id = ''
    for i, ent in enumerate(up_data_p):
        update_status = 0
        learning_details = 0
        creat_date = datetime.datetime.strptime(asses_date, '%m/%d/%Y')
        if i == 0:
            teach_offer = Offering.objects.get(pk=ent['offer'])
            offering_teacher = teach_offer.session_set.all().filter(date_start__lte=today).exclude(teacher=None).order_by('date_start').reverse()
            if offering_teacher: teacher = teacehr[0].teacher
            else: teacher = request.user
            teacher_id = teacher.id

        chid_dict = {'category': ent['category'], 'total_marks': ent['total'], 'obtained_marks': ent['actual'],
                     'is_present': ent['is_present']}
        update_status = Scholastic.objects.filter(category=ent['category'], learning_record__student=ent['id'], learning_record__offering=ent['offer']).update(**chid_dict)
        if update_status == 0:
            lr_dict = {'student_id': ent['id'], 'offering_id': ent['offer'], 'category_id': category.id,
                   'created_by_id': teacher_id, 'date_created': creat_date}
            child_dict = {'category': ent['category'], 'total_marks': ent['total'], 'obtained_marks': ent['actual'],
                      'is_present': ent['is_present']}
            lr = LearningRecord(**lr_dict)
            lr.save()
            schol = Scholastic(learning_record_id=lr.id, **child_dict)
            schol.save()
        else:
            learning_record_id = Scholastic.objects.values('learning_record_id').filter(category=ent['category'], learning_record__student=ent['id'], learning_record__offering=ent['offer'])
            learning_record_id = learning_record_id[0]['learning_record_id']
            learning_details = LearningRecord.objects.filter(id=learning_record_id).update(category=category, created_by=teacher, date_created=creat_date)

        if update_status and learning_details:
            updated_count = updated_count + 1
        elif update_status == 0:
            create_count=create_count+1
        else:
            rejected_count = rejected_count + 1
    update_list.append(updated_count)
    update_list.append(rejected_count)
    update_list.append(create_count)
    return update_list


def update_diag_file_records(up_data_p, asses_date, ver):
    updated_count = 0
    rejected_count = 0
    created_count=0
    update_list = []
    for ent in up_data_p['data']:
        creat_date = datetime.datetime.strptime(asses_date, '%m/%d/%Y')
        ent_cpy = ent
        stud_id = ent_cpy.pop('Student Id')
        offer_id = ent_cpy.pop('Offering Id')
        offer = Offering.objects.get(pk=offer_id)
        grade = offer.course.grade
        sub = offer.course.subject
        agg_level = ent_cpy.pop('Aggregate level')
        category = ent_cpy.pop('category')
        del ent_cpy['Course Name'], ent_cpy['Student Name']
        diag = Diagnostic.objects.filter(student=stud_id, offering_id=offer_id, category=category)
        diag_dict = {'id' : diag[0].id, 'student_id': stud_id, 'offering_id': offer_id, 'grade': grade, 'subject': sub,
                     'aggregate_level': agg_level, 'date_created': creat_date, 'category': category}
        diag_val = Diagnostic(**diag_dict)
        agg_level = calculate_agg_level(diag_val)
        update_status = diag.update(id =diag[0].id, student=stud_id, offering=offer_id, grade=grade, subject=sub,
                                    aggregate_level=agg_level, category=category, date_created=creat_date)
        if update_status == 0:
            diag_dict = {'student_id': stud_id, 'offering_id': offer_id, 'grade': grade, 'subject': sub,
                     'aggregate_level': agg_level, 'date_created': creat_date, 'category': category}
            diag = Diagnostic(**diag_dict)
            diag.save()
            for k, v in ent_cpy.items():
                p_obj = DiagParameter.objects.get(param_code=k, version=ver)
                dd_dict = {'diagnostic_id': diag.id, 'parameter_id': p_obj.id, 'actual_marks': v}
                dd_obj = DiagDetails(**dd_dict)
                dd_obj.save()
            diag.aggregate_level = calculate_agg_level(diag)
            diag.save()
        else:
            for k, v in ent_cpy.items():
                p_obj = DiagParameter.objects.get(param_code=k, version=ver)
                dd_obj = DiagDetails.objects.filter(diagnostic=diag[0].id).update(diagnostic=diag[0].id,actual_marks=v)

        if update_status:
            updated_count = updated_count + 1
        elif update_status == 0:
            created_count=created_count+1;
        else:
            rejected_count = rejected_count + 1
    update_list.append(updated_count)
    update_list.append(rejected_count)
    update_list.append(created_count)
    return update_list

def new_home(request):
    list_of_index = []
    #userprofiles = UserProfile.objects.filter(rolepreference__role_status = 'Active', rolepreference__role_outcome= 'Recommended').only('id','picture', 'user__first_name', 'user__last_name','languages_known')

    last_rec = Ayfy.objects.values('title').order_by('-id')[:1]
    ayfy = last_rec[0]['title']
    ayfy_list = ['AY-20-21','AY-21-22']
    req_teachers = Offering.objects.filter(active_teacher = None, status__in = ['pending','running'], academic_year__title__in = ayfy_list).count()
    centers = Offering.objects.values_list('center', flat = True).filter(active_teacher = None, status__in = ['pending','running'], academic_year__title__in = ayfy_list).distinct().count()
    from datetime import datetime
    curr_mon = datetime.now().month
    vol_of_month = VolOfMonth.objects.filter(month = curr_mon,status='approved')
   
    #for vol_of_month1 in vol_of_month:
          #vol_of_month1 = check_prof_pic(vol_of_month1)
          #count1 = vol_of_month1.elected_user.session_set.filter(status='Completed').count()
          #vol_of_month1.sessionCount = count1

    if vol_of_month.count() < 3:
        vol_of_month = VolOfMonth.objects.filter(status='approved').order_by('-id')[:5]
    last = vol_of_month.count() - 1
    teachers_dict = {}
    if vol_of_month.count() > 2:
        last = vol_of_month.count() - 1
        for i in range(3):
            list_of_index = create_random_index(list_of_index, last)
            sess_count_temp = vol_of_month[list_of_index[i]].elected_user.session_set.filter(status='Completed').count()
            teachers_dict[i] = vol_of_month[list_of_index[i]].elected_user.userprofile
            teachers_dict[i].sessionCount = sess_count_temp
            path = teachers_dict[i].picture
            #print "path ",type(path)
            picture_name = path.split('/')
            #print "picture_name",picture_name
            if picture_name and path:
                pic_static_dir = picture_name[1]
                if pic_static_dir == 'static':
                    try:
                        path = path[1:]
                        present = PIL.open(path)
                    except:
                        teachers_dict[i].picture = '/static/images/defaultteacherimg_1.png'
            #if teachers_dict[i].languages_known:
            #    teachers_dict[i].languages_known = literal_eval(teachers_dict[i].languages_known)

    #print "teachers_dict ",teachers_dict

    """from datetime import datetime
    curr_mon = datetime.now().month
    vol_of_month = VolOfMonth.objects.filter(month = curr_mon)
    for vol_of_month1 in vol_of_month:
          count1 = vol_of_month1.elected_user.session_set.filter(status='Completed').count()
          vol_of_month1.sessionCount = count1"""




    """ 
    teachers_dict = {}
    MyObj1 = userprofiles[list_of_index[0]]
    MyObj1.languages_known = literal_eval(MyObj1.languages_known)
    MyObj2 = userprofiles[list_of_index[1]]
    MyObj3 = userprofiles[list_of_index[2]]

    teachers_dict = {1: MyObj1, 2: MyObj2, 3: MyObj3}
    print "teachers_dict ",teachers_dict[1].id
    print "teachers_dict ",teachers_dict"""
    #print "teachers_dictnnnn ",teachers_dict[1].languages_known
    show_popup = request.GET.get("show_popup", None)
    popup_type = request.GET.get("type", None)
    show_popup = {"show_popup": show_popup, "type": popup_type}

    return render_response(request, 'new_ui_home.html', {'teachers_dict': teachers_dict, "show_popup": show_popup, 'req_teachers': req_teachers, 'centers': centers})


def create_random_index(list_of_index, last):
    index1 = random.randint(0, last)
    if index1 in list_of_index:
        create_random_index(list_of_index, last)
    else:
        list_of_index.append(index1)
    return list_of_index

def projectsummarydetail(request):
    centers =[]
    if request.GET['search']:
        search = request.GET['search']

        partner = request.user.partner_set.all()
        partner_count = partner.count()
        print "partner",partner
        if partner:
            partner_types = partner[0].partnertype.values()
            for partnerty in partner_types:
                if partnerty['name'] == 'Organization Unit': is_orgUnit = True
                if partnerty['name'] == 'Funding Partner': is_funding_partner = True
            centers = Center.objects.filter(Q(orgunit_partner__contactperson=request.user, status='Active') | Q(
                delivery_partner__contactperson=request.user, status='Active') | Q(
                funding_partner__contactperson=request.user, status='Active'),state=search).values('name')
            print "centers",centers


        else:
            centers = Center.objects.filter(state=search,status = 'Active').values('name')
    data = list(centers)
    return HttpResponse(simplejson.dumps(data), content_type="application/json")


def tttinfo(request):
    return render_response(request, 'tttinfo.html')

@csrf_exempt
@login_required
def manage_tttinfo(request): 
    
    if request.method == 'POST':
        fields=['class','state', 'subject', 'date', 'chapter', 'chanel']
        table = { x:request.POST[x] for x in fields }
        # modify date
        if table['date']:
            x = table['date']
            m = x.replace('T', '-').replace(':', '-').split('-')
            d = datetime.datetime(int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4]))
        else:
            d=None
        
        form = TvBroadCast.objects.create(state=table['state'], student_class=table['class'], subject=table['subject'], chapter_name=table['chapter'], chanel=table['chanel'],date=d)
        form.save()
        data = {'state':str(table['state'])}
        

        return HttpResponse(simplejson.dumps(data), content_type='application/json')
         
    
    table = TvBroadCast.objects.filter(date__gt=datetime.datetime.now().date())
    return render_response(request, 'manage_tttinfo.html', {'table':table})


@csrf_exempt
def tv_timetable_bulk_upload(request):
    if request.method == "POST":
        queryset = request.POST.items()[0][0]  
        mydict = ast.literal_eval(queryset)
        bulk_list = []

        for state in mydict:
            if len(mydict[state]) >0:
                mystate = str(state)
                for row in mydict[state]:
                    if row['date']:
                        x = row['date']
                        m = x.replace('T', '-').replace(':', '-').split('-')
                        d = datetime.datetime(int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4]))
                    else:
                        d=None
                    bulk = TvBroadCast(state=mystate, chanel=row['chanel'], date=d, student_class=int(row['student_class']), subject=row['subject'], chapter_name=row['chapter_name'])
                    bulk_list.append(bulk)
        
        # print(bulk_list)
        # import pdb; pdb.set_trace()
        TvBroadCast.objects.bulk_create(bulk_list)  # bulk create  NO-need to call save() 
        messages.success(request, 'Timetable list details updated.')     

        return HttpResponse('s', content_type='application/json')
        


@csrf_exempt
def update_time_table(request): 

    # import pdb; pdb.set_trace()
    if request.method == 'POST':
       
        fields=[ 'id', 'student_class', 'subject', 'date', 'chapter_name', 'chanel']
        table = { x:request.POST.get(x, None) for x in fields }
        
        # modify date
        x = table['date']
        m = x.replace('T', '-').replace(':', '-').split('-')
        d = datetime.datetime(int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4]))
        form = TvBroadCast.objects.get(pk=int(table['id']))

        form.date = d
        form.student_class = int(table['student_class'])
        form.subject = str(table['subject'])
        form.chapter_name = str(table['chapter_name'])
        form.chanel = str(table['chanel'])
        form.save()

        return HttpResponse('u', content_type='application/json')


@csrf_exempt
def delete_time_table(request):
    if request.method == 'POST':
        id = int(request.POST.get('id', None))
        # print(id)
        table = TvBroadCast.objects.get(pk=id)
        table.delete()
        return HttpResponse('d', content_type='application/json')


@csrf_exempt
def get_time_table(request):
    if request.method=='POST':
        state = str(request.POST.get('state', None))
        for_map = request.POST.get('map', False)

        data =[]
        if state:
            if for_map:
                qs = TvBroadCast.objects.filter(state = state, date__gt=datetime.datetime.now().date()).order_by('date')[0:10]
                states = TvBroadCast.objects.filter(date__gt=datetime.datetime.now().date()).distinct().values_list('state', flat=True)
                
                state_list = [val.encode("utf-8") for val in states]
                data.append({'states':state_list})

                qs_json = serializers.serialize('json', qs)
                qs_dict = json.loads(qs_json)
                data.append({'table':qs_dict})
            
                data_json = simplejson.dumps(data)
                
            else:
                qs = TvBroadCast.objects.filter(state = state, date__gt=datetime.datetime.now().date()).order_by('date')
                data_json = serializers.serialize('json', qs)


            
        
            return HttpResponse(data_json, content_type='application/json')
        return HttpResponse('No state', content_type='application/json')


def multi_stat(request):

    profile = UserProfile.objects.get(user=request.user)
    is_partner=False; is_school_admin = False
    if profile:
        if len(profile.role.filter(name = "Partner Admin")) > 0 or len(profile.role.filter(name = "OUAdmin")):
            is_partner=True
        elif len(profile.role.filter(name = "School Admin")) > 0:
            schooladmin = Partner.objects.get(contactperson=request.user)
            is_school_admin = True

    mycenters = getAllCenters(request)
    states = []
    if mycenters is not None and len(mycenters) > 0:
        states = mycenters.values_list('state', flat=True).distinct().order_by('state')
    if states != [] and states[0] is None:
        states = states[1:]

    centers = mycenters.filter(state__in=states).distinct().order_by('name')
    ays = Ayfy.objects.filter(board__isnull = False).order_by('-title').values_list('title', flat=True).distinct()
    context = {'centers': centers, 'states': states,'ays':ays, 'is_partner':is_partner, 'is_school_admin':is_school_admin}
    return render_response(request, 'multi_stat.html', context)


   
def stat_fetch_details(request):

    myDict = dict(request.POST.iterlists())
    data = { key.encode("utf-8").replace('[]',''):map(str, val) for key, val in myDict.items() }
    state =   data['state']
    partner = [int(x) for x in data['partner'] ]
    funding_partner=[int(x) for x in data['donor']]
    centers =[int(x) for x in data['center']]
    all_centers = getAllCenters(request)
    total_centers = len(all_centers.filter(delivery_partner__in=partner,state__in=state).distinct().order_by('name'))

    if all_centers !=None:
        all_centers = all_centers.values('id','name','state','delivery_partner_id','delivery_partner__name_of_organization','funding_partner_id','funding_partner__name_of_organization', 'board').distinct().order_by('name')
    data = []
    
    if '-1' not in state:
        all_centers = all_centers.filter(state__in=state).distinct().order_by('name')
    if total_centers != 0:
        all_centers = all_centers.filter(delivery_partner__in=partner).distinct().order_by('name')
    if -1 not in  partner:
        all_centers = all_centers.filter(delivery_partner__in=partner).distinct().order_by('name')
    if -1 not in funding_partner:
        all_centers = all_centers.filter(funding_partner__in=funding_partner).distinct().order_by('name')
    if -1 not in centers:
        all_centers = all_centers.filter(id__in=centers).distinct().order_by('name')

    mypartner= []; mycenter = []; mystate=[]; mydonor = []; myboard=[]; mycenter_list=[]

    [(mycenter.append({'center_id':center['id'],'center_name':center['name']}), mycenter_list.append(center['id']), mystate.append({'state':center['state']}), mydonor.append({'donor_id':center['funding_partner_id'],'donor_name':center['funding_partner__name_of_organization']}), mypartner.append({'partner_id':center['delivery_partner_id'],'partner_name':center['delivery_partner__name_of_organization']}), myboard.append({'board':center['board']})) for center in all_centers]

    clean_partner = []; clean_center = []; clean_donor = []; clean_state=[]; clean_board=[]; mycourse = []; dump =[]
    [dump.append(x) for x in mycenter_list if x not in dump]
    offer = Offering.objects.filter(center__in=dump).order_by('id').values_list('course', flat=True).distinct()
    myc = Course.objects.filter(pk__in=offer, type='s').values_list('id', 'board_name', 'subject', 'grade').distinct().order_by('board_name')
    mycid = Course.objects.filter(pk__in=offer, type='s').values_list('id', flat=True).distinct().order_by('id')
    
    [mycourse.append({'id':x[0], 'board':x[1], 'subject':x[2], 'class':x[3]}) for x in myc]
    [clean_center.append(x) for x in mycenter if x not in clean_center and x['center_id'] !=None]
    [clean_partner.append(x) for x in mypartner if x not in clean_partner and x['partner_id'] !=None]
    [clean_donor.append(x) for x in mydonor if x not in clean_donor and x['donor_id'] !=None]
    [clean_state.append(x) for x in mystate if x not in clean_state and x['state'] !=None]
    [clean_board.append(x) for x in myboard if x not in clean_board and x['board'] !=None]
    data.append(clean_center); data.append(clean_partner); data.append(clean_donor); data.append(clean_state); data.append(mycourse)
    
    return HttpResponse(simplejson.dumps(data), mimetype = 'application/json')


def stat_summary(request):
    '''
       returns summery data 
    '''
    myDict = dict(request.POST.iterlists())
    data = { key.encode("utf-8").replace('[]',''):map(str, val) for key, val in myDict.items() }
    state =   [x for x in data['state_id']]
    partner = [int(x) for x in data['partner_id']]
    centers = [int(x) for x in data['center_id']]
    courses = [int(x) for x in data['course_id']]
    funding_partner=[int(x) for x in data['donor_id']]
    ays = Ayfy.objects.values_list('id', flat=True).filter(title=data['ay_id'][0])
    ayfy = data['ay_id'][0]
    date_start = datetime.datetime.strptime(data["from_date"][0] ,"%Y-%m-%d")
    date_end = datetime.datetime.strptime(data["to_date"][0] ,"%Y-%m-%d")
    all_centers = getAllCenters(request)

    try:
        if '-1' not in state:all_centers = all_centers.filter(state__in=state).distinct().order_by('name')
        if -1 not in  partner:all_centers = all_centers.filter(delivery_partner__in=partner).distinct().order_by('name')
        if -1 not in funding_partner:all_centers = all_centers.filter(funding_partner__in=funding_partner).distinct().order_by('name')
        if -1 not in centers:all_centers = all_centers.filter(id__in = centers)
        centers = all_centers.values_list('id', flat=True)
        
        if -1 in courses:courses = Course.objects.values_list('id', flat=True)
        else:courses = Course.objects.values_list('id', flat=True).filter(id__in=courses)

        student_grades = Course.objects.values_list('grade', flat=True).filter(id__in=courses)
        global_data = {'center_count':0, 'teacher_count' : 0,'active_teacher_count' : 0,'active_offering_count' : 0, 'total_student' : 0, 'planvsact' : 0, 'child_attend': 0, 'session_unique_present_students':0}
        student_grades = Course.objects.values_list('grade', flat=True).filter(id__in=courses)
        active_students = Student.objects.filter(center__in=centers, grade__in=student_grades, status='Active').count()
        active_students_boys = Student.objects.filter(center__in=centers, grade__in=student_grades, status='Active', gender='Boy').count()
        active_students_girls = Student.objects.filter(center__in=centers, grade__in=student_grades, status='Active', gender='Girl').count()
        active_offering = Offering.objects.values_list('id', flat=True).filter(academic_year__title=ayfy, status__in=['running'], active_teacher__isnull = False, center__in=centers, course__in=courses).distinct()
        completed_offering = Offering.objects.values_list('id', flat=True).filter(academic_year__title=ayfy, status__in=['completed'], active_teacher__isnull = False, center__in=centers, course__in=courses).distinct()
        enrolled_offering = Offering.objects.values_list('id', flat=True).filter(academic_year__title=ayfy, status__in=['running', 'completed'], center__in=centers, course__in=courses).distinct()
        active_teachers = Offering.objects.values_list('active_teacher', flat=True).filter(academic_year__title=ayfy, status__in=['running','pending'], center__in=centers, active_teacher__isnull = False, course__in=courses).distinct().count()
        # total_teachers = Offering.objects.values_list('active_teacher', flat=True).filter(academic_year__title=ayfy, status__in=['running','completed'], center__in=centers, active_teacher__isnull = False).distinct().count()
        # completed_sessions_offering = Session.objects.values_list('offering', flat=True).filter(offering__academic_year__title=ayfy, offering__in=enrolled_offering, status__in=['completed'], offering__center__in=centers, offering__course__in=courses, date_start__gte=str(date_start), date_end__lte=str(date_end)).distinct()
        students_enroll = []
        ofs = Offering.objects.filter(id__in=enrolled_offering)
        [students_enroll.extend(off.enrolled_students.filter(status='Active').values_list('id', flat=True)) for off in ofs]
        students_enroll = list(set(students_enroll))
        students_enroll_boys = Student.objects.filter(id__in=students_enroll, gender__in=('Boy','male')).count()
        students_enroll_girls = Student.objects.filter(id__in=students_enroll, gender__in=('Girl','female')).count()
        print(students_enroll, students_enroll_boys, students_enroll_girls)
        print('--------1----------')
        # enrolled_students = Offering_enrolled_students.objects.values_list('student_id', flat=True).filter(offering__in=active_sessions_offering).distinct().count()
        # active_sessions = Session.objects.values_list('id', flat=True).filter(offering__in=active_sessions_offering, status__in=['running','pending'], date_start__gte=str(date_start), date_end__lte=str(date_end))
        completed_sessions = Session.objects.values_list('id', flat=True).filter(offering__in=completed_offering, status__in=['completed','Completed','Offline'], date_start__gte=str(date_start), date_end__lte=str(date_end))
        print('--------1.5----------')
        session_enrolled_students = SessionAttendance.objects.filter(session__in=completed_sessions).count()
        print('--------2----------')
        if session_enrolled_students:
            session_present_students = SessionAttendance.objects.filter(session__in=completed_sessions, is_present='yes').count()
            session_unique_present_students = SessionAttendance.objects.filter(session__in=completed_sessions, is_present='yes').distinct().count()
        else: 
            session_present_students = 0
            session_unique_present_students = 0
        print('--------3----------')
        # total_sessions = Session.objects.values_list('id', flat=True).filter(offering__academic_year__title=ayfy, offering__center__in=centers, offering__center__status='Active', date_start__gte=str(date_start), date_end__lte=str(date_end)).count()
        # completed_sessions = Session.objects.values_list('id', flat=True).filter(offering__academic_year__title=ayfy, status__in=['completed','Completed','Offline'], offering__center__in=centers, offering__course__in=courses, offering__center__status='Active', date_start__gte=str(date_start), date_end__lte=str(date_end)).count()
        # sessions_status = Session.objects.values('status').filter(offering__academic_year__title=ayfy, offering__center__in=centers, offering__course__in=courses, date_start__gte=str(date_start), date_end__lte=str(date_end)).annotate(session_status_count=Count('status')).order_by()
        # print('--------4----------')
        # sessions_cancel = Session.objects.values('cancel_reason').filter(offering__academic_year__title=ayfy, status='Cancelled', offering__center__in=centers, offering__course__in=courses, date_start__gte=str(date_start), date_end__lte=str(date_end)).annotate(session_cancellReason_count=Count('cancel_reason')).order_by()
        # print('--------5----------')
        # global_data['total_sessions'] = total_sessions
        # global_data['completed_sessions'] = completed_sessions
        global_data['session_enrolled_students'] = session_enrolled_students
        global_data['session_present_students'] = session_present_students
        global_data['session_unique_present_students'] = session_unique_present_students
        global_data['center_count'] = len(centers)
        # global_data['teacher_count'] = total_teachers
        global_data['total_students_center'] = active_students
        global_data['total_students_boys_center'] = active_students_boys
        global_data['total_students_girls_center'] = active_students_boys
        global_data['active_teacher_count'] = active_teachers
        global_data['active_offering_count'] = len(active_offering)
        global_data['enroll_students'] = len(students_enroll)
        global_data['enroll_students_boys'] = students_enroll_boys
        global_data['enroll_students_girls'] = students_enroll_girls
        # global_data['class_status'] = list(sessions_status)
        # global_data['cancle_class_status'] = list(sessions_cancel)
    except Exception as e:
            print("FlmStudentAttendanceView POST Exception  e", e)
            traceback.print_exc()
    return HttpResponse(simplejson.dumps(global_data), mimetype = 'application/json')


def get_stat_table(request):

    try:

        queryDict = request.POST
        myDict = dict(queryDict.iterlists())
        data = { key.encode("utf-8").replace('[]',''):map(str, val) for key, val in myDict.items() }
        state =   data['state_id']
        partner = [int(x) for x in data['partner_id'] ]
        centers = [int(x) for x in data['center_id'] ]
        funding_partner=[int(x) for x in data['donor_id']]
        ay_id= data['ay_id'][0]
        date_start = datetime.datetime.strptime(data["from_date"][0] ,"%Y-%m-%d")
        date_end = datetime.datetime.strptime(data["to_date"][0] ,"%Y-%m-%d")
        all_centers = getAllCenters(request)

        if '-1' not in state:
            all_centers = all_centers.filter(state__in=state).distinct().order_by('name')
        if -1 not in  partner:
            all_centers = all_centers.filter(delivery_partner__in=partner).distinct().order_by('name')
        if -1 not in funding_partner:
            all_centers = all_centers.filter(funding_partner__in=funding_partner).distinct().order_by('name')
        if -1 not in centers:
            all_centers = all_centers.filter(id__in = centers)

        if ay_id:
            for center in all_centers:
                if center.offering_set.filter(academic_year__title=ay_id):
                    pass
                else:
                    all_centers.exclude(id=center.id)

        if all_centers !=None:
            allcenters = all_centers.values('id','name','state','delivery_partner_id','delivery_partner__name_of_organization','funding_partner_id','funding_partner__name_of_organization', 'board').distinct().order_by('name')
        
        mycenter_list=[]; clean_board=[]; dump =[]

        [mycenter_list.append(center['id']) for center in allcenters]
        [dump.append(x) for x in mycenter_list if x not in dump]
        offer = Offering.objects.filter(center__in=dump).order_by('id').values_list('course', flat=True).distinct()
        mcid = Course.objects.filter(pk__in=offer, type='s').values_list('id', flat=True).distinct().order_by('id')
        mycid = [str(x) for x in mcid]

        if len(mcid) > 0 :
            cidstr =""
            i=0
            for id in mycid:
                cidstr+= "'"+id+"'"
                i=i+1
                if i < len(mcid) :
                    cidstr += ","

        db = evd_getDB()
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        global_data = {'center_count':0, 'teacher_count' : 0,'active_teacher_count' : 0,'active_offering_count' : 0, 'total_student' : 0, 'planvsact' : 0, 'child_attend': 0}
        center_ids = all_centers.values_list('id',flat=True)
        center_ids = ','.join(map(str, center_ids)) 
        idList = center_ids.split(",")
        myCenterId=''
        i=0
        if len(idList) > 0 : 
            for ids in idList:
                myCenterId+= "'"+ids+"'"
                i=i+1
                if i < len(idList) :
                    myCenterId += ","


        global_data = {}
        table_data = []

        if -1 in centers:
            try:
                for center in all_centers:
                    query = '''select count(distinct(web_sessionattendance.student_id)) as unique_student_count,
                            count(web_sessionattendance.is_present) as enrol_student_count,
                            count(case when web_sessionattendance.is_present = 'yes' then 1 end) present_student_count
                            from web_sessionattendance join web_session on web_session.id=web_sessionattendance.session_id
                            join web_offering on web_offering.id=web_session.offering_id 
                            join web_ayfy on web_ayfy.id = web_offering.academic_year_id
                            join web_student on web_student.id =  web_sessionattendance.student_id
                            where (DATE(web_session.date_start)>='{date_start}') and (DATE(date_start) <= '{date_end}') and web_student.is_test_user=0 and web_student.status='Active'
                            and web_offering.center_id={center_id} and (teacher_id is not null or teacher_id !='') and web_ayfy.title= "{ay_id}" '''.format(date_start=date_start, date_end=date_end, center_id=center.id, ay_id=ay_id)
                    
                    dict_cur.execute(query)
                    student_details = dict_cur.fetchall()
                    query = "select count(distinct(web_offering.id)) as offering_count,\
                            count(distinct(web_session.id)) as planned_session,\
                            count(case when web_session.status in ( 'completed') then 1 end) online_session,\
                            count(case when web_session.status = 'offline' then 1 end) offline_session,\
                            count(case when web_session.status = 'cancelled' then 1 end) cancelled_session from web_offering \
                            join web_session on web_session.offering_id = web_offering.id \
                            where DATE(web_session.date_start)>='"+str(date_start)+"' and DATE(web_session.date_end)<='"+str(date_end)+"' \
                            and web_offering.center_id ="+str(center.id)+" and (teacher_id is not null or teacher_id !='')"
                    dict_cur.execute(query) 
                    session_details = dict_cur.fetchall()
                    if student_details[0]['enrol_student_count']>0:
                        attendance_perc = str(round(((float( student_details[0]['present_student_count'])/ student_details[0]['enrol_student_count'])*100 ),2))
                    else:
                        attendance_perc = 0

                    details = {'center_name':center.name,
                            'offering_count':session_details[0]['offering_count'],
                            'planned_session':session_details[0]['planned_session'],
                            'online_session':session_details[0]['online_session'], 
                            'cancelled_session':session_details[0]['cancelled_session'],
                            'offline_session':session_details[0]['offline_session'],
                            'total_students':student_details[0]['unique_student_count'],
                            'enrol_students':student_details[0]['enrol_student_count'],
                            'present_students': student_details[0]['present_student_count'],
                            'attendance_perc':attendance_perc
                            }
                    table_data.append(details)
            except Exception as exp:
                print("EXCEPTION: " + str(exp))
            global_data['table_data'] = table_data
        # --------------------------------------
        else:

            identified_centers = [str(center.id) for center in all_centers]
            centers = ",".join(identified_centers)
            query = '''select distinct(web_offering.id) from web_offering 
                        join web_ayfy on web_ayfy.id = web_offering.academic_year_id
                        where center_id in ({centers}) and ((DATE(web_offering.start_date)<='{date_start}' and DATE(web_offering.end_date) >= '{date_start}') 
                        OR (DATE(web_offering.start_date)<='{date_end}' and DATE(web_offering.end_date) >= '{date_end}'))   
                        AND web_ayfy.title= "{ay_id}"'''.format(date_start=str(date_start), date_end=str(date_end), centers=centers, ay_id=ay_id)

            dict_cur.execute(query)
            offering_ids = dict_cur.fetchall()
            for id in offering_ids:
                offering = Offering.objects.get(id=id['id'])
                query = "select count(distinct(web_session.id)) as planned_sessions, count(case when web_session.status in ( 'completed') then 1 end) as online_sessions, count(case when web_session.status = 'offline' then 1 end) offline_session, count(case when web_session.status = 'cancelled' then 1 end) cancelled_sessions from web_session join web_offering on web_offering.id=web_session.offering_id where web_session.offering_id='"+str(offering.id)+"' and DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' and (teacher_id is not null or teacher_id !='')"
                dict_cur.execute(query)
                session_details = dict_cur.fetchall()
                query = "select auth_user.first_name, auth_user.last_name from web_session join web_offering on web_offering.id=web_session.offering_id join auth_user on auth_user.id=web_session.teacher_id where web_session.offering_id='"+str(offering.id)+"' and DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' and (teacher_id is not null or teacher_id !='') limit 1"
                dict_cur.execute(query)
                session_teacher = dict_cur.fetchall()
                if session_details:
                    query = "select count(distinct(student_id)) as unique_student_count, \
                            count(web_sessionattendance.is_present) as enrol_student_count, \
                            count(case when web_sessionattendance.is_present = 'yes' then 1 end) present_student_count  \
                            from web_sessionattendance join web_session on web_session.id=web_sessionattendance.session_id \
                            join web_offering on web_offering.id=web_session.offering_id \
                            join web_student on web_student.id =  web_sessionattendance.student_id\
                            where DATE(date_start)>='"+str(date_start)+"' \
                            and DATE(date_start)<='"+str(date_end)+"' \
                            and web_session.offering_id='"+str(offering.id)+"' \
                            and (teacher_id is not null or teacher_id !='') and web_student.status='Active'"
                    dict_cur.execute(query)
                    student_data = dict_cur.fetchall()
                    attendance_perc = 0
                    if student_data and student_data[0]['enrol_student_count']>0:
                        attendance_perc = str(round(((float(student_data[0]['present_student_count'])/student_data[0]['enrol_student_count'])*100 ),2))

                    teacher_name = ''
                    if session_teacher:
                        teacher_name = session_teacher[0]['last_name']
                        if session_teacher[0]['first_name']:
                            teacher_name = session_teacher[0]['first_name'] + ' ' + session_teacher[0]['last_name']
                        details = {'center_name':offering.center.name,
                                    'subject':offering.course.subject,
                                    'grade':offering.course.grade,
                                    'planned_sessions':session_details[0]['planned_sessions'],
                                    'online_sessions':session_details[0]['online_sessions'],
                                    'cancelled_sessions':session_details[0]['cancelled_sessions'],
                                    'offline_sessions': session_details[0]['offline_sessions'] if 'offline_sessions' in session_details[0]  else session_details[0]['offline_session'],
                                    'teacher':teacher_name,
                                    'total_students':student_data[0]['unique_student_count'] if student_data[0]['unique_student_count'] else offering.enrolled_students.all().count(),
                                    'enrol_students':student_data[0]['enrol_student_count'],
                                    'present_students': student_data[0]['present_student_count'],
                                    'attendance_perc':attendance_perc,
                                    }
                        table_data.append(details)
            global_data['table_data_single'] = table_data
            
        db.close()
        dict_cur.close()

        return HttpResponse(simplejson.dumps(global_data), mimetype = 'application/json')
    except Exception as e:
        print(e)
        traceback.print_exc()
        return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


def get_session_table(request):
    
    myDict = dict(request.POST.iterlists())
    data = { key.encode("utf-8").replace('[]',''):map(str, val) for key, val in myDict.items() }

    state =   data['state_id']
    partner = [int(x) for x in data['partner_id']]
    centers = [int(x) for x in data['center_id']]
    courses = [int(x) for x in data['course_id']]
    funding_partner=[int(x) for x in data['donor_id']]
    ay_id= data['ay_id'][0]
    
    date_start = datetime.datetime.strptime(data["from_date"][0] ,"%Y-%m-%d")
    date_end = datetime.datetime.strptime(data["to_date"][0] ,"%Y-%m-%d")
    
    # print "summary inputs",funding_partner,state,partner, center, date_start, date_end, ay_id

    all_centers = getAllCenters(request)

    if '-1' not in state:
        all_centers = all_centers.filter(state__in=state).distinct().order_by('name')
    if -1 not in  partner:
        all_centers = all_centers.filter(delivery_partner__in=partner).distinct().order_by('name')
    if -1 not in funding_partner:
        all_centers = all_centers.filter(funding_partner__in=funding_partner).distinct().order_by('name')
    if -1 not in centers:
        all_centers = all_centers.filter(id__in = centers)

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
    tot_user_cur = db.cursor()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    session_table = []; attnd_table = []; status_count=[];cancle_status_count=[]
    
    if all_centers:
        center_ids = [str(centerid) for centerid in all_centers.values_list('id', flat=True)]
        center_ids = ",".join(center_ids)
        
        query = "select ws.id, wco.subject, wco.board_name, wco.grade, ws.date_start, ws.date_end, au.first_name, au.last_name, wc.name, ws.status, ws.cancel_reason from web_session ws join web_offering wo on wo.id=ws.offering_id join web_course wco on wco.id=wo.course_id join web_center wc on wc.id=wo.center_id left join auth_user au on au.id=ws.teacher_id join web_ayfy ay on ay.id = wo.academic_year_id where wo.center_id in ("+center_ids+") and ay.title = '"+str(ay_id) +"' and (teacher_id is not null or teacher_id !='') and DATE(ws.date_start)>='"+str(date_start)+"' and DATE(ws.date_end)<='"+str(date_end)+"' order by ws.date_start asc"
        #and ((DATE(start_date)<='"+str(start_date)+"' and DATE(end_date) >= '"+str(start_date)+"') OR (DATE(start_date)<='"+str(end_date)+"' and DATE(end_date) >= '"+str(end_date)+"'))"

        dict_cur.execute(query)
        sessions = dict_cur.fetchall()

        
        if sessions and len(sessions)>0:
            for session in sessions:
                cancel_reason = session['cancel_reason']
                subject = str(session['board_name']) + ' ' + str(session['subject']) + ' ' + str(session['grade'])
                attendance = 0; attendance_count=0; enrolled_students=0; present_students=0
                teacher = session['first_name']
                if session['last_name']:teacher = session['first_name'] + '' + session['last_name']
                if session['first_name'] or session['last_name']:
                    query = "select count(is_present) as student_count,count(case when is_present = 'yes' then 1 end) Present from web_sessionattendance where session_id='"+str(session['id'])+"' "
                    dict_cur.execute(query)
                    attendance_count = dict_cur.fetchall()
                    if attendance_count and len(attendance_count)>0:
                        enrolled_students = attendance_count[0]['student_count']
                        present_students = attendance_count[0]['Present']
                        if attendance_count[0]['student_count']>0:attendance = (float(attendance_count[0]['Present'])/attendance_count[0]['student_count'])*100

                session_table.append({'course':subject,'starttime':str(session['date_start'].strftime("%b. %d, %Y, %I:%M %p")),'endtime':str(session['date_end'].strftime("%b. %d, %Y, %I:%M %p")),
                            'session_attendance':str(round(attendance,0)),'teacher':teacher,'center':str(session['name']),'status':session['status'], 'cancel_reason': session['cancel_reason'],
                            'total_student':enrolled_students, 'present_students':present_students})

        # import pdb;pdb.set_trace()

        if -1 not in centers:
            query = "select id, name from web_student where center_id in ("+center_ids+")"
            dict_cur.execute(query)
            students = dict_cur.fetchall() 
            if students:
                for student in students:
                    query = "select distinct(wof.id) from web_offering wof join web_session ws on wof.id=ws.offering_id join web_sessionattendance wsa on ws.id=wsa.session_id where wsa.student_id='"+str(student['id'])+"' and DATE(ws.date_start)>='"+str(date_start)+"' and DATE(ws.date_start)<='"+str(date_end)+"' and ((DATE(start_date)<='"+str(date_start)+"' and DATE(end_date) >= '"+str(date_start)+"') OR (DATE(start_date)<='"+str(date_end)+"' and DATE(end_date) >= '"+str(date_end)+"'))"
                    dict_cur.execute(query)
                    offering_ids = dict_cur.fetchall()
                    student_name = X(student['name'])
                    if offering_ids:
                        for offering_id in offering_ids:
                            offering = Offering.objects.get(id=offering_id['id'])
                            offering_name = str(offering.course.board_name) + ' ' + str(offering.course.subject) + ' ' + str(offering.course.grade)
                            query = "select count(distinct(ws.id)) as total_session from web_session ws where ws.offering_id='"+str(offering.id)+"' and DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(date_end)+"' and (teacher_id is not null or teacher_id!='') "
                            dict_cur.execute(query)
                            total_session = dict_cur.fetchall()
                            query = "select count(case when is_present = 'yes' then 1 end) as present_count, count(case when is_present = 'no' then 1 end) as absent_count from web_sessionattendance wsa join web_session ws on ws.id=wsa.session_id where wsa.student_id='"+str(student['id'])+"' and DATE(ws.date_start)>='"+str(date_start)+"' and DATE(ws.date_start)<='"+str(date_end)+"' and ws.offering_id='"+str(offering.id)+"'"
                            dict_cur.execute(query)
                            attendance_count = dict_cur.fetchall()
                            today = datetime.datetime.now()
                            change_date = date_end
                            if change_date >= today:
                                change_date = today
                            query = "select count(distinct(ws.id)) as asoftoday from web_session ws where ws.offering_id='"+str(offering.id)+"' and DATE(date_start)>='"+str(date_start)+"' and DATE(date_start)<='"+str(change_date)+"' and (teacher_id is not null or teacher_id!='') "
                            dict_cur.execute(query)
                            asoftoday = dict_cur.fetchall()
                            if asoftoday and attendance_count:
                                
                                uncap = asoftoday[0]['asoftoday'] - (attendance_count[0]['present_count'] + attendance_count[0]['absent_count'])
                                details = {'student':student_name,'course':offering_name,'present':attendance_count[0]['present_count'],
                                           'absent':attendance_count[0]['absent_count'],"asoftoday": asoftoday[0]['asoftoday'],'totalsess':total_session[0]['total_session'],'uncap':uncap,'total_student':attendance_count[0]['present_count']}
                                attnd_table.append(details)

        if -1 not in courses:
            courses = Course.objects.values_list('id', flat=True).filter(id__in=courses)
            course_ids = [str(courseid) for courseid in courses]
            course_ids = ",".join(course_ids)

            query = "select count(web_session.id) as session_cancellReason_count, cancel_reason from web_session join web_offering on web_offering.id=web_session.offering_id join web_ayfy on web_offering.academic_year_id=web_ayfy.id where DATE(web_session.date_start)>='"+str(date_start)+"'and DATE(web_session.date_end)<='"+str(date_end)+"' and web_offering.center_id in ("+str(center_ids)+") and web_offering.course_id in ("+str(course_ids)+") and (teacher_id is not null or teacher_id !='') and  web_session.cancel_reason !='' and web_ayfy.title='"+str(ay_id)+"'  group by cancel_reason"
            dict_cur.execute(query)
            cancle_status_count = dict_cur.fetchall()
            query = "select count(web_session.id) as session_status_count, web_session.status from web_session join web_offering on web_offering.id=web_session.offering_id join web_ayfy on web_offering.academic_year_id=web_ayfy.id  where DATE(web_session.date_start)>='"+str(date_start)+"' and DATE(web_session.date_end)<='"+str(date_end)+"'and web_offering.center_id in ("+str(center_ids)+") and web_offering.course_id in ("+str(course_ids)+") and  (teacher_id is not null or teacher_id !='') and web_ayfy.title='"+str(ay_id)+"'  group by web_session.status"
            dict_cur.execute(query)
            status_count = dict_cur.fetchall()
        else:
            query = "select count(web_session.id) as session_cancellReason_count, cancel_reason from web_session join web_offering on web_offering.id=web_session.offering_id join web_ayfy on web_offering.academic_year_id=web_ayfy.id where DATE(web_session.date_start)>='"+str(date_start)+"'and DATE(web_session.date_end)<='"+str(date_end)+"' and web_offering.center_id in ("+str(center_ids)+") and (teacher_id is not null or teacher_id !='') and  web_session.cancel_reason !='' and web_ayfy.title='"+str(ay_id)+"'  group by cancel_reason"
            dict_cur.execute(query)
            cancle_status_count = dict_cur.fetchall()
            query = "select count(web_session.id) as session_status_count, web_session.status from web_session join web_offering on web_offering.id=web_session.offering_id join web_ayfy on web_offering.academic_year_id=web_ayfy.id  where DATE(web_session.date_start)>='"+str(date_start)+"' and DATE(web_session.date_end)<='"+str(date_end)+"'and web_offering.center_id in ("+str(center_ids)+") and  (teacher_id is not null or teacher_id !='') and web_ayfy.title='"+str(ay_id)+"'  group by web_session.status"
            dict_cur.execute(query)
            status_count = dict_cur.fetchall()


    db.close()
    dict_cur.close()       
    return HttpResponse(simplejson.dumps({'session_table':session_table,'attnd_table':attnd_table, 'status_count':status_count, 'cancle_status_count':cancle_status_count}), mimetype = 'application/json')


def get_course_coverage(request):
    
    myDict = dict(request.POST.iterlists())
    data = { key.encode("utf-8").replace('[]',''):map(str, val) for key, val in myDict.items() }

    state =   data['state_id']
    partner = [int(x) for x in data['partner_id']]
    centers = [int(x) for x in data['center_id']]
    courses = [int(x) for x in data['course_id']]
    funding_partner=[int(x) for x in data['donor_id']]
    ay_id= data['ay_id'][0]
    
    date_start = datetime.datetime.strptime(data["from_date"][0] ,"%Y-%m-%d")
    date_end = datetime.datetime.strptime(data["to_date"][0] ,"%Y-%m-%d")
    
    # print "summary inputs",funding_partner,state,partner, center, date_start, date_end, ay_id

    all_centers = getAllCenters(request)

    if '-1' not in state:
        all_centers = all_centers.filter(state__in=state).distinct().order_by('name')
    if -1 not in  partner:
        all_centers = all_centers.filter(delivery_partner__in=partner).distinct().order_by('name')
    if -1 not in funding_partner:
        all_centers = all_centers.filter(funding_partner__in=funding_partner).distinct().order_by('name')
    if -1 not in centers:
        all_centers = all_centers.filter(id__in = centers)

    if ay_id:
        for center in all_centers:
            if center.offering_set.filter(academic_year__title=ay_id):
                pass
            else:
                all_centers.exclude(id=center.id)

    if '-1' not in state:all_centers = all_centers.filter(state__in=state).distinct().order_by('name')
    if -1 not in  partner:all_centers = all_centers.filter(delivery_partner__in=partner).distinct().order_by('name')
    if -1 not in funding_partner:all_centers = all_centers.filter(funding_partner__in=funding_partner).distinct().order_by('name')
    if -1 not in centers:all_centers = all_centers.filter(id__in = centers)
    center_ids = [str(centerid) for centerid in all_centers.values_list('id', flat=True)]
    centers = ",".join(center_ids)
    db = evd_getDB()
    dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select wco.board_name, wco.grade, wco.subject,\
                count(ws.id) as total_sessions,\
                count(case when ws.status in ('Completed', 'completed', 'Offline') then 1 end) completed_sessions_count,\
                count(case when ws.status in ('cancelled', 'scheduled') then 1 end) not_completed_sessions_count\
                from web_session ws \
                join web_offering wo on wo.id=ws.offering_id \
                join web_course wco on wco.id=wo.course_id \
                join web_center wc on wc.id=wo.center_id \
                where wc.id in ("+centers+") and ws.date_start >='"+str(date_start)+"' and ws.date_end <='"+str(date_end)+"'\
                and (teacher_id is not null or teacher_id !='') group by wco.board_name, wco.grade, wco.subject"

    dict_cur.execute(query)
    sessions = dict_cur.fetchall()
    db.close()
    dict_cur.close()
    return HttpResponse(simplejson.dumps(sessions), mimetype = 'application/json')



def nps_awards_pdf(request):
    with open('static/nps_awards_invite_2.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(),content_type='application/pdf')
        return response

def nps(request):
    with open('static/Roshni_NPS_2021.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(),content_type='application/pdf')
        return response

def duplicate_digital_school(request):
    return render_response(request, 'digitalschool _copy.html')


def roshni(request):
    return redirect('/nps')


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


class Plounge(View):

    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        self.type = self.request.GET.get('type', None)
        print(self.type)
        return render_response(self.request, 'plounge.html')

    # @method_decorator(login_required)
    # def post(self, request,  *args, **kwargs):
    #     return create_school_api(self.request)

class MobilePlounge(View):
    
    def get(self, request,  *args, **kwargs):
        pk = self.kwargs.get('pk')
        partner = get_object_or_none(Partner, id=pk)

        if partner:
            return render_response(self.request, 'plounge.html')
        return redirect('/')


class BulkUploadDigitalSchoolView(View):

    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            data = {}; isDigitalPartner=False
            if self.request.user.is_superuser: data['all_partners'] = Partner.objects.filter(status__in=['New','Approved', 'Lead'], partnertype__id=6)
            partner = get_object_or_none(Partner, contactperson=self.request.user)
            if partner:
                data['partner'] = self.request.user
                isDigitalPartner = genUtility.isDigitalPartner(partner)
            if isDigitalPartner or self.request.user.is_superuser:
                print('data: -----------', data)
                return render_response(self.request, 'bulkschoolupload.html', data)
        except Exception as e:
            print("Error reason =", e)
            print("Error at line no = ", traceback.format_exc())
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')
            
    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            return create_school_api(self.request)
        except Exception as e:
            print("Error reason =", e)
            print("Error at line no = ", traceback.format_exc())
        return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')
            


class UploadDigitalSchoolDoc(View):
    
    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            intFormat = self.request.GET.get('format', None)        # png,jpg,pdf,doc,docx,jpeg
            intDocType = self.request.GET.get('doc_type', None)     # school_logo,school_banner,student_doubt etc
            if intFormat is None or intDocType is None:
                return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')
            cloudFolderName = settings.SCHOOL_DOCUMENT_STORAGE_FOLDER
            return upload_user_document_s3(self.request, "partner", None, cloudFolderName, None,None)
        except Exception as e:
            return genUtility.getStandardErrorResponse(request, 'kMissingReqFields')
            print("Error reason =", e)
            print("Error at line no = ", traceback.format_exc())

def get_quiz_result(request):
    stud_id = request.POST.get('stud_id', '')
    offer_id = request.POST.get('offer_id', '')

    if stud_id:
        student = Student.objects.get(pk=stud_id)
        quizSet = Quiz_History.objects.filter(student_id=stud_id,offering_id=offer_id).order_by('attempt')

        data = []
        for qSet in  quizSet:
            questions = Quiz_History_Detail.objects.filter(quiz_history_id=qSet.id).count()
            correctAns = Quiz_History_Detail.objects.filter(quiz_history_id=qSet.id, result=1).count()
            cre = qSet.created_on
            date = cre.strftime("%m/%d/%Y")

            temp = {
                'attempt': qSet.attempt,
                'offer_id':qSet.offering_id,
                'date'  : date,
                'numOfQuestions': questions,
                'numOfCorrectAns': correctAns,
            }
            data.append(temp)
        return HttpResponse(simplejson.dumps({'data': data}), mimetype='application/json')
    else:
        return 'Invalid Request'




class ContentVolunteerView(View):

    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            booked_demad = Content_Demand.objects.filter(author=self.request.user).exclude(status__in=[1,8,9]).values('id', 'topic__id', 'status',
                        'topic__title', 'topic__course_id__board_name', 'topic__course_id__subject', 'topic__course_id__grade', 'content_type__id', 'content_type__name', 
                        'topic__course_id__language__name', 'subtopic__name', 'workstream__name', 'workstream_id', 'comment', 'url', 'due_date')

            published_demand = Content_Demand.objects.filter(author=self.request.user, status__in=[8,9]).values('id', 'topic__id', 'status',
                        'topic__title', 'topic__course_id__board_name', 'topic__course_id__subject', 'topic__course_id__grade', 'content_type__id', 'content_type__name', 
                        'topic__course_id__language__name', 'subtopic__name', 'workstream__name', 'due_date')

            context = {'booked_demad':simplejson.dumps(list(booked_demad), default=str), 'published_demand':simplejson.dumps(list(published_demand), default=str), 'assistance':request.user.userprofile.assistance}
            
            return render_response(request, 'content_volunteer.html', context)
        except Exception as e:
            print("Error reason =", e); print("Error at line no = ", traceback.format_exc())
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')


    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            id = requestParams.get('id', None)
            link = requestParams.get('link', None)

            Content_Demand.objects.filter(id=id).update(url=link, status=4)

            print(id, link)
            return genUtility.getSuccessApiResponse(self.request, 'Success')

        except Exception as e:
            print("Error reason =", e); print("Error at line no = ", traceback.format_exc())
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')


    @method_decorator(login_required)
    def put(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            print(requestParams)
            return genUtility.getSuccessApiResponse(self.request, 'Success')
        except Exception as e:
            print("Error reason =", e); print("Error at line no = ", traceback.format_exc())
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')



class ContentAdminView(View):

    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            admin_assigned_roles = ["TSD Panel Member","Content Reviewer","Content Admin", "Class Assistant", "vol_admin", "vol_co-ordinator", "Partner Admin"]
            roles = Role.objects.exclude(name__in=admin_assigned_roles)
            admin_assignedroles = ["Content Reviewer"]
            assign_roles = Role.objects.filter(name__in=admin_assignedroles)
            reviewers = UserProfile.objects.filter(pref_roles=19)

            booked_content = Content_Demand.objects.all().exclude(status__in=[1,8,9]).values('id', 'topic__id', 'topic__title', 'topic__course_id__board_name', 'status',
             'topic__course_id__subject', 'topic__course_id__grade', 'topic__course_id__language__name', 'subtopic__name', 'subtopic__id', 'workstream__name', 'workstream__id', 'content_type__id', 'content_type__name',
             'author__id', 'author__first_name', 'author__last_name', 'reviewer__id', 'reviewer__first_name', 'reviewer__last_name', 'comment', 'url', 'due_date').order_by('status')
            
            published_content = Content_Demand.objects.filter(status=8).values('id', 'topic__id', 'topic__title', 'topic__course_id__board_name', 'status',
             'topic__course_id__subject', 'topic__course_id__grade', 'topic__course_id__language__name', 'subtopic__name', 'subtopic__id', 'workstream__name', 'workstream__id', 'content_type__id', 'content_type__name', 
             'author__id', 'author__first_name', 'author__last_name', 'reviewer__id', 'reviewer__first_name', 'reviewer__last_name', 'comment', 'url', 'due_date').order_by('-id')
            
            host_type = ContentHostMaster.objects.all().values()
            
            # per_page = 10
            # obj_paginator = Paginator(newsdata, per_page)
            # first_page = obj_paginator.page(1).object_list
            # page_range = obj_paginator.page_range

            # content_data = {
            # 'obj_paginator':obj_paginator,
            # 'first_page':first_page,
            # 'page_range':page_range
            # }

            return render_response(request, 'content_admin.html',{'assign_roles':assign_roles, 'roles':roles, 'reviewers':reviewers, 
                'booked_content':simplejson.dumps(list(booked_content), default=str), 'published_content':simplejson.dumps(list(published_content), default=str), 'host_type':host_type})
        except Exception as e:
            print("Error reason =", e); print("Error at line no = ", traceback.format_exc())
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')

        
    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            data = requestParams.get('data', None)
            response = requestParams.get('response', None)
            is_assigned = requestParams.get('is_assigned', None)
            ids = []
            status = 1
            user = request.user
            reason = duedate = ''
            
            for element in data:
                duedatestr = element.get('duedate', None)
                duedate = None
                if duedatestr:
                    date_string = duedatestr + " 00:00:00"
                    duedate = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
                    print(duedate)
                ids.append(int(element['id']))
                demand = Content_Demand.objects.filter(id=int(element['id']))
                if response == 2 or response == 3:
                    if element['reviewer']:
                        if int(element['status']) == 4: status = 5
                        else: status = int(element['status'])
                        user = reviewer = User.objects.get(id=int(element['reviewer']))
                        demand.update(reviewer=reviewer, status=status, url=element['url'], due_date=duedate)
                    else:
                        if int(element['status']) == 2 and is_assigned: status = 3
                        else: status = int(element['status']) 
                        print('status:', status)
                        demand.update(status=status, due_date=duedate, comment=None, url=None, reviewer=None)
                        user = demand[0].author
                        
                elif response == 1:
                    user = demand[0].author
                    reason = element['comment'] if element['comment'] else ''
                    demand.update(status=1, author=None, comment=None, url=None, due_date=None, reviewer=None)
                    
                

            demands = Content_Demand.objects.filter(id__in=ids)
            updated_data = demands.values('id', 'topic__id', 'topic__title', 'topic__course_id__board_name', 'status', 'content_type__id', 'content_type__name', 
                'topic__course_id__subject', 'topic__course_id__grade', 'topic__course_id__language__name', 'subtopic__name', 'workstream__name', 'workstream__id', 
                'author__id', 'author__first_name', 'author__last_name', 'reviewer__id', 'reviewer__first_name', 'reviewer__last_name', 'comment', 'url')

            self.alert(user, demands, status, reason)
            return genUtility.getSuccessApiResponse(request, {"updated_data":list(updated_data)})
        except Exception as e:
            print("Error reason =", e); print("Error at line no = ", traceback.format_exc())
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')
        
    def alert(self, user, demands, status, reason, *args, **kwargs):
        username = user.get_full_name()
        to = [user.email]
        cc = []
        content_admins = AlertUser.objects.filter(role_id=5)
        if content_admins: cc.extend([admin.user.email for admin in content_admins])
        demand=demands[0]
        args = {'username':username, 
                'topic_name':demand.topic.title, 
                'workstream':demand.workstream.name, 
                'grade':demand.topic.course_id.grade, 
                'subject':demand.topic.course_id.subject, 
                'board':demand.topic.course_id.board_name,
                'demands':demands,
                'date': demand.due_date.strftime("%Y-%m-%d") if demand.due_date else '',
                'reason': reason if reason else ''
                }
        # choose mail template
        temp_dict1 = {1:'reject_booking.txt', 2:'book.txt', 4:'submit.txt', 5:'assign_reviewer.txt', 6:'approve.txt', 7:'resubmit.txt'}
        temp_dict2 = {3:'accept_booking_worksheet.txt', 1:'accept_booking_videos.txt', 2:'accept_booking_activities.txt', 6:'accept_booking_assesment.txt'}
        if status==3: temp = temp_dict2[demand.workstream.id]
        else: temp = temp_dict1[status]
        body_template = 'mail/content/'+ temp
        body = get_mail_content(body_template, args)
        try:
            thread.start_new_thread(genUtility.send_mail_thread, ("Your content status has changed", body, settings.DEFAULT_FROM_EMAIL, to, cc))   
        except Exception as e: print("Exception", e); traceback.print_exc()
        
        
class ContentReviwerView(View):
    
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        review_content = Content_Demand.objects.filter(reviewer=request.user, status__in=[5,6,7]).order_by('status').values('id', 'topic__id', 'topic__title', 'topic__course_id__board_name', 'status',
            'topic__course_id__subject', 'topic__course_id__grade', 'topic__course_id__language__name', 'subtopic__name', 'workstream__name', 'workstream__id', 
            'author__id', 'author__first_name', 'author__last_name', 'reviewer__id', 'reviewer__first_name', 'reviewer__last_name', 'comment', 'url' )
            
        published_content = Content_Demand.objects.filter(status=8, reviewer=request.user).order_by('-id').values('id', 'topic__id', 'topic__title', 'topic__course_id__board_name', 'status',
            'topic__course_id__subject', 'topic__course_id__grade', 'topic__course_id__language__name', 'subtopic__name', 'workstream__name', 'workstream__id', 
            'author__id', 'author__first_name', 'author__last_name', 'reviewer__id', 'reviewer__first_name', 'reviewer__last_name', 'comment', 'url')

        checklist = Content_Demand_Review_Checklist.objects.all().values()
        save_user_activity(request, 'Viewed Page: My Book - Manage Contents', 'Page Visit')
        return render_response(request,'content_reviewer.html', {"checklist":list(checklist), 'review_content':list(review_content), 'published_content':list(published_content)})
    
    


class ModifyStudentEnroll(View):

    @method_decorator(login_required)
    def get(self, request, cent_id, off_id, *args, **kwargs):
        try:
            if request.user.is_superuser or has_role(request.user.userprofile, "Center Admin") or has_role(request.user.userprofile, "Delivery co-ordinator"):
                center = Center.objects.get(id=cent_id)
                offering = genUtility.get_object_or_none(Offering, id=int(off_id))
                
                strgrades = str(offering.course.grade)
                grades = [int(x) for x in strgrades.split(',')]

                try:
                    students_master = Student.objects.filter(center_id=int(cent_id)).filter(grade__in=grades, status='Active')
                except ValueError:
                    students_master = Student.objects.filter(center_id=int(cent_id)).filter(~Q(status='Alumni'))
                
                context = {"students_enroll": offering.enrolled_students.filter(status='Active'), "students_master": students_master, "offering": offering, "center": center}
                
                return render_response(request, 'modify_enroll.html', context)
            else:
                return HttpResponse("You are not authorized to perform this action")
        except Exception as e:
            logService.logException("FtDemand GET Exception error", e.message)
            return genUtility.error_404(request, e.message)


    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            offering_id = request.POST.get('offering_id', None)
            if offering_id and request.user.is_superuser or has_role(request.user.userprofile, "Center Admin") or has_role(request.user.userprofile, "Delivery co-ordinator"):
                offering = Offering.objects.get(id=offering_id)
                orig_enroll_list = orig_enroll_list2 = []
                orig_enroll = offering.enrolled_students.all()
                for ent in orig_enroll:
                    orig_enroll_list.append(int(ent.id))

                en_count = de_count = 0
                recvenroll_list = request.POST.getlist('enrolllist1[]')
                recvdellist = request.POST.getlist('derolllist1[]')
                for i in recvenroll_list:
                    if int(i) not in orig_enroll_list:
                        student = Student.objects.get(id=i)
                        offering.enrolled_students.add(student)
                        Offering_Enrolled_Students_History.objects.create(student=student, offering=offering, assignment_status=1, created_by=request.user, updated_by=request.user)
                        en_count += 1
                offering.save()
                orig_enroll = offering.enrolled_students.all()
                for ent in orig_enroll:
                    orig_enroll_list2.append(int(ent.id))
                for stu in recvdellist:
                    if int(stu) in orig_enroll_list2:
                        student = Student.objects.get(id=stu)
                        offering.enrolled_students.remove(student)
                        Offering_Enrolled_Students_History.objects.create(student=student, offering=offering, assignment_status=2, created_by=request.user, updated_by=request.user)
                        de_count += 1
                offering.save()
                message = "Enrollment Success"
                return render_response(request, 'success.html', {"message": message})
            else:
                message = "You are not authorized to perform this action."
                return render_response(request, 'success.html', {"message": message})
        except Exception as e:
            logService.logException("FtDemand GET Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')

def onboarding_alert(request, teacher, offering):
    """send mail to onboarding teacher

    Args:
        request (request object): Django request object
        teacher (queryset): send to teacher queryset object
        offering (queryset): booked offering queryset object

    Returns:
        bool: True => mail sent successfully and False => error while sending
    """    
    try:
        teacher_subject = str(offering.course.grade)+'th '+str(offering.course.subject)
        center_name = offering.center.name
        teacher_email = teacher.email
        teacher_name = teacher.get_full_name()
        cc = []
        if offering.center.delivery_coordinator: cc.append(offering.center.delivery_coordinator.email)
        if offering.center.admin: cc.append(offering.center.admin.email)
        subject = "Welcome on-board as a teacher in "+str(center_name)
        to = [teacher_email]
        content_admins = AlertUser.objects.filter(role__name='vol_admin')
        content_admins = content_admins[0].user.all()
        if content_admins: cc.extend([user.email for user in content_admins])
        ctx = {'user':teacher_name,'center_name':center_name,'subject':teacher_subject}
        message = get_template('mail/teacher_on_board.txt').render(Context(ctx))
        msg = EmailMessage(subject, message, to=to, from_email=settings.DEFAULT_FROM_EMAIL,cc=cc)
        msg.content_subtype = 'html'
        msg.send()
        return True
    except Exception as e:
        logService.logException("FtDemand GET Exception error", e.message)
        return False


class ManageBooking(View):
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            panel_member_list = {}
            
            panel_members_obj = UserProfile.objects.filter(role__in=[7,17])
            tsd_outcome_list = ['Scheduled', 'Assigned', 'Completed', 'Cancelled']
            cancel_reasons = ['Online on mobile', 'Skype issue', 'No show from volunteer', 'Duplicate booking', 'Existing RFT',
                            'Infra issue', 'Panel missed, rebook', 'Personal Reasons', 'Others']

            for panel_member in panel_members_obj:
                panel_member_list[panel_member.id] = {'name': panel_member.user.get_full_name(), 'id':panel_member.user.id}
    
            save_user_activity(request, 'Viewed Page:Manage TSD- Manage Booking', 'Page Visit')

            return render_response(request, 'manage_booking.html', {'panel_member_list': panel_member_list,'tsd_outcome_list': tsd_outcome_list, 'cancel_reasons': cancel_reasons})
            
        except Exception as e:
            logService.logException("mb GET Exception error", e.message)
            return genUtility.error_404(request, e.message)


    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            limit = request.POST.get('limit', None)
            if limit=='0': limit = None
            slots = SelectionDiscussionSlot.objects.filter(status="Booked").values('id', 'userp__user__id', 'userp__user__first_name', 'userp__user__last_name',
            'userp__user__email', 'userp__user__username', 'userp__city', 'userp__state', 'userp__phone', 'role__name', 'tsd_panel_member__user__first_name', 'tsd_panel_member__user__last_name',
            'outcome', 'booked_date', 'start_time', 'end_time').order_by('-start_time')[0:limit] 
            return genUtility.getSuccessApiResponse(request, {"data":simplejson.dumps(list(slots), default=str)})  
        except Exception as e:
            logService.logException("mb POST Exception error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')
        
    
    @method_decorator(login_required)
    def put(self, request,  *args, **kwargs):
        try:
            data = simplejson.loads(request.body)
            slot = data.get("slot_id", None)
            tsd_outcome = data.get("tsd_outcome", None)
            tsd_member = data.get("tsd_member", None)
            cancel_reason = data.get("cancel_reason", None)
            slot_obj = SelectionDiscussionSlot.objects.get(id=slot)
            slot_obj.outcome = tsd_outcome
            slot_obj.tsd_panel_member_id = tsd_member
            slot_obj.save()
            UserProfile.objects.filter(id=slot_obj.userp_id).update(dicussion_outcome = tsd_outcome)
            if tsd_outcome == 'Completed' and slot_obj.role_id == 3:
                rolepreference_id= RolePreference.objects.get(userprofile_id=slot_obj.userp_id ,role_id=3)
                OnboardingStepStatus.objects.filter(role_preference_id=rolepreference_id.id,step_id=12).update(status=1)
                
            if tsd_outcome == 'Completed' and slot_obj.role_id == 20:
                rolepreference_id= RolePreference.objects.get(userprofile_id=slot_obj.userp_id ,role_id=20)
                OnboardingStepStatus.objects.filter(role_preference_id=rolepreference_id.id,step_id=13).update(status=1)

            if tsd_outcome == 'Cancelled':
                try:
                    history_obj = SelectionDiscussionSlotHistory.objects.filter(slot_id=slot_obj, userp=slot_obj.userp).latest(
                        "booked_date")
                    history_obj.status = 'Admin Released'
                    history_obj.released_date = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
                    history_obj.reason_to_release = cancel_reason
                    history_obj.save()
                except:
                    pass

            if tsd_member and tsd_outcome in ['Scheduled', 'Assigned']:
                volunteer_userp = slot_obj.userp
                panelmember_firstname = slot_obj.tsd_panel_member.user.first_name
                panelmember_lastname = slot_obj.tsd_panel_member.user.last_name
                slot_time = slot_obj.start_time
                recipients = slot_obj.tsd_panel_member.user.email
                userid = request.user.id

                template_dir = '_panel_assign'
                args = {'userp': volunteer_userp, 'first_name': panelmember_firstname, \
                        'lastname': panelmember_lastname, 'slot': slot_time}
                subject_template = 'mail/%s/short.txt' % template_dir
                subject = get_mail_content(subject_template, args).replace('\n', '')

                body_template_html = 'mail/%s/fullhtml.html' % template_dir
                body_html = get_mail_content(body_template_html, args)

                insert_into_alerts(subject, body_html, recipients, userid, 'email')
            slots = SelectionDiscussionSlot.objects.filter(id=slot).values('id', 'userp__user__id', 'userp__user__first_name', 'userp__user__last_name',
            'userp__user__email', 'userp__user__username', 'userp__city', 'userp__state', 'userp__phone', 'role__name', 'tsd_panel_member__user__first_name', 'tsd_panel_member__user__last_name',
            'outcome', 'booked_date', 'start_time', 'end_time').order_by('-start_time')
            return genUtility.getSuccessApiResponse(request, {"data":simplejson.dumps(list(slots), default=str)})
        except Exception as e:
            logService.logException("mb PUT error", e.message)
            return genUtility.getStandardErrorResponse(request, 'kUnauthorisedAction')