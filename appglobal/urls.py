from django.conf.urls import patterns, url

urlpatterns = patterns('appglobal',
    url(r'^$', 'views.index',name='index'),
    url(r'^home/$', 'views.home',name='home'),
    url(r'^about/$', 'views.about',name='about'),
    url(r'^configuration/$', 'views.system_configuration',name='system_configuration'),
)