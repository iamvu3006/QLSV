"""
Script tạo dữ liệu mẫu FULL cho hệ thống QLSV.

Bao gồm:
- 10 giáo viên
- 20 môn học CNTT DUT
- 10 lớp học CNTT (23T1–23T10)
- 100 sinh viên
- Điểm học kỳ 1, học kỳ 2, học kỳ hè
- GPA cho từng kỳ

Chạy:
    python load_data.py
"""

import os
import django
import random
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qlsv.settings")
django.setup()

from accounts.models import CustomUser
from student.models import Student
from classes.models import Class
from grades.models import Grade, StudentGPA, Subject


# =======================
# DỮ LIỆU NGUỒN
# =======================

TEN_LOP = [
    "Công nghệ phần mềm",
    "Khoa học máy tính",
    "Mạng máy tính & Truyền thông",
    "Hệ thống thông tin",
    "Kỹ thuật máy tính",
    "Trí tuệ nhân tạo",
    "Khoa học dữ liệu",
    "An toàn thông tin",
    "CNTT ứng dụng",
    "Kỹ thuật dữ liệu",
]

MON_HOC = [
    ("IT001", "Nhập môn lập trình", 3),
    ("IT002", "Lập trình hướng đối tượng", 3),
    ("IT003", "Cấu trúc dữ liệu & giải thuật", 3),
    ("IT004", "Kiến trúc máy tính", 3),
    ("IT005", "Mạng máy tính", 3),
    ("IT006", "Hệ điều hành", 3),
    ("IT007", "Hệ quản trị cơ sở dữ liệu", 3),
    ("IT008", "Phân tích & thiết kế hệ thống", 3),
    ("IT009", "Kỹ thuật lập trình", 3),
    ("IT010", "Lập trình Web", 3),
    ("IT011", "Lập trình Python", 3),
    ("IT012", "Toán rời rạc", 3),
    ("IT013", "Xác suất thống kê", 3),
    ("IT014", "Trí tuệ nhân tạo", 3),
    ("IT015", "Học máy (Machine Learning)", 3),
    ("IT016", "An toàn thông tin", 3),
    ("IT017", "Mật mã & an ninh mạng", 3),
    ("IT018", "Công nghệ phần mềm", 3),
    ("IT019", "Ứng dụng đa nền tảng", 3),
    ("IT020", "Điện toán đám mây", 3),
]


def random_score():
    return round(random.uniform(4.0, 10.0), 1)


def create_data():

    print("🚀 BẮT ĐẦU TẠO DỮ LIỆU...")

    # ====================================
    # 1. TẠO GIÁO VIÊN
    # ====================================
    print("\n👨‍🏫 Tạo giáo viên...")
    teachers = []

    for i in range(1, 11):
        user, created = CustomUser.objects.get_or_create(
            username=f"teacher{i}",
            defaults={
                "role": "teacher",
                "first_name": "Giáo viên",
                "last_name": f"Số {i}",
            },
        )
        if created:
            user.set_password("teacher123")
            user.save()

        teachers.append(user)

    print("✅ Hoàn tất 10 giáo viên!")

    # ====================================
    # 2. TẠO 20 MÔN HỌC
    # ====================================
    print("\n📚 Tạo môn học...")

    subject_list = []
    for ma, ten, tc in MON_HOC:
        sb, _ = Subject.objects.get_or_create(
            ma_mon=ma,
            defaults={"ten_mon": ten, "so_tin_chi": tc},
        )
        subject_list.append(sb)

    print("✅ Hoàn tất 20 môn học!")

    # ====================================
    # 3. TẠO 10 LỚP CNTT
    # ====================================
    print("\n🏫 Tạo lớp học...")

    class_list = []

    for i in range(1, 11):
        ma_lop = f"23T{i}"
        ten_lop = TEN_LOP[i - 1]

        cl, _ = Class.objects.get_or_create(
            ma_lop=ma_lop,
            defaults={
                "ten_lop": ten_lop,
                "giao_vien_chu_nhiem": teachers[i - 1],
                "nam_hoc": "2024-2025",
            },
        )
        class_list.append(cl)

    print("✅ Hoàn tất 10 lớp học!")

    # ====================================
    # 4. TẠO 100 SINH VIÊN
    # ====================================
    print("\n👨‍🎓 Tạo sinh viên...")

    ho = ["Nguyễn", "Lê", "Trần", "Võ", "Phạm", "Đỗ"]
    tendem = ["Văn", "Hữu", "Hoàng", "Minh", "Anh", "Quốc"]
    ten = ["Nam", "Tú", "Long", "Duy", "Hải", "Sang", "Tâm", "Tài", "Khoa"]

    students = []

    for i in range(1, 101):
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

        fullname = f"{random.choice(ho)} {random.choice(tendem)} {random.choice(ten)}"

        chosen_class = random.choice(class_list)

        st, _ = Student.objects.get_or_create(
            ma_sv=f"SV{i:03d}",
            defaults={
                "user": user,
                "ho_ten": fullname,
                "ngay_sinh": date(2004, random.randint(1, 12), random.randint(1, 28)),
                "lop": chosen_class.ma_lop,
                "email": f"student{i}@sv.dut.edu.vn",
            },
        )

        chosen_class.students.add(st)
        students.append(st)

    print("✅ Hoàn tất 100 sinh viên!")

    # ====================================
    # 5. TẠO ĐIỂM 3 HỌC KỲ
    # ====================================
    print("\n📝 Tạo điểm cho từng sinh viên...")

    hoc_ky_list = ["1", "2", "3"]  # Summer

    total_grades = 0

    for st in students:
        for hk in hoc_ky_list:
            for sb in subject_list:
                Grade.objects.get_or_create(
                    student=st,
                    subject=sb,
                    hoc_ky=hk,
                    nam_hoc="2024-2025",
                    defaults={
                        "diem_qua_trinh": random_score(),
                        "diem_giua_ky": random_score(),
                        "diem_cuoi_ky": random_score(),
                    },
                )
                total_grades += 1

    print(f"✅ Đã tạo {total_grades} bản ghi điểm!")

    # ====================================
    # 6. TÍNH GPA
    # ====================================
    print("\n📊 Tính GPA...")

    for st in students:
        for hk in hoc_ky_list:
            gpa, tin_chi, diem_tl = StudentGPA.calculate_gpa(st, hk, "2024-2025")
            StudentGPA.objects.update_or_create(
                student=st,
                hoc_ky=hk,
                nam_hoc="2024-2025",
                defaults={
                    "gpa": gpa,
                    "tong_tin_chi": tin_chi,
                    "tong_diem_tich_luy": diem_tl,
                },
            )

    print("🎉 GPA đã được tính cho cả 3 học kỳ!")

    print("\n🎉 HOÀN TẤT TẠO DỮ LIỆU FULL!")


if __name__ == "__main__":
    create_data()
