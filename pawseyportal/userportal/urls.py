from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

# List of urls for the announce app. The login required wrappers are stated where we're using class based views.
urlpatterns = [
    url(r'^api/listAllocations/$', views.listAllocationsView, name='list_allocations'),
    url(r'^api/listPeople/$', views.listPeopleView, name='list_people'),
    url(r'^api/userDetail/$', views.userDetailView, name='user_detail'),
]
