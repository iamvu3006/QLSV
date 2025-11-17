from django.contrib import admin
from .models import TeacherNote


@admin.register(TeacherNote)
class TeacherNoteAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'student', 'class_obj', 'created_at']
    list_filter = ['class_obj', 'created_at']
    search_fields = ['student__ma_sv', 'student__ho_ten', 'teacher__username']

