# Create your views here.

import calendar
import json
import operator
import simplejson
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.db.models import Q
from datetime import datetime
from web.models import *
from web.views import *
from models import FcmKey
from models import StudentFcmKey
from rest_authentication.views import get_user_info
from .api_utils import get_timezone_now
from collections import OrderedDict
from django.contrib.auth.models import User
from models import *
from web.exotel.sendansms import *
import os
import base64
from os import path
import requests

def return_response(data, content_type='application/json'):
    return HttpResponse(simplejson.dumps(data), content_type=content_type)


@csrf_exempt
def authenticate_user(request):
    data = {'status': 'fail'}
    username = request.POST.get('username')
    passwd = request.POST.get('password')
    if not username or not passwd:
        return return_response(data)

    user = authenticate(username=username, password=passwd)
    if user and user.is_authenticated():
        login(request, user)
        userp = user.userprofile
        session_key = request.session._get_session_key()
        if session_key:
            data['status'] = 'success'
            data['session_key'] = session_key
            if user.is_superuser:
               data['role'] = 'Super Admin'
            elif has_role(userp,'Center Admin'):
               data['role'] = 'Center Admin'
            elif has_role(userp,'Teacher'):
               data['role'] = 'Teacher'
            elif has_role(userp, "Class Assistant"):
               data['role'] = "Class Assistant"
            elif has_role(userp, "Content Admin"):
               data['role'] = 'Content Admin'
            elif has_role(userp, "Well Wisher"):
               data['role']  =  "Well Wisher"
            else:
               data['role'] = 'Unassigned'
    return return_response(data)

def make_hour_re(time):
    time_lst = time.split(':')
    hour = int(time_lst[0])
    minuts = time_lst[1]
    if hour >= 12 and hour <=23:
        if hour > 12:
            hour = hour - 12
        hour = str(hour) +' : '+str(minuts) + " PM"
    else:
        hour = str(hour) +' : '+str(minuts) + " AM"

    return hour


