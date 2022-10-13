from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist
import requests
import json
from web.views import get_credentials
from datetime import timedelta

class Command(BaseCommand):
    def handle(self, *args, **options):
        selection_discussions = SelectionDiscussion.objects.all()
        credentials = get_credentials()
        with open('gcal_refresh_log.txt','w') as f:
            if selection_discussions:
                latest_discussion = selection_discussions.latest('updated_at')
                channel_expiry = latest_discussion.channel_expiry
                resource_id = latest_discussion.resource_id
                channel_id = latest_discussion.channel_id
                now = datetime.datetime.utcnow()+timedelta(hours=5,minutes=30)
                difference = channel_expiry - now
                if True:
                    stop_resp = self.stop_existing_channels(credentials, latest_discussion)
                    f.write('Successfully stopped notifications')
                    f.write(str(stop_resp.text))
                    new_channel_resp = self.refresh_channel(now, credentials)
                    f.write('successfully registered web hook ')
                    f.write(str(new_channel_resp.text))
                else:
                    f.write('Channel will expire after %s days' %str(difference.days))

    def refresh_channel(self, now, credentials):
        calender_id = 'discussions@evidyaloka.org'
        new_channel_id = 'google_webhook_notification_'+now.strftime('%d_%m_%Y_%H_%M')
        expiry_time = now+timedelta(days=30)
        expiry_ts = int((expiry_time - datetime.datetime(1970,1,1)).total_seconds())
        access_token = credentials.access_token
        url = 'https://www.googleapis.com/calendar/v3/calendars/'+calender_id+'/events/watch'
        headers = {'content-type': 'application/json', 'Authorization' : 'Bearer '+ access_token}
        data = {'id': new_channel_id, "type": "web_hook", "address": "https://dev.evidyaloka.org/gcalender_api_callback/"}
        refresh_resp = requests.post(url, data=json.dumps(data), headers=headers)
        return refresh_resp


    def stop_existing_channels(self, credentials, latest_discussion):
        access_token = credentials.access_token
        url = 'https://www.googleapis.com/calendar/v3/channels/stop'
        headers = {'content-type': 'application/json', 'Authorization' : 'Bearer '+ access_token}
        resource_id = latest_discussion.resource_id
        channel_id = latest_discussion.channel_id
        data = {'id':channel_id, 'resourceId':resource_id}
        stop_resp = requests.post(url, data=json.dumps(data), headers=headers)
        return stop_resp
