from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Class
from .forms import ClassForm
from student.models import Student


def is_admin_or_teacher(user):
    """Kiểm tra user là admin hoặc giáo viên"""
    return user.is_authenticated and (user.role == 'admin' or user.role == 'teacher')


@login_required
@user_passes_test(is_admin_or_teacher)
def class_list(request):
    """Danh sách tất cả các lớp học"""
    classes = Class.objects.all().prefetch_related('students', 'giao_vien_chu_nhiem')
    return render(request, 'classes/class_list.html', {'classes': classes})


@login_required
@user_passes_test(is_admin_or_teacher)
def class_detail(request, pk):
    """Chi tiết lớp học"""
    class_obj = get_object_or_404(Class, pk=pk)
    students = class_obj.students.all()
    return render(request, 'classes/class_detail.html', {
        'class_obj': class_obj,
        'students': students
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_create(request):
    """Tạo lớp học mới"""
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tạo lớp học thành công!")
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'classes/class_form.html', {'form': form, 'title': 'Tạo lớp học'})


@login_required
@user_passes_test(is_admin_or_teacher)
def class_update(request, pk):
    """Cập nhật thông tin lớp học"""
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật lớp học thành công!")
            return redirect('class_detail', pk=class_obj.pk)
    else:
        form = ClassForm(instance=class_obj)
    return render(request, 'classes/class_form.html', {
        'form': form,
        'class_obj': class_obj,
        'title': 'Cập nhật lớp học'
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_delete(request, pk):
    """Xóa lớp học"""
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, "Xóa lớp học thành công!")
        return redirect('class_list')
    return render(request, 'classes/class_confirm_delete.html', {'class_obj': class_obj})


@login_required
@user_passes_test(is_admin_or_teacher)
def class_add_student(request, pk):
    """Thêm sinh viên vào lớp"""
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if student_id:
            student = get_object_or_404(Student, pk=student_id)
            class_obj.students.add(student)
            messages.success(request, f"Đã thêm {student.ho_ten} vào lớp {class_obj.ten_lop}!")
            return redirect('class_detail', pk=class_obj.pk)
    
    # Lấy danh sách sinh viên chưa có trong lớp
    existing_student_ids = class_obj.students.values_list('id', flat=True)
    available_students = Student.objects.exclude(id__in=existing_student_ids)
    
    return render(request, 'classes/class_add_student.html', {
        'class_obj': class_obj,
        'available_students': available_students
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_remove_student(request, pk, student_id):
    """Xóa sinh viên khỏi lớp"""
    class_obj = get_object_or_404(Class, pk=pk)
    student = get_object_or_404(Student, pk=student_id)
    
    if request.method == 'POST':
        class_obj.students.remove(student)
        messages.success(request, f"Đã xóa {student.ho_ten} khỏi lớp {class_obj.ten_lop}!")
        return redirect('class_detail', pk=class_obj.pk)
    
    return render(request, 'classes/class_remove_student.html', {
        'class_obj': class_obj,
        'student': student
    })

