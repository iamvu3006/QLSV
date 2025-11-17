from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Avg
from django.contrib import messages
from .models import Student, StudentProfile
from .forms import StudentForm, StudentProfileForm
from grades.models import Grade, StudentGPA, Subject
from classes.models import Class
from django.contrib.auth.decorators import login_required

# Create your views here.
def student_list(request):
    query = request.GET.get('q')
    if query:
        students = Student.objects.filter(
            Q(ma_sv__icontains=query) |
            Q(ho_ten__icontains=query) |
            Q(lop__icontains=query) |
            Q(email__icontains=query)
        )
    else:
        students = Student.objects.all()
    return render(request, 'student/student_list.html', {'students': students})

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'student/student_form.html', {'form': form})

def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'student/student_form.html', {'form': form})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'student/student_confirm_delete.html', {'student': student})

@login_required
def student_profile(request):
    """Hiển thị thông tin cá nhân của sinh viên"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin sinh viên.")
        return redirect('login')
    
    # Lấy hoặc tạo StudentProfile
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={'student': student}
    )
    
    # Cập nhật student nếu chưa có
    if not profile.student:
        profile.student = student
        profile.save()
    
    return render(request, "student/student_profile.html", {
        "student": student,
        "profile": profile
    })

@login_required
def student_profile_update(request):
    """Cập nhật thông tin profile của sinh viên"""
    try:
        student = Student.objects.get(user=request.user)
        profile, created = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={'student': student}
        )
    except Student.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin sinh viên.")
        return redirect('login')
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật thông tin thành công!")
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=profile)
    
    return render(request, 'student/student_profile_update.html', {
        'form': form,
        'student': student,
        'profile': profile
    })

@login_required
def student_grades(request):
    """Hiển thị điểm số và GPA của sinh viên"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin sinh viên.")
        return redirect('login')
    
    hoc_ky = request.GET.get('hoc_ky', '1')
    nam_hoc = request.GET.get('nam_hoc', '2024-2025')
    
    # Lấy điểm số theo học kỳ
    grades = Grade.objects.filter(
        student=student,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc
    ).select_related('subject').order_by('subject__ma_mon')
    
    # Tính GPA
    gpa_record, created = StudentGPA.objects.get_or_create(
        student=student,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc
    )
    
    if created or not gpa_record.gpa:
        gpa, total_credits, total_points = StudentGPA.calculate_gpa(student, hoc_ky, nam_hoc)
        if gpa is not None:
            gpa_record.gpa = gpa
            gpa_record.tong_tin_chi = total_credits
            gpa_record.tong_diem_tich_luy = total_points
            gpa_record.save()
    
    # Lấy tất cả các học kỳ có điểm
    all_semesters = Grade.objects.filter(student=student).values_list(
        'hoc_ky', 'nam_hoc'
    ).distinct().order_by('-nam_hoc', '-hoc_ky')
    
    # Lấy tất cả các môn học
    all_subjects = Subject.objects.all().order_by('ma_mon')
    
    return render(request, 'student/student_grades.html', {
        'student': student,
        'grades': grades,
        'gpa_record': gpa_record,
        'hoc_ky': hoc_ky,
        'nam_hoc': nam_hoc,
        'all_semesters': all_semesters,
        'all_subjects': all_subjects,
        'HOC_KY_CHOICES': Grade.HOC_KY_CHOICES,
    })