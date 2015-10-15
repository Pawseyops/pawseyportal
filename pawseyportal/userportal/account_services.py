from django.core import mail as django_mail
from django.core.urlresolvers import reverse
from django.conf import settings
import uuid
import datetime
import ldap_helper
from django.utils import simplejson
import logging
logger = logging.getLogger('pawsey_ldap')
logger.setLevel(logging.DEBUG)

from models import *
from django.db import transaction
from django.utils import simplejson
from django.template import loader, Context
from models import EmailTemplate


def send_account_creation_mail(person, request):
    subject = "Successful application for Pawsey Supercomputing Centre infrastructure"
    email_hash = str(uuid.uuid4())
    link = "%s%s/%s" % (settings.MYURL, 'account-request', email_hash)
    template = EmailTemplate.objects.get(name='Participant Account Request')
    subject, message = template.render_to_string({'participant': person, 'link': link})
    send_mail(subject, message, person.institutionEmail)

    person.account_email_hash = email_hash
    person.status = Participant.STATUS['EMAIL_SENT']
    person.accountEmailOn = datetime.datetime.now()
    person.save()

def send_account_created_notification_mail(person, request):
    subject = "Account created for Pawsey Supercomputing Centre infrastructure"
    uid = person.personAccount.uid
    account_details = get_user_account_details(uid)
    project = person.allocation.project.code
    hours_allocated = person.allocation.serviceunits
    assert project is not None and len(project)>0, "Project could not be retrieved at time of 'account created' email for user %s" % (uid) 
    assert (hours_allocated is not None) and (hours_allocated > 0), "Invalid hours allocated (%s) at time of 'account created' email" % (str(hours_allocated) )
    template = EmailTemplate.objects.get(name='Participant Account Created')
    subject, message = template.render_to_string({'participant': person, 'project': project, 'uid': uid})
    send_mail(subject, message, person.insitutionEmail)

    person.status = Participant.STATUS['ACCOUNT_CREATED_EMAIL_SENT']
    person.accountCreatedEmailOn = datetime.datetime.now()
    person.save()

def send_mail(subject, message, to):   
    django_mail.send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to])

#TODO: remove when create_user_accounts calls create_application_group
def get_application_area(application):
    areanum = str(application.id)
    parentarea = application.priority_area.name
    childarea = application.priority_area.code
    return (parentarea, childarea, areanum)

def create_application_group(ldaphandler, application):
    '''
    Create the group in LDAP for the application. Create the parent area if needed
    return the project name if successful else None
    '''
    if application.ldap_project_name is not None and application.ldap_project_name != '':
        groupname = application.ldap_project_name
    else:
        groupname = '%s%s' % (application.priority_area.code, str(application.id))
    gidnumber = str(30010 + application.id)     # TODO: CAUTION: the offset is hard coded here
    description = str(application.project_title)

    groupdone = create_group(ldaphandler = ldaphandler, parentou = application.priority_area, groupname = groupname, description = description, gidnumber = gidnumber)
    if groupdone:
        res = groupname
    else:
        res = None
    return res

def create_applications_groups(applicationidlist):
    '''
    Create the goups in LDAP for the application ids passed in
    returns a dict with the count created and errors.
    '''

    result = {'created': 0, 'errors': 0}
    
    #connect to the ldap server, where we create all the accounts
    logger.debug("ldap bind with: server: %s userdn: %s" % (settings.USER_LDAP_SERVER, settings.USER_LDAP_USERDN) )
    ldaph = ldap_helper.user_ldap_handler()

    for id in applicationidlist:
        app = Application.objects.get(id=id)
        logger.debug("Application: %s" % (app.project_title,) )
        if app.complete and app.hours_allocated and app.hours_allocated > 0:
            groupname = create_application_group(ldaph, app) # returns groupname or None
            if groupname:
                # save the groupname like 'Astronomy23' in the application
                logger.debug("Application: %s ldap group created: %s" % (app.project_title, groupname) )
                app.ldap_project_name = groupname
                app.save()
                result['created'] += 1
            else: result['errors'] += 1
        else:
            result['errors'] += 1   # don't create the group for a project not submitted or with no hours allocated
    ldaph.close()
    return result    

