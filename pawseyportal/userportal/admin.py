from django.contrib import admin

# Register your models here.
from .models import *

class PersonProjectInline(admin.TabularInline):
    model = Person
    extra = 3

class FilesystemInline(admin.TabularInline):
    model = AllocationFilesystem
    extra = 2

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner')

class PersonAdmin(admin.ModelAdmin):
    list_display = ('displayName', 'institution', 'preferredEmail') 

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'principalInvestigator')

class AllocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'startQuarter', 'endQuarter', 'permanent')
    list_filter = ['start','end']

    inlines = [FilesystemInline]

class PriorityAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'helpEmail')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')

class AllocationRoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'start_date', 'end_date')

admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Allocation, AllocationAdmin)
admin.site.register(PriorityArea, PriorityAreaAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Filesystem)
admin.site.register(PersonAccount)
admin.site.register(AllocationRound, AllocationRoundAdmin)
