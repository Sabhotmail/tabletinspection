from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from . import views
from .views import delete_inspection, user_profile, schedule_view,CustomLoginView, export_pdf, report_list


urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
     # เส้นทางสำหรับการรีเซ็ตรหัสผ่าน
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'), name='password_reset_complete'),
    # path('register/', views.register, name='register'),
    path('list/', views.inspection_list, name='inspection_list'),  # รายการทั้งหมด
    path('create/', views.create_inspection, name='create_inspection'),  # สร้างข้อมูลใหม่
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete/<int:inspection_id>/', delete_inspection, name='delete_inspection'),

    path('detail/<int:pk>/', views.inspection_detail, name='inspection_detail'),
    path('profile/', user_profile, name='user_profile'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),

    path('schedule/', schedule_view, name='schedule'),
    path('add-schedule/', views.add_schedule, name='add_schedule'),
    
    path('reports/', report_list, name='report_list'),
    path('reports/export/', export_pdf, name='export_pdf'),
]
