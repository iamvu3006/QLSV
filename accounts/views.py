from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm

# accounts/views.py

def login_view(request):
    """View xử lý đăng nhập"""
    # Nếu user đã login, redirect về dashboard tương ứng
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('dashboard')  # Admin dashboard
        elif request.user.role == 'teacher':
            return redirect('teacher_dashboard')  # Teacher dashboard mới
        elif request.user.role == 'student':
            return redirect('student_dashboard')
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Xin chào {user.username}!")
            
            # Redirect dựa trên role
            if user.role == 'admin':
                return redirect("dashboard")  # Admin dashboard
            elif user.role == 'teacher':
                return redirect("teacher_dashboard")  # Teacher dashboard mới
            elif user.role == 'student':
                return redirect("student_dashboard")
            else:
                # Fallback nếu role không xác định
                return redirect("dashboard")
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu!")
    
    return render(request, "accounts/login.html")


def register_view(request):
    """View xử lý đăng ký"""
    # Nếu đã login thì không cho đăng ký nữa
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Đăng ký thành công! Hãy đăng nhập với tài khoản {user.username}")
            return redirect('login')
        else:
            # Hiển thị lỗi validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """View xử lý đăng xuất - Hỗ trợ cả GET và POST"""
    if request.user.is_authenticated:
        if request.method == 'POST':
            # POST request - thực hiện logout
            username = request.user.username
            logout(request)
            messages.info(request, f"Đã đăng xuất {username}. Hẹn gặp lại!")
            return redirect("login")
        else:
            # GET request - hiển thị trang xác nhận
            return render(request, 'accounts/logout_confirm.html')
    else:
        # Chưa login thì redirect về login
        return redirect("login")


@login_required
def profile_view(request):
    """View hiển thị profile user"""
    return render(request, 'accounts/profile.html', {'user': request.user})