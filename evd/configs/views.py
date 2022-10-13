from tokenize import Name
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import SettingsGroup, SettingsGroupItems, UserSettings, RoleDefaultSettings, AppreciationReason, Stickers, DemandShareShortUrl, Certificate
from web.models import UserProfile, ReferenceChannel, Session, Center, Offering, Ayfy
import ast
import uuid
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from datetime import timedelta
from web.models import Role, RolePreference, OnboardingStepStatus, Ayfy
from django.db.models import Count, Q
from django.core import mail
from django.template.loader import get_template
from django.template import Context, loader
import settings
from glob import glob
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import StringIO
import simplejson
import traceback
from django.views.generic import View
from django.utils.decorators import method_decorator
import thread
from genutilities.views import get_object_or_none
import MySQLdb
from genutilities import views as genUtility
import genutilities.logUtility as logService
from web.views import *
# from alerts.models import NotificationCategory, NotificationType
# from .forms import RoleNotificationForm, UserNotificationForm
# from django.forms.formsets import formset_factory


@login_required
def list_roles(request, role_id=None):
    if request.method == 'GET':
        if request.user.is_superuser:
            if role_id:
                try:
                    role = Role.objects.get(id=role_id)
                    rolesettings = RoleDefaultSettings.objects.filter(
                        role=role, is_removed=False)
                    # notifications = RoleNotificationSettings.objects.filter(roll__id=role.id)
                    # notifications = [{'type':'SMS','cat':'Wish'},{'type':'SMS','cat':'Announcement'}]
                    return render(request, 'view_or_list_roles.html', {'role': role, 'rolesettings': rolesettings, 'view_flag': True})
                except Role.DoesNotExist:
                    pass
            roles = Role.objects.all()
            return render(request, 'view_or_list_roles.html', {'roles': roles})
        else:
            return HttpResponseRedirect('/profile/')
    else:
        return HttpResponseRedirect('/profile/')


@login_required
def add_role_specific_settings(request, role_id):
    if (request.method == 'GET' or request.method == 'POST') and request.user.is_superuser and role_id:
        try:
            role = Role.objects.get(id=role_id)
            settingsgroups = SettingsGroup.objects.all()

            if request.method == 'GET':
                return render(request, 'add_role_specific_settings.html', {'settings': settingsgroups, 'role': role})

            elif request.method == 'POST':
                response_dict = {}
                for d in request.POST.lists():
                    if d[0] == 'csrfmiddlewaretoken' or d[0] == 'group_id' or d[0] == 'group_name':
                        pass
                    # elif d[0] == 'group_name' :
                    #     if d[1] not in usersettings_json.values():
                    #         usersettings_json[str(d[1])] = str(request.POST.get(d[1][0]+'_allornone'))
                    else:
                        response_dict[str(d[0])] = str(d[1])

                group_id = int(request.POST.get('group_id'))
                roleid = int(request.POST.get('role'))
                if role.id == int(roleid) == int(role_id):
                    settingsgroup = settingsgroups.get(id=group_id)
                    for item in response_dict.items():
                        if '_-' in item[0]:
                            name, id = item[0].split('_-')
                            if id == 'allornone' and str(name) == settingsgroup.group_name:
                                pass
                            else:
                                setgrpitem = settingsgroup.settingsgroupitems_set.get(
                                    id=int(id))
                                values = ''
                                for value in ast.literal_eval(item[1]):
                                    values += value + ','
                                values = values[:-1]
                                try:
                                    rolesettings = RoleDefaultSettings.objects.get(
                                        role=role, settings_grp_items=setgrpitem)
                                    rolesettings.name = name
                                    rolesettings.values = values
                                    rolesettings.updated_by = request.user
                                    rolesettings.is_removed = False
                                except RoleDefaultSettings.DoesNotExist:
                                    rolesettings = RoleDefaultSettings.objects.create(role=role,
                                                                                      settings_grp_items=setgrpitem, name=name,
                                                                                      values=values, added_by=request.user)
                                rolesettings.save()
                                # print 'name',name,'settings name',setgrpitem.input_name,'item values',item[1],'setting values',setgrpitem.input_values

                    all_rolesettings = RoleDefaultSettings.objects.filter(
                        settings_grp_items__settings_group=settingsgroup, role=role)
                    for rolesetitem in all_rolesettings:
                        i = 0
                        for item in response_dict.items():
                            if '_-' in item[0]:
                                name, id = item[0].split('_-')
                                if str(name) == rolesetitem.name:
                                    i += 1
                        if i == 0:
                            rolesetitem.is_removed = True
                            rolesetitem.save()
                    return HttpResponseRedirect('/config/roles/%s' % role.id)
                else:
                    return HttpResponseRedirect('/config/roles/')
        except Role.DoesNotExist:
            return HttpResponseRedirect('/config/roles/')
    else:
        return HttpResponseRedirect('/config/roles/')
