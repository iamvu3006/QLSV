from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Sai tên đăng nhập hoặc mật khẩu")
    return render(request, "accounts/login.html")

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard_view(request):
    user = request.user
    if user.groups.filter(name="Admin").exists():
        return render(request, "accounts/dashboard_admin.html", {"user": user})
    elif user.groups.filter(name="Student").exists():
        student = getattr(user, "student", None)  # user liên kết Student
        return render(request, "accounts/dashboard_student.html", {"user": user, "student": student})
    else:
        messages.error(request, "Tài khoản của bạn chưa được phân quyền")
        return redirect("logout")

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')