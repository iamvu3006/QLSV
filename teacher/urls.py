# teacher/urls.py
# FINAL VERSION: Chỉ giữ URLs cho chức năng độc quyền

from django.urls import path
from . import views

urlpatterns = [
    # ❌ XÓA: teacher_class_list, teacher_class_detail
    # → Dùng /classes/ (classes/urls.py) với phân quyền tự động
    
    # Xem điểm sinh viên (wrapper view)
    path('students/<int:student_id>/grades/', views.teacher_student_grades, name='teacher_student_grades'),
    
    # Nhận xét sinh viên (chức năng độc quyền)
    path('notes/', views.teacher_note_list, name='teacher_note_list'),
    path('notes/create/', views.teacher_note_create, name='teacher_note_create'),
    path('notes/<int:pk>/update/', views.teacher_note_update, name='teacher_note_update'),
    path('notes/<int:pk>/delete/', views.teacher_note_delete, name='teacher_note_delete'),
]

# ============================================
# URL MAPPING MỚI:
# ============================================
# 
# ADMIN:
# /classes/              → Xem tất cả lớp
# /classes/<id>/         → Chi tiết bất kỳ lớp nào
# /classes/create/       → Tạo lớp mới
# /classes/<id>/update/  → Sửa bất kỳ lớp nào
# /classes/<id>/delete/  → Xóa bất kỳ lớp nào
#
# TEACHER:
# /classes/              → Xem lớp mình phụ trách (tự động filter)
# /classes/<id>/         → Chi tiết lớp mình phụ trách (có check quyền)
# /classes/create/       → Tạo lớp (tự động set mình là GVCN)
# /classes/<id>/update/  → Sửa lớp mình phụ trách (có check quyền)
# /classes/<id>/delete/  → Xóa lớp mình phụ trách (có check quyền)
#
# /teacher/students/<id>/grades/  → Xem điểm sinh viên (wrapper)
# /teacher/notes/                 → Quản lý nhận xét (độc quyền)