@login_required
def get_user_sessions(request):
    sess_response = {"status": 0, "message": "", "data": {}, "total": 0, "next_page": 0}
    next_page   = request.POST.get('next_page', 0)
    per_page    = request.POST.get('per_page', 10)
    res_status  = request.POST.get('status', '').strip()

    status_to_db = {"teaching": "started"}
    db_to_status = dict((v,k) for k,v in status_to_db.iteritems())
    if res_status:
        res_status = status_to_db.get(res_status, res_status)

    search_status = ["prefered", "scheduled", "started", "completed", "cancelled"]
    if res_status:
        search_status = [i.strip().lower() for i in res_status.split(',') if i]

    if not isinstance(next_page, int):
        if next_page.isdigit():
            next_page = int(next_page)
        else:
            next_page = 0

    if not isinstance(per_page, int):
        if per_page.isdigit():
            per_page = int(per_page)
        else:
            per_page = 10

    limit_query = ""
    if per_page != -1:
        offset_value = next_page * per_page
        limit_query = "LIMIT {},{}".format(offset_value, per_page)

    data = sess_response["data"]

    conn        = MySQLdb.connect(host=settings.DATABASES['default']['HOST'] or "localhost",
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    dict_cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    base_query = "SELECT S.id as session_id, S.status, CO.grade, CO.subject, T.title as topic, "
    base_query += "WOF.language, CO.board_name, S.date_start, S.date_end, "
    base_query += "CONCAT(U.first_name, ' ', U.last_name) as teacher, C.name as center, C.state, "
    base_query += "C.district, C.village, C.photo as center_image, S.teacher_id,S.offering_id, "
    base_query += "WOF.center_id, WOF.course_id, T.id as topic_id FROM web_session S "
    base_query += "LEFT JOIN auth_user U ON S.teacher_id = U.id "
    base_query += "LEFT JOIN web_offering WOF ON S.offering_id = WOF.id "
    base_query += "LEFT JOIN web_center C ON WOF.center_id = C.id "
    base_query += "LEFT JOIN web_course CO ON WOF.course_id = CO.id "
    base_query += "LEFT JOIN web_session_planned_topics ST On S.id = ST.session_id "
    base_query += "LEFT JOIN web_topic T ON ST.topic_id = T.id WHERE"

    pref_query = "SELECT D.id as demand_id, CO.grade, CO.subject, WOF.language, CO.board_name, "
    pref_query += "D.day, D.start_time, D.end_time, CONCAT(U.first_name, ' ', U.last_name) as teacher, "
    pref_query += "C.name as center, C.state, C.district, C.village, C.photo as center_image, "
    pref_query += "D.user_id as teacher_id, D.offering_id, WOF.center_id, WOF.course_id FROM web_demandslot D "
    pref_query += "LEFT JOIN auth_user U ON D.user_id = U.id "
    pref_query += "LEFT JOIN web_offering WOF ON D.offering_id = WOF.id "
    pref_query += "LEFT JOIN web_center C ON WOF.center_id = C.id "
    pref_query += "LEFT JOIN web_course CO ON WOF.course_id = CO.id WHERE"

    user       = request.user
    user_roles = [i.name for i in user.userprofile.role.all()]
    if not user_roles:
        user_roles = ["Teacher"]

    center_ids = []
    role_query = []
    if user.is_superuser or "Center Admin" in user_roles or "Class Assistant" in user_roles:
        centers = []
        if user.is_superuser:
            centers = Center.objects.filter(status='Active').values_list("id")
        elif "Center Admin" in user_roles:
            centers = Center.objects.filter(admin=user, status='Active').values_list("id")
        else:
            centers = Center.objects.filter(assistant=user, status='Active').values_list("id")

        for center in centers:
            if center:
                center_ids.append(str(center[0]))

        role_query.append("C.id in ({})".format(",".join(center_ids[:5])))

    datetime_fields = ["date_start", "date_end"]
    date_fields     = ["start_time", "end_time"]
    for s_status in search_status:
        condition_query = []
        or_query = []
        query = [base_query]
        if s_status == 'prefered':
            query = [pref_query]
            order_by = "ORDER BY D.id desc"
            if role_query:
                or_query.append("D.user_id = {}".format(int(user.id)))
                or_query.extend(role_query)
            else:
                condition_query.append("D.user_id = {}".format(int(user.id)))
        else:
            order_by = "ORDER BY S.date_start desc"
            if "Teacher" in user_roles and role_query:
                or_query.append("S.teacher_id = {}".format(int(user.id)))
                or_query.extend(role_query)
            elif role_query:
                condition_query.extend(role_query)
            else:
                condition_query.append("S.teacher_id = {}".format(int(user.id)))

            condition_query.append("S.status = \"{}\"".format(s_status))
            if s_status == "scheduled":
                condition_query.append("S.date_start > NOW()")
                order_by = "ORDER BY S.date_start asc"

        if or_query:
            new_cond_query = "({})".format(" OR ".join(or_query))
            condition_query.append(new_cond_query)

        condition_query = " AND ".join(condition_query)
        query.append(condition_query)
        query.append(order_by)
        if limit_query:
            query.append(limit_query)

        query = " ".join(query)
        dict_cursor.execute(query)
        status_data = dict_cursor.fetchall()
        sess_response["total"] += len(status_data)
        final_data = data.setdefault(db_to_status.get(s_status, s_status), [])
        for _data in status_data:
            if s_status == 'prefered':
                _data["status"] = s_status
            for date_field in datetime_fields:
                if _data.has_key(date_field):
                    value = _data[date_field]
                    _data[date_field] = value.strftime("%d-%m-%Y %H:%M:%S")

            for date_field in date_fields:
                if _data.has_key(date_field):
                    value = _data[date_field]
                    if value:
                        value = "{}:{}".format(value.seconds // 3600, value.seconds // 60 % 60)
                        value = datetime.datetime.strptime(value, "%H:%M").strftime("%H:%M")
                        _data[date_field] = value

            center_image = _data.get("center_image", "")
            if center_image and not center_image.startswith("http://"):
                _data["center_image"] = 'http://'+ request.META['HTTP_HOST'] + "/" + str(center_image)

            final_data.append(_data)

    if sess_response["total"] < per_page:
        sess_response['next_page'] = 0
    else:
        sess_response['next_page'] = next_page + 1

    return return_response(sess_response)


@csrf_exempt
def get_upcom_sess(request):
     user = request.user
     userp = user.userprofile
     time_now =(datetime.datetime.utcnow()+datetime.timedelta(hours=5, minutes=0))
     max_results = 20
     post_results = request.POST.get('max_results')
     if post_results:
         max_results = int(post_results)
     page_number = 0
     post_page = request.POST.get('page_number')
     if post_page:
         page_number = int(post_page)
     start_index = page_number * max_results
     end_index = start_index + max_results
     res_status = request.POST.get('status', '')
     data = {'status':'fail'}
     if user.is_superuser:
        data = {}
        centers = Center.objects.filter(status='Active')
        #session_list = []
        session_list = Session.objects.none()
        sess_count = 0
        for ent in centers:
            center_offerings = Offering.objects.filter(center=ent).filter(status='Running')
            for ent1 in center_offerings:
                if res_status:
                    offer_sess = ent1.session_set.filter(date_end__gte = time_now, status = res_status).order_by('date_start')
                else:
                    offer_sess = ent1.session_set.filter(date_end__gte = time_now).order_by('date_start')
                sess_count += offer_sess.count()
                #session_list.extend(list(offer_sess))
                session_list = session_list | offer_sess
        #session_list.order_by('date_start')
        #session_list.sort()
        data['role'] = 'Super Admin'
        construct_data(session_list,data,start_index,end_index,page_number,sess_count)
     elif has_role(userp,'Center Admin'):
        data = {}
        centers = Center.objects.filter(admin=user).filter(status='Active')
        #session_list = []
        session_list = Session.objects.none()
        sess_count = 0
        for ent in centers:
            center_offerings = Offering.objects.filter(center=ent).filter(status='Running')
            for ent1 in center_offerings:
                if res_status:
                    offer_sess = ent1.session_set.filter(date_end__gte = time_now, status = res_status).order_by('date_start')
                else:
                    offer_sess = ent1.session_set.filter(date_end__gte = time_now).order_by('date_start')
                sess_count += offer_sess.count()
                #session_list.extend(list(offer_sess))
                session_list = session_list | offer_sess
                session_list.order_by('date_start')
        #print session_list
        #import pdb;pdb.set_trace()
        data['role'] = 'Center Admin'
        construct_data(session_list,data,start_index,end_index,page_number,sess_count)
     elif has_role(userp,'Class Assistant'):
        data = {}
        centers = Center.objects.filter(assistant = user)
        #session_list = []
        session_list = Session.objects.none()
        sess_count = 0
        for ent in centers:
            center_offerings = Offering.objects.filter(center=ent).filter(status='Running')
            for ent1 in center_offerings:
                if res_status:
                    offer_sess = ent1.session_set.filter(date_end__gte = time_now, status = res_status).order_by('date_start')
                else:
                    offer_sess = ent1.session_set.filter(date_end__gte = time_now).order_by('date_start')
                sess_count += offer_sess.count()
                #session_list.extend(list(offer_sess))
                session_list = session_list | offer_sess
                session_list.order_by('date_start')
        #print session_list
        #import pdb;pdb.set_trace()
        data['role'] = 'Class Assistant'
        construct_data(session_list,data,start_index,end_index,page_number,sess_count)
     elif has_role(userp,'Teacher') :
        data={}
        if res_status:
            user_sessions = Session.objects.filter(teacher = user).filter(status = res_status)
            if res_status.lower() == 'scheduled':
                user_sessions = user_sessions.order_by('date_start')
            else:
                user_sessions = user_sessions.order_by('-date_start')
        else:
            user_sessions = Session.objects.filter(teacher = user).filter(date_end__gte = time_now).order_by('date_start') 
        count = user_sessions.count()
        data['role'] = 'Teacher'
        construct_data(user_sessions,data,start_index,end_index,page_number,count)
     else:
        data = {'next_page':0,'total':0,'role':'Undefined','results':[]}
     return return_response(data)


def construct_data(user_sessions,data,start_index,end_index,page_number,count):
    data['next_page'] = 0
    if end_index < count:
       data['next_page'] = page_number + 1
    data['results'] = []

    counter = 0
    usersess = list(user_sessions[start_index:end_index])
    for ent in usersess:
        counter += 1
        temp = {}
        start_date_time = (ent.date_start).strftime('%d/%m/%Y::%H:%M').split('::')
        temp['time'] = make_hour_re(start_date_time[1])
        temp['date'] = start_date_time[0]
        topic = ent.planned_topics.all()
        if topic:
            topic = str(topic[0].title)
        else:
            topic = 'Unassigned Topic'
        temp['topic']= topic
        offer = ent.offering
        center_image = ''
        if offer.center.photo:
            center_image = 'http://www.evidyaloka.org/' + str(offer.center.photo)
        temp['grade'] = str(make_number_verb(offer.course.grade))+' class'
        temp['subject'] = str(offer.course.subject)
        temp['center'] = str(offer.center.name)
        temp['center_image'] = center_image
        temp['status'] = str(ent.status)
        temp['id']=ent.id
        teacher = ent.teacher
        temp['teacher'] = str(teacher.first_name) +' ' +str(teacher.last_name)
        data['results'].append(temp)
    data['total'] = counter


@csrf_exempt
def save_session_status(request):
    #print "*** save_session_status **** \n", request.POST
    data = {'status': 'fail'}
    try:
        sess_id = request.POST.get('session_id')
        status = request.POST.get('status')
        attendance = request.POST.get('attended_students', [])
        comment = request.POST.get('comment', '')
        topic = request.POST.get('topic_id', '')

        reason = ""
        if status.lower() == "cancelled":
            reason = request.POST.get('reason', 'No reason provided')

        if attendance != "" and status.lower() != "cancelled":
            for student in attendance[1:-1].split(","):
                student = student.strip()
                try:
                    student_attendance = SessionAttendance.objects.get(session=sess_id, student=student)
                except SessionAttendance.DoesNotExist as exp:
                    db_student = Student.objects.get(id=student)
                    db_session = Session.objects.get(id=sess_id)
                    SessionAttendance.objects.create(session=db_session, student=db_student, is_present='yes')
                except SessionAttendance.MultipleObjectsFound:
                    pass
                else:
                    student_attendance.is_present = 'yes'
                    student_attendance.save()

        if sess_id and status:
            try:
                session = Session.objects.get(id=sess_id)
                session.status = status
                session.comments = comment
                if reason != "":
                    session.cancel_reason = reason
                if topic != "":
                    db_topic = Topic.objects.get(id=topic)
                    session.actual_topics = [db_topic]
                session.save()
                data['status']= 'success'
            except ObjectDoesNotExist:
                pass
    except Exception as exp:
        print "*** save_session_status \n", exp
    return return_response(data)


def fcm_update(request):
    user    = request.user
    if user:
        user_id = request.user.id
    else:
        user_id = ''

    old_key = request.POST.get('old_key', '')
    new_key = request.POST.get('new_key', '')
    try:
        obj = FcmKey.objects.get(fcm_key=old_key)
        obj.fcm_key = new_key
        obj.user_id = user_id
        obj.save()
    except FcmKey.DoesNotExist:
        try:
            obj = FcmKey.objects.get(fcm_key=new_key)
            obj.user_id = user_id
            obj.save()
        except FcmKey.DoesNotExist:
            obj=FcmKey(user_id=user_id, fcm_key=new_key)
            obj.save()
    data = {}
    data['status'] = 0
    data['message'] = 'success'
    return return_response(data)

@login_required
def get_user_meta(request):
    user = request.user
    data = get_user_info(user)
    data['ref_channel_name'] = ""
    data['available_ref_channels'] = []
    ref_list = [each.upper() for each in ReferenceChannel.objects.values_list("name", flat=True).filter(~Q(name = ""), ~Q(partner_id = None)).order_by("name").distinct()]
    data['available_ref_channels'] = ref_list
    ref_channel_id = UserProfile.objects.filter(user_id=user.id).values_list('referencechannel_id', flat=True)
    if len(ref_channel_id) > 0:
        data['ref_channel_name'] = (ReferenceChannel.objects.get(id=ref_channel_id[0])).name

    response_data = {'message': '', 'status': 0, 'data': data}
    return return_response(response_data)


@login_required
def get_avalilable_tsd_slots(request):
    selected_year  = request.GET.get("year", "")
    selected_month = request.GET.get("month", "")
    response_data = {"status": 0, "message": "", "data": {}}

    #Check if selected year and month are valid
    selected_date = None
    if selected_year and selected_month:
        try:
            selected_year  = int(selected_year)
            selected_month = int(selected_month)
        except ValueError:
            response_data["status"] = 1
            response_data["message"] = "Year and Month should be intergers, requested values are "
            response_data["message"] += "Year: {}, Month: {}".format(selected_year, selected_month)
            return return_response(response_data)

        try:
            selected_date = datetime.datetime(selected_year, selected_month, 01)
        except ValueError as e:
            response_data["status"] = 1
            response_data["message"] = "{}, requested values are ".format(e.message)
            response_data["message"] += "Year: {}, Month: {}".format(selected_year, selected_month)
            return return_response(response_data)

    #Getting Current time in Indian Timezone 'Asia/Kolkata'
    today = get_timezone_now('Asia/Kolkata')

    query = Q(userp=None)
    if selected_date:
        query = query & Q(start_time__gte=today, start_time__month=selected_date.month)
        query = query & Q(start_time__year=selected_date.year)
    else:
        query = query & Q(start_time__gte=today, start_time__month=today.month, start_time__year=today.year)

    available_slots = SelectionDiscussionSlot.objects.filter(query).order_by('start_time') 
    if not available_slots:
        return return_response(response_data)

    booked_slots = {}
    _data = response_data["data"]
    slots_data = _data.setdefault("available_slots", {})
    for available_slot in available_slots:
        start_time = available_slot.start_time
        day_data = slots_data.setdefault("%02d" % start_time.day, {})
        start_time_str = start_time.strftime("%I:%M %p")
        end_time_str = available_slot.end_time.strftime("%I:%M %p")
        day_data.update({available_slot.id: "{} to {}".format(start_time_str, end_time_str)})
        _data['year']  = start_time.year
        _data['month'] = start_time.month

    query = Q(userp=request.user.userprofile) & ~Q(outcome = "Cancelled")
    current_slot_objs = SelectionDiscussionSlot.objects.filter(query)
    for current_slot_obj in current_slot_objs:
        role_obj = current_slot_obj.role
        start_time = current_slot_obj.start_time.strftime("%B %d %Y, From %I:%M %p")
        end_time   = current_slot_obj.end_time.strftime("%I:%M %p")
        booked_time = "{} to {}".format(start_time, end_time)
        slot_info = {"role_id": role_obj.id, "role": role_obj.name, "booked_time": booked_time}
        booked_slots[current_slot_obj.id] =  slot_info
    _data["booked_slots"] = booked_slots

    return return_response(response_data)


@login_required
def save_selfevalinfo(request):
    se_form  = request.POST.get('form_dump', '')
    role_ids = request.POST.get('roles', '')
    response_data = {"status": 0, "message": "", "data": {}}

    try:
        role_ids = [i for i in role_ids.split(",") if i]
    except ValueError:
        response_data["status"] = 1
        response_data["message"] = "Roles should be interger values, requested values are {}".format(role_ids)
        return return_response(response_data)
    else:
        if not role_ids:
           response_data["status"] = 1
           response_data["message"] = "Roles are manditory to Save Self Eval Info."
           return return_response(response_data)

    userprofile = request.user.userprofile
    rolepref_objects = RolePreference.objects.filter(userprofile=userprofile, role__id__in=role_ids)
    if not rolepref_objects:
       response_data["status"] = 1
       response_data["message"] = "Role Ids are not valid."
       return return_response(response_data)

    #Getting Current time in Indian Timezone 'Asia/Kolkata'
    ist_today = get_timezone_now('Asia/Kolkata')
    for rolepref_obj in rolepref_objects:
        se, created = SelfEvaluation.objects.get_or_create(userp=userprofile, role_preference=rolepref_obj)
        se.se_form  = se_form
        if created:
            se.date_submited = ist_today
        se.save()

        try:
            se_step = rolepref_obj.onboardingstepstatus_set.get(step__stepname = "Self Evaluation", status=False)
            se_step.status = True
            se_step.date_completed = ist_today 
            se_step.save()
        except OnboardingStepStatus.DoesNotExist:
            continue

    return return_response(response_data)

@csrf_exempt
def send_mail_api(request):
    response_data = {"status": 0, "message": "", "data": {}}
    email  = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    try:
        to = ['sumukh.bharadwaj@evidyaloka.org']
        #to = ['taukir@trisysit.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        ctx = {'phone':phone,'email':email}
        message = "<p>Dear Sumukh,</p><p>E-Mail : %s</p><p>Phone : %s</p><br><br><p>Best Regards</p>" %(email,phone)
        msg = EmailMessage('Enrolled for eNFLUENCER', message, to = to, from_email = from_email)
        msg.content_subtype = 'html'
        msg.send()
        response_data["status"] = 1
        response_data["message"] = "Enrolled Successfully"
    except :
        response_data["status"] = 0
        response_data["message"] = "Error"
    return return_response(response_data)
    

@csrf_exempt
def student_search(request):
    phone_num = request.GET.get('phone', '')
    if phone_num == "" or len(phone_num) < 3:
        resp = {"error" : {"status": 404, "message": "Invalid search"}}
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

    students = Student.objects.filter(Q(phone__icontains=phone_num)).order_by("name").values('id', 'name', 'grade', 'gender', 'activation')

    if len(students) < 1:
        resp = {"error": {"status": 404, "message": "Phone number not found"}}
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

    resp = {
        "metadata": {
            "resultset": {
                "count": len(students)
            }
        },
        "results": []
    }

    for each in students:
        id = each['id']
        name = each['name']
        grade = each['grade']
        gender = each['gender']
        activation = each['activation']
        
        student = OrderedDict()
        student["id"] = id
        student["name"] = name.strip()
        student["grade"] = grade
        student["gender"] = gender
        student["activation"] = activation
        #print "student",student
        resp["results"].append(student)

    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


@csrf_exempt
def student_activation(request):
    if request.method == 'GET':
        resp = {"error": {"status": 404, "message": "Unexpected HTTP GET request"}}
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

    student_id = request.POST.get('student', '')

    db_student = None
    try:
        db_student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        db_student = None

    if db_student is None:
        resp = {"error" : {"status": 404, "message": "Student id not found"}}
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

    status = str(request.POST.get('status', ''))
    status = False if status == "0" else True
    Student.objects.filter(id=student_id).update(activation = True)

    resp = {"status": "success"}
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


@csrf_exempt
def student_session(request):
    student_id = request.GET.get('student', '')
    limit = str(request.GET.get('limit', '5'))

    student = None
    try:
        student = Student.objects.get(id=student_id)
    except Exception as exp:
        resp = {"error": {"status": 404, "message": "Student id not found"}}
    else:
        if student.status == 'Active' and student.activation:
            student_center = student.center_id
            photo_path = str((Center.objects.get(id=student_center)).photo)
            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                                 user=settings.DATABASES['default']['USER'],
                                 passwd=settings.DATABASES['default']['PASSWORD'],
                                 db=settings.DATABASES['default']['NAME'],
                                 charset="utf8",
                                 use_unicode=True)

            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query = "SELECT DISTINCT offering_id from web_offering_enrolled_students INNER JOIN web_offering ON web_offering.id=web_offering_enrolled_students.offering_id WHERE student_id= '{}' AND web_offering.status='running' AND web_offering.active_teacher_id is not null".format(
                str(student_id))
            dict_cur.execute(query)

            offers_list = [str(each['offering_id']) for each in dict_cur.fetchall()]
            if len(offers_list) > 0:
                offers_list.sort()
                offering_id = "(" + ",".join(offers_list) + ")"
                today = datetime.datetime.now()
                query = "SELECT web_session.id AS sessionid, CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS name, web_session.teacher_id, web_course.grade, web_course.subject, web_session.ts_link, web_session.date_start FROM web_session INNER JOIN web_offering ON web_offering.id=web_session.offering_id INNER JOIN web_course ON web_course.id=web_offering.course_id INNER JOIN auth_user ON web_session.teacher_id=auth_user.id  WHERE offering_id IN " + offering_id + " AND web_session.date_start >= '" + datetime.datetime.strftime(
                    today, "%Y-%m-%d %H:%M:%S") + "' ORDER BY web_session.date_start ASC"
                dict_cur.execute(query)
                session_details = dict_cur.fetchall()

                resp = {
                    "metadata": {
                        "resultset": {
                            "count": len(session_details)
                        }
                    },
                    "results": []
                }

                for each in session_details:
                    session_id = each['sessionid']
                    query = "select web_topic.title FROM web_session INNER JOIN web_session_planned_topics ON web_session.id=web_session_planned_topics.session_id INNER JOIN web_topic ON web_topic.id=web_session_planned_topics.topic_id where web_session.id=" + str(
                        session_id) + ""

                    dict_cur.execute(query)
                    session_det = dict_cur.fetchall()

                    session = OrderedDict()
                    session["id"] = each['sessionid']
                    session["teacher_id"] = each['teacher_id']
                    session["name"] = each['name']
                    session["grade"] = each['grade']
                    session["subject"] = each['subject']
                    session["ts_link"] = each['ts_link']
                    if session_det:
                        session['title'] = session_det[0]['title']
                    else:
                        session['title'] = "NA"
                    session['date_start'] = str(each['date_start'])
                    session['school_photo'] = photo_path
                    resp["results"].append(session)

                dict_cur.close()
                db.close()
            else:
                resp = {"error": {"status": 404, "message": "No upcoming sessions found for student"}}
        else:
            resp = {"error": {"status": 404, "message": "Student is not Active" if student.status != "Active" else "OTP activation is not completed for student"}}

    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


@csrf_exempt
def reference_channel(request):
    partner_details_json = []
    ref_data = ReferenceChannel.objects.values("id","name").filter(~Q(name = ""),~Q(partner_id =None)).order_by("name").distinct()
    for data in ref_data:
        # if data['name'] == "77":
        #     continue
        partner_details_json.append(data)
    
    return HttpResponse(simplejson.dumps({'data': partner_details_json}), mimetype='application/json')


@csrf_exempt
def student_fcm_update(request):

    student = request.POST.get('student', '')
    device =  request.POST.get('device_id', None)
    fcm_token =  request.POST.get('fcm_token', None)

    resp = {"status": "success"}

    student_fcm_key = StudentFcmKey.objects.filter(fcm_key=fcm_token)

    if student_fcm_key:
        student_fcm_key.update(student_id=student, device_id=device)
    else:
        StudentFcmKey.objects.create(student_id=student, device_id=device, fcm_key=fcm_token)

    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


@csrf_exempt
def send_otp(request):
    try:
        auth_key = settings.SMS_AUTHENTICATION_KEY
        template_id = settings.TEMPLATE_ID
        if request.method == 'GET':
            # required parameters
            phone = request.GET.get('phone', '')
            extra_params = {"Param1":"Value1"}
            if not phone:
                resp = {"data" : {"message" : "Required parameters not sent."}}
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

            if len(str(phone)) > 10 or len(str(phone)) < 10 :
                resp = {"data" : {"message" : "Invalid phone number."}}
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

            phone = '91' + str(phone)
            print "phone = ", phone
            url = "https://api.msg91.com/api/v5/otp?authkey={}&template_id={}&extra_param={}&mobile={}".format(auth_key, template_id, simplejson.dumps(extra_params), phone)
            # print "------------------------------------", url
            resp = requests.get(url)
            response = resp.json()
            return HttpResponse(simplejson.dumps(response), mimetype='application/json')
        elif request.method == 'POST':
            base_url = "https://api.msg91.com/api/v5/otp"
            is_resend = request.POST.get('is_resend', '')
            phone = request.POST.get('phone', '')

            # Validation
            if not phone:
                resp = {"data" : {"message" : "Required parameters not sent."}}
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

            if len(str(phone)) > 10 or len(str(phone)) < 10 :
                resp = {"data" : {"message" : "Invalid phone number."}}
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            
            phone = '91' + str(phone)
            
            # API for resend otp 
            if is_resend == 1 or is_resend == '1':
                base_url += "/retry?mobile={}&authkey={}".format(phone, auth_key)
                print "base url = ", base_url
                payload = {
                    "mobile" : phone,
                    "authkey" : auth_key
                }

                resp = requests.post(base_url, data=payload)
                response = resp.json()
                return HttpResponse(simplejson.dumps(response), mimetype='application/json')
            elif is_resend == 0 or is_resend == '0':
                # API for verify otp
                otp = request.POST.get('otp', '')
                
                # Validation
                if not otp:
                    resp = {"data" : {"message" : "Required parameters not sent."}}
                    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

                base_url += "/verify?mobile={}&otp={}&authkey={}".format(phone, otp, auth_key)
                # print "url ------", base_url
                payload = {
                    "mobile" : phone,
                    "otp" : otp,
                    "authkey" : auth_key
                }

                resp = requests.post(base_url, data=payload)
                response = resp.json()
                return HttpResponse(simplejson.dumps(response), mimetype='application/json')
            else:
                resp = {"data" : {"message" : "Invalid request."}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()

"""
    From here newly added duplicate functions are started.
    Before adding anything below please contact to Amit Kumar Pradhan
"""

@login_required
def get_user_sessions_duplicate(request):
    sess_response = {"status": 0, "message": "", "data": {}, "total": 0, "next_page": 0}
    next_page   = request.POST.get('next_page', 0)
    per_page    = request.POST.get('per_page', 10)
    res_status  = request.POST.get('status', '').strip()
    status_to_db = {"teaching": "started"}
    db_to_status = dict((v,k) for k,v in status_to_db.iteritems())
    if res_status:
        res_status = status_to_db.get(res_status, res_status)
    search_status = ["prefered", "scheduled", "started", "completed", "cancelled"]
    if res_status:
        search_status = [i.strip().lower() for i in res_status.split(',') if i]
    if not isinstance(next_page, int):
        if next_page.isdigit():
            next_page = int(next_page)
        else:
            next_page = 0
    if not isinstance(per_page, int):
        if per_page.isdigit():
            per_page = int(per_page)
        else:
            per_page = 10
    limit_query = ""
    if per_page != -1:
        offset_value = next_page * per_page
        limit_query = "LIMIT {},{}".format(offset_value, per_page)
    data = sess_response["data"]
    conn        = MySQLdb.connect(host=settings.DATABASES['default']['HOST'] or "localhost",
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    dict_cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    base_query = "SELECT S.id as session_id, S.status, S.video_link, S.mode, CO.grade, CO.subject, T.title as topic, "
    base_query += "WOF.language, CO.board_name, S.date_start, S.date_end, "
    base_query += "CONCAT(U.first_name, ' ', U.last_name) as teacher, C.name as center, C.state, "
    base_query += "C.district, C.village, C.photo as center_image, S.teacher_id,S.offering_id, "
    base_query += "WOF.center_id, WOF.course_id, T.id as topic_id FROM web_session S "
    base_query += "LEFT JOIN auth_user U ON S.teacher_id = U.id "
    base_query += "LEFT JOIN web_offering WOF ON S.offering_id = WOF.id "
    base_query += "LEFT JOIN web_center C ON WOF.center_id = C.id "
    base_query += "LEFT JOIN web_course CO ON WOF.course_id = CO.id "
    base_query += "LEFT JOIN web_session_planned_topics ST On S.id = ST.session_id "
    base_query += "LEFT JOIN web_topic T ON ST.topic_id = T.id WHERE"
    pref_query = "SELECT D.id as demand_id, CO.grade, CO.subject, WOF.language, CO.board_name, "
    pref_query += "D.day, D.start_time, D.end_time, CONCAT(U.first_name, ' ', U.last_name) as teacher, "
    pref_query += "C.name as center, C.state, C.district, C.village, C.photo as center_image, "
    pref_query += "D.user_id as teacher_id, D.offering_id, WOF.center_id, WOF.course_id FROM web_demandslot D "
    pref_query += "LEFT JOIN auth_user U ON D.user_id = U.id "
    pref_query += "LEFT JOIN web_offering WOF ON D.offering_id = WOF.id "
    pref_query += "LEFT JOIN web_center C ON WOF.center_id = C.id "
    pref_query += "LEFT JOIN web_course CO ON WOF.course_id = CO.id WHERE"
    user       = request.user
    user_roles = [i.name for i in user.userprofile.role.all()]
    if not user_roles:
        user_roles = ["Teacher"]
    center_ids = []
    role_query = []
    if user.is_superuser or "Center Admin" in user_roles or "Class Assistant" in user_roles:
        centers = []
        if user.is_superuser:
            centers = Center.objects.filter(status='Active').values_list("id")
        elif "Center Admin" in user_roles:
            centers = Center.objects.filter(admin=user, status='Active').values_list("id")
        else:
            centers = Center.objects.filter(assistant=user, status='Active').values_list("id")
        for center in centers:
            if center:
                center_ids.append(str(center[0]))
        role_query.append("C.id in ({})".format(",".join(center_ids[:5])))
    datetime_fields = ["date_start", "date_end"]
    date_fields     = ["start_time", "end_time"]
    for s_status in search_status:
        condition_query = []
        or_query = []
        query = [base_query]
        if s_status == 'prefered':
            query = [pref_query]
            order_by = "ORDER BY D.id desc"
            if role_query:
                or_query.append("D.user_id = {}".format(int(user.id)))
                or_query.extend(role_query)
            else:
                condition_query.append("D.user_id = {}".format(int(user.id)))
        else:
            order_by = "ORDER BY S.date_start desc"
            if "Teacher" in user_roles and role_query:
                or_query.append("S.teacher_id = {}".format(int(user.id)))
                or_query.extend(role_query)
            elif role_query:
                condition_query.extend(role_query)
            else:
                condition_query.append("S.teacher_id = {}".format(int(user.id)))
            condition_query.append("S.status = \"{}\"".format(s_status))
            if s_status == "scheduled":
                condition_query.append("S.date_start > NOW()")
                order_by = "ORDER BY S.date_start asc"
        if or_query:
            new_cond_query = "({})".format(" OR ".join(or_query))
            condition_query.append(new_cond_query)
        condition_query = " AND ".join(condition_query)
        query.append(condition_query)
        query.append(order_by)
        if limit_query:
            query.append(limit_query)
        query = " ".join(query)
        dict_cursor.execute(query)
        status_data = dict_cursor.fetchall()
        sess_response["total"] += len(status_data)
        final_data = data.setdefault(db_to_status.get(s_status, s_status), [])
        for _data in status_data:
            if s_status == 'prefered':
                _data["status"] = s_status
            for date_field in datetime_fields:
                if _data.has_key(date_field):
                    value = _data[date_field]
                    _data[date_field] = value.strftime("%d-%m-%Y %H:%M:%S")
            for date_field in date_fields:
                if _data.has_key(date_field):
                    value = _data[date_field]
                    if value:
                        value = "{}:{}".format(value.seconds // 3600, value.seconds // 60 % 60)
                        value = datetime.datetime.strptime(value, "%H:%M").strftime("%H:%M")
                        _data[date_field] = value
            center_image = _data.get("center_image", "")
            if center_image and not center_image.startswith("http://"):
                _data["center_image"] = 'http://'+ request.META['HTTP_HOST'] + "/" + str(center_image)
            final_data.append(_data)
    if sess_response["total"] < per_page:
        sess_response['next_page'] = 0
    else:
        sess_response['next_page'] = next_page + 1
    return return_response(sess_response)


@csrf_exempt
def student_session_duplicate(request):
    student_id = request.GET.get('student', '')
    # limit = str(request.GET.get('limit', '5'))
    new_offering_id = str(request.GET.get('offering_id', ''))
    if new_offering_id == '':
        resp = {"data" : {"status" : 422,"message" : "Required Parameters not sent"}}
        return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')
    student = None
    try:
        student = Student.objects.get(id=student_id)
    except Exception as exp:
        resp = {"data": {"status": 404, "message": "Student id not found"}}
    else:
        if student.status == 'Active' and student.activation:
            student_center = student.center_id
            photo_path = str((Center.objects.get(id=student_center)).photo)
            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                                 user=settings.DATABASES['default']['USER'],
                                 passwd=settings.DATABASES['default']['PASSWORD'],
                                 db=settings.DATABASES['default']['NAME'],
                                 charset="utf8",
                                 use_unicode=True)
            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query = "SELECT DISTINCT offering_id from web_offering_enrolled_students INNER JOIN web_offering ON web_offering.id=web_offering_enrolled_students.offering_id WHERE student_id= '{}' AND web_offering.status='running' AND web_offering.active_teacher_id is not null".format(
                str(student_id))
            dict_cur.execute(query)
            offers_list = [str(each['offering_id']) for each in dict_cur.fetchall()]
            if len(offers_list) > 0:
                offers_list.sort()
                offering_id = "(" + ",".join(offers_list) + ")"
                today = datetime.datetime.now()
                query = "SELECT web_session.offering_id as offer_id, web_session.id AS sessionid, web_session.video_link as video_link, web_session.mode as mode, CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS name, web_session.teacher_id, web_course.grade, web_course.subject, web_session.ts_link, web_session.date_start FROM web_session INNER JOIN web_offering ON web_offering.id=web_session.offering_id INNER JOIN web_course ON web_course.id=web_offering.course_id INNER JOIN auth_user ON web_session.teacher_id=auth_user.id  WHERE offering_id=" + new_offering_id + " AND year(web_session.date_start)="+str(today.year)+" and month(web_session.date_start)="+str(today.month)+" ORDER BY web_session.date_start ASC"
                dict_cur.execute(query)
                session_details = dict_cur.fetchall()
                print "offer list ======================", offers_list
                resp = {
                    "metadata": {
                        "resultset": {
                            "count": len(session_details)
                        }
                    },
                    "results": []
                }
                    
                for each in session_details:
                    session_id = each['sessionid']
                    query = "select web_topic.title FROM web_session INNER JOIN web_session_planned_topics ON web_session.id=web_session_planned_topics.session_id INNER JOIN web_topic ON web_topic.id=web_session_planned_topics.topic_id where web_session.id=" + str(
                        session_id) + ""
                    dict_cur.execute(query)
                    session_det = dict_cur.fetchall()
                    homework_data = Homeworks.objects.filter(session_id=each['sessionid'], student_id=student_id)
                    all_assignment_details = []
                    session = OrderedDict()
                    session["id"] = each['sessionid']
                    session["offering_id"] = each['offer_id']
                    session["teacher_id"] = each['teacher_id']
                    session["name"] = each['name']
                    session["grade"] = each['grade']
                    session["subject"] = each['subject']
                    session["ts_link"] = each['ts_link']
                    session['video_link'] = each['video_link']
                    session['mode'] = each['mode']
                    if session_det:
                        session['title'] = session_det[0]['title']
                    else:
                        session['title'] = "NA"
                    session['date_start'] = str(each['date_start'])
                    session['school_photo'] = photo_path
                    # Adding assignments details to the api
                    session['assignments'] = []
                    for details in homework_data:
                        topic_details = Topic.objects.filter(id=details.topic_id)
                        assignment_details = {
                            'id' : details.id,
                            'topic_comment' : details.topic_comment,
                            'assignment_type' : details.assignment_type,
                            'assignment_details' : details.assignment_details,
                            'topic_id' : details.topic_id,
                            'topic_name' : topic_details[0].title,
                            "file_path" : details.file_path,
                            "file_name" : details.file_name,
                            'status' : details.status,
                            'remarks' : details.remarks,
                            'assignment_no' : details.assignment_no,
                            "student_uploaded_assignments" : [],
                            "last_submission_date" : str(details.last_submission_date)
                        }
                        student_uploaded_assignment = Homeworksdetails.objects.filter(homework_id=details.id, student_id=student_id)
                        for assignment in student_uploaded_assignment:
                            uploaded_assignment = {
                                'id' : assignment.id,
                                'file_name' : assignment.file_name,
                                'file_path' : assignment.file_path,
                                'file_type' : assignment.file_type,
                                'base64_format' : ''
                            }
                            # f_path = '/var/www/evd/static/uploads/assignments/'
                            # Amit local testing path
                            f_path = '/var/www/evd/' + assignment.file_path + assignment.file_name
                            if path.exists(f_path) and assignment.file_type and assignment.file_type == 'img':
                                with open(f_path, "rb") as img_file:
                                    base64_format = base64.b64encode(img_file.read())
                                file_extension = (assignment.file_name).split('.')
                                uploaded_assignment['base64_format'] =  'data:image/' + file_extension[1] + ';base64,' + base64_format
                            assignment_details['student_uploaded_assignments'].append(uploaded_assignment)
                        session['assignments'].append(assignment_details)
                    resp["results"].append(session)
                dict_cur.close()
                db.close()
            else:
                resp = {"data": {"status": 404, "message": "No upcoming sessions found for student"}}
        else:
            resp = {"data": {"status": 404, "message": "Student is not Active" if student.status != "Active" else "OTP activation is not completed for student"}}
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


"""
    Newly added functions and url
"""

#sending sms to students
def send_sms_to_students(enrolled_students, assignment_details):
    for student in enrolled_students:
        phone_no = student.phone
        if(phone_no):
            if phone_no[0] != '0':
                phone_no = '0' + phone_no
            # Sending sms to student
            message = "Assignment - " + (datetime.datetime.now()).strftime('%d/%m/%Y') + " " + assignment_details
            response = send_message(sid, token, "08047091718", phone_no, message)
            print(response.json())
        else:
            print("Invalid phone no for student id = {}, student name = {} ".format(student.id, student.name))
    return True



def log_error_messages(msg):
    with open(os.getcwd() + "/api/session_assignment_creation_log.log", "a") as output_file:
        cur_date = str(datetime.datetime.now())
        output_file.write(cur_date + " : " + msg + "\n")


'''
    Author Name : Amit Kumar Pradhan
    CRUD API for teacher assignment
'''
@csrf_exempt
def save_session_assignment(request):
    print("Entering here ========================================\n")
    try:
        resp = {
            "metadata": {
                "resultset": {
                    "count": 0
                }
            },
            "results": []
        }
        if request.method == 'GET':
            try:
                session_id = request.GET.get('session_id', '')
                assignment_no = request.GET.get('assignment_no', '')
                status = request.GET.get('status', '')
                if status:
                    # As Mayank asked format changed for the api (front end requirement)
                    resp = {
                        "metadata": {
                            "resultset": {
                                "count": 0
                            }
                        },
                        "results": {
                            status : []
                        }
                    }


                    # Validation
                    valid_status = ['Submitted', 'Reviewed', 'Completed', 'Resubmit']
                    if status not in valid_status:
                        resp['message'] = 'Invalid status.'
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                    
                    # Fetching homeworks assigned based on status and added user
                    homeworks = Homeworks.objects.filter(status=status, added_by=request.user)
                    if homeworks.count() == 0:
                        resp['message'] = 'No data available for user {} with status = {}.'.format(request.user.username, status)
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                    
                    offering_ids = homeworks.values_list('offering_id').distinct()
                    print "offering ids = ", offering_ids
                    
                    for offering_id in offering_ids: 
                        offering_data = Offering.objects.get(id=offering_id[0])
                        print "offering _data = ", offering_data
                        required_resp = {}
                        required_resp = {
                            'status' : status,
                            'offering_id' : offering_id[0],
                            'center_id' : offering_data.center_id,
                            'center_name' : offering_data.center.name,
                            'course_details' : {
                                'course_id' : offering_data.course_id,
                                'subject' : offering_data.course.subject,
                                'grade' : offering_data.course.grade,
                                'board_name' : offering_data.course.board_name,
                                'type' : offering_data.course.type
                            }
                        }
                        resp['results'][status].append(required_resp)
                    resp['message'] = "success"
                    resp['metadata']['resultset']['count'] = len(resp['results'][status])
                    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                elif session_id and assignment_no:
                    homeworks = Homeworks.objects.filter(session_id=session_id, assignment_no=assignment_no).order_by('id')
                    if homeworks.count() == 0:
                        resp['message'] = 'No homeworks available for session id = {} and assignment no = {}'.format(session_id, assignment_no)
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                elif session_id:
                    homeworks = Homeworks.objects.filter(session_id=session_id).order_by('id')
                    if homeworks.count() == 0:
                        resp['message'] = 'No data available for session id = '+ session_id
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json') 
                else:
                    homeworks = Homeworks.objects.all().order_by('id')
                    if homeworks.count() == 0:
                        resp = {'data' : {'message' : 'No data available for session id = '+ session_id}}
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                    
                resp = {
                    "metadata": {
                        "resultset": {
                            "count": homeworks.count()
                        }
                    },
                    "results": []
                }

                for homework in homeworks:
                    assignment_data = {}
                    topic = Topic.objects.filter(id=homework.topic_id)
                    # print 'works =====================', homework
                    assignment_data['assignment_no'] = homework.assignment_no
                    assignment_data['student_id'] = homework.student_id
                    assignment_data['offering_id'] = homework.offering_id
                    assignment_data['session_id'] = homework.session_id
                    assignment_data['topic_id'] = homework.topic_id
                    assignment_data['topic_name'] = topic[0].title if topic.count() else ''
                    assignment_data['topic_comment'] = homework.topic_comment
                    assignment_data['assignment_type'] = homework.assignment_type
                    assignment_data['assignment_details'] = homework.assignment_details
                    assignment_data['status'] = homework.status
                    assignment_data['remarks'] = homework.remarks
                    assignment_data['file_path'] = homework.file_path
                    assignment_data['file_name'] = homework.file_name
                    assignment_data['last_submission_date'] = str(homework.last_submission_date)
                    resp['results'].append(assignment_data)
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            except Exception as e:
                print "Error reason = ", e
                print "Error at line no = ", traceback.format_exc()
                resp['message'] =  'Invalid Request'
                resp['status'] = 400
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
        elif request.method == 'POST':
            is_new = request.POST.get('is_new', '')
            session_id = request.POST.get('session_id', '')
            topic_id = request.POST.get('topic_id', '')
            topic_comment = request.POST.get('topic_comment', '')
            assignment_type = request.POST.get('assignment_type', '')
            assignment_details = request.POST.get('assignment_details', '')
            _file = request.FILES.get('session_assignment', '')
            last_submission_date = request.POST.get('last_submission_date', '')
            print("session_id = ", session_id)
            print("topic_id = ", topic_id)
            print("topic_comment = ", topic_comment)
            print("assignment_type = ", assignment_type)
            print("assgnment_details = ", assignment_details)
            print("last_submission_date = ", last_submission_date)
            print("is_new", is_new)
            valid_assignment_types = ['Message', 'Videos', 'Worksheets']
            print("ERROR: Error reason = 1 \n session id = {}, is_new = {}, topic id = {}, topic comment = {}, assignment type = {}, assignment details = {}, session assignment = {}, last_submission_date = {}".format(session_id, is_new, topic_id, topic_comment, assignment_type, assignment_details, _file, last_submission_date))
            # Fetching session data
            session = Session.objects.filter(id=session_id)

            # validation
            if is_new == '' or session_id ==  '' or topic_id == '' or topic_comment == '' or assignment_type == '' or assignment_details == '' or assignment_type not in valid_assignment_types or last_submission_date == '':
                resp = {"data" : {"status" : 422,"message" : "Required Parameters not sent"}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')
            try:
                last_submission_date = datetime.datetime.strptime(last_submission_date, "%d/%m/%Y").date()
                last_submission_date = last_submission_date.strftime("%Y-%m-%d")
            except:
                resp = {'data' : {'message' : 'Invalid last_submission_date'}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')
            
            f_path, f_name = None, None
            if assignment_type == 'Worksheets' and (_file ==  None or len(_file) == 0):
                resp = {"data" : {"status" : 422,"message" : "Required Parameters not sent"}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')

            if(session.count() == 0):
                resp = {"data" : {"status" : 422, "message" : "Invalid session id" }}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')
            print("ERROR: Error reason = 2 \n") 
            '''
                Fetching filename and checking for the extension. 
                If space available removing the space and 
            '''
            try:
                if assignment_type == 'Worksheets':
                    f_path = '/var/www/evd/static/uploads/session_assignments/'
                    # f_path = '/home/user/my_proj/upload_test/'
                    # f_path = '/home/amit/trisys_projects/evidyaloka/new_clone/evd/static/uploads/session_assignments/'
                    no_of_files = len(os.listdir(f_path))
                    no_of_files += 1
                    _file_name = _file.name
                    _file.name = (os.path.splitext(_file_name)[0] + '_' + str(session_id) + '_' + str(no_of_files) + os.path.splitext(_file_name)[1]).replace(' ', '_')
                    _file_name = _file.name
                    valid_extensions = ['.txt', '.doc', '.pdf', '.docx']
                    if len(os.path.splitext(_file_name)) > 1 and (os.path.splitext(_file_name))[1] not in valid_extensions:
                        resp = {'data' : {'message' : 'Invalid file format.', "status" : 422}}
                        return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')

                    # Moving file to uploads/assignment folder
                    f_name = _file_name
                    f = open(f_path + f_name, 'w+')
                    f.write(_file.read())
                    f.close()
            except Exception as e:
                print "Error  reason = ", e
                print "Error at line no = ", traceback.format_exc()
                log_error_messages("ERROR: Error reason = \n" + str(e))
                log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
                resp = {'data' : {'message' : 'internal error.'}}
            print("ERROR: Error reason = 3 \n", )
            enrolled_students = session[0].offering.enrolled_students.all()
            print "Total enrolled students = ", enrolled_students.count()
            # For creating new session assignment if is_new=1 else updating it
            if is_new == 1 or is_new =='1':
                if enrolled_students.count() == 0:
                    resp = {'data' : {'message' : 'Enrolled students not found for the offering.', "status" : 200}}
                    return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')

                total_session_homeworks = Homeworks.objects.filter(session_id=session_id).order_by('-id')
                assignment_number = 1
                print "total home works = ", total_session_homeworks
                if total_session_homeworks.count():
                    assignment_number = total_session_homeworks[0].assignment_no + 1
                log_error_messages("ERROR: Error reason = 4 \n")
                print "assignment no = ",assignment_number
                # create Homeworks
                for student in enrolled_students:
                    try:
                        if assignment_type == 'Worksheets':
                            Homeworks.objects.create(student_id=student.id, offering_id=session[0].offering_id,
                                                session_id=session_id, topic_id=topic_id, topic_comment=topic_comment,
                                                assignment_type=assignment_type, assignment_details=assignment_details,
                                                file_path='/static/uploads/session_assignments/', file_name=f_name,
                                                added_by=request.user, added_on=datetime.datetime.now(), assignment_no=assignment_number,
                                                last_submission_date=last_submission_date
                                                )
                        else:
                            Homeworks.objects.create(student_id=student.id, offering_id=session[0].offering_id,
                                                session_id=session_id, topic_id=topic_id, topic_comment=topic_comment,
                                                assignment_type=assignment_type, assignment_details=assignment_details,
                                                added_by=request.user, added_on=datetime.datetime.now(), assignment_no=assignment_number,
                                                last_submission_date=last_submission_date
                                                )
                        
                        resp = {"data" : {"status":200, "message":"Assignment saved successfully"}}
                    except Exception as e:
                        print "Error reason = ", e
                        print "Error at line no = ", traceback.format_exc()
                        resp = {"data" : {"status":500, "message":"Internal error."}}
                        log_error_messages("ERROR: Error reason = \n" + str(e))
                        log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
                log_error_messages("ERROR: Error reason = 5 \n" + str(resp))
                '''
                    assignment type is message send message to all the enrolled students 
                    for the respective offering
                '''
                log_error_messages("ERROR: Error reason = resp == " + str(resp))
                if assignment_type == 'Message':
                    send_sms_to_students(enrolled_students, assignment_details)
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                log_error_messages("ERROR: Error reason = 6 \n")
            elif is_new == 0 or is_new =='0':
                # Validation
                assignment_no = request.POST.get('assignment_no', '')
                if not assignment_no:
                    resp = {'data' : {'message' : 'Invalid assignment number'}}

                homeworks = Homeworks.objects.filter(session_id=session_id)
                if homeworks.count() == 0:
                    resp = {'data' : {'message' : 'No homeworks available for session id = ' + session_id}}
                    return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')

                homeworks = homeworks.filter(assignment_no=assignment_no)
                if homeworks.count() == 0:
                    resp = {'data' : {'message' : 'Invalid assignment no for session id = ' + session_id}}
                    return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
                
                '''
                    exist assignment type not equal to message and 
                    new asssignment type is Message then send sending messge to students
                '''
                if homeworks[0].assignment_type != 'Message' and assignment_type == 'Message':
                    send_sms_to_students(enrolled_students, assignment_details)

                resp = {'data' : {'message' : 'Assignment updated successfully.'}}
                for student in enrolled_students:
                    try:
                        if assignment_type == 'Worksheets':
                            homeworks.filter(student_id=student.id).update(topic_id=topic_id, topic_comment=topic_comment, 
                                    assignment_type=assignment_type, assignment_details=assignment_details,
                                    updated_by=request.user, updated_on=datetime.datetime.now(), 
                                    file_path='/static/uploads/session_assignments/', file_name=f_name, last_submission_date=last_submission_date)
                        else:
                            homeworks.filter(student_id=student.id).update(topic_id=topic_id, topic_comment=topic_comment, 
                                assignment_type=assignment_type, assignment_details=assignment_details,
                                updated_by=request.user, updated_on=datetime.datetime.now(),
                                file_path='', file_name='',last_submission_date=last_submission_date)
                    except Exception as e:
                        print "Error reason = ", e
                        print "Error at line no = ", traceback.format_exc()
                        log_error_messages("ERROR: Error reason = \n" + str(e))
                        log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
                        resp = {'data' : {'message' : 'Internal error.'}}
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                
            else:
                resp = {'data' : {'message' : 'Invalid is_new data'}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
        elif request.method == 'DELETE':
            session_id = request.GET.get('session_id', '')
            assignment_no = request.GET.get('assignment_no', '')
            assignment_id = request.GET.get('assignment_id', '')

            if session_id and assignment_no:
                homeworks = Homeworks.objects.filter(session_id=session_id, added_by=request.user)
                if homeworks.count() == 0:
                    resp = {'data' : {'message' : 'Invalid session id.'}}
                    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                
                homeworks = homeworks.filter(assignment_no=assignment_no, added_by=request.user)
                if homeworks.count() == 0:
                    resp = {'data' : {'message' : 'Invalid assignment no = {} for session id = {}.'.format(assignment_no, session_id)}}
                    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

                homeworks.delete()
                resp = {'data' : {'message' : 'Session deleted successfully for session id = {} and assignment no = {}'.format(session_id, assignment_no)}}
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            elif session_id:
                homeworks = Homeworks.objects.filter(session_id=session_id, added_by=request.user)
                if homeworks.count() == 0:
                    resp = {'data' : {'message' : 'Invalid session id.'}}
                    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                
                homeworks.delete()
                resp = {'data' : {'message' : 'Session deleted successfully for session id = {}.'.format(session_id)}}
            elif assignment_id:
                homeworks = Homeworks.objects.filter(id=assignment_id, added_by=request.user)
                if homeworks.count() == 0:
                    resp = {'data' : {'message' : 'Invalid assignemnt id.'}}
                    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                
                homeworks.delete()
                resp = {'data' : {'message' : 'Assignment deleted successfully for assignment id = {}.'.format(assignment_id)}}
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            else:
                resp = {'data' : {'message' : 'Invalid Request.'}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print "Error  reason = ", e
        print "Error at line no = ", traceback.format_exc()
        log_error_messages("ERROR: Error reason = \n" + str(e))
        log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
        resp = {'data' : {'message' : 'internal error.'}}
    log_error_messages("ERROR: Error reason = 7 \n")
    log_error_messages("ERROR: Error reason = 8 \n", resp)
    return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')


'''
    Author Name : Amit Kumar Pradhan
'''
@csrf_exempt
def delete_session_assignment_by_id(request):
    resp = {}
    # Delete session assignment data by id
    assignment_id = request.GET.get('assignment_id', '')
    if assignment_id:
        homeworks_data = Homeworks.objects.filter(id=assignment_id)
        print(homeworks_data)
        if(len(homeworks_data)):
            homeworks_data.delete()
            resp = {"data" : {"status" : 200, "message" : "Deleted successfully"}}
        else:
            resp = {"data" : {"status" : 422, "message" : "Invalid assignment id"}}
    else:
        resp = {"data" : {"status" : 422, "message" : "Required Parameters not sent"}}
    
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


def send_email(email_id, name, student_name, file_path):
    response_data = {}
    try:
        to = ['amit@trisysit.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        message = "<p>Dear %s,</p><p>%s has submitted his assignment</p><p>File Path : %s</p><br><br><p>Best Regards</p>" %(name, student_name, file_path)
        subject = "Students uploaded assignment"
        msg = EmailMessage(subject, message, to = to, from_email = from_email)
        msg.content_subtype = 'html'
        msg.send()
        response_data["status"] = 1
        response_data["message"] = "Mailed delivers successfully"
    except Exception as e:
        response_data["status"] = 0
        response_data["message"] = "Error while sending the mail"
        print("Error while sending the mail")
        print("exception==============================================", e)
    return response_data


'''
    Author Name : Amit Kumar Pradhan
'''
@csrf_exempt
def upload_assignment(request):
    resp = {}
    try:
        # Fetching the required parameters
        answer_doc_files = request.FILES.get('answer_doc', '')
        assignment_id = request.POST.get('assignment_id', '')
        student_id = request.POST.get('student_id', '')
        answer_img_files = request.POST.getlist('answer_img')
        
        # Validating parameter
        if assignment_id == '':
            resp = {'data' : {'message' : 'Required parameter assignment id not sent.'}}
            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
        if student_id == '':
            resp = {'data' : {'message' : 'Required parameter student id not sent.'}}
            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
        if answer_doc_files == '' and len(answer_doc_files) == 0 and request.FILES == None and len(request.FILES) == 0 and answer_img_files and len(answer_img_files) == 0:
            if answer_img_files and len(answer_img_files) == 0:
                pass
            resp = {'data' : {'message' : 'Required parameter answer document files not sent.'}}
            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
        # Fetching homeworks details by id
        homeworks_details = Homeworks.objects.filter(id=assignment_id)
        if (homeworks_details.count()) == 0:
            resp = {'data' : {'message' : 'Invalid assignment id' }}
            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json') 
        session_id = homeworks_details[0].session_id
        # From course details fetching offering id
        course_details = Session.objects.filter(id = session_id)
        offering_id = course_details[0].offering_id
        '''
            Checking data available for student id and offering id.
            if not available returning as a bad request student id is not available
            else processing
        ''' 
        offering_enrolled_students_count = Offering_enrolled_students.objects.filter(student_id=student_id).count() 
        if offering_enrolled_students_count == 0:
            resp = {'data' : {'message' : 'Invalid student id'}}
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')      
        # offering_enrolled_students_data = Offering_enrolled_students.objects.filter(student_id=student_id)
        '''
            Fetching filename and checking for the extension. 
            If space available removing the space and 
        '''
        success_files, memory_exceed_files, format_error_files = [], [], []
        success_msg, limit_message, format_msg = 'File upload suceed for ', 'File size exceeded for ', 'Invalid file format for '
        db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                user=settings.DATABASES['default']['USER'],
                passwd=settings.DATABASES['default']['PASSWORD'],
                db=settings.DATABASES['default']['NAME'],
                charset="utf8",
                use_unicode=True)
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        
        count = 0
        for answer_doc_file in request.FILES.getlist('answer_doc'):
            count += 1
            original_file_name = answer_doc_file.name
            answer_doc_file_name = answer_doc_file.name
            answer_doc_file.name = (os.path.splitext(answer_doc_file_name)[0] + '_' + str(student_id) + os.path.splitext(answer_doc_file_name)[1]).replace(' ', '_')
            answer_doc_file_name = answer_doc_file.name
            valid_extensions = ['.txt', '.doc', '.pdf', '.xls', '.xlsx', '.docx'] #, '.jpeg', '.png', '.jpg', '.tiff', '.psd', '.eps', '.ai', '.indd', '.raw'
            if len(os.path.splitext(answer_doc_file_name)) > 1 and (os.path.splitext(answer_doc_file_name))[1] in valid_extensions:
                if answer_doc_file.size < 3145728:
                    # Moving file to uploads/assignment folder
                    f_path = '/var/www/evd/static/uploads/assignments/'
                    # Amit local testing path
                    # f_path = '/home/user/my_proj/kanishka/'
                    f_name = answer_doc_file_name
                    f = open(f_path + f_name, 'w+')
                    f.write(answer_doc_file.read())
                    f.close()
                    # Creating student upload assignment data
                    Homeworksdetails.objects.create(homework_id=assignment_id, student_id=student_id, 
                                                        file_path='/static/uploads/assignments/', file_name=answer_doc_file_name,
                                                        added_on=datetime.datetime.now(), file_type='file')
                    
                    success_files.append(original_file_name)
                else:
                    memory_exceed_files.append(original_file_name)
            else:
                format_error_files.append(original_file_name)
        else:
            msg = ''
            success_image_files = []
            # Converting ase64 string to image and saving it in db
            for answer_doc_img in request.POST.getlist('answer_img'):
                f_path = '/var/www/evd/static/uploads/assignments/'
                # Amit local testing path
                # f_path = '/home/user/my_proj/kanishka/'
                homework_details_data = Homeworksdetails.objects.all().order_by('-id')
                image_no = 0
                if homework_details_data.count():
                    image_no = homework_details_data.count()
                # validating base64 url
                image = (answer_doc_img.split(';'))
                answer_doc_img =image[0]
                image_type = answer_doc_img.split('/')
                if len(image_type) > 1 and len(image) > 1 and 'base64,' in image[1]:
                    image_extension = image_type[1]
                    try:
                        imgdata = base64.b64decode((image[1]).replace('base64,', ''))
                        # Uploading image to required path
                        filename = "answer_image_" + str(image_no) + "_" + str(student_id) + "." + image_extension
                        with open(f_path + filename, 'wb') as f:
                            f.write(imgdata)
                        
                        Homeworksdetails.objects.create(homework_id=assignment_id, student_id=student_id, 
                                                        file_path='/static/uploads/assignments/', file_name=filename,
                                                        added_on=datetime.datetime.now(), file_type='img')
                        success_image_files.append(filename)
                        count += 1
                    except Exception as e:
                        print "Error reason = ", e
                        print "Error at line no = ", traceback.format_exc()
                        msg = 'Invalid base64 format string found in request. Please check. '
                        log_error_messages("ERROR: Error reason = \n" + str(e))
                        log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
                else:
                    msg = 'Invalid base64 format string found in request. Please check. '
            else:
                if len(success_image_files):
                    # Updating db
                    Homeworks.objects.filter(id=assignment_id).update(status='Submitted')
                    msg += "Images uploaded successfully with name = " + (', '.join(success_image_files)) + ". "
            if count == 0:
                msg = 'Please provide correct required parameters. '
                resp = {'data' : {'message' : msg}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
            if len(success_files):
                # Updating db
                Homeworks.objects.filter(id=assignment_id).update(status='Submitted')
                success_msg += ','.join(success_files)
                msg += (success_msg + '. ')
            if len(memory_exceed_files):
                limit_message += ','.join(memory_exceed_files)
                msg += (limit_message + '. ')
            if len(format_error_files):
                format_msg += ','.join(format_error_files)
                msg += (format_msg + '.')
        # Fetching session details and sending mail
        teacher_id = course_details[0].teacher_id
        if teacher_id:
            user_details_query = "SELECT * FROM auth_user where id = '{}'".format(teacher_id)
            dict_cur.execute(user_details_query)
            user_res = dict_cur.fetchall()
            student_details = Student.objects.get(id=student_id)
            print(student_details.name)
            send_email(user_res[0].get('email', ''), user_res[0].get('first_name', ''), student_details.name, (','.join(success_files) + ', ' + ', '.join(success_image_files)))   
        resp = {'data' : {'message' : msg}}
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print('Error reason = ', e)
        print('Error in line no = ', traceback.format_exc())
        resp = {'data' : {'message' : 'Internal Error', 'status' : 500}}
        log_error_messages("ERROR: Error reason = \n" + str(e))
        log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


'''
    Author Name : Amit Kumar Pradhan
'''
@csrf_exempt
def delete_student_uploaded_assignment(request, uploaded_id):
    resp = {}
    try:
        homeworksdetails_data = Homeworksdetails.objects.filter(id=uploaded_id)
        if homeworksdetails_data.count():
            assignment_id = homeworksdetails_data[0].homework_id
            student_id = homeworksdetails_data[0].student_id
            homeworksdetails_data.delete()
            assignment_data = Homeworks.objects.filter(id=assignment_id)
            session_id = assignment_data[0].session_id
            session_data = Session.objects.filter(id=session_id)
            offering_data = session_data[0].offering
            homeworkdetails_count = Homeworksdetails.objects.filter(homework_id=assignment_id, student_id=student_id).count()
            if homeworkdetails_count == 0:
                Homeworks.objects.filter(id=assignment_id).update(status='Assigned')
            
            resp = {'data' : {'message' : 'Uploaded assignment deleted successfully for id {}'.format(uploaded_id)}}
            
        else:
            resp = {'data' : {'message' : 'Invalid upload assignment id.'}}
    except Exception as e:
        print("Error reason = ", e)
        print("Error at line non =", traceback.format_exc())
        resp ={'data' : {'message' : 'Internal Error', 'status' : 500}}
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


'''
    Author Name : Amit Kumar Pradhan
'''
@csrf_exempt
def get_uploaded_assignment(request, session_assignment_id):
    resp = {}
    try:
        if session_assignment_id:
            homeworks_data = Homeworks.objects.filter(id=session_assignment_id)
            if homeworks_data.count()==0:
                resp = {'data' : {'message' : 'Invalid assignment id'}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
            topic_details = Topic.objects.filter(id=homeworks_data[0].topic_id)
            assignment_details = {
                'id' : homeworks_data[0].id,
                'topic_comment' : homeworks_data[0].topic_comment,
                'assignment_type' : homeworks_data[0].assignment_type,
                'assignment_details' : homeworks_data[0].assignment_details,
                'topic_id' : homeworks_data[0].topic_id,
                'topic_name' : topic_details[0].title,
                "file_path" : homeworks_data[0].file_path,
                "file_name" : homeworks_data[0].file_name,
                "student_uploaded_assignments" : []
                # "last_submission_date" : homeworks_data[0].last_submission_date
            }
            homeworkdetails_data = Homeworksdetails.objects.filter(homework_id=session_assignment_id)
            for uploaded_assignment in homeworkdetails_data:
                uploads = {
                    'id' : uploaded_assignment.id,
                    'file_name' : uploaded_assignment.file_name,
                    'file_path' : uploaded_assignment.file_path,
                    'file_type' : uploaded_assignment.file_type,
                    'base64_format' : ''
                }
                f_path = '/var/www/evd/' + uploaded_assignment.file_path + uploaded_assignment.file_name
                if path.exists(f_path) and uploaded_assignment.file_type and uploaded_assignment.file_type == 'img':
                    with open(f_path, "rb") as img_file:
                        base64_format = base64.b64encode(img_file.read())
                    file_extension = (uploaded_assignment.file_name).split('.')
                    uploads['base64_format'] =  'data:image/' + file_extension[1] + ';base64,' + base64_format
                assignment_details['student_uploaded_assignments'].append(uploads)
            resp = {'results': assignment_details}
        else:
            resp = {'data' : {'message' : 'Required parameters not sent'}}
            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print "Error Reason ===", e
        print "Error at line no = ", traceback.format_exc()
        resp ={'data' : {'message' : 'Internal Error', 'status' : 500}}
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


'''
    Author Name : Amit Kumar Pradhan
'''
@csrf_exempt
def get_assignments_for_offering(request):
    resp = {
                "metadata": {
                    "resultset": {
                        "count": 0
                    }
                },
                "results": []
            }
    try:
        status = request.GET.get('status', '')
        offering_id = request.GET.get('offering_id', '')
        
        if not offering_id or not status:
            resp['message'] = 'Required parameters not sent.'
            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
        valid_status = ['Submitted', 'Reviewed', 'Resubmit', 'Completed']
        if status not in valid_status:
            resp['message'] = 'Invalid status.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        homeworks_data = Homeworks.objects.filter(offering_id=offering_id, added_by=request.user)
        if homeworks_data.values_list('assignment_no').distinct().count() == 0:
            resp['message'] = 'No assignment available for offering id = {} and user = {}.'.format(offering_id, request.user.username, status)
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        assignemnt_nos = homeworks_data.values_list('assignment_no').distinct()
        for assignment_no in assignemnt_nos:
            homeworks = homeworks_data.filter(assignment_no=int(assignment_no[0]))
            session_data = Session.objects.filter(id=homeworks[0].session_id)
            assignments = {
                'offering_id' : offering_id,
                'session_id' : homeworks[0].session_id,
                'topic_id' : homeworks[0].topic_id,
                'topic_comment' : homeworks[0].topic_comment,
                'assignment_type' : homeworks[0].assignment_type,
                'assignment_details' : homeworks[0].assignment_details,
                'file_name' : homeworks[0].file_name,
                'file_path' : homeworks[0].file_path,
                'assignment_no' : homeworks[0].assignment_no,
                'last_submission_date' : str(homeworks[0].last_submission_date),
                'session_start_date' : (session_data[0].date_start).strftime("%d-%m-%Y %H:%M:%S"),
                'uploaded_data_count'  : (homeworks_data.filter(status=status, assignment_no=int(assignment_no[0]))).count()
            }
            resp['results'].append(assignments)
        resp['metadata']['resultset']['count'] = len(resp['results'])
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()
        resp['message'] = 'Internal error.'
        resp['status'] = 500
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
'''
    Author Name : Amit Kumar Pradhan
'''


@login_required
def get_students_for_offering(request):
    resp = {
                "metadata": {
                    "resultset": {
                        "count": 0
                    }
                },
                "results": []
            }
    try:
        status = request.GET.get('status', '')
        offering_id = request.GET.get('offering_id', '')
        session_id = request.GET.get('session_id', '')
        assignment_no = request.GET.get('assignment_no', '')
        print "offering id =", offering_id, status
        if not offering_id or not status or not session_id or not assignment_no:
            resp['message'] = 'Required parameters not sent.'
            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
        valid_status = ['Submitted', 'Reviewed', 'Resubmit', 'Completed']
        if status not in valid_status:
            resp['message'] = 'Invalid status.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        homeworks_data = Homeworks.objects.filter(offering_id=offering_id, status=status, session_id=session_id, assignment_no=assignment_no, added_by=request.user)
        if homeworks_data.count() == 0:
            resp['message'] = 'No data available for offering id = {} and user = {} having status = {}'.format(offering_id, request.user.username, status)
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        for data in homeworks_data:
            student_details = {}
            student_data = Student.objects.filter(id=data.student_id)
            session_data = Session.objects.filter(id=data.session_id)
            student_details['name'] = student_data[0].name
            student_details['id'] = data.student_id
            student_details['date'] = (session_data[0].date_start).strftime("%d-%m-%Y")
            student_details['session_id'] = data.session_id
            student_details['homework_id'] = data.id
            student_details['last_submission_date'] = str(data.last_submission_date)
            student_details['session_time'] = (session_data[0].date_start).strftime("%H:%M") + ' - ' + (session_data[0].date_end).strftime("%H:%M")
            resp['results'].append(student_details)
        resp['metadata']['resultset']['count']  = len(resp['results'])
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()
        resp['message'] = 'Internal error.'
        resp['status'] = 500
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


'''
    Author Name : Amit Kumar Pradhan
'''
@login_required
def get_uploaded_assignment_for_student(request):
    resp = {
            "metadata": {
                "resultset": {
                    "count": 0
                }
            },
            "results": []
        }
    try:
        student_id = request.GET.get('student_id', '')
        status = request.GET.get('status', '')
        session_id = request.GET.get('session_id', '')
        assignment_no = request.GET.get('assignment_no', '')
        print "student id = ", student_id, "status = ", status, "session id = ", session_id, "assignment no = ", assignment_no
        if not student_id or not status or not session_id or not assignment_no:
            resp ['message'] = 'Required parameters not sent.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        valid_status = ['Submitted', 'Reviewed', 'Resubmit', 'Completed']
        if status not in valid_status:
            resp['message'] = 'Invalid status.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        homeworks_data = Homeworks.objects.filter(student_id=student_id, status=status, session_id=session_id, assignment_no=assignment_no, added_by=request.user)
        
        for homework_data in homeworks_data:
            homeworkdetails = Homeworksdetails.objects.filter(homework_id=homework_data.id)
            for detail in homeworkdetails:
                return_data = {}
                return_data['id'] = detail.id
                return_data['homework_id'] = detail.homework_id
                return_data['status'] = status
                return_data['session_id'] = homework_data.session_id
                return_data['assignment_no'] = homework_data.assignment_no
                return_data['student_id'] = detail.student_id
                return_data['file_path'] = detail.file_path
                return_data['file_name'] = detail.file_name
                return_data['file_type'] = detail.file_type
                return_data['added_on'] = (detail.added_on).strftime('%d-%m-%Y')
                resp['results'].append(return_data)
        if len(resp['results']) == 0:
            resp['message'] = 'No data available for student id = {}, assignment no = {}, session id = {}  and user = {} having status = {}'.format(student_id, assignment_no, session_id, request.user.username, status)
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        
        resp['metadata']['resultset']['count'] = len(resp['results'])
        resp['message'] = 'success'
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()
        resp['message'] = 'Internal error.'
        resp['status'] = 500
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')



'''
    Author Name : Amit Kumar Pradhan
'''
@csrf_exempt
def update_status_and_remarks(request):
    try:
        session_id = request.POST.get('session_id', '')
        student_id = request.POST.get('student_id', '')
        assignment_no = request.POST.get('assignment_no', '')
        status = request.POST.get('status', '')
        remarks = request.POST.get('remarks', '')
        if not session_id and not not student_id and not assignment_no and not status:
            resp = {'data' : {'message' : 'Required parameters not sent.'}}
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        valid_status = ['Reviewed', 'Resubmit', 'Completed']
        if status not in valid_status:
            resp = {'data' : {'message' : 'Invalid status.'}}
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        homeworks_data = Homeworks.objects.filter(student_id=student_id)
        if homeworks_data.count() == 0:
            resp = {'data' : {'message' : 'Invalid student id.'}}
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        homeworks_data = homeworks_data.filter(session_id=session_id)
        if homeworks_data.count() == 0:
            resp = {'data' : {'message' : 'Invalid session id.'}}
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        homeworks_data = homeworks_data.filter(assignment_no=assignment_no)
        if homeworks_data.count() == 0:
            resp = {'data' : {'message' : 'Invalid assignment no.'}}
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        homeworks_data.update(status=status, remarks=remarks)
        
        resp = {'data' : {'message' : 'Status updated successfully.'}}
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()
        resp = {'data' : {'message' : 'Internal error.'}}
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


@csrf_exempt
def approved_videos(request):
    resp = {
                "metadata": {
                    "resultset": {
                        "count": 0
                    }
                },
                "results": []
            }
    try:
        if request.method == 'GET':
            center_id = request.GET.get('center_id', '')
            grade = request.GET.get('grade', '')
            subject = request.GET.get('subject', '')
            topic = request.GET.get('topic', '')
            if not center_id or not grade or not subject or not topic:
                resp['message'] = 'Required parameters not sent.'
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            
            board_name = ((Center.objects.get(id=center_id)).board)
            video_assignments = VideoAssignments.objects.filter(board_name=board_name, grade=grade, subject=subject, topic=topic, status='Approved')
            for assignments in video_assignments:
                resp['results'].append(assignments.video_url)
            
            resp['metadata']['resultset']['count'] = len(resp['results'])
        elif request.method == 'POST':
            video_url = request.POST.get('video_link', '')
            mode = request.POST.get('mode', '')
            session_id = request.POST.get('session_id', '')
            valid_modes = ['online', 'offline']
            if not session_id or not mode or not video_url:
                resp['message'] = 'Required parameters not sent.'
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            if mode not in valid_modes:
                resp['message'] = 'Invalid mode type given.'
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            session_data = Session.objects.filter(id=session_id)
            if session_data.count() == 0:
                resp['message'] = 'Invalid session id.'
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            session_data = session_data.filter(teacher=request.user)
            if session_data.count() == 0:
                resp['message'] = 'Invalid user.'
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            if 'youtube' in video_url and '/embed/' not in video_url:
                url_arr = video_url.split('?v=')
                temp_url = url_arr[1].split('&')
                video_url = 'https://www.youtube.com/embed/' + temp_url[0]
            elif 'youtu.be' in video_url and '/embed/' not in video_url:
                url_arr = video_url.split('?list=')
                temp_url = url_arr[0].split('/')
                video_url = 'https://www.youtube.com/embed/' + temp_url[len(temp_url)-1]
            session_data.update(video_link=video_url, mode=mode)
            resp['message'] = 'Video url and mode updated successfully.'
        elif request.method == 'DELETE':
            session_id = request.GET.get('session_id', '')
            if not session_id:
                resp['message'] = 'Required parameters not sent.'
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            
            session_data = Session.objects.filter(id=session_id)
            if session_data.count() == 0:
                resp['message'] = 'Invalid session id.'
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            session_data = session_data.filter(teacher=request.user)
            if session_data.count() == 0:
                resp['message'] = 'Invalid user.'
                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
            if session_data[0].video_link:
                session_data.update(video_link=None)
            resp['message'] = 'Video link deleted for session = {}'.format(session_id)
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()
        resp['message'] = 'Internal Error.'
        resp['status'] = 500
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


@csrf_exempt
def update_session_status(request):
    resp = {}
    resp['data'] = {}
    try:
        session_id = request.POST.get('session_id', '')
        status = request.POST.get('status', '')
        valid_status = ['Started']
        if not session_id:
            resp['data']['message'] = 'Required parameters not sent.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        
        if status not in valid_status:
            resp['data']['message'] = 'Invalid status.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        session_data = Session.objects.filter(id=session_id)
        if session_data.count() == 0:
            resp['data']['message'] = 'Invalid session id.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        session_data = session_data.filter(teacher=request.user)
        if session_data.count() == 0:
            resp['data']['message'] = 'Invalid user.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        
        session_data.update(status='Started')
        resp['data']['message'] = 'Status updated successfully.'
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()
        resp['data']['message'] = 'Internal error.'
        resp['data']['status'] =  500
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


@csrf_exempt
def update_student_attendance(request):
    resp = {}
    resp['data'] = {}
    try:
        session_id = request.POST.get('session_id', '')
        student_id = request.POST.get('student_id', '')
        if not student_id or not session_id:
            resp['data']['message'] = 'Required parameters not sent.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        session_attendance = SessionAttendance.objects.filter(session_id=session_id, student_id=student_id)
        if session_attendance.count() == 0:
            new_session_attendance = SessionAttendance()
            new_session_attendance.student_id= student_id
            new_session_attendance.session_id = session_id
            new_session_attendance.is_present = "yes"
            new_session_attendance.save()
        #     resp['data']['message'] = "Invalid session id."
        #     return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        # session_attendance = session_attendance.filter(student_id=student_id) 
        # if session_attendance.count() == 0:
        #     resp['data']['message'] = "Invalid student id."
        #     return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        else:
            session_attendance.update(is_present='yes')
        resp['data']['message'] = 'Attendance updated successfully for student id = {} and session id = {}'.format(student_id, session_id)
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()
        resp['data']['message'] = "Internal error."
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


def get_offering_details(request):
    try:
        if request.method == 'GET':
            try:
                student_id = request.GET.get('student_id', '')
                print "student id ::",student_id
                if student_id:
                    students = Student.objects.filter(id=student_id)
                    
                    if(students.count()):
                        try:
                            resp = {
                                    'metadata' : {
                                        'resultset' : {
                                            'count' : 0
                                            }
                                            },
                                    'results' : []
                                    }
                            grade = students[0].grade
                            gender = students[0].gender
                            enrolled_offering = Offering_enrolled_students.objects.filter(student_id=student_id).order_by('-offering')
                            if(enrolled_offering.count()):
                                for each_off in enrolled_offering:
                                    off_details = {}
                                    offering_id = each_off.offering_id
                                    print "offering id ::",offering_id
                                    offering_details = Offering.objects.filter(id=offering_id, status='running')
                                    if(offering_details.count()):
                                        active_teacher_id = offering_details[0].active_teacher
                                        print " teacher id ::", active_teacher_id
                                        course = Course.objects.filter(id=offering_details[0].course.id)[0]
                                        board_name = course.board_name
                                        subject = course.subject
                                        language = offering_details[0].language
                                        if active_teacher_id:
                                            active_teacher_id = active_teacher_id.id
                                            teacher_name = str(User.objects.filter(id=active_teacher_id)[0].first_name)+' '+str(User.objects.filter(id=active_teacher_id)[0].last_name)
                                            off_details['teacher_name'] = teacher_name
                                        else:
                                            off_details['teacher_name']  = "NA"   
                                        off_details['student_id'] = student_id
                                        off_details['grade'] = grade
                                        off_details['gender'] = gender
                                        off_details['language'] = language                   
                                        off_details['offering_id'] = offering_id
                                        off_details['board_name'] = board_name
                                        off_details['subject'] = subject
                                        resp['results'].append(off_details)
                                        resp['metadata']['resultset']['count'] +=1
                                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                            else:
                                resp = {'data' : {'status':200, 'message' : 'No enrolled students found.'}}
                                return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                        except Exception as e:
                            print "Error reason = ", e
                            print "Error at line no = ", traceback.format_exc()
                            resp = {'data' : {'message' : 'internal error.'}}
                            return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')
                    else:
                        resp = {"data" : {"status" : 422, "message" : "Invalid Student id"}}
                        return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')
            except Exception as e:
                print "Error reason = ", e
                print "Error at line no = ", traceback.format_exc()
                resp = {"data" : {"status" : 400, "message" : "Invalid Request"}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print "Error  reason = ", e
        print "Error at line no = ", traceback.format_exc()
        log_error_messages("ERROR: Error reason = \n" + str(e))
        log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
        resp = {'data' : {'message' : 'internal error.'}}
    return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')


def get_videos_for_subject(request):
    try:
        if request.method == 'GET':
            try:
                offering_id = request.GET.get('offering_id','')
                if offering_id:
                    session_list = Session.objects.filter(offering=offering_id)
                    
                    resp = {
                        'metadata' : {
                            'resultset' : {
                                'count' : 0
                                }
                                },
                        'results' : []
                        }
                    if session_list:
                        for session in session_list:
                            if session.video_link:
                                video_info = {}
                                video_info['session_id'] = session.id
                                video_info['date_start'] = str(session.date_start)
                                video_info['date_end'] = str(session.date_end)
                                video_info['video_link'] = session.video_link
                                video_info['mode'] = session.mode
                                resp['results'].append(video_info)
                                resp['metadata']['resultset']['count'] +=1
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                    else:
                        resp = {'data' : {'status': 200, 'message' : 'No session found for offering id : {}'.format(offering_id)}}
                        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
                else:
                    resp = {'data' : {'status': 422, 'message' : 'Required parameter not sent.'}}
                    return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
            except Exception as e:
                print "Error reason = ", e
                print "Error at line no = ", traceback.format_exc()
                resp = {"data" : {"status" : 400, "message" : "Invalid Request"}}
                return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print "Error  reason = ", e
        print "Error at line no = ", traceback.format_exc()
        log_error_messages("ERROR: Error reason = \n" + str(e))
        log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
        resp = {'data' : {'message' : 'internal error.'}}
    return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')


def get_all_assignments_for_month(request):
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    
    try:
        if from_date and to_date:
            from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d')
            to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d')
            to_date = to_date + timedelta(hours=23, minutes=59, seconds=59)
            query = "SELECT * from web_homeworks where (\'"+datetime.datetime.strftime(from_date, "%Y-%m-%d %H:%M:%S")+"\' <= added_on) and  (\'"+datetime.datetime.strftime(to_date, "%Y-%m-%d %H:%M:%S")+"\' >= added_on)"
        else:
            curr_date = datetime.datetime.now()
            query = "SELECT * from web_homeworks where year(added_on)="+str(curr_date.year)+" and month(added_on)="+str(curr_date.month)
        db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                                user=settings.DATABASES['default']['USER'],
                                passwd=settings.DATABASES['default']['PASSWORD'],
                                db=settings.DATABASES['default']['NAME'],
                                charset="utf8",
                                use_unicode=True)
    
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        dict_cur.execute(query)
        print query
        all_homeworks = dict_cur.fetchall()
        resp = {
                "metadata": {
                    "resultset": {
                        "count": len(all_homeworks)
                    }
                },
                "results": []
            }
        for each_homework in all_homeworks:
            homework_detail = {}
            homework_detail['student_id'] = each_homework['student_id']
            homework_detail['offering_id'] = each_homework['offering_id']
            homework_detail['session_id'] = each_homework['session_id']
            homework_detail['topic_id'] = each_homework['topic_id']
            homework_detail['assignment_type'] = each_homework['assignment_type']
            homework_detail['assignment_details'] = each_homework['assignment_details']
            homework_detail['status'] = each_homework['status']
            homework_detail['file_path'] = each_homework['file_path']
            homework_detail['file_name'] = each_homework['file_name']
            homework_detail['assignment_no'] = each_homework['assignment_no']
            homework_detail['last_submission_date'] = str(each_homework['last_submission_date'])
            resp['results'].append(homework_detail)
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print "Error  reason = ", e
        print "Error at line no = ", traceback.format_exc()
        log_error_messages("ERROR: Error reason = \n" + str(e))
        log_error_messages("ERROR: Error at line no = \n" + str(traceback.format_exc()))
        resp = {'data' : {'message' : 'internal error.'}}
    return HttpResponseBadRequest(simplejson.dumps(resp), mimetype='apllication/json')


@csrf_exempt
def student_current_month_session(request):
    student_id = request.GET.get('student', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    student = None
    try:
        student = Student.objects.get(id=student_id)
    except Exception as exp:
        resp = {"data": {"status": 404, "message": "Student id not found"}}
    else:
        if student.status == 'Active' and student.activation:
            student_center = student.center_id
            photo_path = str((Center.objects.get(id=student_center)).photo)
            db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                                user=settings.DATABASES['default']['USER'],
                                passwd=settings.DATABASES['default']['PASSWORD'],
                                db=settings.DATABASES['default']['NAME'],
                                charset="utf8",
                                use_unicode=True)

            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
            query = "SELECT DISTINCT offering_id from web_offering_enrolled_students INNER JOIN web_offering ON web_offering.id=web_offering_enrolled_students.offering_id WHERE student_id= '{}' AND web_offering.status='running' AND web_offering.active_teacher_id is not null".format(
                str(student_id))
            dict_cur.execute(query)

            offers_list = [str(each['offering_id']) for each in dict_cur.fetchall()]
            if len(offers_list) > 0:
                offers_list.sort()
                offering_id = "(" + ",".join(offers_list) + ")"
                today = datetime.datetime.now()
                if from_date=='' and to_date=='':
                    query = "SELECT web_session.offering_id as offer_id, web_session.id AS sessionid, web_session.video_link as video_link, web_session.mode as mode, CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS name, web_session.teacher_id, web_course.grade, web_course.subject, web_session.ts_link, web_session.date_start FROM web_session INNER JOIN web_offering ON web_offering.id=web_session.offering_id INNER JOIN web_course ON web_course.id=web_offering.course_id INNER JOIN auth_user ON web_session.teacher_id=auth_user.id  WHERE offering_id IN " + offering_id + " AND year(web_session.date_start)="+str(today.year)+" and month(web_session.date_start)="+str(today.month)+" ORDER BY web_session.date_start ASC"
                else:
                    from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d')
                    to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d')
                    from_month = from_date.month
                    from_year = from_date.year
                    to_month = to_date.month
                    to_year = to_date.year
                    print "from month = {}, from year = {}, to year = {}, to month = {}".format(from_month, from_year, to_month, to_year)
                    # from_date = datetime.datetime.strptime(from_date, '%Y/%m/%d')
                    # to_date = datetime.datetime.strptime(to_date, '%Y/%m/%d')
                    to_date = to_date + timedelta(hours=23, minutes=59, seconds=59) 
                    from_date = datetime.datetime.strftime(from_date, "%Y-%m-%d %H:%M:%S")
                    to_date = datetime.datetime.strftime(to_date, "%Y-%m-%d %H:%M:%S")
                    query = "SELECT web_session.offering_id as offer_id, web_session.id AS sessionid, web_session.video_link as video_link, web_session.mode as mode, CONCAT(auth_user.first_name, ' ', auth_user.last_name) AS name, web_session.teacher_id, web_course.grade, web_course.subject, web_session.ts_link, web_session.date_start FROM web_session INNER JOIN web_offering ON web_offering.id=web_session.offering_id INNER JOIN web_course ON web_course.id=web_offering.course_id INNER JOIN auth_user ON web_session.teacher_id=auth_user.id  WHERE offering_id IN " + offering_id + " AND ((year(web_session.date_start) =\'"+str(from_year)+"\' AND month(web_session.date_start) =\'"+str(from_month)+"\') OR (year(web_session.date_start) =\'"+str(to_year)+"\' AND month(web_session.date_start) =\'"+str(to_month)+"\')) ORDER BY web_session.date_start ASC"
                    print query
                dict_cur.execute(query)
                session_details = dict_cur.fetchall()
                print query
                print "offer list ======================", offers_list

                resp = {
                    "metadata": {
                        "resultset": {
                            "count": len(session_details)
                        }
                    },
                    "results": []
                }

                    
                for each in session_details:
                    session_id = each['sessionid']
                    query = "select web_topic.title FROM web_session INNER JOIN web_session_planned_topics ON web_session.id=web_session_planned_topics.session_id INNER JOIN web_topic ON web_topic.id=web_session_planned_topics.topic_id where web_session.id=" + str(
                        session_id) + ""

                    dict_cur.execute(query)
                    session_det = dict_cur.fetchall()
                    homework_data = Homeworks.objects.filter(session_id=each['sessionid'], student_id=student_id)
                    all_assignment_details = []
                    session = OrderedDict()
                    session["id"] = each['sessionid']
                    session["offering_id"] = each['offer_id']
                    session["teacher_id"] = each['teacher_id']
                    session["name"] = each['name']
                    session["grade"] = each['grade']
                    session["subject"] = each['subject']
                    session["ts_link"] = each['ts_link']
                    session['video_link'] = each['video_link']
                    session['mode'] = each['mode']
                    if session_det:
                        session['title'] = session_det[0]['title']
                    else:
                        session['title'] = "NA"
                    session['date_start'] = str(each['date_start'])
                    session['school_photo'] = photo_path
                    # Adding assignments details to the api
                    session['assignments'] = []

                    for details in homework_data:
                        topic_details = Topic.objects.filter(id=details.topic_id)
                        assignment_details = {
                            'id' : details.id,
                            'topic_comment' : details.topic_comment,
                            'assignment_type' : details.assignment_type,
                            'assignment_details' : details.assignment_details,
                            'topic_id' : details.topic_id,
                            'topic_name' : topic_details[0].title,
                            "file_path" : details.file_path,
                            "file_name" : details.file_name,
                            'status' : details.status,
                            'remarks' : details.remarks,
                            'assignment_no' : details.assignment_no,
                            "student_uploaded_assignments" : [],
                            "last_submission_date" : str(details.last_submission_date)
                        }

                        student_uploaded_assignment = Homeworksdetails.objects.filter(homework_id=details.id, student_id=student_id)
                        for assignment in student_uploaded_assignment:
                            uploaded_assignment = {
                                'id' : assignment.id,
                                'file_name' : assignment.file_name,
                                'file_path' : assignment.file_path,
                                'file_type' : assignment.file_type,
                                'base64_format' : ''
                            }

                            # f_path = '/var/www/evd/static/uploads/assignments/'
                            # Amit local testing path
                            f_path = '/var/www/evd/' + assignment.file_path + assignment.file_name
                            if path.exists(f_path) and assignment.file_type and assignment.file_type == 'img':
                                with open(f_path, "rb") as img_file:
                                    base64_format = base64.b64encode(img_file.read())
                                file_extension = (assignment.file_name).split('.')
                                uploaded_assignment['base64_format'] =  'data:image/' + file_extension[1] + ';base64,' + base64_format
                            assignment_details['student_uploaded_assignments'].append(uploaded_assignment)

                        session['assignments'].append(assignment_details)
                    resp["results"].append(session)

                dict_cur.close()
                db.close()
            else:
                resp = {"data": {"status": 404, "message": "No upcoming sessions found for student"}}
        else:
            resp = {"data": {"status": 404, "message": "Student is not Active" if student.status != "Active" else "OTP activation is not completed for student"}}

    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')


def get_session_details_duplicate(request):
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
            event['video_link'] = session.video_link
            event['mode'] = session.mode
            event["topics"] = topics
            event["grade"] = make_number_verb(session.offering.course.grade)
            event["start"] = make_date_time(session.date_start)["time"]
            event["date"] = make_date_time(session.date_start)["date"] + " " + str(session.date_start.year)
            event["day_num"] = session.date_start.strftime('%d')
            event["month"] = session.date_start.strftime('%m')
            event["year"] = session.date_start.strftime('%Y')
            event["day_text"] = session.date_start.weekday()
            event["center"] = session.offering.center.name
            event["center_id"] = session.offering.center.id
            event["teacher"] = session.teacher.username if session.teacher else ''
            event["color"] = "#46D150"
            event["textColor"] = "black"
            event["ts_link"] = session.ts_link if (session.ts_link != "" and session.ts_link != None) else "NA"
            homeworks_data = Homeworks.objects.filter(session_id=session_id)
            event['assignments'] = list()
            assgn_no = []
            if(len(session_id)):
                for session_data in homeworks_data:
                    topic_details = Topic.objects.filter(id=session_data.topic_id)
                    topic_name = ''
                    if topic_details and len(topic_details):
                        topic_name = topic_details[0].title
                    if session_data.assignment_no not in assgn_no:
                        data = {
                            "session_id" : session_data.session_id,
                            "topic_name" : topic_name,
                            "topic_id" : session_data.topic_id,
                            "topic_comment" : session_data.topic_comment,
                            "assignment_type" : session_data.assignment_type,
                            "assignment_details" : session_data.assignment_details,
                            "file_path" : session_data.file_path,
                            "file_name" : session_data.file_name,
                            "student_id" : session_data.student_id,
                            "offering_id" : session_data.offering_id,
                            "assignment_no" : session_data.assignment_no
                            # "last_submission_date" : str(session_data.last_submission_date)
                        }
                        assgn_no.append(session_data.assignment_no)
                        event['assignments'].append(data)
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
def get_uploaded_assignment_for_student_status(request):
    resp = {
            "metadata": {
                "resultset": {
                    "count": 0
                }
            },
            "results": []
        }
    try:
        student_id = request.GET.get('student_id', '')
        status = request.GET.get('status', '')
        offering_id = request.GET.get('offering_id', '')
        print "student id = ", student_id, "status = ", status, "offering_id = ", offering_id
        if not student_id or not status or not offering_id:
            resp ['message'] = 'Required parameters not sent.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

        valid_status = ['Submitted', 'Reviewed', 'Resubmit', 'Completed']
        if status not in valid_status:
            resp['message'] = 'Invalid status.'
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

        homeworks_data = Homeworks.objects.filter(student_id=student_id, status=status, offering_id=offering_id,added_by=request.user)
        
        for homework_data in homeworks_data:
            homeworkdetails = Homeworksdetails.objects.filter(homework_id=homework_data.id)
            for detail in homeworkdetails:
                return_data = {}
                return_data['id'] = detail.id
                return_data['homework_id'] = detail.homework_id
                return_data['status'] = status
                return_data['session_id'] = homework_data.session_id
                return_data['assignment_no'] = homework_data.assignment_no
                return_data['student_id'] = detail.student_id
                return_data['file_path'] = detail.file_path
                return_data['file_name'] = detail.file_name
                return_data['file_type'] = detail.file_type
                return_data['added_on'] = (detail.added_on).strftime('%d-%m-%Y')
                resp['results'].append(return_data)
        if len(resp['results']) == 0:
            resp['message'] = 'No data available for student id = {} and offering id {} and user = {} having status = {}'.format(student_id, offering_id, request.user.username, status)
            return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
        
        resp['metadata']['resultset']['count'] = len(resp['results'])
        resp['message'] = 'success'
        return HttpResponse(simplejson.dumps(resp), mimetype='application/json')
    except Exception as e:
        print "Error reason = ", e
        print "Error at line no = ", traceback.format_exc()
        resp['message'] = 'Internal error.'
        resp['status'] = 500
    return HttpResponse(simplejson.dumps(resp), mimetype='application/json')

