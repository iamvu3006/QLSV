from django.db import models
from django.conf import settings
from student.models import Student
from classes.models import Class

User = settings.AUTH_USER_MODEL


class TeacherNote(models.Model):
    """Model lưu nhận xét/ghi chú của giáo viên về sinh viên"""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_notes',
        limit_choices_to={'role': 'teacher'},
        verbose_name="Giáo viên"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='teacher_notes',
        verbose_name="Sinh viên"
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='teacher_notes',
        null=True,
        blank=True,
        verbose_name="Lớp học"
    )
    note = models.TextField(verbose_name="Nhận xét/Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nhận xét giáo viên"
        verbose_name_plural = "Nhận xét giáo viên"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.teacher.username} - {self.student.ma_sv}"

