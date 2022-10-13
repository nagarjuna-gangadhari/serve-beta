
import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from django.conf import settings


kSTORAGE_SUPPORTED_FILE_FORMATS = {
    "1":"png",
    "2":"jpg"
}

kSTORAGE_SUPPORTED_FILE_TYPES = {
    "1":{"objectName":"DigitalSchool","type":"school_logo"},
    "2":{"objectName":"DigitalSchool","type":"school_banner"},
    "3":{"objectName":"UserProfile","type":"user_profile"},
    "4":{"objectName":"Doubt_Thread","type":"student_doubt"},
    "5":{"objectName":"Doubt_Thread","type":"student_doubt_response"},
    "6":{"objectName":"student","type":"student_profile_pic"}
}


kSTORAGE_SUPPORTED_PERMISSION_PUBLIC = "public"
kSTORAGE_SUPPORTED_PERMISSION_PRIVATE = "private"

def getDocStorageServiceCredentials():
    serviceName = os.getenv('STORAGE_ACCESS_KEY_ID')
    serviceKey = os.environ.get('STORAGE_SECRET_ACCESS_KEY')
    bucketName = os.environ.get('STORAGE_BUCKET_NAME')
    region = os.environ.get('STORAGE_BUCKET_REGION')
    if serviceName and serviceKey and bucketName and region:
        return {"serviceKey":serviceKey,"serviceName":serviceName,"bucketName":bucketName,"region":region}
    else:
        return None


def s3Examples():
    credentials = getDocStorageServiceCredentials()
    serviceName = credentials.get('serviceName')
    serviceKey = credentials.get('serviceKey')
    region = credentials.get('region')
    storage_config = Config(
        region_name=region
    )
    s3 = boto3.client('s3',aws_access_key_id=serviceName,aws_secret_access_key=serviceKey,config=storage_config)
    response = s3.list_buckets()

def uploadDocument(folderName,filePath,fileName,permissionType):
    permissionData = {'ACL': 'public-read'}
    if permissionType != kSTORAGE_SUPPORTED_PERMISSION_PUBLIC:
        permissionData = None

    credentials = getDocStorageServiceCredentials()
    if credentials is None:
        print("Storage credentials are not set.")
        return None
    serviceName = credentials.get('serviceName')
    serviceKey = credentials.get('serviceKey')
    bucketName = credentials.get('bucketName')
    region = credentials.get('region')
    storage_config = Config(
        region_name=region
    )

    try:
        s3_client = boto3.client('s3', aws_access_key_id=serviceName, aws_secret_access_key=serviceKey,
                                 config=storage_config)
        s3FilePath = folderName+"/"+fileName
        response = s3_client.upload_file(filePath, bucketName, folderName+"/"+fileName,ExtraArgs=permissionData)
        return "https://s3."+region+".amazonaws.com/"+bucketName+"/"+s3FilePath

    except ClientError as e:
        print("ClientError ",e)
        return None
    except Exception as e:
        print("ClientError ", e)
        return None