#
# @login_required
# def add_role_specific_notifications(request,role_id):
#     if role_id:
#         rolespecificformset = formset_factory(RoleNotificationForm,extra=0)
#         # notify_categories = NotificationCategory.objects.all()
#         # nc_values = notify_categories.values('id', 'name')
#         # labels_ncats = [str(nc['name']) for nc in nc_values]
#         # if request.method == 'GET':
#         #     frmset = rolespecificformset(initial=[{'ncategoryid':nc['id']} for nc in nc_values])
#         #     return render(request,'add_rolespecific_notifications.html',{'labels_ncats':labels_ncats,'frmset':frmset})
#         # elif request.method == 'POST':
#         #     frmset = rolespecificformset(request.POST)
#         #     if frmset.is_valid():
#         #         for form in frmset:
#         #             ncategoryid = form.cleaned_data['ncategoryid']
#         #             notify_types = form.cleaned_data['notify_types']
#         #             print 'notify_types',notify_types,'ncategoryid',ncategoryid
#         #     else:
#         #         return render(request, 'add_rolespecific_notifications.html',{'labels_ncats': labels_ncats, 'frmset': frmset})
#         # else:
#         #     return HttpResponseRedirect('/config/roles/%s/' %role_id)
#     else:
#         return HttpResponseRedirect('/profile/')
#
#
# @login_required
# def add_user_specific_notifications(request,user_id):
#     if user_id:
#         userspecificformset = formset_factory(UserNotificationForm,extra=0)
#         # notify_categories = NotificationCategory.objects.all()
#         # nc_values = notify_categories.values('id','name')
#         # labels_ncats = [str(nc['name']) for nc in nc_values]
#         # if request.method == 'GET':
#         #     frmset = userspecificformset(initial=[{'ncategoryid':nc['id'],'role_specific':True} for nc in nc_values])
#         #     return render(request,'add_userspecific_notifications.html',{'labels_ncats':labels_ncats,'frmset':frmset})
#     else:
#         return HttpResponseRedirect('/profile/')


@login_required
def user_settings(request):
    if request.method == 'GET':
        settingsgroup = SettingsGroup.objects.all()
        userprofile = UserProfile.objects.get(user=request.user)
        if userprofile.languages_known:
            userprofile.languages_known = ast.literal_eval(
                userprofile.languages_known)
        else:
            userprofile.languages_known = []
        if userprofile.usersettings_data:
            usersettings_json = ast.literal_eval(userprofile.usersettings_data)
        else:
            usersettings_json = {}
        user_profile_dict = userprofile.get_dict()
        location_fields = ['country', 'state', 'city']
        user_location_info = {}
        for k, v in user_profile_dict.iteritems():
            if k in location_fields and v:
                user_location_info[k] = str(v)
        refchannel = ReferenceChannel.objects.filter(
            id=userprofile.referencechannel_id)
        if refchannel:
            refchannel = refchannel[0]
        ref_channels = ReferenceChannel.objects.filter(
            partner__status='Approved')

#         curr_user = request.user
        roles, pref_roles, unassigned_offering_arr, prof_per = [], [], [], 35
