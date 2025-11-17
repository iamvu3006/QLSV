from django import forms
from .models import TeacherNote
from student.models import Student
from classes.models import Class
from grades.models import Grade
from django.conf import settings

User = settings.AUTH_USER_MODEL


class TeacherNoteForm(forms.ModelForm):
    """Form để giáo viên thêm nhận xét về sinh viên"""
    class Meta:
        model = TeacherNote
        fields = ['student', 'class_obj', 'note']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'class_obj': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            # Chỉ hiển thị các lớp mà giáo viên này phụ trách
            self.fields['class_obj'].queryset = Class.objects.filter(giao_vien_chu_nhiem=teacher)
            # Chỉ hiển thị sinh viên trong các lớp mà giáo viên phụ trách
            classes_managed = Class.objects.filter(giao_vien_chu_nhiem=teacher)
            student_ids = Student.objects.filter(classes__in=classes_managed).values_list('id', flat=True)
            self.fields['student'].queryset = Student.objects.filter(id__in=student_ids)


class GradeUpdateForm(forms.ModelForm):
    """Form để giáo viên cập nhật điểm số"""
    class Meta:
        model = Grade
        fields = ['diem_qua_trinh', 'diem_giua_ky', 'diem_cuoi_ky', 'ghi_chu']
        widgets = {
            'diem_qua_trinh': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '10'
            }),
            'diem_giua_ky': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '10'
            }),
            'diem_cuoi_ky': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '10'
            }),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

