from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Subject, SubjectPrerequisite
from .forms import SubjectForm, SubjectPrerequisiteForm

@login_required
@permission_required('subjects.view_subject', raise_exception=True)
def subject_list(request):
    subjects = Subject.objects.all().order_by('code')
    
    # Filter
    subject_type = request.GET.get('subject_type')
    if subject_type:
        subjects = subjects.filter(subject_type=subject_type)
    
    search = request.GET.get('search')
    if search:
        subjects = subjects.filter(name__icontains=search) | subjects.filter(code__icontains=search)
    
    # Pagination
    paginator = Paginator(subjects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'subject_count': subjects.count(),
    }
    return render(request, 'subjects/subject_list.html', context)

@login_required
@permission_required('subjects.add_subject', raise_exception=True)
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thêm môn học thành công!')
            return redirect('subjects:subject_list')
    else:
        form = SubjectForm()
    
    return render(request, 'subjects/subject_form.html', {'form': form, 'title': 'Thêm môn học'})

@login_required
@permission_required('subjects.change_subject', raise_exception=True)
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật môn học thành công!')
            return redirect('subjects:subject_list')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'subjects/subject_form.html', {'form': form, 'title': 'Cập nhật môn học'})

@login_required
@permission_required('subjects.delete_subject', raise_exception=True)
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Xóa môn học thành công!')
        return redirect('subjects:subject_list')
    
    return render(request, 'subjects/subject_confirm_delete.html', {'subject': subject})