#         user_profile = UserProfile.objects.filter(user=curr_user)
        if userprofile:
            admin_assigned_roles = ["TSD Panel Member", "Class Assistant",
                                    "vol_admin", "vol_co-ordinator", "Partner Admin", "Content Admin"]
            roles = Role.objects.exclude(name__in=admin_assigned_roles)
            pref_roles = [role.id for role in userprofile.pref_roles.exclude(
                name__in=admin_assigned_roles)]
        language_dropdown = ['Bengali', 'Gujarathi', 'Hindi', 'Kannada', 'Malayalam',
                             'Marathi', 'Oriya', 'Punjabi', 'Assamese', 'Tamil', 'Telugu', 'Urdu']
        unavail_list = [x for x in dict(
            UserProfile._meta.get_field('unavailability_reason').choices)]
        return render(request, 'user_settings_group_item.html', {'settings': settingsgroup, 'user_profile': userprofile, 'user_settings': usersettings_json, 'user_location_info': user_location_info, 'ref_channels': ref_channels, 'referencechannel': refchannel, 'roles': roles, 'pref_roles': pref_roles, 'language_dropdown': language_dropdown, 'unavail_list': unavail_list})
    elif request.method == 'POST':
        # print 'sms',request.POST.get('SMS')
        response_dict = {}
        
        
        for d in request.POST.lists():
            if d[0] == 'csrfmiddlewaretoken' or d[0] == 'group_id' or d[0] == 'group_name':
                pass
            # elif d[0] == 'group_name' :
            #     if d[1] not in usersettings_json.values():
            #         usersettings_json[str(d[1])] = str(request.POST.get(d[1][0]+'_allornone'))
            else:
                response_dict[str(d[0])] = str(d[1])

        group_id = int(request.POST.get('group_id'))
        settingsgroup = SettingsGroup.objects.get(id=group_id)
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except (UserProfile.DoesNotExist, UserProfile.MultipleObjectsReturned):
            
            return HttpResponseRedirect('/v2/vLounge')
       
        
        
        consent=str(request.POST.get('consent_data_-6'))

        if consent=='Accept':
            user_profile.consent=1
        elif consent=='Decline':
            user_profile.consent=2
         
        else:
            pass
        user_profile.save()
        for item in response_dict.items():
            if '_-' in item[0]:
                name, id = item[0].split('_-')
                if id == 'allornone' and str(name) == settingsgroup.group_name:
                    pass
                else:
                    setgrpitem = settingsgroup.settingsgroupitems_set.get(
                        id=int(id))
                    values = ''
                    for value in ast.literal_eval(item[1]):
                        values += value + ','
                    values = values[:-1]
                    try:
                        usersetting = UserSettings.objects.get(
                            user=request.user, settings_grp_items=setgrpitem)
                        usersetting.name = name
                        usersetting.values = values
                        usersetting.updated_by = request.user
                        usersetting.is_removed = False
                        
                    except UserSettings.DoesNotExist:
                        usersetting = UserSettings.objects.create(
                            user=request.user, settings_grp_items=setgrpitem, name=name, values=values, added_by=request.user)
                    usersetting.save()
            
                    # print 'name',name,'settings name',setgrpitem.input_name,'item values',item[1],'setting values',setgrpitem.input_values
            elif '_' in item[0]:
                name, id = item[0].split('_')
                if id == 'allornone' and str(name) == settingsgroup.group_name:
                    allornone = ast.literal_eval(item[1])
                    usersettingsdata = UserProfile.objects.get(
                        user=request.user)
                    if usersettingsdata.usersettings_data:
                        usersettings_json = ast.literal_eval(
                            usersettingsdata.usersettings_data)
                        usersettings_json[settingsgroup.group_name] = allornone[0]
                        usersettingsdata.usersettings_data = usersettings_json
                    else:
                        usersettings_json = {}
                        usersettings_json[settingsgroup.group_name] = allornone[0]
                        usersettingsdata.usersettings_data = usersettings_json
                    usersettingsdata.save()
                else:
                    pass
        all_usersettings = UserSettings.objects.filter(
            settings_grp_items__settings_group=settingsgroup, user=request.user)
        for usersetitem in all_usersettings:
            i = 0
            for item in response_dict.items():
                if '_-' in item[0]:
                    name, id = item[0].split('_-')
                    if str(name) == usersetitem.name:
                        i += 1
            if i == 0:
                usersetitem.is_removed = True
                usersetitem.save()

        # usersettings = UserSettings.objects.create()
        # return  HttpResponseRedirect('/config/user/settings/')
        return HttpResponseRedirect('/v2/vLounge')


@login_required
def userprofile_save(request):
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except (UserProfile.DoesNotExist, UserProfile.MultipleObjectsReturned):
            # return HttpResponseRedirect('/config/user/settings/')
            return HttpResponseRedirect('/v2/vLounge')
        user_profile.user.first_name = request.POST.get('firstname')
        user_profile.user.last_name = request.POST.get('lastname')
        user_profile.user.email = request.POST.get('email')
        user_profile.secondary_email = request.POST.get('alt_email')
        user_profile.skype_id = request.POST.get('skype_id')
        user_profile.phone = request.POST.get('phone')
        user_profile.gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        dateofbirth = datetime.datetime.strptime(
            str(dob)+'-01-01', '%Y-%m-%d').date()
        user_profile.dob = dateofbirth
        user_profile.pref_medium = request.POST.get('prefered_medium')
        refer = request.POST.get('refer')
        reference_id = request.POST.get('reference_id')
        
        if user_profile.referencechannel and user_profile.referencechannel.partner_id:
            pass
        else:
            ref_id = request.POST.get('referrence_channel')
            if ref_id:
                try:
                    refchannel = ReferenceChannel.objects.get(id=ref_id)
                    user_profile.referencechannel = refchannel
                except ReferenceChannel.DoesNotExist:
                    pass
        user_profile.country = request.POST.get('country')
        user_profile.state = request.POST.get('state')
        user_profile.city = request.POST.get('city')
        user_profile.profession = request.POST.get('profession')
        user_profile.short_notes = request.POST.get('short_notes')
        user_profile.profile_completion_status = True
        user_profile.user.save()
        user_profile.save()
    # return HttpResponseRedirect('/config/user/settings/')
    return HttpResponseRedirect('/v2/vLounge')
@login_required
def userprofile_add_consent(request):
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except (UserProfile.DoesNotExist, UserProfile.MultipleObjectsReturned):
            
            return HttpResponseRedirect('/v2/vLounge')
       
        
        
        consent=str(request.POST.get('consent_data'))

        if consent=='Accept':
            user_profile.consent=1
        elif consent=='Decline':
            user_profile.consent=2
         
        else:
            pass
        user_profile.save()
        return HttpResponseRedirect('/v2/vLounge')
    

            


