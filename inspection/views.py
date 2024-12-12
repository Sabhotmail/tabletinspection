from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import DeviceInspection,Saleman, Branch
from .forms import DeviceInspectionForm, CustomUserCreationForm
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate



@login_required
def inspection_list(request):
    # ตรวจสอบว่าผู้ใช้เป็น admin หรือไม่
    if request.user.is_superuser:  
        inspections = DeviceInspection.objects.all()  # Admin เห็นข้อมูลทุกสาขา
    else:
        inspections = DeviceInspection.objects.filter(branch=request.user.branch)  # ผู้ใช้ธรรมดาเห็นเฉพาะ branch ของตัวเอง
    
    return render(request, 'inspection/inspection_list.html', {'inspections': inspections})



@login_required
def create_inspection(request):
    if request.method == 'POST':
        form = DeviceInspectionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Inspection created successfully!")
            return redirect('inspection_list')  # เปลี่ยน URL ไปยังหน้าที่ต้องการหลังบันทึก
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        form = DeviceInspectionForm(user=request.user)
    return render(request, 'inspection/create_inspection.html', {'form': form})

@login_required
def edit_inspection(request, pk):
    # ดึงข้อมูลที่ตรงกับ branch ของผู้ใช้
    inspection = get_object_or_404(DeviceInspection, pk=pk)

    if request.method == 'POST':
        form = DeviceInspectionForm(request.POST, request.FILES, instance=inspection, user=request.user)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.save()
            return redirect('inspection_list')  # เปลี่ยน URL นี้ตามต้องการ
    else:
        form = DeviceInspectionForm(instance=inspection, user=request.user)

    return render(request, 'inspection/edit_inspection.html', {'form': form, 'inspection': inspection})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')  # เปลี่ยน URL ตามหน้าหลักของคุณ
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    # Statistics
    total_devices = DeviceInspection.objects.count()
    broken_devices = DeviceInspection.objects.filter(condition='ชำรุด').count()
    normal_devices = DeviceInspection.objects.filter(condition='ปกติ').count()
    active_saleman = Saleman.objects.filter(status='active').count()

    # Branch-wise Statistics
    branch_stats = Branch.objects.annotate(
        total_devices=Count('deviceinspection'),
        broken_devices=Count('deviceinspection', filter=Q(deviceinspection__condition='ชำรุด')),
        normal_devices=Count('deviceinspection', filter=Q(deviceinspection__condition='ปกติ'))
    )

    # Inspections Over Time
    inspections = (
        DeviceInspection.objects.annotate(day=TruncDate('inspected_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    inspection_dates = [inspection['day'].strftime('%Y-%m-%d') for inspection in inspections]
    inspection_counts = [inspection['count'] for inspection in inspections]

    # Prepare Pie Chart Data
    pie_data = {
        'labels': ['Normal', 'Broken'],
        'data': [normal_devices, broken_devices],
        'backgroundColor': ['#28a745', '#dc3545'],
        'hoverBackgroundColor': ['#218838', '#c82333']
    }

    # Prepare Branch Statistics for Chart
    branch_names = [branch.branchname for branch in branch_stats]
    total_devices_list = [branch.total_devices for branch in branch_stats]
    normal_devices_list = [branch.normal_devices for branch in branch_stats]
    broken_devices_list = [branch.broken_devices for branch in branch_stats]

    branch_chart_data = {
        'labels': branch_names,
        'datasets': [
            {
                'label': 'Total Devices',
                'data': total_devices_list,
                'backgroundColor': 'rgba(78, 115, 223, 0.5)',
                'borderColor': 'rgba(78, 115, 223, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Normal Devices',
                'data': normal_devices_list,
                'backgroundColor': 'rgba(40, 167, 69, 0.5)',
                'borderColor': 'rgba(40, 167, 69, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Broken Devices',
                'data': broken_devices_list,
                'backgroundColor': 'rgba(220, 53, 69, 0.5)',
                'borderColor': 'rgba(220, 53, 69, 1)',
                'borderWidth': 1
            }
        ]
    }

    context = {
        'total_devices': total_devices,
        'broken_devices': broken_devices,
        'normal_devices': normal_devices,
        'active_saleman': active_saleman,
        'inspection_dates': inspection_dates,
        'inspection_counts': inspection_counts,
        'pie_data': pie_data,  # Pie chart data
        'branch_chart_data': branch_chart_data,  # Branch statistics chart data
        'branch_stats': branch_stats,
    }
    return render(request, 'dashboard.html', context)


@login_required
def delete_inspection(request, inspection_id):
    inspection = get_object_or_404(DeviceInspection, id=inspection_id)
    if request.method == 'POST':
        inspection.delete()
        messages.success(request, "Inspection deleted successfully!")
        return redirect('inspection_list')
    return render(request, 'inspection/confirm_delete.html', {'inspection': inspection})
