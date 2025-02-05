from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import DeviceInspection,Salesman, Branch, InspectionSchedule
from .forms import DeviceInspectionForm, CustomUserCreationForm,InspectionScheduleForm
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils.timezone import now
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.template.loader import render_to_string
# from weasyprint import HTML
from django.http import JsonResponse

class CustomLoginView(LoginView):
    template_name = 'login.html'  # ชื่อไฟล์ Template ที่ใช้แสดงหน้า Login

    def form_invalid(self, form):
        # เพิ่มข้อความแจ้งเตือนเมื่อ Login ไม่สำเร็จ
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

# 
@login_required
def inspection_list(request):
    # รับค่าจาก Query Parameters
    selected_period = request.GET.get('period')
    selected_branch_code = request.GET.get('branch')  # รับค่า branch (เป็น branchcode)

    # ดึง branch ของ User ที่ล็อกอินอยู่
    user_branch = request.user.branch if hasattr(request.user, 'branch') else None

    # Query Inspections
    if request.user.is_staff:
        inspections = DeviceInspection.objects.all()  # Admin เห็นทุกสาขา
    else:
        inspections = DeviceInspection.objects.filter(branch=user_branch)  # จำกัดให้เห็นเฉพาะ branch ของตัวเอง

    # ค้นหา ID ของสาขาที่เลือก
    if request.user.is_staff and selected_branch_code:
        branch_obj = Branch.objects.filter(branchcode=selected_branch_code).first()
        if branch_obj:
            inspections = inspections.filter(branch=branch_obj.id)  # ใช้ ID ของ Branch ในการกรอง

    # กรองตาม period ถ้ามีการเลือก
    if selected_period:
        inspections = inspections.filter(period=selected_period)

    # ดึงรายชื่อสาขาทั้งหมด (สำหรับ Admin)
    all_branches = Branch.objects.values_list('branchcode', flat=True).distinct().order_by('branchcode')

    # ดึงรายชื่อ periods ทั้งหมด
    all_periods = InspectionSchedule.objects.values_list('period', flat=True).distinct().order_by('period')

    context = {
        'inspections': inspections,
        'all_branches': list(all_branches),  # ส่งรายชื่อสาขาทั้งหมดไปยัง template
        'all_periods': list(all_periods),  # ส่ง periods ทั้งหมดไปยัง template
        'selected_period': selected_period,  # ส่งค่า period ที่เลือก
        'selected_branch': selected_branch_code,  # ส่งค่า branch ที่เลือก
    }
    return render(request, 'inspection/inspection_list.html', context)


@login_required
def create_inspection(request):
    # เก็บเวลาปัจจุบัน
    current_time = now()
    print(f"Current time: {current_time}")

    # ตรวจสอบตารางเวลาปัจจุบัน
    schedule = InspectionSchedule.objects.filter(
        start_time__lte=current_time,
        end_time__gte=current_time
    ).first()

    if not schedule:
        print("No valid schedule found!")
        messages.error(
            request, 
            "The inspection form is currently closed. Please try again during the scheduled period."
        )
        return redirect('inspection_list')

    # Debug ตารางเวลา
    print(f"Schedule found: Start - {schedule.start_time}, End - {schedule.end_time}, Period - {schedule.period}")

    if request.method == 'POST':
        form = DeviceInspectionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # ตรวจสอบว่ามี sn และ period ซ้ำหรือไม่
            sn = form.cleaned_data.get('sn')
            period = schedule.period
            if DeviceInspection.objects.filter(sn=sn, period=period).exists():
                messages.error(request, f"SN '{sn}' already exists for the selected period '{period}'.")
                return redirect('inspection_list')

            # บันทึกข้อมูล
            inspection = form.save(commit=False)
            inspection.schedule = schedule  # เชื่อมโยง Schedule ปัจจุบัน
            inspection.period = schedule.period  # เพิ่ม Period จาก Schedule
            inspection.save()
            messages.success(request, "Inspection created successfully!")
            return redirect('inspection_list')
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        form = DeviceInspectionForm(user=request.user)

    return render(request, 'inspection/create_inspection.html', {'form': form, 'schedule': schedule})


@login_required
def dashboard(request):
    """ แสดงหน้า Dashboard หลัก """
    all_periods = InspectionSchedule.objects.values_list('period', flat=True).distinct().order_by('period')
    return render(request, 'dashboard.html', {'is_admin': request.user.is_staff, 'all_periods': all_periods})