@csrf_exempt
def user_preferences_save(request):
    if request.method == 'POST':
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except (UserProfile.DoesNotExist, UserProfile.MultipleObjectsReturned):
            return HttpResponseRedirect('/config/user/settings/')

        json_p = request.POST.get('json', '')
        details_json = json.loads(json_p)
        
        # no_of_hrs = details_json['no_of_hrs']
        languages_known = details_json['lang_array']
        preferred_roles = details_json['preferred_roles']
        availability_details = details_json['availability_details']
        user_profile.languages_known = languages_known
        # user_profile.no_hrs_week = no_of_hrs
        listOfLanguages = []
        for x in languages_known:
            for key, value in x.items():
                if value == 1:
                    continue
                else:
                    listOfLanguages.append(value)

        pref_langages = ', '.join(map(str, listOfLanguages))
        user_profile.pref_medium = pref_langages
        if preferred_roles:
            selected_roles = [Role.objects.get(
                pk=int(role)) for role in preferred_roles if role]
        else:
            selected_roles = []

        # user_profile.role.clear()
        for role in user_profile.role.filter(type='External'):
            if role.name == 'Partner Admin' or role.id == 10:
                pass
            else:
                user_profile.role.remove(role)
        for role in selected_roles:
            user_profile.role.add(role)

        # user_profile.pref_roles.clear()
        for role in user_profile.pref_roles.filter(type='External'):
            if role.name == 'Partner Admin' or role.id == 10:
                pass
            else:
                user_profile.pref_roles.remove(role)
        for role in selected_roles:
            user_profile.pref_roles.add(role)
        user_profile.save()

        # Creating/Updating the RolePreference table for the user based on his selection of Roles
        pref_roles = user_profile.pref_roles.filter(type='External')
        for role in pref_roles:
            role_preference, created = RolePreference.objects.get_or_create(
                userprofile=user_profile, role=role)
            if role.name == 'Well Wisher':
                role_preference.role_outcome = 'Recommended'
                role_preference.save()
            steps = role.onboardingstep_set.all()
            for step in steps:
                step_status, creat = OnboardingStepStatus.objects.get_or_create(
                    role_preference=role_preference, step=step)

        role = Role.objects.filter(name="Teacher")

        try:
            onboard = user_profile.rolepreference_set.get(role=role[0])
            availability = availability_details['isAvailable']
            if availability:
                onboard.availability = True
                pref_days = availability_details['details']['pref_days']
                days = ''
                for d in pref_days:
                    days += d + ';'
                user_profile.pref_days = days[:-1]
                slots = availability_details['details']['pref_times']
                pref_slots = ''
                for slot in slots:
                    pref_slots += slot[0] + '-' + slot[1] + ';'
                user_profile.pref_slots = pref_slots[:-1]
                subjects = availability_details['details']['pref_subjects']
                pref_subjects = ''
                for d in subjects:
                    pref_subjects += d + ';'
                user_profile.pref_subjects = pref_subjects[:-1]

                from_date = availability_details['details']['availableFrom']
                to_date = availability_details['details']['availableTo']
                if from_date and to_date:
                    from_date = datetime.datetime.strptime(
                        from_date, '%Y-%m-%d')
                    to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')
                date_submited = datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)
                user_profile.from_date = from_date
                user_profile.to_date = to_date

                from web.views import save_step_status
                step_status = save_step_status(
                    onboard.id, 'Availability and Preferences')
            else:
                onboard.availability = False
                follow_up_date = availability_details['details']['Follow_Up_Date']
                if follow_up_date:
                    follow_up_date = datetime.datetime.strptime(
                        follow_up_date, '%Y-%m-%d')
                onboard.follow_up_date = follow_up_date
                user_profile.unavailability_reason = availability_details[
                    'details']['unavailabilityReason']
            onboard_string = '' + str(onboard)
            onboard_name = ''
            if len(onboard_string) > 1:
                onboard_name = onboard_string.split(' ', 1)[1]

            onboard.save()
            from web.views import save_user_activity
            save_user_activity(request,
                               "Role:" + str(
                                   onboard_name) + ",Completed Onboarding Step 3: Availability and Preferences",
                               'Action')

        except RolePreference.DoesNotExist:
            pass
        user_profile.save()
        return HttpResponse('Success')

##########  For getting Timezone based on Location (Lat/Lang)  ###################
# from tzwhere import tzwhere
# tz = tzwhere.tzwhere()
# @csrf_exempt
# def get_timezone_by_location(request,latitude='22.9833',longitude='73.5833'):
#     tzname = tz.tzNameAt(float(latitude), float(longitude))
#     return HttpResponse(tzname)


def has_mail_receive_accepted(user, type_of_notify):
    ''' Takes User(Auth User) objects and Type of Email Notification and return whehter User or Role settings has access to send an Email  '''
    data = {'user_settings': False, 'role_settings': False}
    try:
        user_settings = UserSettings.objects.get(
            user=user, settings_grp_items__settings_group__group_name='notification', settings_grp_items__input_name='email', is_removed=False)
        data['user_settings'] = True
    except UserSettings.DoesNotExist:
        # Role Specific Mail will go here
        if type_of_notify not in ['Feedback Surveys', 'Feedback', 'Survey', 'Season Greetings', 'Wishes']:
            if user.userprofile.role.all() or user.userprofile.pref_roles.all():
                role_outcome_count = 0
                for role in user.userprofile.role.all():
                    try:
                        role_outcome = user.userprofile.rolepreference_set.get(
                            role=role).role_outcome
                    except RolePreference.DoesNotExist:
                        role_outcome = ''
                    if role_outcome == 'Recommended':
                        try:
                            role_settings = RoleDefaultSettings.objects.get(
                                role=role, settings_grp_items__settings_group__group_name='notification', settings_grp_items__input_name='email', is_removed=False)
                            role_outcome_count += 1
                        except RoleDefaultSettings.DoesNotExist:
                            pass
                if role_outcome_count:
                    data['role_settings'] = True
        if type_of_notify == 'Reset_Password':
            data['role_settings'] = True
    return data


