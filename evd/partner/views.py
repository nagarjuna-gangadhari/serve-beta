# Create your views here.
import re
import time
import json
import MySQLdb
import simplejson
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login, logout
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseNotFound
from social_auth.backends import get_backend
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.forms.models import model_to_dict
from django.shortcuts import render
from PIL import Image as PIL
import xlwt
from xlwt import Workbook
from web.models import *
from models import *
from .form import UserForm, AddPartnerSchoolForm,SavePartnerSchoolForm, AddCenter, get_center_data
from webext.models import UpdateHistoryLog
from django.db.models import Q, Count
from django.template.loader import get_template
from django.template import Context, loader
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import ast
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import StringIO, simplejson
from django.contrib import messages
from datetime import datetime
import thread
from django.contrib.auth.hashers import check_password
import genutilities.views as genUtility
import genutilities.docStorageUtility as docStorageService
from genutilities.models import *
from django.core.files.storage import FileSystemStorage
from django.db import connection
import os
import student.views as studentApp
from student.models import *
from web.models import Offering
import genutilities.logUtility as logService
import genutilities.uploadDocumentService as docUploadService
import alerts.views as notificationModule
import genutilities.pushNotificationService as pushNotificationService
from genutilities.views import get_object_or_none, getLanguages
from django.views.generic import View
from questionbank.models import Question_Set,Question,Question_Component
from django.utils.decorators import method_decorator
from collections import defaultdict
from django.db.models import Max
import random

@csrf_exempt
def SignupView(request):
    name = request.POST.get('name')
    name_of_organization = request.POST.get('name_of_organization', '').strip()
    phone = request.POST.get('phone', '')
    email = request.POST.get('email', '')
    address = request.POST.get('address', '')
    poc_name = request.POST.get('poc_name')
    poc_phone = request.POST.get('poc_phone')
    poc_email = request.POST.get('poc_email')
    ptypes = request.POST.getlist('ptype')
    referral_id = request.POST.get('referral_id',' ')
    referalUser = None
    referal_name = ''
    """if referral_id!=' ':
        try:
            referalUser = User.objects.get(pk=referral_id)
            referal_name = str(referalUser.first_name) + " " + str(referalUser.last_name)
        except:
            pass"""

    if ptypes:
        selected_ptypes = [Partnertype.objects.get(name = ptype) for ptype in ptypes]
    else:
        selected_ptypes = []
    partner_model = {}
    if poc_email:
        existing_user = User.objects.filter(email=poc_email)
        if existing_user:
            response_data = {}
            response_data['status'] = 1
            response_data['message'] = 'User exists already, please login'
            return HttpResponse(json.dumps(response_data),mimetype="application/json")

        try:
            query = Q()
            query = query & Q(name = name_of_organization)
            query = query & ~Q(partner_id = None)
            ref_name = ReferenceChannel.objects.get(query)
            if ref_name:
                mail = ref_name.partner.email
                response_data = {}
                response_data['status'] = 1
                response_data['message'] = 'User exists already with the same Organization, here is the partner mail-id %s' % mail
                return HttpResponse(json.dumps(response_data),mimetype="application/json")
        except:
            print "exception raised"

        new_user = User.objects.create_user(email=poc_email, username=poc_email)
        password = User.objects.make_random_password()
        new_user.set_password(password)
        new_user.save()
        user = authenticate(username=poc_email, password=password)
        #login(request, user)

        userp = user.userprofile

        try:
            partner_model = Partner.objects.create(contactperson=user)
            partner_model.name = name
            partner_model.name_of_organization = name_of_organization
            partner_model.phone = phone
            partner_model.email = email
            partner_model.address = address
            partner_model.status = 'New'

            for ptype in selected_ptypes:
                partner_model.partnertype.add(ptype)

            if len(poc_name.split(' ')) == 2:
                first_name, last_name = poc_name.split(' ')
            else:
                first_name, last_name = poc_name, ''
            userp = user.userprofile
            user.first_name = first_name
            user.last_name = last_name
            userp.phone = poc_phone
            partner_model.save()

            try:
                ref_channel = ReferenceChannel.objects.get(name=name_of_organization)
            except:
                ref_channel = ''

            if ref_channel:
                ref_channel.partner = partner_model
            else:
                ref_channel, status = ReferenceChannel.objects.get_or_create(name=name_of_organization, partner = partner_model)
            ref_channel.save()

            userp.referencechannel = ref_channel

            role = Role.objects.get(name = 'Partner Admin')
            if role:
                userp.role.add(role)
                userp.pref_roles.add(role)

            """if referalUser != None and referal_name!='':
                userp.referer = referal_name
                userp.referred_user = referalUser"""
            user.save()
            userp.save()
            args = { 'username': poc_email, 'name':str(first_name)+ ' '+str(last_name),'password':password,'name_of_organization':name_of_organization}
            mail = ''
            body = ''
            subject = 'Welcome to eVidyaloka - '+str(name_of_organization)
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [poc_email]
            body = get_template('partner_signup_mail.html').render(Context(args))
            if email:
                cc = [email]
                mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
            else:
                mail = EmailMessage(subject, body, to=to, from_email=from_email)
            mail.content_subtype = 'html'
            mail.send()

            """ sub = 'Welcome To eVidyaloka - %s!' % (email)
            message = 'Thanks for logged-in\n'
            message += 'Here is your password, %s\n' % password
            message += 'Please change your password by clicking the following link.\n'
            host = 'http://' + request.META['HTTP_HOST']
            message += '%s/accounts/password/reset/' % host
            insert_into_alerts(sub, message, email, user.id, 'email')"""

        except Exception as e:
            print e.message
            return HttpResponse('Error')
        return HttpResponse("Thanks for signing-up, We've sent an email to your registered email, with contact person login credentials.")
    else:
        return HttpResponse('Please enter email-id')


def send_welcome_email(email_id, arguments):
    mail = ''
    body = ''
    subject = 'Welcome to eVidyaloka - Registration Successful !!!'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [email_id]
    body = get_template('school_onboarding_stage1.txt').render(Context(arguments))
    if email_id:
        cc = [email_id]
        mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
    else:
        mail = EmailMessage(subject, body, to=to, from_email=from_email)
    mail.content_subtype = 'html'
    mail.send()


def createNewUser(email, firstName, lastName, phone):
    new_user = User.objects.create_user(email=email,username=email)
    password = User.objects.make_random_password()
    #print "Random pswd", password
    new_user.set_password(password)
    new_user.save()
    user = authenticate(username=email, password=password)
    userp = user.userprofile
    userp.phone = phone
    userp.save()

    args = {'username': email, 'name': str(firstName) + ' ' + str(lastName), 'password': password, }

    try:
        thread.start_new_thread(send_welcome_email, (email, args))
    except:
        print "Threading failed"
    else:
        print "Sending mail is done by another thread"

    return user


def profile(request):
    curr_user =  request.user
    user_profile, partner_details = [], []
    p_html = 'profile.html'
    user_profile = UserProfile.objects.filter(user = curr_user)
    if user_profile:
        user_profile = user_profile[0]
        prefer_roles = user_profile.pref_roles.all()
        for prefer_role in prefer_roles:
            if prefer_role.name == 'Teacher':
                user_profile.pref_roles.remove(prefer_role)

        user_location_info = {}
        user_profile_dict = user_profile.get_dict()
        location_fields = ['country', 'state', 'city']
        for k,v in user_profile_dict.iteritems():
            if k in location_fields and v:
                user_location_info[k] = str(v)

        org = False
        if user_profile.profile_completion_status:
            org = True
    partner_details = Partner.objects.filter(contactperson = curr_user)
    if partner_details:
        partner_details = partner_details[0]
        ref_channel = partner_details.partner_referencechannel
        if ref_channel:
            ref_channel = ref_channel.all()
            if len(ref_channel)>0:
                ref_channel = ref_channel[0]
        else:
            ref_channel = ''
        if partner_details.partnertype.values():
            p_type = partner_details.partnertype.values()[0]['name']
            p_html = 'profile.html'

    return render(request, p_html, {"user_profile":user_profile,\
                        'partner_details' : partner_details, 'org' : org,\
                        'user_location_info': user_location_info,\
                        'ref_channel' : ref_channel})

def deliverypartner_org(request):
    user = request.user
    partner = request.user.partner_set.all()[0]
    delivery_partner = partner.delivery_partnerobj.all()
    if delivery_partner:
        delivery_partner = delivery_partner[0]
    else:
        delivery_partner = ''
    ref_channel = partner.partner_referencechannel.all()
    if ref_channel:
        ref_channel = ref_channel[0]
    else:
        ref_channel = ''
    return render(request, 'delivery_org_details.html', {'delivery_partner' : delivery_partner,\
                                            'ref_channel' : ref_channel, 'partner' : partner})

def organization_details(request):
    user = request.user
    partner = request.user.partner_set.all()[0]
    ref_channel = partner.partner_referencechannel.all()
    if ref_channel:
        ref_channel = ref_channel[0]
    else:
         ref_channel = ''
    return render(request, 'org_details.html', {'ref_channel' : ref_channel, 'partner' : partner})

def save_profile(request):
    user =  request.user
    userp = user.userprofile
    step = request.POST.get('step')
    if step == 'base_profile':
        request_to_db = {
                            'prefered_medium': 'pref_medium',
                            'alt_email': 'secondary_email'
                        }
        user_fields = [i.name for i in User._meta.fields]
        user_fields.remove('id')
        userp_fields = [i.name for i in UserProfile._meta.fields]
        userp_fields.remove('id')
        userp_fields.remove('referencechannel')
        user_update_fileds = {}
        userp_update_fileds = {}
        for k,v in request.POST.iteritems():
            k = request_to_db.get(k, k)
            if isinstance(v, list):
                v = ",".join(v)
            if k in user_fields:
                user_update_fileds[k] = v
            elif k in userp_fields:
                userp_update_fileds[k] = v
        if user_update_fileds:
            user_id = User.objects.filter(id = user.id).update(**user_update_fileds)
        if userp_update_fileds:
            userp.__dict__.update(userp_update_fileds)
            userp.save()

        userp.profile_completion_status = True

    elif step == 'org_profile':
        deliveryp_fields = [i.name for i in DeliveryPartnerOrgDetails._meta.fields]
        deliveryp_fields.remove('id')
        deliveryp_update_fileds = {}
        for k,v in request.POST.iteritems():
            if isinstance(v, list):
                v = ",".join(v)
            if k in deliveryp_fields:
                deliveryp_update_fileds[k] = v

        if deliveryp_update_fileds:
            p_id = request.user.partner_set.all()[0].id
            delivery_form, status = DeliveryPartnerOrgDetails.objects.get_or_create(partner_id = p_id)
            delivery_form.__dict__.update(**deliveryp_update_fileds)

            delivery_form.save()

        userp = request.user.userprofile
        userp.organization_complete_status = True

        #request.user.partner_set.update(status = 'Approved') # Admin should update the status, need to remove while moving ro prod

    elif step == 'school_details':
        school_fields = [i.name for i in School._meta.fields]
        school_fields.remove('id')

        school_update_fields = {}
        for k,v in request.POST.iteritems():
            if isinstance(v, list):
                v = ",".join(v)
            if k in school_fields:
                school_update_fields[k] = v

        f_name = ''
        photo = request.FILES.get('photo', '')
        if photo:
            f_path = os.getcwd()
            f_name = '/static/uploads/school/' + request.user.first_name + '_'+ photo.name
            f = open(f_path + f_name, 'w+')
            f.write(photo.read())
            f.close()

            image = PIL.open(f_path + f_name)
            image.thumbnail([150,150], PIL.ANTIALIAS)
            image.save(f_path + f_name, image.format, quality=90)

        if school_update_fields:
            school_form, status = School.objects.get_or_create(name= request.POST['name'])
            school_form.__dict__.update(**school_update_fields)

            school_form.photo = f_name
            school_form.created_by_id = request.user.id

            school_form.save()

    try:
        user.save()
        userp.save()
    except Exception as e:
        print e
        return HttpResponse('Error')
    return HttpResponse('Success')

def volunteer_dash(request):
    return render(request, 'volunteer_dash.html', {})

def has_role(self, role):
    if len(self.role.filter(name = role)) > 0:
        return True
    else:
        return False

def has_pref_role(self, role):
    if len(self.pref_roles.filter(name = role)) > 0:
        return True
    else:
        return False

@csrf_exempt
@login_required
def get_partners_details(request):

    search_params = parse_datatable_request_params(request)

    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    users_cur = db.cursor(MySQLdb.cursors.DictCursor)

    equal_to_fields = ["id"]
    date_fields     = ["last_login", "date_joined", "from_date", "to_date"]
    boolean_fields  = [
                        "is_active", "profile_completion_status", "self_eval",
                        "computer", "evd_rep", "trainings_complete",
                        "code_conduct", "review_resources", "availability"
                      ]
    text_fields     = ["short_notes"]
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

    #import pdb;pdb.set_trace()
    newline_seperator = "</br>"
    if search_params.get("download_excel", 'false') == 'true':
        newline_seperator = "\n"

    conditions_query = []
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

            alias_name =  db_field
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
            conditions_query.append(search_value_query)

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

            alias_name =  db_field
            db_field   = field_alias_to_db.get(db_field, db_field)
            if isinstance(value, list):
                value = ",".join("\"{}\"".format(i) for i in value)
                search_query.append("{}.{} in ({})".format(table_alias_name, db_field, value))
            elif db_field in equal_to_fields or alias_name in equal_to_fields:
                search_query.append("{}.{} = \"{}\"".format(table_alias_name, db_field, value))
            else:
                search_query.append("{}.{} like \"%{}%\"".format(table_alias_name, db_field, value))

        if search_query:
            search_columns_query = " AND ".join(search_query)
            conditions_query.append(search_columns_query)
    if request.user.partner_set.values():
        org_name = request.user.partner_set.values()[0]['name_of_organization']
        try:
            org = ReferenceChannel.objects.get(name = org_name)
        except:
            org = None
        if org !=None:
            conditions_query.append("UP.referencechannel_id = %s" % org.id)
        #conditions_query.append("WS.status = 'Completed'")

    if conditions_query  and org !=None:
        base_query.append("WHERE")
        search_final_query = " AND ".join(i for i in conditions_query if i)
        base_query.append(search_final_query)

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
    page_limit   = search_params.get("per_page_length", "-1")
    if page_limit != "-1":
        base_query.append("LIMIT {},{};".format(start_offset, page_limit))

    final_query = " ".join(base_query)
    response_data["iTotalRecords"] = get_total_matched_count(users_cur, final_query)
    response_data["iTotalDisplayRecords"] = response_data["iTotalRecords"]
    try:
        users_cur.execute(final_query)
    except Warning:
        pass
    users = users_cur.fetchall()
    data = response_data["aaData"]
    for user_index, user in enumerate(users):
        user_profile_id = ''
        roles_data   = []
        role_status_dict  = {}
        role_outcome_dict = {}
        role_onboarding_status_dict = {}
        role_availability_dict = {}

        removed_none = dict((k,"") for k,v in user.iteritems() if v is None)
        if removed_none:
            user.update(removed_none)

        for boolean_field in boolean_fields:
            if user.has_key(boolean_field):
                if boolean_field == "availability":
                    user[boolean_field] = ",".join(['True' if x=='1' else 'False'  for x in user[boolean_field].split(',') ])
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

            role_ids     = [i.strip() for i in user.get('role_id', "").split(',')]
            role_names   = [i.strip() for i in user.get('name', "").split(',')]
            role_outcome = [i.strip() for i in user.get('role_outcome', "").split(',')]
            role_status  = [i.strip() for i in user.get('role_status', "").split(',')]
            role_onboarding_status = [i.strip() for i in user['role_onboarding_status'].split(',')]
            role_availability = [i.strip() for i in user['availability'].split(',')]

            for index, role_id in enumerate(role_ids):
                roles_dict = {}
                if not role_id:
                    continue

                roles_dict["role_id"] = role_id
                if len(role_names) >= (index+1):
                    roles_dict["name"]         = role_names[index]
                else:
                    roles_dict["name"]         = ""

                if len(role_outcome) >= (index+1):
                    role_outcome_dict[role_id] = role_outcome[index]
                else:
                    role_outcome_dict[role_id] = ""

                if len(role_status) >= (index+1):
                    role_status_dict[role_id] = role_status[index]
                else:
                    role_status_dict[role_id] = ""

                if len(role_onboarding_status) >= (index+1):
                    role_onboarding_status_dict[role_id] = role_onboarding_status[index]
                else:
                    role_onboarding_status_dict[role_id] = ""

                if len(role_availability) >= (index+1):
                    role_availability_dict[role_id] = role_availability[index]
                else:
                    role_availability_dict[role_id] = ""

                if roles_dict:
                    roles_data.append(roles_dict)

        dates_fields = {}
        select_fields = field_table_alias_name.keys()
        record = dict((k, user[k]) for k in select_fields if user.has_key(k) and k not in date_fields)
        for date_field in date_fields:
            if not user.has_key(date_field):
                continue
            if user[date_field]:
                dates_fields[date_field] = user[date_field].strftime('%Y-%m-%d %H:%M')
            else:
                dates_fields[date_field] = ""

        if dates_fields:
            record.update(dates_fields)

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
        record['role_status']    = role_status_dict
        record['role_outcome']   = role_outcome_dict
        record['role_onboarding_status'] = role_onboarding_status_dict
        record['availability'] = role_availability_dict

        data.append(record)
    users_cur.close()
    if search_params.get("download_excel", 'false') == 'true':
        excel_reponse_data = generate_volunteerdb_excel(request.user.id, response_data)
        dump_json = simplejson.dumps(excel_reponse_data)
    else:
        dump_json = simplejson.dumps(response_data)
    return HttpResponse(dump_json,mimetype='application/json')


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
        {"name": "Status", "data": "status"},
        {"name": "Active Teacher", "data": "is_active_teacher"},
        {"name": "Center", "data": "center_name"},
        {"name": "Preferred Roles", "data": "prefered_roles"},
        {"name": "Role Status", "data": "role_status"},
        {"name": "Role Outcome", "data": "role_outcome"},
        {"name": "Role Completion Status", "data": "role_onboarding_status"},
        # {"name": "Recommended Date", "data": "recommended_date"},
        {"name": "Profile Completion Status", "data": "profile_completion_status"},
        {"name": "Skype ID", "data": "skype_id"},
        # {"name": "Reference Channel", "data": "reference_channel"},
        {"name": "Orientation", "data": "evd_rep"},
        {"name": "Computer", "data": "computer"},
        {"name": "Availability", "data": "availability"},
        {"name": "Available From", "data": "from_date"},
        {"name": "Available Till", "data": "to_date"},
        {"name": "Last Login", "data": "last_login"},
        {"name": "Joined Date", "data": "date_joined"},
        {"name": "Short Notes", "data": "short_notes"}]

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
                    value = " ,".join("{}:{}".format(i['role_id'], i['name']) for i in value)
                else:
                    value = " \n".join("{}:{}".format(k, v) for k, v in value.iteritems())
            ws.write(i + 1, j, value)

    fname = os.path.join(download_path, 'volunteerdb_data_{}.xls'.format(user_id))
    if os.path.isfile(fname):
        os.remove(fname)

    download_link = fname.replace(settings.PROJECT_DIR, "")
    wb.save(fname)
    return {"excel_link": download_link}


def parse_datatable_request_params(request):
    request_params = {
                        'search_columns': {}, 'order_by_columns': {}, 'search_value': '',
                        'start': 0, 'per_page_length': 20, 'searchable_fields': [],
                        'download_excel': "false"
                     }

    data = request.POST
    for key,value in data.iteritems():
        order_column_re  = re.search('order\[(\d+)\]\[column\]', key)
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
                        'pref_days', 'pref_slots', 'short_notes'
                      ]

    web_role = [ 'name' ]
    userprofile_role = [ 'role_id' ]
    web_rolepreference = ['role_status', 'role_outcome', 'role_onboarding_status', 'availability']

    web_offering = ['status{}is_active_teacher'.format(as_seperator)]
    web_session = ['status{}class_status'.format(as_seperator)]
    web_course = ['grade', 'subject']
    web_offering = ['status{}is_active_teacher'.format(as_seperator)]
    web_referencechannel = ['name{}reference_channel'.format(as_seperator)]

    web_center = ['name{}center_name'.format(as_seperator),
                'state{}center_state'.format(as_seperator), 'village']

    field_table_alias_name = OrderedDict()
    field_table_alias_name.update(dict((i.strip(), "U") for i in auth_user))
    field_table_alias_name.update(dict((i.strip(), "UP") for i in web_userprofile))
    field_table_alias_name.update(dict((i.strip(), "R") for i in web_role))
    field_table_alias_name.update(dict((i.strip(), "UR") for i in userprofile_role))
    field_table_alias_name.update(dict((i.strip(), "RP") for i in web_rolepreference))
    field_table_alias_name.update(dict((i.strip(), "WOF") for i in web_offering))
    field_table_alias_name.update(dict((i.strip(), "WC") for i in web_center))
    field_table_alias_name.update(dict((i.strip(), "WS") for i in web_session))
    field_table_alias_name.update(dict((i.strip(), "C") for i in web_course))

    select_fields_list = []
    for k,v in field_table_alias_name.iteritems():
        if k in web_role or k in userprofile_role or k in web_rolepreference:
            select_fields_list.append("GROUP_CONCAT({}.{} SEPARATOR ',') as {}".format(v,k,k))
        else:
            select_fields_list.append("{}.{}".format(v,k))

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
                        "LEFT JOIN web_session WS ON WOF.id = WS.offering_id",
                        "LEFT JOIN web_course C ON WOF.course_id = C.id"
                       ]

    base_query.append(" ".join(left_join_tables))
    base_query = " ".join(base_query)

    #Generating Field Alias mapping dict
    field_alias_to_db = {}
    for k,v in field_table_alias_name.iteritems():
        if as_seperator not in k:
            continue

        db_field, alias_name = k.split(as_seperator)
        dict_value = field_table_alias_name.pop(k)
        field_table_alias_name[alias_name] = dict_value
        field_alias_to_db[alias_name.strip()] = db_field.strip()

    return base_query, field_table_alias_name, field_alias_to_db

def get_total_matched_count(cursor, final_query):

    total_count = 0

    #replacing select fields by count to get the matching count
    re_search = re.search("select (.*?)from ", final_query, re.IGNORECASE)
    if not re_search:
        return total_count

    matched_string = "".join(re.findall(re_search.re, final_query))
    count_query = final_query.replace(matched_string, 'count(*) as count ')

    #Remove Limit
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

@login_required
def add_schools(request):
    school_name = request.GET.get('school_id', '')
#     school_detail = 'select * from web_school where name="'+school_name+'"'
    school_detail = School.objects.filter(name = school_name)
#     print "addschool",school_detail[0].name," dist",school_detail[0].district_details," cont",school_detail[0].contact_details
    partner_admins = Partner.objects.all()

    return render(request, "school.html", {'partner_admins' : partner_admins, 'school_detail':school_detail})

def my_schools(request):
    return render(request, 'school_dash.html', {})

@csrf_exempt
def get_school_details(request):

    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                    user=settings.DATABASES['default']['USER'],
                    passwd=settings.DATABASES['default']['PASSWORD'],
                    db=settings.DATABASES['default']['NAME'],
                    charset="utf8",
                    use_unicode=True)
    users_cur = db.cursor(MySQLdb.cursors.DictCursor)

    response_data = {"iTotalRecords": 0, "iTotalDisplayRecords": 0, "aaData": []}

    final_query = 'select name, district_details, typeofmgmt, noofchildren, headmaster_incharge, \
            grades_inschool, current_teacher, school_number, ledtv_available,\
            web_camera from web_school where created_by_id = %s' % request.user.id

    #print final_query
    response_data["iTotalRecords"] = get_total_matched_count(users_cur, final_query)
    response_data["iTotalDisplayRecords"] = response_data["iTotalRecords"]
    try:
        users_cur.execute(final_query)
    except Warning:
        pass

    users = users_cur.fetchall()
    data = response_data["aaData"]
    for user_index, user in enumerate(users):
        data.append(user)

    users_cur.close()

    dump_json = simplejson.dumps(response_data)
    return HttpResponse(dump_json,mimetype='application/json')

def insert_into_alerts(sub, body, recipients, user, _type):

    conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
        user=settings.DATABASES['default']['USER'],
        passwd=settings.DATABASES['default']['PASSWORD'],
        db=settings.DATABASES['default']['NAME'],
        charset="utf8",
        use_unicode=True)

    cur_time = datetime.now()

    cursor = conn.cursor()
    if _type == 'sms':
        mes = sub
    else:
        mes = sub + '#<>#' + body
    status = 'pending'

    query = "insert into Alerts(message, type, status, recipients, user, dt_added, dt_updated) values('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    values = (mes,  _type, status, recipients, user, cur_time, cur_time)
    cursor.execute(query%values)
    conn.commit()

    cursor.close()
    conn.close()

#volunteer_partner_contributions
def contributions(request):
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                        user=settings.DATABASES['default']['USER'],
                        passwd=settings.DATABASES['default']['PASSWORD'],
                        db=settings.DATABASES['default']['NAME'],
                        charset="utf8",
                        use_unicode=True)
    users_cur = db.cursor(MySQLdb.cursors.DictCursor)
    if has_role(request.user.userprofile, "Partner Account Manager") or has_pref_role(request.user.userprofile, "Partner Account Manager"):
        query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
        users_cur.execute(query)
        partner_id = [str(each['value']) for each in users_cur.fetchall()]
        partner_id.sort()
    else:
        partner_id = Partner.objects.filter(contactperson_id=request.user.id).values_list('id', flat=True)
                
    ref_channel_id = ReferenceChannel.objects.filter(partner_id__in= partner_id).values_list("id", flat=True)
    resp = ''
    if len(ref_channel_id)>1:
        ref_channel_id = tuple(map(int,ref_channel_id))
        my_users_query = ("select au.id from auth_user au, web_userprofile up where au.id = up.user_id and up.referencechannel_id in "+str(ref_channel_id)+" ")  
    else:
        ref_channel_id = ref_channel_id[0]
        my_users_query = ("select au.id from auth_user au, web_userprofile up where au.id = up.user_id and up.referencechannel_id = %s") %(ref_channel_id)
    users_cur.execute(my_users_query)
    my_users_list = [usr['id'] for usr in users_cur.fetchall()]
    offerings_query = "select wo.active_teacher_id as user_id, CONCAT_WS(' ', au.first_name, au.last_name) as user_name, wr.name as reference_channel ,wo.id as offering_id, \
                       wc.id as center_id, CONCAT_WS('-',wc.name, wc.state)  as center_name, CONCAT_WS(' ',wco.board_name, subject) as subject, \
                       wco.grade as grade, wc.language as language, DATE(wo.start_date) as start_date, DATE(wo.end_date) as end_date\
                       from web_offering wo, auth_user au,web_userprofile wu,web_referencechannel wr, web_center wc, web_course wco \
                       where wo.course_id = wco.id and au.id = wo.active_teacher_id and wo.center_id = wc.id and wu.user_id=wo.active_teacher_id and wu.referencechannel_id =wr.id and \
                       wo.active_teacher_id in (" + ','.join(map(str,my_users_list)) + ")"
    users_cur.execute(offerings_query)
    resp = users_cur.fetchall()

    for offer in resp:
            offering = Offering.objects.get(id=offer['offering_id'])
            offer['stud_enrolled'] = offering.enrolled_students.count()
            offer['sess_sched'] = offering.session_set.filter(status="scheduled",teacher = offering.active_teacher).count()
            offer['sess_compl'] = offering.session_set.filter(status="completed",teacher = offering.active_teacher).count()
            offer['sess_cancl'] = offering.session_set.filter(status="cancelled",teacher = offering.active_teacher).count()

    db.close()
    users_cur.close()
    return render(request, 'contributions.html', {'offerings': resp})


@csrf_exempt
@login_required
def get_offering_details(request):
    offering_id = request.POST.get("id",'')
    if offering_id:
        offering = Offering.objects.get(id=offering_id)
        resp = OrderedDict([
                ("Grade", offering.course.grade),
                ("Subject", offering.course.subject),
                ("Start Date", offering.start_date.strftime('%Y-%m-%d')),
                ("End Date", offering.end_date.strftime('%Y-%m-%d')),
                ("Students enrolled", offering.enrolled_students.count()),
                ("Sessions Completed", offering.session_set.filter(status="scheduled").count()),
                ("Sessions Scheduled", offering.session_set.filter(status="completed").count()),
                ("Sessions Cancelled", offering.session_set.filter(status="cancelled").count())
               ])

    else:
        resp = "Error Occured"

    return HttpResponse(simplejson.dumps(resp),mimetype='application/json')