@login_required
def dashboard_data(request):
    """ API สำหรับดึงข้อมูล Dashboard """
    user_branch = request.user.branch if hasattr(request.user, 'branch') else None

    # ดึงข้อมูล Inspection ตามสิทธิ์ของ User
    if request.user.is_staff:
        inspections = DeviceInspection.objects.all()
        branch_stats = Branch.objects.annotate(
            total_devices=Count('deviceinspection'),
            broken_devices=Count('deviceinspection', filter=Q(deviceinspection__condition='ชำรุด')),
            normal_devices=Count('deviceinspection', filter=Q(deviceinspection__condition='ปกติ'))
        )
    else:
        inspections = DeviceInspection.objects.filter(branch=user_branch)
        branch_stats = Branch.objects.filter(id=user_branch.id).annotate(
            total_devices=Count('deviceinspection'),
            broken_devices=Count('deviceinspection', filter=Q(deviceinspection__condition='ชำรุด')),
            normal_devices=Count('deviceinspection', filter=Q(deviceinspection__condition='ปกติ'))
        )

    device_stats = inspections.aggregate(
        total_devices=Count('id'),
        broken_devices=Count('id', filter=Q(condition='ชำรุด')),
        normal_devices=Count('id', filter=Q(condition='ปกติ'))
    )

    active_salesman = Salesman.objects.filter(
        status='active', branch=user_branch if not request.user.is_staff else None
    ).count()

    inspections_over_time = inspections.annotate(day=TruncDate('inspected_at')).values('day').annotate(count=Count('id')).order_by('day')

    response_data = {
        'total_devices': device_stats['total_devices'],
        'broken_devices': device_stats['broken_devices'],
        'normal_devices': device_stats['normal_devices'],
        'active_salesman': active_salesman,
        'inspection_dates': [entry['day'].strftime('%Y-%m-%d') for entry in inspections_over_time],
        'inspection_counts': [entry['count'] for entry in inspections_over_time],
        'pie_data': {
            'labels': ['ปกติ', 'ชำรุด'],
            'data': [device_stats['normal_devices'], device_stats['broken_devices']],
            'backgroundColor': ['#28a745', '#dc3545'],
            'hoverBackgroundColor': ['#218838', '#c82333']
        },
        'is_admin': request.user.is_staff,
        'branch_chart_data': {
            'labels': [b.branchname for b in branch_stats] if branch_stats else [],
            'datasets': [
                {
                    'label': 'Total Devices',
                    'data': [b.total_devices for b in branch_stats] if branch_stats else [],
                    'backgroundColor': 'rgba(78, 115, 223, 0.5)',
                    'borderColor': 'rgba(78, 115, 223, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'ปกติ',
                    'data': [b.normal_devices for b in branch_stats] if branch_stats else [],
                    'backgroundColor': 'rgba(40, 167, 69, 0.5)',
                    'borderColor': 'rgba(40, 167, 69, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'ชำรุด',
                    'data': [b.broken_devices for b in branch_stats] if branch_stats else [],
                    'backgroundColor': 'rgba(220, 53, 69, 0.5)',
                    'borderColor': 'rgba(220, 53, 69, 1)',
                    'borderWidth': 1
                }
            ]
        } if request.user.is_staff else None
    }

    return JsonResponse(response_data)



@login_required
def delete_inspection(request, inspection_id):
    from django.contrib.auth.decorators import login_required
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from .models import DeviceInspection

    inspection = get_object_or_404(DeviceInspection, id=inspection_id)

    # ตรวจสอบสถานะของ schedule
    if inspection.schedule.status == 'Closed':
        messages.error(request, "You cannot delete an inspection from a closed period.")
        return redirect('inspection_list')

    if request.method == 'POST':
        inspection.delete()
        messages.success(request, "Inspection deleted successfully!")
        return redirect('inspection_list')

    return redirect('inspection_list')

@login_required
def inspection_detail(request, pk):
    inspection = get_object_or_404(DeviceInspection, pk=pk)
    return render(request, 'inspection/inspection_detail.html', {'inspection': inspection})

@login_required
def user_profile(request):
    if request.method == 'POST':
        # Handle profile update logic here if needed
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'inspection/user_profile.html', {
        'user': request.user,
        'page_title': 'Profile'
    })

