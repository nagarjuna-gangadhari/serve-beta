from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^authenticate_user/$', views.authenticate_user, name='authenticate_user'),
    url(r'^get_upcom_sess/$', views.get_upcom_sess, name='get_upcom_sess'),
    url(r'^save_session_status/$', views.save_session_status, name='save_session_status'),
    url(r'^fcm_key', views.fcm_update, name = 'fcm_update'),
    url(r'^get_user_sessions', views.get_user_sessions, name = 'get_user_sessions'),
    url(r'^get_user_meta', views.get_user_meta, name = 'get_user_meta'),
    url(r'^get_avalilable_tsd_slots', views.get_avalilable_tsd_slots, name = 'get_avalilable_tsd_slots'),
    url(r'^save_selfevalinfo', views.save_selfevalinfo, name = 'save_selfevalinfo'),
    url(r'^send_mail', views.send_mail_api, name = 'send_mail_api'),

    url(r'^student/search/?$', views.student_search, name = 'student_search'),
    url(r'^student/fcm/?$', views.student_fcm_update, name = 'student_fcm_update'),
    url(r'^student/activation/?$', views.student_activation, name = 'student_activate'),
    url(r'^student/session/?$',views.student_session,name='student_session'),
    url(r'^reference_channel/?$',views.reference_channel,name='reference_channel'),
    url(r'student/send/otp/?$', views.send_otp, name='send_otp'),
    # Newly added functions and urls(duplicate)
    url(r'^get_user_sessions_new', views.get_user_sessions_duplicate, name = 'get_user_sessions_new'),
    url(r'^student/session_new/?$',views.student_session_duplicate,name='student_session_new'),
    url(r'^save_session_assignment/?$', views.save_session_assignment, name='save_session_assignment'),
    url(r'^delete_session_assignment/?$', views.delete_session_assignment_by_id, name='delete_session_assignment'),
    url(r'^upload_assignment/?$', views.upload_assignment, name='upload_assignment'),
    url(r'delete_upload_assignment/(?P<uploaded_id>\d+)?/?$', views.delete_student_uploaded_assignment, name='delete_upload_assignment'),
    url(r'get_uploaded_assignment/(?P<session_assignment_id>\d+)?/?$', views.get_uploaded_assignment, name='get_uploaded_assignment'),
    url(r'offering/assignments/?$', views.get_assignments_for_offering, name='get_assignments_for_offering'),
    url(r'students/offering/?$', views.get_students_for_offering, name='get_students_for_offering'),
    url(r'student/uploaded/assignments/?$', views.get_uploaded_assignment_for_student, name='get_uploaded_assignment_for_student'),
    url(r'update_status_and_remarks/?$', views.update_status_and_remarks, name='update_status_and_remarks'),
    url(r'approved_videos/?$', views.approved_videos, name='approved_videos'),
    url(r'session/status/?$', views.update_session_status, name='update_session_status'),
    url(r'student/attendance/?$', views.update_student_attendance, name='update_student_attendance'),
    url(r'get_offering_details/?$', views.get_offering_details, name='get_offering_details'),
    url(r'get_videos_for_subject/?$', views.get_videos_for_subject, name='get_videos_for_subject'),
    url(r'get_all_assignments_for_month/?$', views.get_all_assignments_for_month, name='get_all_assignments_for_month'),
    url(r'student/current_month/session/?$', views.student_current_month_session, name='student_current_month_session'),
    url(r'^get_session_details_new/?$', views.get_session_details_duplicate, name='get_session_details_new'),
    url(r'student/uploaded/assignments/status?$', views.get_uploaded_assignment_for_student_status, name='get_uploaded_assignment_for_student_status'),

]
