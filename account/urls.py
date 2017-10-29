from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('account',
    url(r'^login/$', 'views.user_login',name='user_login'),
    url(r'^logout/$', 'views.user_logout',name='user_logout'),
    url(r'^changepwd/$', 'views.change_password',name='change_password'),
    url(r'^resetpwd/(?P<object_id>\d+)/$', 'views.reset_password',name='reset_password'),
    url(r'^group/list$',StudentGroupListView.as_view(),name='student_group_list'),
    url(r'^group/(?P<group_id>\d+)/member/list$',"views.group_member_list",
        name='group_member_list'),
    url(r'^group/create$',StudentGroupEditView.as_view(),name='student_group_create'),
    url(r'^group/(?P<object_id>\d+)/edit$', StudentGroupEditView.as_view(),name='student_group_edit'),
    url(r'^group/delete-selected/$', StudentGroupDeleteSelectedView.as_view(),name='student_group_delete_selected'),


    url(r'^student/list$',StudentUserProfileListView.as_view(),name='student_user_profile_list'),
    url(r'^student/create$',StudentUserProfileEditView.as_view(),name='user_create'),
    url(r'^student/(?P<user_id>\d+)$',"views.profile_edit" ,name='student_user_profile_create'),
    url(r'^student/(?P<user_id>\d+)/edit$',"views.profile_edit",
        name='student_user_profile_edit'),
    url(r'^student/delete-selected/$', StudentUserProfileDeleteSelectedView.as_view(),name='student_user_profile_delete_selected'),
    url(r'^student/import/$' ,'views.data_import',{'type':'user'},name='student_user_profile_import'),
   # url(r'^group/import/$','views.data_import', {'type':'group'},name='user_group_import'),
)