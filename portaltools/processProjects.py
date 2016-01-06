#!/bin/python
import httplib
import urllib
import json
import ConfigParser
import os
import sys
import getopt
import ldap
import ldap.modlist as modlist

#
# Create LDAP, Filesystem and Scheduler portions of allocations, projects and accounts. Does nothing if everything is in place so can be run at any time. Includes user initial password
#

# Get an LDAP connection for use in other parts of the script
def initLDAP():
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    try:
        l = ldap.initialize(ldapUri)
    except ldap.LDAPError, e:
        print e
        exit(1)

    l.simple_bind(ldapBindDN, ldapBindPW)

    return l

# Check for user's existance in LDAP
def ldapExistanceCheck(user):
    # Get an appropriate LDAP Object
    pawseyLdap = initLDAP()
    searchFilter = ("uid=%s" % user)
    try:
        ldap_result_id = pawseyLdap.search(ldapBaseDN, ldapSearchScope, searchFilter, ldapRetrieveAttributes)
        result_data = []
        result_type, result_data = pawseyLdap.result(ldap_result_id, 0)
        if (result_data == []):
            print ("User %s does not exist" % user)
            return 0
        else:
            print ("User %s does exist" % user)
            return 1
    except ldap.LDAPError, e:
        print e
        exit(1)

# Create user in LDAP
def createLdapUser(user, personId):
    # Need to get user details and then pump them into ldap to create a user and a group
    userDict = userDetails(personId)
    print userDict
    
    # Required details: Given Name, sn, Username, uidnumber, gidnumber (use username for gid), password hash, email address, phone number
    if all (k in userDict for k in ("givenName", "sn", "uid", "uidNumber", "gidNumber", "mail", "userPassword", "telephoneNumber", "institution")):
        print "we are here"
        # Process them
        pawseyLdap = initLDAP()
        # DN for the new user entry
        dn = ("uid=%s,ou=%s,ou=People,%s" % (userDict["uid"], userDict["institution"], ldapBaseDN))
        # Attributes for the new entry
        attrs = {}
        attrs['objectclass'] = ['top', 'inetOrgPerson', 'organizationalPerson', 'person', 'posixAccount', 'inetUser']
        attrs['cn'] = ("%s %s" % (userDict['givenName'], userDict['sn'])).encode("utf8")
        attrs['givenName'] = userDict['givenName'].encode("utf8")
        attrs['sn'] = userDict['sn'].encode("utf8")
        attrs['uid'] = userDict['uid'].encode("utf8")
        attrs['uidNumber'] = str(userDict['uidNumber'])
        attrs['gidNumber'] = str(userDict['gidNumber'])
        attrs['loginShell'] = '/bin/bash'
        attrs['mail'] = userDict['mail'].encode("utf8")
        attrs['homeDirectory'] = ("/home/%s" % (userDict['uid'])).encode("utf8")
        attrs['userPassword'] = userDict['userPassword'].encode("utf8")
        attrs['telephoneNumber'] = userDict['telephoneNumber'].encode("utf8")

        print attrs
        print dn

        # Make the attributes dictionary into something we can throw at an ldap server
        ldif = modlist.addModlist(attrs)

        print ldif
        # Throw it at the ldap server!
        try: 
            pawseyLdap.add_s(dn,ldif)
        except ldap.LDAPError, e:
            print e
            exit(1)

        # Now create their group
        dn = ("cn=%s,ou=POSIX,ou=Groups,%s" % (userDict["uid"], ldapBaseDN))
        # Attributes for the new entry
        attrs = {}
        attrs['objectclass'] = ['top', 'posixGroup']
        attrs['cn'] = userDict['uid'].encode("utf8")
        attrs['gidNumber'] = str(userDict['gidNumber'])

        # Make the attributes dictionary into something we can throw at an ldap server
        ldif = modlist.addModlist(attrs)

        # Throw it at the ldap server!
        try: 
            pawseyLdap.add_s(dn,ldif)
        except ldap.LDAPError, e:
            print e
            exit(1)

    return

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
def userDetails(personId):
    
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
def activateAccount(user, allocation, personId):
    print ("Activating %s on allocation \"%s\" for project \"%s\"." % (user, allocation['name'], allocation['project']))
    
    # Check whether account is populated in LDAP, if not trigger ldap creation (or wait for details to be filled in).
    if not (ldapExistanceCheck(user)):
        print ("User %s doesn't exist in ldap, attempting to create" % (user))
        createLdapUser(user, personId)
        
    # Add user to Allocation in ldap if they aren't already
    if not (ldapAllocationCheck(user,allocation)):
        print ("User %s isn't attached to allocation \"%s\", so attaching them" % (user,allocation['name']))
        attachLdapUser(user, allocation)

    # Check User has a home directory on the appropriate system and create if not. Also create /group and /scratch directory (manual workaround for /scratch2 for now)
    checkUserDirectories(user, allocation)

    # Check Slurm configuration for user. Add any missing pieces.
    checkUserSlurmAllocation(user, allocation)

    # Traditional last step: Put user in correct host group if they are not already
    checkUserHostGroup(user, allocation['service'])
        
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

# Ldap config
ldapUri = config.get('ldap','uri')
ldapBaseDN = config.get('ldap','baseDN')
ldapBindDN = config.get('ldap','bindDN')
ldapBindPW = config.get('ldap','bindPW')
ldapSearchScope = ldap.SCOPE_SUBTREE
ldapRetrieveAttributes = None

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
            print user
            activateAccount(users[user], allocations[allocation], user) # That last argument is the Person.id. You'll be glad you had it later.

