from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
User = settings.AUTH_USER_MODEL

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    ma_sv = models.CharField(max_length=20, unique=True)  # Mã sinh viên
    ho_ten = models.CharField(max_length=100)
    ngay_sinh = models.DateField()
    lop = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.ma_sv} - {self.ho_ten}"


class StudentProfile(models.Model):
    """Thông tin chi tiết của sinh viên liên kết với User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile của {self.user.username}"