@csrf_exempt
def get_partner_school(request):
#     ''' Function to search School information from Master School table for a Partner '''
    #print "\n***** REQUEST ****** ", request.user.id
    if request.method == 'GET':
        schoolId = request.GET.get('schoolId', '')
        schoolname = request.GET.get('schoolname', '')
        user_type = request.GET.get('user_type', '')
        print "=================================================", user_type
        #print "\n******* SCHOOL ID ****** \n", schoolId
        isAPartnerAdmin = False
        isAddedByMe = False
        anotherPartnerSchool = False
        userloggedIn = False
        is_school_admin = False
        # if request.user.schooladmin_set.values():
        #     is_school_admin = True
        #     userp = request.user.userprofile
        #     print(userp.organization_complete_status)
        #     if userp.organization_complete_status == 'Incomplete':
        #         org_complete_status = False
        #         schoolId = School.objects.filter(created_by=request.user)
        #         SchoolId = schoolId[0].id
        #         is_new_profile = True
        if schoolId != "":
            isAPartnerAdmin = False
            isAddedByMe = False
            anotherPartnerSchool = False
            userloggedIn = False
        #     # user_profile = UserProfile.objects.filter(user = request.user)
        #     user_location_info = {}
            # if user_profile:
            #     user_profile = user_profile[0]
            #     prefer_roles = user_profile.pref_roles.all()
            #     for prefer_role in prefer_roles:
            #         if prefer_role.name == 'Teacher':
            #             user_profile.pref_roles.remove(prefer_role)
            #     user_profile_dict = user_profile.get_dict()
            #     location_fields = ['country', 'state', 'city']
            #     for k,v in user_profile_dict.iteritems():
            #         if k in location_fields and v:
            #             user_location_info[k] = str(v)
            
            try:
                school = School.objects.only( 'id','name','school_code','village','district_details','grades_inschool', 'pincode').get(id = schoolId)
            except School.DoesNotExist:
                pass
            else:
                if request.user.id is not None:
                    #print "\n******* USER IS LOGGED IN *******\n"
                    userloggedIn = True

                if userloggedIn:
                    try:
                        school_admin = Partner.objects.filter(contactperson=request.user)
                        if school_admin.count() and school_admin[0].role_id and school_admin[0].role_id == '16':
                            is_school_admin = True
                        school_data = getMySchoolBySchoolId(schoolId, request.user.id)
                        if len(school_data) > 0:
                            isAddedByMe = True
                    except:
                        pass

                    try:
                        Partner.objects.get(contactperson_id=request.user.id)
                    except Partner.DoesNotExist:
                        pass
                    except Partner.MultipleObjectsReturned:
                        isAPartnerAdmin = True
                    else:
                        isAPartnerAdmin = True

                if not isAddedByMe:
                    school_data = getMySchoolBySchoolId(schoolId, "")
                    if len(school_data) > 0:
                        anotherPartnerSchool = True
            # if is_new_profile:
                # success_msg = 'Username and password sent to email.'
                # return render(request,'school_onboarding_stage1.html',{'schoolId':schoolId, 'schoolname':schoolname, 'school':school,'school_flag':True,'userloggedIn':userloggedIn,'iAmPartnerSchool':isAddedByMe,'anotherPartnerSchool':anotherPartnerSchool, 'isAPartnerAdmin':isAPartnerAdmin, 'is_school_admin':is_school_admin, 'org_complete_status':org_complete_status, "user_location_info" : user_location_info, 'successmsg' : success_msg})
                # return render(request,'school_onboarding_stage1.html',{'schoolId':schoolId, 'schoolname':schoolname, 'school':school,'school_flag':True,'userloggedIn':userloggedIn,'iAmPartnerSchool':isAddedByMe,'anotherPartnerSchool':anotherPartnerSchool, 'isAPartnerAdmin':isAPartnerAdmin})
            return render(request,'school_onboarding_stage1.html',{'schoolId':schoolId, 'schoolname':schoolname, 'school':school,'school_flag':True,'userloggedIn':userloggedIn,'iAmPartnerSchool':isAddedByMe,'anotherPartnerSchool':anotherPartnerSchool, 'isAPartnerAdmin':isAPartnerAdmin, 'user_type':user_type, 'is_school_admin':is_school_admin})
        else:
            #print "****** School Id ", schoolId
            return render(request,'school_onboarding_stage1.html',{'school_flag':False})#, 'is_school_admin':is_school_admin, 'org_complete_status': org_complete_status})
    elif request.method == 'POST':
        try:
            is_logged_in = request.POST.get('is_logged_in') == 'true'
            exisiting_user = is_logged_in
            adding_user = None
            first_name = ''
            user_email = ''

            if not is_logged_in:
                user_email = request.POST.get('email_id', '')
                first_name = request.POST.get('first_name', '')
                try:
                    adding_user = User.objects.get(email = user_email)
                except User.DoesNotExist:
                    pass
                except User.MultipleObjectsReturned:
                    adding_user = User.objects.filter(email = user_email).order_by('id')[0]
                    exisiting_user = True
                else:
                    exisiting_user = True
            if not exisiting_user:
                last_name = request.POST.get('last_name')
                phone_number = request.POST.get('phone_number')
                new_user = createNewUser(user_email, first_name, last_name, phone_number)
                user_profile = new_user.userprofile
                new_user.first_name = first_name
                new_user.last_name = last_name
                role = Role.objects.get(name='Well Wisher')
                if role:
                    user_profile.role.add(role)
                    user_profile.pref_roles.add(role)
                new_user.save()
                user_profile.save()
                adding_user = new_user

            school_id = request.POST.get('school_id')
            school_data = School.objects.only('id', 'name', 'school_code', 'village', 'district_details').get(id=school_id)

            grades_in_school = []

            if request.POST.get('grade5') == 'true':
                grades_in_school.append('5')
            if request.POST.get('grade6') == 'true':
                grades_in_school.append('6')
            if request.POST.get('grade7') == 'true':
                grades_in_school.append('7')
            if request.POST.get('grade8') == 'true':
                grades_in_school.append('8')

            grades_in_school = ",".join(grades_in_school)
            teachers_available = request.POST.get('teachers_available', '') if request.POST.get('teachers_available', '') else '0'
            teachers_required = request.POST.get('teachers_required', '') if request.POST.get('teachers_required', '') else '0'
            num_of_teachers_available = int(teachers_available)
            num_of_teachers_required = int(teachers_required)
            has_electricity = request.POST.get('electricity') == 'true'
            has_computer = request.POST.get('computer') == 'true'
            has_projector = request.POST.get('projector') == 'true'
            has_internet = request.POST.get('internet') == 'true'

            added_by_user = adding_user
            partner_data = None
            schooladmin_data = None
            school_admin = 0
            if is_logged_in:
                added_by_user = request.user
                school_admin = Partner.objects.filter(contactperson=request.user)
                if school_admin.count() and school_admin[0].role_id and school_admin[0].role_id == '16':
                    try:
                        schooladmin_data = Partner.objects.get(contactperson_id=added_by_user.id)
                    except Schooladmin.DoesNotExist:
                        schooladmin_data = None
                    except Schooladmin.MultipleObjectsReturned:
                        schooladmin_data = Partner.objects.filter(contactperson_id=added_by_user.id).order_by('id')[0]
                else:
                    try:
                        partner_data = Partner.objects.get(contactperson_id=added_by_user.id)
                    except Partner.DoesNotExist:
                        partner_data = None
                    except Partner.MultipleObjectsReturned:
                        partner_data = Partner.objects.filter(contactperson_id=added_by_user.id).order_by('id')[0]
            if school_admin.count() and school_admin[0].role_id == '16':
                if schooladmin_data is not None:
                    new_school = MySchool.objects.create(school=school_data, partner_id=schooladmin_data.id,
                                                        status="Verified", added_by=added_by_user,
                                                        grades_in_school=grades_in_school,
                                                        teachers_available=num_of_teachers_available,
                                                        teachers_required=num_of_teachers_required,
                                                        electricity=has_electricity,
                                                        computer=has_computer, projector_or_led=has_projector,
                                                        internet=has_internet)
                else:
                    new_school = MySchool.objects.create(school=school_data, status="New", added_by=added_by_user,
                                                        grades_in_school=grades_in_school,
                                                        teachers_available=num_of_teachers_available,
                                                        teachers_required=num_of_teachers_required,
                                                        electricity=has_electricity,
                                                        computer=has_computer, projector_or_led=has_projector,
                                                        internet=has_internet)
            else:
                if partner_data is not None:
                    new_school = MySchool.objects.create(school=school_data, partner_id=partner_data.id,
                                                        status="New", added_by=added_by_user,
                                                        grades_in_school=grades_in_school,
                                                        teachers_available=num_of_teachers_available,
                                                        teachers_required=num_of_teachers_required,
                                                        electricity=has_electricity,
                                                        computer=has_computer, projector_or_led=has_projector,
                                                        internet=has_internet)
                else:
                    try:
                        user_reference_channel_id = UserProfile.objects.values_list("referencechannel_id",flat=True).filter(user_id = request.user.id)[0]
                        partner_id = ReferenceChannel.objects.values_list("partner_id",flat=True).filter(id = user_reference_channel_id)[0]
                    except:
                        partner_id = ""
                    new_school = MySchool.objects.create(school=school_data, status="New",partner_id=partner_id, added_by=added_by_user,
                                                        grades_in_school=grades_in_school,
                                                        teachers_available=num_of_teachers_available,
                                                        teachers_required=num_of_teachers_required,
                                                        electricity=has_electricity,
                                                        computer=has_computer, projector_or_led=has_projector,
                                                        internet=has_internet)

            new_school.save()

            return_message = "New school on-boarding registration is successful."
            redirect_blank = ""
            redirect_self = "/myevidyaloka/"
            if exisiting_user:
                if school_admin:
                    # return_message += "\n\nPlease initiate verification of school you have added"
                    redirect_self = '/v2/myschools/'
                else:
                    if not is_logged_in:
                        return_message += "\n\nPlease initiate verification of school you have added through 'My Schools' " \
                                    "option in your profile page after login."
                    if is_logged_in and partner_data is None:
                        return_message += "\n\nPlease initiate verification of school you have added through 'My Schools' " \
                                        "option in your profile page."
                        redirect_self = "/v2/vLounge#schoolslist"
                    elif partner_data is not None:
                        return_message += "\n\nPlease initiate verification of school you have added"
                        redirect_self = "/partner/myschools/"
            else:
                return_message += "\nThank you {} for joining eVidyaloka and care for the society " \
                                "by promoting education.\n\nLogin details are sent to your registered e-mail id." \
                                "\nPlease initiate verification of school you have added through 'My Schools' " \
                                "option in your profile page after login.".format(first_name)
                redirect_blank = "http://" + user_email.split("@")[-1]

            return HttpResponse(simplejson.dumps({"message": return_message, "redirect_blank": redirect_blank,
                                                "redirect_self": redirect_self}), mimetype='application/json')
        except Exception as e:
            print("Error reason ---------------", e)
            print("Error at line no ---------------------------", traceback.format_exc())


@csrf_exempt
def setSchoolDetail(school, request) :
    grade = getGrade(request)
    school.grades_inschool = grade
    teachersAvailable = request.POST.get('teachersAvailable', '')
    teachersRequired = request.POST.get('teachersRequired', '')

    facilityElectricity = request.POST.get('facilityElectricity', '')
    facilityWorkingComputer = request.POST.get('facilityWorkingComputer', '')

    facilityProjector = request.POST.get('facilityProjector', '')
    facilityInternet = request.POST.get('facilityInternet', '')

    return school


@csrf_exempt
def getGrade(request) :
    grade =""
    grade5 = request.POST.get('grade5', '')
    grade6 = request.POST.get('grade6', '')
    grade7 = request.POST.get('grade7', '')
    grade8 = request.POST.get('grade8', '')
    if grade5:
        grade += grade5
    if grade6:
        grade += grade6
    if grade7:
        grade += grade7
    if grade8:
        grade += grade8

    return grade


@csrf_exempt
def getMySchoolBySchoolId(schoolId, userId):
    #print "\n***** getMySchoolBySchoolId ******** ", schoolId, userId
    myschool = None
    if schoolId :
        if not userId:
            myschool = MySchool.objects.filter(school_id=schoolId).values_list("added_by_id")
            # try:
            #     myschool = MySchool.objects.filter(school_id = schoolId)
            # except MySchool.DoesNotExist:
            #     pass
        else:
            myschool = MySchool.objects.filter(school_id=schoolId, added_by_id=userId).values_list("added_by_id")
            # try:
            #     myschool = MySchool.objects.filter(school_id = schoolId, added_by_id = userId)
            # except MySchool.DoesNotExist:
            #     pass
            # else:
        #print "\n****** ", myschool
    return myschool

    # print "In side ==", schoolId
    # db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
    #             user=settings.DATABASES['default']['USER'],
    #             passwd=settings.DATABASES['default']['PASSWORD'],
    #             db=settings.DATABASES['default']['NAME'],
    #             charset="utf8",
    #             use_unicode=True)
    # tot_user_cur = db.cursor()
    # dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
    # query=""
    # myschool =""
    # try:
    #     query = " select id,school_id,partner_id from partner_myschool where school_id = '"+schoolId+"'"
    #     if userId :
    #         query += " and added_by_id='"+ userId+"'"
    #     dict_cur.execute(query)
    #     myschool = dict_cur.fetchone()
    #
    # except:
    #     pass
    #
    # db.close()
    # dict_cur.close()
    # return myschool


@csrf_exempt
def getSchoolById(schoolId):
    school=""
    if schoolId :
        school = School.objects.get()
        print "In side ==", schoolId
        db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                    user=settings.DATABASES['default']['USER'],
                    passwd=settings.DATABASES['default']['PASSWORD'],
                    db=settings.DATABASES['default']['NAME'],
                    charset="utf8",
                    use_unicode=True)
        tot_user_cur = db.cursor()
        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query=""
        school =""
        try:
            query = " select id,name,school_code,village,district_details,grades_inschool, pincode from web_school where id = '"+schoolId+"'"
            dict_cur.execute(query)
            school = dict_cur.fetchone()

        except:
            pass

        db.close()
        dict_cur.close()
        return school

