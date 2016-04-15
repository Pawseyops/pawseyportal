from django import forms
from pawseyportal.userportal.models import *
import account_services

class PersonAccountForm(forms.Form):
    firstName = forms.CharField(max_length=256 )
    lastName = forms.CharField(max_length=256)
    institution = forms.ModelChoiceField(queryset=Institution.objects.all()) 
    phone = forms.CharField(max_length=256, label='Phone number', required=False)
    mobilePhone = forms.CharField(max_length=256, label='Mobile Phone number (useful for password resets)', required=False)
    uid = forms.CharField(max_length=50, label='Desired username for logging on to Pawsey systems')
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False), label='Desired password')
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label='Password (again)')

    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                            label='I have read and agree to the Conditions of Use',
                            error_messages={'required': "You must agree to the terms to register"      })

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        if 'uid' in self.cleaned_data:
            self.cleaned_data['uid'] = self.cleaned_data['uid'].lower()
            if not account_services.check_unique_uid(self.cleaned_data['uid'], ):
                raise forms.ValidationError("The uid you requested is already taken")
        return self.cleaned_data 
