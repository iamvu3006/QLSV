from django.contrib import admin
from .models import Subject, Grade, StudentGPA


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['ma_mon', 'ten_mon', 'so_tin_chi']
    search_fields = ['ma_mon', 'ten_mon']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'hoc_ky', 'nam_hoc', 'diem_tong_ket', 'get_letter_grade']
    list_filter = ['hoc_ky', 'nam_hoc', 'subject']
    search_fields = ['student__ma_sv', 'student__ho_ten', 'subject__ten_mon']
    readonly_fields = ['diem_tong_ket', 'created_at', 'updated_at']


@admin.register(StudentGPA)
class StudentGPAAdmin(admin.ModelAdmin):
    list_display = ['student', 'hoc_ky', 'nam_hoc', 'gpa', 'tong_tin_chi']
    list_filter = ['hoc_ky', 'nam_hoc']
    search_fields = ['student__ma_sv', 'student__ho_ten']

