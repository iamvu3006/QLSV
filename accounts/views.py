from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirect dựa trên role
            if user.role == 'admin':
                return redirect("dashboard")
            elif user.role == 'teacher':
                return redirect("teacher_dashboard")
            elif user.role == 'student':
                return redirect("student_dashboard")
            else:
                return redirect("dashboard")
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu")
    return render(request, "accounts/login.html")

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')