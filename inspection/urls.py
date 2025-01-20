from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from . import views
from .views import delete_inspection, user_profile, schedule_view, CustomLoginView, report_list, filter_data

urlpatterns = [
    # Main URLs
    path('', views.inspection_list, name='inspection_list'),  # หน้าหลักใช้ inspection_list
    path('list/', views.inspection_list, name='inspection_list'),
    path('create/', views.create_inspection, name='create_inspection'),  # แก้จาก add_inspection เป็น create_inspection
    path('detail/<int:pk>/', views.inspection_detail, name='inspection_detail'),
    path('delete/<int:inspection_id>/', delete_inspection, name='delete_inspection'),
    path('dashboard/', views.dashboard, name='dashboard'),  # เพิ่ม URL pattern สำหรับ dashboard
    path('inspection/delete/<int:pk>/', views.inspection_delete, name='inspection_delete'),
    
    # Authentication URLs
    path('login/', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Password Management URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='auth/password_change.html', success_url='/profile/'), name='password_change'),
    
    # Profile URLs
    path('profile/', user_profile, name='profile'),
    
    # Schedule URLs
    path('schedule/', schedule_view, name='schedule'),
    path('add-schedule/', views.add_schedule, name='add_schedule'),
    
    # Report URLs
    path('reports/', report_list, name='report_list'),

    path('api/filter-data', views.filter_data, name='filter-data'),
]
