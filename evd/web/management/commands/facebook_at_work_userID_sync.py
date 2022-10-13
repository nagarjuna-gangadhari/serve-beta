from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist
import requests
import json
import requests

class Command(BaseCommand):
    def handle(self, *args, **options):
        #Facebook at work admin access token and community_id ( You can find it in company dashboard )
        community_id = '1715660651987686'
        admin_access_token = '1756803257874199|6qdzMuw3ZJDfICOTw5ICKy17o0c'
        limit = '10000'
        success_count = 0
        error_count = 0
        url = 'https://graph.facebook.com/'+community_id+'/members/?fields=id,name,email&access_token='+admin_access_token+'&limit='+limit
        #Get all members in fb at work.
        fb_response = requests.get(url)
        fb_response_data = fb_response.json()['data']
        with open('fbid_migrate_log.txt', 'w') as f:
            f.write('Date : '+ datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '\n')
            for ent in fb_response_data:
                user = User.objects.filter(email = ent['email'])
                if user:
                    userp = user[0].userprofile
                    userp.fbatwork_id = ent['id']
                    try:
                        userp.save()
                        success_count += 1
                    except Exception as e:
                        f.write('Error saving user : ' + str(userp.id) + '\n' )
                        f.write(e.message + '\n')
                        error_count += 1
                    print 'Updated user ' + str(userp.id) + ' : '+ ent['email'] + ' ---> ' + str(ent['id']) + '\n'
                else:
                    f.write('User with email not found : ' + ent['email'] + '\n')
                    error_count += 1
            f.write('Successfull Updations : ' + str(success_count) + '\n')
            f.write('Failed to update : ' + str(error_count) + '\n')
        print 'Successfull Updations : ' + str(success_count)
        print 'Failed to update : ' + str(error_count)
