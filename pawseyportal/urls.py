"""pawseyportal URL Configuration

"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as authViews

urlpatterns = [
    url(r'^portal/', include('pawseyportal.userportal.urls', namespace="portal")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', authViews.login, name='login', template_name='userportal/login.html'),
    url(r'^logout/$', authViews.logout, { 'next_page': 'portal:index' } , name='logout', template_name='userportal/logged_out.html'),
]