def schedule_view(request):
    from django.utils.timezone import localtime

    # ดึงข้อมูล Schedule ทั้งหมด
    schedules = InspectionSchedule.objects.all().order_by('-end_time')  # เรียงลำดับจากเวลาล่าสุด
    latest_schedule = schedules.first()  # ดึงตารางล่าสุด

    # แปลงข้อมูลเป็น JSON เพื่อส่งให้ JavaScript
    events = [
        {
            "title": f"{localtime(schedule.start_time).strftime('%H:%M')} - {localtime(schedule.end_time).strftime('%H:%M')}",
            "start": schedule.start_time.isoformat(),
            "end": schedule.end_time.isoformat(),
            "period": schedule.period,  # เพิ่มข้อมูล period
            "description": f"Inspection from {localtime(schedule.start_time).strftime('%Y-%m-%d %H:%M')} "
                           f"to {localtime(schedule.end_time).strftime('%Y-%m-%d %H:%M')}"
        }
        for schedule in schedules
    ]
    context = {
        "events": events,
        "latest_schedule": latest_schedule,
    }
    return render(request, 'inspection/schedule.html', context)


def add_schedule(request):
    if request.method == 'POST':
        form = InspectionScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, f"Schedule for Period {schedule.period} added successfully!")
            return redirect('schedule')  # กลับไปยังหน้าปฏิทิน
        else:
            messages.error(request, "There was an error adding the schedule. Please check your input.")
    else:
        form = InspectionScheduleForm()

    return render(request, 'inspection/add_schedule.html', {'form': form})

def update_schedule_status():
    current_time = now()
    schedules = InspectionSchedule.objects.filter(end_time__lte=current_time, status='active')
    for schedule in schedules:
        schedule.status = 'Closed'
        schedule.save()

# def export_pdf(request):
#     # ดึงข้อมูลสำหรับรายงาน
#     inspections = DeviceInspection.objects.filter(branch=request.user.branch) if not request.user.is_superuser else DeviceInspection.objects.all()

#     # สร้าง Context สำหรับ Template
#     context = {
#         'inspections': inspections,
#         'total_inspections': inspections.count(),
#         'total_broken': inspections.filter(condition='ชำรุด').count(),
#         'total_normal': inspections.filter(condition='ปกติ').count(),
#     }

#     # Render HTML จาก Template
#     html_string = render_to_string('report/report_pdf.html', context)

#     # สร้าง PDF ด้วย WeasyPrint
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'inline; filename="inspection_report.pdf"'

#     HTML(string=html_string).write_pdf(response)
#     return response

def report_list(request):
    # ตรวจสอบสิทธิ์ของ User
    if request.user.is_superuser:
        inspections = DeviceInspection.objects.all()  # Admin เห็นข้อมูลทุก Branch
    else:
        user_branch = request.user.branch if hasattr(request.user, 'branch') else None
        inspections = DeviceInspection.objects.filter(branch=user_branch)  # User เห็นเฉพาะ Branch ตัวเอง

    # สรุปข้อมูล
    total_inspections = inspections.count()
    total_broken = inspections.filter(condition='ชำรุด').count()
    total_normal = inspections.filter(condition='ปกติ').count()

    context = {
        'inspections': inspections,
        'total_inspections': total_inspections,
        'total_broken': total_broken,
        'total_normal': total_normal,
    }
    return render(request, 'report/report_list.html', context)

@login_required
def inspection_delete(request, pk):
    inspection = get_object_or_404(DeviceInspection, pk=pk)
    
    # Optional: Add permission check
    if request.method == 'POST':
        # Check if the user has permission to delete
        # if request.user.is_staff or request.user == inspection.salesman.user:
        if request.user.is_active:
            inspection.delete()
            messages.success(request, 'Inspection deleted successfully.')
            return redirect('inspection_list')
        else:
            messages.error(request, 'You do not have permission to delete this inspection.')
            return redirect('inspection_list')
    
    # If not a POST request, redirect back to list
    return redirect('inspection_list')


def filter_data(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)

        # ดึงค่าจาก Request
        branch = data.get('branch')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # กรองข้อมูลตามที่เลือก (ตัวอย่าง)
        filtered_data = {
            'inspection_dates': ['2025-01-01', '2025-01-02'],  # แทนที่ด้วยข้อมูลจริง
            'inspection_counts': [5, 10],                      # แทนที่ด้วยข้อมูลจริง
            'pie_data': {
                'labels': ['Normal', 'Broken'],
                'data': [80, 20],
                'backgroundColor': ['#28a745', '#dc3545'],
                'hoverBackgroundColor': ['#218838', '#c82333'],
            },
            'branch_chart_data': {
                'labels': ['Branch A', 'Branch B'],
                'datasets': [{
                    'label': 'Devices',
                    'data': [50, 30],
                    'backgroundColor': ['#007bff', '#6610f2'],
                }],
            },
        }

        return JsonResponse(filtered_data)