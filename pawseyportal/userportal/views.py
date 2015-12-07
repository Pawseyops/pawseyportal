from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required

# List All Currently Active Allocations
def listAllocationsView(request):
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
