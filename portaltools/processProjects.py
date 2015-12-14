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
    listAllocationsUrl = url + "/portal/api/listAllocations/" + system
    conn.request("POST", listAllocationsUrl, params, headers)
    response = conn.getresponse()
    data = response.read()

    # Unencode and return
    return json.loads(data)

# Check if an allocation is completely active on a system and activate/repair if not
def activateAllocation(allocation):
    return

# Get a list of users on a project that owns an allocation
def getProjectUsers(allocation):
    return

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

#user = userDetails(params,2)

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
    if o in ("s","system"):
        system = a
    elif o in ("h","help"):
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
    activateAllocation(allocation)

    # get list of project users for allocation
    users = []
    users = getProjectUsers(allocation)

    if users == None:
        print "This project has no users. How can that be?"
        continue
    else:
        # Process users for allocation to make sure they are activated and set up for the current allocation
        for user in users:
            activateAccount(user, allocation)

