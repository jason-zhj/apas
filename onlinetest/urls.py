from django.conf.urls import patterns, url
from appglobal.views import file_download,simple_clear_submissions
from .models import OnlineTest,OnlineTestSubmission
from question.views import question_submission_grade,task_submission_plagiarism_check
from .views import *

#_student means both staff and student can access

urlpatterns = patterns('onlinetest.views',
    #------------------urls for OnlineTest---------------------------------------
    url(r'^list/$', OnlineTestStaffListView.as_view(),name='online_test_list'),
    url(r'^list-student/$', OnlineTestStudentListView.as_view(),name='online_test_list_student'),
    url(r'^(?P<online_test_slug>[-\w]*)/edit/$', "online_test_edit",name='online_test_edit'),
    url(r'^create/$', "online_test_edit",name='online_test_create'),
    url(r'^delete-selected/$', OnlineTestDeleteSelectedView.as_view(),name='online_test_delete_selected'),

    url(r'^clear-submission/$', simple_clear_submissions,{
        "model_class":OnlineTest
    },name='online_test_clear_submission'),
    #------------------------urls for OnlineTestSubmission------------------------------------------
    # for students
    url(r'^(?P<object_slug>[-\w]*)/submission/create/$', "online_test_submission_create",name='online_test_submission_create'),
    url(r'^(?P<object_slug>[-\w]*)/submission/end/$', "onlinetest_submission_end",name='online_test_submission_end_student'),
    url(r'^submission/list-student/$', OnlineTestSubmissionStudentListView.as_view(),name='online_test_submission_list_student'),
    url(r'^submission/(?P<object_id>\d+)/view-student/$', OnlineTestQuestionSubmissionListView.as_view(),name='online_test_submission_view_student'),
    # for staff
    url(r'^(?P<object_slug>[-\w]*)/submission/list-staff/$',
        OnlineTestSubmissionStaffListView.as_view(),name='online_test_submission_list'),
    url(r'^(?P<object_slug>[-\w]*)/submission/grade/$',
        question_submission_grade,{
            'model_class':OnlineTest,'redirect_to':"online_test_submission_list"
        },name='online_test_submission_grade'),
    url(r'^(?P<object_slug>[-\w]*)/submission/plagiarism/$',
        task_submission_plagiarism_check,{
            "model_class":OnlineTest
        },name='online_test_submission_plagiarism_check'),
    url(r'^submission/delete-selected/$', OnlineTestSubmissionDeleteSelectedView.as_view(),name='online_test_submission_delete_selected'),
    #---------------------urls for finding strange code----------------------------
    url(r'^(?P<object_slug>[-\w]*)/submission/find-strange-code/$', "online_test_submission_find_strange_code",
        name='online_test_submission_find_strange_code'),
    url(r'^(?P<object_slug>[-\w]*)/submission/validate-requirement/$', "online_test_submission_validate_requirement",
        name='online_test_submission_validate_requirement'),
    #-------------------url for creating result-------------------------------------
    url(r'^(?P<object_slug>[-\w]*)/submission/create-result-sheet/$', "online_test_submission_create_result_sheet",
        name='online_test_submission_create_result_sheet'),
    url(r'^(?P<object_slug>[-\w]*)/submission/create-question-sheet/$', "online_test_submission_create_question_sheet",
        name='online_test_submission_create_question_sheet'),
    #---------------------urls for doing OnlineTest------------------------------------------
    url(r'^download/(?P<file_name>.+)$', file_download,{"type":"onlinetest"},name='onlinetest_file_download'),


)

