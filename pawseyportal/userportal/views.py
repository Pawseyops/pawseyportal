from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied

import datetime

# The API is meant to not require the csrf headers.
from django.views.decorators.csrf import csrf_exempt

# List All Currently Active Allocations
@csrf_exempt
def listAllocationsView(request):
    # Make sure we are authenticated, or if not see if we can authenticate with POST variables. This is to keep from needing cookie management in command line tools.
    user = request.user
    if not user.is_authenticated():
        #check POST Variables or return
        if request.method == 'POST':
            usernm = request.POST["username"]
            passwd = request.POST["password"]
            user = authenticate(username=usernm, password=passwd)
            if user is None:
                raise PermissionDenied
        else:
            raise PermissionDenied

    if user.is_active and user.is_superuser:
        response_data = {}
        for allocation in Allocation.objects.filter(start__lte=datetime.date.today()).filter(end__gte=datetime.date.today()).exclude(suspend='True'):
            alloc = {}
            alloc['name'] = allocation.name
            alloc['project'] = allocation.project.title
            alloc['priorityArea'] = allocation.priorityArea.name
            alloc['serviceunits'] = allocation.serviceunits
            alloc['service'] = allocation.service.name

            response_data[allocation.id]=alloc
        return JsonResponse(response_data)
    else:
            raise PermissionDenied
