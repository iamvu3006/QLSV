# classes/views.py
# REFACTORED: Thêm logic phân quyền cho admin và teacher

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Class
from .forms import ClassForm
from student.models import Student


def is_admin_or_teacher(user):
    """Kiểm tra user là admin hoặc giáo viên"""
    return user.is_authenticated and (user.role == 'admin' or user.role == 'teacher')


# ============================================
# HELPER FUNCTION: Lọc lớp học theo role
# ============================================

def get_classes_for_user(user):
    """
    Lấy danh sách lớp học dựa trên role:
    - Admin: Tất cả lớp học
    - Teacher: Chỉ lớp mình phụ trách
    """
    if user.role == 'admin':
        return Class.objects.all()
    elif user.role == 'teacher':
        return Class.objects.filter(giao_vien_chu_nhiem=user)
    return Class.objects.none()


def check_class_permission(user, class_obj):
    """
    Kiểm tra quyền truy cập lớp học:
    - Admin: Full quyền
    - Teacher: Chỉ lớp mình phụ trách
    """
    if user.role == 'admin':
        return True
    elif user.role == 'teacher':
        return class_obj.giao_vien_chu_nhiem == user
    return False


# ============================================
# CLASS VIEWS - DÙNG CHUNG cho Admin và Teacher
# ============================================

@login_required
@user_passes_test(is_admin_or_teacher)
def class_list(request):
    """
    Danh sách lớp học - DÙNG CHUNG
    - Admin: Xem tất cả lớp
    - Teacher: Chỉ xem lớp mình phụ trách
    """
    # ✅ Tự động lọc theo role
    classes = get_classes_for_user(request.user).prefetch_related('students', 'giao_vien_chu_nhiem')

    # Tính tổng số sinh viên phù hợp với role:
    # - Admin: tổng số sinh viên trong hệ thống
    # - Teacher: tổng số sinh viên mà giáo viên đó đang phụ trách (distinct)
    if request.user.role == 'teacher':
        total_students = Student.objects.filter(classes__giao_vien_chu_nhiem=request.user).distinct().count()
    else:
        total_students = Student.objects.count()

    return render(request, 'classes/class_list.html', {
        'classes': classes,
        'user_role': request.user.role,  # Để template biết role
        'total_students': total_students,
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_detail(request, pk):
    """
    Chi tiết lớp học - DÙNG CHUNG
    - Admin: Xem bất kỳ lớp nào
    - Teacher: Chỉ xem lớp mình phụ trách
    """
    class_obj = get_object_or_404(Class, pk=pk)
    
    # ✅ Kiểm tra quyền truy cập
    if not check_class_permission(request.user, class_obj):
        messages.error(request, "Bạn không có quyền xem lớp học này.")
        return redirect('class_list')
    
    students = class_obj.students.all()
    
    return render(request, 'classes/class_detail.html', {
        'class_obj': class_obj,
        'students': students,
        'user_role': request.user.role,
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_create(request):
    """
    Tạo lớp học mới
    - Admin: Tạo bất kỳ lớp nào
    - Teacher: Tạo lớp với mình là GVCN (tùy chính sách)
    """
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            class_obj = form.save(commit=False)
            
            # ✅ Nếu là teacher, tự động set mình làm GVCN
            if request.user.role == 'teacher':
                class_obj.giao_vien_chu_nhiem = request.user
            
            class_obj.save()
            form.save_m2m()  # Lưu many-to-many (students)
            
            messages.success(request, "Tạo lớp học thành công!")
            return redirect('class_list')
    else:
        form = ClassForm()
        
        # ✅ Nếu là teacher, ẩn field giao_vien_chu_nhiem (tự động là mình)
        if request.user.role == 'teacher':
            form.fields['giao_vien_chu_nhiem'].widget.attrs['readonly'] = True
            form.initial['giao_vien_chu_nhiem'] = request.user
    
    return render(request, 'classes/class_form.html', {
        'form': form, 
        'title': 'Tạo lớp học',
        'user_role': request.user.role,
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_update(request, pk):
    """
    Cập nhật thông tin lớp học - DÙNG CHUNG
    - Admin: Sửa bất kỳ lớp nào
    - Teacher: Chỉ sửa lớp mình phụ trách
    """
    class_obj = get_object_or_404(Class, pk=pk)
    
    # ✅ Kiểm tra quyền truy cập
    if not check_class_permission(request.user, class_obj):
        messages.error(request, "Bạn không có quyền cập nhật lớp học này.")
        return redirect('class_list')
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            # ✅ Teacher không được đổi GVCN sang người khác
            if request.user.role == 'teacher':
                form.instance.giao_vien_chu_nhiem = request.user
            
            form.save()
            messages.success(request, "Cập nhật lớp học thành công!")
            return redirect('class_detail', pk=class_obj.pk)
    else:
        form = ClassForm(instance=class_obj)
        
        # ✅ Teacher không thể đổi GVCN
        if request.user.role == 'teacher':
            form.fields['giao_vien_chu_nhiem'].disabled = True
    
    return render(request, 'classes/class_form.html', {
        'form': form,
        'class_obj': class_obj,
        'title': 'Cập nhật lớp học',
        'user_role': request.user.role,
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_delete(request, pk):
    """
    Xóa lớp học
    - Admin: Xóa bất kỳ lớp nào
    - Teacher: Chỉ xóa lớp mình phụ trách (nếu cho phép)
    """
    class_obj = get_object_or_404(Class, pk=pk)
    
    # ✅ Kiểm tra quyền truy cập
    if not check_class_permission(request.user, class_obj):
        messages.error(request, "Bạn không có quyền xóa lớp học này.")
        return redirect('class_list')
    
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, "Xóa lớp học thành công!")
        return redirect('class_list')
    
    return render(request, 'classes/class_confirm_delete.html', {
        'class_obj': class_obj,
        'user_role': request.user.role,
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_add_student(request, pk):
    """
    Thêm sinh viên vào lớp - DÙNG CHUNG
    - Admin: Thêm vào bất kỳ lớp nào
    - Teacher: Chỉ thêm vào lớp mình phụ trách
    """
    class_obj = get_object_or_404(Class, pk=pk)
    
    # ✅ Kiểm tra quyền truy cập
    if not check_class_permission(request.user, class_obj):
        messages.error(request, "Bạn không có quyền thêm sinh viên vào lớp này.")
        return redirect('class_list')
    
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
        'available_students': available_students,
        'user_role': request.user.role,
    })


@login_required
@user_passes_test(is_admin_or_teacher)
def class_remove_student(request, pk, student_id):
    """
    Xóa sinh viên khỏi lớp - DÙNG CHUNG
    - Admin: Xóa từ bất kỳ lớp nào
    - Teacher: Chỉ xóa từ lớp mình phụ trách
    """
    class_obj = get_object_or_404(Class, pk=pk)
    student = get_object_or_404(Student, pk=student_id)
    
    # ✅ Kiểm tra quyền truy cập
    if not check_class_permission(request.user, class_obj):
        messages.error(request, "Bạn không có quyền xóa sinh viên khỏi lớp này.")
        return redirect('class_list')
    
    if request.method == 'POST':
        class_obj.students.remove(student)
        messages.success(request, f"Đã xóa {student.ho_ten} khỏi lớp {class_obj.ten_lop}!")
        return redirect('class_detail', pk=class_obj.pk)
    
    return render(request, 'classes/class_remove_student.html', {
        'class_obj': class_obj,
        'student': student,
        'user_role': request.user.role,
    })