# dashboard/views.py
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Q
from student.models import Student
from classes.models import Class
from grades.models import Grade, Subject, StudentGPA
from teacher.models import TeacherNote
from accounts.models import CustomUser
import json


def is_admin(user):
    """Kiểm tra user là admin"""
    return user.is_authenticated and user.role == 'admin'


def is_teacher(user):
    """Kiểm tra user là giáo viên"""
    return user.is_authenticated and user.role == 'teacher'


@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    """Dashboard tổng quan CHỈ DÀNH CHO ADMIN"""
    
    # 1. Thống kê tổng quan
    total_students = Student.objects.count()
    total_classes = Class.objects.count()
    total_subjects = Subject.objects.count()
    total_teachers = CustomUser.objects.filter(role='teacher').count()
    
    # 2. Thống kê điểm theo học kỳ hiện tại
    current_semester = request.GET.get('hoc_ky', '1')
    current_year = request.GET.get('nam_hoc', '2024-2025')
    
    # Lấy tất cả điểm của học kỳ hiện tại
    grades_current = Grade.objects.filter(
        hoc_ky=current_semester,
        nam_hoc=current_year,
        diem_tong_ket__isnull=False
    )
    
    # Tính điểm trung bình chung
    average_grade = grades_current.aggregate(Avg('diem_tong_ket'))['diem_tong_ket__avg']
    
    # Thống kê sinh viên qua/rớt (>= 5.0 là qua)
    passed_count = grades_current.filter(diem_tong_ket__gte=5.0).values('student').distinct().count()
    failed_count = grades_current.filter(diem_tong_ket__lt=5.0).values('student').distinct().count()
    
    # 3. Top 5 sinh viên có GPA cao nhất
    top_students = StudentGPA.objects.filter(
        hoc_ky=current_semester,
        nam_hoc=current_year,
        gpa__isnull=False
    ).select_related('student').order_by('-gpa')[:5]
    
    # 4. Thống kê điểm theo môn học
    subjects_stats = []
    for subject in Subject.objects.all():
        subject_grades = grades_current.filter(subject=subject)
        if subject_grades.exists():
            avg_score = subject_grades.aggregate(Avg('diem_tong_ket'))['diem_tong_ket__avg']
            passed = subject_grades.filter(diem_tong_ket__gte=5.0).count()
            failed = subject_grades.filter(diem_tong_ket__lt=5.0).count()
            total = subject_grades.count()
            
            # Tính tỉ lệ đạt (FIX LỖI Ở ĐÂY)
            passed_ratio = (passed / total * 100) if total > 0 else 0
            
            subjects_stats.append({
                'subject': subject,
                'avg_score': round(avg_score, 2) if avg_score else 0,
                'passed': passed,
                'failed': failed,
                'total': total,
                'passed_ratio': round(passed_ratio, 1)  # Thêm passed_ratio
            })
    
    # Sắp xếp theo điểm trung bình giảm dần
    subjects_stats = sorted(subjects_stats, key=lambda x: x['avg_score'], reverse=True)
    
    # 5. Dữ liệu cho biểu đồ (Chart.js)
    # Biểu đồ phân bố điểm
    grade_distribution = {
        "A (8.5-10)": grades_current.filter(diem_tong_ket__gte=8.5).count(),
        "B (7.0-8.4)": grades_current.filter(diem_tong_ket__gte=7.0, diem_tong_ket__lt=8.5).count(),
        "C (5.5-6.9)": grades_current.filter(diem_tong_ket__gte=5.5, diem_tong_ket__lt=7.0).count(),
        "D (4.0-5.4)": grades_current.filter(diem_tong_ket__gte=4.0, diem_tong_ket__lt=5.5).count(),
        "F (0-3.9)": grades_current.filter(diem_tong_ket__lt=4.0).count(),
    }
    
    # 6. Thống kê theo lớp
    classes_stats = []
    for class_obj in Class.objects.all()[:10]:  # Giới hạn 10 lớp
        students_in_class = class_obj.students.all()
        if students_in_class.exists():
            # Tính GPA trung bình của lớp
            gpa_records = StudentGPA.objects.filter(
                student__in=students_in_class,
                hoc_ky=current_semester,
                nam_hoc=current_year
            )
            avg_gpa = gpa_records.aggregate(Avg('gpa'))['gpa__avg']
            
            classes_stats.append({
                'class': {
                    'id': class_obj.id,
                    'ma_lop': class_obj.ma_lop,
                    'ten_lop': class_obj.ten_lop,
                },
                'student_count': students_in_class.count(),
                'avg_gpa': round(avg_gpa, 2) if avg_gpa else 0
            })
    
    context = {
        # Thống kê tổng quan
        'total_students': total_students,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'total_teachers': total_teachers,
        
        # Học kỳ hiện tại
        'current_semester': current_semester,
        'current_year': current_year,
        'average_grade': round(average_grade, 2) if average_grade else 0,
        'passed_count': passed_count,
        'failed_count': failed_count,
        
        # Top sinh viên
        'top_students': top_students,
        
        # Thống kê môn học (ĐÃ CÓ passed_ratio)
        'subjects_stats': subjects_stats,
        
        # Dữ liệu biểu đồ
        'grade_distribution': grade_distribution,
        'classes_stats': classes_stats,
        
        # Filter options
        'HOC_KY_CHOICES': Grade.HOC_KY_CHOICES,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    """Dashboard CHỈ DÀNH CHO GIÁO VIÊN"""
    teacher = request.user
    
    # 1. Lấy các lớp giáo viên phụ trách
    classes = Class.objects.filter(giao_vien_chu_nhiem=teacher).prefetch_related('students')
    
    # 2. Thống kê tổng quan
    total_classes = classes.count()
    total_students = Student.objects.filter(classes__in=classes).distinct().count()
    total_grades = Grade.objects.filter(
        student__classes__in=classes
    ).distinct().count()
    total_notes = TeacherNote.objects.filter(teacher=teacher).count()
    
    # 3. Thống kê điểm trung bình theo lớp
    class_stats = []
    for class_obj in classes:
        students_in_class = class_obj.students.all()
        if students_in_class.exists():
            grades = Grade.objects.filter(
                student__in=students_in_class,
                diem_tong_ket__isnull=False
            )
            avg_grade = grades.aggregate(Avg('diem_tong_ket'))['diem_tong_ket__avg']
            
            if avg_grade:
                class_stats.append({
                    'class_name': class_obj.ma_lop,
                    'average_grade': round(avg_grade, 2)
                })
    
    # 4. Top 5 sinh viên xuất sắc trong các lớp phụ trách
    students_in_classes = Student.objects.filter(classes__in=classes).distinct()
    top_students = StudentGPA.objects.filter(
        student__in=students_in_classes,
        gpa__isnull=False
    ).select_related('student').order_by('-gpa')[:5]
    
    # 5. Sinh viên có GPA thấp cần quan tâm (GPA < 2.0)
    low_gpa_students = StudentGPA.objects.filter(
        student__in=students_in_classes,
        gpa__lt=2.0,
        gpa__isnull=False
    ).select_related('student').order_by('gpa')[:5]
    
    # 6. Nhận xét gần đây
    recent_notes = TeacherNote.objects.filter(
        teacher=teacher
    ).select_related('student', 'class_obj').order_by('-created_at')[:4]
    
    context = {
        'teacher': teacher,
        'classes': classes,
        'total_classes': total_classes,
        'total_students': total_students,
        'total_grades': total_grades,
        'total_notes': total_notes,
        'class_stats': json.dumps(class_stats),
        'top_students': top_students,
        'low_gpa_students': low_gpa_students,
        'recent_notes': recent_notes,
    }
    
    return render(request, 'dashboard/teacher_dashboard.html', context)

@login_required
def student_dashboard_view(request):
    """Dashboard cho sinh viên"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        # ✅ TẠO STUDENT TỰ ĐỘNG NẾU CHƯA CÓ
        from datetime import date
        student = Student.objects.create(
            user=request.user,
            ma_sv=request.user.username,
            ho_ten=request.user.get_full_name() or request.user.username,
            ngay_sinh=date(2000, 1, 1),
            lop='Chưa phân lớp',
            email=request.user.email
        )
        messages.info(request, "Hồ sơ sinh viên đã được tạo. Vui lòng cập nhật thông tin đầy đủ.")
    
    # Lấy học kỳ hiện tại
    current_semester = '1'
    current_year = '2024-2025'
    
    # Lấy GPA hiện tại
    try:
        current_gpa = StudentGPA.objects.get(
            student=student,
            hoc_ky=current_semester,
            nam_hoc=current_year
        )
    except StudentGPA.DoesNotExist:
        current_gpa = None

    # Tính xếp loại học tập (string) và class cho badge dựa trên thang điểm 10
    current_gpa_rating = None
    current_gpa_rating_class = None
    if current_gpa and current_gpa.gpa is not None:
        g = current_gpa.gpa
        if g >= 8.5:
            current_gpa_rating = 'Giỏi'
            current_gpa_rating_class = 'bg-success'
        elif g >= 7.0:
            current_gpa_rating = 'Khá'
            current_gpa_rating_class = 'bg-primary'
        elif g >= 5.5:
            current_gpa_rating = 'Trung bình'
            current_gpa_rating_class = 'bg-warning'
        elif g >= 4.0:
            current_gpa_rating = 'Kém'
            current_gpa_rating_class = 'bg-secondary'
        else:
            current_gpa_rating = 'Yếu'
            current_gpa_rating_class = 'bg-danger'
    
    # Lấy điểm các môn học kỳ hiện tại
    current_grades = Grade.objects.filter(
        student=student,
        hoc_ky=current_semester,
        nam_hoc=current_year
    ).select_related('subject')
    
    # Lấy tất cả lớp học
    classes = student.classes.all()
    
    # Lịch sử GPA
    gpa_history = StudentGPA.objects.filter(
        student=student
    ).order_by('-nam_hoc', '-hoc_ky')
    
    context = {
        'student': student,
        'current_gpa': current_gpa,
        'current_grades': current_grades,
        'classes': classes,
        'gpa_history': gpa_history,
        'current_semester': current_semester,
        'current_year': current_year,
        'current_gpa_rating': current_gpa_rating,
        'current_gpa_rating_class': current_gpa_rating_class,
    }
    
    return render(request, 'dashboard/student_dashboard.html', context)