@login_required
def add_appreciationReason(request, reason_id=None):
    if request.method == 'POST' and request.user.is_superuser:
        # reason_types_choices = AppreciationReason._meta.get_field('reason_type').choices
        # for_whom_choices = AppreciationReason._meta.get_field('for_whom').choices
        # return render(request, 'add_appreciation_reason.html', {'reason_types_choices':reason_types_choices,'for_whom_choices':for_whom_choices})
        reason = request.POST.get('reason', '').strip()
        reason_type = request.POST.get('reason_type')
        for_whom = request.POST.get('for_whom')
        form_reason_id = request.POST.get('appre_reason_id')
        if reason_id and reason_id == form_reason_id:
            try:
                reason_obj = AppreciationReason.objects.get(id=reason_id)
                reason_obj.reason_type = reason_type
                reason_obj.for_whom = for_whom
                reason_obj.reason = reason
                reason_obj.updated_by = request.user
                reason_obj.save()
            except AppreciationReason.DoesNotExist:
                pass
        else:
            try:
                appre_reason = AppreciationReason.objects.get(
                    reason_type=reason_type, for_whom=for_whom, reason=reason)
            except AppreciationReason.DoesNotExist:
                appre_reason = AppreciationReason.objects.create(
                    reason_type=reason_type, for_whom=for_whom, reason=reason, added_by=request.user)
        return HttpResponseRedirect('/config/appreciationreasons/')
    else:
        return HttpResponseRedirect('/myevidyaloka')


@login_required
def list_appreciationReasons(request):
    if request.user.is_superuser and request.method == 'GET':
        appreciation_reasons = AppreciationReason.objects.filter(
            reason_type='appreciation')
        reason_types_choices = AppreciationReason._meta.get_field(
            'reason_type').choices
        for_whom_choices = AppreciationReason._meta.get_field(
            'for_whom').choices
        return render(request, 'list_appreciationReasons.html', {'appreciation_reasons': appreciation_reasons, 'reason_types_choices': reason_types_choices, 'for_whom_choices': for_whom_choices})
    else:
        return HttpResponseRedirect('/myevidyaloka')


@login_required
def add_sticker(request, sticker_id=None):
    if request.method == 'POST' and request.user.is_superuser:
        # reason_types_choices = AppreciationReason._meta.get_field('reason_type').choices
        # for_whom_choices = AppreciationReason._meta.get_field('for_whom').choices
        # return render(request, 'add_appreciation_reason.html', {'reason_types_choices':reason_types_choices,'for_whom_choices':for_whom_choices})
        sticker_name = request.POST.get('sticker_name', '').strip()
        sticker_type = request.POST.get('sticker_type')
        for_whom = request.POST.get('for_whom')
        form_sticker_id = request.POST.get('sticker_id')
        photo = request.FILES.get('photo', '')
        if sticker_id and sticker_id == form_sticker_id:
            try:
                sticker = Stickers.objects.get(id=sticker_id)
                sticker.sticker_type = sticker_type
                sticker.for_whom = for_whom
                sticker.sticker_name = sticker_name
                sticker.updated_by = request.user
                if photo:
                    sticker.sticker_path = photo
                sticker.save()
            except Stickers.DoesNotExist:
                pass
        else:
            try:
                sticker = Stickers.objects.get(
                    sticker_type=sticker_type, for_whom=for_whom, sticker_name=sticker_name)
            except Stickers.DoesNotExist:
                sticker = Stickers.objects.create(
                    sticker_type=sticker_type, for_whom=for_whom, sticker_name=sticker_name, added_by=request.user)
                if photo:
                    sticker.sticker_path = photo
                    sticker.save()
        return HttpResponseRedirect('/config/stickers/')
    else:
        return HttpResponseRedirect('/myevidyaloka')


@login_required
def list_stickers(request):
    if request.user.is_superuser and request.method == 'GET':
        stickers = Stickers.objects.filter(sticker_type='appreciation')
        sticker_types_choices = Stickers._meta.get_field(
            'sticker_type').choices
        for_whom_choices = Stickers._meta.get_field('for_whom').choices
        return render(request, 'list_stickers.html', {'stickers': stickers, 'sticker_types_choices': sticker_types_choices, 'for_whom_choices': for_whom_choices})
    else:
        return HttpResponseRedirect('/myevidyaloka')


