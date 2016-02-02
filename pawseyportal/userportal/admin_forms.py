from django import forms
from django.contrib.auth.models import User, Group
from models import *
from datetime import datetime

class EmailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailTemplateForm, self).__init__(*args, **kwargs)
        self.fields["template"].widget = forms.Textarea(attrs={'rows':30, 'cols':80})
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'template']

class ProjectAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['people'].queryset = Person.objects.distinct('institutionEmail')
    class Meta:
        model = Project
        fields = ['code', 'title', 'principalInvestigator', 'summary', 'people']

