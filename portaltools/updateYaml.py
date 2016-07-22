#!/bin/python
import httplib
import urllib
import ConfigParser
import os
import sys
import getopt
from datetime import date

def getYaml(authParams):

    # Encode  Credentials and other parameters for POSTing
    params = urllib.urlencode(authParams)
    
    # Use httplib to request the data
    conn = httplib.HTTPSConnection(servername)
    YamlUrl=url + "/portal/api/yamlAllocation//"
    conn.request("POST", YamlUrl, params, headers)
    response = conn.getresponse()
    data = response.read()

    # return
    return data

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
    opts, args = getopt.getopt(sys.argv[1:], "h:", ["help", ])
except getopt.GetoptError as err:
    # print help information and exit:
    print(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

print getYaml(authParams)
