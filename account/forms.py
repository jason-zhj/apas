__author__ = 'Administrator'
from django import forms
from .models import StudentGroup,StudentUserProfile
from django.contrib.auth.models import User
from appglobal.helper import get_or_none

class UserGroupForm(forms.ModelForm):
    class Meta:
        model=StudentGroup

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=('username','password','email',)
        widgets = {
            'password': forms.PasswordInput(),
        }
        # exclude=['is_staff','is_active','date_joined']

    def save(self, commit=True):
        user=super(UserForm,self).save(commit=commit)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model=StudentUserProfile
        exclude=['user']

class ChangePasswordForm(forms.Form):
    old_password=forms.CharField(widget=forms.PasswordInput)
    new_password=forms.CharField(widget=forms.PasswordInput)
    new_password_again=forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """
        check whether the 'new_password' and 'new_password_again' are equal
        :raise ValidationError if not
        """
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_password_again=cleaned_data.get('new_password_again')
        new_password=cleaned_data.get('new_password')
        if (new_password != new_password_again):
            raise forms.ValidationError("New password is not consistent")
