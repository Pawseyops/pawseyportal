from django.contrib import admin

from .models import *
from admin_forms import *
import account_services
import admin_widgets
from ajax_select.admin import *


class PersonProjectInline(admin_widgets.ImproveRawIdFieldsInline):
    model = Project.people.through
    raw_id_fields = ('person',)
    readonly_fields = ['institution', 'status']
    def status(self, instance):
        return instance.person.status
    status.short_description = 'Status'
    def institution(self, instance):
        return instance.person.institution.name
    institution.short_description = 'Institution'
    extra = 3

class FilesystemInline(admin.TabularInline):
    model = AllocationFilesystem
    extra = 2

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner')

class PersonAdmin(admin.ModelAdmin):
    list_display = ('displayName', 'institution', 'preferredEmail') 
    actions = ['send_account_request_email', 'send_account_created_email' ]
    exclude = ['personAccount']

    def send_account_request_email(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)

        for id in selected:
            person = Person.objects.get(id=id)
            account_services.send_account_request_mail(person, request)
            
        message = "Account request email sent to %s people" % len(selected)
        self.message_user(request, message)

    send_account_request_email.short_description = "Send account request details email to selected People."

    def send_account_created_email(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)

        for id in selected:
            person = Person.objects.get(id=id)
            account_services.send_account_created_notification_mail(person, request)
            
        message = "Account created notification email sent to %s people" % len(selected)
        self.message_user(request, message)

    send_account_created_email.short_description = "Send account created notification email to selected People."

class ProjectAdmin(AjaxSelectAdmin):
    inlines = [PersonProjectInline]
    #exclude = ['people']
    list_display = ('code', 'title', 'principalInvestigator')
    filter_horizontal = ['people']
    form = ProjectAdminForm

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

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')
    form = EmailTemplateForm

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
admin.site.register(EmailTemplate,EmailTemplateAdmin)
