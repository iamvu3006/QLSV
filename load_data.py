"""
Script tạo dữ liệu mẫu đầy đủ cho hệ thống QLSV
Tạo:
- 10 giáo viên
- 10 môn học chuyên ngành CNTT Bách Khoa Đà Nẵng
- 4 lớp học CNTT K23
- 100 sinh viên
- Điểm số + GPA
Chạy: python load_data.py
"""

import os
import django
import random
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qlsv.settings')
django.setup()

# Import models
from accounts.models import CustomUser
from student.models import Student
from classes.models import Class
from grades.models import Subject, Grade, StudentGPA


def main():
    print("🚀 BẮT ĐẦU TẠO DỮ LIỆU MẪU...")

    # =============================
    # 1. ADMIN
    # =============================
    admin, created = CustomUser.objects.get_or_create(
        username="admin",
        defaults={
            "role": "admin",
            "first_name": "Admin",
            "last_name": "System",
        },
    )
    if created:
        admin.set_password("admin123")
        admin.save()
        print("✅ Admin: admin/admin123")

    # =============================
    # 2. GIÁO VIÊN (10 người)
    # =============================
    print("\n🧑‍🏫 Tạo giáo viên...")

    teachers = []
    for i in range(1, 11):
        teacher, created = CustomUser.objects.get_or_create(
            username=f"teacher{i}",
            defaults={
                "role": "teacher",
                "first_name": "Giáo viên",
                "last_name": f"Số {i}",
            },
        )
        if created:
            teacher.set_password("teacher123")
            teacher.save()

        teachers.append(teacher)

    print(f"✅ Đã tạo {len(teachers)} giáo viên")

    # =============================
    # 3. 10 môn học CNTT BK ĐÀ NẴNG
    # =============================
    print("\n📚 Tạo môn học...")

    subjects_data = [
        ("IT001", "Nhập môn Lập trình", 3),
        ("IT002", "Cấu trúc dữ liệu & Giải thuật", 3),
        ("IT003", "Kiến trúc máy tính", 3),
        ("IT004", "Mạng máy tính", 3),
        ("IT005", "Hệ quản trị cơ sở dữ liệu", 3),
        ("IT006", "Lập trình hướng đối tượng (Java)", 3),
        ("IT007", "Lập trình Web", 3),
        ("IT008", "Hệ điều hành", 3),
        ("IT009", "An toàn thông tin", 3),
        ("IT010", "Trí tuệ nhân tạo", 3),
    ]

    subjects = []
    for ma, ten, tc in subjects_data:
        sbj, created = Subject.objects.get_or_create(
            ma_mon=ma,
            defaults={"ten_mon": ten, "so_tin_chi": tc},
        )
        subjects.append(sbj)

    print(f"✅ Đã tạo {len(subjects)} môn học CNTT")

    # =============================
    # 4. LỚP HỌC
    # =============================
    print("\n🏫 Tạo lớp học...")

    classes_info = [
        ("23T1", "CNPM K23", teachers[0]),
        ("23T2", "Khoa học máy tính K23", teachers[1]),
        ("23T3", "An toàn thông tin K23", teachers[2]),
        ("23T4", "Hệ thống thông tin K23", teachers[3]),
    ]

    class_list = []
    for ma, ten, gv in classes_info:
        cl, created = Class.objects.get_or_create(
            ma_lop=ma,
            defaults={
                "ten_lop": ten,
                "giao_vien_chu_nhiem": gv,
                "nam_hoc": "2024-2025",
            },
        )
        class_list.append(cl)

    print(f"✅ Đã tạo {len(class_list)} lớp học")

    # =============================
    # 5. 100 SINH VIÊN
    # =============================
    print("\n👨‍🎓 Tạo sinh viên...")

    students = []

    ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Võ"]
    ten_dem = ["Văn", "Hữu", "Quang", "Thanh", "Anh", "Ngọc"]
    ten = ["Nam", "Huy", "Tú", "Long", "Minh", "Duy", "Hải", "Tâm", "Sang", "Tài"]

    for i in range(1, 101):
        # Tạo user
        user, created = CustomUser.objects.get_or_create(
            username=f"student{i}",
            defaults={
                "role": "student",
                "first_name": "Sinh viên",
                "last_name": f"Số {i}",
            },
        )
        if created:
            user.set_password("student123")
            user.save()

        # Tên ngẫu nhiên
        fullname = f"{random.choice(ho)} {random.choice(ten_dem)} {random.choice(ten)}"

        # Tạo profile student
        st, created = Student.objects.get_or_create(
            ma_sv=f"SV{i:03d}",
            defaults={
                "user": user,
                "ho_ten": fullname,
                "ngay_sinh": date(2004, random.randint(1, 12), random.randint(1, 28)),
                "lop": random.choice([c.ma_lop for c in class_list]),
                "email": f"student{i}@sv.dut.edu.vn",
            },
        )
        students.append(st)

        # Gán vào lớp
        cl = random.choice(class_list)
        cl.students.add(st)

    print(f"✅ Đã tạo {len(students)} sinh viên")

    # =============================
    # 6. ĐIỂM SỐ
    # =============================
    print("\n📝 Tạo điểm cho sinh viên...")

    total_grades = 0

    for st in students:
        for sb in subjects:
            grade, created = Grade.objects.get_or_create(
                student=st,
                subject=sb,
                hoc_ky="1",
                nam_hoc="2024-2025",
                defaults={
                    "diem_qua_trinh": round(random.uniform(5, 10), 1),
                    "diem_giua_ky": round(random.uniform(4, 10), 1),
                    "diem_cuoi_ky": round(random.uniform(4, 10), 1),
                },
            )
            if created:
                total_grades += 1

    print(f"✅ Đã tạo {total_grades} điểm số")

    # =============================
    # 7. GPA
    # =============================
    print("\n📊 Tính GPA cho sinh viên...")

    total_gpa = 0
    for st in students:
        gpa, credits, points = StudentGPA.calculate_gpa(st, "1", "2024-2025")
        if gpa:
            StudentGPA.objects.update_or_create(
                student=st,
                hoc_ky="1",
                nam_hoc="2024-2025",
                defaults={
                    "gpa": gpa,
                    "tong_tin_chi": credits,
                    "tong_diem_tich_luy": points,
                },
            )
            total_gpa += 1

    print(f"✅ Đã tạo {total_gpa} GPA")

    print("\n🎉 HOÀN THÀNH TẠO DỮ LIỆU!")
    print("\n📝 Tài khoản:")
    print("  Admin: admin/admin123")
    print("  Giáo viên: teacher1…teacher10, pass: teacher123")
    print("  Sinh viên: student1…student100, pass: student123")


if __name__ == "__main__":
    main()
