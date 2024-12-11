from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import DeviceInspection, User, Branch, Saleman
from django.core.exceptions import ValidationError

class DeviceInspectionForm(forms.ModelForm):
    class Meta:
        model = DeviceInspection
        fields = ['branch', 'saleman', 'device_type', 'sn', 'condition', 'remarks', 'image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        print(f"User passed to form: {user}")
        super().__init__(*args, **kwargs)
        if user and user.branch:
            print(f"Filtering Branch for user: {user.branch}")
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['saleman'].queryset = Saleman.objects.filter(branch=user.branch, status='active')  # กรองเฉพาะ Active
        else:
            print("User has no branch or is not logged in.")
            self.fields['branch'].queryset = Branch.objects.none()
            self.fields['saleman'].queryset = Saleman.objects.none()

    def clean_sn(self):
        sn = self.cleaned_data['sn']
        if DeviceInspection.objects.filter(sn=sn).exists():
            raise forms.ValidationError("This Serial Number (SN) already exists.")
        return sn


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'branch']