#!/bin/python
import httplib
import urllib
import json
import ConfigParser
import os
import sys
import getopt

#
# Obtain User Details from Pawsey Portal for inserting into LDAP. Includes user initial password
#

# Obtain list of Allocations
def listAllocations(authParams):
    
    # Use httplib to request the data
    conn = httplib.HTTPSConnection(servername)
    listAllocationsUrl=url + "/portal/api/listAllocations/"
    conn.request("POST", listAllocationsUrl, authParams, headers)
    response = conn.getresponse()
    data = response.read()

    # Unencode and return
    return json.loads(data)

# Obtain user details
def userDetails(authParams, personId):
    
    authParams['person'] = personId

    # Encode  Credentials and other parameters for POSTing
    params = urllib.urlencode(authParams)

    # Use httplib to request the data
    conn = httplib.HTTPSConnection(servername)
    userDetailUrl=url + "/portal/api/userDetail/"
    conn.request("POST", userDetailUrl, params, headers)
    response = conn.getresponse()
    data = response.read()

    # Unencode and return
    return json.loads(data)

# Get the allocations that are valid for this period on this system
def getAllocations(system, authParams):
    
    # Encode  Credentials and other parameters for POSTing
    params = urllib.urlencode(authParams)

    # Use httplib to request the data
    conn = httplib.HTTPSConnection(servername)
    listAllocationsUrl = url + "/portal/api/listAllocations/"
    conn.request("POST", listAllocationsUrl, params, headers)
    response = conn.getresponse()
    data = response.read()

    # Unencode
    allocations = json.loads(data)

    # Filter, if necessary and return
    if system:
        filteredAllocations = {}
        for key in allocations:
            if allocations[key]["service"] == system:
                filteredAllocations[key] = allocations[key]
        return filteredAllocations

    return allocations

# Check if an allocation is completely active on a system and activate/repair if not
def activateAllocation(allocation):
    print ("Work work work. I'm activating \"%s\" for \"%s\" with %s core hours on %s." % (allocation['name'], allocation['project'], allocation['serviceunits'], allocation['service']))
    return

# Get a list of users on a project that owns an allocation
def getProjectUsers(allocation):
    print ("Getting list of users for project \"%s\" which has ID %s" % (allocation['project'], allocation['projectId']))
    
    authParams['projectId'] = allocation['projectId']

    # Encode  Credentials and other parameters for POSTing
    params = urllib.urlencode(authParams)

    # Use httplib to request the data
    conn = httplib.HTTPSConnection(servername)
    listAllocationsUrl = url + "/portal/api/listPeople/"
    conn.request("POST", listAllocationsUrl, params, headers)
    response = conn.getresponse()
    data = response.read()

    # Unencode
    users = json.loads(data)

    return users

# Activate accounts on a system (in the future also trigger emails for creation if necessary)
def activateAccount(user, allocation):
    return

# Usage
def usage():
    print "Usage Instructions"
    exit(0)

# Configuration
config = ConfigParser.RawConfigParser()
config.read(os.path.expanduser('~/.pawseyportal'))

username = config.get('auth','username')
password = config.get('auth','password')
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

servername = config.get('portal','servername')
url = config.get('portal','url')

authParams = {'username': username, 'password': password}

# Get options
try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:", ["help", "system="])
except getopt.GetoptError as err:
    # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

system = ''

for opt, arg in opts:
    if opt in ("-s","-system"):
        system = arg
    elif opt in ("-h","-help"):
        usage()
        sys.exit(0)

# Get the current allocations for this system
allocations = getAllocations(system, authParams)

if allocations == None:
    print "No valid allocations. You may turn off the system and all go home."
    exit (0)

# Cycle through allocations
for allocation in allocations:
    # Check if allocation is already fully set up on system and set it up if not
    activateAllocation(allocations[allocation])

    # get list of project users for allocation
    users ={} 
    users = getProjectUsers(allocations[allocation])

    if users == None:
        print "This project has no users. How can that be?"
        continue
    else:
        # Process users for allocation to make sure they are activated and set up for the current allocation
        for user in users:
            activateAccount(users[user], allocations[allocation])

