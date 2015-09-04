from django.db import models

# Create your models here.
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


class Person(models.Model):
    firstName = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    institution = models.ForeignKey(Institution)
    institutionEmail = models.EmailField(max_length=64)
    preferredEmail = models.EmailField(max_length=64)
    phone = models.CharField(max_length=32)
    student = models.BooleanField(default = False)
    suspend = models.BooleanField(default = False)
    personAccount = models.ForeignKey('PersonAccount', null=True, related_name='person')    

    def displayName(self):
        return self.firstName + ' ' + self.surname

    def __unicode__(self):
        return self.displayName()

class Project(models.Model):
    code = models.CharField(max_length=32)
    title = models.CharField(max_length=200)
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

class Allocation(models.Model):
    name = models.CharField(max_length=32)
    project = models.ForeignKey(Project)
    start = models.DateField()
    end = models.DateField()
    permanent = models.BooleanField(default = False)
    priorityArea = models.ForeignKey(PriorityArea)
    serviceunits = models.IntegerField()
    service = models.ForeignKey(Service)
    suspend = models.BooleanField(default = False)

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

