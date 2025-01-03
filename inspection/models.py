from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

class Branch(models.Model):
    branchcode = models.CharField(max_length=100)
    branchname = models.CharField(max_length=100)
    address = models.TextField()

    class Meta:
        db_table = 'branch'

    def __str__(self):
        return f"{self.branchname} ({self.branchcode})"

class User(AbstractUser):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        db_table = 'auth_user'

    
class Salesman(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)  # เชื่อมกับ Branch
    salesmancode = models.CharField(max_length=50, unique=True)  # รหัส Saleman
    salesmanname = models.CharField(max_length=100)  # ชื่อ Saleman
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')  # สถานะ

    class Meta:
        db_table = 'salesman'

    def __str__(self):
        return f"{self.salesmancode} - {self.salesmanname}"

class DeviceInspection(models.Model):
    CONDITION_CHOICES = [
        ('ปกติ', 'ปกติ'),
        ('ชำรุด', 'ชำรุด'),
    ]
    
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    salesman = models.ForeignKey('Salesman', on_delete=models.SET_NULL, null=True, blank=True)
    device_type = models.CharField(max_length=50, choices=[('Tablet', 'Tablet'), ('Printer', 'Printer')])
    sn = models.CharField(max_length=100, blank=True, null=True)  # ลบ unique=True
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

    # Add Period
    schedule = models.ForeignKey('InspectionSchedule', on_delete=models.CASCADE, related_name="inspections", blank=True, null=True)
    period = models.CharField(max_length=7, blank=True, null=True)  # เช่น '2024-12'

    def save(self, *args, **kwargs):
        # Clear bag_status if device_type is not Tablet
        if self.device_type != 'Tablet':
            self.bag_status = None
        
        # ดึง Period จาก Schedule ถ้ายังไม่มีค่า
        if self.schedule and not self.period:
            self.period = self.schedule.period
        
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'deviceinspection'
        constraints = [
            models.UniqueConstraint(fields=['sn', 'period'], name='unique_sn_period')
        ]


class InspectionSchedule(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    period = models.CharField(max_length=7, unique=True)  # เช่น '2024-12'
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    description = models.TextField(blank=True, null=True)

    def update_status(self):
        """อัปเดตสถานะตามเวลาปัจจุบัน"""
        current_time = now()
        if self.start_time > current_time:
            self.status = 'upcoming'
        elif self.start_time <= current_time <= self.end_time:
            self.status = 'active'
        else:
            self.status = 'closed'

    def save(self, *args, **kwargs):
        """ปรับปรุงสถานะก่อนบันทึก"""
        self.update_status()  # อัปเดตสถานะก่อนบันทึก
        super(InspectionSchedule, self).save(*args, **kwargs)

    def __str__(self):
        return f"Period: {self.period} ({self.get_status_display()})"
    class Meta:
        db_table = 'inspectionschedule'