def create_user_accounts(person_id_list):
    '''
    Create the account in LDAP and add it to the group
    if the user account doesn't exist, create it else update it.
    Update means update the attributes already in the LDAP entry
    and add the ones from the old LDAP entry that are not the in the new LDAP
    '''
    created_count = 0
    error_count = 0
    result = {'created':0, 'errors':0, 'updated':0, 'msg': ''}
    
    #connect to the 'new' ldap repo, where we create all the accounts
    logger.debug("ldap bind with: server: %s userdn: %s" % (settings.USER_LDAP_SERVER, settings.USER_LDAP_USERDN) )
    ldaph = ldap_helper.user_ldap_handler()

    # needed for ldap_helper.ldap_add_user: dn = 'uid=%s,%s,%s,%s' % (username, usercontainer, userdn, basedn)
    usercontainer = settings.USER_LDAP_USER_OU
    userdn = settings.USER_LDAP_COMPANY
    basedn = settings.USER_LDAP_DOMAIN

    if ldaph:
        for id in person_id_list:
            person = Person.objects.get(id=id)
            logger.debug("\nParticipant: %s" % (person.institutionEmail,) )

            if person.status != Person.STATUS['DETAILS_FILLED']:   # account not ready yet
                result['errors'] += 1
                logger.debug("Skipping participant %s, details not filled" % (person.institutionEmail) )
                continue # next person

            try:
                person_account = person.personAccount
                email = person.institutionEmail

                if not person_account:
                    raise PersonAccount.DoesNotExist()

                if person_account:
                    logger.debug("participant: %s %s email:%s" % (person_account.first_name, person_account.last_name, email) )
                    # get the user entry in the new ldap repo if it exists

                    #userdetails = ldaph.get_user_details_from_attribute(attribute = 'mail', value = email)
                    userdetails = ldaph.get_user_details_from_attribute(attribute = 'uid', value = person_account.uid)
                    logger.debug("user uid: %s details: %s" % (person_account.uid, userdetails) )
                    done = False

                    if not userdetails:
                        # user entry does not exist in the new ldap, create it
                        logger.debug("creating user %s in LDAP"%(email))
                        userdone = create_user_account(ldaph, person, usercontainer, userdn, basedn)
                        if userdone:
                            result['created'] += 1
                    else:
                        logger.debug("updating user %s in LDAP"%(email))
                        userdone = update_user_account(ldaph, person)
                        if userdone:
                            result['updated'] += 1

                    if userdone:
                        # user added or updated to the ldap directory, add the user to the group, create the group if it doesn't exist
                        (parentarea, childarea, areanum) = get_application_area(person.allocation)

                        if person.application.ldap_project_name is not None and person.application.ldap_project_name != '':
                            groupname = person.application.ldap_project_name
                        else:
                            groupname = '%s%s' % (childarea, areanum)
                        gidnumber = str(30010 + person.application.id)
                        description = str(person.application.project_title)
                        groupdone = create_group(ldaphandler = ldaph, parentou = parentarea, groupname = groupname, description = description, gidnumber = gidnumber)
                        
                        uid = person_account.uid
                        logger.debug("Adding user uid: %s to group: %s"%(uid, groupname))
                        # ldap_add_user_to_group(username, groupname, objectclass='groupofuniquenames', membershipattr="uniqueMember"):
                        usergroupdone = ldaph.ldap_add_user_to_group(uid, groupname, objectclass='posixgroup', membershipattr='memberUid')
                        logger.debug("Adding user uid: %s to group: %s RESULT: %s"%(uid, groupname, usergroupdone))

                        # create a posixGroup with cn=uid
                        posixgroupname = person_account.uid
                        gidnumber = str(person_account.gid_number)
                        parentou = settings.USER_LDAP_POSIXGROUPBASE # 'ou=POSIX,ou=Groups,dc=ivec,dc=org'
                        
                        
                        posixdone = ldaph.ldap_add_group_with_parent(groupname = posixgroupname, parentdn = parentou, objectClasses = ['top','posixGroup'], attributes = [('gidNumber',gidnumber)])

                        # update the user status only if all the steps went through
                        logger.debug( "groupdone %s usergroupdone %s posixdone %s" % (groupdone, usergroupdone, posixdone) )
                        if groupdone and usergroupdone and posixdone:
                            person.status = Participant.STATUS['ACCOUNT_CREATED']
                            person.accountCreatedOn = datetime.datetime.now()
                            person.save()

                        # save the groupname like 'Astronomy23' in the application
                        application = person.application
                        application.ldap_project_name = groupname
                        application.save()

            except PersonAccount.DoesNotExist, e:
                logger.debug("PersonAccount.DoesNotExist error: %s" % (e) )
                result['errors'] += 1
        ldaph.close()
    return result

