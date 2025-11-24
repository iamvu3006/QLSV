from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Sum
from student.models import Student


class Subject(models.Model):
    """Model môn học"""
    ma_mon = models.CharField(max_length=20, unique=True, verbose_name="Mã môn")
    ten_mon = models.CharField(max_length=100, verbose_name="Tên môn học")
    so_tin_chi = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Số tín chỉ"
    )
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Môn học"
        verbose_name_plural = "Môn học"
        ordering = ['ma_mon']

    def __str__(self):
        return f"{self.ma_mon} - {self.ten_mon}"


class Grade(models.Model):
    """Model điểm số"""
    HOC_KY_CHOICES = [
        ('1', 'Học kỳ 1'),
        ('2', 'Học kỳ 2'),
        ('3', 'Học kỳ hè'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name="Sinh viên"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name="Môn học"
    )
    hoc_ky = models.CharField(max_length=1, choices=HOC_KY_CHOICES, verbose_name="Học kỳ")
    nam_hoc = models.CharField(max_length=20, default="2024-2025", verbose_name="Năm học")
    diem_qua_trinh = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        null=True,
        blank=True,
        verbose_name="Điểm quá trình"
    )
    diem_giua_ky = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        null=True,
        blank=True,
        verbose_name="Điểm giữa kỳ"
    )
    diem_cuoi_ky = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        null=True,
        blank=True,
        verbose_name="Điểm cuối kỳ"
    )
    diem_tong_ket = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        null=True,
        blank=True,
        verbose_name="Điểm tổng kết"
    )
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Điểm số"
        verbose_name_plural = "Điểm số"
        unique_together = ['student', 'subject', 'hoc_ky', 'nam_hoc']
        ordering = ['-nam_hoc', 'hoc_ky', 'subject']

    def __str__(self):
        return f"{self.student.ma_sv} - {self.subject.ten_mon} - HK{self.hoc_ky}"

    def calculate_final_grade(self):
        """Tính điểm tổng kết dựa trên điểm quá trình, giữa kỳ và cuối kỳ"""
        if self.diem_cuoi_ky is not None:
            # Công thức: 20% quá trình + 30% giữa kỳ + 50% cuối kỳ
            diem_qt = self.diem_qua_trinh or 0
            diem_gk = self.diem_giua_ky or 0
            diem_ck = self.diem_cuoi_ky or 0
            return round(diem_qt * 0.2 + diem_gk * 0.3 + diem_ck * 0.5, 2)
        return None

    def save(self, *args, **kwargs):
        """Tự động tính điểm tổng kết khi lưu"""
        if self.diem_cuoi_ky is not None:
            self.diem_tong_ket = self.calculate_final_grade()
        super().save(*args, **kwargs)

    def get_letter_grade(self):
        """Chuyển đổi điểm số sang chữ"""
        if self.diem_tong_ket is None:
            return "Chưa có điểm"
        if self.diem_tong_ket >= 9.0:
            return "A+"
        elif self.diem_tong_ket >= 8.5:
            return "A"
        elif self.diem_tong_ket >= 8.0:
            return "B+"
        elif self.diem_tong_ket >= 7.0:
            return "B"
        elif self.diem_tong_ket >= 6.5:
            return "C+"
        elif self.diem_tong_ket >= 5.5:
            return "C"
        elif self.diem_tong_ket >= 5.0:
            return "D+"
        elif self.diem_tong_ket >= 4.0:
            return "D"
        else:
            return "F"


class StudentGPA(models.Model):
    """Model lưu GPA của sinh viên theo học kỳ"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='gpa_records',
        verbose_name="Sinh viên"
    )
    hoc_ky = models.CharField(max_length=1, choices=Grade.HOC_KY_CHOICES, verbose_name="Học kỳ")
    nam_hoc = models.CharField(max_length=20, default="2024-2025", verbose_name="Năm học")
    gpa = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)],
        null=True,
        blank=True,
        verbose_name="GPA"
    )
    tong_tin_chi = models.IntegerField(default=0, verbose_name="Tổng tín chỉ")
    tong_diem_tich_luy = models.FloatField(default=0.0, verbose_name="Tổng điểm tích lũy")

    class Meta:
        verbose_name = "GPA học kỳ"
        verbose_name_plural = "GPA học kỳ"
        unique_together = ['student', 'hoc_ky', 'nam_hoc']
        ordering = ['-nam_hoc', 'hoc_ky']

    def __str__(self):
        return f"{self.student.ma_sv} - HK{self.hoc_ky} - GPA: {self.gpa or 'N/A'}"

    @staticmethod
    def calculate_gpa(student, hoc_ky, nam_hoc):
        """Tính GPA cho sinh viên trong một học kỳ"""
        grades = Grade.objects.filter(
            student=student,
            hoc_ky=hoc_ky,
            nam_hoc=nam_hoc,
            diem_tong_ket__isnull=False
        )

        if not grades.exists():
            return None, 0, 0.0

        total_credits = 0
        total_points = 0.0

        for grade in grades:
            credits = grade.subject.so_tin_chi
            score = grade.diem_tong_ket
            total_credits += credits
            total_points += score * credits

        if total_credits == 0:
            return None, 0, 0.0

        gpa = round(total_points / total_credits, 2)
        return gpa, total_credits, total_points