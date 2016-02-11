from django.db import models
from pawseyportal.userportal.help_text import *
from ldap_helper import *
from django.template import engines, Context
from datetime import date

# Models for Projects, people, accounts.
class ServiceType(models.Model):
    name = models.CharField(max_length=256)
    helpEmail = models.EmailField(max_length=254)

    def __unicode__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=256)
    type = models.ForeignKey(ServiceType)

    def __unicode__(self):
        return self.name

class Institution(models.Model):
    name = models.CharField(max_length=256)
    partner = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class PersonAccount(models.Model):
    uid = models.CharField(max_length=256, null=True, blank=True)
    uidNumber = models.IntegerField(null=True, blank=True)
    gidNumber = models.IntegerField(null=True, blank=True)
    passwordHash = models.CharField(('password'), max_length=256, null=True, blank=True)

    def constrain_uidgid(self):
        '''Ensures the users uidnumber and gidnumber are over 20k, and unique in the database.
           Can only be called after the user has already been saved.
        '''
        offset = 21000
        maxid = 29999
        # Make sure the new LDAP uid doesn't already exist on the LDAP server
        # Iterate 5 times, which should be ample. If we hit the end, it might require
        # human intervention anyway so throw an exception.
        pawseyLdap = user_ldap_handler()
        for newid in range(self.id + offset, self.id + offset + 100):
            if newid > maxid:
                raise Exception('Maximum LDAP uidNumber of %s exceeded'%maxid)
            user = pawseyLdap.get_user_details_from_attribute(attribute = 'uidNumber', value = newid)
            if not len(user):
                break
        else:
            raise Exception('Difficulty allocating an LDAP uidNumber for ParticipantAccount=%s.'\
                'Tried %s - %s, but they were all unavailable in ldap'%(self.id, self.id + offset, newid))
        
        if ( (self.uidNumber != newid) or (self.gidNumber != newid)):
            self.uidNumber = newid
            self.gidNumber = newid
            self.save()
        
        return newid

    def __unicode__(self):
        #return self.uid   #TODO: relate this back to the Person to get name.
        try:
            personName = ("%s %s" % (self.person.last().firstName, self.person.last().surname))
        except:
            personName = "No person attached"
        return personName

