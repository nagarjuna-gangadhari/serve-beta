from pyfcm import FCMNotification
import os

def getPushNotificationKey():
    firebaseKey = os.getenv('EVD_FIREBASE_FCM_KEY')
    return firebaseKey

FCM_API_KEY = getPushNotificationKey()

try:
    pushService = FCMNotification(api_key=FCM_API_KEY)
except Exception as e:
    print("Push service creation ",e)


def sendNotificationToSingleDevice(pushToken,title,body,dataPayload):
   try:
       registration_id = pushToken
       message_title = title
       message_body = body
       data_message = dataPayload
       result = pushService.notify_single_device(registration_id=registration_id, message_title=message_title,message_body=message_body,data_message=data_message)
       print("result", result)
       return result

   except Exception as e:
       print("Exception", e)
       return None

def sendNotificationToMultipleDevices(pushTokens,title,body,dataPayload):
   try:
       message_title = title
       message_body = body
       data_message = dataPayload
       result = pushService.notify_multiple_devices(registration_ids=pushTokens, message_title=message_title,message_body=message_body,data_message=data_message)
       if result:
           sttausSuccess = result["success"]
           if sttausSuccess > 0:
               return (True,result)
           else:
               return (False, result)

       return (False, None)
   except Exception as e:
       print("Exception", e)