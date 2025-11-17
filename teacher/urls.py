from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_dashboard, name='teacher_dashboard'),
    path('classes/', views.teacher_class_list, name='teacher_class_list'),
    path('classes/<int:pk>/', views.teacher_class_detail, name='teacher_class_detail'),
    path('students/<int:student_id>/grades/', views.teacher_student_grades, name='teacher_student_grades'),
    path('grades/<int:pk>/update/', views.teacher_grade_update, name='teacher_grade_update'),
    path('grades/<int:pk>/delete/', views.teacher_grade_delete, name='teacher_grade_delete'),
    path('notes/', views.teacher_note_list, name='teacher_note_list'),
    path('notes/create/', views.teacher_note_create, name='teacher_note_create'),
    path('notes/<int:pk>/update/', views.teacher_note_update, name='teacher_note_update'),
    path('notes/<int:pk>/delete/', views.teacher_note_delete, name='teacher_note_delete'),
]

