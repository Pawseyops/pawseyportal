#!/bin/python
import httplib
import urllib
import json
import ConfigParser
import os

# Obtain User Details from Pawsey Portal for inserting into LDAP. Includes user initial password

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

def userDetails(authParams, personId):
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
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

# Configuration
config = ConfigParser.RawConfigParser()
config.read(os.path.expanduser('~/.pawseyportal'))

username = config.get('auth','username')
password = config.get('auth','password')

servername = config.get('portal','servername')
url = config.get('portal','url')

params = {'username': username, 'password': password}

user = userDetails(params, 6583)

print ("User Name: %s %s" % (user['givenName'],user['sn']))
print ("Phone Number: %s" % (user['telephoneNumber']))
print ("Email Address: %s" % (user['mail']))
print ("Uid: %s" % (user['uid']))
print ("Uid Number: %s" % (user['uidNumber']))
print ("Gid Number: %s" % (user['gidNumber']))
