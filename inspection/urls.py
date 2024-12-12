from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from . import views
from .views import delete_inspection


urlpatterns = [
    path('', LoginView.as_view(template_name='login.html'), name='login'),
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
    path('edit/<int:pk>/', views.edit_inspection, name='edit_inspection'),  # เส้นทางสำหรับหน้าแก้ไข
    path('list/', views.inspection_list, name='inspection_list'),  # รายการทั้งหมด
    path('create/', views.create_inspection, name='create_inspection'),  # สร้างข้อมูลใหม่
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete/<int:inspection_id>/', delete_inspection, name='delete_inspection'),

    path('detail/<int:pk>/', views.inspection_detail, name='inspection_detail'),
]
