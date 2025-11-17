from django import forms
from django.forms import formset_factory, BaseFormSet
from .models import Grade, Subject, StudentGPA
from student.models import Student


class GradeForm(forms.ModelForm):
    """Form để nhập điểm cho một môn học"""
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'hoc_ky', 'nam_hoc', 'diem_qua_trinh', 
                  'diem_giua_ky', 'diem_cuoi_ky', 'ghi_chu']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'hoc_ky': forms.Select(attrs={'class': 'form-control'}),
            'nam_hoc': forms.TextInput(attrs={'class': 'form-control'}),
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

    def clean(self):
        cleaned_data = super().clean()
        diem_qt = cleaned_data.get('diem_qua_trinh')
        diem_gk = cleaned_data.get('diem_giua_ky')
        diem_ck = cleaned_data.get('diem_cuoi_ky')

        # Kiểm tra ít nhất phải có điểm cuối kỳ
        if not diem_ck:
            raise forms.ValidationError("Vui lòng nhập điểm cuối kỳ.")

        return cleaned_data


class GradeFormSet(BaseFormSet):
    """Formset để nhập điểm cho nhiều sinh viên cùng lúc"""
    def clean(self):
        if any(self.errors):
            return
        for form in self.forms:
            if form.cleaned_data:
                diem_ck = form.cleaned_data.get('diem_cuoi_ky')
                if not diem_ck:
                    raise forms.ValidationError("Tất cả các môn học phải có điểm cuối kỳ.")


GradeFormSet = formset_factory(GradeForm, formset=GradeFormSet, extra=1, can_delete=True)


class BulkGradeForm(forms.Form):
    """Form để nhập điểm hàng loạt cho một lớp"""
    class_obj = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Chọn lớp"
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Chọn môn học"
    )
    hoc_ky = forms.ChoiceField(
        choices=Grade.HOC_KY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Học kỳ"
    )
    nam_hoc = forms.CharField(
        max_length=20,
        initial="2024-2025",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Năm học"
    )

    def __init__(self, *args, **kwargs):
        from classes.models import Class
        super().__init__(*args, **kwargs)
        self.fields['class_obj'].queryset = Class.objects.all()


class SubjectForm(forms.ModelForm):
    """Form để tạo và cập nhật môn học"""
    class Meta:
        model = Subject
        fields = ['ma_mon', 'ten_mon', 'so_tin_chi', 'mo_ta']
        widgets = {
            'ma_mon': forms.TextInput(attrs={'class': 'form-control'}),
            'ten_mon': forms.TextInput(attrs={'class': 'form-control'}),
            'so_tin_chi': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'mo_ta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

