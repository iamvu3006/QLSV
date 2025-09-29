from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Student
from .forms import StudentForm
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
    student = Student.objects.get(user=request.user)
    return render(request, "student/student_profile.html", {"student": student})