class PersonStatus(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.name

class Person(models.Model):
    STATUS = {
        'NEW': 1,
        'EMAIL_SENT': 2,
        'DETAILS_FILLED': 3,
        'ACCOUNT_CREATED': 4,
        'ACCOUNT_CREATED_EMAIL_SENT': 5,
        'SUSPENDED': 6,
    }

    firstName = models.CharField(max_length=32, verbose_name='First Name')
    surname = models.CharField(max_length=32)
    institution = models.ForeignKey(Institution)
    institutionEmail = models.EmailField(max_length=64, verbose_name='Institution Email')
    preferredEmail = models.EmailField(max_length=64, null=True, blank=True, verbose_name='Alternative Email')
    phone = models.CharField(max_length=32, null=True, blank=True)
    mobilePhone = models.CharField(max_length=32, null=True, blank=True, verbose_name='Mobile Phone')
    student = models.BooleanField(default = False)
    personAccount = models.ForeignKey('PersonAccount', null=True, blank=True, related_name='person')    
    accountEmailHash = models.CharField(max_length=50, null=True, blank=True, verbose_name='Account Email Hash')
    status = models.ForeignKey(PersonStatus, default=STATUS['NEW'])
    accountEmailOn = models.DateTimeField(null=True, blank=True, verbose_name='Account Creation Email On')
    accountCreatedOn = models.DateTimeField(null=True, blank=True, verbose_name='Account Created On')
    accountCreatedEmailOn = models.DateTimeField(null=True, blank=True, verbose_name='Account Created Email On')

    def save(self, *args, **kwargs):
        instance = getattr(self, 'instance', None)
        if not self.pk:
            personAccount = PersonAccount()
            persons = Person.objects.filter(institutionEmail=self.institutionEmail)
            if len(persons) > 0:
                # Existing persons with this email address
                # Attempt to re-use existing personAccount records before
                # creating a new empty one.
                existing_person = persons[0]
                if existing_person.personAccount:
                    personAccount = existing_person.personAccount
                else:
                    personAccount = PersonAccount()
            personAccount.save()
            self.personAccount = personAccount
        super(Person, self).save(*args, **kwargs)

    def displayName(self):
        return self.firstName + ' ' + self.surname

    def projectList(self):
        return self.project_set.all()

    def __unicode__(self):
        return self.displayName()

class Project(models.Model):
    code = models.CharField(max_length=32, null=True, blank=True)
    title = models.CharField(max_length=1024)
    principalInvestigator = models.ForeignKey(Person, related_name='pi', verbose_name='Principal Investigator')
    summary = models.TextField(null=True, blank=True)
    people = models.ManyToManyField(Person)

    def activeAllocations(self):
        today = date.today()
        allocations = self.allocation_set.filter(start__lte=date.today()).filter(end__gte=date.today()).exclude(suspend='True')
        return allocations

    def __unicode__(self):
        return self.title

class PriorityArea(models.Model):
    name = models.CharField(max_length = 256)
    code = models.CharField(max_length = 256)

    def __unicode__(self):
        return self.name

class AllocationRound(models.Model):
        system = models.ForeignKey(Service)
        start_date = models.DateField()
        end_date = models.DateField()
        name = models.CharField(max_length = 512, null = True, blank = True)
        priority_area = models.ManyToManyField(PriorityArea)

        def status(self):
            today = date.today()
            if today >= self.start_date and today <= self.end_date:
                return "open"
            elif today <= self.start_date:
                return "pending"
            else:
                return "closed"

        def __unicode__(self):
            if self.name and len(self.name):
                label = self.name
            else:
                label = self.system
            return "%s: %s to %s" % (label, self.start_date.strftime('%d %b %Y'),
                    self.end_date.strftime('%d %b %Y'))

class Allocation(models.Model):
    name = models.CharField(max_length=256)
    project = models.ForeignKey(Project)
    start = models.DateField()
    end = models.DateField()
    permanent = models.BooleanField(default = False)
    priorityArea = models.ForeignKey(PriorityArea, verbose_name = 'Priority Area', null = True, blank = True)
    serviceunits = models.IntegerField(null = True, blank = True)
    service = models.ForeignKey(Service)
    suspend = models.BooleanField(default = False)
    allocation_round = models.ForeignKey(AllocationRound)

    def startQuarter(self):
        return str(self.start.year) + 'Q' + str((self.start.month-1)//3 + 1)

    def endQuarter(self):
        return str(self.end.year) + 'Q' + str((self.end.month-1)//3 + 1)

    def startYear(self):
        return self.start.year

    def endYear(self):
        return self.end.year

    def active(self):
        today = date.today()
        if today >= self.start and today <=self.end:
            return true
        return false

    def __unicode__(self):
        return self.name

class Filesystem(models.Model):
    name = models.CharField(max_length=32)
    quotad = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class AllocationFilesystem(models.Model):
    filesystem = models.ForeignKey(Filesystem)
    allocation = models.ForeignKey(Allocation)
    quota = models.IntegerField(default = 0)

    def __unicode__(self):
        return self.filesystem.name

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, help_text=help_text_emailtemplate_name)
    subject = models.CharField(max_length=100, help_text=help_text_emailtemplate_subject)
    template = models.CharField(max_length=8192, blank=True, help_text=help_text_emailtemplate_template)

    def render_to_string(self, template_vars):
        django_engine = engines['django']
        html_template = django_engine.from_string(self.template)
        context = Context(template_vars)
        html_body = html_template.render(context)
        return (
            self.subject,
            html_body
        )

    def __unicode__(self):
        return self.name
