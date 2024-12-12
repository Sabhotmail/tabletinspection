from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import DeviceInspection, User, Branch, Saleman
from django.core.exceptions import ValidationError

class DeviceInspectionForm(forms.ModelForm):
    class Meta:
        model = DeviceInspection
        fields = ['branch', 'saleman', 'device_type', 'sn', 'condition', 'remarks', 'image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ดึงข้อมูล user ที่ส่งเข้ามาใน form
        print(f"User passed to form: {user}")
        super().__init__(*args, **kwargs)

        if user:
            if user.is_superuser:
                # ถ้าเป็น admin ให้เห็นทุก branch และ saleman
                print("Admin detected, showing all branches and salemen.")
                self.fields['branch'].queryset = Branch.objects.all()
                self.fields['saleman'].queryset = Saleman.objects.filter(status='active',)  # เฉพาะ Saleman ที่ active
            elif user.branch:
                # ถ้าไม่ใช่ admin ให้กรองตาม branch ของ user
                print(f"Filtering Branch for user: {user.branch}")
                self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
                self.fields['saleman'].queryset = Saleman.objects.filter(branch=user.branch, status='active')
            else:
                # ถ้า user ไม่มี branch
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