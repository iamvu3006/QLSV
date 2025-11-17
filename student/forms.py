from django import forms
from .models import Student, StudentProfile

class StudentForm(forms.ModelForm):
    ngay_sinh = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Chọn ngày sinh',
                'style': 'max-width: 200px;'
            }
        )
    )

    class Meta:
        model = Student
        fields = ['ma_sv', 'ho_ten', 'ngay_sinh', 'lop', 'email']


class StudentProfileForm(forms.ModelForm):
    """Form để cập nhật thông tin profile của sinh viên"""
    class Meta:
        model = StudentProfile
        fields = ['phone', 'address', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
