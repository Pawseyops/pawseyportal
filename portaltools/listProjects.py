#!/bin/python
import httplib
import urllib
import json
import ConfigParser
import os

# Preliminary Test Script for framework of command line tools to access Pawsey Portal

def listAllocations(authParams):
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Use httplib to request the data
    conn = httplib.HTTPSConnection(servername)
    listAllocationsUrl=url + "/portal/api/listAllocations/"
    conn.request("POST", listAllocationsUrl, authParams, headers)
    response = conn.getresponse()
    data = response.read()

    # Unencode and return
    return json.loads(data)

# Configuration
config = ConfigParser.RawConfigParser()
config.read(os.path.expanduser('~/.pawseyportal'))

username = config.get('auth','username')
password = config.get('auth','password')

servername = config.get('portal','servername')
url = config.get('portal','url')

# Encode  Credentials for POSTing
params = urllib.urlencode({'username': username, 'password': password})

allocations = listAllocations(params)

for allId ,allocation in allocations.iteritems():
    print("Project Name: %s" % (allocation["project"]))
    print("Project Code: %s" % (allocation["projectCode"]))
    print("Allocation name: %s" % (allocation["name"]))
    print("Pawsey Service: %s" % (allocation["service"]))
    print("Priority Area: %s" % (allocation["priorityArea"]))
    print("Service Units: %s" % (allocation["serviceunits"]))
    print("")


