# qlsv/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Hàm redirect trang chủ về login
def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('dashboard')
        elif request.user.role == 'teacher':
            return redirect('teacher_dashboard')
        elif request.user.role == 'student':
            return redirect('student_dashboard')
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),  # Thêm dòng này
    path('accounts/', include('accounts.urls')),  # Sửa từ '' thành 'accounts/'
    path('dashboard/', include('dashboard.urls')),
    path('students/', include('student.urls')),
    path('classes/', include('classes.urls')),
    path('grades/', include('grades.urls')),
    path('teacher/', include('teacher.urls')),
]