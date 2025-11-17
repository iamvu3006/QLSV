from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.student_create, name='student_create'),
    path('edit/<int:pk>/', views.student_update, name='student_update'),
    path('delete/<int:pk>/', views.student_delete, name='student_delete'),
    path("profile/", views.student_profile, name="student_profile"),
    path("profile/update/", views.student_profile_update, name="student_profile_update"),
    path("grades/", views.student_grades, name="student_grades"),
]
