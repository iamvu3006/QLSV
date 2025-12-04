from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']
        widgets = {
            'role': forms.Select(choices=CustomUser.ROLE_CHOICES),
        }


class AdminUserCreationForm(UserCreationForm):
    """Form để admin tạo user mới"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class AdminUserUpdateForm(UserChangeForm):
    """Form để admin cập nhật user"""
    password = None  # Không cho sửa mật khẩu ở đây
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PasswordResetByAdminForm(forms.Form):
    """Form để admin đặt lại mật khẩu cho user"""
    new_password1 = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    new_password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Hai mật khẩu không khớp!")
        
        return cleaned_data


class TeacherProfileForm(forms.Form):
    """Form để tạo/sửa thông tin giáo viên"""
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    khoa = forms.CharField(max_length=100, required=False, label="Khoa", widget=forms.TextInput(attrs={'class': 'form-control'}))
    trinh_do = forms.ChoiceField(
        choices=[
            ('', '-- Chọn trình độ --'),
            ('cu_nhan', 'Cử nhân'),
            ('thac_si', 'Thạc sĩ'),
            ('tien_si', 'Tiến sĩ'),
            ('pho_giao_su', 'Phó giáo sư'),
            ('giao_su', 'Giáo sư'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    chuyen_mon = forms.CharField(max_length=200, required=False, label="Chuyên môn", widget=forms.TextInput(attrs={'class': 'form-control'}))