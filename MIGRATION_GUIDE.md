# Hướng dẫn chạy migrations

Sau khi đã triển khai các models mới, bạn cần chạy migrations để tạo database schema.

## Các bước thực hiện:

1. **Tạo migrations cho tất cả các app:**
   ```bash
   python manage.py makemigrations
   ```

2. **Chạy migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Tạo superuser (nếu chưa có):**
   ```bash
   python manage.py createsuperuser
   ```

## Lưu ý:

- Nếu có lỗi về circular imports hoặc dependencies, có thể cần chạy migrations từng app một:
  ```bash
  python manage.py makemigrations student
  python manage.py makemigrations classes
  python manage.py makemigrations grades
  python manage.py makemigrations teacher
  python manage.py migrate
  ```

- Nếu database đã có dữ liệu cũ, có thể cần xóa file `db.sqlite3` và chạy lại migrations (chỉ trong môi trường development).

## Cấu trúc Models đã tạo:

### Student App:
- `StudentProfile`: Thông tin chi tiết của sinh viên (phone, address, avatar)

### Classes App:
- `Class`: Lớp học với mã lớp, tên lớp, giáo viên chủ nhiệm, quan hệ Many-to-Many với Student

### Grades App:
- `Subject`: Môn học với mã môn, tên môn, số tín chỉ
- `Grade`: Điểm số liên kết Student với Subject, tự động tính điểm tổng kết
- `StudentGPA`: Lưu GPA của sinh viên theo học kỳ, tự động tính toán

### Teacher App:
- `TeacherNote`: Nhận xét/ghi chú của giáo viên về sinh viên

