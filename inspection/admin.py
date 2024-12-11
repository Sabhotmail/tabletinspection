from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Branch, DeviceInspection, Saleman
from django.utils.html import format_html

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'branchcode', 'branchname', 'address')  # แสดงฟิลด์ในหน้า Admin
    search_fields = ('branchcode', 'branchname')  # เพิ่มช่องค้นหาตาม branchcode และ branchname
    list_filter = ('branchname',)  # เพิ่มตัวกรองจาก branchname
    ordering = ('branchname',)  # เรียงลำดับตาม branchname


@admin.register(Saleman)
class SalemanAdmin(admin.ModelAdmin):
    list_display = ('id', 'salemancode', 'salemanname', 'branch', 'status')  # แสดง status
    search_fields = ('salemancode', 'salemanname', 'branch__branchname')
    list_filter = ('branch', 'status')  # เพิ่มตัวกรอง status
    ordering = ('salemancode',)


@admin.register(DeviceInspection)
class DeviceInspectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'saleman', 'device_type', 'sn', 'condition', 'image_preview', 'inspected_at')
    search_fields = ('branch__branchname', 'saleman__salemanname', 'device_type', 'sn')  # ค้นหาตาม branch, saleman, device_type, sn
    list_filter = ('device_type', 'condition', 'branch')  # ตัวกรอง device_type, condition, branch
    date_hierarchy = 'inspected_at'  # กรองตามวันที่
    readonly_fields = ('inspected_at',)  # กำหนดให้ inspected_at เป็น readonly

    def save_model(self, request, obj, form, change):
        if obj.saleman.branch != obj.branch:
            raise ValidationError("The selected Saleman does not belong to the selected Branch.")
        super().save_model(request, obj, form, change)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: auto;">', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"




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