@login_required
def save_partner_school(request):
    ''' Function to save School information to a Partner in MySchool table'''

    if request.method == 'POST':
        form = SavePartnerSchoolForm(request.POST)
        if form.is_valid():
            partner_id = form.cleaned_data['partner']
            school_id = form.cleaned_data['school']
            try:
                partner = Partner.objects.get(id=partner_id,status='Approved')
                school = School.objects.only('id','name','school_code','headmaster_incharge','principal','pincode','village','district_details').get(id=school_id)
                partner_myschools = MySchool.objects.filter(partner_id=partner.id,school_id=school.id)
                if partner_myschools.count() == 0 :
                    myschool = MySchool.objects.create(partner=partner,school=school,added_by=request.user)
                    myschool.save()

                    subject = 'School '+str(school.name) + ", added for eVidyaloka consideration."
                    to = [partner.contactperson.email]
                    cc = ['evplus@evidyaloka.org']
                    from_email = settings.DEFAULT_FROM_EMAIL
                    ctx = {'partner_name': str(partner.contactperson.first_name) + ' ' + str(partner.contactperson.last_name),'created_on':myschool.added_on,'status':myschool.status,
                           'school_name': school.name,'schoolcode':school.school_code,'village':school.village,'district':school.district_details,'myschool_id':myschool.id}
                    message = get_template('partner_school_addition_mail.html').render(Context(ctx))
                    msg = EmailMessage(subject, message, to=to, cc=cc, from_email=from_email)
                    msg.content_subtype = 'html'
                    msg.send()
                    return HttpResponseRedirect('/partner/myschool/%s/' % myschool.id)
                else:
                    error_msg = "This School is already added to this Partner"
                    return render(request, 'add_partner_school.html', {'form': form, 'error_msg': error_msg})
            except Partner.DoesNotExist:
                error_msg = "Become a Partner to Add School"
                return render(request, 'add_partner_school.html', {'form': form, 'error_msg': error_msg})
            except School.DoesNotExist:
                error_msg = "Something went wrong. Please search School again"
                return render(request, 'add_partner_school.html', {'form': form, 'error_msg': error_msg})
        else:
            return HttpResponseRedirect('/school/search/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def view_partner_myschool(request,myschool_id=None,tab_name='',error_msg=''):
    ''' Function to view requested School information '''
    try:
        partner_name = request.user.first_name+" "+request.user.last_name
        is_delivery_partner_id = Partner.objects.values_list("partnertype",flat = True).filter(name = partner_name,partnertype = "2")
        if is_delivery_partner_id:
            is_delivery_partner = True
        else:
            is_delivery_partner = ""
    except:
        is_delivery_partner = ""
    is_pam = False
    is_school_admin = False
    school = 0
    if request.method == "GET":
        try:
            partner = Partner.objects.get(contactperson=request.user)
        except:
            partner = ""
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@patrner",partner)
        try:
            if myschool_id:
                if request.user.is_superuser:
                    myschool = MySchool.objects.select_related('school','partner').get(id=myschool_id)
                else:

                    usrprof = UserProfile.objects.get(user=request.user)
                    uroles = usrprof.role.all()
                    rolesrequired = uroles.filter(Q(name='Field co-ordinator') | Q(name='Partner Admin') | Q(name='OUAdmin')| Q(name='Partner Account Manager') | Q(name='School Admin'))
                    rolepreference_outcome = []
                    for role in rolesrequired:
                        try:
                            roleprefe = RolePreference.objects.get(userprofile_id=usrprof.id, role_id=role.id)
                            if roleprefe.role_status == 'New' or roleprefe.role_status == 'Active':
                                rolepreference_outcome.append(roleprefe.role_outcome)
                        except RolePreference.DoesNotExist:
                            pass
                    parnter_count = Partner.objects.filter(contactperson=request.user,status='Approved').count()
                    user_refchanel_partner = False
                    if usrprof.referencechannel:
                        if usrprof.referencechannel.partner_id:
                            user_refchanel_partner = True
                    if (user_refchanel_partner and (rolesrequired.count() > 0) and ('Recommended' in rolepreference_outcome)) or parnter_count > 0:
                        if parnter_count > 0:
                            partner = Partner.objects.get(contactperson=request.user, status='Approved')
                        elif usrprof.referencechannel.partner_id:
                            if usrprof.referencechannel.partner.status == 'Approved':
                                partner = usrprof.referencechannel.partner
                            else:
                                return HttpResponseRedirect('/profile/')
                        else:
                            return HttpResponseRedirect('/profile/')
                        if uroles.filter(name='OUAdmin').count()>0:
                            myschool = MySchool.objects.select_related('school', 'partner').filter(center__orgunit_partner=partner).get(id=myschool_id)
                            # print "wwwwwwwwwwwww",myschool
                        elif uroles.filter(name='School Admin').count() > 0:
                            is_school_admin = True
                            myschool = MySchool.objects.select_related('school', 'partner').filter(partner_id=partner).get(id=myschool_id)
                        elif uroles.filter(name='Partner Account Manager').count() > 0:
                            is_pam = True
                            db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)

                            dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
                            query = "select partner_id as value from partner_partner_partnertype where pam= '"+str(request.user.id)+"'"
                            dict_cur.execute(query)
                            partner = [str(each['value']) for each in dict_cur.fetchall()]
                            partner.sort()
                            myschool  = MySchool.objects.select_related('school', 'partner').filter( (Q(partner_id__in=partner) |Q(center__funding_partner_id__in=partner) | Q(center__delivery_partner_id__in=partner))).distinct().get(id=myschool_id)

                            db.close()
                            dict_cur.close()                            
                        else:
                            myschool = MySchool.objects.select_related('school','partner').filter(Q(partner_id=partner)|Q(center__delivery_partner=partner)|Q(center__funding_partner=partner)|Q(added_by_id=request.user.id)).distinct().get(id=myschool_id)
                            
                myschoolstatus = MySchoolStatus.objects.filter(myschool=myschool).distinct()
                # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@schoool",myschoolstatus)
                # for msstatus in myschoolstatus:
                #     if msstatus.other_info:
                #         msstatus.other_info = ast.literal_eval(msstatus.other_info)

                log_history = UpdateHistoryLog.objects.filter(referred_table_id=myschool.school.id,log_type='1').order_by('-id')
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
                is_funding_partner = ""
                if partner:
                    try:
                        is_funding_partner = Partner.objects.values("partnertype").filter(contactperson=request.user,partnertype=3)
                    except:
                        is_funding_partner = ""
                else:
                    is_funding_partner = ""
                return render(request,'view_partner_myschool.html',{'myschool':myschool,'myschoolstatus':myschoolstatus,'is_super':request.user.is_superuser,'tab':tab_name,'error_msg':error_msg,'log':log,"is_partner":partner,"partner":partner,"school":1,"is_deliver_partner":is_delivery_partner,
                                            "is_funding_partner":is_funding_partner,'is_pam':is_pam, 'is_school_admin' : is_school_admin, 'is_orgUnit':has_role(request.user.userprofile,'OUAdmin')})
            else:
                return HttpResponseRedirect('/partner/myschools/')
        except (MySchool.DoesNotExist, Partner.DoesNotExist):
            return HttpResponseRedirect('/myevidyaloka/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def list_partner_myschools(request):
    """For listing all Schools added by partners if the user is Super User. If the user is a Partner, then returns only schools added by requested user"""

    if request.method=="GET":
        is_partner=False
        is_funding_partner = False
        partner=''
        if request.user.is_superuser:
            partner_schools = MySchool.objects.all()
        else:
            profile = UserProfile.objects.get(user=request.user)
            if profile:
                if len(profile.role.filter(name = "Partner Admin")) > 0 or len(profile.role.filter(name = "OUAdmin")):
                    partner = Partner.objects.get(contactperson=request.user)
                    is_partner=True
                else :
                    partner = None
            usrprof = UserProfile.objects.get(user=request.user)
            uroles = usrprof.role.all()
            rolesrequired = uroles.filter(Q(name='Field co-ordinator') | Q(name='Partner Admin') | Q(name='OUAdmin')| Q(name='Partner Account Manager'))
            rolepreference_outcome = []
            for role in rolesrequired:
                try:
                    roleprefe = RolePreference.objects.get(userprofile_id=usrprof.id, role_id=role.id)
                    if roleprefe.role_status == 'New' or roleprefe.role_status == 'Active':
                        rolepreference_outcome.append(roleprefe.role_outcome)
                except RolePreference.DoesNotExist:
                    pass
            parnter_count = Partner.objects.filter(contactperson=request.user,status='Approved').count()
            user_refchanel_partner = False
            if usrprof.referencechannel:
                if usrprof.referencechannel.partner_id:
                    user_refchanel_partner = True
            if (user_refchanel_partner and (rolesrequired.count() > 0) and ('Recommended' in rolepreference_outcome)) or parnter_count > 0:
                if parnter_count > 0:
                    partner = Partner.objects.get(contactperson=request.user, status='Approved')
                elif usrprof.referencechannel.partner_id:
                    if usrprof.referencechannel.partner.status == 'Approved':
                        partner = usrprof.referencechannel.partner
                    else:
                        return HttpResponseRedirect('/myevidyaloka/')
                else:
                    return HttpResponseRedirect('/myevidyaloka/')
                if uroles.filter(name='OUAdmin').count() > 0:
                    partner_schools = MySchool.objects.filter(Q(center__orgunit_partner=partner) | Q(center__funding_partner=partner) | Q(center__delivery_partner=partner))
                elif uroles.filter(name='Partner Account Manager').count() > 0:
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
                    partner_schools  = MySchool.objects.filter( Q(partner_id__in=partner_id)|Q(center__funding_partner_id__in=partner_id) | Q(center__delivery_partner_id__in=partner_id)).distinct()

                    db.close()
                    dict_cur.close()
                else:
                    partner_schools = MySchool.objects.filter(Q(partner_id=partner.id)|Q(center__funding_partner=partner) | Q(center__delivery_partner=partner) | Q(added_by_id = request.user.id)).distinct()
            else:
                return HttpResponseRedirect('/myevidyaloka/')
        if is_partner == True:
            try:
                is_funding_partner = Partner.objects.values("partnertype").filter(contactperson=request.user,partnertype=3)
            except:
                is_funding_partner = ""
        else:
            is_funding_partner = ""

        return render(request,'list_partner_myschools_for_superuser.html',{'partner_schools':partner_schools,"is_partner":is_partner,"partner":partner,"is_funding_partner":is_funding_partner})
    else:
        return HttpResponseRedirect('/myevidyaloka/')



@login_required
def update_myschool_status(request,myschool_id):
    """For Super user to update Partner_MySchool Status"""

    if request.user.is_superuser and myschool_id:
        if request.method=="POST":
            try:
                myschool = MySchool.objects.get(id=myschool_id)
                school_status = request.POST.get('school_status')
                remarks = request.POST.get('school_update_remarks')
                myschool.status = school_status
                myschool.remarks = remarks
                myschool.updated_by = request.user
                myschool.save()
                return HttpResponseRedirect('/partner/myschool/%s/' % myschool.id)
            except MySchool.DoesNotExist:
                return HttpResponseRedirect('/partner/myschools/')
        else:
            return HttpResponseRedirect('/partner/myschools/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def view_myschool_verification_log(request,myschool_id):
    ''' Returns a set of verification records if available else empty list, of a requested School '''

    if request.method == "GET" and myschool_id:
        try:
            myschool = MySchool.objects.get(id=myschool_id)
            log_history = UpdateHistoryLog.objects.filter(referred_table_id=myschool.school.id,log_type='1').order_by('-id')

            for log in log_history:
                log.other_info = ast.literal_eval(log.other_info)
            return render(request,'view_myschool_verification_history.html',{'log_history':log_history,'myschool':myschool})
        except MySchool.DoesNotExist:
            return HttpResponseRedirect('/myevidyaloka/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')



@login_required
def verify_myschool(request,myschool_id,verification_type=''):
    ''' Verify_Myschool is a function to LOG/Store the verification details of respective School added by partner whenever Partner does a verification on the same school '''
    #print "Verification Type ", verification_type
    if myschool_id:

        usrprof = UserProfile.objects.get(user=request.user)
        uroles = usrprof.role.all()
        rolesrequired = uroles.filter(Q(name='Field co-ordinator') | Q(name='Partner Admin'))
        #print "Roles Required ", rolesrequired
        rolepreference_outcome = []
        for role in rolesrequired:
            try:
                roleprefe = RolePreference.objects.get(userprofile_id=usrprof.id, role_id=role.id)
                if roleprefe.role_status == 'New' or roleprefe.role_status == 'Active':
                    rolepreference_outcome.append(roleprefe.role_outcome)
            except RolePreference.DoesNotExist:
                pass
        partner_count = Partner.objects.filter(contactperson=request.user,status='Approved').count()
        #print "Partners count ", partner_count
        user_refchanel_partner = False
        if usrprof.referencechannel:
            if usrprof.referencechannel.partner_id:
                user_refchanel_partner = True
        if (user_refchanel_partner and (rolesrequired.count() > 0) and ('Recommended' in rolepreference_outcome)) or partner_count > 0:
            if request.method == 'GET':
                try:
                    if partner_count > 0:
                        partner = Partner.objects.get(contactperson=request.user, status='Approved')
                    elif usrprof.referencechannel.partner_id:
                        if usrprof.referencechannel.partner.status == 'Approved':
                            partner = usrprof.referencechannel.partner
                        else:
                            return HttpResponseRedirect('/myevidyaloka/')
                    else:
                        return HttpResponseRedirect('/myevidyaloka/')

                    myschool = MySchool.objects.get(id=myschool_id,partner_id=partner.id)

                    return render(request,'partner_myschool_verification.html',{'myschool':myschool})
                except (MySchool.DoesNotExist, Partner.DoesNotExist):
                    return HttpResponseRedirect('/partner/myschools/')
            elif request.method=='POST':
                if myschool_id and verification_type:
                    tab = ''
                    try:
                        if partner_count > 0:
                            partner = Partner.objects.get(contactperson=request.user, status='Approved')
                        elif usrprof.referencechannel.partner_id:
                            if usrprof.referencechannel.partner.status == 'Approved':
                                partner = usrprof.referencechannel.partner
                            else:
                                return HttpResponseRedirect('/myevidyaloka/')
                        else:
                            return HttpResponseRedirect('/myevidyaloka/')
                        myschool = MySchool.objects.get((Q(id=myschool_id))&(Q(partner_id=partner.id)|Q(added_by_id = request.user.id)))

                        if verification_type == 'internetandgeo':
                            myschoolid = request.POST.get('geo_myschoolid')
                            address = request.POST.get('locationName')  # address
                            postal_code = request.POST.get('postal_code')  # postal_code
                            geo_schoolCode = request.POST.get('geo_schoolCode')
                            geo_schoolName = request.POST.get('geo_schoolName')
                            villageName = request.POST.get('villageName')
                            distirictName = request.POST.get('distirictName')
                            serviceProvider = request.POST.get('serviceProvider')
                            connectionType = request.POST.get('connectionType')
                            downloadSpeed = request.POST.get('downloadSpeed')
                            uploadSpeed = request.POST.get('uploadSpeed')
                            latitude = request.POST.get('latitude')
                            longitude = request.POST.get('longitude')

                            other_log_info = {}
                            other_log_info['schoolCode'] = geo_schoolCode
                            other_log_info['verification_type'] = 'Connectivity & Geo Verification'
                            other_log_info['schoolName'] = geo_schoolName
                            other_log_info['villageName'] = villageName
                            other_log_info['distirictName'] = distirictName
                            other_log_info['serviceProvider'] = serviceProvider
                            other_log_info['connectionType'] = connectionType
                            other_log_info['downloadSpeed'] = downloadSpeed
                            other_log_info['uploadSpeed'] = uploadSpeed
                            other_log_info['address'] = address
                            other_log_info['latitude'] = latitude
                            other_log_info['longitude'] = longitude
                            other_log_info['partner_myschool_id'] = myschool.id
                            other_log_info['status'] = 'Success'
                            #if str(myschool.school.pincode) in address:
                            #    other_log_info['status'] = 'Success'
                            #else:
                            #    other_log_info['status'] = 'Failed'

                            school_update_hist_log = UpdateHistoryLog.objects.create(referred_table_id=myschool.school.id,log_type=1,added_by=request.user,other_info=other_log_info)
                            school_update_hist_log.save()
                            # print "School PIN Code as per DB data ", str(myschool.school.pincode)
                            # print "Address obtained ", address
                            # print "Postal Code ", postal_code
                            if True or str(myschool.school.pincode) in address and str(myschool.school.pincode) == postal_code:
                                if myschool.status != '4' or myschool.status != 4 or myschool.status != 'Eligible':
                                    try:
                                        myschoolstatus = MySchoolStatus.objects.get(myschool=myschool,verification_type='Internet and Geo')
                                        myschoolstatus.other_info = other_log_info
                                        myschoolstatus.updated_by = request.user
                                    except MySchoolStatus.DoesNotExist:
                                        myschoolstatus = MySchoolStatus.objects.create(myschool=myschool,verification_type='Internet and Geo',status=True,other_info=other_log_info,added_by=request.user)
                                    myschoolstatus.save()
                                    if myschool.status == 'New':
                                        myschool.status = 'Verification in Progress'
                                        myschool.save()
                                    else:
                                        pass
                            else:
                                error_msg = 'Verification Failed due to Incorrect Location'
                                tab = 'internet'
                                request.method = 'GET'
                                return view_partner_myschool(request, myschool.id, tab, error_msg)
                                # return render(request, 'partner_myschool_verification.html', {'myschool': myschool,'error_msg':error_msg})
                            tab = 'everification'
                            school_verified(myschool)
                            #return render(request,'partner_myschool_verification.html',{'myschool':myschool, 'tab':tab})
                        elif verification_type == 'everification':
                            myschoolid = request.POST.get('ev_myschoolid')
                            ev_schoolCode = request.POST.get('ev_schoolCode')
                            ev_schoolname = request.POST.get('ev_schoolname')
                            noOfTeachers = request.POST.get('noOfTeachers')
                            noOfStudents = request.POST.get('noOfStudents')
                            headMasterName = request.POST.get('headMasterName')

                            other_log_info = {}
                            other_log_info['schoolCode'] = ev_schoolCode
                            other_log_info['verification_type'] = 'eVidyaloka Verification'
                            other_log_info['schoolName'] = ev_schoolname
                            other_log_info['noOfTeachers'] = noOfTeachers
                            other_log_info['noOfStudents'] = noOfStudents
                            other_log_info['headMasterName'] = headMasterName
                            other_log_info['partner_myschool_id'] = myschool.id
                            other_log_info['status'] = 'Success'

                            school_update_hist_log = UpdateHistoryLog.objects.create(referred_table_id=myschool.school.id,log_type=1, added_by=request.user,other_info=other_log_info)
                            school_update_hist_log.save()
                            if myschool.status != '4' or myschool.status != 4 or myschool.status != 'Eligible':
                                try:
                                    myschoolstatus = MySchoolStatus.objects.get(myschool=myschool,verification_type='eVidyaloka Verification')
                                    myschoolstatus.other_info = other_log_info
                                    myschoolstatus.updated_by = request.user
                                except MySchoolStatus.DoesNotExist:
                                    myschoolstatus = MySchoolStatus.objects.create(myschool=myschool,verification_type='eVidyaloka Verification',status=True, other_info=other_log_info,added_by=request.user)
                                myschoolstatus.save()
                                if myschool.status == 'New':
                                    myschool.status = 'Verification in Progress'
                                    myschool.save()
                                else:
                                    pass
                            tab = 'visual_verification'
                            school_verified(myschool)
                            #return render(request,'partner_myschool_verification.html',{'myschool':myschool, 'tab':tab})
                        elif verification_type == 'visualverification':
                            school_pic_path = ''
                            class_pic_path = ''
                            permission_letter_path = ''
                            today = datetime.datetime.now()
                            i = 0
                            j = 20
                            if 'school_pic' in request.FILES:
                                newPhoto=''
                                school_pic = request.FILES['school_pic']
                                photonew = school_pic.name.split('.')
                                if len(photonew[0]) > 45 or len(photonew) > 2:
                                    for pht in photonew[0]:
                                        if i < j:
                                            newPhoto += pht
                                        i += 1
                                    newPhoto += '.'
                                    newPhoto += photonew[-1]
                                else:
                                    newPhoto = school_pic.name
                                school_pic_path = '/static/schoolverificaton/uploads/' + str(myschool.school.school_code) + '_schoolpic_' + today.strftime("%d_%m_%Y") + '_' + newPhoto + ''
                                f_path = os.getcwd()
                                f_name = '/static/schoolverificaton/uploads/' + str(myschool.school.school_code) + '_schoolpic_' + today.strftime("%d_%m_%Y") + '_' + newPhoto + ''
                                f = open(f_path + f_name, 'w+')
                                f.write(school_pic.read())
                                f.close()


                            if 'class_pic' in request.FILES:
                                newPhoto = ''
                                class_pic = request.FILES['class_pic']
                                photonew = class_pic.name.split('.')
                                if len(photonew[0]) > 45 or len(photonew) > 2:
                                    for pht in photonew[0]:
                                        if i < j:
                                            newPhoto += pht
                                        i += 1
                                    newPhoto += '.'
                                    newPhoto += photonew[-1]
                                else:
                                    newPhoto = class_pic.name
                                class_pic_path = '/static/schoolverificaton/uploads/' + str(myschool.school.school_code) + '_classpic_' + today.strftime("%d_%m_%Y") + '' + today.strftime("%X") + '_' + newPhoto + ''
                                f_path = os.getcwd()
                                f_name = '/static/schoolverificaton/uploads/' + str(myschool.school.school_code) + '_classpic_' + today.strftime("%d_%m_%Y") + '' + today.strftime("%X") + '_' + newPhoto + ''
                                f = open(f_path + f_name, 'w+')
                                f.write(class_pic.read())
                                f.close()


                            if 'permission_letter' in request.FILES:
                                newPhoto = ''
                                permission_letter = request.FILES['permission_letter']
                                photonew = permission_letter.name.split('.')
                                if len(photonew[0]) > 45 or len(photonew) > 2:
                                    for pht in photonew[0]:
                                        if i < j:
                                            newPhoto += pht
                                        i += 1
                                    newPhoto += '.'
                                    newPhoto += photonew[-1]
                                else:
                                    newPhoto = permission_letter.name
                                permission_letter_path = '/static/schoolverificaton/uploads/' + str(myschool.school.school_code) + '_permissionletter_' + today.strftime("%d_%m_%Y") + '' + today.strftime("%X") + '_' + newPhoto + ''
                                f_path = os.getcwd()
                                f_name = '/static/schoolverificaton/uploads/' + str(myschool.school.school_code) + '_permissionletter_' + today.strftime("%d_%m_%Y") + '' + today.strftime("%X") + '_' + newPhoto + ''
                                f = open(f_path + f_name, 'w+')
                                f.write(permission_letter.read())
                                f.close()



                            vis_myschoolid = request.POST.get('vis_myschoolid')
                            vis_schoolCode = request.POST.get('vis_schoolCode')
                            vis_schoolname = request.POST.get('vis_schoolname')
                            other_log_info = {}
                            other_log_info['schoolCode'] = vis_schoolCode
                            other_log_info['verification_type'] = 'Visual & Documents Verification'
                            other_log_info['schoolName'] = vis_schoolname
                            other_log_info['school_pic_path'] = school_pic_path
                            other_log_info['class_pic_path'] = class_pic_path
                            other_log_info['permission_letter_path'] = permission_letter_path
                            other_log_info['partner_myschool_id'] = myschool.id
                            other_log_info['status'] = 'Success'


                            school_update_hist_log = UpdateHistoryLog.objects.create(referred_table_id=myschool.school.id,log_type=1, added_by=request.user,other_info=other_log_info)
                            school_update_hist_log.save()
                            if myschool.status != '4' or myschool.status != 4 or myschool.status != 'Eligible':
                                try:
                                    myschoolstatus = MySchoolStatus.objects.get(myschool=myschool,verification_type='Documents Verification')
                                    myschoolstatus.other_info = other_log_info
                                    myschoolstatus.updated_by = request.user
                                except MySchoolStatus.DoesNotExist:
                                    myschoolstatus = MySchoolStatus.objects.create(myschool=myschool,verification_type='Documents Verification',status=True, other_info=other_log_info,added_by=request.user)
                                myschoolstatus.save()
                                if myschool.status == 'New':
                                    myschool.status = 'Verification in Progress'
                                    myschool.save()
                                else:
                                    pass
                            school_verified(myschool)
                            #return HttpResponseRedirect('/partner/myschool/%s/' % myschool.id)
                            #return render(request,'partner_myschool_verification.html',{'myschool':myschool, 'tab':tab})
                        else:
                            return HttpResponseRedirect('/partner/my_schools/')

    #                     if myschool.status == 'New' or myschool.status == 'Verification in Progress':
    #                         print "final"
    #                         myschoolstatus_all = MySchoolStatus.objects.filter(myschool=myschool).values('verification_type').annotate(verify_type_count=Count('verification_type'))
    #                         if myschoolstatus_all.count() == 3:
    #                             print "verified"
    #                             myschool.status='Verified'
    #                             myschool.save()
    #                             school_name = myschool.school.name
    #                             subject = str(school_name)+" Verification has completed successfully."
    #                             admin_email = User.objects.values_list('email',flat = True).filter(is_superuser = True,is_active = True).distinct()
    #                             to = admin_email
    #                             from_email = settings.DEFAULT_FROM_EMAIL
    #                             ctx = {'partner_name':str(myschool.added_by.first_name)+' '+str(myschool.added_by.last_name),'school_name':school_name}
    #                             message = get_template('mail/school_verification.html').render(Context(ctx))
    #                             msg = EmailMessage(subject, message, to=[from_email], bcc=to, from_email=from_email)
    #                             msg.content_subtype = 'html'
    #                             msg.send()
    #                         tab = 'visual_verification'
    #                         print "myschool.id ",myschool.id
                        myschoolstatus_all = MySchoolStatus.objects.filter(myschool=myschool).values('verification_type').annotate(verify_type_count=Count('verification_type'))
                        if myschoolstatus_all.count() == 3:
                            return HttpResponseRedirect('/partner/myschool/%s/' % myschool.id)
                        request.method = 'GET'
                        return view_partner_myschool(request,myschool.id,tab)
                        # return render(request,'partner_myschool_verification.html',{'myschool':myschool, 'tab':tab})
                    except MySchool.DoesNotExist:
                        return HttpResponseRedirect('/partner/my_schools/')
                else:
                    return HttpResponseRedirect('/myevidyaloka/')
            else:
                return HttpResponseRedirect('/myevidyaloka/')
        else:
            return HttpResponseRedirect('/myevidyaloka/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')

def school_verified(myschool):
    if myschool.status == 'New' or myschool.status == 'Verification in Progress':
        myschoolstatus_all = MySchoolStatus.objects.filter(myschool=myschool).values('verification_type').annotate(verify_type_count=Count('verification_type'))
        if myschoolstatus_all.count() == 3:
            myschool.status='Verified'
            myschool.save()
            school_name = myschool.school.name
            subject = str(school_name)+" Verification has completed successfully."
            admin_email = User.objects.values_list('email',flat = True).filter(is_superuser = True,is_active = True).distinct()
            to = admin_email
            from_email = settings.DEFAULT_FROM_EMAIL
            ctx = {'partner_name':str(myschool.added_by.first_name)+' '+str(myschool.added_by.last_name),'school_name':school_name}
            message = get_template('mail/school_verification.html').render(Context(ctx))
            msg = EmailMessage(subject, message, to=[from_email], bcc=to, from_email=from_email)
            msg.content_subtype = 'html'
            msg.send()


def partner_signup(request):
    """ Partner Signup wihtout selecting Type of Partner. Type of Partner will be assigned once after the successful Registraion of Partner by SuperUser """
    if request.method == 'GET':
        return render(request, 'new_signup_page.html',{})
    elif request.method == 'POST':
        name = request.POST.get('name')
        name_of_organization = request.POST.get('name_of_organization', '').strip()
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        org_address = request.POST.get('org_address')
        poc_fname = request.POST.get('poc_fname')
        poc_lname = request.POST.get('poc_lname')
        poc_email = request.POST.get('poc_email')
        poc_phone = request.POST.get('poc_phone')

        if poc_email and name_of_organization and email and poc_fname:
            ### Checking for Contact Person Already Exist or not
            try:
                existing_user = User.objects.get(username=poc_email)
                errormsg = 'User exists already with the Same Contact details, please login'
                return render(request, 'new_signup_page.html', {'errormsg':errormsg})
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                errormsg = 'User exists already, please login'
                return render(request, 'new_signup_page.html', {'errormsg': errormsg})
            ### Checking Reference Channel for the Organizarion Already Exists or not
            try:
                query = Q()
                query = query & Q(name=name_of_organization)
                query = query & ~Q(partner_id=None)
                ref_name = ReferenceChannel.objects.get(query)
                errormsg = 'User exists already with the same Organization, here is the partner mail-id %s' % ref_name.partner.email
                return render(request, 'new_signup_page.html', {'errormsg': errormsg})
            except:
                pass
            ### Creating User and UserProfile
            new_user = User.objects.create_user(email=poc_email, username=poc_email)
            password = User.objects.make_random_password()
            new_user.set_password(password)
            new_user.save()
            user = authenticate(username=poc_email, password=password)
            user.first_name = poc_fname
            user.last_name = poc_lname
            userp = user.userprofile
            userp.phone = poc_phone
            ### Creating Partner Info
            partner_model = Partner.objects.create(contactperson=user,name = name,name_of_organization = name_of_organization,phone = phone,email = email,address = org_address,status = 'New')
            partner_model.save()
            ### Creating Reference Channel Entry
            try:
                ref_channel = ReferenceChannel.objects.get(name=name_of_organization)
                ref_channel.partner = partner_model
            except:
                ref_channel = ReferenceChannel.objects.create(name=name_of_organization, partner=partner_model)
            ref_channel.save()
            ### Updating Users Referencechannel and Saving his Profile
            userp.referencechannel = ref_channel
            ### Adding PartnerAdmin Role to the User
            role = Role.objects.get(name='Partner Admin')
            if role:
                userp.role.add(role)
                userp.pref_roles.add(role)
            userp.save()
            user.save()
            ### Sending Registration Mail to the User by Copying to Organization
            args = {'username': poc_email, 'name': str(poc_fname) + ' ' + str(poc_lname), 'password': password,
                    'name_of_organization': name_of_organization}
            mail = ''
            body = ''
            subject = 'Welcome to eVidyaloka - ' + str(name_of_organization)
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [poc_email]
            body = get_template('partner_signup_mail.html').render(Context(args))
            if email:
                cc = [email]
                mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
            else:
                mail = EmailMessage(subject, body, to=to, from_email=from_email)
            mail.content_subtype = 'html'
            mail.send()

            ### Sending Emial to SuperUsers
            evladmins = User.objects.filter(is_superuser=True,is_active=True)#.filter(email__icontains='@evidyaloka.org')
            mail_to = [adm.email for adm in evladmins]
            mail_subject = 'New Partner Signed up'
            mail_args = {'username': user.username, 'org_name': name_of_organization, 'contactperson_email': user.email}
            mail_body = get_template('mail/_partner/New_Partner_SignUp_Notify_SuperUSer.html').render(Context(mail_args))
            adm_mail = EmailMessage(mail_subject, mail_body, to=mail_to, from_email=from_email)
            adm_mail.content_subtype = 'html'
            adm_mail.send()

            successmsg = "Thanks for signing-up, We've sent an email to your registered email, with contact person login credentials."
            alertmsg = "Thank you for interest. Your registration is under review. You will notified via email, on approval of your organisation profile"
            login(request, user)
            return render(request, 'new_signup_page.html', {'successmsg': successmsg,'alertmsg':alertmsg,'success':True})
        else:
            errormsg = 'Please Fill all the information and then Submit.'
            return render(request, 'new_signup_page.html', {'errormsg': errormsg})
    else:
        return render(request, 'new_signup_page.html', {})


@login_required
def list_partners(request,partner_id=None):
    if request.method == 'GET' and request.user.is_superuser:
        if partner_id:
            try:
                partner = Partner.objects.get(id=partner_id)
                partner_types = Partnertype.objects.all()
                status_choices = [ 'New', 'In Process', 'Approved', 'On Hold', 'Not Approved']
                return render(request,'list_partners.html',{'partner':partner,'view_flag':True,'status_choices':status_choices,'partner_types':partner_types})
            except Partner.DoesNotExist:
                return HttpResponseRedirect('/partner/partners/')
        partners = Partner.objects.all().order_by('id')
        partner_types = Partnertype.objects.all()
        return render(request,'list_partners.html',{'partners':partners,'partner_types':partner_types})
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def partner_update_type_status(request,partner_id):
    if request.method == 'POST' and request.user.is_superuser:
        if partner_id:
            partner_types = request.POST.getlist('ptypes')
            status = request.POST.get('partner_status')
            try:
                partner = Partner.objects.get(id=partner_id)
                partner.partnertype.clear()
                partner.status = status
                for ptypeid in partner_types:
                    try:
                        ptype = Partnertype.objects.get(id=ptypeid)
                        partner.partnertype.add(ptype)
                    except Partnertype.DoesNotExist:
                        pass
                partner.save()

                ### Sending Emial to SuperUsers
                ptypes = ', '.join(t.name for t in partner.partnertype.all())
                if partner.status == 'Approved' and ptypes:
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to = [partner.contactperson.email]
                    subject = 'Congratulations! You are a %s at eVidyaloka' %ptypes
                    mail_args = {'first_name': partner.contactperson.first_name, 'last_name': partner.contactperson.last_name}
                    body = get_template('mail/_partner/partner_status_and_approval_update.html').render(Context(mail_args))
                    if partner.email:
                        cc = [partner.email]
                        mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
                    else:
                        mail = EmailMessage(subject, body, to=to, from_email=from_email)
                    mail.content_subtype = 'html'
                    mail.send()

                    try:
                        if ptype and ptype.name == "Digital Partner":
                            authUser = partner.contactperson
                            notificationModule.sendPartnerApprovalNotification(partner, authUser)
                    except:
                        pass

                return HttpResponseRedirect('/partner/partners/%s/' %partner.id)
            except Partner.DoesNotExist:
                return HttpResponseRedirect('/partner/partners/')
            # for d in request.POST.lists():
            #     d = dict(d)
        else:
            return HttpResponseRedirect('/partner/partners/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def list_centers(request):
    if request.method == 'GET':
        is_orgUnit = False
        is_funding_partner = False
        is_partner=False
        is_delivery_partner= False
        partner_admin=''
        usrprof = UserProfile.objects.get(user=request.user)
        uroles = usrprof.role.all()
        boards = Center.objects.values_list("board").distinct()  #["DCERT","APSB","BSEB","JACB","MHSB","SCERT","TNSB","UBSE","UPMSP","WBSED","JKBOSE"]
        if request.user.is_superuser:
            centers = Center.objects.all().filter(board__in = boards)
        elif uroles.filter(name='Partner Account Manager').count() > 0:
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
            centers  =Center.objects.filter( Q(funding_partner_id__in=partner_id) | Q(delivery_partner_id__in=partner_id))

            db.close()
            dict_cur.close()
        else:
            profile = UserProfile.objects.get(user=request.user)
            if profile:
                if len(profile.role.filter(name = "Partner Admin")) > 0 or len(profile.role.filter(name = "OUAdmin")):
                    partner_admin = Partner.objects.get(contactperson=request.user)
                    is_partner=True
                else :
                    partner_admin = None
            centers = []
            orgunit_partner_count = request.user.partner_set.filter(status='Approved',partnertype__id=4).count()
            delivery_parnter_count = Partner.objects.filter(contactperson=request.user, status='Approved',partnertype__id=2).count()
            funding_parnter_count = Partner.objects.filter(contactperson=request.user, status='Approved',partnertype__id=3).count()

            partner = request.user.partner_set.all()
            partner_count=partner.count()
            if partner:
                partner_types = partner[0].partnertype.values()
                for partnerty in partner_types:
                    if partnerty['name'] == 'Organization Unit': is_orgUnit = True
                    if partnerty['name'] == 'Funding Partner' : is_funding_partner=True
                    if partnerty['name'] == 'Delivery Partner' : is_delivery_partner=True

            if partner_count > 0:
                centers =Center.objects.filter(Q(partner_school__partner__contactperson=request.user,status='Active') | Q(orgunit_partner__contactperson=request.user,status='Active')
                                    |Q(funding_partner__contactperson=request.user,status='Active')|Q(delivery_partner__contactperson=request.user,status='Active')|Q(digital_school_partner__contactperson=request.user,status='Active'))
                str_base = "{} - {}, "
                for each in centers:
                   
                    str_data = ""
                    offering = Offering.objects.filter(Q(center_id=each.id) & Q(status='running')).exclude(active_teacher_id=None).values('course').distinct()

                    for offer in offering:
                        cr = Course.objects.get(pk=offer['course'])
                        str_data += str_base.format(cr.grade, cr.subject)
                    str_data = str_data[:-2]
                    each.grade_offer = str_data
        is_school_admin = False
        is_evd_centers = False
        if has_role(request.user.userprofile, 'School Admin'):
            is_school_admin = True
            is_evd_centers = True

        return render(request, 'list_centers.html', {'centers': centers,'is_orgUnit':is_orgUnit, 'is_delivery_partner':is_delivery_partner, 'is_funding_partner':is_funding_partner,'partner':partner_admin,'is_partner':is_partner, 'is_school_admin' : is_school_admin, 'is_evd_centers' : is_evd_centers})
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def add_center_to_school(request,myschool_id):
    if (request.method == 'GET' or request.method == 'POST') and myschool_id and request.user.is_superuser or has_role(request.user.userprofile, "Partner Account Manager") or has_pref_role(request.user.userprofile, "Partner Account Manager"):
        try:
            myschool = MySchool.objects.get(id=myschool_id)
            is_super_admin = False
            users = User.objects.all().exclude(is_active=False)
            print(myschool.partner_id)
            partner_data = Partner.objects.get(id=myschool.partner_id)
            if request.method == 'GET':
                center_form = AddCenter()
                # center_form.fields['admin'].queryset = users
                # center_form.fields['assistant'].queryset = users
                # center_form.fields['field_coordinator'].queryset = users
                # center_form.fields['delivery_coordinator'].queryset = users
                if partner_data.role_id == '16':
                    is_school_admin = True
                    return render(request,'add_center_to_school.html',{'center_form':center_form, 'is_school_admin' : is_school_admin, 'school_id' : myschool_id, 'school_name' : myschool.school.name, 'school_data' : myschool})

                return render(request,'add_center_to_school.html',{'center_form':center_form})

            elif request.method == 'POST':
                center_form = AddCenter(request.POST)
                # center_form.fields['admin'].queryset = users
                # center_form.fields['assistant'].queryset = users
                # center_form.fields['field_coordinator'].queryset = users
                # center_form.fields['delivery_coordinator'].queryset = users
                if center_form.is_valid():
                    name = center_form.cleaned_data['name']
                    language = center_form.cleaned_data['language']
                    board = center_form.cleaned_data['board']
                    working_days = center_form.cleaned_data['working_days']
                    working_slots = center_form.cleaned_data['working_slots']

                    admin_name = center_form.cleaned_data['admin']
                    selected_admin = center_form.cleaned_data['selected_admin']
                    admin = None
                    if admin_name and selected_admin:
                        admin = users.get(id=selected_admin)

                    assistant_name = center_form.cleaned_data['assistant']
                    selected_assistant = center_form.cleaned_data['selected_assistant']
                    assistant = None
                    if assistant_name and selected_assistant:
                        assistant = users.get(id=selected_assistant)

                    description = center_form.cleaned_data['description']
                    classlocation = center_form.cleaned_data['classlocation']
                    grades = center_form.cleaned_data['grades']
                    subjectscovered = center_form.cleaned_data['subjectscovered']
                    noofchildren = center_form.cleaned_data['noofchildren']
                    status = center_form.cleaned_data['status']
                    launchdate = center_form.cleaned_data['launchdate']
                    donor_name = center_form.cleaned_data['donor_name']
                    skype_id = center_form.cleaned_data['skype_id']
                    location_map = center_form.cleaned_data['location_map']
                    ops_donor_name = center_form.cleaned_data['ops_donor_name']
                    funding_partner = center_form.cleaned_data['funding_partner']
                    delivery_partner = center_form.cleaned_data['delivery_partner']
                    orgunit_partner = center_form.cleaned_data['orgunit_partner']

                    field_coordinator_name = center_form.cleaned_data['field_coordinator']
                    selected_field_coordinator = center_form.cleaned_data['selected_field_coordinator']
                    field_coordinator = None
                    if field_coordinator_name and selected_field_coordinator:
                        field_coordinator = users.get(id=selected_field_coordinator)

                    delivery_coordinator_name = center_form.cleaned_data['delivery_coordinator']
                    selected_delivery_coordinator = center_form.cleaned_data['selected_delivery_coordinator']
                    delivery_coordinator = None
                    if delivery_coordinator_name and selected_delivery_coordinator:
                        delivery_coordinator = users.get(id=selected_delivery_coordinator)

                    hm = center_form.cleaned_data['hm']
                    partner_school = center_form.cleaned_data['partner_school']
                    if not noofchildren:
                        noofchildren = 0

                    try:
                        center = Center.objects.get(name=name,partner_school=partner_school)
                        errormsg = 'For %s, Same center %s is already added.' %(myschool.school.name, name)
                        return render(request, 'add_center_to_school.html', {'center_form': center_form,'errormsg':errormsg})
                    except Center.DoesNotExist:
                        center = Center.objects.create(name=name,state=myschool.school.state,district=myschool.school.district_details,village=myschool.school.village,language=language,board=board,working_days=working_days,
                                                       working_slots=working_slots,admin=admin,assistant=assistant,description=description,classlocation=classlocation,grades=grades,subjectscovered=subjectscovered,noofchildren=noofchildren,
                                                       status=status,launchdate=launchdate,donor_name=donor_name,skype_id=skype_id,location_map=location_map,ops_donor_name=ops_donor_name,funding_partner=funding_partner,
                                                       delivery_partner=delivery_partner,orgunit_partner=orgunit_partner,created_by=request.user,field_coordinator=field_coordinator,delivery_coordinator=delivery_coordinator,HM=hm,partner_school=partner_school)
                        try:
                            photo = request.FILES['photo']
                            center.photo=photo
                        except :
                            pass
                        center.save()
                    try:
                        current_ay = Ayfy.objects.get(start_date__year=datetime.datetime.now().year, board=center.board).id
                    except:
                        from dateutil.relativedelta import relativedelta
                        last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
                        current_ay = Ayfy.objects.get(start_date__year=last_year, board=center.board).id
                    return HttpResponseRedirect('/centeradmin/?center_id=%s&ay_id=%s' %(center.id,current_ay))
                else:
                    return render(request, 'add_center_to_school.html', {'center_form': center_form})
        except MySchool.DoesNotExist:
            return HttpResponseRedirect('/partner/myschools/')
    else:
        return HttpResponseRedirect('/partner/centers/')


@login_required
def update_center(request,center_id,myschool_id):
    try:
        partner_name = request.user.first_name+" "+request.user.last_name
        is_delivery_partner_id = Partner.objects.values_list("partnertype",flat = True).filter(name = partner_name,partnertype = "2")
        if is_delivery_partner_id:
            is_delivery_partner = True
        else:
            is_delivery_partner = ""
    except:
        is_delivery_partner = ""
        
    if (request.method == 'GET' or request.method == 'POST') and center_id and myschool_id and request.user.is_superuser or has_role(request.user.userprofile,'Partner Account Manager') or is_delivery_partner == True:
        try:
            center = Center.objects.get(id=center_id,partner_school_id=myschool_id)
            users = User.objects.all().exclude(is_active=False)
            myschool = MySchool.objects.get(id=myschool_id)
            if request.method == 'GET':
                data = get_center_data(center)
                center_form = AddCenter(initial=data)
                if myschool.partner.role_id == '16':
                    is_school_admin = True
                    return render(request,'add_center_to_school.html',{'center_form':center_form, 'is_school_admin' : is_school_admin, 'school_id' : myschool_id, 'school_name' : myschool.school.name, 'school_data' : myschool, 'update_flag':True})
                return render(request, 'add_center_to_school.html', {'center_form': center_form,'update_flag':True,"is_deliver_partner":is_delivery_partner})
            elif request.method == 'POST':
                
                center_form = AddCenter(request.POST)
                if center_form.is_valid():
                    
                    center.name = center_form.cleaned_data['name']
                    center.language = center_form.cleaned_data['language']
                    center.board = center_form.cleaned_data['board']
                    center.working_days = center_form.cleaned_data['working_days']
                    center.working_slots = center_form.cleaned_data['working_slots']

                    admin_name = center_form.cleaned_data['admin']
                    selected_admin = center_form.cleaned_data['selected_admin']
                    if admin_name and selected_admin:
                        center.admin = users.get(id=selected_admin)
                    else:
                        center.admin = None

                    assistant_name = center_form.cleaned_data['assistant']
                    selected_assistant = center_form.cleaned_data['selected_assistant']
                    if assistant_name and selected_assistant:
                        center.assistant = users.get(id=selected_assistant)
                    else:
                        center.assistant = None

                    center.description = center_form.cleaned_data['description']
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@dd",center_form.cleaned_data['hm'])
                    center.classlocation = center_form.cleaned_data['classlocation']
                    center.grades = center_form.cleaned_data['grades']
                    center.subjectscovered = center_form.cleaned_data['subjectscovered']
                    noofchildren = center_form.cleaned_data['noofchildren']
                    center.status = center_form.cleaned_data['status']
                    center.launchdate = center_form.cleaned_data['launchdate']
                    # center.donor_name = center_form.cleaned_data['donor_name']
                    center.skype_id = center_form.cleaned_data['skype_id']
                    center.location_map = center_form.cleaned_data['location_map']
                    # center.ops_donor_name = center_form.cleaned_data['ops_donor_name']
                    center.funding_partner = center_form.cleaned_data['funding_partner']
                    center.delivery_partner = center_form.cleaned_data['delivery_partner']
                    center.orgunit_partner = center_form.cleaned_data['orgunit_partner']

                    field_coordinator_name = center_form.cleaned_data['field_coordinator']
                    selected_field_coordinator = center_form.cleaned_data['selected_field_coordinator']
                    if field_coordinator_name and selected_field_coordinator:
                        center.field_coordinator = users.get(id=selected_field_coordinator)
                    else:
                        center.field_coordinator = None

                    delivery_coordinator_name = center_form.cleaned_data['delivery_coordinator']
                    selected_delivery_coordinator = center_form.cleaned_data['selected_delivery_coordinator']
                    if delivery_coordinator_name and selected_delivery_coordinator:
                        center.delivery_coordinator = users.get(id=selected_delivery_coordinator)

                        center.hm = center_form.cleaned_data['hm']
                    partner_school = center_form.cleaned_data['partner_school']
                    if not noofchildren:
                        center.noofchildren = 0
                    center.save()
                    try:
                        hm = request.POST.get('hm')
                        Center.objects.filter(id = center_id).update(HM=hm)
                    except:
                        pass
                    return HttpResponseRedirect('/partner/myschool/%s/' %center.partner_school.id)
                    # try:
                    #     current_ay = Ayfy.objects.get(start_date__year=datetime.datetime.now().year, board=center.board).id
                    # except:
                    #     from dateutil.relativedelta import relativedelta
                    #     last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
                    #     current_ay = Ayfy.objects.get(start_date__year=last_year, board=center.board).id
                    # return HttpResponseRedirect('/centeradmin/?center_id=%s&ay_id=%s' %(center.id,current_ay))
                else:
                    return render(request, 'add_center_to_school.html',{'center_form': center_form, 'update_flag': True,"is_deliver_partner":is_delivery_partner})
            else:
                return HttpResponseRedirect('/partner/centers/')
        except Center.DoesNotExist:
            return HttpResponseRedirect('/partner/centers/')
    else:
        return HttpResponseRedirect('/partner/centers/')



@login_required
def partner_admin_defaultpage(request):
    if request.method == 'GET' or request.method == 'POST' :
        try:
            partner = Partner.objects.get(contactperson=request.user)
            partner_name=partner.name_of_organization
            users=UserProfile.objects.filter(referencechannel_id=partner.id)
            if users:
                users_count=users.count()
            else :
                users_count=None
            is_partner_volunteer,is_partner_delivery,is_partner_funding = [False] * 3
            for ptype in partner.partnertype.all():
                if ptype.id == 1:
                    is_partner_volunteer = True
                elif ptype.id == 2:
                    is_partner_delivery = True
                elif ptype.id == 3:
                    is_partner_funding = True
            if request.method == 'GET':
                if has_role(request.user.userprofile,'OUAdmin'):
                    myschools_count = MySchool.objects.filter(center__orgunit_partner=partner.id).count()
                elif has_role(request.user.userprofile,'Partner Admin'):
                    myschools_count = MySchool.objects.filter(Q(center__funding_partner=partner.id)|Q(center__delivery_partner=partner.id)).count()
                else:
                    myschools_count = MySchool.objects.filter(partner_id=partner.id,status='Eligible').count()
                if has_role(request.user.userprofile,'Partner Admin'):
                    mycenters_count = Center.objects.filter(Q(funding_partner_id=partner.id,status='Active')|Q(orgunit_partner_id=partner.id,status='Active')|Q(delivery_partner_id=partner.id,status='Active')).count()
                else:
                    mycenters_count = Center.objects.filter(partner_school__partner_id=partner.id,status='Active').count()
                admin_assigned_roles = ["Class Assistant", "TSD Panel Member", "vol_admin", "vol_co-ordinator", "Field co-ordinator", "Delivery co-ordinator", "support", 'Digital School Manager']
                roles = Role.objects.filter(name__in=admin_assigned_roles)
                return render(request,'partner_admin_page.html',{'partner':partner,'is_partner_volunteer':is_partner_volunteer,'is_partner_delivery':is_partner_delivery,'myschools_count':myschools_count,
                                                                 'mycenters_count':mycenters_count,'roles':roles,'is_partner_funding':is_partner_funding,'partner_name':partner_name,'users_count':users_count})
            elif request.method == 'POST':
                partner.name_of_organization = request.POST.get('org_name')
                partner.address = request.POST.get('address')
                if is_partner_volunteer or is_partner_delivery:
                    try:
                        partner_org_details = DeliveryPartnerOrgDetails.objects.get(partner=partner)
                    except DeliveryPartnerOrgDetails.DoesNotExist:
                        partner_org_details = DeliveryPartnerOrgDetails.objects.create(partner=partner)
                    partner_org_details.website_address = request.POST.get('website_address')
                    partner_org_details.office_phone = request.POST.get('office_phone')
                    partner.email = request.POST.get('email')
                    partner_org_details.type_of_org = request.POST.get('org_type')
                    if is_partner_delivery:
                        partner_org_details.date_of_reg = request.POST.get('date_of_reg')
                        partner_org_details.place_of_reg = request.POST.get('org_reg_place')
                        partner_org_details.reg_number = request.POST.get('reg_number')
                        partner_org_details.number = request.POST.get('number')
                        partner_org_details.fcra_reg_number = request.POST.get('fcra_reg_number')
                        partner_org_details.fcra_acc_number = request.POST.get('fcra_acc_number')
                        partner_org_details.bank_name = request.POST.get('bank_name')
                        partner_org_details.ifsc_code = request.POST.get('ifsc_code')
                        partner_org_details.acc_holder_name = request.POST.get('acc_name')
                        partner_org_details.acc_number = request.POST.get('acc_number')
                        partner_org_details.type_of_acc = request.POST.get('acc_type')
                    partner_org_details.save()
                partner.save()
                return HttpResponseRedirect('/myevidyaloka/')

        except Partner.DoesNotExist:
            return HttpResponseRedirect('/myevidyaloka/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')

@login_required
def partner_users(request):
    try:
        search_term = request.GET.get('term', '')
        role = request.GET.get('role', None)
        if request.method == 'GET':
            # print "000000000000000000000000000000000", request.user.is_superuser
            userp = UserProfile.objects.filter(user=request.user)[0]
            if request.user.is_superuser or has_pref_role(userp, "Content Admin"):
                users = User.objects.filter(Q(id__icontains=search_term) | Q(username__icontains=search_term) | Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)).order_by('id')
                lusers = []
                for u in users:
                    # uroles = UserProfile.objects.get(user_id=int(u['id'])).role.all()
                    user = {}
                    # user['id'] = u['id']
                    # user['name'] = u['first_name'] + ' ' + u['last_name']
                    # user['value'] = u['first_name'] + ' ' + u['last_name']
                    # user['label'] = u['first_name'] + ' ' + u['last_name']
                    user['id'] = u.id
                    user['name'] = u.first_name + ' ' + u.last_name
                    user['value'] = u.id
                    user['label'] = str(u.id) + '-' + u.first_name + ' ' + u.last_name
                    try:
                        user_profile_id = UserProfile.objects.get(user_id=u.id)
                        uroles = [str(ur.name) for ur in UserProfile.objects.get(user_id=u.id).role.filter(type='Internal').exclude(Q(name='Partner Admin') | Q(name='OUAdmin'))]
                        user['roles'] = ", ".join(uroles)
                        lusers.append(user)
                    except:
                        continue
                return HttpResponse(simplejson.dumps(lusers))
            try:
                if has_role(request.user.userprofile, "School Admin"):
                    school_admin_details = Partner.objects.filter(contactperson=request.user)
                    school_admin = school_admin_details[0]
                    users = User.objects.filter(Q(userprofile__referencechannel__partner__id=school_admin.id))
                else:
                    partner = request.user.partner_set.all()[0]
                    users = User.objects.filter(Q(userprofile__referencechannel__partner__id=partner.id))
                users_filtered = users.filter(Q(username__icontains=search_term) | Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)).order_by('id')
                lusers = []
                for u in users_filtered:
                    # uroles = UserProfile.objects.get(user_id=int(u['id'])).role.all()
                    user ={}
                    # user['id'] = u['id']
                    # user['name'] = u['first_name'] + ' ' + u['last_name']
                    # user['value'] = u['first_name'] + ' ' + u['last_name']
                    # user['label'] = u['first_name'] + ' ' + u['last_name']
                    # uroles = [str(ur.name) for ur in UserProfile.objects.get(user_id=int(u['id'])).role.filter(type='Internal').exclude(name='Partner Admin')]
                    # user['roles'] = ", ".join(uroles)
                    user['id'] = u.id
                    user['name'] = u.first_name + ' ' + u.last_name
                    user['value'] = u.first_name + ' ' + u.last_name
                    user['label'] = u.first_name + ' ' + u.last_name
                    uroles = [str(ur.name) for ur in UserProfile.objects.get(user_id=u.id).role.filter(type='Internal').exclude(Q(name='Partner Admin') | Q(name='OUAdmin') | Q(name='School Admin'))]
                    user['roles'] = ", ".join(uroles)
                    lusers.append(user)
                return HttpResponse(simplejson.dumps(lusers))
            except (User.DoesNotExist or UserProfile.DoesNotExist, Partner.DoesNotExist):
                return HttpResponse('Data Not Found...!!!')
    except Exception as e:
        print("Erro at line no --------------------", e)
        print("Error reason ----------------------",  traceback.format_exc())


@login_required
def get_my_select_users(request):
    search_term = request.GET.get('term', '')
    role_id = request.GET.get('role_id', '')
    # type = request.GET.get('type', '')
    center_id = request.GET.get('center_id', '')
    try :
        partner = request.user.partner_set.all()[0]
        # center = Center.objects.get(id=center_id)
        # center_language = center.language
        # #center_name=center.name
        # center_state=center.state;
        users = User.objects.filter(Q(userprofile__referencechannel__partner__id=partner.id)|Q(userprofile__referred_user_id=partner.contactperson_id))
        users_filtered = users.filter(Q(username__icontains=search_term) | Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)).order_by('id')
        lusers = []
        for u in users_filtered:
            # uroles = UserProfile.objects.get(user_id=int(u['id'])).role.all()
            user = {}
            # user['id'] = u['id']
            # user['center_id'] = ''
            # user['username'] = u['first_name'] + ' ' + u['last_name']
            # user['value'] = str(u['id']) + ' :: ' + u['first_name'] + ' ' + u['last_name']
            # user['label'] = str(u['id']) + ' :: ' + u['first_name'] + ' ' + u['last_name']
            user['id'] = u.id
            user['center_id'] = ''
            user['name'] = u.first_name + ' ' + u.last_name
            user['value'] = u.first_name + ' ' + u.last_name
            user['label'] = u.first_name + ' ' + u.last_name
            lusers.append(user)

        return HttpResponse(simplejson.dumps(lusers))
    except Partner.DoesNotExist:
        center = None
        lusers = []
        return HttpResponse('Oops...!!! Failed to get the data.')


