from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Subject(models.Model):
    SUBJECT_TYPES = [
        ('compulsory', 'Bắt buộc'),
        ('elective', 'Tự chọn'),
    ]
    
    code = models.CharField(max_length=10, unique=True, verbose_name="Mã môn học")
    name = models.CharField(max_length=100, verbose_name="Tên môn học")
    credits = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Số tín chỉ"
    )
    subject_type = models.CharField(
        max_length=20,
        choices=SUBJECT_TYPES,
        default='compulsory',
        verbose_name="Loại môn học"
    )
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subjects'
        verbose_name = 'Môn học'
        verbose_name_plural = 'Quản lý môn học'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class SubjectPrerequisite(models.Model):
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE,
        related_name='prerequisites',
        verbose_name="Môn học"
    )
    prerequisite_subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='required_for',
        verbose_name="Môn học tiên quyết"
    )
    
    class Meta:
        db_table = 'subject_prerequisites'
        unique_together = ['subject', 'prerequisite_subject']
        verbose_name = 'Môn học tiên quyết'
        verbose_name_plural = 'Quản lý môn học tiên quyết'

    def __str__(self):
        return f"{self.subject.code} cần {self.prerequisite_subject.code}"