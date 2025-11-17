from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import TeacherNote
from .forms import TeacherNoteForm, GradeUpdateForm
from classes.models import Class
from student.models import Student
from grades.models import Grade


def is_teacher(user):
    """Kiểm tra user là giáo viên"""
    return user.is_authenticated and user.role == 'teacher'


@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """Dashboard của giáo viên"""
    teacher = request.user
    classes = Class.objects.filter(giao_vien_chu_nhiem=teacher).prefetch_related('students')
    return render(request, 'teacher/dashboard.html', {
        'teacher': teacher,
        'classes': classes
    })


@login_required
@user_passes_test(is_teacher)
def teacher_class_list(request):
    """Danh sách lớp mà giáo viên phụ trách"""
    teacher = request.user
    classes = Class.objects.filter(giao_vien_chu_nhiem=teacher).prefetch_related('students')
    return render(request, 'teacher/class_list.html', {
        'teacher': teacher,
        'classes': classes
    })


@login_required
@user_passes_test(is_teacher)
def teacher_class_detail(request, pk):
    """Chi tiết lớp học và danh sách sinh viên"""
    teacher = request.user
    class_obj = get_object_or_404(Class, pk=pk, giao_vien_chu_nhiem=teacher)
    students = class_obj.students.all()
    
    return render(request, 'teacher/class_detail.html', {
        'teacher': teacher,
        'class_obj': class_obj,
        'students': students
    })


@login_required
@user_passes_test(is_teacher)
def teacher_student_grades(request, student_id):
    """Xem và quản lý điểm số của một sinh viên"""
    teacher = request.user
    student = get_object_or_404(Student, pk=student_id)
    
    # Kiểm tra sinh viên có trong lớp mà giáo viên phụ trách không
    classes_managed = Class.objects.filter(giao_vien_chu_nhiem=teacher)
    if not student.classes.filter(id__in=classes_managed.values_list('id', flat=True)).exists():
        messages.error(request, "Bạn không có quyền xem điểm của sinh viên này.")
        return redirect('teacher_dashboard')
    
    grades = Grade.objects.filter(student=student).select_related('subject').order_by('-nam_hoc', '-hoc_ky', 'subject__ma_mon')
    
    return render(request, 'teacher/student_grades.html', {
        'teacher': teacher,
        'student': student,
        'grades': grades
    })


@login_required
@user_passes_test(is_teacher)
def teacher_grade_update(request, pk):
    """Cập nhật điểm số của sinh viên"""
    teacher = request.user
    grade = get_object_or_404(Grade, pk=pk)
    
    # Kiểm tra sinh viên có trong lớp mà giáo viên phụ trách không
    classes_managed = Class.objects.filter(giao_vien_chu_nhiem=teacher)
    if not grade.student.classes.filter(id__in=classes_managed.values_list('id', flat=True)).exists():
        messages.error(request, "Bạn không có quyền cập nhật điểm của sinh viên này.")
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = GradeUpdateForm(request.POST, instance=grade)
        if form.is_valid():
            grade = form.save()
            messages.success(request, "Cập nhật điểm thành công!")
            return redirect('teacher_student_grades', student_id=grade.student.id)
    else:
        form = GradeUpdateForm(instance=grade)
    
    return render(request, 'teacher/grade_update.html', {
        'teacher': teacher,
        'grade': grade,
        'form': form
    })


@login_required
@user_passes_test(is_teacher)
def teacher_grade_delete(request, pk):
    """Xóa điểm số"""
    teacher = request.user
    grade = get_object_or_404(Grade, pk=pk)
    
    # Kiểm tra sinh viên có trong lớp mà giáo viên phụ trách không
    classes_managed = Class.objects.filter(giao_vien_chu_nhiem=teacher)
    if not grade.student.classes.filter(id__in=classes_managed.values_list('id', flat=True)).exists():
        messages.error(request, "Bạn không có quyền xóa điểm của sinh viên này.")
        return redirect('teacher_dashboard')
    
    student_id = grade.student.id
    
    if request.method == 'POST':
        grade.delete()
        messages.success(request, "Xóa điểm thành công!")
        return redirect('teacher_student_grades', student_id=student_id)
    
    return render(request, 'teacher/grade_confirm_delete.html', {
        'teacher': teacher,
        'grade': grade
    })


@login_required
@user_passes_test(is_teacher)
def teacher_note_list(request):
    """Danh sách nhận xét của giáo viên"""
    teacher = request.user
    notes = TeacherNote.objects.filter(teacher=teacher).select_related('student', 'class_obj').order_by('-created_at')
    return render(request, 'teacher/note_list.html', {
        'teacher': teacher,
        'notes': notes
    })


@login_required
@user_passes_test(is_teacher)
def teacher_note_create(request):
    """Tạo nhận xét mới về sinh viên"""
    teacher = request.user
    
    if request.method == 'POST':
        form = TeacherNoteForm(request.POST, teacher=teacher)
        if form.is_valid():
            note = form.save(commit=False)
            note.teacher = teacher
            note.save()
            messages.success(request, "Thêm nhận xét thành công!")
            return redirect('teacher_note_list')
    else:
        form = TeacherNoteForm(teacher=teacher)
    
    return render(request, 'teacher/note_form.html', {
        'teacher': teacher,
        'form': form,
        'title': 'Thêm nhận xét'
    })


@login_required
@user_passes_test(is_teacher)
def teacher_note_update(request, pk):
    """Cập nhật nhận xét"""
    teacher = request.user
    note = get_object_or_404(TeacherNote, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        form = TeacherNoteForm(request.POST, instance=note, teacher=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật nhận xét thành công!")
            return redirect('teacher_note_list')
    else:
        form = TeacherNoteForm(instance=note, teacher=teacher)
    
    return render(request, 'teacher/note_form.html', {
        'teacher': teacher,
        'form': form,
        'title': 'Cập nhật nhận xét'
    })


@login_required
@user_passes_test(is_teacher)
def teacher_note_delete(request, pk):
    """Xóa nhận xét"""
    teacher = request.user
    note = get_object_or_404(TeacherNote, pk=pk, teacher=teacher)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, "Xóa nhận xét thành công!")
        return redirect('teacher_note_list')
    
    return render(request, 'teacher/note_confirm_delete.html', {
        'teacher': teacher,
        'note': note
    })

