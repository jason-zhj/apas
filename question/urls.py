from django.conf.urls import patterns, url
from appglobal.views import file_download
from .views import *

urlpatterns = patterns('question.views',
    #------------------------Question--------------------------------
    url(r'^list/$', QuestionListView.as_view(),name='question_list'),
    url(r'^(?P<object_id>[-\w]*)/edit/$', QuestionEditView.as_view(),name='question_edit'),
    url(r'^create/$', QuestionEditView.as_view(),name='question_create'),
    url(r'^delete-selected/$', QuestionDeleteSelectedView.as_view(),name='question_delete_selected'),

    #----------------------------Question Topic--------------------------------
    url(r'^topic/list/$', QuestionTopicListView.as_view(),name='question_topic_list'),
    url(r'^topic/create/$', QuestionTopicEditView.as_view(),name='question_topic_create'),
    url(r'^topic/(?P<object_id>\d+)/edit/$', QuestionTopicEditView.as_view(),name='question_topic_edit'),
    url(r'^topic/delete-selected/$', QuestionTopicDeleteSelectedView.as_view(),name='question_topic_delete_selected'),

    #-------------------------QuestionPool---------------------------------------
    url(r'^pool/list/$', QuestionPoolListView.as_view(),name='question_pool_list'),
    url(r'^pool/(?P<object_id>[-\w]*)/edit/$', QuestionPoolEditView.as_view(),name='question_pool_edit'),
    url(r'^pool/create/$', QuestionPoolEditView.as_view(),name='question_pool_create'),
    url(r'^pool/delete-selected/$', QuestionPoolDeleteSelectedView.as_view(),name='question_pool_delete_selected'),

    #------------------------------------TestCaseSet--------------------------------------------
    url(r'^(?P<question_slug>[-\w]*)/test_case_set/list/$', TestCaseSetListView.as_view(),name='test_case_set_list'),
    url(r'^(?P<question_slug>[-\w]*)/test_case_set/create/$', 'test_case_set_edit',name='test_case_set_create'),
    url(r'^(?P<question_slug>[-\w]*)/test_case_set/delete-selected/$',TestCaseSetDeleteSelectedView.as_view(),name='test_case_set_delete_selected'),
    url(r'^test_case_set/(?P<object_id>\d+)/edit/$', 'test_case_set_edit',name='test_case_set_edit'),
    # create test case along with single test case
    url(r'^(?P<question_slug>[-\w]*)/test_case/create/$', 'test_case_create',name='test_case_create'),

    # ---------------------plagiarism checking------------------------------------
    url(r'^submission/plagiarism/(?P<question_slug>[-\w]*)/$', 'question_submission_plagiarism_check_result',name='question_submission_plagiarism_check'),

    #--------------------QuestionSubmission------------------------------------------
    url(r'^submission/(?P<object_id>\d+)/view/$', 'question_submission_view_student',name='question_submission_view_student'),
    url(r'^submission/find-strange-code/(?P<index>\d+)/$', 'strange_question_submission_detail',name='strange_question_submission_detail'),

    url(r'^download/(?P<file_name>.+)$', file_download,{"type":"question"},name='question_file_download'),

    #-------------------------test compilation(AJAX)------------------------------------
    url(r'test-compilation/$','test_compilation',name='test_compilation_student'),
)

