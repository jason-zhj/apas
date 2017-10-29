from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from .settings import MEDIA_ROOT,MEDIA_URL

admin.autodiscover()

urlpatterns = patterns('',
    # accounts
    url(r'^accounts/', include('account.urls')),
    # question
    url(r'^question/', include('question.urls')),
    # assignment
    url(r'^assignment/', include('assignment.urls')),
    # onlinetest
    url(r'^onlinetest/', include('onlinetest.urls')),
    # global
    url(r'^', include('appglobal.urls')),
    # admin
    url(r'^admin/', include(admin.site.urls)),
)+ static(MEDIA_URL, document_root=MEDIA_ROOT) # serve files uploaded by user


# urlpatterns = patterns('',
#     # global
#     url(r'^$', 'apas_app.views.index',name='index'),
#     url(r'^home/$', 'apas_app.views.home',name='home'),
#     url(r'^about/$', 'apas_app.views.static_page',{'template':'flatpage/about.html'}),
#     url(r'^help/$', 'apas_app.views.static_page',{'template':'flatpage/help.html'}),
#     # accounts
#     url(r'^accounts/login/$', 'apas_app.views.login',name='login'),
#     url(r'^accounts/logout/$', 'apas_app.views.logout',name='logout'),
#     # question
#     url(r'^question/list/$', 'apas_app.views.question_list',name='question_list'),
#     url(r'^question/(?P<questionid>\d+)/edit/$', 'apas_app.views.question_edit',name='question_edit'),
#     url(r'^question/(?P<questionid>\d+)/detail/$', 'apas_app.views.question_detail',name='question_detail'),
#     url(r'^question/(?P<questionid>\d+)/delete/$', 'apas_app.views.question_delete',name='question_delete'),

#     # testing view
#     url(r'^testing/$', 'apas_app.views.testing',name='testing'),
#     # django admin
#     url(r'^admin/', include(admin.site.urls)),
# )