def create_group(ldaphandler, parentou, groupname, description, gidnumber):
    '''
    description, gidnumber must be string (not a unicode string)
    '''
    # create the OU for this group like 'Astronomy'
    oudescription = None
    parentdn = settings.USER_LDAP_GROUPBASE
    logger.debug("create_group create_ou: parentou: %s parentdn: %s"%(parentou, parentdn))
    res = ldaphandler.create_ou(name = parentou, parentdn = parentdn) # 'ou=Projects,ou=Groups,%s' % (USER_LDAP_BASE)
    # ignore the result, the OU can exist already

    # can't create the group if the parent doesn't exist
    # the group name would be like 'Astronomy18' where 18 is the application number
    groupparent = 'ou=%s,%s' % (parentou, settings.USER_LDAP_GROUPBASE)
    logger.debug("create_group ldap_add_group_with_parent: groupname: %s parentou: %s, gidnumber: %s"%(groupname, groupparent, gidnumber))
    res = ldaphandler.ldap_add_group_with_parent(groupname = groupname, parentdn = groupparent, description = description,  objectClasses = ['top','posixGroup'], attributes = [('gidNumber',gidnumber)])
    return res

def add_user_to_group(ldaphandler, uid, groupname):
    done = ldaph.ldap_add_user_to_group(uid, groupname)
    return done

def set_user_ldap_dict(person):
    '''set the user attributes from the old dictionary and add/'override the attributes we really need'''
    
    detailsdict = {}
    personaccount = person.personaccount

    detailsdict["givenName"] = [person.first_name]
    detailsdict["sn"] = [person.surname]
    detailsdict["cn"] = [person.displayName] # required attribute
    #only want non blank telephone nums
    if person.phone is not None and len(person.phone) > 0: 
        detailsdict['telephoneNumber'] = [person.phone]
    detailsdict['userPassword'] = [personaccount.password_hash]
    detailsdict['mail'] = [person.institutionEmail]

    uid =  str(personaccount.uid)
    detailsdict['uid'] = [uid]
    
    #POSIX STUFF
    detailsdict['uidNumber'] = [personaccount.uid_number]
    detailsdict['gidNumber'] = [personaccount.gid_number]
    detailsdict['homeDirectory'] = ['/home/%s' % (uid)]
    detailsdict['loginShell'] = ['/bin/bash']


    # convert the unicode strings in strings for ldap, will be done in ldap_handler in the future
    for attr in detailsdict:
        valuelist = detailsdict[attr] # list of attributes in unicode strings
        strlist = [str(value) for value in valuelist]
        detailsdict[attr] = strlist

    return detailsdict

def create_user_account(ldaph, person, usercontainer, userdn, basedn):
    res = False
    person_account = person.personAccount
    person_account.constrain_uidgid()
    uid = person_account.uid
    unique_uid = person_account.get_unique_uid()
    if uid != unique_uid:
        logger.debug("Unwilling to submit non-unique uid (%s) for LDAP account creation - suggest %s" % (uid, unique_uid) )
    else: 
        institution = person_account.institution.ldap_ou_name
        usercontainer = 'ou=%s,%s' % (institution,usercontainer)
        olddict = {}
       
        detailsdict = set_user_ldap_dict(person)

        logger.debug( "create_user_account %s uid: %s userdn: %s basedn: %s" % (person.institutionEmail, uid, userdn, basedn) )
        # ldap_handler.add_user build the user dn like this:
        # dn = 'uid=%s,%s,%s,%s' % (username, usercontainer, userdn, basedn)
        # real example from ldap browser: uid=hum092,ou=CSIRO,ou=People,dc=ivec,dc=org
        res = ldaph.ldap_add_user(username = uid,
                      detailsDict = detailsdict,
                      pwencoding = None,
                      #objectclasses = ['top', 'inetOrgPerson', 'organizationalPerson', 'person', 'posixAccount'],
                      objectclasses = ['top', 'inetOrgPerson', 'organizationalPerson', 'person', 'posixAccount', 'inetUser'],
                      usercontainer = usercontainer,
                      userdn = userdn,
                      basedn = basedn)

    # ldap_add_user returns false if the user was not added
    logger.debug("create_user_account result: %s" % (res,) )
    return res

