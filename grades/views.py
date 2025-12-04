# grades/views.py
# REFACTORED: Thêm logic phân quyền cho teacher

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import formset_factory
from .models import Grade, Subject, StudentGPA
from .forms import GradeForm, BulkGradeForm, SubjectForm
from student.models import Student
from classes.models import Class

# Tạo GradeFormSet
GradeFormSet = formset_factory(GradeForm, extra=1, can_delete=True)


def is_admin_or_teacher(user):
    """Kiểm tra user là admin hoặc giáo viên"""
    return user.is_authenticated and (user.role == 'admin' or user.role == 'teacher')


# ============================================
# HELPER FUNCTION: Kiểm tra quyền truy cập điểm
# ============================================

def check_grade_permission(user, grade):
    """
    Kiểm tra quyền truy cập điểm số
    - Admin: Full quyền
    - Teacher: Chỉ điểm của sinh viên trong lớp mình phụ trách
    """
    if user.role == 'admin':
        return True
    
    if user.role == 'teacher':
        classes_managed = Class.objects.filter(giao_vien_chu_nhiem=user)
        return grade.student.classes.filter(
            id__in=classes_managed.values_list('id', flat=True)
        ).exists()
    
    return False


# ============================================
# SUBJECT VIEWS (Giữ nguyên)
# ============================================

@login_required
@user_passes_test(is_admin_or_teacher)
def subject_list(request):
    """Danh sách môn học"""
    subjects = Subject.objects.all()
    return render(request, 'grades/subject_list.html', {'subjects': subjects})


@login_required
@user_passes_test(is_admin_or_teacher)
def subject_create(request):
    """Tạo môn học mới"""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tạo môn học thành công!")
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'grades/subject_form.html', {'form': form, 'title': 'Tạo môn học'})


@login_required
@user_passes_test(is_admin_or_teacher)
def subject_update(request, pk):
    """Cập nhật môn học"""
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật môn học thành công!")
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'grades/subject_form.html', {'form': form, 'title': 'Cập nhật môn học'})


@login_required
@user_passes_test(is_admin_or_teacher)
def subject_delete(request, pk):
    """Xóa môn học"""
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, "Xóa môn học thành công!")
        return redirect('subject_list')
    return render(request, 'grades/subject_confirm_delete.html', {'subject': subject})


# ============================================
# GRADE VIEWS (Thêm phân quyền)
# ============================================

@login_required
@user_passes_test(is_admin_or_teacher)
def grade_create(request):
    """Tạo điểm số cho một sinh viên"""
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save()
            
            # Tính lại GPA
            gpa, total_credits, total_points = StudentGPA.calculate_gpa(
                grade.student, grade.hoc_ky, grade.nam_hoc
            )
            if gpa is not None:
                gpa_record, created = StudentGPA.objects.get_or_create(
                    student=grade.student,
                    hoc_ky=grade.hoc_ky,
                    nam_hoc=grade.nam_hoc
                )
                gpa_record.gpa = gpa
                gpa_record.tong_tin_chi = total_credits
                gpa_record.tong_diem_tich_luy = total_points
                gpa_record.save()
            
            messages.success(request, "Thêm điểm thành công!")
            return redirect('grade_list')
    else:
        form = GradeForm()
        
        # ✅ Nếu là teacher, chỉ cho chọn sinh viên trong lớp mình phụ trách
        if request.user.role == 'teacher':
            classes_managed = Class.objects.filter(giao_vien_chu_nhiem=request.user)
            student_ids = Student.objects.filter(
                classes__in=classes_managed
            ).values_list('id', flat=True)
            form.fields['student'].queryset = Student.objects.filter(id__in=student_ids)
    
    return render(request, 'grades/grade_form.html', {'form': form, 'title': 'Thêm điểm'})


