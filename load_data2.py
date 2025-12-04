"""
Script tạo dữ liệu mẫu cho Dashboard BK-DN
Chạy: python load_data_bkdn.py
Dữ liệu lấy cảm hứng từ chương trình Công nghệ Thông tin - ĐH Bách Khoa Đà Nẵng
Không cần thư viện Faker
"""

import os
import sys
import django
from datetime import date
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qlsv.settings')
django.setup()

# Import sau khi setup Django
from accounts.models import CustomUser
from student.models import Student
from classes.models import Class
from grades.models import Subject, Grade, StudentGPA

def generate_vietnamese_name():
    """Tạo tên tiếng Việt tự nhiên"""
    ho_list = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ']
    dem_list = ['Văn', 'Thị', 'Hữu', 'Công', 'Minh', 'Thanh', 'Kim', 'Quang', 'Đức', 'Nhật', 'Bảo', 'Anh', 'Phương']
    ten_nam = ['An', 'Bình', 'Cường', 'Dũng', 'Giang', 'Hải', 'Hùng', 'Khoa', 'Long', 'Mạnh', 'Nam', 'Phong', 
               'Quân', 'Sơn', 'Thắng', 'Trung', 'Tuấn', 'Việt']
    ten_nu = ['Ân', 'Bích', 'Châu', 'Diễm', 'Giang', 'Hà', 'Hương', 'Lan', 'Linh', 'Mai', 'Nga', 'Ngọc', 
              'Như', 'Oanh', 'Phương', 'Quỳnh', 'Thảo', 'Trang', 'Uyên', 'Vy', 'Yến']
    
    ho = random.choice(ho_list)
    dem = random.choice(dem_list)
    
    # Chọn tên theo giới tính (nếu có)
    if dem == 'Thị' or random.choice([True, False]):
        ten = random.choice(ten_nu)
    else:
        ten = random.choice(ten_nam)
    
    return f"{ho} {dem} {ten}"

def generate_address():
    """Tạo địa chỉ giả"""
    duong_list = ['Trần Phú', 'Lê Duẩn', 'Nguyễn Văn Linh', 'Hoàng Diệu', 
                  'Điện Biên Phủ', 'Hùng Vương', 'Nguyễn Tất Thành', 'Lê Lợi']
    phuong_list = ['Hải Châu', 'Thanh Khê', 'Sơn Trà', 'Ngũ Hành Sơn', 
                   'Liên Chiểu', 'Cẩm Lệ', 'Hòa Cường', 'Hòa Khánh']
    thanhpho_list = ['Đà Nẵng', 'Hà Nội', 'Hồ Chí Minh', 'Huế', 'Quảng Nam', 'Quảng Ngãi']
    
    so_nha = random.randint(1, 300)
    duong = random.choice(duong_list)
    phuong = random.choice(phuong_list)
    thanhpho = random.choice(thanhpho_list)
    
    return f"{so_nha} {duong}, {phuong}, {thanhpho}"

def generate_phone():
    """Tạo số điện thoại giả"""
    prefixes = ['090', '091', '092', '093', '094', '096', '097', '098']
    prefix = random.choice(prefixes)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{prefix}{suffix}"

