# -*- coding: utf-8 -*-
import ldap
import ldap.modlist as modlist
import random
import django
from django.contrib.auth.models import User, Group

#for LDAP search results helper
import ldif
from StringIO import StringIO
from ldap.cidict import cidict

from django.conf import settings

import socket, errno
import logging

#Create a logging object for ldap debugging
logger = logging.getLogger('pawsey_ldap')
logger.setLevel(logging.DEBUG)
import md5 
import base64 

#
# Pass pwencoding=None to store the password CLEAR
# Other supported encodings: 'md5'
def createpassword(newpassword, pwencoding=None):
    encpassword = ''
    if newpassword is None or newpassword == '':
        raise Exception("Cannot create password given None or empty input")
    else:
        logger.debug( 'encoding new password') 
        #time to encode the password:
        if pwencoding is None:
            #No encoding
            encpassword = newpassword
        elif pwencoding == 'md5':
            #MD5 encoding
            m = md5.new()
            m.update(newpassword)
            logger.debug( 'doing md5')
            encpassword = '{MD5}%s' % (base64.encodestring( m.digest()) ) 
        elif pwencoding == 'ssha':
            logger.debug('doing SSHA')
            encpassword = ssha_password(newpassword)
        #Insert other encoding schemes here.            
        else:
            raise Exception("Unsupported password encoding")

    return encpassword.strip()

def ssha_password(password):
    import hashlib, os
    from base64 import encodestring
    salt = os.urandom(4)
    h = hashlib.sha1(password)
    h.update(salt)
    return "{SSHA}" + encodestring(h.digest() + salt)[:-1]

class LDAPSearchResult(object):
    """A class to model LDAP results.
    """
    def __init__(self, entry_tuple):
        """Create a new LDAPSearchResult object."""
        #print 'Creating LDAPSearchResult item...'
        (dn, attrs) = entry_tuple
        if dn:
            self.dn = dn
        else:
            self.dn = ''
            return

        self.attrs = cidict(attrs)

    def get_attributes(self):
        """Get a dictionary of all attributes.
        get_attributes()->{'name1':['value1','value2',...], 'name2: [value1...]}
        """
        return self.attrs

    def set_attributes(self, attr_dict):
        """Set the list of attributes for this record.

        The format of the dictionary should be string key, list of string 
        values. e.g. {'cn': ['M Butcher','Matt Butcher']}

        set_attributes(attr_dictionary)
        """
        self.attrs = cidict(attr_dict)

    def has_attribute(self, attr_name):
        """Returns true if there is an attribute by this name in the
        record.

        has_attribute(string attr_name)->boolean
        """
        return self.attrs.has_key( attr_name )

    def get_attr_values(self, key):
        """Get a list of attribute values.
        get_attr_values(string key)->['value1','value2']
        """
        return self.attrs[key]

    def get_attr_names(self):
        """Get a list of attribute names.
        get_attr_names()->['name1','name2',...]
        """
        return self.attrs.keys()

    def get_dn(self):
        """Get the DN string for the record.
        get_dn()->string dn
        """
        return self.dn

    def pretty_print(self):
        """Create a nice string representation of this object.

        pretty_print()->string
        """
        str = "DN: " + self.dn + "\n"
        for a, v_list in self.attrs.iteritems():
            str = str + "Name: " + a + "\n"
            for v in v_list:
                str = str + "  Value: " + v + "\n"
        str = str + "========"
        return str

    def to_ldif(self):
        """Get an LDIF representation of this record.

        to_ldif()->string
        """
        out = StringIO()
        ldif_out = ldif.LDIFWriter(out)
        ldif_out.unparse(self.dn, self.attrs)
        return out.getvalue()


def port_probe( host, port ):
    """Uses low level socket connection to door knock for a service without blocking"""
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    try:
        sock.connect( (host, port) )
        return True
    except socket.gaierror, gai:
        # DNS lookup failures!
        return False
    except socket.error, se:
        if se[0]==errno.ECONNREFUSED:
            # connection refused
            return False
    # fallback is "not responding"
    return False

def parse_ldap_url(url):
    assert url.startswith("ldap")
    assert "://" in url
    
    return url.split('/')[2], 636 if url.startswith("ldaps") else 389 if url.startswith("ldap") else None

