from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponseRedirect
from models import *
from forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.exceptions import PermissionDenied
import account_services

import datetime

PROCESSED_PARTICIPANT_SESSION_KEY = 'PROCESSED_PARTICIPANT'

# The API is meant to not require the csrf headers. Do no decorate any of the user facing non api views with this.
from django.views.decorators.csrf import csrf_exempt

# Index, Currently a placeholder
def indexView(request):
    raise Http404("No view requested")

# Get user details for user creation
def userDetailsRequest(request, email_hash):
    # Note that this relies on the hash being unique in the database, if it isn't for some reason we still want to throw the error.
    try:
        person = Person.objects.get(accountEmailHash=email_hash)
    except Person.DoesNotExist:
        return render(request, 'userportal/invalid_hash.html', {})

    try:
        person_account = person.personAccount
    except PersonAccount.DoesNotExist:
        person_account = PersonAccount(person=person) 

    if request.method == 'POST':
        form = PersonAccountForm(request.POST)
        if form.is_valid():
            person.firstName = form.cleaned_data.get('firstName')
            person.surname = form.cleaned_data.get('lastName')
            person.institution_id = form.cleaned_data.get('institution').id
            person.mobinePhone = form.cleaned_data.get('mobilePhone')
            person.phone = form.cleaned_data.get('phone')
            person_account.password_hash = account_services.hash_password(form.cleaned_data.get('password1'))

            account_services.save_account_details(person)
            request.session[PROCESSED_PARTICIPANT_SESSION_KEY] = email_hash
            return HttpResponseRedirect(settings.MYURL + '/portal/account-thanks/')
    else:
        form = PersonAccountForm(initial = {'firstName': person.firstName, 'lastName': person.surname})

    return render(request, 'userportal/account_request.html', {
        'form': form, 'person_email': person.institutionEmail })

# Display a summary of account details when they have submitted them
def userDetailsThanks(request):
    person_email_hash = None
    try:
        person_email_hash = request.session.get(PROCESSED_PARTICIPANT_SESSION_KEY,None)
    except:
        pass
    
    #now remove the session key if it existed
    if person_email_hash is not None:
        del request.session[PROCESSED_PARTICIPANT_SESSION_KEY]
    
    persondetails = None
    error = None
    if person_email_hash is None:
        error = "Unable to retrieve person by hash: no hash provided."
    else:
        try:
            person = Person.objects.get(accountEmailHash = person_email_hash)
            #erase the email hash - we don't need it anymore
            person.accountEmailHash = None
            person.save()
            
            ppt_account = person.personAccount
            persondetails = []
            persondetails.append( ("First Name", person.firstName) )
            persondetails.append( ("Last Name", person.surname) )
            persondetails.append( ("Institution Email", person.institutionEmail) )
            persondetails.append( ("Alternative Email", person.preferredEmail) )
            persondetails.append( ("Phone Number", person.phone) )
            persondetails.append( ("Mobile Phone Number", person.mobilePhone) )
            persondetails.append( ("Username (pending)", ppt_account.uid) )
            persondetails.append( ("Institution", person.institution.name) )

        except Person.DoesNotExist:
            error = "Unable to retrieve person by hash: %s" % (str(person_email_hash))
    return render(request, 'userportal/account_details_thanks.html', {"persondetails": persondetails, "error":error})

# Authentication for API views. Make sure we are authenticated, or if not see if we can authenticate with POST variables. This is to keep from needing cookie management in command line tools.
def portalAuth(request):
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
    return user

# API view List All Currently Active Allocations
@csrf_exempt
def listAllocationsView(request):
    user = portalAuth(request)
    if user.is_active and user.is_superuser:
        response_data = {}
        for allocation in Allocation.objects.filter(start__lte=datetime.date.today()).filter(end__gte=datetime.date.today()).exclude(suspend='True'):
            alloc = {}
            alloc['name'] = allocation.name
            alloc['project'] = allocation.project.title
            alloc['priorityArea'] = allocation.priorityArea.name
            alloc['serviceunits'] = allocation.serviceunits
            alloc['service'] = allocation.service.name
            alloc['projectCode'] = allocation.project.code
            alloc['projectId'] = allocation.project.id

            response_data[allocation.id]=alloc
        return JsonResponse(response_data)
    else:
            raise PermissionDenied

# API view List all users in a Project
@csrf_exempt
def listPeopleView(request):
    user = portalAuth(request)

    if 'projectId' not in request.POST:
        raise Http404("No project requested")
    else:    
        projectId = request.POST["projectId"]

    if user.is_active and user.is_superuser:
        response_data = {}
        proj = Project.objects.get(id=projectId)
        projectPeople = proj.people.all()
        for person in projectPeople:
            response_data[person.id]=person.personAccount.uid
        return JsonResponse(response_data)
    else:
        raise PermissionDenied
            

# API view Get Person details for creating account
@csrf_exempt
def userDetailView(request):
    user = portalAuth(request)
    if 'person' not in request.POST:
        raise Http404("No person requested")
    else:    
        personId = request.POST["person"]
    
    if user.is_active and user.is_superuser:
        response_data = {}
        person = Person.objects.get(id=personId)
        response_data['id'] = personId
        response_data['givenName'] = person.firstName
        response_data['sn'] = person.surname
        response_data['uid'] = person.personAccount.uid
        response_data['uidNumber'] = person.personAccount.uidNumber
        response_data['gidNumber'] = person.personAccount.gidNumber
        response_data['mail'] = person.institutionEmail
        response_data['userPassword'] = person.personAccount.passwordHash
        response_data['telephoneNumber'] = person.phone
        response_data['institution'] = person.institution.name
        
        return JsonResponse(response_data)
    else:
        raise PermissionDenied
    
