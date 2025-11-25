"""
Script tạo dữ liệu mẫu cho Dashboard
Chạy: python load_data.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qlsv.settings')
django.setup()

# Import sau khi setup Django
from accounts.models import CustomUser
from student.models import Student
from classes.models import Class
from grades.models import Subject, Grade, StudentGPA
from datetime import date
import random

def main():
    print("🚀 Bắt đầu tạo dữ liệu mẫu...")
    
    # 1. Tạo Admin
    admin, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'role': 'admin',
            'first_name': 'Admin',
            'last_name': 'System'
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("✅ Tạo Admin: admin/admin123")
    else:
        print("ℹ️  Admin đã tồn tại")
    
    # 2. Tạo Giáo viên
    teachers = []
    for i in range(1, 4):
        teacher, created = CustomUser.objects.get_or_create(
            username=f'teacher{i}',
            defaults={
                'role': 'teacher',
                'first_name': f'Giáo viên',
                'last_name': f'Số {i}'
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
        teachers.append(teacher)
    print(f"✅ Tạo {len(teachers)} giáo viên")
    
    # 3. Tạo Môn học
    subjects_data = [
        ('MATH101', 'Toán cao cấp', 3),
        ('PHYS101', 'Vật lý đại cương', 3),
        ('PROG101', 'Lập trình Python', 4),
        ('ENGL101', 'Tiếng Anh cơ bản', 2),
        ('CHEM101', 'Hóa học đại cương', 3),
    ]
    subjects = []
    for ma_mon, ten_mon, tin_chi in subjects_data:
        subject, created = Subject.objects.get_or_create(
            ma_mon=ma_mon,
            defaults={
                'ten_mon': ten_mon,
                'so_tin_chi': tin_chi
            }
        )
        subjects.append(subject)
    print(f"✅ Tạo {len(subjects)} môn học")
    
    # 4. Tạo Lớp học
    classes_data = [
        ('23NH16', 'Công nghệ thông tin K23', teachers[0]),
        ('23NH17', 'Khoa học máy tính K23', teachers[1]),
        ('23NH18', 'An toàn thông tin K23', teachers[2]),
    ]
    classes_list = []
    for ma_lop, ten_lop, teacher in classes_data:
        class_obj, created = Class.objects.get_or_create(
            ma_lop=ma_lop,
            defaults={
                'ten_lop': ten_lop,
                'giao_vien_chu_nhiem': teacher,
                'nam_hoc': '2024-2025'
            }
        )
        classes_list.append(class_obj)
    print(f"✅ Tạo {len(classes_list)} lớp học")
    
    # 5. Tạo Sinh viên
    students = []
    for i in range(1, 21):  # Tạo 20 sinh viên
        # Tạo User
        student_user, created = CustomUser.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'role': 'student',
                'first_name': f'Sinh viên',
                'last_name': f'Số {i}'
            }
        )
        if created:
            student_user.set_password('student123')
            student_user.save()
        
        # Tạo Student profile
        student, created = Student.objects.get_or_create(
            ma_sv=f'SV{i:03d}',
            defaults={
                'user': student_user,
                'ho_ten': f'Nguyễn Văn {chr(64+i)}' if i <= 26 else f'Nguyễn Văn {i}',
                'ngay_sinh': date(2003, random.randint(1, 12), random.randint(1, 28)),
                'lop': random.choice(['23NH16', '23NH17', '23NH18']),
                'email': f'student{i}@example.com'
            }
        )
        students.append(student)
        
        # Thêm sinh viên vào lớp
        class_obj = random.choice(classes_list)
        if not class_obj.students.filter(id=student.id).exists():
            class_obj.students.add(student)
    
    print(f"✅ Tạo {len(students)} sinh viên")
    
    # 6. Tạo Điểm số
    grades_created = 0
    for student in students:
        for subject in subjects:
            # Random điểm số
            diem_qt = round(random.uniform(5.0, 10.0), 1)
            diem_gk = round(random.uniform(5.0, 10.0), 1)
            diem_ck = round(random.uniform(4.0, 10.0), 1)
            
            grade, created = Grade.objects.get_or_create(
                student=student,
                subject=subject,
                hoc_ky='1',
                nam_hoc='2024-2025',
                defaults={
                    'diem_qua_trinh': diem_qt,
                    'diem_giua_ky': diem_gk,
                    'diem_cuoi_ky': diem_ck,
                }
            )
            if created:
                grades_created += 1
    
    print(f"✅ Tạo {grades_created} bản ghi điểm")
    
    # 7. Tính GPA cho sinh viên
    gpa_created = 0
    for student in students:
        gpa, total_credits, total_points = StudentGPA.calculate_gpa(
            student, '1', '2024-2025'
        )
        if gpa is not None:
            gpa_record, created = StudentGPA.objects.get_or_create(
                student=student,
                hoc_ky='1',
                nam_hoc='2024-2025',
                defaults={
                    'gpa': gpa,
                    'tong_tin_chi': total_credits,
                    'tong_diem_tich_luy': total_points
                }
            )
            if created:
                gpa_created += 1
    
    print(f"✅ Tạo {gpa_created} bản ghi GPA")
    
    print("\n🎉 Hoàn thành! Dữ liệu đã được tạo.")
    print("\n📝 Thông tin đăng nhập:")
    print("  Admin: admin/admin123")
    print("  Giáo viên: teacher1/teacher123, teacher2/teacher123, teacher3/teacher123")
    print("  Sinh viên: student1/student123, student2/student123, ...")
    print("\n🌐 Truy cập:")
    print("  Dashboard Admin: http://127.0.0.1:8000/dashboard/")
    print("  Dashboard Student: http://127.0.0.1:8000/dashboard/student/")
    print("  Quản lý môn học: http://127.0.0.1:8000/grades/subjects/")

if __name__ == '__main__':
    main()