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
    
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    saleman = models.ForeignKey('Saleman', on_delete=models.SET_NULL, null=True, blank=True)
    device_type = models.CharField(max_length=50, choices=[('Tablet', 'Tablet'), ('Printer', 'Printer')])
    sn = models.CharField(max_length=100, unique=True, blank=True, null=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    remarks = models.TextField(blank=True, null=True)
    inspected_at = models.DateTimeField(auto_now_add=True)

    # Charger and Bag
    charger_status_tablet = models.CharField(
        max_length=10, choices=CONDITION_CHOICES, default='ปกติ', verbose_name="Tablet Charger Status"
    )
    charger_status_printer = models.CharField(
        max_length=10, choices=CONDITION_CHOICES, default='ปกติ', verbose_name="Printer Charger Status"
    )
    bag_status = models.CharField(
        max_length=10, choices=CONDITION_CHOICES, default='ปกติ', blank=True, null=True, verbose_name="Bag Status"
    )

    # Images
    tablet_image = models.ImageField(upload_to='uploads/tablet_images/', blank=True, null=True)
    charger_image_tablet = models.ImageField(upload_to='uploads/charger_images/', blank=True, null=True)
    charger_image_printer = models.ImageField(upload_to='uploads/charger_images/', blank=True, null=True)
    bag_image = models.ImageField(upload_to='uploads/bag_images/', blank=True, null=True)
    printer_image = models.ImageField(upload_to='uploads/printer_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Clear bag_status if device_type is not Tablet
        if self.device_type != 'Tablet':
            self.bag_status = None
        super().save(*args, **kwargs)