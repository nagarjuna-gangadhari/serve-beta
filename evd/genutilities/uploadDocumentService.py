
from web.models import *
import genutilities.views as genUtility
import genutilities.docStorageUtility as docStorageService
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def sendErrorResponse(request, errorConstant):
    return genUtility.getStandardErrorResponse(request, errorConstant)


def getSuccessResponseStatus(request, responseData):
    return genUtility.getSuccessApiResponse(request, responseData)

def upload_user_document_s3(request,userType,guardianObj,cldFolderName,userIdPrefix,returnType):
    try:
        intFormat = request.GET.get('format')  # png,jpg,pdf,doc,docx,jpeg
        intDocType = request.GET.get('doc_type')  # school_logo,school_banner,student_doubt etc

        if userType == "teacher":
            intFormat,intDocType = "1","5"

        fileFormat = None
        docType = None
        objectType = None
        if intFormat and intDocType:
            fileFormat = docStorageService.kSTORAGE_SUPPORTED_FILE_FORMATS.get(str(intFormat))
            fileTypeObj = docStorageService.kSTORAGE_SUPPORTED_FILE_TYPES.get(str(intDocType))
            docType = fileTypeObj.get('type')
            objectType = fileTypeObj.get('objectName')

            if fileFormat and docType:
                pass
            else:
                if returnType == "obj":
                    return None
                return sendErrorResponse(request, "kInvalidRequest")
        else:
            if returnType == "obj":
                return None
            return sendErrorResponse(request, "kMissingReqFields")

        userIdStr = ""
        userObj = None
        if userType == "guardian":
            if userIdPrefix:
                userIdStr = userIdPrefix
            else:
                userIdStr = "gu" + str(guardianObj.id)
        else:
            userIdStr = "pu"+str(request.user.id)
            userObj = request.user


        randomString = genUtility.getRandomString()
        localDocName = userIdStr + randomString + docType + "." + fileFormat

        tempStorage = FileSystemStorage(location=settings.TEMPORARY_DOCUMENT_STOREAGE_PATH)
        fileData = request.FILES['file']
        if fileData is None:
            if returnType == "obj":
                return None
            return sendErrorResponse(request, "kMissingReqFields")

        fStatus = tempStorage.save(localDocName, fileData)

        cloudFolderName = cldFolderName
        filePathToBeuploaded = settings.TEMPORARY_DOCUMENT_STOREAGE_PATH + "/" + localDocName
        permissionType = docStorageService.kSTORAGE_SUPPORTED_PERMISSION_PUBLIC
        uploadedUrl = docStorageService.uploadDocument(cloudFolderName, filePathToBeuploaded, localDocName,
                                                       permissionType)
        if uploadedUrl:
            tempStorage.delete(localDocName)
            try:
                # create document object and save
                docRecord = UserDocument.objects.create(
                    file_name=localDocName,
                    url=uploadedUrl,
                    doc_type=docType,
                    source="s3",
                    doc_format=fileFormat,
                    status=True,
                    belongs_to_object=objectType,
                    created_by=userObj,
                    updated_by=userObj
                )
                docRecord.save()
                dataObj = {
                    "id": docRecord.id,
                    "message": "Document uploaded successfully"
                }
                if returnType == "obj":
                    return docRecord
                return getSuccessResponseStatus(request, dataObj)
            except:
                if returnType == "obj":
                    return None
                return sendErrorResponse(request, "kFileUploadFailed")
        else:
            tempStorage.delete(localDocName)
            return sendErrorResponse(request, "kFileUploadFailed")
    except Exception as e:
        print("upload_student_document", e)
        if returnType == "obj":
            return None
        return sendErrorResponse(request, "kInvalidRequest")