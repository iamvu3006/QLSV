from django.db import models
from django.conf import settings
from student.models import Student

User = settings.AUTH_USER_MODEL


class Class(models.Model):
    """Model lớp học"""
    ma_lop = models.CharField(max_length=20, unique=True, verbose_name="Mã lớp")
    ten_lop = models.CharField(max_length=100, verbose_name="Tên lớp")
    giao_vien_chu_nhiem = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_managed',
        limit_choices_to={'role': 'teacher'},
        verbose_name="Giáo viên chủ nhiệm"
    )
    students = models.ManyToManyField(
        Student,
        related_name='classes',
        blank=True,
        verbose_name="Sinh viên"
    )
    nam_hoc = models.CharField(max_length=20, default="2024-2025", verbose_name="Năm học")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lớp học"
        verbose_name_plural = "Lớp học"
        ordering = ['ma_lop']

    def __str__(self):
        return f"{self.ma_lop} - {self.ten_lop}"

    def get_student_count(self):
        """Trả về số lượng sinh viên trong lớp"""
        return self.students.count()

