from django import forms
from .models import Student

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
