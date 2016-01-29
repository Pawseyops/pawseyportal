from django.core import mail as django_mail
from django.core.urlresolvers import reverse
from django.conf import settings
import uuid
import datetime
import ldap_helper
import logging
logger = logging.getLogger('pawsey_ldap')
logger.setLevel(logging.DEBUG)

from models import *
from django.db import transaction
from django.template import loader, Context
from models import EmailTemplate
from helpers import siteurl


def send_account_request_mail(person, request):
    subject = "Successful application for Pawsey Supercomputing Centre infrastructure"
    email_hash = str(uuid.uuid4())
    #link = "%s%s/%s" % (settings.MYURL, 'account-request', email_hash)
    link = "%sportal/%s/%s" % (siteurl(request), 'account-request', email_hash)
    template = EmailTemplate.objects.get(name='Person Account Request')
    subject, message = template.render_to_string({'person': person, 'link': link})
    send_mail(subject, message, person.institutionEmail)

    person.accountEmailHash = email_hash
    person.status_id = Person.STATUS['EMAIL_SENT']
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

    person.status_id = Person.STATUS['ACCOUNT_CREATED_EMAIL_SENT']
    person.accountCreatedEmailOn = datetime.datetime.now()
    person.save()

def send_mail(subject, message, to):   
    django_mail.send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to])

def hash_password(newpassword, pwencoding='ssha'):
    return ldap_helper.createpassword(newpassword, pwencoding=pwencoding)

@transaction.atomic
def save_account_details(person):
    person_account = person.personAccount
    person.status_id = Person.STATUS['DETAILS_FILLED']
    person.details_filled_on = datetime.datetime.now()
    #make sure the uid is valid
    person_account.save()
    person_account.constrain_uidgid() #'fixes' the uidnumber/gidnumber and saves
     
    person.save()

def check_unique_uid(uid):
    if uid is None or len(uid) == 0:
        return False
    qs = PersonAccount.objects.filter(uid = uid)
    if len(qs) == 0:
        #There were none. OK!
        return True
    elif (len(qs) == 1) and qs[0].id == self.id:
        #There was one, but it was me.
        return True
    else:
        return False
