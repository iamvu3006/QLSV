from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .forms import (RegisterForm, AdminUserCreationForm, AdminUserUpdateForm, 
                    PasswordResetByAdminForm, TeacherProfileForm)
from .models import CustomUser

# Các views cũ giữ nguyên...
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('dashboard')
        elif request.user.role == 'teacher':
            return redirect('teacher_dashboard')
        elif request.user.role == 'student':
            return redirect('student_dashboard')
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Xin chào {user.username}!")
            
            if user.role == 'admin':
                return redirect("dashboard")
            elif user.role == 'teacher':
                return redirect("teacher_dashboard")
            elif user.role == 'student':
                return redirect("student_dashboard")
            else:
                return redirect("dashboard")
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu!")
    
    return render(request, "accounts/login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Đăng ký thành công! Hãy đăng nhập với tài khoản {user.username}")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            username = request.user.username
            logout(request)
            messages.info(request, f"Đã đăng xuất {username}. Hẹn gặp lại!")
            return redirect("login")
        else:
            return render(request, 'accounts/logout_confirm.html')
    else:
        return redirect("login")


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


# ==================== ADMIN VIEWS ====================

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    """Danh sách tất cả users"""
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    context = {
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'ROLE_CHOICES': CustomUser.ROLE_CHOICES,
    }
    return render(request, 'accounts/admin_user_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_create(request):
    """Tạo user mới"""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Tạo tài khoản {user.username} thành công!")
            return redirect('admin_user_list')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'accounts/admin_user_form.html', {
        'form': form,
        'title': 'Tạo tài khoản mới'
    })


@login_required
@user_passes_test(is_admin)
def admin_user_update(request, pk):
    """Cập nhật user"""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cập nhật tài khoản {user.username} thành công!")
            return redirect('admin_user_list')
    else:
        form = AdminUserUpdateForm(instance=user)
    
    return render(request, 'accounts/admin_user_form.html', {
        'form': form,
        'user_obj': user,
        'title': f'Cập nhật tài khoản {user.username}'
    })


@login_required
@user_passes_test(is_admin)
def admin_user_delete(request, pk):
    """Xóa user"""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if user == request.user:
        messages.error(request, "Không thể xóa tài khoản của chính mình!")
        return redirect('admin_user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Đã xóa tài khoản {username}!")
        return redirect('admin_user_list')
    
    return render(request, 'accounts/admin_user_confirm_delete.html', {'user_obj': user})


@login_required
@user_passes_test(is_admin)
def admin_reset_password(request, pk):
    """Đặt lại mật khẩu cho user"""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = PasswordResetByAdminForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()
            messages.success(request, f"Đã đặt lại mật khẩu cho {user.username}!")
            return redirect('admin_user_list')
    else:
        form = PasswordResetByAdminForm()
    
    return render(request, 'accounts/admin_reset_password.html', {
        'form': form,
        'user_obj': user
    })


@login_required
@user_passes_test(is_admin)
def admin_toggle_active(request, pk):
    """Khoá/mở khóa tài khoản"""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if user == request.user:
        messages.error(request, "Không thể khóa tài khoản của chính mình!")
        return redirect('admin_user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "mở khóa" if user.is_active else "khóa"
    messages.success(request, f"Đã {status} tài khoản {user.username}!")
    return redirect('admin_user_list')


@login_required
@user_passes_test(is_admin)
def admin_teacher_list(request):
    """Danh sách giáo viên"""
    query = request.GET.get('q', '')
    
    teachers = CustomUser.objects.filter(role='teacher').order_by('username')
    
    if query:
        teachers = teachers.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    return render(request, 'accounts/admin_teacher_list.html', {
        'teachers': teachers,
        'query': query
    })


@login_required
@user_passes_test(is_admin)
def admin_teacher_create(request):
    """Tạo giáo viên mới"""
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST)
        if form.is_valid():
            # Tạo user với role teacher
            user = CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password='teacher123',  # Mật khẩu mặc định
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
                role='teacher'
            )
            messages.success(request, f"Tạo giáo viên {user.username} thành công! Mật khẩu mặc định: teacher123")
            return redirect('admin_teacher_list')
    else:
        form = TeacherProfileForm()
    
    return render(request, 'accounts/admin_teacher_form.html', {
        'form': form,
        'title': 'Thêm giáo viên mới'
    })


@login_required
@user_passes_test(is_admin)
def admin_teacher_update(request, pk):
    """Cập nhật thông tin giáo viên"""
    teacher = get_object_or_404(CustomUser, pk=pk, role='teacher')
    
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST)
        if form.is_valid():
            teacher.username = form.cleaned_data['username']
            teacher.email = form.cleaned_data['email']
            teacher.first_name = form.cleaned_data.get('first_name', '')
            teacher.last_name = form.cleaned_data.get('last_name', '')
            teacher.save()
            messages.success(request, f"Cập nhật giáo viên {teacher.username} thành công!")
            return redirect('admin_teacher_list')
    else:
        form = TeacherProfileForm(initial={
            'username': teacher.username,
            'email': teacher.email,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
        })
    
    return render(request, 'accounts/admin_teacher_form.html', {
        'form': form,
        'teacher': teacher,
        'title': f'Cập nhật giáo viên {teacher.username}'
    })


@login_required
@user_passes_test(is_admin)
def admin_teacher_delete(request, pk):
    """Xóa giáo viên"""
    teacher = get_object_or_404(CustomUser, pk=pk, role='teacher')
    
    if request.method == 'POST':
        username = teacher.username
        teacher.delete()
        messages.success(request, f"Đã xóa giáo viên {username}!")
        return redirect('admin_teacher_list')
    
    return render(request, 'accounts/admin_teacher_confirm_delete.html', {'teacher': teacher})