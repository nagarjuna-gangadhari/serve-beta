from web.models import *
from web.views import *

import requests
import json
import urllib
import collections

from workplace_utils import init_logger 

log = init_logger('workplace.log')

# property constants
FIELD_USER_NAME = 'userName'
FIELD_MANAGER_ID = 'managerId'
FIELD_NAME = 'name'
FIELD_GIVEN_NAME = 'givenName'
FIELD_FAMILY_NAME = 'familyName'
FIELD_TITLE = 'title'
FIELD_DEPARTMENT = 'department'
FIELD_PHONE_NUMBERS = 'phoneNumbers'
FIELD_WORK = 'work'
FIELD_VALUE = 'value'
FIELD_ADDRESSES = 'addresses'
FIELD_FORMATTED = 'formatted'
FIELD_LOCALE = 'locale'
FIELD_ACTIVE = 'active'
FIELD_RESOURCES = 'Resources'
FIELD_TOTAL_RESULTS = "totalResults"
FIELD_ITEMS_PER_PAGE = "itemsPerPage"
FIELD_ERROR = 'error'
FIELD_MESSAGE = 'message'
FIELD_ID = 'id'
FIELD_TYPE = 'type'
FIELD_PRIMARY = 'primary'
FIELD_MANAGER = 'manager'
FIELD_SCHEMAS = 'schemas'
FIRST_ITEM = 0

#request constants
HEADER_AUTH_KEY = 'Authorization'
HEADER_AUTH_VAL_PREFIX = 'Bearer '
USERS_RESOURCE_SUFFIX = 'Users'
HTTP_DELIM = '/'
EMAIL_LOOKUP_SUFFIX = '?filter=userName'
ESCAPED_EMAIL_LOOKUP_PREFIX = ' eq \"'
ESCAPED_EMAIL_LOOKUP_SUFFIX = '\"'
START_INDEX = "?startIndex="

#request json constants
SCHEME_CORE = 'urn:scim:schemas:core:1.0'
SCHEME_NTP = 'urn:scim:schemas:extension:enterprise:1.0'

#response status code constants
RESPONSE_OK = 200
RESPONSE_CREATED = 201

#prompt constants
RESULT_STATUS_DELIM = ':'
EXPORT_RESULT_DELIM = " / "
CREATING_USER_PROMPT = 'Creating user '
DELETING_USER_PROMPT = 'Deleting user '
UPDATING_USER_PROMPT = 'Updating user '

#error constants
ERROR_RECORD_NOT_FOUND = 'Record not found for '
ERROR_NEWFIELDS_INVALID_FORMAT = 'newFields must be a dictionary using the following keys: '
ERROR_WITH_MESSAGE_PREFIX = 'Error'
ERROR_WITHOUT_MESSAGE = "Invalid request, no error message found"


#app access tocken . here 
access_token = 'DQVJ2dGl5R2QxUTd4SlZAmQ2Y3NmtLcnBzWUxCTm5MN1lvcFlnOFRSWDYycUR1VGhGX3BRSVVIUnVUVjZABQ1FBTVBVc2JXakJqakszNlFnQ21Eajd5LXNuTVVNd1ZAvaEk4TmVSNnpiMjlnSHZAGX0hXbnFiTWEtSjFPRkJ5VHZAoeVFNOXNfTDQ0RXJJRnpnVlI0X2hoenZAmQzdFbzNsSmt6VHJZAcWp6ZAUI5ckFMcVlwcFVwcVVxRE1GTFJyMGd6REZAWTGVPRmpMUGFrN2RicmtrbQZDZD'

#group scim_url
scim_url = 'https://www.facebook.com/company/1715660655321019/scim/'

def feed_posting(request):
    user_details = users_data = UserProfile.objects.filter(user_id=int(request.user.id)).values('fbatwork_id','fb_member_token')[0]
    action_type = request.GET.get('type','')
    if action_type == 'post':
        post = request.GET.get('message','')
        post.replace(' ', '+')
        posting_url = "https://graph.facebook.com/"+ user_details['fbatwork_id'] +"/feed/?message=" + post + "&access_token=" + user_details['fb_member_token']
        response = requests.post(posting_url)
        return HttpResponse(response.text)
    elif action_type == 'feed':
        feed_url = 'https://graph.facebook.com/'+ user_details['fbatwork_id'] +'/feed/?fields=picture,name,message,link,icon,from,created_time,id,source,story&access_token=' + user_details['fb_member_token'] + '&date_format=U'
        response = requests.get(feed_url)
        return HttpResponse(response.text)
    else:
        return HttpResponse("type is not identified")

