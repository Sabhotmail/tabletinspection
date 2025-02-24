from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Branch, DeviceInspection, Salesman, InspectionSchedule
from django.utils.html import format_html
from django.utils.safestring import mark_safe

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'branchcode', 'branchname', 'address')  # แสดงฟิลด์ในหน้า Admin
    search_fields = ('branchcode', 'branchname')  # เพิ่มช่องค้นหาตาม branchcode และ branchname
    list_filter = ('branchname',)  # เพิ่มตัวกรองจาก branchname
    ordering = ('branchname',)  # เรียงลำดับตาม branchname


@admin.register(Salesman)
class SalesmansAdmin(admin.ModelAdmin):
    list_display = ('id', 'salesmancode', 'salesmanname', 'branch', 'status')  # แสดง status
    search_fields = ('salesmancode', 'salesmanname', 'branch__branchname')
    list_filter = ('branch', 'status')  # เพิ่มตัวกรอง status
    ordering = ('salesmancode',)


@admin.register(DeviceInspection)
class DeviceInspectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'salesman', 'device_type', 'sn', 'condition', 'inspected_at')
    search_fields = ('branch__branchname', 'salesman__salesmanname', 'device_type', 'sn')  # ค้นหาตาม branch, saleman, device_type, sn
    list_filter = ('device_type', 'condition', 'branch')  # ตัวกรอง device_type, condition, branch
    date_hierarchy = 'inspected_at'  # กรองตามวันที่
    readonly_fields = ('inspected_at',)  # กำหนดให้ inspected_at เป็น readonly

    def save_model(self, request, obj, form, change):
        if obj.salesman.branch != obj.branch:
            raise ValidationError("The selected Salesman does not belong to the selected Branch.")
        super().save_model(request, obj, form, change)



@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active', 'branch', 'date_joined')
    search_fields = ('username', 'email', 'branch__branchname')
    list_filter = ('is_staff', 'is_active', 'date_joined', 'branch')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'branch')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'branch', 'is_staff', 'is_active'),
        }),
    )

@admin.register(InspectionSchedule)
class InspectionScheduleAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'description')
    list_filter = ('start_time', 'end_time')
