from django.contrib import admin
from .models import Subject, SubjectPrerequisite

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'subject_type', 'is_active', 'created_at']
    list_filter = ['subject_type', 'is_active', 'created_at']
    search_fields = ['code', 'name']
    list_editable = ['is_active']
    ordering = ['code']

@admin.register(SubjectPrerequisite)
class SubjectPrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['subject', 'prerequisite_subject']
    list_filter = ['subject']
    search_fields = ['subject__code', 'subject__name', 'prerequisite_subject__code']