def main():
    print("🚀 Bắt đầu tạo dữ liệu mẫu BK-DN (Không cần Faker)...")
    
    # [Phần còn lại giữ nguyên y như script gốc]
    # 1. Tạo Admin
    admin, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'role': 'admin',
            'first_name': 'Quản trị',
            'last_name': 'Hệ thống',
            'email': 'admin@dut.udn.vn'
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("✅ Tạo Admin: admin/admin123")
    else:
        print("ℹ️  Admin đã tồn tại")
    
    # 2. Tạo Giáo viên (10 giáo viên) - Giữ nguyên
    teachers = []
    teacher_names = [
        ('Trần Văn', 'Hải', 'TVH'),
        ('Lê Thị', 'Mai', 'LTM'),
        ('Phạm Công', 'Sơn', 'PCS'),
        ('Hoàng Nhật', 'Minh', 'HNM'),
        ('Vũ Thanh', 'Bình', 'VTB'),
        ('Đặng Thị', 'Phương', 'DTP'),
        ('Bùi Quang', 'Trung', 'BQT'),
        ('Nguyễn Đức', 'Anh', 'NDA'),
        ('Phan Văn', 'Tuấn', 'PVT'),
        ('Huỳnh Thị', 'Lan', 'HTL')
    ]
    
    for i, (first_name, last_name, code) in enumerate(teacher_names, 1):
        teacher, created = CustomUser.objects.get_or_create(
            username=f'gv{code.lower()}',
            defaults={
                'role': 'teacher',
                'first_name': first_name,
                'last_name': last_name,
                'email': f'gv{code.lower()}@dut.udn.vn'
            }
        )
        if created:
            teacher.set_password('gv123')
            teacher.save()
            print(f"✅ Tạo giáo viên: {first_name} {last_name} (gv{code.lower()}/gv123)")
        teachers.append(teacher)
    
    print(f"✅ Đã tạo {len(teachers)} giáo viên")
    
    # 3. Tạo Môn học (CNTT - ĐH Bách Khoa Đà Nẵng) - Giữ nguyên
    subjects_data = [
        # Năm 1 - Học kỳ 1
        ('MATH101', 'Toán cao cấp A1', 3, 1),
        ('PHYS101', 'Vật lý đại cương', 3, 1),
        ('PROG101', 'Lập trình Python cơ bản', 3, 1),
        ('ENG101', 'Tiếng Anh A1', 2, 1),
        ('IT101', 'Nhập môn CNTT', 2, 1),
        
        # Năm 1 - Học kỳ 2
        ('MATH102', 'Toán cao cấp A2', 3, 2),
        ('PROG102', 'Cấu trúc dữ liệu và giải thuật', 4, 2),
        ('DBS101', 'Cơ sở dữ liệu', 3, 2),
        ('ENG102', 'Tiếng Anh A2', 2, 2),
        ('WEB101', 'Lập trình Web cơ bản', 3, 2),
        
        # Năm 2 - Học kỳ 3
        ('OS101', 'Hệ điều hành', 3, 3),
        ('NW101', 'Mạng máy tính', 3, 3),
        ('OOP101', 'Lập trình hướng đối tượng', 3, 3),
        ('AI101', 'Trí tuệ nhân tạo', 3, 3),
        ('SE101', 'Kỹ thuật phần mềm', 3, 3),
        
        # Năm 2 - Học kỳ 4
        ('WEB201', 'Lập trình Web nâng cao', 3, 4),
        ('MOB101', 'Lập trình di động', 3, 4),
        ('PM101', 'Quản lý dự án phần mềm', 2, 4),
        ('SEC101', 'An toàn thông tin', 3, 4),
        ('PROJ101', 'Đồ án cơ sở', 2, 4)
    ]
    
    subjects = []
    for ma_mon, ten_mon, tin_chi, hoc_ky in subjects_data:
        subject, created = Subject.objects.get_or_create(
            ma_mon=ma_mon,
            defaults={
                'ten_mon': ten_mon,
                'so_tin_chi': tin_chi,
                'hoc_ky': hoc_ky
            }
        )
        subjects.append(subject)
    print(f"✅ Đã tạo {len(subjects)} môn học")
    
    # 4. Tạo Lớp học (5 lớp) - Giữ nguyên
    classes_data = [
        ('22DTH01', 'Công nghệ thông tin K22A', teachers[0], 2022),
        ('22DTH02', 'Công nghệ thông tin K22B', teachers[1], 2022),
        ('23DTH01', 'Công nghệ thông tin K23A', teachers[2], 2023),
        ('23DTH02', 'Công nghệ thông tin K23B', teachers[3], 2023),
        ('24DTH01', 'Công nghệ thông tin K24A', teachers[4], 2024),
    ]
    
    classes_list = []
    for ma_lop, ten_lop, teacher, nam_nhap_hoc in classes_data:
        class_obj, created = Class.objects.get_or_create(
            ma_lop=ma_lop,
            defaults={
                'ten_lop': ten_lop,
                'giao_vien_chu_nhiem': teacher,
                'nam_hoc': f'{nam_nhap_hoc}-{nam_nhap_hoc+4}',
                'si_so': 0
            }
        )
        classes_list.append(class_obj)
    print(f"✅ Đã tạo {len(classes_list)} lớp học")
    
    # 5. Tạo Sinh viên (100 sinh viên) - Sửa phần tạo tên và địa chỉ
    students = []
    
    # Tạo danh sách MSSV để tránh trùng lặp
    mssv_list = [f'SV{year}{i:03d}' for year in [22, 23, 24] for i in range(1, 35)][:100]
    
    for i, mssv in enumerate(mssv_list, 1):
        # Xác định năm học dựa trên MSSV
        year_prefix = int(mssv[2:4])
        if year_prefix == 22:
            class_obj = random.choice(classes_list[:2])  # Lớp K22
            birth_year = 2002
        elif year_prefix == 23:
            class_obj = random.choice(classes_list[2:4])  # Lớp K23
            birth_year = 2003
        else:
            class_obj = classes_list[4]  # Lớp K24
            birth_year = 2004
        
        # Tạo tên đầy đủ
        full_name = generate_vietnamese_name()
        name_parts = full_name.split()
        
        # Tạo User
        student_user, created = CustomUser.objects.get_or_create(
            username=f'sv{mssv.lower()}',
            defaults={
                'role': 'student',
                'first_name': ' '.join(name_parts[:-1]),  # Họ và đệm
                'last_name': name_parts[-1],  # Tên
                'email': f'{mssv.lower()}@student.dut.udn.vn'
            }
        )
        if created:
            student_user.set_password('sv123')
            student_user.save()
        
        # Tạo Student profile
        student, created = Student.objects.get_or_create(
            ma_sv=mssv,
            defaults={
                'user': student_user,
                'ho_ten': full_name,
                'ngay_sinh': date(birth_year, random.randint(1, 12), random.randint(1, 28)),
                'lop': class_obj.ma_lop,
                'email': f'{mssv.lower()}@student.dut.udn.vn',
                'gioi_tinh': 'Nữ' if 'Thị' in full_name else random.choice(['Nam', 'Nữ']),
                'dia_chi': generate_address(),
                'sdt': generate_phone()
            }
        )
        students.append(student)
        
        # Thêm sinh viên vào lớp
        if not class_obj.students.filter(id=student.id).exists():
            class_obj.students.add(student)
            class_obj.si_so = class_obj.students.count()
            class_obj.save()
        
        if i <= 5:  # Hiển thị 5 sinh viên đầu tiên
            print(f"✅ Tạo sinh viên: {full_name} - {mssv} - Lớp {class_obj.ma_lop}")
    
    print(f"✅ Đã tạo {len(students)} sinh viên")
    
    # 6. Tạo Điểm số cho nhiều học kỳ - Giữ nguyên
    print("\n📊 Đang tạo điểm số...")
    grades_created = 0
    
    for student in students:
        # Xác định học kỳ dựa trên năm học của sinh viên
        mssv_year = int(student.ma_sv[2:4])
        
        if mssv_year == 22:  # K22: đã học 4-6 học kỳ
            max_hk = 6
        elif mssv_year == 23:  # K23: đã học 2-4 học kỳ
            max_hk = 4
        else:  # K24: mới học 1-2 học kỳ
            max_hk = 2
        
        for hk in range(1, random.randint(max_hk-1, max_hk+1)):
            # Chọn môn học theo học kỳ
            subjects_for_hk = [s for s in subjects if s.hoc_ky == hk]
            
            for subject in subjects_for_hk:
                # Tạo điểm với phân bố thực tế hơn
                rand_val = random.random()
                
                if rand_val < 0.6:  # 60% sinh viên giỏi/khá
                    diem_qt = round(random.uniform(7.0, 9.5), 1)
                    diem_gk = round(random.uniform(7.0, 9.5), 1)
                    diem_ck = round(random.uniform(7.0, 9.5), 1)
                elif rand_val < 0.9:  # 30% sinh viên trung bình
                    diem_qt = round(random.uniform(5.0, 7.5), 1)
                    diem_gk = round(random.uniform(5.0, 7.5), 1)
                    diem_ck = round(random.uniform(5.0, 7.5), 1)
                else:  # 10% sinh viên yếu
                    diem_qt = round(random.uniform(3.0, 5.5), 1)
                    diem_gk = round(random.uniform(3.0, 5.5), 1)
                    diem_ck = round(random.uniform(3.0, 5.5), 1)
                
                # Đảm bảo không có điểm âm
                diem_qt = max(0, diem_qt)
                diem_gk = max(0, diem_gk)
                diem_ck = max(0, diem_ck)
                
                # Xác định năm học
                if mssv_year == 22:
                    nam_hoc = f'{2022 + (hk-1)//2}-{2023 + (hk-1)//2}'
                elif mssv_year == 23:
                    nam_hoc = f'{2023 + (hk-1)//2}-{2024 + (hk-1)//2}'
                else:
                    nam_hoc = f'{2024 + (hk-1)//2}-{2025 + (hk-1)//2}'
                
                grade, created = Grade.objects.get_or_create(
                    student=student,
                    subject=subject,
                    hoc_ky=str(hk),
                    nam_hoc=nam_hoc,
                    defaults={
                        'diem_qua_trinh': diem_qt,
                        'diem_giua_ky': diem_gk,
                        'diem_cuoi_ky': diem_ck,
                    }
                )
                if created:
                    grades_created += 1
    
    print(f"✅ Đã tạo {grades_created} bản ghi điểm")
    
    # 7. Tính GPA cho sinh viên cho tất cả học kỳ - Giữ nguyên
    print("\n🧮 Đang tính GPA...")
    gpa_created = 0
    
    for student in students:
        mssv_year = int(student.ma_sv[2:4])
        
        if mssv_year == 22:
            hoc_ky_range = range(1, 7)  # K22: 6 học kỳ
        elif mssv_year == 23:
            hoc_ky_range = range(1, 5)  # K23: 4 học kỳ
        else:
            hoc_ky_range = range(1, 3)  # K24: 2 học kỳ
        
        for hk in hoc_ky_range:
            # Xác định năm học
            if mssv_year == 22:
                nam_hoc = f'{2022 + (hk-1)//2}-{2023 + (hk-1)//2}'
            elif mssv_year == 23:
                nam_hoc = f'{2023 + (hk-1)//2}-{2024 + (hk-1)//2}'
            else:
                nam_hoc = f'{2024 + (hk-1)//2}-{2025 + (hk-1)//2}'
            
            gpa, total_credits, total_points = StudentGPA.calculate_gpa(
                student, str(hk), nam_hoc
            )
            
            if gpa is not None:
                gpa_record, created = StudentGPA.objects.get_or_create(
                    student=student,
                    hoc_ky=str(hk),
                    nam_hoc=nam_hoc,
                    defaults={
                        'gpa': round(gpa, 2),
                        'tong_tin_chi': total_credits,
                        'tong_diem_tich_luy': round(total_points, 2),
                        'xep_loai': StudentGPA.get_grade_classification(gpa) if hasattr(StudentGPA, 'get_grade_classification') else ''
                    }
                )
                if created:
                    gpa_created += 1
    
    print(f"✅ Đã tạo {gpa_created} bản ghi GPA")
    
    # 8. Tạo một số điểm đặc biệt để demo
    print("\n🎯 Tạo dữ liệu demo đặc biệt...")
    
    # Tạo 1 sinh viên xuất sắc
    excellent_student = students[0]
    excellent_grades = Grade.objects.filter(student=excellent_student)
    for grade in excellent_grades:
        grade.diem_qua_trinh = round(random.uniform(9.0, 10.0), 1)
        grade.diem_giua_ky = round(random.uniform(9.0, 10.0), 1)
        grade.diem_cuoi_ky = round(random.uniform(9.0, 10.0), 1)
        grade.save()
    
    # Tạo 1 sinh viên cần cải thiện
    weak_student = students[1]
    weak_grades = Grade.objects.filter(student=weak_student)
    for grade in weak_grades:
        grade.diem_qua_trinh = round(random.uniform(3.0, 5.0), 1)
        grade.diem_giua_ky = round(random.uniform(3.0, 5.0), 1)
        grade.diem_cuoi_ky = round(random.uniform(3.0, 5.0), 1)
        grade.save()
    
    # Cập nhật lại GPA cho 2 sinh viên này
    for student in [excellent_student, weak_student]:
        for gpa_record in StudentGPA.objects.filter(student=student):
            gpa, total_credits, total_points = StudentGPA.calculate_gpa(
                student, gpa_record.hoc_ky, gpa_record.nam_hoc
            )
            if gpa:
                gpa_record.gpa = round(gpa, 2)
                gpa_record.tong_diem_tich_luy = round(total_points, 2)
                if hasattr(StudentGPA, 'get_grade_classification'):
                    gpa_record.xep_loai = StudentGPA.get_grade_classification(gpa)
                gpa_record.save()
    
    print("\n" + "="*50)
    print("🎉 HOÀN THÀNH TẠO DỮ LIỆU MẪU BK-DN!")
    print("="*50)
    
    print("\n📊 THỐNG KÊ DỮ LIỆU:")
    print(f"  👨‍🏫 Giáo viên: {len(teachers)}")
    print(f"  👨‍🎓 Sinh viên: {len(students)}")
    print(f"  📚 Môn học: {len(subjects)}")
    print(f"  🏫 Lớp học: {len(classes_list)}")
    print(f"  📝 Bản ghi điểm: {grades_created}")
    print(f"  📈 Bản ghi GPA: {gpa_created}")
    
    print("\n🔑 THÔNG TIN ĐĂNG NHẬP:")
    print("  👑 Admin: admin/admin123")
    print("  👨‍🏫 Giáo viên: gvtvh/gv123, gvtlm/gv123, ...")
    print("  👨‍🎓 Sinh viên: sv22001/sv123, sv23001/sv123, ...")
    
    print("\n⭐ SINH VIÊN DEMO ĐẶC BIỆT:")
    print(f"  🏆 Xuất sắc: {excellent_student.ho_ten} - {excellent_student.ma_sv}")
    print(f"  📉 Cần cải thiện: {weak_student.ho_ten} - {weak_student.ma_sv}")
    
    print("\n🌐 TRUY CẬP HỆ THỐNG:")
    print("  📊 Dashboard Admin: http://127.0.0.1:8000/dashboard/")
    print("  🎓 Dashboard Sinh viên: http://127.0.0.1:8000/dashboard/student/")
    print("  📚 Quản lý môn học: http://127.0.0.1:8000/grades/subjects/")
    print("  👨‍🎓 Quản lý sinh viên: http://127.0.0.1:8000/student/students/")
    print("  🏫 Quản lý lớp học: http://127.0.0.1:8000/classes/classes/")
    print("  📈 Xem báo cáo: http://127.0.0.1:8000/dashboard/reports/")

if __name__ == '__main__':
    main()