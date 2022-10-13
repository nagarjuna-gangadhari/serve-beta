import json
import urllib2
from datetime import datetime

from django.contrib import auth
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import ensure_csrf_cookie
from django.forms.models import model_to_dict
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import simplejson
import social_auth
from social_auth.backends import get_backend

from web.models import UserProfile, RolePreference, Role
from api.models import FcmKey
from .forms import UserForm

#response status code constants
RESPONSE_OK = 0
RESPONSE_NOT_OK = 1

@ensure_csrf_cookie
def EnsureCsrf (request):
   return HttpResponse("")

def get_supported_social_backends():
    supported_social_backends = {}
    for _backends in settings.AUTHENTICATION_BACKENDS:
        if "social_auth" not in  _backends:
            continue
        try:
            backend_object = eval(_backends)
            backend_name, backend_type = _backends.split('.')[-2:]
            supported_social_backends.setdefault(backend_name, []).append(backend_object.name)
        except AttributeError:
            continue
    if not supported_social_backends and not retry:
        '''
        In external scripts all the enabled backends are not loading by default by social auth
        if we initialize the backends using django.contrib.auth only then
        social auth is able to load the backends. So just trying if it works here as well.
        '''
        backends = auth.get_backends()
        return get_supported_social_backends(retry = True)
    return supported_social_backends

def oauthtoken_to_user(request,backend_name,token,username,password,*args, **kwargs):
    """Check and retrieve user with given token.
    """
    if not isinstance(backend_name, list):
        backend_name = [backend_name]

    if 'auth' in backend_name:
        user = authenticate(username = username, password = password)
    else:
        user = None
        response = {}
        for _backend_name in backend_name:
            backend = get_backend(_backend_name,request,"")
            try:
                response = backend.user_data(token) or {}
            except ValueError:
                continue

            if not response:
                try:
                    refresh_token_response = backend.refresh_token(token)
                except urllib2.HTTPError:
                    continue
                if refresh_token_response:
                    token = refresh_token_response['access_token']
                    response = backend.user_data(token) or {}
                    if not response:
                        continue

            response['access_token'] = token
            kwargs.update({'response': response, _backend_name: True})
            user = authenticate(*args, **kwargs)
            if isinstance(user, User):
                break
        if not user and response:
            user = backend.do_auth(access_token=token)

    if isinstance(user, User):
        login(request, user)
    return user

def get_user_info(user):
    user_info = {}
    if not isinstance(user, User):
        return user_info

    basic_fields = [field.name for field in user._meta.fields]
    basic_fields.remove('password')
    user_info.update(model_to_dict(user, fields=basic_fields))

    usp_skip_fields = ['pref_roles', 'pref_offerings', 'role', 'referred_user']
    user_profile = user.userprofile
    if isinstance(user_profile, UserProfile):
        usp_fields = [field.name for field in user_profile._meta.fields]
        for usp_skip_field in usp_skip_fields:
            if usp_skip_field in usp_fields:
                usp_fields.remove(usp_skip_field)

        usp_dict = model_to_dict(user_profile, fields=usp_fields)
        if 'id' in usp_dict:
            usp_id  = usp_dict.pop('id')
        user_info.update(usp_dict)
        #user_info['roles'] = [{role.id: role.name} for role in user_profile.pref_roles.all()]
        roles_info = user_info.setdefault('roles', [])
        for role in user_profile.pref_roles.all():
            role_dict = {"role_id": role.id, "role": role.name}
            try:
                rolepref_obj = user_profile.rolepreference_set.get(role=role)
                step_filter = Q(step__stepname__icontains = 'Self Evaluation')
                step_filter = step_filter | Q(step__stepname__icontains = 'Selection Discussion')
                steps_status = rolepref_obj.onboardingstepstatus_set.filter(step_filter)
                for step_status in steps_status:
                    if 'self evaluation' in step_status.step.stepname.lower():
                        role_dict["self_eval_status"] = step_status.status
                    else:
                        slots = user_profile.selectiondiscussionslot_set.filter(role = role).order_by('-booked_date')
                        slots_outcome = ""
                        for slot in slots:
                            #Latest slot outcome
                            slots_outcome = slot.outcome.lower()
                            break

                        if slots_outcome == "cancelled" or not slots_outcome:
                            role_dict["tsd_status"] = False
                        else:
                            role_dict["tsd_status"] = True
            except RolePreference.DoesNotExist:
                pass
            roles_info.append(role_dict)

    for k,v in user_info.iteritems():
        if isinstance(v, datetime):
            user_info[k] = v.strftime("%d:%m:%Y %H:%M")

    user_info['dob'] = str(user_info['dob'])
    return user_info


