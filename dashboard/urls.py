from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # Chỉ dành cho Admin
    path('teacher/', views.teacher_dashboard_view, name='teacher_dashboard'),  # Dành cho Teacher
    path('student/', views.student_dashboard_view, name='student_dashboard'),  # Dành cho Student
]