from django.conf.urls import patterns
from django.conf.urls import url
from .views import *

urlpatterns = [
   
    url(r'^api/v1/signin?$',signin_mobile,name='signin_mobile'),
    url(r'^api/v1/verifyOtp?$',verify_otp,name='verifyOtp'),
    url(r'^api/v1/guardian/sendotp?$', send_otp_guardian,name='send_otp_guardian'),
    url(r'^api/v1/guardian/register?$',guardian_registration_api,name='guardian_registration_api'),
    url(r'^api/v1/guardian/students?$',guardian_students,name='guardian_students'),

    url(r'^api/v1/schoolofferings?$',digital_school_offerings,name='ds_offerings'),
    url(r'^api/v1/offering?$',generic_offering,name='generic_offerings'),
    url(r'^api/v1/ping?$',student_ping_api,name='ping'),

    url(r'^api/v1/schedulecourse?$',schedulecourse,name='schedulecourse'),
    url(r'^api/v1/session?$',student_session,name='student_session'),
    url(r'^api/v1/contentdetails?$',contentdetails,name='contentdetails'),
    url(r'^api/v1/session/detail?$',student_session_detail,name='student_session_detail'),
    url(r'^api/v1/session/attendance?$',update_attendance,name='attendance'),
    url(r'^api/v1/documents?$', upload_student_document,name='upload_student_document'),
    url(r'^api/v1/doubt?$', student_doubt_api,name='student_doubt_api'),
    url(r'^api/v1/subjects?$', get_subject_progress,name='get_subject_progress'),
    url(r'^api/v1/subjects/detail?$',get_subject_detail,name='get_subject_detail'),
    url(r'^api/v1/content/viewstatus?$',update_content_view_status,name='update_content_view_status'),
    url(r'^api/v1/doubt/detail?$', get_doubt_detail,name='get_doubt_detail'),
    url(r'^api/v1/logout?$', student_logout,name='student_logout'),
    url(r'^api/v1/subjects/add?$', student_subject_add,name='student_subject_add'),
    url(r'^api/v1/session/rate?$', student_session_rate,name='student_session_rate'),
    url(r'^api/v1/missedsessions?$', student_missed_session,name='student_missed_session'),
    url(r'^api/v1/pincodes?$', student_get_pincodes,name='student_get_pincodes'),
    url(r'^api/v1/languages?$', student_get_languages,name='student_get_languages'),
    url(r'^api/v1/courseproviders?$', student_get_courseproviders, name='student_get_courseproviders'),
    url(r'^api/v1/explore/schools/detail?$', school_explore_detail_api,name='school_explore_detail_api'),
    url(r'^api/v1/guadian/update?$', student_guardian_update_details, name='student_guardian_update'),
    url(r'^api/v1/guardian/enroll_student?$', guardian_enroll_student, name='guardian_enroll_student'),
    url(r'^api/v1/grades?$', student_get_grade, name='student_get_grade'),
    url(r'^api/v1/updatetoken?$', guardian_update_push_token, name='guardian_update_push_token'),
    url(r'^api/v1/testpush?$', test_push_api, name='test_push_api'),
    url(r'^api/v1/testredis?$', test_redis, name='test_redis'),

    url(r'^api/v1/subtopic/session?$', student_get_session_detail, name='student_get_session_detail'),
    url(r'^api/v1/content/update-download-status?$', update_content_download_status, name='update_content_download_status'),
    url(r'^api/v1/quiz/getQuestions?$',student_get_quiz, name='student_get_quiz'),
    url(r'^api/v1/quiz/getQuestionSet?$',student_get_question_set, name='student_get_question_set'),
    url(r'^api/v1/quiz/updateSummary?$',student_update_quiz_summary, name='student_update_quiz_summary'),
    ]
