# teacher/views.py
# FINAL VERSION: Chỉ giữ lại chức năng ĐỘC QUYỀN của teacher

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import TeacherNote
from .forms import TeacherNoteForm
from classes.models import Class
from student.models import Student
from grades.models import Grade


def is_teacher(user):
    """Kiểm tra user là giáo viên"""
    return user.is_authenticated and user.role == 'teacher'


# ❌ XÓA: teacher_class_list, teacher_class_detail
# → Dùng classes/views.py với URL /classes/


# ============================================
# XEM ĐIỂM SINH VIÊN - View wrapper cho teacher
# ============================================

@login_required
@user_passes_test(is_teacher)
def teacher_student_grades(request, student_id):
    """
    View wrapper: Xem điểm số của sinh viên
    - Kiểm tra quyền truy cập
    - Render template CHUNG từ grades/
    """
    teacher = request.user
    student = get_object_or_404(Student, pk=student_id)
    
    # ✅ Kiểm tra sinh viên có trong lớp mình phụ trách không
    classes_managed = Class.objects.filter(giao_vien_chu_nhiem=teacher)
    if not student.classes.filter(id__in=classes_managed.values_list('id', flat=True)).exists():
        messages.error(request, "Bạn không có quyền xem điểm của sinh viên này.")
        return redirect('class_list')
    
    # Lấy điểm số
    grades = Grade.objects.filter(student=student).select_related('subject').order_by('-nam_hoc', '-hoc_ky', 'subject__ma_mon')
    
    # ✅ DÙNG TEMPLATE CHUNG từ grades/grade_list.html
    return render(request, 'grades/grade_list.html', {
        'grades': grades,
        'student': student,
        'is_teacher_view': True,  # Flag để template biết
        'HOC_KY_CHOICES': Grade.HOC_KY_CHOICES,
    })


# ============================================
# NHẬN XÉT SINH VIÊN - Chức năng ĐỘC QUYỀN
# ============================================

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