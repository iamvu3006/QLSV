from django import forms
from .models import Subject, SubjectPrerequisite

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'credits', 'subject_type', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: MATH101'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'subject_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'code': 'Mã môn học',
            'name': 'Tên môn học',
            'credits': 'Số tín chỉ',
            'subject_type': 'Loại môn học',
            'description': 'Mô tả',
            'is_active': 'Kích hoạt'
        }

class SubjectPrerequisiteForm(forms.ModelForm):
    class Meta:
        model = SubjectPrerequisite
        fields = ['subject', 'prerequisite_subject']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'prerequisite_subject': forms.Select(attrs={'class': 'form-control'}),
        }