@login_required
def partner_assign_user_roles(request):
    # print "requeasdfghjklst",request
    first_name= request.user.first_name
    last_name = request.user.last_name
    if request.user.is_superuser:
        first_name= request.user.first_name
        last_name = request.user.last_name
    if request.method == 'POST':
        selected_user = request.POST.get('selected_user')
        selected_roles = request.POST.getlist('roles')
        userp = UserProfile.objects.get(user_id=selected_user)

        # userp.role.clear()
        for role in userp.role.filter(type='Internal'):
            if role.name == 'Partner Admin' or role.id==10:
                pass
            elif role.name == 'School Admin' or role.id ==16:
                pass
            else:
                userp.role.remove(role)
        for role in selected_roles:
            userp.role.add(role)

        # userp.pref_roles.clear()
        for role in userp.pref_roles.filter(type='Internal'):
            if role.name == 'Partner Admin' or role.id==10:
                pass
            elif role.name == 'School Admin' or role.id ==16:
                pass
            else:
                userp.pref_roles.remove(role)
        for role in selected_roles:
            userp.pref_roles.add(role)

        ######### Creating/Updating the RolePreference table for the user based on his selection of Roles
        pref_roles = userp.pref_roles.filter(type='Internal')
        for role in pref_roles:
            if role.name == 'support':
                pass
            else:
                role_preference, created = RolePreference.objects.get_or_create(userprofile=userp, role=role)
                role_preference.role_outcome = 'Recommended'
                role_preference.role_status ='Active'
                role_preference.save()

        roleoreferences = RolePreference.objects.filter(userprofile=userp)
        for roleoreference in roleoreferences:
            if roleoreference.role in pref_roles:
                # print 'in if ',roleoreference
                pass
            else:
                # print 'in else ',roleoreference
                if roleoreference.role.type == 'External' or roleoreference.role.name == 'Partner Admin' or roleoreference.role.name == 'support':
                    pass
                else:
                    # print 'role id',roleoreference.role, 'role outcome ',roleoreference.role_outcome
                    roleoreference.role_outcome = 'Not Started'
                    roleoreference.save()

        userp.save()
        #### Mail to the user on Update Roles
        user_roles = ', '.join(t.name for t in userp.pref_roles.all())
        if user_roles:
            from_email = settings.DEFAULT_FROM_EMAIL
            to = [userp.user.email]
            subject = 'Congratulations! You are now a %s' % user_roles
            if has_role(request.user.userprofile,'School Admin'):
                try:
                    partner_fname = userp.referencechannel.partner.contactperson.first_name,
                    partner_lname = userp.referencechannel.partner.contactperson.last_name,
                    partner_org_name = userp.referencechannel.partner.name
                except:
                    partner_fname = 'NA'
                    partner_lname = 'NA'
                    partner_org_name = 'NA'
                mail_args = { 'super_user_frstname':first_name, 'super_user_lastname':last_name,'first_name': userp.user.first_name, 'last_name': userp.user.last_name,'myroles':user_roles,'partner_fname':partner_fname,
                        'partner_lname': partner_lname,'partner_org_name':partner_org_name}
            else:
                try:
                    partner_fname = userp.referencechannel.partner.contactperson.first_name,
                    partner_lname = userp.referencechannel.partner.contactperson.last_name,
                    partner_org_name = userp.referencechannel.partner.name
                except:
                    partner_fname = 'NA'
                    partner_lname = 'NA'
                    partner_org_name = 'NA'
                mail_args = { 'super_user_frstname':first_name, 'super_user_lastname':last_name,'first_name': userp.user.first_name, 'last_name': userp.user.last_name,'myroles':user_roles,'partner_fname':partner_fname,
                            'partner_lname': partner_lname,'partner_org_name':partner_org_name}
            if request.user.is_superuser:
                body = get_template('mail/_partner/superadmin_volunteer_role_update_by_superuser.html').render(Context(mail_args))
            else:
                body = get_template('mail/_partner/Partner_volunteer_role_update_by_partner_mail.html').render(Context(mail_args))
        
        try:
            thread.start_new_thread(send_mail_assign, (subject, body, to, from_email))
        except:
            print "Threading failed"
        else:
            print "Sending mail is done by another thread"

            
            
        if request.user.is_superuser or has_pref_role(UserProfile.objects.get(user=request.user), "Content Admin"):
            messages.success(request, 'Successfully Assigned ')
            return HttpResponseRedirect('/myevidyaloka/')
        else:
            
            messages.success(request, 'Successfully Assigned.')
            return HttpResponseRedirect('/partner/my_users/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


def send_mail_assign(subject, body, to, from_email):
    mail = EmailMessage(subject, body, to=to, from_email=from_email)
    mail.content_subtype = 'html'
    mail.send()

@login_required
def update_digitalinfo(request,center_id,myschool_id):
    if (request.method == 'GET' or request.method == 'POST') and center_id and myschool_id :
        try:
            users = User.objects.all().exclude(is_active=False)
            center = Center.objects.get(id=center_id,partner_school_id=myschool_id)
            if request.method == 'GET':
                data = get_center_data(center)
                update_center_form = AddCenter(initial=data)

                if not request.user.is_superuser:
                    update_center_form.fields["name"].widget.attrs['readonly'] = True
                    update_center_form.fields["language"].widget.attrs['readonly'] = True
                    update_center_form.fields["board"].widget.attrs['readonly'] = True
                    update_center_form.fields["working_days"].widget.attrs['readonly'] = True
                    update_center_form.fields["working_slots"].widget.attrs['readonly'] = True
                    update_center_form.fields["status"].widget.attrs['readonly'] = True
                    update_center_form.fields["admin"].widget.attrs['readonly'] = True
                    update_center_form.fields["assistant"].widget.attrs['readonly'] = True
                    update_center_form.fields["photo"].widget.attrs['readonly'] = True
                    update_center_form.fields["field_coordinator"].widget.attrs['readonly'] = True
                    update_center_form.fields["delivery_coordinator"].widget.attrs['readonly'] = True
                    update_center_form.fields["funding_partner"].widget.attrs['readonly'] = True
                    update_center_form.fields["delivery_partner"].widget.attrs['readonly'] = True
                    update_center_form.fields["partner_school"].widget.attrs['readonly'] = True
                    update_center_form.fields["classlocation"].widget.attrs['readonly'] = True
                    update_center_form.fields["grades"].widget.attrs['readonly'] = True
                    update_center_form.fields["subjectscovered"].widget.attrs['readonly'] = True
                    update_center_form.fields["noofchildren"].widget.attrs['readonly'] = True
                    update_center_form.fields["launchdate"].widget.attrs['readonly'] = True
                    update_center_form.fields["description"].widget.attrs['readonly'] = True
                    update_center_form.fields["orgunit_partner"].widget.attrs['readonly'] = True
                return render(request, 'add_center_to_school.html', {'center_form': update_center_form,'update_flag': True})
            elif request.method == 'POST':
                update_center_form = AddCenter(request.POST)
                if update_center_form.is_valid():
                    center.skype_id = update_center_form.cleaned_data['skype_id']
                    center.location_map = update_center_form.cleaned_data['location_map']
                    center.hm = update_center_form.cleaned_data['hm']
                    if request.user.is_superuser:
                        center.name = update_center_form.cleaned_data['name']
                        center.language = update_center_form.cleaned_data['language']
                        center.board = update_center_form.cleaned_data['board']
                        center.working_days = update_center_form.cleaned_data['working_days']
                        center.working_slots = update_center_form.cleaned_data['working_slots']
                        center.status = update_center_form.cleaned_data['status']
                        selected_admin = update_center_form.cleaned_data['selected_admin']
                        admin_name = update_center_form.cleaned_data['admin']
                        if selected_admin and admin_name:
                            center.admin = users.get(id=selected_admin)
                        assistant_name = update_center_form.cleaned_data['assistant']
                        selected_assistant = update_center_form.cleaned_data['selected_assistant']
                        try:
                            photo = request.FILES['photo']
                            center.photo=photo
                        except:
                            pass
                        field_coordinator_name = update_center_form.cleaned_data['field_coordinator']
                        selected_field_coordinator = update_center_form.cleaned_data['selected_field_coordinator']
                        if field_coordinator_name and selected_field_coordinator:
                            center.field_coordinator = users.get(id=selected_field_coordinator)
                        delivery_coordinator_name = update_center_form.cleaned_data['delivery_coordinator']
                        selected_delivery_coordinator = update_center_form.cleaned_data['selected_delivery_coordinator']
                        if delivery_coordinator_name and selected_delivery_coordinator:
                            center.delivery_coordinator = users.get(id=selected_delivery_coordinator)
                        center.funding_partner = update_center_form.cleaned_data['funding_partner']
                        center.delivery_partner = update_center_form.cleaned_data['delivery_partner']
                        center.partner_school = update_center_form.cleaned_data['partner_school']
                        center.classlocation = update_center_form.cleaned_data['classlocation']
                        center.grades = update_center_form.cleaned_data['grades']
                        center.subjectscovered = update_center_form.cleaned_data['subjectscovered']
                        center.noofchildren = update_center_form.cleaned_data['noofchildren']
                        center.launchdate = update_center_form.cleaned_data['launchdate']
                        center.description = update_center_form.cleaned_data['description']
                        center.orgunit_partner = update_center_form.cleaned_data['orgunit_partner']
                    center.save()
                    return HttpResponseRedirect('/partner/centers/')
                else:
                    return render(request, 'add_center_to_school.html',{'center_form': update_center_form,'update_flag': True})
            else:
                return HttpResponseRedirect('/partner/centers/')
        except Center.DoesNotExist:
            return HttpResponseRedirect('/partner/centers/')
    else:
        return HttpResponseRedirect('/partner/centers/')
@login_required
def mou_list(request, partner_id):
    partner_id = request.POST.get("partner_id_dropdown","")
    profile = UserProfile.objects.get(user=request.user)
    approved = Partner.objects.values('status').filter(contactperson_id=request.user.id)
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@oartner", approved
    is_partner=False
    partners_name = ''
    if profile:
        if len(profile.role.filter(name = "Partner Admin")) > 0 or len(profile.role.filter(name = "OUAdmin")):
            partner = Partner.objects.get(contactperson=request.user)
            is_partner=True
        else :
            partner = None

    if not request.user.is_superuser:
        Partner_mou_list=Partner_MOU.objects.filter(partner_id=request.user.id).order_by('-updated_on')
    else:
        Partner_mou_list=Partner_MOU.objects.all().order_by('-updated_on')
        if request.GET.get('search_results') and request.GET.get('search_results') != '':
            partners_name = request.GET.get('search_results')
            Partner_mou_list=Partner_MOU.objects.filter(partner_name=partners_name).order_by('-updated_on')

    if partner_id:
        Partner_mou_list = Partner_mou_list.filter(partner_id=partner_id).order_by('-updated_on')
    unique_partner_choicse = Partner_mou_list.values_list("partner__id","partner_name").distinct()

    partner_names=Partner_MOU.objects.filter(partner_id=request.user.id)
    if partner_names:
        partner = Partner.objects.get(contactperson=request.user)
        partner_name_org=partner.name_of_organization
        print "partner_name_org",partner_name_org
    else :
        partner_name_org=None
    
    is_school_admin = False
    is_mou = False
    if has_role(request.user.userprofile, "School Admin"):
        is_school_admin = True
        is_mou = True
    return render(request, 'mou_list.html',{'Partner_mou_list': Partner_mou_list,'parter_dropdown_choices':unique_partner_choicse,'partner':partner,'is_partner':is_partner,'partner_name_org':partner_name_org, 'partners_name':partners_name, "is_school_admin" : is_school_admin, "is_mou" : is_mou})


@login_required
def mou_form(request):
    partner = Partner.objects.get(contactperson_id=request.user.id)
    user_state = request.user.userprofile.state
    if user_state == "Andhra Pradesh":
        user_state = "Andra Pradesh"
    elif user_state == "Telangana":
        user_state = "Telengana"
    board = Center.objects.filter(state = user_state).values_list('board',flat = True)[:1]
    acaedemic_year = Ayfy.objects.filter(board = board).order_by('-id')[0]
    academic_year_end = acaedemic_year.end_date
    # print("$$$$$$$$$$$$$$$$$$$$$$",academic_year_end)
    academic_year_end = datetime.strftime(academic_year_end,'%b %d, %Y')
    # print("#############################",academic_year_end)
    dated=partner.dt_updated.strftime('%b %d, %Y')
    rate_of_coordinator = 3000
    rate_of_volunteer = 1000
    status = "Null"
    mou_form = {}
    mou_form['partner_name_org'] = partner.address
    mou_form['partner_name'] = partner.name
    mou_form['partner_org_name'] = partner.name_of_organization
    mou_form['academic_year_end'] = academic_year_end
    mou_form['dated'] = dated
    mou_form['mou_id'] = None
    is_school_admin = False
    is_mou = False
    if has_role(request.user.userprofile, "School Admin"):
        is_school_admin = True
        is_mou = True
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",partner)
    return render(request,'mou_form.html',{"mou_form": mou_form, "partner": partner,"is_partner":partner,"agreement":1,"rate_of_coordinator":rate_of_coordinator,
                                    'rate_of_volunteer':rate_of_volunteer, "is_school_admin":is_school_admin, "is_mou":is_mou})


@login_required
def create_mou(request):
    try:
        partner=request.user.id
        partner_name=request.user.first_name+" "+ request.user.last_name
        No_Of_schools = request.POST.get('id_no_of_school')
        No_of_Coordinators = request.POST.get('id_no_of_coordinator')
        estimated_cost=request.POST.get('id_total_cost')
        Author_signature=request.POST.get('id_author')
        mou_value=request.POST.get('id_mou_value')
        No_of_volunteer =request.POST.get('id_no_of_volunteer')
        Start_Date =request.POST.get('id_available_from')
        No_Of_Months =request.POST.get('no_of_months')
        rate_of_coordinator =request.POST.get('rate_of_coordinator')
        rate_of_volunteer =request.POST.get('rate_of_volunteer')
        # print "@@@@@@@@nio",No_Of_Months
        if str(Start_Date) is '':
            Start_Date = None

        Admin_signature=request.POST.get('Admin')
        status = request.POST.get('save')
        partner_mou=Partner_MOU.objects.create(partner_id=partner, partner_name=partner_name, status=status, Start_Date=Start_Date, No_of_volunteer=No_of_volunteer, Author_signature=Author_signature, mou_value=mou_value, No_Of_schools=No_Of_schools, No_of_Coordinators=No_of_Coordinators, estimated_cost=estimated_cost,No_Of_Months = No_Of_Months,
                                                    rate_of_volunteer=rate_of_volunteer,rate_of_coordinator=rate_of_coordinator)
        partner_mou.save()
        return HttpResponseRedirect('/partner/partner_mou/')
    except:
        return HttpResponseRedirect('/partner/partner_mou')


@login_required
def update_mou(request, mou_id):
    if request.method == 'GET':
        mou_form = {}
        mou_form['mou_id'] = mou_id
        partner = None
        partner_mou_obj = Partner_MOU.objects.get(id=mou_id)
        if not request.user.is_superuser:
            partner = Partner.objects.get(contactperson=request.user)
        mou_form['partner_mou_obj'] = Partner_MOU.objects.get(id=mou_id)
        id_partner = mou_form['partner_mou_obj'].partner_id
        partner = Partner.objects.get(contactperson=id_partner)
        mou_form['partner_name_address'] = partner.address
        mou_form['partner_org_name'] = partner.name_of_organization
        mou_form['dated'] = partner.dt_updated.strftime('%b %d, %Y')
        partner_id = partner_mou_obj.partner_id
        user_state = UserProfile.objects.values_list("state",flat= True).filter(user_id = partner_id)
        if "Andhra Pradesh" in user_state:
            user_state = "Andra Pradesh"
        elif "Telangana" in user_state:
            user_state = "Telengana"

        rate_of_coordinator = partner_mou_obj.rate_of_coordinator
        rate_of_volunteer = partner_mou_obj.rate_of_volunteer
        board = Center.objects.filter(state = user_state).values_list('board',flat = True)[:1]
        acaedemic_year = Ayfy.objects.filter(board = board).order_by('-id')[0]
        mou_form['academic_year_end'] = datetime.strftime(acaedemic_year.end_date,'%b %d, %Y')
        mou_form['mou_value'] = mou_form['partner_mou_obj'].mou_value
        if mou_form['partner_mou_obj'].Start_Date:
            mou_form['start_date'] = mou_form['partner_mou_obj'].Start_Date.strftime('%Y-%m-%d')
        total_co_ordinator_cost = int(partner_mou_obj.No_of_Coordinators)*int(rate_of_coordinator)
        No_of_Coordinators = partner_mou_obj.No_of_Coordinators
        No_of_volunteer = partner_mou_obj.No_of_volunteer
        academic_year_end = acaedemic_year.end_date
        no_of_month = partner_mou_obj.No_Of_Months
        no_of_schools = partner_mou_obj.No_Of_schools
        total_volunteer_cost = int(partner_mou_obj.No_of_volunteer) * int(rate_of_volunteer) *int(no_of_month)
        grand_total = total_co_ordinator_cost + total_volunteer_cost
        estimated_end_date = ((partner_mou_obj.Start_Date + relativedelta(months=int(no_of_month)) - relativedelta(days=int(1)))).strftime('%d/%m/%Y')
        estimated_end_date_full = ((partner_mou_obj.Start_Date + relativedelta(months=int(no_of_month)) - relativedelta(days=int(1)))).strftime('%d-%b-%Y')
        start_date_full = (partner_mou_obj.Start_Date).strftime('%d-%b-%Y')
        status = partner_mou_obj.status

        try:
            is_partner = Partner.objects.get(contactperson_id=request.user.id)
        except:
            is_partner = ""
        context = {
            'mou_form': mou_form,
            "partner": partner,
            "is_partner":is_partner,
            "total_volunteer_cost":total_volunteer_cost,
            "No_of_Coordinators" : No_of_Coordinators,
            "No_of_volunteer" : No_of_volunteer,
            "total_co_ordinator_cost" : total_co_ordinator_cost,
            "grand_total" : grand_total,
            "no_of_month" : no_of_month,
            "agreement" : 1,
            "academic_year_end":academic_year_end,
            "estimated_end_date":estimated_end_date,
            "estimated_end_date_full":estimated_end_date_full,
            "start_date_full":start_date_full,
            "no_of_schools":no_of_schools,
            "rate_of_coordinator":rate_of_coordinator,
            "rate_of_volunteer":rate_of_volunteer,
            "status":status,
            "is_school_admin" : False,
            "is_mou" : False
        }
        if has_role(request.user.userprofile, 'School Admin'):
            context['is_school_admin'] = True
            context['is_mou'] = True
        return render(request,'mou_form.html',context)
    elif request.method == 'POST':
        partner_update = Partner_MOU.objects.get(id=mou_id)
        mou_value = request.POST.get('id_mou_value')
        #admin_signature

        partner_update.status = request.POST.get('save')
        if has_role(request.user.userprofile,'Partner Admin') or has_role(request.user.userprofile,'School Admin'):
            partner_update.Author_signature = request.POST.get('id_author')
            partner_update.No_Of_schools = request.POST.get('id_no_of_school')
            partner_update.No_of_Coordinators = request.POST.get('id_no_of_coordinator')
            partner_update.No_of_volunteer=request.POST.get('id_no_of_volunteer')
            partner_update.No_Of_Months=request.POST.get('no_of_months')
            partner_update.estimated_cost=request.POST.get('id_total_cost')
            partner_update.Start_Date=request.POST.get('id_available_from')
            partner_update.rate_of_volunteer = request.POST.get('rate_of_volunteer')
            partner_update.rate_of_coordinator = request.POST.get('rate_of_coordinator')

            
        else:
            partner_update.No_Of_schools = request.POST.get('id_no_of_school')
            partner_update.No_of_Coordinators = request.POST.get('id_no_of_coordinator')
            partner_update.No_of_volunteer=request.POST.get('id_no_of_volunteer')
            partner_update.Admin_signature = request.POST.get('id_author_evd')
            partner_update.rate_of_volunteer = request.POST.get('rate_of_volunteer')
            partner_update.rate_of_coordinator = request.POST.get('rate_of_coordinator')
            partner_update.estimated_cost=request.POST.get('id_total_cost')
            if request.POST.get('save') == 'Complete':
                partner_update.status = request.POST.get('save')
        start_date =request.POST.get('id_available_from')
        if str(start_date) is '':
            start_date = None
        partner_update.Start_Date = start_date

        partner_update.mou_value = mou_value
        try:

            partner_update.save()
        except:
            pass
        return HttpResponseRedirect('/partner/partner_mou/')


def get_mou_partner(request):
    search_term = request.GET.get('term', '')
    user_id=request.user.id
    db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                            user=settings.DATABASES['default']['USER'],
                            passwd=settings.DATABASES['default']['PASSWORD'],
                            db=settings.DATABASES['default']['NAME'],
                            charset="utf8",
                            use_unicode=True)
    users_cur = db.cursor(MySQLdb.cursors.DictCursor)
    query = "select distinct partner_name as value from partner_partner_mou where partner_name like '%"+search_term+"%' group by id limit 50"
    users_cur.execute(query)
    volunteers = users_cur.fetchall()
    db.close()
    users_cur.close()
    return HttpResponse(simplejson.dumps(volunteers))

def  view_of_partner_engagementt(request,id):
    partner_mou_obj = Partner_MOU.objects.get(id=id)
    partner = Partner.objects.get(contactperson=partner_mou_obj.partner_id)
    partner_name_org=partner.name_of_organization
    return render(request,'view_partner_engagement.html',{'partner_mou_obj':partner_mou_obj,'partner_name_org':partner_name_org})

def view_of_mou (request,id):
    partner_mou_obj = Partner_MOU.objects.get(id=id)
    partner_name=partner_mou_obj.partner_name

    partner = Partner.objects.get(contactperson=partner_mou_obj.partner_id)
    partner_address=partner.address
    partner_name_org=partner.name_of_organization
    if request.user.is_superuser:
        partner_id = partner_mou_obj.partner_id
        user_state = UserProfile.objects.values_list("state",flat= True).filter(user_id = partner_id)
    else:
        user_state = request.user.userprofile.state
    if "Andhra Pradesh" in user_state:
        user_state = "Andra Pradesh"
    elif "Telangana" in user_state:
        user_state = "Telengana"
    rate_of_coordinator = partner_mou_obj.rate_of_coordinator
    rate_of_volunteer = partner_mou_obj.rate_of_volunteer

    board = Center.objects.filter(state = user_state).values_list('board',flat = True)[:1]
    acaedemic_year = Ayfy.objects.filter(board = board).order_by('-id')[0]
    academic_year_end = acaedemic_year.end_date
    total_co_ordinator_cost = int(partner_mou_obj.No_of_Coordinators) * int(rate_of_coordinator)
    difference = (academic_year_end- partner_mou_obj.Start_Date).days
    no_of_month = int(partner_mou_obj.No_Of_Months)
    total_volunteer_cost = (int(partner_mou_obj.No_of_volunteer) * int(rate_of_volunteer) * no_of_month)
    total_cost = total_volunteer_cost + total_co_ordinator_cost
    academic_year_end = (partner_mou_obj.Start_Date + relativedelta(months=int(no_of_month)) - relativedelta(days=int(1))).strftime('%b %d, %Y')
    acc_start_date = partner_mou_obj.Start_Date.strftime('%b %d, %Y')
    dated=partner.dt_updated.strftime('%b %d, %Y')
    return render(request,'view_mou.html',{'dated':dated,'partner_mou_obj':partner_mou_obj,'partner_name':partner_name,'partner_address':partner_address,'partner_name_org':partner_name_org, 'academic_year_end': academic_year_end,
                            'acc_start_date': acc_start_date, 'total_coordinator_cost':total_co_ordinator_cost, 'total_volunteer_cost': total_volunteer_cost, 
                            "total_month" : no_of_month, 'total_cost':total_cost,"date_added":partner_mou_obj.added_on.strftime('%b %d, %Y'),"date_updated":partner_mou_obj.updated_on.strftime('%b %d, %Y'),
                            "rate_of_coordinator":rate_of_coordinator,"rate_of_volunteer":rate_of_volunteer})




