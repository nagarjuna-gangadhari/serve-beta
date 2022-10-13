from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
from django.core.exceptions import ObjectDoesNotExist
import requests
import json
import requests
import urllib
import collections


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


class Command(BaseCommand):
	def handle(self, *args, **options):
		users_data = UserProfile.objects.filter(fbatwork_id='')[:2]
		sample = self.user_creation(users_data)
		print sample
	def user_creation(self,users_data):
		def createUser(scim_url, access_token, userObj):
			user_id = userObj.pop('user_id')
			print 'creating user'
			url = scim_url + USERS_RESOURCE_SUFFIX
			data = getCreatJSON(userObj)
			result = requests.post(url, headers=getHeaders(access_token), data=data)

			if result.status_code == RESPONSE_CREATED:
				mem_data    = json.loads(result.text)
				member_id   = str(mem_data['id'])
				member_access_token = get_facebook_member_token(member_id)
				UserProfile.objects.filter(user_id=user_id).update(fbatwork_id=member_id,fb_member_token=member_access_token)
				return "user_created"
			elif result.status_code == 409 :
				return "user_existed"
			else:
				return "something went wrong"

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
				member_token = response['impersonate_token']
				return member_token


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

		final_data = {}
		final_data['created'] = []
		final_data['not_created'] = []
		for user in users_data:
			user_details = User.objects.filter(id=int(user.user_id))[0]
			user_obj = {}
			user_obj['user_id']    = int(user_details.id)
			user_obj['user_name']  = user_details.email
			user_obj['givenName']  = user_details.first_name
			user_obj['familyName'] = user_details.last_name
			user_obj['formatted']  = user_details.first_name
			user_creating_response = createUser(scim_url, access_token, user_obj)
			if user_creating_response == 'user_created':
				final_data['created'].append(user_details.first_name)
			else:
				final_data['not_created'].append(user_details.first_name)
		return final_data
