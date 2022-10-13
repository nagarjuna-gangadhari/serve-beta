from django.conf.urls import url
from .views import *
urlpatterns = [
    url(r'^(?P<question_id>\d+)?/?$', view_or_list_Questions),
    url(r'^add/?$',addQuestion),
    url(r'^question_instruction/?$',question_instruction),
    url(r'^delete/(?P<question_id>\d+)?/?$',deleteQuestion),
    url(r'^update/(?P<question_id>\d+)?/?$',updateQuestion),
    url(r'^assesment/?$',getAssesment,name="getAssesment"),
    url(r'^get_centers_by_state/?$',get_centers_by_state,name="get_centers_by_state"),
    url(r'^get_offering_by_center/?$',get_offering_by_center,name="get_offering_by_center"),
    url(r'^get_topic_and_sub_topic/?$',get_topic_and_sub_topic,name="get_topic_and_sub_topic"),
    url(r'^get_question_list/?$',get_question_list,name="get_question_list"),
    url(r'^(?P<type_name>\w+)?/?$',getAddQuestionDropdowns),
    url(r'^approve/reject/?$', approve_reject_question, name='approve_reject_question'),
    url(r'^upload/quiz/view?$',bulk_upload_quiz_view,name="bulk_upload_quiz"),
    url(r'^upload/quiz/action?$',bulk_upload_quiz_action,name="bulk_upload_quiz"),
    # url(r'^approve_question/?$', approve_question),
    # url(r'^reject_question/?$', reject_question)

]