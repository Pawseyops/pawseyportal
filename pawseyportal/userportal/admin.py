from django.contrib import admin

from .models import *
from admin_forms import *
import account_services
import admin_widgets
from ajax_select.admin import *
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode

class ProjectCommentsInline(admin.TabularInline):
    model = Comment
    exclude = ['allocation','user']
    readonly_fields = ['commenter_name']
    extra = 1
    
    def commenter_name(self,instance):
        if instance.user is None:
            return mark_safe(u'<span></span>')
        else:
            return mark_safe(u'<span>%s %s</span>' % (conditional_escape(force_unicode(instance.user.first_name)), conditional_escape(force_unicode(instance.user.last_name))))
            
class AllocationCommentsInline(admin.TabularInline):
    model = Comment
    exclude = ['project', 'user']
    readonly_fields = ['commenter_name']
    extra = 1

    def commenter_name(self,instance):
        if instance.user is None:
            return mark_safe(u'<span></span>')
        else:
            return mark_safe(u'<span>%s %s</span>' % (conditional_escape(force_unicode(instance.user.first_name)), conditional_escape(force_unicode(instance.user.last_name))))

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

class AllocationInline(admin.TabularInline):
    model = Allocation
    extra = 0
    show_change_link = True
    can_delete = False
    readonly_fields = ['permanent', 'priorityArea', 'serviceunits']

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner')
    search_fields = ['^name']

class PersonAdmin(admin.ModelAdmin):
    list_display = ('displayName', 'institution', 'preferredEmail', 'status') 
    list_filter = ['status']
    actions = ['send_account_request_email', 'send_account_created_email' ]
    exclude = ['personAccount', 'accountEmailHash' ]
    readonly_fields = ['status', 'accountEmailOn', 'accountCreatedOn', 'accountCreatedEmailOn']
    search_fields = ['^firstName', '^surname'] 

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
    inlines = [AllocationInline, ProjectCommentsInline]

    list_display = ('code', 'title', 'principalInvestigator')
    filter_horizontal = ['people']
    form = ProjectAdminForm
    search_fields = ['^code', '^title']

    def save_formset(self, request, form, formset, change): 
        if formset.model == Comment:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.save()
        else:
            formset.save()

class AllocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'startQuarter', 'endQuarter', 'permanent')
    list_filter = ['start','end']
    search_fields = ['^name', '^project__code']

    inlines = [FilesystemInline, AllocationCommentsInline]

    def save_formset(self, request, form, formset, change): 
        if formset.model == Comment:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
            instance.save()
        else:
            formset.save()

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