def create_user(request):
    result = {}
    if request.user.is_authenticated():
        user_details = request.user.userprofile
        if user_details.fbatwork_id and user_details.fb_member_token:
            result['data'] = 'user existed'
            return HttpResponse(json.dumps(result),content_type='application/json')
        else:
            user_obj = {}
            user_obj['user_id']    = request.user.id
            user_obj['user_name']  = request.user.email
            user_obj['givenName']  = request.user.first_name
            user_obj['familyName'] = request.user.last_name
            user_obj['formatted']  = request.user.first_name
            user_creating_response = createUser(scim_url, access_token, user_obj)
            result['data'] = user_creating_response
            return HttpResponse(json.dumps(result),content_type='application/json')
    else:
        result['data'] = 'login_required'
        return HttpResponse(json.dumps(result),content_type='application/json')

def createUser(scim_url, access_token, userObj):
    user_id = userObj.pop('user_id')
    user_email = userObj.get("user_name", "")
    url = scim_url + USERS_RESOURCE_SUFFIX
    data = getCreatJSON(userObj)
    result = requests.post(url, headers=getHeaders(access_token), data=data)
    if result.status_code == RESPONSE_CREATED:
        mem_data    = json.loads(result.text)
        member_id   = str(mem_data['id'])
        member_access_token = get_facebook_member_token(member_id)
        fb_id_update = UserProfile.objects.filter(user_id=user_id).update(fbatwork_id=member_id,fb_member_token=member_access_token)
        message = "Congrats, you are now part of eVidyaloka Workplace."
        message += "</br>Please check the mail {}, for further steps.".format(user_email)
        return message
    elif result.status_code == 409:
        member_id = getResourceFromEmail(scim_url, access_token,userObj['user_name'])
        member_access_token = get_facebook_member_token(str(member_id))
        if member_id:
            fb_id_update = UserProfile.objects.filter(user_id=user_id).update(fbatwork_id=member_id,fb_member_token=member_access_token)
        message = "Your email {} is already registered with Workplace.".format(user_email)
        message += "</br>You can visit the Workplace by clicking on the link: https://evidyaloka.facebook.com"
        return message
    elif result.status_code == 400:
        message = "We need your Email and Name for creating an acccount."
        message += "</br>Please update the info by clicking on the Edit Profile and try again."
        return message
    else:
        r_errors = result.json().get('Errors', [])
        message = []
        unhandled_errors = []
        for r_error in r_errors:
            if r_error.get('code', "") == 1855009:
                message.append(r_error['description'])
                message.append("Please try with other email, By updating the profile.")
            else:
                error_code = r_error.get('code', "")
                error_desc = r_error.get('description', "")
                if error_desc:
                    unhandled_errors.append("FB ErrorCode: {} -- ErrorMsg: {}".format(error_code, error_desc))
        if message:
            message = "</br>".join(message)
        else:
            message = "Please send your request to Join the Community to Rini Jose, email : rini.jose@evidyaloka.org"
            unhandled_msg = ", ".join(unhandled_errors)
            log.error("UserDetails: {}, {}".format(userObj, unhandled_msg))
        return message

    #return result.status_code == RESPONSE_CREATED

def get_facebook_member_token(member_id):
    values = {
        'access_token' : access_token,
        'fields' : 'impersonate_token'
    }
    
    request_url = 'https://graph.facebook.com/' + member_id+'/?fields='+values['fields']+'&access_token='+values['access_token']
    response = urllib.urlopen(request_url).read()
    if response:
        response = json.loads(response)
        member_token = response['id']
        return member_token


def getResourceFromEmail(scim_url, access_token, email):
    url = scim_url +  USERS_RESOURCE_SUFFIX + EMAIL_LOOKUP_SUFFIX + urllib.quote(ESCAPED_EMAIL_LOOKUP_PREFIX + email + ESCAPED_EMAIL_LOOKUP_SUFFIX, safe='')
    result = requests.get(url, headers=getHeaders(access_token))
    resultObj = json.loads(result.text)
    if resultObj[FIELD_RESOURCES] and len(resultObj[FIELD_RESOURCES]) > 0:
        return resultObj[FIELD_RESOURCES][FIRST_ITEM]['id']

    return None

def getHeaders(access_token):
    headers = {HEADER_AUTH_KEY: HEADER_AUTH_VAL_PREFIX + access_token}
    return headers

def getCreatJSON(userObj):
    json_obj = buildUserJSONObj(userObj)
    json_obj[FIELD_ACTIVE] = True
    return json.dumps(json_obj)

def getName(userObj):
    name = {}
    name[FIELD_GIVEN_NAME] = userObj['givenName']
    name[FIELD_FAMILY_NAME] = userObj['familyName']
    name[FIELD_FORMATTED]  = userObj['formatted']
    return name

def buildUserJSONObj(userObj):
    data = {}
    schemas = [SCHEME_CORE]
    data[FIELD_USER_NAME] = userObj['user_name']
    data[FIELD_NAME]  = getName(userObj)
    data[FIELD_SCHEMAS] = schemas
    return data