def save_skype_phone(request):
    skype_id = request.POST.get('skype_id', '')
    phone = request.POST.get('phone', '')
    booking_url = request.POST.get('booking_url', '')
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.skype_id = skype_id
        user_profile.phone = phone
        user_profile.save()
    except (UserProfile.DoesNotExist, UserProfile.MultipleObjectsReturned):
        return HttpResponseRedirect('/config/user/settings/')
    return HttpResponseRedirect(booking_url)


def get_my_certificate(request):
    if request.user.is_authenticated():
        certificates = Certificate.objects.filter(user=request.user).values(
            'id', 'user__first_name', 'user__last_name', 'center__name', 'sessions', 'ay__title', 'created_on')
        print(certificates)
        return render(request, 'volunteer_get_my_certificate.html', {'certificates': json.dumps(list(certificates), default=str)})
    else:
        return HttpResponseRedirect('/')


@csrf_exempt
def getDemandSharableLink(request):
    if request.method == 'POST':
        data = json.loads(request.POST['selected_data'])
        sharableLinksData = DemandShareShortUrl.objects.all()
        short_url = ""
        for sharableLinkData in sharableLinksData:
            filtered_data = ast.literal_eval(sharableLinkData.filtered_data)
            try:
                filtered_data["days"], filtered_data["languages"], filtered_data[
                    "contribution_nature"], filtered_data["subjects"], filtered_data["grades"]
                if (sorted(data["days"]) == sorted(filtered_data.get("days"))) and (sorted(data["languages"]) == sorted(filtered_data.get("languages"))) and (sorted(data["contribution_nature"]) == sorted(filtered_data.get("contribution_nature"))) and (sorted(data["subjects"]) == sorted(filtered_data.get("subjects"))) and (sorted(data["grades"]) == sorted(filtered_data.get("grades"))):
                    short_url = sharableLinkData.unique_url_path
                    break
            except KeyError:
                pass
        if not short_url:
            unique_url_path = uuid.uuid1()
            sharablelinkData = DemandShareShortUrl.objects.create(
                filtered_data=data, unique_url_path=unique_url_path, added_by=request.user)
            short_url = sharablelinkData.unique_url_path
        return HttpResponse(short_url)
    else:
        return None


def getDemandSharableLinkForFilters(request):
    if request.method == "GET":
        state = request.GET.get("state", '-1')
        partner = request.GET.get("partner", '-1')
        center = request.GET.get("center", '-1')
        academicYear = request.GET.get("academicyear", '-1')
        from_date = request.GET.get("from", '')
        to_date = request.GET.get("to", '')
        filters = {}
        if state and state != 'All':
            if state != '-1':
                filters['center__state'] = state
        else:

            centers_all = getAllCenters(request)
            states_all = centers_all.values_list(
                'state', flat=True).distinct().order_by('state')
            filters['center__state__in'] = states_all
        if partner and partner != 'All':
            if partner != '-1':
                filters['center__delivery_partner_id'] = partner
        if center and center != 'All':
            if center != '-1':
                filters['center_id'] = center
        if academicYear and academicYear != 'All':
            if academicYear != '-1':
                filters['academic_year__title'] = academicYear
        start_date = datetime.datetime.strptime(from_date, "%d-%m-%Y")
        end_date = datetime.datetime.strptime(to_date, "%d-%m-%Y")

        offerings = Offering.objects.filter(**filters).filter(center__status='Active', start_date__gte=start_date,
                                                              start_date__lte=end_date).filter(Q(status="pending") or Q(status="running",
                                                                                                                        active_teacher_id__isnull=True
                                                                                                                        )).values("course__subject", "course__grade",
                                                                                                                                  "center__name", "language",
                                                                                                                                  )
        # print 'offerings : ',offerings
        request.session['sharableDemandscount'] = len(offerings)
        return HttpResponse(simplejson.dumps(list(offerings)), mimetype="application/json")


@login_required()
def getsharableURLfor(request):
    if request.method == "GET":
        demands_count = request.session['sharableDemandscount']
        state = request.GET.get("state", 'All')
        partner_id = request.GET.get("partner", 'All')
        center = request.GET.get("center", 'All')
        academicYear = request.GET.get("academicyear", 'All')
        from_date = request.GET.get("from", '')
        to_date = request.GET.get("to", '')
        dict = {'state': state, 'center': center, 'partner': partner_id, 'academicYear': academicYear,
                'from_date': from_date, 'to_date': to_date, "demands_count": demands_count}
        if partner_id and not (partner_id == "All" or partner_id == -1):
            from partner.models import Partner
            partner = Partner.objects.get(id=partner_id)
            pref_medium = partner.contactperson.userprofile.pref_medium
            dict['languages'] = [pref_medium]

        sharableLinksData = DemandShareShortUrl.objects.all()
        short_url = ""
        for sharableLinkData in sharableLinksData:
            filtered_data = ast.literal_eval(sharableLinkData.filtered_data)
            try:
                filtered_data["state"], filtered_data["center"], filtered_data["partner"], filtered_data[
                    "academicYear"], filtered_data["from_date"], filtered_data["to_date"]
                if (sorted(dict["state"]) == sorted(filtered_data.get("state"))) and (sorted(dict["partner"]) == sorted(filtered_data.get("partner"))) and (sorted(dict["center"]) == sorted(filtered_data.get("center"))) and (sorted(dict["academicYear"]) == sorted(filtered_data.get("academicYear"))) and (sorted(dict["from_date"]) == sorted(filtered_data.get("from_date"))) and (sorted(dict["to_date"]) == sorted(filtered_data.get("to_date"))):
                    short_url = sharableLinkData.unique_url_path
                    filtered_data['demands_count'] = demands_count
                    sharableLinkData.filtered_data = filtered_data
                    sharableLinkData.save()
                    break
            except KeyError:
                pass
        if not short_url:
            short_url = uuid.uuid1()
            shareurl_obj = DemandShareShortUrl.objects.create(
                filtered_data=dict, unique_url_path=short_url, added_by=request.user)
        del request.session['sharableDemandscount']
        return HttpResponse(short_url)


