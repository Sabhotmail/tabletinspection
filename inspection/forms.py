from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import DeviceInspection, User, Branch, Salesman, InspectionSchedule
from django.core.exceptions import ValidationError

class DeviceInspectionForm(forms.ModelForm):
    class Meta:
        model = DeviceInspection
        fields = [
            'branch', 
            'salesman', 
            'device_type', 
            'sn', 
            'condition', 
            'charger_status_tablet',  # สถานะสายชาร์จ Tablet
            'charger_status_printer',  # สถานะสายชาร์จ Printer
            'bag_status',  # สถานะกระเป๋า
            'tablet_image', 
            'charger_image_tablet', 
            'charger_image_printer', 
            'bag_image',
            'printer_image',
            'remarks',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter branch and saleman fields based on user
        if user and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['salesman'].queryset = Salesman.objects.filter(branch=user.branch, status='active')
        else:
            self.fields['branch'].queryset = Branch.objects.none()
            self.fields['salesman'].queryset = Salesman.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        # Prevent changes to branch, device_type, and sn
        if self.instance.pk:  # Check if this is an update
            if cleaned_data.get('branch') != self.instance.branch:
                raise ValidationError("Branch cannot be changed.")
            if cleaned_data.get('device_type') != self.instance.device_type:
                raise ValidationError("Device Type cannot be changed.")
            if cleaned_data.get('sn') != self.instance.sn:
                raise ValidationError("Serial Number (SN) cannot be changed.")

        return cleaned_data



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'branch']

class InspectionScheduleForm(forms.ModelForm):
    class Meta:
        model = InspectionSchedule
        fields = ['period', 'start_time', 'end_time', 'description']  # เพิ่มฟิลด์ 'period' และ 'description'
        widgets = {
            'period': forms.TextInput(attrs={
                'placeholder': 'YYYY-MM',
                'class': 'form-control',
            }),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Add a description for the schedule (optional)',
            }),
        }
