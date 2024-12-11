from django.contrib.auth.models import AbstractUser
from django.db import models

class Branch(models.Model):
    branchcode = models.CharField(max_length=100)
    branchname = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return f"{self.branchname} ({self.branchcode})"

class User(AbstractUser):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username

class Saleman(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)  # เชื่อมกับ Branch
    salemancode = models.CharField(max_length=50, unique=True)  # รหัส Saleman
    salemanname = models.CharField(max_length=100)  # ชื่อ Saleman
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')  # สถานะ

    def __str__(self):
        return f"{self.salemancode} - {self.salemanname}"

class DeviceInspection(models.Model):
    CONDITION_CHOICES = [
        ('ปกติ', 'ปกติ'),
        ('ชำรุด', 'ชำรุด'),
    ]
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    saleman = models.ForeignKey(Saleman, on_delete=models.SET_NULL, null=True, blank=True)  # เชื่อมกับ Saleman
    device_type = models.CharField(max_length=50, choices=[('Tablet', 'Tablet'), ('Printer', 'Printer')])
    sn = models.CharField(max_length=100,null=True,blank=True,unique=True)  # Serial Number
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)  # ใช้ choices
    remarks = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    inspected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.branch} - {self.device_type} ({self.condition})"
