from django import forms
from .models import Class
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ClassForm(forms.ModelForm):
    """Form để tạo và cập nhật lớp học"""
    class Meta:
        model = Class
        fields = ['ma_lop', 'ten_lop', 'giao_vien_chu_nhiem', 'nam_hoc', 'students']
        widgets = {
            'ma_lop': forms.TextInput(attrs={'class': 'form-control'}),
            'ten_lop': forms.TextInput(attrs={'class': 'form-control'}),
            'giao_vien_chu_nhiem': forms.Select(attrs={'class': 'form-control'}),
            'nam_hoc': forms.TextInput(attrs={'class': 'form-control'}),
            'students': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Chỉ hiển thị giáo viên trong dropdown
        self.fields['giao_vien_chu_nhiem'].queryset = User.objects.filter(role='teacher')

