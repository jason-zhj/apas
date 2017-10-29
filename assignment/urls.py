from django.conf.urls import patterns, url
from appglobal.views import file_download,simple_clear_submissions
from question.views import question_submission_grade,task_submission_plagiarism_check,question_submission_view_student
from .views import *
from .models import Assignment,AssignmentSubmission,AssignmentQuestionSubmission

urlpatterns = patterns('assignment.views',
    url(r'^list-staff/$', AssignmentListView.as_view(),name='assignment_list'),
    url(r'^list-student/$', AssignmentListView.as_view(),name='assignment_list_student'),
    url(r'^create/$', 'assignment_edit',name='assignment_create'),
    url(r'^(?P<assignment_slug>[-\w]*)/edit/$', 'assignment_edit',name='assignment_edit'),
    url(r'^clearsubmission/$', simple_clear_submissions,{
        "model_class":Assignment
    },name='assignment_clear_submission'),
    url(r'^delete-selected/$', AssignmentDeleteSelectedView.as_view(),name='assignment_delete_selected'),

    url(r'^question-submission/(?P<object_id>\d+)/view/$',question_submission_view_student,name='assignment_assignment_question_submission_view'),
    url(r'^(?P<object_slug>[-\w]*)/submission/plagiarism/$', task_submission_plagiarism_check,{
        "model_class":Assignment
    },name='assignment_submission_plagiarism_check'),

    url(r'^submission/list/$', AssignmentSubmissionStudentListView.as_view(),name='assignment_submission_list_student'),
    url(r'^(?P<assignment_slug>[-\w]*)/submission/list/$', AssignmentSubmissionStaffListView.as_view(),name='assignment_submission_list_staff'),
    url(r'^(?P<object_slug>[-\w]*)/submission/grade/$', question_submission_grade,{
        "model_class":Assignment,"redirect_to":'assignment_submission_list_staff'
    },name='assignment_submission_grade'),
    url(r'^(?P<object_slug>[-\w]*)/submission/create/$', "assignment_submission_create",name='assignment_submission_create_student'),
    url(r'^submission/(?P<assignment_submission_id>\d+)/view/$', AssignmentQuestionSubmissionListView.as_view(),name='assignment_submission_view'),
    url(r'^(?P<assignment_slug>[-\w]*)/submission/(?P<assignment_submission_id>\d+)/report/$', 'assignment_submission_report',name='assignment_submission_report'),
    url(r'^submission/delete-selected/$', AssignmentSubmissionDeleteSelectedView.as_view(),name='assignment_submission_delete_selected'),

#----------------------------------for finding strange code---------------------------------------------
    url(r'^(?P<object_slug>[-\w]*)/submission/find-strange-code/$', "assignment_submission_find_strange_code",
        name='assignment_submission_find_strange_code'),
    url(r'^download/(?P<file_name>.+)$', file_download,{"type":"assignment"},name='assignment_file_download'),
    url(r'^(?P<object_slug>[-\w]*)/submission/validate-requirement/$', "assignment_submission_validate_requirement",
        name='assignment_submission_validate_requirement'),
#---------------------------------for creating result data sheet--------------------------------------------
    url(r'^(?P<object_slug>[-\w]*)/submission/create-result-sheet/$', "assignment_submission_create_result_sheet",
        name='assignment_submission_create_result_sheet'),

)