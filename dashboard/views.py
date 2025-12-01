from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Q
from student.models import Student
from classes.models import Class
from grades.models import Grade, Subject, StudentGPA
from accounts.models import CustomUser


def is_admin_or_teacher(user):
    """Kiểm tra user là admin hoặc giáo viên"""
    return user.is_authenticated and (user.role == 'admin' or user.role == 'teacher')


@login_required
@user_passes_test(is_admin_or_teacher)
def dashboard_view(request):
    """Dashboard tổng quan cho Admin/Teacher"""
    
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
            
            subjects_stats.append({
                'subject': subject,
                'avg_score': round(avg_score, 2) if avg_score else 0,
                'passed': passed,
                'failed': failed,
                'total': subject_grades.count()
            })
    
    # Sắp xếp theo điểm trung bình giảm dần
    subjects_stats = sorted(subjects_stats, key=lambda x: x['avg_score'], reverse=True)
    
    # 5. Dữ liệu cho biểu đồ (Chart.js)
    # Biểu đồ phân bố điểm
    grade_dist_A = grades_current.filter(diem_tong_ket__gte=8.5).count()
    grade_dist_B = grades_current.filter(diem_tong_ket__gte=7.0, diem_tong_ket__lt=8.5).count()
    grade_dist_C = grades_current.filter(diem_tong_ket__gte=5.5, diem_tong_ket__lt=7.0).count()
    grade_dist_D = grades_current.filter(diem_tong_ket__gte=4.0, diem_tong_ket__lt=5.5).count()
    grade_dist_F = grades_current.filter(diem_tong_ket__lt=4.0).count()
    
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
        
        # Thống kê môn học
        'subjects_stats': subjects_stats,
        
        # Dữ liệu biểu đồ
        'grade_dist_A': grade_dist_A,
        'grade_dist_B': grade_dist_B,
        'grade_dist_C': grade_dist_C,
        'grade_dist_D': grade_dist_D,
        'grade_dist_F': grade_dist_F,
        'classes_stats': classes_stats,
        
        # Filter options
        'HOC_KY_CHOICES': Grade.HOC_KY_CHOICES,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def student_dashboard_view(request):
    """Dashboard cho sinh viên"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'dashboard/no_student_profile.html')
    
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
    }
    
    return render(request, 'dashboard/student_dashboard.html', context)