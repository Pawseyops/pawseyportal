"""pawseyportal URL Configuration

"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as authViews
from ajax_select import urls as ajax_select_urls

urlpatterns = [
    url(r'^portal/', include('pawseyportal.userportal.urls', namespace="portal")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', authViews.login, { 'template_name': 'userportal/login.html' }, name='login'),
    url(r'^logout/$', authViews.logout, { 'next_page': 'portal:index', 'template_name': 'userportal/logged_out.html' } , name='logout'),
    url(r'^ajax_select/', include(ajax_select_urls)),
]