@login_required
def generate_certificate_for_Memorandum_of_Understanding(request,id):
    print "request,id",request,id
    if request.method=='GET':
        partner_mou_obj = Partner_MOU.objects.get(id=id)
        if request.user.is_superuser:
            partner_id = partner_mou_obj.partner_id
            user_state = UserProfile.objects.values_list("state",flat= True).filter(user_id = partner_id)
        else:
            user_state = request.user.userprofile.state
        if "Andhra Pradesh" in user_state:
            user_state = "Andra Pradesh"
        elif "Telangana" in user_state:
            user_state = "Telengana"
        rate_of_coordinator = partner_mou_obj.rate_of_coordinator
        rate_of_volunteer = partner_mou_obj.rate_of_volunteer

        no_of_month = (partner_mou_obj.No_Of_Months)
        board = Center.objects.filter(state = user_state).values_list('board',flat = True)[:1]
        acaedemic_year = Ayfy.objects.filter(board = board).order_by('-id')[0]
        academic_year_end_date = (partner_mou_obj.Start_Date + relativedelta(months=int(no_of_month)) - relativedelta(days=int(1))).strftime('%b %d, %Y')
        academic_year_end = (partner_mou_obj.Start_Date + relativedelta(months=int(no_of_month)) - relativedelta(days=int(1))).strftime('%b %d, %Y')
        print("@@@@@@@@@@@@@@@@@@@@@@",academic_year_end)
        id_author=partner_mou_obj.partner_name
        start_date=partner_mou_obj.Start_Date
        academicc_start_date = partner_mou_obj.Start_Date.strftime('%b %d, %Y')
        difference = no_of_month
        # academicc_start_date = academicc_start_date.strftime('%d-%m-%Y')
        print "start_date",difference
        # end_date=(start_date + datetime.timedelta(6*365/12))
        print "end_date",partner_mou_obj.added_on
        date_cretaed=partner_mou_obj.added_on.strftime('%b %d, %Y')
        acc_start_date=partner_mou_obj.Start_Date.strftime('%b %d, %Y')
        acc_start_date_pdf=partner_mou_obj.Start_Date.strftime('%d-%m-%Y')
        id_admin=partner_mou_obj.Admin_signature
        date_updated=partner_mou_obj.updated_on.strftime('%b %d, %Y')
        id_partner=partner_mou_obj.partner_id
        # add_months = datetime.datetime.start_date() + relativedelta(months=+6)
        # print "add_months",add_months
        partner = Partner.objects.get(contactperson=id_partner)
        print "partner",partner
        partner_name_org=partner.name_of_organization
        partner_name_address=partner.address
        dated=partner.dt_updated.strftime('%b %d, %Y')
        academicc_start_date = partner_mou_obj.Start_Date
        #values
        No_of_Coordinators = partner_mou_obj.No_of_Coordinators
        tot_amount_coordinator = str(int(No_of_Coordinators) * int(rate_of_coordinator))
        No_of_volunteer = partner_mou_obj.No_of_volunteer
        tot_amount_volunteer = str(int(No_of_volunteer) * int(rate_of_volunteer) * int(difference))
        grand_total = str(int(tot_amount_volunteer) + int(tot_amount_coordinator))
        No_Of_schools = partner_mou_obj.No_Of_schools
        fle_path = "MOU/"+id_author+"_"+acc_start_date_pdf+".pdf"
        pdfFileObj = open('static/mou_document/MOU1.pdf', 'rb')
        packet = StringIO.StringIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont('Times-Bold',12)
        can.drawString(100, 400,id_author)
        can.drawString(110, 362,date_cretaed)
        can.drawString(330, 400,id_admin)
        can.drawString(360, 362,date_updated)
        can.save()
        packet.seek(0)
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pdfWriter = PyPDF2.PdfFileWriter()
        pageObj1 = pdfReader.getPage(0)
        pageObj2 = pdfReader.getPage(1)
        pageObj3 = pdfReader.getPage(2)
        pageObj4 = pdfReader.getPage(3)
        input = PyPDF2.PdfFileReader(packet)
        pageObj2.mergePage(input.getPage(0))

    packet = StringIO.StringIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Times-Bold',12)

    can.drawString(107, 578,partner_name_org)
    can.drawString(107, 557,partner_name_address)
    can.drawString(270, 545,acc_start_date)
    can.drawString(309, 271,acc_start_date)
    can.drawString(392, 271,academic_year_end)
    can.drawString(235, 271,difference)
    can.save()
    packet.seek(0)
    input = PyPDF2.PdfFileReader(packet)

    pageObj1.mergePage(input.getPage(0))
    packet = StringIO.StringIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Times-Bold',12)
    can.drawString(107, 645.5,partner_name_org)
    can.drawString(255, 630,acc_start_date)
    can.drawString(205, 600,acc_start_date)
    can.drawString(305, 353,No_of_Coordinators)
    can.drawString(193, 519,No_Of_schools)
    can.drawString(305, 502,No_of_Coordinators)
    can.drawString(300, 485,acc_start_date)
    can.drawString(460, 485,academic_year_end)
    can.drawString(305, 288,No_of_volunteer)
    can.drawString(380, 353,"1 Time")
    can.drawString(380, 288,difference + "Months")
    can.drawString(460, 353,tot_amount_coordinator)
    can.drawString(460, 288,tot_amount_volunteer)
    can.drawString(460, 225,grand_total + " INR")
    can.save()
    packet.seek(0)
    input = PyPDF2.PdfFileReader(packet)
    pageObj3.mergePage(input.getPage(0))

    pdfWriter.addPage(pageObj1)
    pdfWriter.addPage(pageObj2)
    pdfWriter.addPage(pageObj3)
    pdfWriter.addPage(pageObj4)

    outputStream = open(fle_path, "wb")

    pdfWriter.write(outputStream)
    outputStream.close()
    certificate = open(fle_path, "r")
    from django.core.servers.basehttp import FileWrapper
    response = HttpResponse(FileWrapper(certificate), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + fle_path + '"'
    return response



@login_required
def generate_certificate_for_Terms_of_Engagement(request,id):
    print "request,id",request,id
    if request.method=='GET':
        partner_mou_obj = Partner_MOU.objects.get(id=id)
        if request.user.is_superuser:
            partner_id = partner_mou_obj.partner_id
            user_state = UserProfile.objects.values_list("state",flat= True).filter(user_id = partner_id)
        else:
            user_state = request.user.userprofile.state
        if "Andhra Pradesh" in user_state:
            user_state = "Andra Pradesh"
        elif "Telangana" in user_state:
            user_state = "Telengana"


        board = Center.objects.filter(state = user_state).values_list('board',flat = True)[:1]
        acaedemic_year = Ayfy.objects.filter(board = board).order_by('-id')[0]
        academic_year_end_date = acaedemic_year.end_date
        academic_year_end = datetime.strftime(academic_year_end_date,'%b %d, %Y')
        id_author=partner_mou_obj.partner_id
        partner = Partner.objects.get(contactperson=id_author)
        partner_name_org=partner.name_of_organization
        acc_start_date=partner_mou_obj.Start_Date.strftime('%b %d, %Y')
        name_partner=partner_mou_obj.partner_name
        acc_start_date_pdf=partner_mou_obj.Start_Date.strftime('%d-%m-%Y')

        fle_path = "MOU/"+name_partner+"_"+acc_start_date_pdf+".pdf"
        pdfFileObj = open('static/mou_document/Terms of Engagement.pdf', 'rb')
        packet = StringIO.StringIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont('Times-Bold',14)
        can.drawString(100, 633,"-"+partner_name_org)

        can.save()
        packet.seek(0)
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pdfWriter = PyPDF2.PdfFileWriter()
        pageObj1 = pdfReader.getPage(0)
        pageObj2 = pdfReader.getPage(1)
        pageObj3 = pdfReader.getPage(2)
        pageObj4 = pdfReader.getPage(3)
        pageObj5 = pdfReader.getPage(4)
        pageObj6 = pdfReader.getPage(5)


        input = PyPDF2.PdfFileReader(packet)
        pageObj5.mergePage(input.getPage(0))


        packet = StringIO.StringIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont('Times-Bold',12)

        can.drawString(80, 560,"-"+partner_name_org)
        can.save()
        packet.seek(0)
        input = PyPDF2.PdfFileReader(packet)

        pageObj1.mergePage(input.getPage(0))
        packet = StringIO.StringIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont('Times-Bold',12)
        can.save()
        packet.seek(0)
        input = PyPDF2.PdfFileReader(packet)
        pageObj3.mergePage(input.getPage(0))
        pdfWriter.addPage(pageObj1)
        pdfWriter.addPage(pageObj2)
        pdfWriter.addPage(pageObj3)
        pdfWriter.addPage(pageObj4)
        pdfWriter.addPage(pageObj5)
        pdfWriter.addPage(pageObj6)
        can.drawString(200, 633,partner_name_org)
        input = PyPDF2.PdfFileReader(packet)
        pageObj3.mergePage(input.getPage(0))


        outputStream = open(fle_path, "wb")
        pdfWriter.write(outputStream)
        outputStream.close()
        certificate = open(fle_path, "r")
        from django.core.servers.basehttp import FileWrapper
        response = HttpResponse(FileWrapper(certificate), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="' + fle_path + '"'
        return response


@login_required
def my_users(request):
    print("usersssssssssssssssssssssssss")
    if has_role(request.user.userprofile, "School Admin"):
        schooladmin = Partner.objects.get(contactperson=request.user)
        schooladmin_name = schooladmin.name_of_organization
        reference_channel_id = ReferenceChannel.objects.values_list("id",flat= True).filter(partner_id = schooladmin.id)
        users=UserProfile.objects.filter(referencechannel_id=reference_channel_id)

        if users:
            users_count=users.count()
        else :
            users_count= "no"
        schooladmins_schools_count = MySchool.objects.filter(partner_id=schooladmin.id).count()
        admin_assigned_roles = ["Class Assistant", "Field co-ordinator", "Delivery co-ordinator"]
        roles = Role.objects.filter(name__in=admin_assigned_roles)
        return render(request,'my_users.html',{'myschools_count':schooladmins_schools_count,
                    'roles':roles,'partner_name':schooladmin_name,'users_count':users_count,
                    "is_school_admin":schooladmin})
    else:
        partner = Partner.objects.get(contactperson=request.user)
        partner_name=partner.name_of_organization
        reference_channel_id = ReferenceChannel.objects.values_list("id",flat= True).filter(partner_id = partner.id)
        users=UserProfile.objects.filter(referencechannel_id=reference_channel_id)

        if users:
            users_count=users.count()
        else :
            users_count= "no"
        is_partner_volunteer,is_partner_delivery,is_partner_funding = [False] * 3
        for ptype in partner.partnertype.all():
            if ptype.id == 1:
                is_partner_volunteer = True
            elif ptype.id == 2:
                is_partner_delivery = True
            elif ptype.id == 3:
                is_partner_funding = True

            if has_role(request.user.userprofile,'OUAdmin'):
                myschools_count = MySchool.objects.filter(center__orgunit_partner=partner.id).count()
            elif has_role(request.user.userprofile,'Partner Admin'):
                myschools_count = MySchool.objects.filter(Q(center__funding_partner=partner.id)|Q(center__delivery_partner=partner.id)).count()
            else:
                myschools_count = MySchool.objects.filter(partner_id=partner.id,status='Eligible').count()
            if has_role(request.user.userprofile,'Partner Admin'):
                mycenters_count = Center.objects.filter(Q(funding_partner_id=partner.id,status='Active')|Q(orgunit_partner_id=partner.id,status='Active')|Q(delivery_partner_id=partner.id,status='Active')).count()
            else:
                mycenters_count = Center.objects.filter(partner_school__partner_id=partner.id,status='Active').count()
            admin_assigned_roles = ["Class Assistant", "TSD Panel Member", "vol_admin", "vol_co-ordinator", "Field co-ordinator", "Delivery co-ordinator", "support", 'Digital School Manager']
            roles = Role.objects.filter(name__in=admin_assigned_roles)
        return render(request,'my_users.html',{'partner':partner,'is_partner_volunteer':is_partner_volunteer,'is_partner_delivery':is_partner_delivery,'myschools_count':myschools_count,
                                                                 'mycenters_count':mycenters_count,'roles':roles,'is_partner_funding':is_partner_funding,'partner_name':partner_name,'users_count':users_count,"is_partner":partner,"is_funding_partner":is_partner_funding})
                                                                 

@login_required
def org_details(request):
    if request.method == 'GET' or request.method == 'POST' :
        try:
            partner = Partner.objects.get(contactperson=request.user)
            is_funding_partner = ""
            if partner:
                try:
                    is_funding_partner = Partner.objects.values("partnertype").filter(contactperson=request.user,partnertype=3)
                except:
                    is_funding_partner = ""
            else:
                is_funding_partner = ""
            partner_name=partner.name_of_organization
            is_partner_volunteer,is_partner_delivery,is_partner_funding = [False] * 3
            for ptype in partner.partnertype.all():
                if ptype.id == 1:
                    is_partner_volunteer = True
                elif ptype.id == 2:
                    is_partner_delivery = True
                elif ptype.id == 3:
                    is_partner_funding = True
            if request.method == 'GET':
                if has_role(request.user.userprofile,'OUAdmin'):
                    myschools_count = MySchool.objects.filter(center__orgunit_partner=partner.id).count()
                elif has_role(request.user.userprofile,'Partner Admin'):
                    myschools_count = MySchool.objects.filter(Q(center__funding_partner=partner.id)|Q(center__delivery_partner=partner.id)).count()
                else:
                    myschools_count = MySchool.objects.filter(partner_id=partner.id,status='Eligible').count()
                if has_role(request.user.userprofile,'Partner Admin'):
                    mycenters_count = Center.objects.filter(Q(funding_partner_id=partner.id,status='Active')|Q(orgunit_partner_id=partner.id,status='Active')|Q(delivery_partner_id=partner.id,status='Active')).count()
                else:
                    mycenters_count = Center.objects.filter(partner_school__partner_id=partner.id,status='Active').count()
                admin_assigned_roles = ["Class Assistant", "TSD Panel Member", "vol_admin", "vol_co-ordinator", "Field co-ordinator", "Delivery co-ordinator", "support"]
                roles = Role.objects.filter(name__in=admin_assigned_roles)
                
                return render(request,'organisation_detail.html',{'partner':partner,'is_partner_volunteer':is_partner_volunteer,'is_partner_delivery':is_partner_delivery,'myschools_count':myschools_count,
                                                                 'mycenters_count':mycenters_count,'roles':roles,'is_partner_funding':is_partner_funding,'partner_name':partner_name,'is_partner':partner,"is_funding_partner":is_funding_partner})
            elif request.method == 'POST':
                partner.name_of_organization = request.POST.get('org_name')
                partner.address = request.POST.get('address')
                photo = request.FILES.get('org_logo')
                if photo:
                    partner.logo = photo
                if is_partner_volunteer or is_partner_delivery:
                    try:
                        partner_org_details = DeliveryPartnerOrgDetails.objects.get(partner=partner)
                    except DeliveryPartnerOrgDetails.DoesNotExist:
                        partner_org_details = DeliveryPartnerOrgDetails.objects.create(partner=partner)
                    partner_org_details.website_address = request.POST.get('website_address')
                    partner_org_details.office_phone = request.POST.get('office_phone')
                    partner.email = request.POST.get('email')
                    partner_org_details.type_of_org = request.POST.get('org_type')
                    if is_partner_delivery:
                        partner_org_details.date_of_reg = request.POST.get('date_of_reg')
                        partner_org_details.place_of_reg = request.POST.get('org_reg_place')
                        partner_org_details.reg_number = request.POST.get('reg_number')
                        partner_org_details.number = request.POST.get('number')
                        partner_org_details.fcra_reg_number = request.POST.get('fcra_reg_number')
                        partner_org_details.fcra_acc_number = request.POST.get('fcra_acc_number')
                        partner_org_details.bank_name = request.POST.get('bank_name')
                        partner_org_details.ifsc_code = request.POST.get('ifsc_code')
                        partner_org_details.acc_holder_name = request.POST.get('acc_name')
                        partner_org_details.acc_number = request.POST.get('acc_number')
                        partner_org_details.type_of_acc = request.POST.get('acc_type')
                    partner_org_details.save()
                partner.save()
                return HttpResponseRedirect('/partner/org_details/')

        except Partner.DoesNotExist:
            return HttpResponseRedirect('/myevidyaloka/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


# Partner Application REST APIs
def isObjectNotEmpty(keyObject):
    return genUtility.isObjectNotEmpty(keyObject)


def appendToStringIfNotEmpty(parentString, substring):
    if substring:
        parentString + ", " + substring
    return parentString


def getValueElseThrowException(requestBodyParams, keyName):
    return genUtility.getValueElseThrowException(requestBodyParams, keyName)


def sendErrorResponse(request, errorConstant):
    return genUtility.getStandardErrorResponse(request, errorConstant)


def getSuccessResponseStatus(request, responseData):
    return genUtility.getSuccessApiResponse(request, responseData)


def sendPartnerSignUpEmailToSuperUsers(user,partner,userProfile):
    try:
        from_email = settings.DEFAULT_FROM_EMAIL
        name_of_organization = partner.name_of_organization
        mobile = ''
        if userProfile:
            mobile = userProfile.phone
        ### Sending Email to SuperUsers
        #evladmins = User.objects.filter(is_superuser=True,is_active=True)
        #mail_to = [adm.email for adm in evladmins]
        mail_to = ["digitalschool@evidyaloka.org"]
        systemEmailConfig = genUtility.getDictObjectFromSystemSettingJSONForKey("systemUserNotificationConfig")
        if systemEmailConfig:
            emailsToBeUsed = systemEmailConfig.get("partnerSignUpNotificationEmails")
            if emailsToBeUsed:
                mail_to = emailsToBeUsed

        prefixString = ""
        if genUtility.isNonProdEnvironment():
            prefixString = "[Test Environment] "

        mail_subject = prefixString + 'New Partner Signed up via eVidyaloka learning app'
        mail_args = {'username': user.username, 'org_name': name_of_organization,
                     'contactperson_email': user.email,"contactperson_phone":mobile}
        mail_body = get_template('mail/_partner/App_Partner_SignUp_Notify_SuperUSer.html').render(
            Context(mail_args))
        adm_mail = EmailMessage(mail_subject, mail_body, to=mail_to, from_email= from_email)
        adm_mail.content_subtype = 'html'
        if genUtility.canSendEmail() is True:
            adm_mail.send()
        else:
            print("EMAIL WILL NOT BE SENT")
        return True
    except Exception as e:
        print("sendPartnerSignUpEmailToSuperUsers", e)
        logService.logInfo("sendPartnerSignUpEmailToSuperUsers", e.message)
        return False

def sendPartnerWelcomeEmail(poc_email,poc_fname,password,name_of_organization,poc_lname,orgEmail):
    try:
        ### Sending Registration Mail to the User by Copying to Organization
        args = {'username': poc_email, 'name': str(poc_fname) + ' ' + str(poc_lname), 'password': password,
                'name_of_organization': name_of_organization}
        mail = ''
        body = ''
        subject = 'Welcome to eVidyaloka - ' + str(name_of_organization)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [poc_email]
        body = get_template('partner_signup_mail.html').render(Context(args))
        if orgEmail:
            cc = [orgEmail]
            mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
        else:
            mail = EmailMessage(subject, body, to=to, from_email=from_email)
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
    except Exception as e:
        print("sendPartnerWelcomeEmail", e)
        logService.logInfo("sendPartnerWelcomeEmail", e.message)
        return False

def registerAndSetupPartner(organisationObj,contactObj,status):
    try:
        name = organisationObj.get('partnerName')
        name_of_organization = organisationObj.get('name')
        email = organisationObj.get('email')
        phone = organisationObj.get('phone')

        # Format organization address
        org_address = ''
        gAddress = organisationObj.get('address')
        if gAddress:
            org_address = gAddress

        poc_fname = contactObj.get('fname')
        poc_lname = contactObj.get('lname')
        poc_email = contactObj.get('email')
        poc_phone = contactObj.get('phone')

        ### Creating User and UserProfile
        new_user = User.objects.create_user(email=poc_email, username=poc_email)
        password = User.objects.make_random_password()
        new_user.set_password(password)
        new_user.save()
        user = authenticate(username=poc_email, password=password)
        user.first_name = poc_fname
        user.last_name = poc_lname
        userp = user.userprofile
        userp.phone = poc_phone
        ### Creating Partner Info
        partner_model = Partner.objects.create(contactperson=user, name=name,
                                               name_of_organization=name_of_organization, phone=phone,
                                               email=email, address=org_address, status=status, source='2')
        partner_model.save()
        ### Creating Reference Channel Entry
        try:
            ref_channel = ReferenceChannel.objects.get(name=name_of_organization)
            ref_channel.partner = partner_model
        except:
            ref_channel = ReferenceChannel.objects.create(name=name_of_organization, partner=partner_model)
        ref_channel.save()
        ### Updating Users Referencechannel and Saving his Profile
        userp.referencechannel = ref_channel
        ### Adding PartnerAdmin Role to the User
        role = Role.objects.get(name='Partner Admin')
        if role:
            userp.role.add(role)
            userp.pref_roles.add(role)
        userp.reset_pasword = True
        userp.profile_completion_status = 1
        userp.organization_complete_status = "Ready"
        userp.profile_complete_status = "Ready"

        userp.save()
        user.save()

        typeObj = Partnertype.objects.get(name="Digital Partner")
        if typeObj is not None:
            partner_model.partnertype.add(typeObj)
            partner_model.save()

        ### Sending Registration Mail to the User by Copying to Organization
        sendPartnerWelcomeEmail(poc_email, poc_fname, password, name_of_organization, poc_lname, email)
        sendPartnerSignUpEmailToSuperUsers(user, partner_model, userp)
        return (partner_model,user)

    except Exception as e:
        print("registerAndSetupPartner", e)
        logService.logInfo("registerAndSetupPartner", e.message)
        return (None,None)

@csrf_exempt
def partner_registration_api(request):
    if genUtility.is_basic_auth_authenticated(request) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == 'POST':
        requestBodyParams = simplejson.loads(request.body)
        organisationObj = requestBodyParams.get('organization')
        if isObjectNotEmpty(organisationObj):

            name = organisationObj.get('partnerName')
            name_of_organization = organisationObj.get('name')
            email = organisationObj.get('email')
            phone = organisationObj.get('phone')

            # Format organization address
            org_address = ''
            gAddress = organisationObj.get('address')
            if gAddress:
                org_address = gAddress

            if name and name_of_organization and email and phone and gAddress:
                pass
            else:
                return sendErrorResponse(request, "kMissingReqFields")

            if genUtility.isValidEmailAddress(email) is False:
                return sendErrorResponse(request, "korgInvalidEmail")

            # org_address = appendToStringIfNotEmpty(org_address,organisationObj.get('address1'))
            # org_address = appendToStringIfNotEmpty(org_address, organisationObj.get('address2'))
            # org_address = appendToStringIfNotEmpty(org_address, organisationObj.get('district'))
            # org_address = appendToStringIfNotEmpty(org_address, organisationObj.get('state'))
            # org_address = appendToStringIfNotEmpty(org_address, organisationObj.get('pincode'))

            contactObj = requestBodyParams.get('contact')
            if isObjectNotEmpty(contactObj):
                # TODO:Custom exception handling
                poc_fname = getValueElseThrowException(contactObj, 'fname')
                poc_lname = getValueElseThrowException(contactObj, 'lname')
                poc_email = getValueElseThrowException(contactObj, 'email')
                poc_phone = getValueElseThrowException(contactObj, 'phone')

                if poc_email and poc_phone and poc_fname:
                    pass
                else:
                    return sendErrorResponse(request, "kMissingReqFields")

                if genUtility.isValidEmailAddress(poc_email) is False:
                    return sendErrorResponse(request, "kInvalidEmailId")

                try:
                    existing_user = User.objects.get(username=poc_email)
                    return sendErrorResponse(request, "kUserExistAlready")
                except User.DoesNotExist:
                    pass
                except User.MultipleObjectsReturned:
                    return sendErrorResponse(request, "kUserExistAlready")
                    ### Checking Reference Channel for the Organizarion Already Exists or not
                try:
                    query = Q()
                    query = query & Q(name=name_of_organization)
                    query = query & ~Q(partner_id=None)
                    ref_name = ReferenceChannel.objects.get(query)
                    return sendErrorResponse(request, "kUserExistSameOrg")
                except ReferenceChannel.DoesNotExist:
                    pass
                except:
                    return sendErrorResponse(request, "kInvalidRequest")

                partner_model,userObj = registerAndSetupPartner(organisationObj, contactObj,'New')
                if partner_model:
                    responseData = {
                        "id": partner_model.id
                    }
                    return getSuccessResponseStatus(request, responseData)
                else:
                    return sendErrorResponse(request, "kParterRegistrationFailed")
            else:
                return sendErrorResponse(request, "kMissingReqFields")
        else:
            return sendErrorResponse(request, "kMissingReqFields")

    return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def partner_login_api(request):
    try:
        if genUtility.is_basic_auth_authenticated(request) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        requestBodyParams = simplejson.loads(request.body)
        username = requestBodyParams.get("username")
        password = requestBodyParams.get("password")
        user = authenticate(username=username, password=password)
        if user is None or user.is_authenticated() is False:
            return sendErrorResponse(request, "kInvalidCred")

        # Get roles for this user
        userRoles = []
        userProfile = user.userprofile;
        prefRoles = userProfile.pref_roles.all()
        for role in prefRoles:
            if role.name == "Partner Admin":
                userRoles.append("DSP")
            if role.name == "Digital School Manager":
                userRoles.append("DSM")

        partner = userProfile.referencechannel.partner
        if partner and genUtility.isDigitalPartner(partner):
            pass
        else:
            return sendErrorResponse(request, "kOnlyDigitalPartners")

        isResetPWdRequired = 0
        if userProfile.reset_pasword:
            isResetPWdRequired = 1

        # Generate session keys
        sessionObj = genUtility.createSessionForUser(user)
        session_key = sessionObj.session_key
        expiryTimeStamp = genUtility.getTimeStampFromDate(sessionObj.expiry_time)
        responseData = {
            "userId": user.id,
            "email": user.email,
            "fname": user.first_name,
            "lname": user.last_name,
            "roles": userRoles,
            "sessionId": session_key,
            "sessionExpiryTime": str(expiryTimeStamp),
            "isResetPwdRequired": isResetPWdRequired,
            "partnerId": partner.id,
            "partnerStatus": partner.status,
            "userStatus": userProfile.status
        }

        return getSuccessResponseStatus(request, responseData)
    except Exception as e:
        logService.logException("partner login", e.message)
        return sendErrorResponse(request, "kInvalidCred " + e.message)


@csrf_exempt
def reset_password_api(request):
    try:
        if request.method == 'POST':
            requestBodyParams = simplejson.loads(request.body)
            userId = requestBodyParams.get("userId")
            oldPassword = requestBodyParams.get("oldPassword")
            newPassword = requestBodyParams.get("newPassword")
            currentPassword = request.user.password  # user's current password
            if (userId and
                    isObjectNotEmpty(oldPassword) and
                    isObjectNotEmpty(newPassword)):
                try:
                    userInstance = User.objects.get(id=userId)
                except:
                    return sendErrorResponse(request, "kUserDoesNotExist")
                try:
                    userProfileObj = UserProfile.objects.get(user__id=userId)
                except:
                    return sendErrorResponse(request, "kUserProfileDoesNotExist")
                matchCheck = check_password(oldPassword, currentPassword)
                if matchCheck:
                    if oldPassword == newPassword:
                        return sendErrorResponse(request, "kPassShouldNotMatch")
                    else:
                        if genUtility.passwordValidator(newPassword):
                            userInstance.set_password(newPassword)
                            userProfileObj.reset_pasword = False
                            userInstance.save()
                            userProfileObj.save()
                            responseData = {
                                "message": "Password changed successfully"
                            }
                            genUtility.invalidateSession(request.currentSession)
                            return getSuccessResponseStatus(request, responseData)
                        else:
                            return sendErrorResponse(request, "kPasswordValidationFailed")
                else:
                    return sendErrorResponse(request, "kInvalidOldPass")
            else:
                return sendErrorResponse(request, "kMissingReqFields")
    except:
        return sendErrorResponse(request, "kUnknownError")


@csrf_exempt
def profile_api_generic(request, userId):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == 'PUT':
        return update_profile_api(request, userId)
    else:
        if request.method == 'GET':
            return get_profile_list(request, userId)
        else:
            return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def get_profile_list(request, userId):
    try:
        responseData = {
            "organization": {
                "id": None,
                "partnerName": None,
                "fname": None,
                "lname": None,
                "email": None,
                "address": None,
                "phone": None,
                "partnerStatus": None,
                "logo": None
            },
            "user": {}
        }

        if userId:
            # check both the requested profile and login user are same
            if int(userId) != request.user.id:
                return genUtility.getForbiddenRequestErrorApiResponse(request)
            # Djnago query to get data from DB
            try:
                userInstance = UserProfile.objects.filter(
                    user__id=int(userId)).select_related('referencechannel').get()
            except UserProfile.DoesNotExist:
                return sendErrorResponse(request, "kUserDoesNotExist")
            # Get roles for this user
            userRoles = []
            prefRoles = userInstance.pref_roles.all()
            for role in prefRoles:
                if role.name == "Partner Admin":
                    userRoles.append("DSP")
                if role.name == "Digital School Manager":
                    userRoles.append("DSM")
            try:
                organizationInstance = userInstance.referencechannel.partner
            except:
                organizationInstance = None
            # Organization data
            if organizationInstance and userRoles:
                responseData["organization"]["id"] = organizationInstance.id
                responseData["organization"]["partnerName"] = organizationInstance.name
                responseData["organization"]["name"] = organizationInstance.name_of_organization
                responseData["organization"]["email"] = organizationInstance.email
                responseData["organization"]["address"] = organizationInstance.address
                responseData["organization"]["phone"] = organizationInstance.phone
                responseData["organization"]["partnerStatus"] = organizationInstance.status
                try:
                    responseData["organization"]["logo"] = organizationInstance.logo.name
                except:
                    responseData["organization"]["logo"] = None

            # User data
            responseData["user"]["id"] = userId
            responseData["user"]["fname"] = userInstance.user.first_name
            responseData["user"]["lname"] = userInstance.user.last_name
            responseData["user"]["phone"] = userInstance.phone
            responseData["user"]["email"] = userInstance.user.email
            try:
                if userInstance.picture and userInstance.picture != '':
                    responseData["user"]["profileImageShortUrl"] = userInstance.picture
                else:
                    responseData["user"]["profileImageShortUrl"] = None
                    if userInstance.profile_pic_doc:
                        responseData["user"]["profileImageFullUrl"] = userInstance.profile_pic_doc.url
                    else:
                        responseData["user"]["profileImageFullUrl"] = None
            except:
                pass
            responseData["user"]["userStatus"] = userInstance.status
            responseData["user"]["roles"] = userRoles
            return getSuccessResponseStatus(request, responseData)
        else:
            return sendErrorResponse(request, "kMissingReqFields")
    except:
        return sendErrorResponse(request, "kUnknownError")


@csrf_exempt
def update_profile_api(request, userId):
    try:
        if not userId:
            return sendErrorResponse(request, "kMissingReqFields")
        ### Check use is DSP and active
        partnerObj = ''
        roles = genUtility.returnRole(userId)

        if genUtility.isDSP is False:
            return sendErrorResponse(request, "kInvalidRequest")
        try:
            userObj = User.objects.get(id=userId, is_active=True)
        except:
            return sendErrorResponse(request, "kUserDoesNotExist")
        ### Get data
        requestBodyParams = simplejson.loads(request.body)
        organisationObj = requestBodyParams.get('organization')
        if isObjectNotEmpty(organisationObj):
            name = organisationObj.get('partnerName')
            email = organisationObj.get('email')
            phone = organisationObj.get('phone')
            gAddress = organisationObj.get('address')

            if not name and not email and not phone and not gAddress:
                return sendErrorResponse(request, "kMissingReqFields")

            if genUtility.isValidEmailAddress(email) is False:
                return sendErrorResponse(request, "korgInvalidEmail")
            ### GET Partner table
            try:
                partnerObj = Partner.objects.get(contactperson=userObj)
            except:
                return sendErrorResponse(request, "kInvalidPartner")
            if name and (name != partnerObj.name):
                partnerObj.name = name
            if email and (email != partnerObj.email):
                partnerObj.email = email
            if phone and (phone != partnerObj.phone):
                partnerObj.phone = phone
            if gAddress and (gAddress != partnerObj.address):
                partnerObj.address = gAddress

            partnerObj.save()

        contactObj = requestBodyParams.get('user')
        if isObjectNotEmpty(contactObj):
            # TODO:Custom exception handling
            poc_phone = getValueElseThrowException(contactObj, 'phone')
            profilePicId = contactObj.get('profilePicId')

            if not poc_phone:
                return sendErrorResponse(request, "kMissingReqFields")
            ### GET UserProfile table
            try:
                userProfileObj = UserProfile.objects.get(user=userObj)
            except:
                return sendErrorResponse(request, "kUserProfileDoesNotExist")
            if poc_phone and (poc_phone != userProfileObj.phone):
                userProfileObj.phone = poc_phone
            if profilePicId:
                try:
                    userDoc = UserDocument.objects.get(id=profilePicId)
                except:
                    return sendErrorResponse(request, "kFileDoesnotExist")
            if profilePicId and userDoc.id != profilePicId:
                userProfileObj.profile_pic_id = profilePicId

            userProfileObj.save()

        if isObjectNotEmpty(contactObj) or isObjectNotEmpty(organisationObj):
            dataObj = {
                "id": userId,
                "message": "Updated successfully"
            }
            return getSuccessResponseStatus(request, dataObj)
        else:
            return sendErrorResponse(request, "kMissingReqFields")
    except:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def course_provider_api(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:
        if request.method == 'GET':
            responseData = {
                "courseProviders": []
            }
            code = request.GET.get("code")
            if code:
                allCourseProviders = CourseProvider.objects.filter(code=code).order_by('name')
            else:
                allCourseProviders = CourseProvider.objects.filter(status=True).order_by('name')

            for singleCourseProvider in allCourseProviders:
                singleCourseProviderDict = {}
                singleCourseProviderDict["id"] = singleCourseProvider.id
                singleCourseProviderDict["name"] = singleCourseProvider.name
                singleCourseProviderDict["type"] = singleCourseProvider.type
                singleCourseProviderDict["code"] = singleCourseProvider.code

                responseData["courseProviders"].append(singleCourseProviderDict)

            return getSuccessResponseStatus(request, responseData)
        else:
            return sendErrorResponse(request, "kInvalidRequest")
    except:
        return sendErrorResponse(request, "kUnknownError")


@csrf_exempt
def course_api(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == 'GET':
        try:
            courseProvider = request.GET.get("courseProvider")
            grade = request.GET.get("grade")
            languageId = request.GET.get("languageId")
            if courseProvider and grade:
                responseData = {
                    "courses": []
                }

                languageObj = None
                if languageId:
                    try:
                        languageObj = Language.objects.get(id=languageId)
                    except:
                        return sendErrorResponse(request, "kMissingReqFields")

                if languageObj:
                    courseObjects = Course.objects.filter(grade=grade, board_name=courseProvider,status="active",language_id=languageObj.id).select_related('language').order_by('subject')
                else:
                    courseObjects = Course.objects.filter(grade=grade, board_name=courseProvider,status="active").select_related('language').order_by('subject')

                for singleCourse in courseObjects:
                    data = {}
                    data["id"] = singleCourse.id
                    data["grade"] = singleCourse.grade
                    data["name"] = singleCourse.subject
                    responseData["courses"].append(data)
                return getSuccessResponseStatus(request, responseData)
            else:
                return sendErrorResponse(request, "kMissingReqFields")
        except:
            return sendErrorResponse(request, "kUnknownError")
    else:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def academic_api(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == 'GET':
        try:
            responseData = {
                "academicYears": []
            }
            courseProviderId = request.GET.get("courseProviderId")
            if courseProviderId:
                courseProviderObject = CourseProvider.objects.get(
                    id=courseProviderId)
                academicObjects = Ayfy.objects.filter(
                    board=courseProviderObject.code
                ).order_by('-start_date')

                counterVal = 0

                for singleacademic in academicObjects:
                    data = {}
                    data["id"] = singleacademic.id
                    data["academicYear"] = str(singleacademic.start_date.year) + '-' + str(singleacademic.end_date.year)
                    responseData["academicYears"].append(data)
                    counterVal = counterVal + 1
                    if counterVal >= 2:
                        break


                return getSuccessResponseStatus(request, responseData)
            else:
                return sendErrorResponse(request, "kMissingReqFields")
        except:
            return sendErrorResponse(request, "kUnknownError")
    else:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def offering_api_generic(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == 'POST':
        return create_offering_api(request)
    else:
        if request.method == 'GET':
            return get_offering_list(request)
        else:
            return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def create_offering_api(request):
    try:
        requestBodyParams = simplejson.loads(request.body)
        digitalSchoolId = requestBodyParams.get("digitalSchoolId")
        courseId = requestBodyParams.get("courseId")
        academicYearId = requestBodyParams.get("academicYearId")
        startDate = requestBodyParams.get("startDate")
        endDate = requestBodyParams.get("endDate")

        if courseId and digitalSchoolId and academicYearId and startDate and endDate:
            try:
                courseObject = Course.objects.get(id=courseId)
            except:
                return sendErrorResponse(request, "kCourseDoesNotExist")
            try:
                centerObject = Center.objects.get(digital_school=digitalSchoolId)
            except:
                return sendErrorResponse(request, "kCenterDoesNotExist")
            try:
                academicObject = Ayfy.objects.get(id=academicYearId)
            except:
                return sendErrorResponse(request, "kAcademicYearDoesNotExist")
            try:
                userObj = User.objects.get(id=request.user.id)
            except:
                return sendErrorResponse(request, "kUserDoesNotExist")

            ### get course_type from courseObject
            course_type = courseObject.type
            if course_type:
                course_type = course_type.lower()
            if course_type is not None and course_type == 'c':
                status = 'not_approved'

            offeringInstance = Offering.objects.create(
                course=Course.objects.get(id=courseId),
                center=Center.objects.get(digital_school=digitalSchoolId),
                academic_year=Ayfy.objects.get(id=academicYearId),
                status="pending",
                course_type=course_type,
                start_date=genUtility.dataFromTimeStampToObj(startDate),
                end_date=genUtility.dataFromTimeStampToObj(endDate),
                created_by=userObj,
                updated_by=userObj
            )
            responseData = {
                "id": offeringInstance.id,
                "message": "Offering course added successfully!!"
            }
            return getSuccessResponseStatus(request, responseData)
        else:
            return sendErrorResponse(request, "kMissingReqFields")
    except:
        return sendErrorResponse(request, "kUnknownError")


def get_offering_list(request):
    try:
        courseProviderId = request.GET.get("courseProviderId")
        digitalSchoolId = request.GET.get("digitalSchoolId")
        grade = request.GET.get("grade")
        AcademicYearId = request.GET.get("AcademicYearId")
        courseProviderObject = ''
        languageId = request.GET.get("languageId")
        try:
            courseProviderObject = CourseProvider.objects.get(id=courseProviderId)
        except:
            pass


        responseData = {
            "offerings": []
        }

        ncurDateTime = genUtility.getCurrentTime()
        if digitalSchoolId:
            offeringObjects = Offering.objects.filter(
                center__digital_school_id=digitalSchoolId,
                status__in=['pending','running'],
                end_date__gte=ncurDateTime,
            ).select_related('course','academic_year')
            offeringObjectsFinal = offeringObjects
        else:
            return sendErrorResponse(request, "kMissingReqFields")
        if languageId:
            offeringObjects = offeringObjects.filter(course__language_id=languageId)

        if grade and AcademicYearId and courseProviderObject:
            gradesObj = offeringObjects.filter(course__grade=grade)
            yearsObj = gradesObj.filter(academic_year__id=AcademicYearId)
            offeringObjectsFinal = yearsObj.filter(course__board_name=courseProviderObject.code)
        if grade and AcademicYearId and not courseProviderObject:
            gradesObj = offeringObjects.filter(course__grade=grade)
            offeringObjectsFinal = gradesObj.filter(academic_year__id=AcademicYearId)
        if grade and courseProviderObject and not AcademicYearId:
            gradesObj = offeringObjects.filter(course__grade=grade)
            offeringObjectsFinal = gradesObj.filter(course__board_name=courseProviderObject.code)
        if AcademicYearId and courseProviderObject and not grade:
            yearsObj = offeringObjects.filter(academic_year__id=AcademicYearId)
            offeringObjectsFinal = yearsObj.filter(course__board_name=courseProviderObject.code)
        if grade and not AcademicYearId and not courseProviderObject:
            offeringObjectsFinal = offeringObjects.filter(course__grade=grade)
        if AcademicYearId and not courseProviderObject and not grade:
            offeringObjectsFinal = offeringObjects.filter(academic_year__id=AcademicYearId)
        if courseProviderObject and not grade and not AcademicYearId:
            offeringObjectsFinal = offeringObjects.filter(course__board_name=courseProviderObject.code)
        for singleoffering in offeringObjectsFinal:
            data = {}
            data["id"] = singleoffering.id
            data["CourseProvider"] = singleoffering.course.board_name
            data["grade"] = singleoffering.course.grade
            data["courseName"] = singleoffering.course.subject
            if singleoffering.academic_year:
                data["AcademicYear"] = str(singleoffering.academic_year.start_date.year) + '-' + str(
                    singleoffering.academic_year.end_date.year)
            else:
                data["AcademicYear"] = None
            data["StartDate"] = singleoffering.start_date.isoformat()
            data["EndDate"] = singleoffering.end_date.isoformat()
            responseData["offerings"].append(data)

        return getSuccessResponseStatus(request, responseData)
    except:
        return sendErrorResponse(request, "kUnknownError")


def check_if_school_name_duplicate(schoolName):
    try:
        dschool = DigitalSchool.objects.get(name=schoolName)
        if dschool is not None:
            return dschool
    except DigitalSchool.DoesNotExist:
        return None
    except DigitalSchool.MultipleObjectsReturned:
        return dschool[0]


@csrf_exempt
def school_api_generic(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == 'POST':
        return create_school_api(request)
    else:
        if request.method == 'GET':
            return get_school_list(request)
        else:
            return sendErrorResponse(request, "kInvalidRequest")


def createStatesAndPincodes(stateList,digitalSchool):
    try:
        for counter in range(len(stateList)):
            stateObj = stateList[counter]
            stateId = stateObj.get("stateId")
            pincodes = stateObj.get("pincodes")
            #logService.logInfo("stateId",stateId)
            try:
                stateObj = State.objects.get(id=stateId)
            except:
                pass
            #logService.logInfo("pincode lenth", len(pincodes))
            if pincodes and len(pincodes) > 0:
                for j in range(len(pincodes)):
                    pObj = pincodes[j]
                    pId, pcode = pObj["id"], pObj["code"]
                    #logService.logInfo("pid and code ", str(pId) + " " +str(pcode))
                    if pId and pcode:
                        locPref = DigitalSchool_Location_Preference.objects.create(
                            digital_school=digitalSchool,
                            state=stateObj,
                            state_code=stateObj.code,
                            sel_type="2",
                            pincode_id=pId,
                            pincode_key=pcode,
                            created_by_id=settings.SYSTEM_USER_ID_AUTH,
                            updated_by_id=settings.SYSTEM_USER_ID_AUTH
                        )
                        locPref.save()
            else:
                locPref = DigitalSchool_Location_Preference.objects.create(digital_school=digitalSchool, state=stateObj,
                                                                           state_code=stateObj.code, sel_type="1",created_by_id=settings.SYSTEM_USER_ID_AUTH,updated_by_id=settings.SYSTEM_USER_ID_AUTH)
                locPref.save()
    except Exception as e:
        print("createStatesAndPincodes ", e)
        logService.logException("createStatesAndPincodes", e.message)

def deleteStatesAndPincodes(stateIdList,digitalSchool,pincodeIdList):
    try:
        if stateIdList and len(stateIdList) > 0:
            # delete all ids here
            data = DigitalSchool_Location_Preference.objects.filter(state_id__in=stateIdList,
                                                                    digital_school=digitalSchool).delete()


        if pincodeIdList and len(pincodeIdList) > 0:
            # delete all ids here
            data = DigitalSchool_Location_Preference.objects.filter(pincode_id__in=pincodeIdList,
                                                                    digital_school=digitalSchool).delete()

    except Exception as e:
        print("deleteStatesAndPincodes ", e)
        logService.logException("deleteStatesAndPincodes", e.message)




def create_school_api(request):
    try:
        if genUtility.checkUserAuthentication(request.user) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        userReq = request.user
        if request.method == 'POST':
            requestBodyParams = simplejson.loads(request.body)
            partnerId = getValueElseThrowException(requestBodyParams, 'partnerId')
            schoolName = getValueElseThrowException(requestBodyParams, 'name')
            purpose = requestBodyParams.get('purpose')
            schoolDescription = getValueElseThrowException(requestBodyParams, 'description')
            logoId = getValueElseThrowException(requestBodyParams, 'logoId')
            courseProvider = getValueElseThrowException(requestBodyParams, 'courseProvider')
            bannerId = requestBodyParams.get("bannerId")
            ### Get address details
            taluk = requestBodyParams.get('taluk')
            district = requestBodyParams.get('district')
            state = requestBodyParams.get('state')
            pin_code = requestBodyParams.get('pin_code')
            is_bulk = requestBodyParams.get('is_bulk')
            selectedStates = requestBodyParams.get('selectedStates')

            # Check if user has permission to create school and partner is of type DS
            # if yes, Check if School name exist
            # if does not exist,then create school
            # check if logoId document exist
            partner = None
            if is_bulk and request.user.is_authenticated:
                contactperson = get_object_or_none(User, id=partnerId)
                if contactperson: partner = get_object_or_none(Partner, contactperson=contactperson)
                if not partner: return sendErrorResponse(request, "kInvalidRequest")
            else:
                try:
                    partner = Partner.objects.get(contactperson=userReq)
                    if partner.id != partnerId: return sendErrorResponse(request, "kInvalidRequest")
                except Partner.DoesNotExist:
                    return sendErrorResponse(request, "kInvalidRequest")
                except Partner.MultipleObjectsReturned:
                    partner = partner[0] 

            try:
                courseProviderObj = CourseProvider.objects.get(code=courseProvider)
            except:
                return sendErrorResponse(request, "kInvalidRequest")

            isDigitalPartner = genUtility.isDigitalPartner(partner)
            if isDigitalPartner is False:
                return sendErrorResponse(request, "kOnlyDigitalPartners")
            else:
                dschool = None
                dschool = check_if_school_name_duplicate(schoolName)
                if dschool is not None:
                    return sendErrorResponse(request, "kSchoolNameDuplicate")

                userDoc = None
                logUrl = None
                try:
                    userDoc = UserDocument.objects.get(id=logoId)
                    logUrl = userDoc.url
                except:
                    return sendErrorResponse(request, "kFileDoesnotExist")

                bannerDoc = None
                bannerUrl = None
                if bannerId:
                    try:
                        bannerDoc = UserDocument.objects.get(id=bannerId)
                        bannerUrl = bannerDoc.url
                    except Exception as e:
                        return sendErrorResponse(request, "kFileDoesnotExist")


                school = DigitalSchool.objects.create(
                    name=schoolName,
                    partner_owner=partner,
                    school_type="digital",
                    status="Pending",
                    description=schoolDescription,
                    logo_url=logUrl,
                    logo_doc=userDoc,
                    statement_of_purpose=purpose,
                    course_provider = courseProviderObj,
                    course_provider_code = courseProvider,
                    created_by=userReq,
                    updated_by=userReq,
                    taluk=taluk,
                    district=district,
                    state=state,
                    pin_code=pin_code,
                    banner_url=bannerUrl,
                    banner_doc=bannerDoc
                )
                school.save()
                userDoc.belongs_to = school.id
                userDoc.save()

                if selectedStates and len(selectedStates) > 0:
                    createStatesAndPincodes(selectedStates,school)

                dataObj = {
                    "id": school.id,
                    "message": "school created successfully"
                }
                return getSuccessResponseStatus(request, dataObj)

    except Exception as e:
        logService.logException("create_school_api",e.message)
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def update_school_api(request, schoolId):
    try:
        if genUtility.checkUserAuthentication(request.user) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        if schoolId is None or schoolId == "":
            return sendErrorResponse(request, "kMissingReqFields")
        userReq = request.user
        if request.method == 'PATCH' or request.method == 'PUT':
            requestBodyParams = simplejson.loads(request.body)
            partnerId = getValueElseThrowException(requestBodyParams, 'partnerId')
            # Check if user has permission to Edit school and partner is of type DS
            # if yes, Check if School name exist
            # if does not exist,then create school
            # check if logoId document exist
            partner = None
            try:
                partner = Partner.objects.get(contactperson=userReq)
                if partner.id != partnerId:
                    return sendErrorResponse(request, "kInvalidPartner")
            except Partner.DoesNotExist:
                return sendErrorResponse(request, "kInvalidPartner")
            except Partner.MultipleObjectsReturned:
                partner = partner[0]

            isDigitalPartner = genUtility.isDigitalPartner(partner)
            if isDigitalPartner is False:
                return sendErrorResponse(request, "kOnlyDigitalPartners")
            else:
                dschool = None
                try:
                    dschool = DigitalSchool.objects.get(id=schoolId, partner_owner=partner)
                except DigitalSchool.DoesNotExist:
                    return sendErrorResponse(request, "kInvalidRequest")
                except DigitalSchool.MultipleObjectsReturned:
                    dschool = dschool[0]
                isBannerUpdated = False
                isLogoUpdated = False
                if (dschool.status == "Pending"):
                    # update key fields and logo
                    schoolName = requestBodyParams.get("name")
                    if schoolName and (schoolName != dschool.name):
                        dupSchool = check_if_school_name_duplicate(schoolName)
                        if dupSchool is not None:
                            return sendErrorResponse(request, "kSchoolNameDuplicate")
                        dschool.name = schoolName

                    purpose = requestBodyParams.get("purpose")
                    if purpose and (purpose != dschool.statement_of_purpose):
                        dschool.statement_of_purpose = purpose

                    schoolDescription = requestBodyParams.get("description")
                    if schoolDescription and (schoolDescription != dschool.description):
                        dschool.description = schoolDescription

                    schoolTaluk = requestBodyParams.get("taluk")
                    if schoolTaluk and (schoolTaluk != dschool.taluk):
                        dschool.taluk = schoolTaluk

                    schoolDistrict = requestBodyParams.get("district")
                    if schoolDistrict and (schoolDistrict != dschool.district):
                        dschool.district = schoolDistrict

                    schoolState = requestBodyParams.get("state")
                    if schoolState and (schoolState != dschool.state):
                        dschool.state = schoolState

                    schoolPincode = requestBodyParams.get("pin_code")
                    if schoolPincode and (schoolPincode != dschool.pin_code):
                        dschool.pin_code = schoolPincode

                    courseProvider = requestBodyParams.get("courseProvider")
                    if courseProvider and (dschool.course_provider_code is None or courseProvider != dschool.course_provider_code):
                        dschool.course_provider_code = courseProvider
                        try:
                            courseProviderObj = CourseProvider.objects.get(code=courseProvider)
                            dschool.course_provider = courseProviderObj
                        except:
                            pass

                    # update Logo if required
                    logoId = requestBodyParams.get("logoId")
                    if logoId and (dschool.logo_doc is None or logoId != dschool.logo_doc.id):
                        userDoc = None
                        logUrl = None
                        try:
                            userDoc = UserDocument.objects.get(id=logoId)
                            dschool.logo_url = userDoc.url
                            dschool.logo_doc = userDoc
                            userDoc.belongs_to = schoolId
                            isLogoUpdated = True
                        except:
                            return sendErrorResponse(request, "kFileDoesnotExist")

                # update non essential fields if any
                # update banner if required
                bannerId = requestBodyParams.get("bannerId")
                if bannerId and (dschool.banner_doc is None or bannerId != dschool.banner_doc.id):
                    banner_doc = None
                    bannerUrl = None
                    try:
                        bannerDoc = UserDocument.objects.get(id=bannerId)
                        dschool.banner_url = bannerDoc.url
                        dschool.banner_doc = bannerDoc
                        bannerDoc.belongs_to = schoolId
                        isBannerUpdated = True
                    except:
                        return sendErrorResponse(request, "kFileDoesnotExist")
                dschool.updated_on = genUtility.getCurrentTime()
                dschool.updated_by = request.user
                dschool.save()
                if isBannerUpdated is True:
                    dschool.banner_doc.save()
                if isLogoUpdated is True:
                    dschool.logo_doc.save()

                dataObj = {
                    "id": dschool.id,
                    "message": "school updated successfully"
                }
                return getSuccessResponseStatus(request, dataObj)
        else:
            return sendErrorResponse(request, "kInvalidRequest")
    except Exception as e:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def upload_user_document(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method != "POST":
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:
        intFormat = request.GET.get('format')  # png,jpg,pdf,doc,docx,jpeg
        intDocType = request.GET.get('doc_type')  # school_logo,school_banner,

        if intFormat is None or intDocType is None:
            return sendErrorResponse(request, "kMissingReqFields")

        cloudFolderName = settings.SCHOOL_DOCUMENT_STORAGE_FOLDER
        return docUploadService.upload_user_document_s3(request, "partner", None, cloudFolderName, None,None)
    except Exception as e:
        return sendErrorResponse(request, "kInvalidRequest")



def check_if_partner_exist(contactObjt, partnerId):
    try:
        partner = Partner.objects.get(contactperson=contactObjt, id=partnerId)
        if partner is not None:
            return partner
    except Partner.DoesNotExist:
        return None
    except Partner.MultipleObjectsReturned:
        return partner[0]


def getLocationPreferenceForSchool(schoolId):
    try:
        stateDictionary = {}
        locList = DigitalSchool_Location_Preference.objects.filter(digital_school_id=schoolId,
                                                                   status="active").select_related('state', 'pincode')

        for counter in range(len(locList)):
            locObj = locList[counter]
            stateId = locObj.state.id
            stateObj = stateDictionary.get(str(stateId))
            if stateObj is None:
                stateObj = {}
                stateObj["stateId"] = locObj.state.id
                stateObj["name"] = locObj.state.name
                stateObj["code"] = locObj.state.code
                stateDictionary[str(stateId)] = stateObj

            pincodeList = stateObj.get('pincodes')
            if pincodeList is None:
                pincodeList = []
                stateObj['pincodes'] = pincodeList

            if locObj.pincode and locObj.pincode_id >= 1:
                pObj = locObj.pincode
                pincodeObj = {'id': pObj.id, 'pincode': pObj.pincode, 'district': pObj.district, 'taluk': pObj.taluk}
                pincodeList.append(pincodeObj)
        return stateDictionary
    except Exception as e:
        print("getLocationPreferenceForSchool", e)
        logService.logException("getLocationPreferenceForSchool", e.message)
        return None

def get_school_list_with_filters(request, schoolId, userType, partnerId, isDetailRequired):
    # Check the usertype and do the authroisation check
    # if authorised, then query schools if more than 1
    # if authorised, then get school details for the Id

    if userType is None or userType == "" or partnerId is None:
        return sendErrorResponse(request, "kMissingReqFields")
    partner = None
    if userType == "DSP":
        partner = check_if_partner_exist(request.user, partnerId)
        if partner is None:
            return sendErrorResponse(request, "kInvalidPartner")
    elif userType == "DSM":
        partner = Partner.objects.get(id=partnerId)
        pass

    isDetailedschooldata = False
    courseProviderCode = None
    if schoolId:
        schoolId = long(schoolId)
        if isinstance(schoolId, (int, long)):
            isDetailedschooldata = True
        else:
            schoolId = None
    try:
        roleObj = Role.objects.get(name="Digital School Manager")
        roleStr = str(roleObj.id)
        parterIdStr = str(partner.id)
        schoolString = ""
        if schoolId:
            schoolString = " and ds.id=" + str(schoolId) + " "
        dsmChecksStr = ""
        if userType == "DSM":
            dsmChecksStr = " and staff.user_id=" + str(request.user.id) + " "
        elif userType == "DSP":
            userIdFilter = request.GET.get("userId")
            if userIdFilter and genUtility.checkIfParamIfInteger(userIdFilter):
                dsmChecksStr = " and staff.user_id=" + str(long(userIdFilter)) + " "

        fieldArray = ["id", "name", "status", "taluk", "district", "state", "pinCode", "description", "purpose",
                        "bannerUrl", "logoUrl", "logoId", "bannerId", "createdOn", "approvedOn","courseProviders",
                        "centerId", "dsmId", "dsmFirstName", "dsmLastName", "dsmUsername", "courseCount", "grades",
                        "studentCount"
                        ]
        
        cursor = connection.cursor()
        sqlQuery = '''select ds.id, ds.name, ds.status,ds.taluk,ds.district,ds.state,ds.pin_code, ds.description,ds.statement_of_purpose,ds.banner_url,ds.logo_url,ds.logo_doc_id,ds.banner_doc_id,ds.created_on,ds.approved_on,ds.course_provider_code,
        ct.id,au.id,au.first_name,au.last_name,au.username,count(DISTINCT ofr.id),group_concat(distinct cr.grade),count(DISTINCT scn.student_id)   
        from web_digitalschool as ds 
        LEFT JOIN web_center as ct on (ct.digital_school_id = ds.id)
        LEFT JOIN web_digitalcenterstaff as staff on (staff.digital_school_id = ds.id and staff.role_id=''' + roleStr + ''' and staff.status="Active")
        LEFT JOIN auth_user as au on (staff.user_id = au.id)
        LEFT JOIN web_offering as ofr on (ofr.center_id = ct.id AND ofr.status != 'completed')
        LEFT JOIN web_course as cr on (cr.id = ofr.course_id)
        LEFT JOIN student_student_school_enrollment as scn on (scn.digital_school_id = ds.id)
        WHERE ds.status != 'Inactive' AND ds.partner_owner_id = ''' + parterIdStr + schoolString + dsmChecksStr + ''' GROUP BY ds.id,ct.id,au.id'''

        cursor.execute(sqlQuery)
        schoolRecords = cursor.fetchall()
        schoolsList = []
        fieldCount = len(fieldArray)
        for eachRecord in schoolRecords:
            eachSchool = {}
            for i in range(fieldCount):
                fieldName = fieldArray[i]
                if fieldName == "createdOn" or fieldName == "approvedOn":
                    timeStamp = genUtility.getTimeStampFromDate(eachRecord[i])
                    if timeStamp:
                        eachSchool[fieldName] = str(timeStamp)
                elif fieldName == "grades":
                    gradeData = eachRecord[i]
                    if gradeData:
                        grades = gradeData.split(',')
                        if grades and len(grades) > 0:
                            grades = sorted(grades)
                        eachSchool[fieldName] = grades
                    pass
                elif fieldName == "courseProviders":
                    eachSchool[fieldName] = [{"code":eachRecord[i]}]
                    courseProviderCode = eachRecord[i]
                else:
                    eachSchool[fieldName] = eachRecord[i]
            if isDetailedschooldata:
                eachSchool["courseProviders"] = []
                if courseProviderCode:
                    courseProviderObj = CourseProvider.objects.filter(code=courseProviderCode)
                    if courseProviderObj:
                        for singleObj in courseProviderObj:
                            data = {}
                            data["id"] = singleObj.id
                            data["code"] = singleObj.code
                            data["name"] = singleObj.name
                            eachSchool["courseProviders"].append(data)
                #get pincode and state data
                stateDictionary = getLocationPreferenceForSchool(schoolId)
                if stateDictionary and len(stateDictionary) > 0:
                    stateArray =  stateDictionary.values()
                    eachSchool["selectedStates"] = stateArray

            # eachSchool["studentCount"] = Student_School_Enrollment.objects.filter(digital_school_id=eachSchool["id"]).count()
            schoolsList.append(eachSchool)

        dataObject = {
            "schools": schoolsList
        }
        return getSuccessResponseStatus(request, dataObject)
    except Exception as e:
        print("get_school_list",e)
        traceback.print_exc()
        logService.logException("get_school_list", e.message)
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def get_school_list(request):
    try:
        if request.method != "GET":
            return sendErrorResponse(request, "kInvalidRequest")

        userType = request.GET.get('userType')
        partnerId = request.GET.get('partnerId')
        schoolId = request.GET.get('schoolId')
        return get_school_list_with_filters(request, schoolId, userType, partnerId, False)
    except Exception as e:
        logService.logException("get_school_list", e.message)
        return sendErrorResponse(request, "kInvalidRequest")


def get_user_list_by_filter(userObj, partnerIdStr, searchString, userIdStr, limitString, isCount, isDetailDataRequired):
    fieldArray = ["id", "firstName", "lastName", "email", "phone", "pictureUrl", "status", "state", "district", "taluk",
                  "pincode", "schoolCount"]
    if isCount:
        fieldArray = ["count"]

    fieldString = "au.id, au.first_name,au.last_name,au.email,prof.phone,prof.picture,prof.status, prof.state,prof.district,prof.city,prof.pincode, count(ds.id)"
    if isCount:
        fieldString = " count(DISTINCT au.id ) "

    groupByString = " GROUP BY au.id "
    if isCount:
        groupByString = ""
        limitString = ""

    queryString = '''SELECT  ''' + fieldString + '''
                        FROM  partner_partner as pt
                        INNER JOIN web_referencechannel as chan ON ( pt.id = chan.partner_id ) 
                        INNER JOIN web_userprofile as prof ON( prof.referencechannel_id = chan.id) 
                        INNER JOIN auth_user as au  ON ( au.id = prof.user_id AND au.is_active = 1) 
                        LEFT  JOIN web_digitalcenterstaff as staff ON ( staff.user_id = au.id and staff.status="Active")
                        LEFT  JOIN web_digitalschool as ds ON (ds.id = staff.digital_school_id) 
                        WHERE pt.id = ''' + partnerIdStr + searchString + userIdStr + groupByString + limitString

    cursor = connection.cursor()
    cursor.execute(queryString)
    userDataList = cursor.fetchall()
    userRespList = []
    fieldCount = len(fieldArray)
    for eachRecord in userDataList:
        eachObject = {}
        for i in range(fieldCount):
            fieldName = fieldArray[i]
            eachObject[fieldName] = eachRecord[i]

        if isDetailDataRequired is True:
            schools = []
            try:
                userId = eachObject['id']
                dataList = DigitalCenterStaff.objects.filter(user_id=userId, status="Active").prefetch_related(
                    'digital_school')
                for j in range(len(dataList)):
                    staffObj = dataList[j]
                    schoolObj = staffObj.digital_school
                    schoolDict = {
                        "id": schoolObj.id,
                        "name": schoolObj.name,
                        "description": schoolObj.description,
                        "purpose": schoolObj.statement_of_purpose,
                        "logoUrl": schoolObj.logo_url,
                    }
                    schools.append(schoolDict)
            except Exception as e:
                logService.logException("school listing detail", e.message)
                pass
            eachObject["schoolsAssigned"] = schools
        userRespList.append(eachObject)

    return userRespList


def partner_users_list(request):
    try:
        partnerId = request.GET.get('partnerId')
        searchKey = request.GET.get('searchKey')
        page = request.GET.get('page')
        count = request.GET.get('count')
        userId = request.GET.get('userId')
        if partnerId is None:
            return sendErrorResponse(request, "kMissingReqFields")
        else:
            partner = check_if_partner_exist(request.user, partnerId)
            if partner is None:
                return sendErrorResponse(request, "kInvalidPartner")
            else:
                queryOffset = 0
                limitRecord = 50
                if page and count and genUtility.checkIfParamIfInteger(page) and genUtility.checkIfParamIfInteger(
                        count):
                    limitRecord = int(count)
                    queryOffset = int(page) * limitRecord

                userIdStr = ""
                isDetailDataRequired = False
                if userId and genUtility.checkIfParamIfInteger(userId):
                    useridl = long(userId)
                    userIdStr = "AND au.id = " + str(useridl) + " "
                    isDetailDataRequired = True

                limitString = " LIMIT " + str(limitRecord) + " OFFSET " + str(queryOffset)
                partnerIdStr = str(partner.id) + " "
                searchString = ""

                if searchKey:
                    # verify search string
                    if genUtility.checkIfKeyIsSafeForQuery(searchKey) is False:
                        return sendErrorResponse(request, "kInvalidSearchKey")

                    searchString = " AND (au.first_name LIKE '%%" + str(
                        searchKey) + "%%' OR au.last_name LIKE '%%" + str(searchKey) + "%%') "
                    pass

                totalCount = 0
                if page and int(page) == 0 and isDetailDataRequired is False:
                    userCountData = get_user_list_by_filter(request.user, partnerIdStr, searchString, userIdStr,
                                                            limitString, True,
                                                            False)
                    if userCountData and len(userCountData) > 0:
                        totalCountDict = userCountData[0]
                        if totalCountDict and len(totalCountDict) > 0:
                            totalCount = totalCountDict["count"]

                userRespList = get_user_list_by_filter(request.user, partnerIdStr, searchString, userIdStr, limitString,
                                                       False,
                                                       isDetailDataRequired)
                dataObject = {
                    "users": userRespList,
                    "totalCount": totalCount
                }
                return getSuccessResponseStatus(request, dataObject)

    except Exception as e:
        logService.logException("partner user list", e.message)
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def add_users_api(request):
    try:
        requestBodyParams = simplejson.loads(request.body)
        ### GET user submitted data
        fname = getValueElseThrowException(requestBodyParams, "fname")
        lname = getValueElseThrowException(requestBodyParams, "lname")
        email = getValueElseThrowException(requestBodyParams, "email")
        phone = getValueElseThrowException(requestBodyParams, "phone")
        city = getValueElseThrowException(requestBodyParams, "taluk")
        state = getValueElseThrowException(requestBodyParams, "state")
        district = getValueElseThrowException(requestBodyParams, "district")
        pincode = getValueElseThrowException(requestBodyParams, "pincode")
        role = getValueElseThrowException(requestBodyParams, "role")
        digitalSchoolId = requestBodyParams.get("digitalSchoolId")
        profilePicId = requestBodyParams.get("profilePicId")

        ### Check email is validgetValueElseThrowException
        if genUtility.isValidEmailAddress(email) is False:
            return sendErrorResponse(request, "kInvalidEmailId")
        if role == "DSM" or role == "Digital School Manager":
            role = "Digital School Manager"

        ### USer exists or not
        try:
            existing_user = User.objects.get(email=email)
            return sendErrorResponse(request, "kUserExistAlready")
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            return sendErrorResponse(request, "kUserExistAlready")
        ### Check profile pic is exist
        if profilePicId:
            try:
                userDoc = UserDocument.objects.get(id=profilePicId)
                logUrl = userDoc.url
            except:
                return sendErrorResponse(request, "kFileDoesnotExist")
        ### Get partner preferrence
        try:
            referObj = ReferenceChannel.objects.get(partner__contactperson=request.user)
        except:
            return sendErrorResponse(request, "kReferenceChannelDoesNotExist")
        ### Get partner name
        partnerName = ''
        try:
            partnerName = referObj.partner.name
        except:
            pass
        ### Get login user object
        try:
            userObj = request.user
        except:
            return sendErrorResponse(request, "kUserDoesNotExist")
        ### GET role
        try:
            role = Role.objects.get(name=role)
        except:
            return sendErrorResponse(request, "kRoleDoesNotExist")
        DeliveryRole = ''
        try:
            DeliveryRole = Role.objects.get(name="Delivery co-ordinator")
        except:
            pass
        ### Create User and UserProfile
        new_user = User.objects.create_user(email=email, username=email)
        password = User.objects.make_random_password()
        new_user.set_password(password)
        new_user.save()
        user = authenticate(username=email, password=password)  ## remove
        user.first_name = fname
        user.last_name = lname
        userp = user.userprofile
        userp.phone = phone
        userp.profile_pic_id = profilePicId
        userp.pincode = pincode
        userp.district = district
        userp.state = state
        userp.city = city
        userp.referencechannel = referObj
        userp.profile_completion_status = 1
        userp.organization_complete_status = "Ready"
        userp.profile_complete_status = "Ready"

        if role:
            userp.role.add(role)
            userp.pref_roles.add(role)
        if DeliveryRole:
            userp.role.add(DeliveryRole)
            userp.pref_roles.add(DeliveryRole)
        if profilePicId:
            userDoc.belongs_to = userp.id
            userDoc.save()
            userp.profile_pic_doc = userDoc
            userp.picture = logUrl
        ### save User and UserProfile
        user.save()
        userp.save()

        ### Assign user to Digital school
        if digitalSchoolId:
            ### GET center
            centerObj = genUtility.getCenter(digitalSchoolId)
            ### GET school object
            try:
                schoolObj = DigitalSchool.objects.get(id=digitalSchoolId)
            except:
                return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")
            assign_user_school(digitalSchoolId, schoolObj, user, userObj, role, centerObj)

        ### Sending Registration Mail to the User
        args = {'username': email,
                'name': str(fname) + ' ' + str(lname),
                'password': password,
                'partnerName': partnerName,
                }
        mail = ''
        body = ''
        subject = 'Welcome to eVidyaloka - '
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email]
        body = get_template('welcome_mail_template.html').render(Context(args))
        if email:
            cc = [email]
            mail = EmailMessage(subject, body, to=to, cc=cc, from_email=from_email)
        else:
            mail = EmailMessage(subject, body, to=to, from_email=from_email)
        mail.content_subtype = 'html'

        try:
            if genUtility.canSendEmail() is True:
                print("EMAIL WILL BE SENT")
                mail.send()
            else:
                print("EMAIL WILL NOT BE SENT")
                pass
        except Exception as e:
            print("Add user email send exception ",e.message)
            logService.logException("Add user email send exception", e.message)
            pass


        dataObject = {
            "id": user.id,
            "message": "user added successfully!"
        }

        return getSuccessResponseStatus(request, dataObject)

    except Exception as e:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def edit_users_api(request, userId):
    try:
        if genUtility.checkUserAuthentication(request.user) is False:
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        if userId is None or userId == "":
            return sendErrorResponse(request, "kMissingReqFields")
        userReq = request.user
        if request.method == 'PATCH' or request.method == 'PUT':
            requestBodyParams = simplejson.loads(request.body)
            fname = requestBodyParams.get("fname")
            lname = requestBodyParams.get("lname")
            phone = requestBodyParams.get("phone")
            city = requestBodyParams.get("taluk")
            state = requestBodyParams.get("state")
            district = requestBodyParams.get("district")
            pincode = requestBodyParams.get("pincode")
            role = requestBodyParams.get("role")
            digitalSchoolId = requestBodyParams.get("digitalSchoolId")
            profilePicId = requestBodyParams.get("profilePicId")

            ### Check user exist or not
            try:
                userObj = User.objects.get(id=userId)
            except:
                return sendErrorResponse(request, "kUserDoesNotExist")
            if role == "DSM" or role == "Digital School Manager":
                role = "Digital School Manager"
            ### login user
            try:
                loginUser = User.objects.get(id=request.user.id)
            except:
                return sendErrorResponse(request, "kUserDoesNotExist")
            ### GET role
            try:
                roleObj = Role.objects.get(name=role)
            except:
                return sendErrorResponse(request, "kRoleDoesNotExist")
            ### Update user
            if fname and (fname != userObj.first_name):
                userObj.first_name = fname
            if lname and (lname != userObj.last_name):
                userObj.last_name = lname
            ### GET user profile
            try:
                userProfileObj = UserProfile.objects.get(user__id=userId)
            except:
                return sendErrorResponse(request, "kUserProfileDoesNotExist")
            isLogoUpdated = False
            if profilePicId and (
                    userProfileObj.profile_pic_doc is None or profilePicId != userProfileObj.profile_pic_doc.id):
                logUrl = None
                userDoc = None
                try:
                    userDoc = UserDocument.objects.get(id=profilePicId)
                    userProfileObj.picture = userDoc.url
                    userProfileObj.profile_pic_doc = userDoc
                    userDoc.belongs_to = userProfileObj.id
                    isLogoUpdated = True
                except:
                    return sendErrorResponse(request, "kFileDoesnotExist")
            ### Update User profile
            if phone and (phone != userProfileObj.phone):
                userProfileObj.phone = phone
            if city and (city != userProfileObj.city):
                userProfileObj.city = city
            if state and (state != userProfileObj.state):
                userProfileObj.state = state
            if district and (district != userProfileObj.district):
                userProfileObj.district = district
            if pincode and (pincode != userProfileObj.pincode):
                userProfileObj.pincode = pincode
            userProfileObj.role = ''
            userProfileObj.role.add(roleObj)
            userObj.save()
            userProfileObj.save()
            if isLogoUpdated:
                userProfileObj.profile_pic_doc.save()
            ### update user in digital center staff table if school id exists
            if digitalSchoolId:
                ### GET center
                centerObj = genUtility.getCenter(digitalSchoolId)
                ### GET school object
                try:
                    schoolObj = DigitalSchool.objects.get(id=digitalSchoolId)
                except:
                    return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")
                assign_user_school(digitalSchoolId, schoolObj, userObj, loginUser, roleObj, centerObj)

            dataObj = {
                "id": userObj.id,
                "message": "User updated successfully"
            }
            return getSuccessResponseStatus(request, dataObj)
        else:
            return sendErrorResponse(request, "kInvalidRequest")
    except Exception as e:
        return sendErrorResponse(request, "kInvalidRequest")


def assign_user_school(
        schoolId, schoolObj, userObj, loginUserObj, role, center=None):
    staffObj = ''
    staffID = ''
    if center:
        try:
            center.delivery_coordinator = userObj
            center.save()
        except:
            pass
    if role.name == "Partner Admin":
        try:
            roleObj = Role.objects.get(name="Digital School Manager")
            userProfileObj = UserProfile.objects.get(user=userObj)
            userProfileObj.role.add(roleObj)
            userProfileObj.pref_roles.add(roleObj)
            role = roleObj
        except:
            pass
    elif role.name != "Digital School Manager":
        try:
            role = Role.objects.get(name="Digital School Manager")
        except:
            return None

    try:
        staffObj = DigitalCenterStaff.objects.get(
            user=userObj, status='Active', digital_school=schoolObj)
    except:
        pass

    if schoolId and not staffObj:
        schoolStaffObj = DigitalCenterStaff.objects.filter(
            digital_school__id=schoolId, status='Active')

        if schoolStaffObj:
            for singleObj in schoolStaffObj:
                singleObj.status = 'Inactive'
                singleObj.save()
        digitalSchoolObj = DigitalCenterStaff.objects.create(
            user=userObj,
            digital_school=schoolObj,
            role=role,
            created_by=loginUserObj,
            center=center
        )
        digitalSchoolObj.save()

        staffID = digitalSchoolObj.id
    return staffID


@csrf_exempt
def assign_user_school_api(request):
    try:
        if request.method == "POST":
            if genUtility.checkUserAuthentication(request.user) is False:
                return genUtility.getForbiddenRequestErrorApiResponse(request)
            schoolId = request.GET.get("schoolId")
            userId = request.GET.get("userId")
            loginUserId = request.user.id
            ### check user ID
            if userId:
                try:
                    userObj = User.objects.get(id=userId)
                    UserProfileObj = UserProfile.objects.get(user__id=userId)
                    roles = UserProfileObj.role.all()
                except:
                    return sendErrorResponse(request, "kUserDoesNotExist")
            ### Check loginuser is exixts
            try:
                loginUserObj = User.objects.get(id=request.user.id)
            except:
                return sendErrorResponse(request, "kUserDoesNotExist")
            ### GET role
            if roles:
                try:
                    role = Role.objects.get(id=roles[0].id)
                except:
                    return sendErrorResponse(request, "kRoleDoesNotExist")
            ### GET center
            centerObj = genUtility.getCenter(schoolId)
            ### GET school object
            try:
                schoolObj = DigitalSchool.objects.get(id=schoolId)
            except:
                return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")
            assignId = assign_user_school(schoolId, schoolObj, userObj, loginUserObj, role, centerObj)
            dataObj = {
                "id": assignId,
                "message": "Digital school manager added"
            }
            return getSuccessResponseStatus(request, dataObj)

        else:
            return sendErrorResponse(request, "kInvalidRequest")
    except:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def partner_users_api(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == "GET":
        return partner_users_list(request)
    elif request.method == "POST":
        return add_users_api(request)


@login_required
def partner_digitalschools_list_approval(request):
    if request.method == "GET":
        if request.user.is_superuser:
            try:
                schoolList = DigitalSchool.objects.filter().prefetch_related('partner_owner', 'created_by')

            except DigitalSchool.DoesNotExist:
                schoolList = []
                print("Schools does not exist")
            except Exception as e:
                logService.logException("School approval page", e.message)

            # return render(request, 'list_partner_digital_schools_superuser.html',
            #  {'partner_schools': schoolList, "is_superuser": True})

            return render(request, 'list_partner_digital_schools_superuser.html',
                          {'partner_schools': schoolList, "is_partner": False,
                           "is_funding_partner": False, "is_school_admin": False, "isExternal": False})

        else:
            return HttpResponseRedirect('/myevidyaloka/')


    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def partner_digitalschools_detail_approval(request, schoolId):
    if request.method == "GET":
        if request.user.is_superuser:
            try:
                schoolData = DigitalSchool.objects.get(id=schoolId)

                centerAllocationText = "Allocated"
                centerData = {
                    'centerLocation' : '',
                    'programType'    : '',
                    'programCode'    : ''
                }
                center =  get_object_or_none(Center, digital_school_id = schoolId)
                if center:
                    if center.program_type == 1:
                        centerData['programType'] = 'Digital Classroom'
                        centerData['programCode'] = 1
                    elif center.program_type == 2:
                        centerData['programType'] = 'Digital School'
                        centerData['programCode'] = 2
                    elif center.program_type == 3:
                        centerData['programType'] = 'Sampoorna'
                        centerData['programCode'] = 3

                    lan = getLanguages()
                    courseProvider = None
                    if schoolData.course_provider:
                        courseProvider = schoolData.course_provider


                    isStatusPending = False
                    enableActivateButton = True
                    buttonText = "Deactivate"
                    buttonUrlPath = "deactivate"
                    if schoolData.status == "Pending":
                        isStatusPending = True
                        centerAllocationText = "Not Allocated"
                        enableActivateButton = False
                    elif schoolData.status == "Inactive":
                        buttonText = "Activate"
                        buttonUrlPath = "activate"

                    return render(request, 'view_partner_digitalschool.html',
                                  {'myschool': schoolData, 'myschoolstatus': schoolData.status,'courseProvider':courseProvider,
                                   'is_super': request.user.is_superuser, 'centerAllocationText': centerAllocationText,
                                   'error_msg': "error_msg",
                                   "is_partner": False, "school": 1,
                                   "buttonUrlPath": buttonUrlPath,
                                   "buttonText": buttonText, 'is_pam': False,
                                   'enableActivateButton': enableActivateButton,
                                   'is_status_pending': isStatusPending,
                                   "center":centerData,
                                   "language" : lan})
            except Exception as e:
                print("FT Exception", e); traceback.print_exc()
                logService.logException("school approval page", e.message)
                return HttpResponseNotFound('School does not exist')
        else:
            return HttpResponseRedirect('/myevidyaloka/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def digitalschools_approve_su_action(request, schoolId):
    if request.method == "GET":
        if request.user.is_superuser:
            try:
                schoolList = DigitalSchool.objects.filter(id=schoolId).prefetch_related('partner_owner')
                if schoolList is None or len(schoolList) <= 0:
                    return HttpResponseNotFound('School does not exist')
                else:
                    dsschool = schoolList[0]
                    partner = dsschool.partner_owner
                    courseProviderCode = None
                    langaugeName = None

                    if dsschool.course_provider is not None:
                        courseProviderCode = dsschool.course_provider.code
                        if dsschool.course_provider.language_code is not None:
                            langaugeName = dsschool.course_provider.language_code

                    # Allocate center
                    # Update School status
                    # update Center in Digital center staff if any
                    center = Center.objects.create(
                        name=dsschool.name,
                        state=dsschool.state,
                        district=dsschool.district,
                        village=dsschool.taluk,
                        admin=partner.contactperson,
                        description=dsschool.description,
                        digital_school=dsschool,
                        digital_school_partner=partner,
                        created_by=request.user,
                        modified_by=request.user,
                        status="Active",
                        board=courseProviderCode,
                        language=langaugeName,
                        program_type=2
                    )
                    dsschool.status = "Active"
                    dsschool.approved_on = genUtility.getCurrentTime()
                    dsschool.approved_by = request.user
                    dsschool.updated_on = genUtility.getCurrentTime()
                    center.save()
                    dsschool.save()

                    try:
                        upData = DigitalCenterStaff.objects.filter(digital_school=dsschool).update(center=center)
                        roleObj = Role.objects.get(name="Digital School Manager")
                        dsmObjects = DigitalCenterStaff.objects.filter(digital_school=dsschool,role=roleObj,status="Active")
                        if dsmObjects and len(dsmObjects) > 0:
                            activeDSM = dsmObjects[0]
                            dsmUser = activeDSM.user
                            center.delivery_coordinator = dsmUser
                            center.save()

                        if partner and partner.contactperson:
                            authUserObj = partner.contactperson
                            pTokens = notificationModule.sendSchoolApprovalNotification(authUserObj,partner,dsschool)



                    except Exception as ec:
                        logService.logException("Center update in staff", ec.message)

                    return HttpResponseRedirect('/partner/digitalschool/' + str(dsschool.id))

            except DigitalSchool.DoesNotExist:
                return HttpResponseNotFound('School does not exist')

            except Exception as e:
                logService.logException("school approval page", e.message)
                return HttpResponseNotFound('School does not exist')
        else:
            return HttpResponseRedirect('/myevidyaloka/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def activateDigitalSchoolForSuperUser(request, schoolId, activate):
    if request.method == "GET":
        if request.user.is_superuser:
            try:
                dsschool = get_object_or_none(DigitalSchool, id=schoolId)
                if dsschool is None:
                    return HttpResponseNotFound('School does not exist')
                else:
                    if activate is True:
                        dsschool.status = "Active"
                    else:
                        dsschool.status = "Inactive"
                    dsschool.updated_on = genUtility.getCurrentTime()
                    dsschool.updated_by = request.user
                    dsschool.save()

                    centers = Center.objects.filter(digital_school=schoolId)
                    for center in centers:
                        center.status = dsschool.status
                        center.save()

                    return HttpResponseRedirect('/partner/digitalschool/' + str(dsschool.id))

            except DigitalSchool.DoesNotExist:
                return HttpResponseNotFound('School does not exist')

            except Exception as e:
                logService.logException("school approval page", e.message)
                return HttpResponseNotFound('School does not exist')
        else:
            return HttpResponseRedirect('/myevidyaloka/')
    else:
        return HttpResponseRedirect('/myevidyaloka/')


@login_required
def digitalschools_deactivate_su_action(request, schoolId):
    return activateDigitalSchoolForSuperUser(request, schoolId, False)


@login_required
def digitalschools_activate_su_action(request, schoolId):
    return activateDigitalSchoolForSuperUser(request, schoolId, True)

@csrf_exempt
def states_api(request):
    try:
        if genUtility.checkUserAuthentication(request.user) is False or request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        dataObj = {
            "states": []
        }

        statesObjests = State.objects.filter(status=1).order_by('name')

        for singleState in statesObjests:
            sampleData = {}
            sampleData["id"] = singleState.id
            sampleData["name"] = singleState.name
            sampleData["code"] = singleState.code

            dataObj["states"].append(sampleData)

        return getSuccessResponseStatus(request, dataObj)
    except:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def dsm_enroll_student(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == "POST":
        # Check if user id is DSM of the school id and school status is active
        requestBodyParams = simplejson.loads(request.body)
        partnerId = requestBodyParams.get("partnerId")
        schoolId = requestBodyParams.get("digitalSchoolId")
        user = request.user

        if partnerId and schoolId:
            try:
                dsSchool = DigitalSchool.objects.get(id=schoolId, partner_owner_id=partnerId)
                if dsSchool.status == "Active":
                    role = Role.objects.get(name="Digital School Manager")
                    staff = DigitalCenterStaff.objects.get(user=user, role=role, digital_school=dsSchool,
                                                           status="Active")
                    if staff:
                        return studentApp.enrolStudentInDigitalSchool(request, requestBodyParams, dsSchool, staff, partnerId,"partner",None)
                else:
                    return sendErrorResponse(request, "kInvalidSchoolStatus")
            except Exception as e:
                logService.logException("DSM enroll student", e.message)
                return sendErrorResponse(request, "kInvalidParterDSMCon")

        else:
            return sendErrorResponse(request, "kMissingReqFields")
    else:
        return genUtility.getForbiddenRequestErrorApiResponse(request)


@csrf_exempt
def partner_students_list_api(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == "GET":
        return studentApp.getStudentListForPartner(request)
    else:
        return genUtility.getForbiddenRequestErrorApiResponse(request)


@csrf_exempt
def partner_students_detail_api(request, studentId):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == "GET":
        return studentApp.getStudentDetailForPartner(request, studentId)
    elif request.method == "PUT":
        return dsm_edit_student(request, studentId)
    else:
        return genUtility.getForbiddenRequestErrorApiResponse(request)


@csrf_exempt
def dsm_edit_student(request, studentId):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == "PUT":
        # Check if user id is DSM of the school id and school status is active
        requestBodyParams = simplejson.loads(request.body)
        partnerId = requestBodyParams.get("partnerId")
        schoolId = requestBodyParams.get("digitalSchoolId")
        user = request.user

        if partnerId and schoolId and studentId:
            try:
                dsSchool = DigitalSchool.objects.get(id=schoolId, partner_owner_id=partnerId)
                if dsSchool.status == "Active":
                    role = Role.objects.get(name="Digital School Manager")
                    staff = DigitalCenterStaff.objects.get(user=user, role=role, digital_school=dsSchool,
                                                           status="Active")
                    if staff:
                        return studentApp.editStudentEnrollmentForPartner(request, requestBodyParams, dsSchool, staff,
                                                                          partnerId, studentId)
                else:
                    return sendErrorResponse(request, "kInvalidSchoolStatus")
            except Exception as e:
                logService.logException("DSM edit student", e.message)
                return sendErrorResponse(request, "kInvalidParterDSMCon")

        else:
            return sendErrorResponse(request, "kMissingReqFields")
    else:
        return genUtility.getForbiddenRequestErrorApiResponse(request)


@csrf_exempt
def partner_language_api(request):
    if genUtility.checkUserAuthentication(request.user) is False or request.method != "GET":
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    languages = []
    try:
        languages = genUtility.getLanguages()
        languageRespList = []
        for i in range(len(languages)):
            lngObj = languages[i]
            languageRespList.append({'id': lngObj.id, 'name': lngObj.name, 'code': lngObj.code})

        dataObj = {
            "languages": languageRespList
        }
        return getSuccessResponseStatus(request, dataObj)
    except Exception as e:
        logService.logException("Language api", e.message)
        return sendErrorResponse(request, "kInvalidRequest")


def getSettingsForPartner():
    keyNames = ["supportedGrades", "allowedChapterForNewUser"]
    jsonKeys = ["supportedGrades", "allowedChapterForNewUser"]
    return genUtility.getSettingsForUserType("partner",keyNames,jsonKeys)

@csrf_exempt
def ping_api(request):
    if genUtility.checkUserAuthentication(request.user) is False or request.method != "POST":
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:
        sessionObj = request.currentSession
        sessionId = sessionObj.session_key

        if sessionId:
            requestBodyParams = simplejson.loads(request.body)
            partnerId = requestBodyParams.get("partnerId")
            if not partnerId:
                return sendErrorResponse(request, "kInvalidRequest")
            ### get Partner obj
            try:
                partnerObj = Partner.objects.get(id=partnerId)
            except:
                return sendErrorResponse(request, "kPartnerDoesNotExist")
            # get userprofile obj
            try:
                userProfileObj = UserProfile.objects.get(user=request.user)
            except:
                return sendErrorResponse(request, "kUserProfileDoesNotExist")

            settingObj = getSettingsForPartner()
            dataObj = {
                'sessionId': sessionId,
                'partnerId': partnerObj.id,
                'partnerStatus': partnerObj.status,
                'userId': request.user.id,
                'useruserStatus': userProfileObj.status,
                'settings': settingObj,
                'sessionExpiryTime': genUtility.getTimeStampFromDate(sessionObj.expiry_time)
            }
            return getSuccessResponseStatus(request, dataObj)
        else:
            return sendErrorResponse(request, "kSessionExpired")
    except Exception as e:
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def logout_api(request):
    if genUtility.checkUserAuthentication(request.user) is False or request.method != "POST":
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:
        sessionObj = request.currentSession
        sessionId = sessionObj.session_key
        if sessionId:
            try:
                sessionInstance = ApiSession.objects.get(session_key=sessionId)
            except:
                return sendErrorResponse(request, "kSessionExpired")
            sessionInstance.status = False
            sessionInstance.expiry_time = genUtility.getCurrentTime()
            sessionInstance.save()
            dataObj = {
                "UserId": request.user.id,
                "message": "Logged out successfully"
            }
            return getSuccessResponseStatus(request, dataObj)
        else:
            return sendErrorResponse(request, "kSessionExpired")
    except:
        return sendErrorResponse(request, "kInvalidRequest")



@csrf_exempt
def pincodes_api(request):
    try:
        if genUtility.checkUserAuthentication(request.user) is False or request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        stateId = request.GET.get("stateId")
        searchText = request.GET.get("searchText")
        page = request.GET.get("page")
        count = request.GET.get("count")

        if not stateId or not page or not count:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(stateId) or not genUtility.isint(page) or not genUtility.isint(count):
            return sendErrorResponse(request, "kInvalidRequest")
        else:
            page = int(page)
            count = int(count)

        if searchText and genUtility.checkIfKeyIsSafeForQuery(searchText) is False:
            return sendErrorResponse(request, "kInvalidSearchKey")

        if count > 50:
            count = 50

        if page < 0:
            page = 0

        page = page * count

        try:
            stateObj = State.objects.get(id=stateId)

        except:
            return sendErrorResponse(request, "kInvalidState")

        pincodeArr = genUtility.getPincodes(stateObj.id, searchText, page, count, connection)
        dataObj = {
            "pincodes": pincodeArr
        }

        return getSuccessResponseStatus(request, dataObj)
    except Exception as e:
        print("pincodes_api error",e)
        #traceback.print_exc()
        logService.logException('pincodes_api', e.message)
        return sendErrorResponse(request, "kInvalidRequest")

def isUserAuthorisedWithSchool(userType,schoolId,userReq,partnerId):
    partner = None
    try:
        partner = Partner.objects.get(contactperson=userReq, id=partnerId)
    except Partner.DoesNotExist:
        pass
    except Partner.MultipleObjectsReturned:
        partner =  partner[0]
    return partner

@csrf_exempt
def schoollocation_add_api(request):
    try:
        if genUtility.checkUserAuthentication(request.user) is False or request.method != 'POST':
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        userReq = request.user
        requestBodyParams = simplejson.loads(request.body)
        partnerId = getValueElseThrowException(requestBodyParams, 'partnerId')
        schoolId = getValueElseThrowException(requestBodyParams, 'schoolId')
        selectedStates = requestBodyParams.get('selectedStates')
        userType = getValueElseThrowException(requestBodyParams, 'userType')

        if not partnerId or not schoolId or not genUtility.isint(partnerId) or not genUtility.isint(schoolId):
            return sendErrorResponse(request, "kMissingReqFields")

        # Check if user has permission to create school and partner is of type DS
        partner = isUserAuthorisedWithSchool(userType,schoolId,userReq,partnerId)
        if partner is None:
            return sendErrorResponse(request, "kInvalidRequest")

        #check if school exist
        dschool = None
        try:
            dschool = DigitalSchool.objects.get(id=schoolId, partner_owner=partner)
        except:
            return sendErrorResponse(request, "kInvalidRequest")

        if selectedStates and len(selectedStates) > 0:
            createStatesAndPincodes(selectedStates, dschool)

        dataObj = {
            "id": dschool.id,
            "message": "Locatipn preference updated successfully"
        }
        return getSuccessResponseStatus(request, dataObj)

    except Exception as e:
        print("schoollocation_add_api error", e)
        # traceback.print_exc()
        logService.logException('schoollocation_add_api', e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def schoollocation_delete_api(request):
    try:
        if genUtility.checkUserAuthentication(request.user) is False or request.method != 'POST':
            return genUtility.getForbiddenRequestErrorApiResponse(request)
        userReq = request.user
        requestBodyParams = simplejson.loads(request.body)
        partnerId = getValueElseThrowException(requestBodyParams, 'partnerId')
        schoolId = getValueElseThrowException(requestBodyParams, 'schoolId')
        deletedStateIds = requestBodyParams.get('deletedStateIds')
        deletedPincodeIds = requestBodyParams.get('deletedPincodeIds')
        userType = getValueElseThrowException(requestBodyParams, 'userType')

        if not partnerId or not schoolId or not genUtility.isint(partnerId) or not genUtility.isint(schoolId):
            return sendErrorResponse(request, "kMissingReqFields")

        newStateIds = []
        if deletedStateIds and len(deletedStateIds) > 0:
            # delete all ids here
            newStateIds = genUtility.convertUnicodeIntegerArrayToIntegerArray(deletedStateIds)
            if newStateIds is None:
                return sendErrorResponse(request, "kInvalidRequest")

        newpincodeids = []
        if deletedPincodeIds and len(deletedPincodeIds) > 0:
            # delete all ids here
            newpincodeids = genUtility.convertUnicodeIntegerArrayToIntegerArray(deletedPincodeIds)
            if newpincodeids is None:
                return sendErrorResponse(request, "kInvalidRequest")

        # Check if user has permission to create school and partner is of type DS
        partner = isUserAuthorisedWithSchool(userType, schoolId, userReq, partnerId)
        if partner is None:
            return sendErrorResponse(request, "kInvalidRequest")

        # check if school exist
        dschool = None
        try:
            dschool = DigitalSchool.objects.get(id=schoolId, partner_owner=partner)
        except:
            return sendErrorResponse(request, "kInvalidRequest")

        deleteStatesAndPincodes(newStateIds, dschool, newpincodeids)

        dataObj = {
            "id": dschool.id,
            "message": "location preference updated successfully"
        }
        return getSuccessResponseStatus(request, dataObj)

    except Exception as e:
        print("schoollocation_delete_api error", e)
        # traceback.print_exc()
        logService.logException('schoollocation_delete_api', e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def partner_explore_School_detail(request):
    try:
        if genUtility.checkUserAuthentication(request.user) is False or request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        courseProviderId = request.GET.get("courseProviderId")
        grade = request.GET.get("grade")

        if not userId or not courseProviderId or not grade:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(courseProviderId) or not genUtility.isint(grade):
            return sendErrorResponse(request, "kInvalidRequest")

        schoolDetail = studentApp.getDefaultSchoolDetailForboard(courseProviderId, grade)
        if schoolDetail is None:
            return sendErrorResponse(request, "kDigitalSchoolDoesNotExist")

        dataObj = {
            "schools": [schoolDetail]
        }
        return getSuccessResponseStatus(request, dataObj)
    except Exception as e:
        print("partner_explore_School_detail error", e)
        # traceback.print_exc()
        logService.logException('partner_explore_School_detail', e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def partner_subject_detail(request):
    try:
        if genUtility.checkUserAuthentication(request.user) is False or request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        offeringId = request.GET.get("offeringId")
        courseId = request.GET.get("courseId")

        if not userId or not userType or not offeringId or not courseId:
            return sendErrorResponse(request, "kMissingReqFields")


        if not genUtility.isint(userId) or not genUtility.isint(offeringId) or not genUtility.isint(courseId):
            return sendErrorResponse(request, "kInvalidRequest")

        allObjects = studentApp.getTopicAndSubtopicForCourse(offeringId, courseId, None)
        dataObj = {
            "topics": allObjects
        }
        return getSuccessResponseStatus(request, dataObj)
    except Exception as e:
        print("partner_subject_detail error", e)
        # traceback.print_exc()
        logService.logException('partner_subject_detail', e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def partner_content_detail(request):
    try:
        if genUtility.checkUserAuthentication(request.user) is False or request.method != "GET":
            return genUtility.getForbiddenRequestErrorApiResponse(request)

        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        offeringId = request.GET.get("offeringId")
        topicId = request.GET.get("topicId")
        subtopicId = request.GET.get("subtopicId")

        if not userId or not userType  or not offeringId or not topicId  or not subtopicId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(offeringId) or not genUtility.isint(topicId) or not genUtility.isint(subtopicId):
            return sendErrorResponse(request, "kInvalidRequest")

        # Get offeringObj obj
        try:
            offeringObj = Offering.objects.get(id=offeringId)
        except:
            return sendErrorResponse(request, "kInvalidOfferings")

        # Check if this topic and sub topic allowed.
        isAllowed = studentApp.checkIfTopicAndSubtopicAllowedForNewUser(topicId, subtopicId, offeringObj, "partner")
        if isAllowed is False:
            return sendErrorResponse(request, "kAccessDenied")

        hardCodedResponse = studentApp.getContentForSubtopicId(None, subtopicId, topicId)
        dataObj = {
            "contentDetail": hardCodedResponse
        }
        return getSuccessResponseStatus(request, dataObj)
    except Exception as e:
        print("partner_content_detail error", e)
        # traceback.print_exc()
        logService.logException('partner_content_detail', e.message)
        return sendErrorResponse(request, "kInvalidRequest")


def validatePartnerResgistrationParams(requestBodyParams):
    name = requestBodyParams.get('name')
    name_of_organization = requestBodyParams.get('orgName')
    email = requestBodyParams.get('email')
    mobile = requestBodyParams.get('mobile')

    if name and name_of_organization and email and mobile:
        pass
    else:
        return "kMissingReqFields"

    if genUtility.isValidEmailAddress(email) is False:
        return "kInvalidEmailId"

    if genUtility.isValidMobileNumber(mobile) is False:
        return "kInvalidMobileNum"

    try:
        existing_user = User.objects.get(username=email)
        return "kEmailExist"
    except User.DoesNotExist:
        pass
    except User.MultipleObjectsReturned:
        return "kEmailExist"
    except:
        return "kEmailExist"

    try:
        userp = UserProfile.objects.get(phone=mobile)
        return "kMobileExist"
    except UserProfile.DoesNotExist:
        pass
    except UserProfile.MultipleObjectsReturned:
        return "kMobileExist"
    except:
        return "kMobileExist"

    try:
        query = Q(phone=mobile) | Q(name_of_organization=name_of_organization)
        partnerList = Partner.objects.filter(query)
        for eachP in partnerList:
            if eachP.name_of_organization == name_of_organization:
                return "kOrgNameExist"
            elif eachP.phone == mobile:
                return "kMobileExist"
    except:
        return "kUserExistSameOrg"

    return None

@csrf_exempt
def partner_send_otp_api(request):
    if genUtility.is_basic_auth_authenticated(request) is False or request.method != 'POST':
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:
        requestBodyParams = simplejson.loads(request.body)
        if isObjectNotEmpty(requestBodyParams):

            name = requestBodyParams.get('name')
            name_of_organization = requestBodyParams.get('orgName')
            email = requestBodyParams.get('email')
            mobile = requestBodyParams.get('mobile')

            errorString = validatePartnerResgistrationParams(requestBodyParams)
            if errorString:
                return sendErrorResponse(request, errorString)

            #Send OTP
            otpExpiryTime = genUtility.getSystemSettingValue("otpExpiryTime")
            maxOTPPerHour = genUtility.getSystemSettingValue("maxOTPPerHour")
            maxOTPPerHour = int(maxOTPPerHour)

            responseData = {
                "message": "OTP has been sent successfully"
            }
            if genUtility.isDevEnvironment() is False:
                curDate = genUtility.getTimeBeforeXhours(1)
                otpObjs = UserOtp.objects.filter(mobile=mobile, created_on__gte=curDate)
                if otpObjs and (len(otpObjs) >= maxOTPPerHour):
                    return sendErrorResponse(request, "kMaxOTPExceed")

                sentOTP = genUtility.sendOTPToMobileNumber(mobile, otpExpiryTime)
                mobile, sentOTP = str(mobile), str(sentOTP)
                if sentOTP:
                    otpExpTime = genUtility.getTimeAfterXMinutesToDate(genUtility.getCurrentTime(), int(otpExpiryTime))
                    otpObj = UserOtp.objects.create(mobile=mobile, otp=sentOTP, type='guardian', expiry_time=otpExpTime)
                    otpObj.save()
                    return getSuccessResponseStatus(request, responseData)
                else:
                    return sendErrorResponse(request, "kOtpNotSent")
            else:
                return getSuccessResponseStatus(request, responseData)
    except Exception as e:
        print("partner_send_otp_api error", e)
        # traceback.print_exc()
        logService.logException('partner_send_otp_api', e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def partner_verify_otp_registration_api(request):
    if genUtility.is_basic_auth_authenticated(request) is False or request.method != 'POST':
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    try:
        requestBodyParams = simplejson.loads(request.body)
        if isObjectNotEmpty(requestBodyParams):

            name = requestBodyParams.get('name')
            orgName = requestBodyParams.get('orgName')
            email = requestBodyParams.get('email')
            mobile = requestBodyParams.get('mobile')
            otp = requestBodyParams.get('otp')

            if not otp:
                return sendErrorResponse(request, "kMissingReqFields")

            errorString = validatePartnerResgistrationParams(requestBodyParams)
            if errorString:
                return sendErrorResponse(request, errorString)

            mobileStr = str(mobile)
            isDevEnvironment = genUtility.isDevEnvironment()
            isOtpEnabled = genUtility.isOTPEnabled()

            otpObj = genUtility.getUserOTPObject(mobileStr, otp)
            if isOtpEnabled is True:
                if otpObj is None or otpObj.status is False:
                    return sendErrorResponse(request, "kInvalidOtp")

            # Verify OTP
            verificationStatus = genUtility.verifyOTPWithServiceProvider(mobile, otp)
            if verificationStatus == "success":
                orgDetails = { "name": orgName,"partnerName":orgName,"email":email,"phone":mobile}
                contactDetails = {"fname": name, "lname": " ", "email": email, "phone": mobile}
                status = 'Lead'
                partner_model,userObj = registerAndSetupPartner(orgDetails, contactDetails,status)
                if partner_model:
                    if otpObj:
                        otpObj.status = False
                        otpObj.save()

                    sessionObj = genUtility.createSessionForUser(userObj)
                    session_key = sessionObj.session_key
                    expiryTimeStamp = genUtility.getTimeStampFromDate(sessionObj.expiry_time)
                    responseData = {
                        "userId": userObj.id,
                        "email": userObj.email,
                        "fname": userObj.first_name,
                        "lname": userObj.last_name,
                        "roles": ["DSP"],
                        "sessionId": session_key,
                        "sessionExpiryTime": str(expiryTimeStamp),
                        "partnerId": partner_model.id,
                        "partnerStatus": partner_model.status,
                        "userStatus": 'New'
                    }
                    return getSuccessResponseStatus(request, responseData)
                else:
                    return sendErrorResponse(request, "kParterRegistrationFailed")

            elif verificationStatus == "expired":
                return sendErrorResponse(request, "kOtpExpired")
            else:
                return sendErrorResponse(request, "kInvalidOtp")

    except Exception as e:
        print("partner_verify_otp_registration_api error", e)
        # traceback.print_exc()
        logService.logException('partner_verify_otp_registration_api', e.message)
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def partner_details_update_api(request):
    if genUtility.checkUserAuthentication(request.user) is False or request.method != "POST":
        return genUtility.getForbiddenRequestErrorApiResponse(request)

    try:
        requestBodyParams = simplejson.loads(request.body)
        partnerId = requestBodyParams.get('partnerId')
        partnerObj = None
        if not partnerId:
            return sendErrorResponse(request, "kMissingReqFields")
        try:
            partnerObj = Partner.objects.get(id=partnerId)
        except:
            return sendErrorResponse(request, "kPartnerDoesNotExist")

        if request.user.id !=  partnerObj.contactperson_id or partnerObj.status != 'Lead':
            return sendErrorResponse(request, "kUnauthorisedAction")

        organisationObj = requestBodyParams.get('organization')
        if isObjectNotEmpty(organisationObj):

            name = organisationObj.get('partnerName')
            name_of_organization = organisationObj.get('name')
            email = organisationObj.get('email')
            phone = organisationObj.get('phone')
            orgAddress = organisationObj.get('address')

            if name and name_of_organization and email and phone and orgAddress:
                pass
            else:
                return sendErrorResponse(request, "kMissingReqFields")

            if genUtility.isValidEmailAddress(email) is False:
                return sendErrorResponse(request, "korgInvalidEmail")


            contactObj = requestBodyParams.get('contact')
            if isObjectNotEmpty(contactObj):
                poc_fname = getValueElseThrowException(contactObj, 'fname')
                poc_lname = getValueElseThrowException(contactObj, 'lname')

                if poc_fname and poc_lname:
                    pass
                else:
                    return sendErrorResponse(request, "kMissingReqFields")

                try:
                    query = Q(phone=phone) | Q(name_of_organization=name_of_organization) | Q(email=email)
                    partnerList = Partner.objects.filter(query & ~Q(id=partnerObj.id))
                    if len(partnerList) > 0:
                        for eachp in partnerList:
                            if eachp.email == email:
                                return sendErrorResponse(request, "kEmailExist")
                            elif eachp.phone == phone:
                                return sendErrorResponse(request, "kMobileExist")
                            elif eachp.name_of_organization == name_of_organization:
                                return sendErrorResponse(request, "kOrganisationExist")
                except Exception as e:
                    logService.logException('partner_details_update_api duplicate', e.message)
                    return sendErrorResponse(request, "kOrganisationExist")

                partnerObj.status = 'New'
                partnerObj.name = name
                partnerObj.name_of_organization = name_of_organization
                partnerObj.phone = phone
                partnerObj.email = email
                partnerObj.address = orgAddress
                partnerObj.save()

                contactUser = partnerObj.contactperson
                contactUser.first_name = poc_fname
                contactUser.last_name = poc_lname
                contactUser.save()

                responseData = {
                    "id": partnerId,
                    "message":"partner details updated successfully",
                    "status":partnerObj.status
                }
                return getSuccessResponseStatus(request, responseData)

            else:
                return sendErrorResponse(request, "kMissingReqFields")
        else:
            return sendErrorResponse(request, "kMissingReqFields")

    except Exception as e:
        print("partner_details_update_api error", e)
        # traceback.print_exc()
        logService.logException('partner_details_update_api', e.message)
        return sendErrorResponse(request, "kInvalidRequest")

@csrf_exempt
def partner_get_grade(request):
    if genUtility.checkUserAuthentication(request.user) is False or request.method != "GET":
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

        offeringObjs = studentApp.getOfferingForCourseProvider(courseProvider)
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
        print("partner_get_grade error message",e)
        logService.logExceptionWithExceptionobject("partner_get_grade ", e)
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def partner_check_offering_exist_forcourse(request):
    if genUtility.checkUserAuthentication(request.user) is False or request.method != "GET":
        return genUtility.getForbiddenRequestErrorApiResponse(request)

    try:

        userId = request.GET.get("userId")
        userType = request.GET.get("userType")
        courseId = request.GET.get("courseId")
        schoolId = request.GET.get("schoolId")

        if not userId or not courseId or not schoolId:
            return sendErrorResponse(request, "kMissingReqFields")

        if not genUtility.isint(userId) or not genUtility.isint(schoolId) or not genUtility.isint(courseId):
            return sendErrorResponse(request, "kInvalidRequest")

        try:
            course = Course.objects.get(id=courseId,status='active')
        except:
            return sendErrorResponse(request, "kCourseDoesNotExist")

        center = genUtility.getCenter(schoolId)

        offeringObjs = Offering.objects.filter(center=center, end_date__gte=genUtility.getCurrentTime(),status__in=['pending', 'running'],course=course)
        isOfferingExist = 0
        if offeringObjs and len(offeringObjs) > 0:
            isOfferingExist = 1


        dataObj = {
            "isSimilarOfferingExist": isOfferingExist
        }
        return genUtility.getSuccessApiResponse(request, dataObj)
    except Exception as e:
        print("partner_get_grade",e)
        logService.logExceptionWithExceptionobject("partner_check_offering_exist_forcourse ", e)
        return sendErrorResponse(request, "kInvalidRequest")


def updateOrCreateDeviceObjectForSystemUser(user,deviceInfo):
    try:
        deviceId = deviceInfo["deviceId"]
        if deviceId is None:
            return None
        osType = deviceInfo["osType"]
        userDevices = UserDevice.objects.filter(deviceId=deviceId,status=True,user_type='authuser',device_type='mobile')
        if userDevices and len(userDevices) > 0:
            devcieObj = userDevices[0]
            if devcieObj.belongs_to_id != user.id:
                devcieObj.belongs_to_id = user.id
                devcieObj.save()
            return devcieObj
        else:
            devcieObj = UserDevice.objects.create(
                deviceId=deviceId,
                belongs_to_id = user.id,
                created_by_id = settings.SYSTEM_USER_ID_AUTH,
                updated_by_id=settings.SYSTEM_USER_ID_AUTH,
                user_type='authuser'
            )
            devcieObj.save()
            return  devcieObj
    except Exception as e:
        print("updateOrCreateDeviceObjectForSystemUser", e)
        logService.logException("updateOrCreateDeviceObjectForSystemUser ", e.message)
        return None

@csrf_exempt
def partner_update_token_api(request):
    if genUtility.checkUserAuthentication(request.user) is False or request.method != "POST":
        return genUtility.getForbiddenRequestErrorApiResponse(request)

    try:
        requestBodyParams = simplejson.loads(request.body)
        partnerId = requestBodyParams.get('partnerId')
        partnerObj = None
        if not partnerId:
            return sendErrorResponse(request, "kMissingReqFields")
        try:
            partnerObj = Partner.objects.get(id=partnerId)
        except:
            return sendErrorResponse(request, "kPartnerDoesNotExist")

        userId = requestBodyParams.get("userId")
        pushToken = requestBodyParams.get("pushToken")
        deviceInfo = requestBodyParams.get("deviceInfo")
        userObj = request.user

        if not userId or not pushToken or not deviceInfo:
            return sendErrorResponse(request, "kMissingReqFields")

        # Check if device exist, if not, create device
        # update push notification for the user and device
        deviceObj = updateOrCreateDeviceObjectForSystemUser(userObj, deviceInfo)
        if deviceObj is None:
            return sendErrorResponse(request, "kMissingReqFields")

        notificationModule.updatePushTokeForAuthUser(userObj, pushToken, deviceObj)
        dataObj = {
            "message": "Token updated successfully"
        }
        return genUtility.getSuccessApiResponse(request, dataObj)

    except Exception as e:
        print("partner_update_token error", e)
        # traceback.print_exc()
        logService.logException('partner_update_token', e.message)
        return sendErrorResponse(request, "kInvalidRequest")


@csrf_exempt
def dsm_promot_student(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)
    if request.method == "POST":
        try:
            # Check if user id is DSM of the school id and school status is active
            requestBodyParams = simplejson.loads(request.body)
            partnerId = requestBodyParams.get("partnerId")
            digitalSchoolId = requestBodyParams.get("digitalSchoolId")
            userType = requestBodyParams.get('userType')
            ayfyId = requestBodyParams.get("ayfyId")
            user = request.user
            if not partnerId or not digitalSchoolId or not digitalSchoolId or not userType or not ayfyId is None:
                return sendErrorResponse(request, "kMissingReqFields")

            staff = studentApp.isUserDSMOfSchool(digitalSchoolId, user)
            if userType != "DSM" or staff is None or staff.status != "Active":
                return sendErrorResponse(request, "kInvalidUserType")

            dsSchool = DigitalSchool.objects.get(id=digitalSchoolId, partner_owner_id=partnerId)
            if dsSchool.status == "Active":
                return studentApp.promotStudentForPartner(request, requestBodyParams)
            else:
                return sendErrorResponse(request, "kInvalidSchoolStatus")
        except Exception as e:
            logService.logException("DSM promot student", e.message)
            return sendErrorResponse(request, "kInvalidParterDSMCon")
    else:
        return genUtility.getForbiddenRequestErrorApiResponse(request)


@csrf_exempt
def dsm_promot_student_list(request):
    if genUtility.checkUserAuthentication(request.user) is False:
        return genUtility.getForbiddenRequestErrorApiResponse(request)

    if request.method == "GET":
        digitalSchoolId = request.GET.get('digitalSchoolId')
        userType = request.GET.get('userType')
        user = request.user
        if userType != "DSM":
            return sendErrorResponse(request, "kInvalidUserType")
        else:
            staff = studentApp.isUserDSMOfSchool(digitalSchoolId, user)
            if staff is None:
                return sendErrorResponse(request, "kInvalidUserType")
        return studentApp.getStudentPromotionListForPartner(request)
    else:
        return genUtility.getForbiddenRequestErrorApiResponse(request)

class QuizPlayer(View):
    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        try:
            centerId = self.request.GET.get('center_id',None)
            offeringId = self.request.GET.get('offering_id',None)
            topicId = self.request.GET.get('topic_id',None)
            studentId = self.request.GET.get('student_id',None)
            ayfyID = self.request.GET.get('ayfy_id',None)



            attempt = 0 # for storing quiz attempt of student
            at = Quiz_History.objects.filter(student_id=studentId).aggregate(Max('attempt'))

            if at['attempt__max'] != None:
                attempt = at['attempt__max'] + 1
            else:
                attempt = 1

            print('attempt', attempt)

            try:
                studentObj = Student.objects.get(id=studentId)
            except:
                return HttpResponseNotFound("Student Not found")

            try:
                offeringObj = Offering.objects.get(id=offeringId)
                courseObj = offeringObj.course
            except:
                return HttpResponseNotFound("Offering Not found")

            data = {"questionSet":{
                "questions":[]
            }}
            data['studentId'] = studentId
            data['offeringId'] = offeringId
            data['attempt'] = attempt

            studData = {
                'studentId'     : studentId,
                'studentName'   : studentObj.name,
                'subject'       : courseObj.subject,
                'grade'         : courseObj.grade,
                'centerId'      : centerId,
                'offeringId'    : offeringId,
                'ayfyID'        : ayfyID,
            }

            try:
                questionSet = Question_Set.objects.filter(topic_id__in=[topicId])    # query to get questionSet from topic id
            except:
                return HttpResponseNotFound("Questions Not found")
                
            questionSetId = questionSet[0].id   # getting id of questionSet
            data['questionSet']['id'] = questionSetId     # adding questionSetId to data, key('id'): value(question_Set id)
            allQuestions = Question.objects.filter(questionset_id__in=[questionSetId])  # Getting all question which match with QuestionSetId
            

            questionByType = defaultdict(list)
            questionByType = {'easy':{'mcq':[],'mmcq':[],'orderBy':[],'categorise':[],'matchTheFollowing':[]},'medium':{'mcq':[],'mmcq':[],'orderBy':[],'categorise':[],'matchTheFollowing':[]},'hard':{'mcq':[],'mmcq':[],'orderBy':[],'categorise':[],'matchTheFollowing':[]}}
            for q in allQuestions:
                if q.complexity == 1:
                    if q.type_code == 'mcq':
                        questionByType['easy']['mcq'].append(q)
                    elif q.type_code == 'mmcq':
                        questionByType['easy']['mmcq'].append(q)
                    elif q.type_code == 'orderBy':
                        questionByType['easy']['orderBy'].append(q)
                    elif q.type_code == 'categorise':
                        questionByType['easy']['categorise'].append(q)
                    elif q.type_code == 'matchTheFollowing': 
                        questionByType['easy']['matchTheFollowing'].append(q)

                elif q.complexity == 2:
                    if q.type_code == 'mcq':
                        questionByType['medium']['mcq'].append(q)
                    elif q.type_code == 'mmcq':
                        questionByType['medium']['mmcq'].append(q)
                    elif q.type_code == 'orderBy':
                        questionByType['medium']['orderBy'].append(q)
                    elif q.type_code == 'categorise':
                        questionByType['medium']['categorise'].append(q)
                    elif q.type_code == 'matchTheFollowing':
                        questionByType['medium']['matchTheFollowing'].append(q)

                elif q.complexity == 3:
                    if q.type_code == 'mcq':
                        questionByType['hard']['mcq'].append(q)
                    elif q.type_code == 'mmcq':
                        questionByType['hard']['mmcq'].append(q)
                    elif q.type_code == 'orderBy':
                        questionByType['hard']['orderBy'].append(q)
                    elif q.type_code == 'categorise':
                        questionByType['hard']['categorise'].append(q)
                    elif q.type_code == 'matchTheFollowing':
                        questionByType['hard']['matchTheFollowing'].append(q)
            

            easy = []
            medium = []
            hard = []
            # function to pick random question and no of specific question accoring to type

            for qType in questionByType['easy']: # function to pick random medium question 
                if qType == 'mcq':
                    if len(questionByType['easy'][qType]) == 1:
                        easy.append(random.sample(questionByType['easy'][qType],1))
                    elif len(questionByType['easy'][qType]) > 1:
                        easy.append(random.sample(questionByType['easy'][qType],2))
                elif qType == 'mmcq':
                    if len(questionByType['easy'][qType]) == 1:
                        easy.append(random.sample(questionByType['easy'][qType],1))
                    elif len(questionByType['easy'][qType]) > 1:
                        easy.append(random.sample(questionByType['easy'][qType],2))

            
            for qType in questionByType['medium']: # function to pick random easy question 
                if qType == 'mcq':
                    if len(questionByType['medium'][qType]) >= 1:
                        medium.append(random.sample(questionByType['medium'][qType],1))           
                elif qType == 'categorise':
                    if len(questionByType['medium'][qType]) >= 1:
                        medium.append(random.sample(questionByType['medium'][qType],1))
                elif qType == 'orderBy':
                    if len(questionByType['medium'][qType]) >= 1:
                        medium .append(random.sample(questionByType['medium'][qType],1))
                elif qType == 'matchTheFollowing':
                    if len(questionByType['medium'][qType]) >= 1:
                        medium.append(random.sample(questionByType['medium'][qType],1))
                #elif qType == 'mmcq':
                    #if len(questionByType['medium'][qType]) >= 1:
                        #medium.append(random.sample(questionByType['medium'][qType],1))           
            
            for qType in questionByType['hard']: # function to pick random hard question 
                if qType == 'mcq':
                    if len(questionByType['medium'][qType]) >= 1:
                        hard.append(random.sample(questionByType['hard'][qType],1))
                elif qType == 'mmcq':
                    if len(questionByType['medium'][qType]) >= 1:
                        hard.append(random.sample(questionByType['hard'][qType],1))

            questiontypeO = easy + medium + hard
            questions = [element for innerList in questiontypeO for element in innerList]

            questionIds = []    #variable to store all questin id

            for qId in questions:
                if qId.id not in questionIds:
                    questionIds.append(qId.id)

            allQuestionComponents = Question_Component.objects.values().filter(question_id__in=questionIds)  # query to get all question components
            questionComponentdict = defaultdict(list)

            for components in allQuestionComponents: # function to group questionid(Key) and question component(values)
                quesionId = components['question_id']
                questionComponentdict[quesionId].append(components)


            for question in questions:  # function to qroup question and option
                questionOptionData = {} #to store question data(ex-id,points,text)and optiondata(ex-id, text)
                if question.type_code == 'mcq' or question.type_code == 'mmcq':
                    questionOptionData['id'] = question.id
                    questionOptionData['points'] = question.points
                    questionOptionData['type'] = question.type_code
                    questionOptionData['text'] = question.text
                    questionOptionData['title'] = question.title

                    optionsList = []    # for storing all options

                    if question.id in questionComponentdict:
                        optionComponent = questionComponentdict[question.id]
                        for options in optionComponent:
                            singleOption = {}     # to store single option and append to optionList
                            singleOption['id'] = options['id']
                            singleOption['text'] = options['text']
                            singleOption['isAnswer'] = options['is_answer']

                            optionsList.append(singleOption)

                        questionOptionData['options'] = optionsList

                    data['questionSet']['questions'].append(questionOptionData)

                elif question.type_code == 'orderBy':
                    questionOptionData['id'] = question.id
                    questionOptionData['points'] = question.points
                    questionOptionData['type'] = question.type_code
                    questionOptionData['text'] = question.text
                    questionOptionData['correctSequenceId'] = question.actual_sequence_string
                    questionOptionData['title'] = question.title
                    optionsList = []

                    if question.id in questionComponentdict:
                        optionComponent = questionComponentdict[question.id]
                        for options in optionComponent:
                            singleOption = {}     # to store single option and append to optionList
                            singleOption['id'] = options['id']
                            singleOption['text'] = options['text']                    
                            
                            optionsList.append(singleOption)

                        questionOptionData['options'] = optionsList
                    
                    data['questionSet']['questions'].append(questionOptionData)
                
                elif question.type_code == 'matchTheFollowing':
                    questionOptionData['id'] = question.id
                    questionOptionData['points'] = question.points
                    questionOptionData['type'] = question.type_code
                    questionOptionData['text'] = question.text
                    questionOptionData['title'] = question.title
                    leftColumnList = []
                    rightColumnList = []

                    if question.id in questionComponentdict:
                        optionComponent = questionComponentdict[question.id]
                        for options in optionComponent:
                            leftColumnOption = {}
                            rightColumnOption = {}

                            if options['subtype'] == '2':
                                leftColumnOption['id'] = options['id']
                                leftColumnOption['text'] = options['text']
                                leftColumnOption['correctAnswerId'] = options['matching_component_id']

                                leftColumnList.append(leftColumnOption)

                            elif options['subtype'] == '3':
                                rightColumnOption['id'] = options['id']
                                rightColumnOption['text'] = options['text']    

                                rightColumnList.append(rightColumnOption)

                        questionOptionData['leftColumn'] = leftColumnList
                        questionOptionData['rightColumn'] = rightColumnList
                    
                    data['questionSet']['questions'].append(questionOptionData)
                
                elif question.type_code == 'categorise':
                    questionOptionData['id'] = question.id
                    questionOptionData['points'] = question.points
                    questionOptionData['type'] = question.type_code
                    questionOptionData['text'] = question.text
                    questionOptionData['title'] = question.title
                    categoryItemList = []
                    categoryList = []

                    if question.id in questionComponentdict:
                        optionComponent = questionComponentdict[question.id]
                        for options in optionComponent:
                            categoryItemOption = {}
                            categoryOption = {}

                            if options['subtype'] == '5':
                                categoryItemOption['id'] = options['id']
                                categoryItemOption['text'] = options['text']
                                categoryItemOption['correctAnswerId'] = options['matching_component_id']

                                categoryItemList.append(categoryItemOption)
                            
                            elif options['subtype'] == '4':
                                categoryOption['id'] = options['id']
                                categoryOption['text'] = options['text']

                                categoryList.append(categoryOption)
                        
                        questionOptionData['categoryItem'] = categoryItemList
                        questionOptionData['category'] = categoryList
                    
                    data['questionSet']['questions'].append(questionOptionData)

            print('alldata',data)
            random.shuffle(data['questionSet']['questions'])
            
            return render(request, 'quizplayer.html', {'data': data,'studData':studData})
        
        except Exception as e:
            return HttpResponseNotFound("Page not found " + e.message)


class SubmitAnswer(View):

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            studentId=int(requestParams["studentId"])
            offeringId=int(requestParams["offeringId"])
            attempt=int(requestParams["attempt"])
            questionSubmitedAnswers=requestParams.get("questionSubmitedAnswers",None)
            questionsetId=questionSubmitedAnswers[0]["questionSet_id"]
            count_correct_ans=0
            res=0
            

            for d in questionSubmitedAnswers:
                if d.get("isCorrect")==1:
                    count_correct_ans+=1
                    res+=d.get("question_points")
            if count_correct_ans/len(questionSubmitedAnswers)>0.4:
                res_status=1
            else:
                res_status=2
            answerdata=Quiz_History.objects.create(student=Student.objects.get(id=studentId),offering=Offering.objects.get(id=offeringId),attempt=attempt,question_set=Question_Set.objects.get(id=questionsetId),total_points=res,status=True,result=res_status,created_on=genUtility.getCurrentTime(),updated_on=genUtility.getCurrentTime(), created_by=self.request.user, updated_by_id=settings.SYSTEM_USER_ID_AUTH)
            
            for d in questionSubmitedAnswers:
                totalpoints=0
                userans=[]
                if (d.get("question_type")=="mcq" and d.get("isCorrect")==1) or (d.get("question_type")=="mmcq" and d.get("isCorrect")==1) or (d.get("question_type")=="orderBy" and d.get("isCorrect")==1) or ( d.get("question_type")=="matchTheFollowing" and d.get("isCorrect")==1):
                    totalpoints+=d.get("question_points")
                    k=json.dumps(d.get("user_submitted_ans"))
                    userans.append(k)
                elif d.get("question_type")=="categorise" and d.get("isCorrect")==1:
                    totalpoints+=d.get("question_points")
                    i=json.dumps({"First category":d.get("first_category_ans"),"Second category":d.get("second_category_ans")})
                    userans.append(i)
                elif (d.get("question_type")=="mcq" and d.get("isCorrect")==0) or (d.get("question_type")=="mmcq" and d.get("isCorrect")==0) or (d.get("question_type")=="orderBy" and d.get("isCorrect")==0) or (d.get("question_type")=="matchTheFollowing" and d.get("isCorrect")==0):
                    k=json.dumps(d.get("user_submitted_ans"))
                    userans.append(k)
                elif d.get("question_type")=="categorise" and d.get("isCorrect")==0:
                    i=json.dumps({"First category":d.get("first_category_ans"),"Second category":d.get("second_category_ans")})
                    userans.append(i) 
                ansdetail=Quiz_History_Detail.objects.create(quiz_history=answerdata,question_id=d.get("question_id"),points_earned=totalpoints,result=d.get("isCorrect"),answer_given=userans[0],created_on=genUtility.getCurrentTime(),updated_on=genUtility.getCurrentTime(), created_by=self.request.user, updated_by_id=settings.SYSTEM_USER_ID_AUTH)
                
                del userans[:]

            return render(request,'quizplayer.html')
        except Exception as e:
            return HttpResponseNotFound(e.message)
        
   
@login_required
def updateDigitalSchool(request, schoolId):
    if request.method == "POST":
        if request.user.is_superuser:
            name = request.POST['schoolName']
            status = request.POST['schoolStatus']
            taluk = request.POST['taluk']
            district = request.POST['district']
            state = request.POST['state']
            pincode = request.POST['pincode']
            description = request.POST['description']
            purpose = request.POST['purpose']
            language = request.POST['language']
            partnerName = request.POST['partnerName']
            partnerContact = request.POST['partnerContact']
            centerLocation = request.POST['centerLocation']
            centerProgramType = request.POST['programType']

            try:
                schoolList = DigitalSchool.objects.filter(id=schoolId).select_related('partner_owner')
                centerObj  = Center.objects.filter(digital_school_id=schoolId)
                schoolData = schoolList[0]
                center = centerObj[0]

                schoolData.name = name
                schoolData.status = status
                schoolData.taluk = taluk
                schoolData.state = state
                schoolData.district = district
                schoolData.pin_code = pincode
                schoolData.description = description
                schoolData.statement_of_purpose = purpose
                schoolData.partner_owner.name_of_organization = partnerName
                schoolData.partner_owner.email = partnerContact
                schoolData.course_provider.language_code = language
                center.name = name
                center.state = state
                center.district = district
                center.description = description
                center.location_map = centerLocation
                center.program_type = int(centerProgramType)

                schoolData.save()
                schoolData.partner_owner.save()
                schoolData.course_provider.save()
                center.save()

                return HttpResponseRedirect('/partner/digitalschool/'+schoolId+'/')

            except Exception as e:
                logService.logException("school approval page", e.message)
                return HttpResponseNotFound('unable to save data please try again')
        else:
            return HttpResponseRedirect('/myevidyaloka/')