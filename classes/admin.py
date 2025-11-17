from django.contrib import admin
from .models import Class


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['ma_lop', 'ten_lop', 'giao_vien_chu_nhiem', 'nam_hoc', 'get_student_count']
    list_filter = ['nam_hoc', 'giao_vien_chu_nhiem']
    search_fields = ['ma_lop', 'ten_lop']
    filter_horizontal = ['students']

