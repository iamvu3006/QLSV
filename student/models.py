from django.db import models
from django.contrib.auth.models import User 

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