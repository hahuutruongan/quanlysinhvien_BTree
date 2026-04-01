## Kiến trúc hệ thống
Dự án sử dụng mô hình kết hợp (Hybrid) để tận dụng ưu điểm của hai ngôn ngữ:
1. **Core Engine (C++):** Triển khai cấu trúc dữ liệu B-Tree, các thuật toán tự cân bằng (`Split`, `Merge`, `Borrow`) để đảm bảo hiệu năng.
2. **GUI Layer (Python - CustomTkinter):** Cung cấp giao diện người dùng hiện đại và tiền xử lý dữ liệu (chuẩn hóa Unicode tiếng Việt).
3. **Bridge (ctypes):** Liên kết động giữa Python và file `core.dll` của C++.



---

## Tính năng nổi bật
* **Chỉ mục B-Tree kép:** * Index theo **Mã Sinh Viên** (Tìm kiếm chính xác).
    * Index theo **Họ Tên** (Tìm kiếm thông minh, hỗ trợ tiếng Việt không dấu, không phân biệt hoa thường).
* **Tốc độ truy xuất cực nhanh:** Hiệu suất tìm kiếm đạt mức **$O(\log n)$**, tối ưu hơn hẳn so với việc duyệt mảng tuần tự $O(n)$.
* **Cơ chế Xóa thông minh:** * **Soft-delete** ở bảng dữ liệu gốc (giữ lịch sử).
    * **Hard-delete** ở cây chỉ mục (gỡ bỏ hoàn toàn và tự động cân bằng cây).
* **Giao diện hiện đại:** Hỗ trợ Dark Mode, hiển thị Console Log trực quan về logic hoạt động của thuật toán.



---

## Cấu trúc thư mục
* `core.cpp`: Mã nguồn C++ triển khai cấu trúc B-Tree và các API giao tiếp.
* `ui.py`: Mã nguồn Python xử lý giao diện và logic ứng dụng.
* `core.dll`: Thư viện liên kết động (Compiled) dùng cho ứng dụng.

---

## Tài liệu tham khảo
1. **Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C.** (2009). *Introduction to Algorithms* (3rd ed.). MIT Press. (Chương 18: B-Trees - Nguồn tài liệu chính về thuật toán).
2. **GeeksforGeeks.** *B-Tree | Set 1 (Introduction)*, *Set 2 (Insert)*, *Set 3 (Delete)*. [Link tham khảo](https://www.geeksforgeeks.org/introduction-of-b-tree-2/).
3. **CustomTkinter Documentation.** *Modern UI for Python*. [Link tham khảo](https://customtkinter.tomschimansky.com/).
4. **Python ctypes Documentation.** *Calling C functions from Python*. [Link tham khảo](https://docs.python.org/3/library/ctypes.html).
