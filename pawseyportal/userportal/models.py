from django.db import models
from pawseyportal.userportal.help_text import *

# Models for Projects, people, accounts.
class ServiceType(models.Model):
    name = models.CharField(max_length=32)
    helpEmail = models.EmailField(max_length=254)

    def __unicode__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=32)
    type = models.ForeignKey(ServiceType)

    def __unicode__(self):
        return self.name

class Institution(models.Model):
    name = models.CharField(max_length=100)
    partner = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class PersonAccount(models.Model):
    uid = models.CharField(max_length=256)
    uidNumber = models.IntegerField()
    gidNumber = models.IntegerField()
    passwordHash = models.CharField(('password'), max_length=256, null=True, blank=True)

    def __unicode(self):
        return self.uid   #TODO: relate this back to the Person to get name.

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

    firstName = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    institution = models.ForeignKey(Institution)
    institutionEmail = models.EmailField(max_length=64)
    preferredEmail = models.EmailField(max_length=64)
    phone = models.CharField(max_length=32)
    student = models.BooleanField(default = False)
    personAccount = models.ForeignKey('PersonAccount', null=True, related_name='person')    
    accountEmailHash = models.CharField(max_length=50, null=True, blank=True)
    status = models.ForeignKey(PersonStatus, default=STATUS['NEW'])
    accountEmailOn = models.DateTimeField(null=True, blank=True)
    accountCreatedOn = models.DateTimeField(null=True, blank=True)
    accountCreatedEmailOn = models.DateTimeField(null=True, blank=True)

    def displayName(self):
        return self.firstName + ' ' + self.surname

    def projectList(self):
        return self.project_set.all()

    def __unicode__(self):
        return self.displayName()

class Project(models.Model):
    code = models.CharField(max_length=32)
    title = models.CharField(max_length=256)
    principalInvestigator = models.ForeignKey(Person, related_name='pi')
    summary = models.TextField()
    people = models.ManyToManyField(Person)

    def __unicode__(self):
        return self.title

class PriorityArea(models.Model):
    name = models.CharField(max_length=32)
    code = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

class AllocationRound(models.Model):
        system = models.ForeignKey(Service)
        start_date = models.DateField()
        end_date = models.DateField()
        name = models.CharField(max_length=512, null=True, blank=True)
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
    priorityArea = models.ForeignKey(PriorityArea)
    serviceunits = models.IntegerField()
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

    def __unicode__(self):
        return self.name