def LoginView(request):
    response_data = {'message': '', 'status': RESPONSE_OK, 'data': {}}
    username      = request.POST.get('username','')
    password      = request.POST.get('password','')
    backend       = request.POST.get('backend','auth')
    access_token  = request.POST.get('access_token','')

    #Getting Supported/Enabled SocialAuth backends from settings
    supported_social_backends =  get_supported_social_backends()
    #Appending 'auth' Model Backend by default
    supported_social_backends.update({'auth': 'auth'})

    if backend not in supported_social_backends:
        response_data['message'] = "Oops this Social Auth Backend is not supported yet!"
        response_data['status']  = RESPONSE_NOT_OK
        return HttpResponse(json.dumps(response_data),mimetype="application/json")

    backend = supported_social_backends.get(backend)
    user = oauthtoken_to_user(request,backend,access_token,username,password)
    if not user:
        response_data['message'] = "User Authentication Failed"
        response_data['status']  = RESPONSE_NOT_OK
        return HttpResponse(json.dumps(response_data),mimetype="application/json")

    response_data['data'] = get_user_info(user)

    return HttpResponse(json.dumps(response_data),mimetype="application/json")


def LogoutView(request):
    response_data = {'message': '', 'status': 200, 'data': {}}
    fcm_key = request.POST.get('fcm_key', '')
    if fcm_key:
        try:
            obj = FcmKey.objects.get(fcm_key=fcm_key)
            obj.user_id = ""
            obj.save()
        except FcmKey.MultipleObjectsReturned:
            obj = FcmKey.objects.filter(fcm_key=fcm_key).update(user_id="")
            obj.save()
        except FcmKey.DoesNotExist:
            pass
    logout(request)
    return HttpResponse(json.dumps(response_data),mimetype="application/json")


@csrf_exempt
def SignupView(request):
    response_data = {'message': '', 'status': RESPONSE_OK, 'data': {}}
    form = UserForm(request.POST)
    if form.is_valid():
        form_data = form.cleaned_data
        password = form_data.pop('password')
        new_user = User.objects.create(**form.cleaned_data)
        new_user.set_password(password)
        new_user.save()
        user = authenticate(username=form.cleaned_data['username'], password=password)
        login(request, user)

        response_data['data'] = get_user_info(user)
        user_id = new_user.id
        ref_id = request.POST.get('ref_id')
        language = str(request.POST.get('language', ''))
        role_pref = str(request.POST.get('role_pref'))
        role_id = 1
        if role_pref == "Others":
            role_id = 4
        phone = str(request.POST.get('phone', ''))

        UserProfile.objects.filter(user_id = user_id).update(referencechannel = ref_id, phone=phone, pref_medium=language)
        db_user_profile = UserProfile.objects.get(user_id=user_id)
        rf = RolePreference.objects.create(userprofile=db_user_profile, role=Role.objects.get(id=role_id), availability=True, role_status='New', role_outcome='Not Started')
    else:
        messages = []
        response_data['status'] = RESPONSE_NOT_OK
        for _field, msgs in form.errors.iteritems():
            messages.extend(msgs)
        response_data['message'] = " and ".join(messages)

    return HttpResponse(json.dumps(response_data),mimetype="application/json")