@login_required
@user_passes_test(is_admin_or_teacher)
def grade_update(request, pk):
    """Cập nhật điểm số - DÙNG CHUNG cho cả admin và teacher"""
    grade = get_object_or_404(Grade, pk=pk)
    
    # ✅ Kiểm tra quyền truy cập
    if not check_grade_permission(request.user, grade):
        messages.error(request, "Bạn không có quyền cập nhật điểm của sinh viên này.")
        return redirect('grade_list')
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            grade = form.save()
            
            # Tính lại GPA
            gpa, total_credits, total_points = StudentGPA.calculate_gpa(
                grade.student, grade.hoc_ky, grade.nam_hoc
            )
            if gpa is not None:
                gpa_record, created = StudentGPA.objects.get_or_create(
                    student=grade.student,
                    hoc_ky=grade.hoc_ky,
                    nam_hoc=grade.nam_hoc
                )
                gpa_record.gpa = gpa
                gpa_record.tong_tin_chi = total_credits
                gpa_record.tong_diem_tich_luy = total_points
                gpa_record.save()
            
            messages.success(request, "Cập nhật điểm thành công!")
            
            # ✅ Redirect khác nhau dựa vào role
            if request.user.role == 'teacher':
                return redirect('teacher_student_grades', student_id=grade.student.id)
            else:
                return redirect('grade_list')
    else:
        form = GradeForm(instance=grade)
    
    # ✅ Sử dụng template CHUNG
    return render(request, 'grades/grade_form.html', {
        'form': form, 
        'title': 'Cập nhật điểm',
        'grade': grade  # Thêm context
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def grade_delete(request, pk):
    """Xóa điểm số - DÙNG CHUNG cho cả admin và teacher"""
    grade = get_object_or_404(Grade, pk=pk)
    
    # ✅ Kiểm tra quyền truy cập
    if not check_grade_permission(request.user, grade):
        messages.error(request, "Bạn không có quyền xóa điểm của sinh viên này.")
        return redirect('grade_list')
    
    student = grade.student
    hoc_ky = grade.hoc_ky
    nam_hoc = grade.nam_hoc
    
    if request.method == 'POST':
        grade.delete()
        
        # Tính lại GPA
        gpa, total_credits, total_points = StudentGPA.calculate_gpa(student, hoc_ky, nam_hoc)
        if gpa is not None:
            gpa_record, created = StudentGPA.objects.get_or_create(
                student=student,
                hoc_ky=hoc_ky,
                nam_hoc=nam_hoc
            )
            gpa_record.gpa = gpa
            gpa_record.tong_tin_chi = total_credits
            gpa_record.tong_diem_tich_luy = total_points
            gpa_record.save()
        else:
            # Xóa GPA record nếu không còn điểm nào
            StudentGPA.objects.filter(
                student=student,
                hoc_ky=hoc_ky,
                nam_hoc=nam_hoc
            ).delete()
        
        messages.success(request, "Xóa điểm thành công!")
        
        # ✅ Redirect khác nhau dựa vào role
        if request.user.role == 'teacher':
            return redirect('teacher_student_grades', student_id=student.id)
        else:
            return redirect('grade_list')
    
    # ✅ Sử dụng template CHUNG
    return render(request, 'grades/grade_confirm_delete.html', {'grade': grade})


@login_required
@user_passes_test(is_admin_or_teacher)
def grade_list(request):
    """Danh sách điểm số - DÙNG CHUNG cho cả admin và teacher"""
    hoc_ky = request.GET.get('hoc_ky', '')
    nam_hoc = request.GET.get('nam_hoc', '')
    
    grades = Grade.objects.all().select_related('student', 'subject')
    
    # ✅ Nếu là teacher, chỉ hiển thị điểm sinh viên trong lớp mình phụ trách
    if request.user.role == 'teacher':
        classes_managed = Class.objects.filter(giao_vien_chu_nhiem=request.user)
        student_ids = Student.objects.filter(
            classes__in=classes_managed
        ).values_list('id', flat=True)
        grades = grades.filter(student_id__in=student_ids)
    
    if hoc_ky:
        grades = grades.filter(hoc_ky=hoc_ky)
    if nam_hoc:
        grades = grades.filter(nam_hoc=nam_hoc)
    
    return render(request, 'grades/grade_list.html', {
        'grades': grades,
        'hoc_ky': hoc_ky,
        'nam_hoc': nam_hoc,
        'HOC_KY_CHOICES': Grade.HOC_KY_CHOICES,
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def bulk_grade_create(request):
    """Nhập điểm hàng loạt cho một lớp"""
    if request.method == 'POST':
        bulk_form = BulkGradeForm(request.POST)
        if bulk_form.is_valid():
            class_obj = bulk_form.cleaned_data['class_obj']
            subject = bulk_form.cleaned_data['subject']
            hoc_ky = bulk_form.cleaned_data['hoc_ky']
            nam_hoc = bulk_form.cleaned_data['nam_hoc']
            
            students = class_obj.students.all()
            formset = GradeFormSet(request.POST, prefix='grades')
            
            if formset.is_valid():
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        student = form.cleaned_data.get('student')
                        if student:
                            grade, created = Grade.objects.get_or_create(
                                student=student,
                                subject=subject,
                                hoc_ky=hoc_ky,
                                nam_hoc=nam_hoc,
                                defaults={
                                    'diem_qua_trinh': form.cleaned_data.get('diem_qua_trinh'),
                                    'diem_giua_ky': form.cleaned_data.get('diem_giua_ky'),
                                    'diem_cuoi_ky': form.cleaned_data.get('diem_cuoi_ky'),
                                    'ghi_chu': form.cleaned_data.get('ghi_chu', ''),
                                }
                            )
                            if not created:
                                grade.diem_qua_trinh = form.cleaned_data.get('diem_qua_trinh')
                                grade.diem_giua_ky = form.cleaned_data.get('diem_giua_ky')
                                grade.diem_cuoi_ky = form.cleaned_data.get('diem_cuoi_ky')
                                grade.ghi_chu = form.cleaned_data.get('ghi_chu', '')
                                grade.save()
                            
                            # Tính lại GPA
                            gpa, total_credits, total_points = StudentGPA.calculate_gpa(
                                student, hoc_ky, nam_hoc
                            )
                            if gpa is not None:
                                gpa_record, created = StudentGPA.objects.get_or_create(
                                    student=student,
                                    hoc_ky=hoc_ky,
                                    nam_hoc=nam_hoc
                                )
                                gpa_record.gpa = gpa
                                gpa_record.tong_tin_chi = total_credits
                                gpa_record.tong_diem_tich_luy = total_points
                                gpa_record.save()
                
                messages.success(request, "Nhập điểm hàng loạt thành công!")
                return redirect('grade_list')
        else:
            formset = GradeFormSet(prefix='grades')
    else:
        bulk_form = BulkGradeForm()
        formset = GradeFormSet(prefix='grades')
    
    return render(request, 'grades/bulk_grade_form.html', {
        'bulk_form': bulk_form,
        'formset': formset,
    })