# Short cut to avoid repeating those static lists of LDAP parameters
def user_ldap_handler():
    return LDAPHandler(userdn     = settings.USER_LDAP_USERDN, 
                                 password   = settings.USER_LDAP_PASSWORD, 
                                 server     = settings.USER_LDAP_SERVER, 
                                 user_base  = settings.USER_LDAP_USERBASE, 
                                 group      = None, 
                                 group_base = settings.USER_LDAP_GROUPBASE, 
                                 admin_base = settings.USER_LDAP_ADMINBASE,
                                 dont_require_cert=True, debug=True)

class LDAPHandler(object):
    def __init__(self, userdn=None, password=None, server = settings.USER_LDAP_SERVER, group = settings.USER_LDAP_GROUP, group_base = settings.USER_LDAP_GROUP_BASE, admin_base = settings.USER_LDAP_ADMIN_BASE, user_base = settings.USER_LDAP_USER_BASE, dont_require_cert=None, debug=None):
        '''This class makes use of the 'settings' module, which should be accessible from the current scope.'''
        try:
            #If require_cert is not specified, check settings
            if dont_require_cert is None:
                if hasattr(settings,"LDAP_DONT_REQUIRE_CERT") and settings.LDAP_DONT_REQUIRE_CERT:
                    dont_require_cert = True
                else:
                    dont_require_cert = False

            if dont_require_cert is True:
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            
            #If debug is not specified, check settings
            if debug is None:
                LDAP_DEBUG = hasattr(settings,"LDAP_DEBUG") and settings.LDAP_DEBUG
            else:
                LDAP_DEBUG = debug
            
            # check our USER_LDAP_SERVER setting. If its a string, turn it to a list. Then we iterate over the list trying servers.
            server_list = [server] if type(server)==str else list(server)
            
            server_live = False
            server_list_copy = server_list[:]
            while len(server_list_copy):
                valid_server = server_list_copy.pop(random.randint(0,len(server_list_copy)-1))
                host, port = parse_ldap_url(valid_server)
                
                if LDAP_DEBUG:
                    logger.debug("Trying server: %s port: %s..."%(host,port))
                
                # probe port
                if port_probe( host, port ):
                    # port is open. use this
                    server_live = True
                    if LDAP_DEBUG:
                        logger.debug("OK\n")
                    break
                else:
                    logger.debug("not responding\n")
                    
            if not server_live:
                raise ldap.LDAPError("All ldap servers not responding. tried: "+str(server_list))
            
            #initialise LDAP server connection
            self.l = ldap.initialize(valid_server)
            self.l.protocol_version = ldap.VERSION3
            if userdn is None:
                #bind using simple auth or Kerberos if available
                if LDAP_DEBUG:
                    logger.debug("trying ldap anonymous bind\n")
                self.l.simple_bind_s()
                if LDAP_DEBUG:
                    logger.debug('Anonymous bind OK\n')
            else:
                if LDAP_DEBUG:
                    logger.debug("trying ldap user bind: %s"%(userdn + ',' + admin_base))
                self.l.simple_bind_s(userdn + ',' + admin_base, password)
                if LDAP_DEBUG:
                    logger.debug('User bind OK\n')

        except ldap.LDAPError, e:
            logger.debug("Ldap Error:\n%s" % e )
            raise

        #Otherwise, set a few variables for later use
        self.GROUP = group
        self.GROUP_BASE = group_base
        self.SERVER = valid_server
        self.USER_BASE = user_base
        self.GROUPOC = 'groupofuniquenames'
        self.USEROC = 'inetorgperson'
        self.MEMBERATTR = 'uniqueMember'
        self.USERDN = 'ou=People'
 
    def close(self):
        self.l.unbind()

    def get_search_results(self, results):
        """Given a set of results, return a list of LDAPSearchResult objects.
        """
        res = []

        if type(results) == tuple and len(results) == 2 :
                (code, arr) = results
        elif type(results) == list:
                arr = results

        if len(results) == 0:
                return res

        for item in arr:
                res.append( LDAPSearchResult(item) )

        return res

    def ldap_query(self, base=None, scope=ldap.SCOPE_SUBTREE, filter="", rattrs=None, timeout=0):
        '''base is the ldap base to search on
           scope is the scope of the search (depth of descendant searches etc)
           userfilter is the user supplied filter information ( a string)
           rattrs is the format of the result set
        '''
        if base==None:
            base=self.USER_BASE

        retval = []
        try:
            if settings.DEBUG:
                logger.debug('LDAP Query: %s, %s, %s, %s' % (str(base), str(scope), str(filter), str(rattrs)))
            result_data = self.l.search_s(base, scope, filter, rattrs)
            retval = self.get_search_results(result_data)
        except ldap.LDAPError, e:
            logger.debug('LDAP Query Error: %s' % (str(e) ) )
        return retval
    
    def ldap_list_groups(self):
        '''returns a list of group names defined for the current group base'''
        groupdn = self.GROUP_BASE 
        userfilter = '(objectClass=%s)' % (self.GROUPOC)
        result_data = self.ldap_query(base=groupdn, filter=userfilter)
        groups = []
        for result in result_data:
            for g in result.get_attr_values('cn'):
                groups.append(g)
        return groups
        
 
    def ldap_get_user_details(self, username):
        ''' Returns a dictionary of user details.
            Returns empty dict on fail'''
        #Get application user details (only users in the application's LDAP tree) 
        logger.debug('***ldap_get_user_details***')
        #TODO: Replace this searchbase with an app variable
        searchbase = self.USER_BASE
        result_data = self.ldap_query(base=searchbase, filter = "uid=%s" % (username) )            
        if len(result_data) > 0:
            userdetails = result_data[0].get_attributes()
            try:
                a = self.ldap_get_user_groups(username)
                logger.debug('\tThe User Groups were: %s' % (str(a)) )
                userdetails['groups'] = a 
            except ldap.LDAPError, e:
                logger.debug('\tException: %s' % (str(e) ) )
            return userdetails
        else:
            logger.debug('\tldap_get_user_details returned no results: uid=%s' % (username) )
            #user doesn't exist
            #this can happen when a dummy user has been inserted into a group.
            return {}

    # FJ start
    # Generic version of ldap_get_user_details that allows to search for a user with an attribute and its value
    # Used to look for a user using its email address.
    # CAUTION: several users could have the same attribute value, the result returned is the details of the first entry returned by the search
    def get_user_details_from_attribute(self, attribute, value):
        ''' Returns a dictionary of user details searchin gor the attribute name and its value
            Returns empty dict on fail'''
        #Get application user details (only users in the application's LDAP tree) 
        logger.debug('***ldap_get_user_details***')
        searchbase = self.USER_BASE
        result_data = self.ldap_query(base=searchbase, filter = "%s=%s" % (attribute, value) )
        if len(result_data) > 0:
            userdetails = result_data[0].get_attributes()   # return the details of the first entry found
            return userdetails
        else:
            logger.debug('\tldap_get_user_details returned no results: %s=%s' % (attribute, value) )
            #user doesn't exist
            #this can happen when a dummy user has been inserted into a group.
            return {}
    # FJ end

    def ldap_update_user(self, username, newusername, newpassword, detailsDict, pwencoding=None):
            '''You will need an authenticated connection with admin privelages to update user details in LDAP'''
            #TODO: return an error status
            logger.debug('***ldap_update_user****')
            #if the new username is different to the old username, 
            #cache the current groups for this user.
            if newusername is None:
                newusername = username
            
            if username != newusername: 
                cachedGroups = self.ldap_get_user_groups(username)
                logger.debug('\tUsername was different. Cached groups are: %s' % (str(cachedGroups) ) )

            #search for the user DN to make sure we aren't renaming to an existing name.
            logger.debug('checking to see if new DN exists')
            newdn = self.ldap_get_user_dn(newusername)
            if newdn is not None:
                if newusername != username:
                    #no good. Trying to rename to an existing username
                    logger.debug( '\tNew Username already existed.')
                    return
           
            logger.debug('\tpreparing data') 
            #prepare data
            detailsDict['objectClass'] = ['top', 'inetOrgPerson', 'simpleSecurityObject', 'organizationalPerson', 'person']
            detailsDict['uid'] = newusername #setting the new username
          
            if newpassword is not None and newpassword != '':
          
                detailsDict['userPassword'] = createpassword(newpassword, pwencoding=pwencoding)
                logger.debug( 'finished encoding' )
            logger.debug( 'looking up old user')
            #ok now look up the user to update. Make sure we look them up using the old name.
            dn = 'uid=%s, %s' % (username, self.USER_BASE) #BASE not quite right
                                                           
            newparent = self.USER_BASE 
            newrdn = 'uid=%s' % (username)
            
            #rename the user if required
            if username != newusername:
                logger.debug( 'renaming user')
                try:
                    r = self.l.rename_s(dn, newrdn, newsuperior=newparent, delold=true)
                    #Change the dn, so we use this one from now on in the update
                    dn = "%s, %s" % (newrdn, newparent) 
                except ldap.LDAPError, e:
                    logger.debug ('User rename failed. %s' % ( str(e) ) )
            
            logger.debug('Editing User: %s' % (str(dn) ) )
            try:
                userfilter = "(&(objectclass=person) (uid=%s))" % username
                usrs = self.ldap_query(filter = userfilter, base=self.USER_BASE)
                if len(usrs) != 1:
                    raise ldap.LDAPError, "More than one user found for %s" % (username)
                old = usrs[0]
                logger.debug('OLD: ')
                o = old.get_attributes()
                for k in o.keys():
                    logger.debug("Key %s, value: %s" % (k, o[k]))
                
                for k in detailsDict.keys():
                    v = detailsDict[k]
                    if not isinstance(v, list):
                        detailsDict[k] = [v] 
                logger.debug('NEW: ')
                for k in detailsDict.keys():
                    logger.debug("Key %s, value: %s" % (k, detailsDict[k]) )

                #Test equality of sets.
                for k in detailsDict.keys():
                    if not o.has_key(k):
                        logger.debug('Key %s not present in OLD' % (k) )
                    elif o[k] != detailsDict[k]:
                        logger.debug( 'Value for %s different. %s vs %s' % (k, o[k], detailsDict[k]) )
                    else:
                        logger.debug('new and old values for %s are the same' % (k) )
                logger.debug('finished testing')
                mods = modlist.modifyModlist(old.get_attributes(), detailsDict, ignore_oldexistent=1)
                
                logger.debug('Mods: ')
                for t in mods:
                    logger.debug(t)
                if len(mods) > 0:
                    r = self.l.modify_ext_s(dn, mods)
            except ldap.LDAPError, e:
                logger.debug('Error editing user: %s' % (str(e) ) )
                #print('Error editing user: %s' % (str(e) ) )

            return

    def ldap_add_user(self, username, detailsDict, pwencoding=None, objectclasses=[], usercontainer='', userdn='', basedn=''):
        '''You need to have used an admin enabled username and password to successfully do this'''
        username = username.strip()
        f = "(&(objectclass=person) (uid=%s))" % username
        usrs = self.ldap_query(filter = f, base=self.USER_BASE)
        retval = False
        if len(usrs) != 0:
            #user already existed!
            logger.debug('\tA user called %s already existed. Refusing to add.' % (username))
            #print('\tA user called %s already existed. Refusing to add.' % (username))
        else:
            try:
                logger.debug('\tPreparing to add user %s' % (username))
                dn = 'uid=%s,%s,%s,%s' % (username, usercontainer, userdn, basedn)
                from copy import deepcopy
                data = deepcopy(detailsDict)
                if isinstance(objectclasses, list):
                    data['objectClass'] = objectclasses
                else:
                    data['objectClass'] = [objectclasses]
                    
                #newattrs = []
                #for key in data:
                #    newattrs.append( (str(key), str(data[key])) )
                newattrs = modlist.addModlist(data)

                #so now newattrs contains a list of tuples, which are key value pairs.
                logger.debug('Calling ldap_add: %s and %s' % (dn, str(newattrs)) )
                #print('Calling ldap_add: %s and %s' % (dn, str(newattrs)) )
                res = self.l.add_s(dn, newattrs)
                #TODO interrogate res
                retval = True
            except ldap.LDAPError, e:
                logger.debug('Exception adding LDAP user: ', str(e))
                #print('Exception adding LDAP user: ', str(e))
        return retval

    def ldap_add_group(self, groupname):
        '''You need to have used an admin enabled username and password to successfully do this'''
        logger.debug('***ldap_add_group***')
        groupname = groupname.strip()
        f = '(objectClass=groupOfUniqueNames)'
        groupresult = self.ldap_query(base = self.GROUP_BASE , filter = f, rattrs = ['cn'])
        for groupres in groupresult:
            if groupname == groupres.get_attr_values('cn')[0]:
                return False
       
        #ok so we are good to go.
        logger.debug('preparing to add group')
        newattrs = []
        newattrs.append( ('cn', str(groupname)) )
        newattrs.append( ('objectClass', self.GROUPOC) )
        #newattrs.append( ('uniqueMember', 'uid=dummy') )   # is it needed?

        dn = 'cn=%s,%s' % (groupname, self.GROUP_BASE)
        logger.debug('calling ldap_add: %s AND %s' % (str(dn), str(newattrs) ) )
        #print('calling ldap_add: %s AND %s' % (str(dn), str(newattrs) ) )
        try:
            res = self.l.add_s(dn, newattrs)
        except ldap.LDAPError, e:
            logger.debug('ldap_add_group: Exception in ldap_add: %s' % ( str(e) ) )
            #print('ldap_add_group: Exception in ldap_add: %s' % ( str(e) ) )
            return False
        logger.debug('the response from the add command was: %s' % (str(res) ) )
        #print('the response from the add command was: %s' % (str(res) ) )

        return True

    # FJ start
    def create_ou(self, name, parentdn):
        '''Create an OU for a group, return True if succeeded otherwise False'''
        newattrs = []
        newattrs.append( ('ou', str(name)) )
        newattrs.append( ('objectClass', 'organizationalunit') )

        dn = 'ou=%s,%s' % (name, parentdn)
        logger.debug('calling ldap create_ou: %s AND %s' % (str(dn), str(newattrs) ) )
        #print('create_ou calling ldap_add: %s AND %s' % (str(dn), str(newattrs) ) )
        try:
            res = self.l.add_s(dn, newattrs)
        except ldap.LDAPError, e:
            logger.debug('create_ou: ldap create_ou: Exception in ldap_add: %s' % ( str(e) ) )
            #print('ldap create_ou: Exception in ldap_add: %s' % ( str(e) ) )
            return False
        logger.debug('the response from the add command was: %s' % (str(res) ) )
        #print('create_ou the response from the add OU command was: %s' % (str(res) ) )

        return True

    def ldap_add_group_with_parent(self, groupname, parentdn, description = None, objectClasses = None, attributes = None):
        '''You need to have used an admin enabled username and password to successfully do this'''
        logger.debug('***ldap_add_group***')
        groupname = str(groupname).strip()  # unicode -> string
        f = '(objectClass=groupOfUniqueNames)'
        groupresult = self.ldap_query(base = self.GROUP_BASE , filter = f, rattrs = ['cn'])
        for groupres in groupresult:
            if groupname == groupres.get_attr_values('cn')[0]:
                return False
       
        #ok so we are good to go.
        logger.debug('preparing to add group')
        newattrs = []
        if attributes:
            newattrs = attributes
        newattrs.append( ('cn', str(groupname)) )
        if not objectClasses:
            objectClasses = self.GROUPOC
        newattrs.append( ('objectClass', objectClasses) )   # objectClasses must be a list
        if description:
            newattrs.append( ('description', str(description)) )

        dn = 'cn=%s,%s' % (groupname, parentdn)
        logger.debug('calling ldap_add: %s AND %s' % (str(dn), str(newattrs) ) )
        #print('calling ldap_add: %s attrs: %s' % (str(dn), str(newattrs) ) )
        res = True
        try:
            res = self.l.add_s(dn, newattrs)
        except ldap.ALREADY_EXISTS, e:
            #this is ok, if you are trying to add a group and it already exists
            logger.debug("Group we are trying to add already existed. Ok")
        except ldap.LDAPError, e:
            logger.debug('ldap_add_group: Exception in ldap_add: %s' % ( str(e) ) )
            #print('ldap_add_group: Exception in ldap_add: %s' % ( str(e) ) )
            return False
        logger.debug('the response from the add command was: %s' % (str(res) ) )
        #print('the response from the add command was: %s' % (str(res) ) )

        return True
    # FJ end

    def ldap_rename_group(self, oldname, newname):
        '''You need to have used an admin enabled username and password to successfully do this'''
        logger.debug('***ldap_rename_group***')
        
        dn = 'cn=%s,%s' % (oldname.strip(), self.GROUP_BASE)
        newrdn = 'cn=%s' % (newname.strip())
        try:
            ret = self.l.rename_s(dn, newrdn) #by default removes the old one (delold=1)
            
        except ldap.LDAPError, e:
            logger.debug('Couldn\'t rename group %s: %s' % (oldname, str(e)) )
            return False
        
        return True


    def ldap_delete_group(self, groupname):
        '''You need to have used an admin enabled username and password to successfully do this'''
        '''CAUTION: This function will delete any group passed to it.
           You need to have sanity checked the group you are trying to delete BEFORE
           calling this function.'''
        logger.debug('ldap_delete_group')
        dn = 'cn=%s,%s' % (groupname.strip(), self.GROUP_BASE)
        try:
            ret = self.l.delete_s(dn)
        except ldap.LDAPError, e:
            logger.debug('Couldn\'t delete group %s: %s' % (groupname, str(e))  ) 
            return False

        return True

    def ldap_get_user_groups(self, username, use_udn=True):
        
        logger.debug('***ldap_get_user_groups:enter***')
        if use_udn:
            udn = self.ldap_get_user_dn(username)
            if udn is None:
                return None
        else:
            udn = username
        f = '(&(objectClass=%s)(%s=%s))' % (self.GROUPOC, self.MEMBERATTR, udn)    
        result_data = self.ldap_query(base=self.GROUP_BASE,filter=f)            
        groups = []
        for result in result_data:
            for g in result.get_attr_values('cn'):
                groups.append(g) 
        
        if len(groups) == 0:
            logger.debug('ldap_get_user_groups returned no results.')
        logger.debug('***ldap_get_user_groups:exit***')
      
        return groups  
            
    def ldap_get_user_dn(self, username):
        result_data = self.ldap_query(filter='uid=%s' % (username))
        if len(result_data) > 0:
            dn = result_data[0].get_dn()
            logger.debug('User DN found as: %s' % (dn) )
            return dn
        else:
            logger.debug('Username not found!')       
            return None            

    def ldap_list_users(self, searchGroup, method = 'and'):
        '''expects searchGroup to be a list of groups to search
           fetches an array of user detail dictionaries
           default method is 'and' (need to be in all groups specified)
           other acceptible method is 'or' (can be in any of the groups)
           '''
        logger.debug('***ldap_list_users: enter ***')
        
        userlists = []
        for groupname in searchGroup:
            g = []
            filter = 'cn=%s' % (groupname)
            userlist = self.ldap_search_users(filter = filter, base=self.GROUP_BASE)
            logger.debug('USERLIST: %s' % (str(userlist)) )
            for user in userlist:
                g.append(user)
            userlists.append(g)

        #so now, users is a list of lists.
        #the first thing to do is get a list of distinct usernames.
        distinct_users = []
        for g in userlists:
            for user in g:
                if user not in distinct_users:
                    distinct_users.append(user)

        #if the method is 'and', then we are returning a list of users that are in all the groups.
        retusers = []
        if method == 'and':
            for user in distinct_users:
                in_all = True
                for g in userlists:
                    if user not in g:   
                        in_all = False
                if in_all:
                    retusers.append(user)

        else:
            retusers = distinct_users #users in any group

        logger.debug('***ldap_list_users: exit***')
        return retusers

    def ldap_search_users(self, base, filter):
        '''returns a list of users, each user being a dict'''
        logger.debug('***ldap_search_users : enter***')
        results = self.ldap_query(filter=filter, base=base)
       
        users = []
        for result in results:
            if result.has_attribute('uniquemember'):
                userresults = result.get_attr_values('uniquemember')
                for user in userresults:
                    logger.debug('\tUSER: %s' % (str(user) ) )
                    prefix, uname =user.split('=', 1)
                    uname = uname.split(',', 1)[0]
                    userdetails = self.ldap_get_user_details(uname)
                    if len(userdetails) > 0:
                        users.append(userdetails)
        logger.debug('***ldap_search_users : exit***')
        return users

    def ldap_add_user_to_group(self, username, groupname, objectclass='groupofuniquenames', membershipattr="uniqueMember"):
        '''adds a user to a group
           returns true on success
           returns false on fail (user didnt exist, group didn't exist)'''
        logger.debug('***ldap_add_user_to_group*** : enter') 
        retval = False
        ud = self.ldap_get_user_details(username)
        if len(ud) > 0: #does the user exist?
            #already have this group?
            if groupname in ud['groups']:
                logger.debug('\tUser already in group')
                retval = True #they were already in the group
            else:
                #does the new group exist?
                if groupname in self.ldap_list_groups():
                    logger.debug('\tCandidate group existed')
                else:
                    logger.warning("Candidate group didn't seem to exist, but I will attempt adding anyway")

                #add the user to the group
                #get group dn:
                gresult = self.ldap_query(base=self.GROUP_BASE, filter='(&(objectclass=%s) (cn=%s))' % (objectclass, groupname))
                if len(gresult) != 0:
                    try:
                        gdn = gresult[0].get_dn()
                        #groupofuniquenames usually uses the full udn as the membership name
                        #posixgroup (for example) just uses the uid.
                        if objectclass=='groupofuniquenames':
                            udn = self.ldap_get_user_dn(username)
                        else:
                            udn = str(username)
                        #modify the group's attrubutes so as to add this entry
                        import ldap.modlist as modlist
                        old = gresult[0]
                        oldattrs = old.get_attributes()
                        import copy
                        newattrs = copy.deepcopy(oldattrs)
                        logger.debug('oldattrs: %s' % ( str( old.get_attributes() ) ) )
                        #catch code for empty groups (no 'uniquemmembers')
                        if not newattrs.has_key(membershipattr):
                            newattrs[membershipattr] = []
                        newattrs[membershipattr].append(udn) 
                        mods = modlist.modifyModlist(oldattrs, newattrs, ignore_oldexistent=1)
                        logger.debug('MODS:%s' % (str(mods)))
                        if len(mods) > 0:
                            r = self.l.modify_ext_s(gdn, mods)
                        retval = True
                    except ldap.TYPE_OR_VALUE_EXISTS, e:
                        #trying to add to a group when we already are a member is ok
                        logger.debug('Trying to add value that already exists: Ok.')
                        retval = True 
                    except ldap.LDAPError, e:
                        logger.debug('Exception adding user %s to group %s: %s' % (username, groupname, str(e)))
                        #print 'Exception adding user %s to group %s: %s' % (username, groupname, str(e))

                else:
                    logger.debug('\tCouldn\'t get group dn')

        logger.debug('***ldap_add_user_to_group*** : exit') 
        return retval


    def ldap_remove_user_from_group(self, username, groupname):
        '''removes a user from a group
           returns true on success
           returns false on fail (user didnt exist, group didn't exist)'''
        logger.debug('***ldap_remove_user_from_group*** : enter') 
        retval = False
        try:
            #get group
            gresult = self.ldap_query(base=self.GROUP_BASE, filter='(&(objectclass=groupofuniquenames) (cn=%s))' % groupname)
            gdn = gresult[0].get_dn()
            ud = self.ldap_get_user_details(username)
            if len(ud) == 0:
                logger.debug('\tNo user found')
            else:
                #remove the user from the group
                udn = self.ldap_get_user_dn(username)
                logger.debug('\tRemoving user %s from group %s' % (udn, gdn))
                old = gresult[0]
                oldattrs = old.get_attributes()
                import copy
                newattrs = copy.deepcopy(oldattrs)
                logger.debug('\toldattrs: %s' % (str(old.get_attributes()) ) )
                #catch code for empty groups (no 'uniquemmembers')
                if not newattrs.has_key('uniqueMember'):
                    newattrs['uniqueMember'] = []

                newattrs['uniqueMember'].remove(udn) 
                import ldap.modlist as modlist
                mods = modlist.modifyModlist(oldattrs, newattrs, ignore_oldexistent=1)
                logger.debug('MODS:%s' % (str(mods)))
                if len(mods) > 0:
                    r = self.l.modify_ext_s(gdn, mods)
                retval = True
        except ldap.LDAPError, e:
            logger.debug( 'Exception when removing %s from %s: %s' % (username, groupname, str(e)) )

        logger.debug('***ldap_remove_user_from_group*** : exit')
        return retval
