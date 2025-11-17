# QLSV
Dự án Python học phần Lập Trình Python 23Nh16

## Hướng dẫn chạy project

### Yêu cầu hệ thống
- Python 3.8 trở lên
- pip (Python package manager)

### Các bước chạy project

1. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Chạy migrations để tạo database:**
   ```bash
   python manage.py migrate
   ```

3. **Tạo superuser (tùy chọn - để truy cập admin panel):**
   ```bash
   python manage.py createsuperuser
   ```

4. **Chạy server:**
   ```bash
   python manage.py runserver
   ```

5. **Truy cập ứng dụng:**
   - Mở trình duyệt và truy cập: `http://127.0.0.1:8000/`
   - Trang admin: `http://127.0.0.1:8000/admin/`

### Lưu ý
- Database SQLite (`db.sqlite3`) đã có sẵn trong project
- Nếu gặp lỗi về migrations, có thể chạy lại: `python manage.py makemigrations` rồi `python manage.py migrate`
