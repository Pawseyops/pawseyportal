from django.db import models
import pawseyportal.userportal.help_text as help_text
from ldap_helper import *
from django.template import engines, Context
from datetime import date
from django.contrib.auth.models import User

# Models for Projects, people, accounts.
class ServiceType(models.Model):
    name = models.CharField(max_length=256, help_text = help_text.servicetype_name)
    helpEmail = models.EmailField(max_length=254, help_text = help_text.servicetype_help_email)

    def __unicode__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=256, help_text = help_text.service_name)
    type = models.ForeignKey(ServiceType, help_text = help_text.service_type)

    def __unicode__(self):
        return self.name

class Institution(models.Model):
    name = models.CharField(max_length=256, help_text = help_text.institution_name)
    partner = models.BooleanField(default = False, help_text = help_text.institution_partner)

    def __unicode__(self):
        return self.name

class PersonAccount(models.Model):
    uid = models.CharField(max_length=256, null=True, blank=True, help_text = help_text.personaccount_uid)
    uidNumber = models.IntegerField(null=True, blank=True, help_text = help_text.personaccount_uidnumber)
    gidNumber = models.IntegerField(null=True, blank=True, help_text = help_text.personaccount_gidnumber)
    passwordHash = models.CharField(('password'), max_length=256, null=True, blank=True, help_text = help_text.personaccount_passwordhash)

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
        try:
            personName = ("%s %s" % (self.person.last().firstName, self.person.last().surname))
        except:
            personName = "No person attached"
        return personName

class PersonStatus(models.Model):
    name = models.CharField(max_length=50, help_text = help_text.personstatus_name)
    description = models.CharField(max_length=256, null=True, blank=True, help_text = help_text.personstatus_description)

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

    firstName = models.CharField(max_length=32, verbose_name='First Name', help_text = help_text.person_firstname)
    surname = models.CharField(max_length=32, help_text = help_text.person_surname)
    institution = models.ForeignKey(Institution, help_text = help_text.person_institution)
    institutionEmail = models.EmailField(max_length=64, verbose_name='Institution Email', help_text = help_text.person_institution_email)
    preferredEmail = models.EmailField(max_length=64, null=True, blank=True, verbose_name='Alternative Email', help_text = help_text.person_alternate_email)
    phone = models.CharField(max_length=32, null=True, blank=True, help_text = help_text.person_phone)
    mobilePhone = models.CharField(max_length=32, null=True, blank=True, verbose_name='Mobile Phone', help_text = help_text.person_mobilephone)
    student = models.BooleanField(default = False, help_text = help_text.person_student)
    personAccount = models.ForeignKey('PersonAccount', null=True, blank=True, related_name='person', help_text = help_text.person_personaccount)    
    accountEmailHash = models.CharField(max_length=50, null=True, blank=True, verbose_name='Account Email Hash', help_text = help_text.person_accountemailhash)
    status = models.ForeignKey(PersonStatus, default=STATUS['NEW'], help_text = help_text.person_status)
    accountEmailOn = models.DateTimeField(null=True, blank=True, verbose_name='Account Creation Email On', help_text = help_text.person_accountemailon)
    detailsFilledOn = models.DateTimeField(null=True, blank=True, verbose_name='Details Filled On', help_text = help_text.person_detailsfilledon)
    accountCreatedOn = models.DateTimeField(null=True, blank=True, verbose_name='Account Created On', help_text = help_text.person_accountcreatedon)
    accountCreatedEmailOn = models.DateTimeField(null=True, blank=True, verbose_name='Account Created Email On', help_text = help_text.person_accountcreatedemailon)

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
    code = models.CharField(max_length=32, null=True, blank=True, help_text = help_text.project_code)
    title = models.CharField(max_length=1024, help_text = help_text.project_title)
    principalInvestigator = models.ForeignKey(Person, related_name='pi', verbose_name='Principal Investigator', help_text = help_text.project_pi)
    summary = models.TextField(null=True, blank=True, help_text = help_text.project_summary)
    people = models.ManyToManyField(Person, help_text = help_text.project_people)

    def activeAllocations(self):
        today = date.today()
        allocations = self.allocation_set.filter(start__lte=date.today()).filter(end__gte=date.today()).exclude(suspend='True')
        return allocations

    def __unicode__(self):
        return self.title