class GenerateCertificate(View):

    '''
    To genrate certificate for the teacher based on session count
    '''

    @method_decorator(login_required)
    def get(self, request,  *args, **kwargs):
        if self.request.user.is_superuser:

            centers = getAllCenters(self.request).values(
                'id', 'name', 'state').order_by('name')
            ays = Ayfy.objects.filter(board__isnull=False, title__startswith='AY').values_list(
                'title', flat=True).distinct().order_by('-title')
            certificates = Certificate.objects.values('id', 'user__id', 'user__first_name', 'user__last_name',
                                                      'user__email', 'center__name', 'sessions', 'ay__title', 'created_on', 'is_alerted')
            return render(self.request, 'generate_certificate_for_vol.html', {'centers': list(centers), 'ays': list(ays), 'certificates': simplejson.dumps(list(certificates), default=str)})

        else:
            return HttpResponseRedirect('/myevidyaloka')

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            if self.request.user.is_superuser:
                requestParams = json.loads(self.request.body)
                ay = requestParams.get('ay', None)
                state = requestParams.get('state', None)
                center_ids = requestParams.get('centers', None)
                # print(ay, state, center_ids)

                ayk = "'" + ay + "'"
                state = " '" + state + "' "
                center_str = ''
                if center_ids:
                    center_str = " and web_center.id in (1"
                    for id in center_ids:
                        center_str += ','+str(int(id))
                    center_str += ') '

                querytext = '''select web_session.teacher_id user_id, concat(auth_user.first_name, ' ', auth_user.last_name) name,  count(web_session.id) sessions, web_center.id center_id, web_center.name center, web_center.digital_school_id, web_ayfy.id ay_id,  web_ayfy.title ay, web_center.state
                                from web_session join web_offering on web_offering.id = web_session.offering_id join auth_user on auth_user.id = web_session.teacher_id
                                join web_center on web_center.id = web_offering.center_id join web_ayfy on web_ayfy.id = web_offering.academic_year_id
                                where web_session.status='completed' and web_ayfy.title = ''' + ayk + ''' and web_center.state=''' + state + center_str + '''group by web_session.teacher_id, web_center.id'''

                db = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'],
                                     passwd=settings.DATABASES['default']['PASSWORD'], db=settings.DATABASES['default']['NAME'], charset="utf8", use_unicode=True)
                users_cur = db.cursor(MySQLdb.cursors.DictCursor)
                users_cur.execute(querytext)
                result = users_cur.fetchall()
                db.close()
                users_cur.close()

                resp = []
                for obj in result:
                    if obj['sessions'] > 10 or (obj['sessions'] > 2 and obj['digital_school_id']):
                        obj['generated_date'] = datetime.datetime.now().strftime(
                            "%d/%m/%Y")
                        certificate = Certificate.objects.filter(
                            user__id=obj['user_id'], center__id=obj['center_id'], ay__id=obj['ay_id']).order_by('-id')

                        if certificate:
                            cert = certificate[0]
                            cert.sessions = obj['sessions']
                            cert.save()
                            resp.append({'id': cert.id, 'user_id': cert.user_id, 'center': cert.center.name, 'center_id': cert.center_id, 'ay_id': cert.ay_id, 'ay': cert.ay.title,
                                        'name': cert.user.get_full_name(), 'sessions': cert.sessions, 'generated_date': cert.created_on, 'is_alerted': cert.is_alerted})
                        else:
                            user = get_object_or_none(User, id=obj['user_id'])
                            center = get_object_or_none(
                                Center, id=obj['center_id'])
                            ay_obj = get_object_or_none(Ayfy, id=obj['ay_id'])
                            cert = Certificate.objects.create(
                                user=user, center=center, ay=ay_obj, sessions=obj['sessions'], created_by=self.request.user, updated_by=self.request.user)
                            # to_mails.append({'id':cert.id, 'user_name': user.get_full_name(), 'email': user.email})
                            is_alerted = alert_user_for_new_certificate(
                                [{'id': cert.id, 'user_name': user.get_full_name(), 'email': user.email}], ay)
                            if is_alerted:
                                cert.is_alerted = True
                                cert.save()
                            resp.append({'id': cert.id, 'user_id': user.id, 'center': center.name, 'center_id': center.id, 'ay_id': ay_obj.id, 'ay': ay_obj.title,
                                        'name': user.get_full_name(), 'sessions': cert.sessions, 'generated_date': cert.created_on, 'is_alerted': is_alerted})

                return HttpResponse(json.dumps(resp, default=str), content_type="application/json")
            else:
                return HttpResponseRedirect('/myevidyaloka')
        except Exception as e:
            print("FT Exception", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

    @method_decorator(login_required)
    def put(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            certificate_id = requestParams.get('id', None)
            ay = requestParams.get('ay', None)
            cert = get_object_or_none(Certificate, id=certificate_id)
            alert_user_for_new_certificate(
                [{'user_name': cert.user.get_full_name(), 'email': cert.user.email}], ay)
            Certificate.objects.filter(
                id=certificate_id).update(is_alerted=True)
            return genUtility.getSuccessApiResponse(request, 'Success')
        except Exception as e:
            print("FT Exception", e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


def alert_user_for_new_certificate(to_mail_user, ay):
    try:
        if to_mail_user:
            connection = mail.get_connection()
            connection.open()
            logService.logInfo("email server connection:", 'open')
            ay_years = ay.split('-')
            next_ay = 'AY-{0}-{1}'.format(
                int(str(ay_years[1]))+1, int(str(ay_years[2]))+1)
            subject = 'A Warm Thank you from eVidyaloka'
            logService.logInfo("total emails count", str(len(to_mail_user)))
            for user in to_mail_user:
                args = {'username': user['user_name'],
                        'ay': ay, 'next_ay': next_ay}
                body = get_template(
                    'mail/_certificate/volunteer_certificate.html').render(Context(args))
                email = mail.EmailMessage(subject, body, to=[
                                          user['email']], from_email=settings.DEFAULT_FROM_EMAIL, connection=connection)
                email.content_subtype = 'html'
                logService.logInfo("sending email to:", user['email'])
                email.send()
                logService.logInfo("email sent to:", user['email'])
            connection.close()
            logService.logInfo("email server connection:", 'closed')
            return True
    except Exception as e:
        logService.logException("certificate email error", e.message)
        return False


class SendCertificate(View):

    @method_decorator(login_required)
    def post(self, request,  *args, **kwargs):
        try:
            requestParams = json.loads(self.request.body)
            to_mail = requestParams.get('to_mail', None)
            certificates = requestParams.get('certificates', None)

            print(to_mail)

            # if not all([certificates, to_mail]): return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')

            thread.start_new_thread(
                mailCirtificateMulti, ([to_mail], certificates))

            dataObject = {"status": "success", "data": {
                "message": "Status  updated successfully", }, "statusCode": 200}
            return genUtility.getSuccessApiResponse(request, dataObject)

        except Exception as e:
            print(e)
            traceback.print_exc()
            return genUtility.getStandardErrorResponse(request, 'kInvalidRequest')


def mailCirtificateMulti(to_mail, certificates):
    try:

        connection = mail.get_connection()

        # Manually open the connection
        connection.open()
        subject = 'Volunteer Certificates'
        body = "<p>Dear Admin,</p><p>Kindly find the attached files of Certificates of the Teachers for the Requested Center</p>"

        # Construct an email message that uses the connection
        email = mail.EmailMessage(
            subject, body, to=to_mail, from_email=settings.DEFAULT_FROM_EMAIL, connection=connection)

        for cert in certificates:
            userId = cert['user_id']
            userName = cert['name']
            centerName = cert['center']
            sessions = cert['sessions']
            date = cert['generated_date'].split(' ')[0]
            ay = cert['ay']
            print(cert)

            pdf = createPDF(userName, centerName, sessions, date, ay)
            email.attach(str(userId)+'_'+userName+'_'+centerName +
                         '_'+str(ay)+'.pdf', pdf, 'application/pdf')

        email.content_subtype = 'html'
        email.send()  # Send the email
        connection.close()
        print('connection closed')

    except Exception as e:
        print(e)
        traceback.print_exc()


def createPDF(userName, centerName, sessions, date, ay=''):
    pdfFileObj = open('static/volunteer_certificates/avt_2022.pdf', 'rb')
    packet = StringIO.StringIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Times-Bold', 18)
    can.drawCentredString(500, 430, userName.upper())
    can.setFont('Times-Bold', 12)
    can.drawString(580, 392, centerName)
    can.drawString(675, 373, str(sessions))
    can.drawString(768, 373, str(ay))
    can.setFont('Times-Bold', 16)
    can.drawString(360, 210, date)
    can.save()
    packet.seek(0)
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pageObj = pdfReader.getPage(0)
    input = PyPDF2.PdfFileReader(packet)
    pageObj.mergePage(input.getPage(0))
    pdfWriter = PyPDF2.PdfFileWriter()
    pdfWriter.addPage(pageObj)
    buffer = StringIO.StringIO()
    pdfWriter.write(buffer)
    pdf = buffer.getvalue()

    return pdf
