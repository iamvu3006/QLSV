from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('student/', views.student_dashboard_view, name='student_dashboard'),
]