class PriorityArea(models.Model):
    name = models.CharField(max_length = 256, help_text = help_text.priorityarea_name)
    code = models.CharField(max_length = 256, help_text = help_text.priorityarea_code)

    def __unicode__(self):
        return self.name

class AllocationRound(models.Model):
        system = models.ForeignKey(Service, help_text = help_text.allocationround_system)
        start_date = models.DateField(help_text = help_text.allocationround_start_date)
        end_date = models.DateField(help_text = help_text.allocationround_end_date)
        name = models.CharField(max_length = 512, null = True, blank = True, help_text = help_text.allocationround_name)
        priority_area = models.ManyToManyField(PriorityArea, help_text = help_text.allocationround_priority_area)

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
    name = models.CharField(max_length=256, help_text = help_text.allocation_name)
    project = models.ForeignKey(Project, help_text = help_text.allocation_project)
    start = models.DateField(help_text = help_text.allocation_start)
    end = models.DateField(help_text = help_text.allocation_end)
    permanent = models.BooleanField(default = False, help_text = help_text.allocation_permanent)
    priorityArea = models.ForeignKey(PriorityArea, verbose_name = 'Priority Area', null = True, blank = True, help_text = help_text.allocation_priorityarea)
    serviceunits = models.IntegerField(null = True, blank = True, help_text = help_text.allocation_serviceunits)
    service = models.ForeignKey(Service, help_text = help_text.allocation_service)
    suspend = models.BooleanField(default = False, help_text = help_text.allocation_suspend)
    allocation_round = models.ForeignKey(AllocationRound, help_text = help_text.allocation_allocation_round)

    def startQuarter(self):
        return str(self.start.year) + 'Q' + str((self.start.month-1)//3 + 1)

    def endQuarter(self):
        return str(self.end.year) + 'Q' + str((self.end.month-1)//3 + 1)

    def quarterLength(self):
        return (self.end - self.start).days/91

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

class Partition(models.Model):
    name = models.CharField(max_length=32, help_text = help_text.partition_name)

    def __unicode__(self):
        return self.name

class AllocationPartition(models.Model):
    partition = models.ForeignKey(Partition, help_text = help_text.allocationpartition_partition)
    allocation = models.ForeignKey(Allocation, help_text = help_text.allocationpartition_allocation)

    def __unicode__(self):
        return self.partition.name

class Filesystem(models.Model):
    name = models.CharField(max_length=32, help_text = help_text.filesystem_name)
    quotad = models.BooleanField(default = False, help_text = help_text.filesystem_quotad)

    def __unicode__(self):
        return self.name

class AllocationFilesystem(models.Model):
    filesystem = models.ForeignKey(Filesystem, help_text = help_text.allocationfilesystem_filesystem)
    allocation = models.ForeignKey(Allocation, help_text = help_text.allocationfilesystem_allocation)
    quota = models.IntegerField(default = 0, help_text = help_text.allocationfilesystem_quota)

    def __unicode__(self):
        return self.filesystem.name

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, help_text=help_text.emailtemplate_name)
    subject = models.CharField(max_length=100, help_text=help_text.emailtemplate_subject)
    template = models.CharField(max_length=8192, blank=True, help_text=help_text.emailtemplate_template)

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

class Comment(models.Model):
    comment =  models.TextField(null = True, blank = True, help_text = help_text.comment_comment)
    allocation = models.ForeignKey(Allocation, related_name = "allocation", null = True, blank = True)
    project = models.ForeignKey(Project, related_name = "project", null = True, blank = True)
    user = models.ForeignKey(User, related_name = "user", null = True, blank = True)

    def __unicode(self):
        return self.user

class ResearchClassification(models.Model):
    project = models.ForeignKey(Project)
    code = models.IntegerField(null=True, blank=True)
    percentage = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.code

class YamlDefaults(models.Model):
    defaults = models.TextField(null = True, blank = True, help_text = help_text.yamldefaults_defaults)

    class Meta:
        verbose_name_plural = 'Yaml defaults'
