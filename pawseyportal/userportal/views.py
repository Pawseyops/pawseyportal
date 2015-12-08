from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate

import datetime

# List All Currently Active Allocations
def listAllocationsView(request):
    #TODO: if authenticated or post variables exist for django.contrib.auth.authenticate authentication (to keep the python client simple for the heavy lifting of Pawsey account activation).
    
    # Make sure we are authenticated, or if not see if we can authenticate with POST variables.
    user = request.user
    if user is  None:
        #check POST Variables or return
        raise PermissionDenied
    else:
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
