"""pawseyportal URL Configuration

"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import authViews

urlpatterns = [
    url(r'^portal/', include('pawseyportal.userportal.urls', namespace="portal")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', authViews.login, name='login'),
    url(r'^logout/$', authViews.logout, { 'next_page': 'portal:index' } , name='logout'),
]
