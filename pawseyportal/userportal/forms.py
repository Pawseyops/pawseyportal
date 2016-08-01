from django import forms
from pawseyportal.userportal.models import *
import account_services
import pawseyportal.userportal.help_text as help_text

class PersonAccountForm(forms.Form):
    firstName = forms.CharField(max_length=256 )
    lastName = forms.CharField(max_length=256)
    institution = forms.ModelChoiceField(queryset=Institution.objects.all()) 
    phone = forms.CharField(max_length=256, label='Phone number', required=False)
    mobilePhone = forms.CharField(max_length=256, label='Mobile Phone number (useful for password resets)', required=False)
    uid = forms.CharField(max_length=50, label='Desired username for logging on to Pawsey systems')

    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                            label='I have read and agree to the Conditions of Use',
                            error_messages={'required': "You must agree to the terms to register"      })

    def clean(self):
        if 'uid' in self.cleaned_data:
            self.cleaned_data['uid'] = self.cleaned_data['uid'].lower()
            if not account_services.check_unique_uid(self.cleaned_data['uid'], ):
                raise forms.ValidationError("The uid you requested is already taken")
        return self.cleaned_data 
 
class PersonForm(forms.Form):
    firstName = forms.CharField(max_length=256, label='First Name', help_text = help_text.person_firstname)
    lastName = forms.CharField(max_length=256, label='Last Name', help_text = help_text.person_surname)
    institutionEmail = forms.EmailField(label='Institution Email', help_text = help_text.person_institution_email)
    institution = forms.ModelChoiceField(queryset=Institution.objects.all(), help_text = help_text.person_institution)
    student = forms.BooleanField(required=False, help_text = help_text.person_student)