def update_user_account(ldaph, person):
    person_account = person.personaccount
    uid = person_account.uid

    detailsdict = set_user_ldap_dict(person)

    #print "update_user_account %s uid: %s" % (person.email, uid)

    res = ldaph.ldap_update_user(username = uid,
                             newusername = uid,
                             newpassword = str(person_account.password_hash),
                             detailsDict = detailsdict,
                             pwencoding = None)

    # ldap_update_user does not return anything, assume success
    # TODO: change ldap_update_user to return a real result code
    res = True
    return res

def get_user_accounts_CSV(person_id_list):
    returnlist = []
    #so the format we will do is:
    #username, emailaddress, homedir, shell, uidnum, gidnum, institution, groups (space separated)
    returnlist.append("#UID, EMAIL, HOMEDIR, SHELL, UIDNUM, GIDNUM, INSTITUTION, GROUPS")
    for id in person_id_list:
        p = Person.objects.get(id=id)
        pa = p.personAccount
        try:
            detailsdict = get_user_account_details(pa.uid)
            ldap_details = detailsdict['details']
            groups = detailsdict['groups'] 
            institution = pa.institution.ldap_ou_name
            groupsstr = " ".join(groups)
            summarystr = "%s,%s,%s,%s,%s,%s,%s,%s" % (pa.uid,p.email,ldap_details['homeDirectory'][0], ldap_details['loginShell'][0], ldap_details['uidNumber'][0], ldap_details['gidNumber'][0], institution, groupsstr)
        except Exception, e:
            summarystr = "Error occurred getting ldap details for uid %s:%s" % (pa.uid, e)
        
        returnlist.append(summarystr)
    
    return returnlist

def get_user_account_details(uid):
    ldaph = ldap_helper.user_ldap_handler()

    usercontainer = settings.USER_LDAP_USER_OU
    userdn = settings.USER_LDAP_COMPANY
    basedn = settings.USER_LDAP_DOMAIN

    #try a bunch of stuff to capture all their group info
    ldaph.GROUP_BASE = settings.USER_LDAP_GROUPBASE
    ldaph.GROUPOC = 'posixgroup'
    ldap_details = ldaph.ldap_get_user_details(uid)
    groups = ldaph.ldap_get_user_groups(uid, use_udn=False)
    ldaph.MEMBERATTR = 'memberUid'
    groups += ldaph.ldap_get_user_groups(uid, use_udn=False)
    ldaph.GROUP_BASE = settings.USER_LDAP_POSIXGROUPBASE
    groups += ldaph.ldap_get_user_groups(uid, use_udn=False)


    ldaph.close()
    return {'details': ldap_details, 'groups': groups}

def hash_password(newpassword, pwencoding='ssha'):
    return ldap_helper.createpassword(newpassword, pwencoding=pwencoding)

def get_applications_CSV(id_list):
    returnlist = []

    # first line with column names
    returnlist.append("PROJECTNAME,HOURSALLOCATED,PROJECTTITLE")

    for id in id_list:
        app = Application.objects.get(id=id)
        if app.ldap_project_name:
            if not app.hours_allocated:
                app.hours_allocated = 0
            summarystr = '%s,%s,"%s"' % (app.ldap_project_name, app.hours_allocated, app.project_title)
            returnlist.append(summarystr)
    
    return returnlist

@transaction.commit_on_success
def save_account_details(person):
    person_account = person.personAccount
    person.status_id = Participant.STATUS['DETAILS_FILLED']
    person.details_filled_on = datetime.datetime.now()
    #make sure the uid is valid
    person_account.uid = person_account.get_unique_uid()
    person_account.save()
    person_account.constrain_uidgid() #'fixes' the uidnumber/gidnumber and saves
     
    person.save()
