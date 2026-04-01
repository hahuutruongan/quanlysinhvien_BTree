import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import ctypes
import os
import platform
import re
import unicodedata
import sys

lib_name = 'core.dll' if platform.system() == 'Windows' else 'core.so'

if getattr(sys, 'frozen', False):
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

lib_path = os.path.join(current_dir, lib_name)

if not os.path.exists(lib_path):
    print(f"Lỗi: Không tìm thấy file {lib_path}. Vui lòng biên dịch lại file C++.")
    exit()

try:
    if platform.system() == 'Windows':
        core = ctypes.CDLL(lib_path, winmode=0)
    else:
        core = ctypes.CDLL(lib_path)
except Exception as e:
    print(f"Lỗi load DLL: {e}")
    exit()

core.add_student.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
core.add_student.restype = ctypes.c_int

core.search_by_id.argtypes = [ctypes.c_char_p]
core.search_by_id.restype = ctypes.c_int

core.search_by_name.argtypes = [ctypes.c_char_p]
core.search_by_name.restype = ctypes.c_int

core.get_student_info.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]

core.delete_student_by_id.argtypes = [ctypes.c_char_p]
core.delete_student_by_id.restype = ctypes.c_bool


# ==========================================
# 2. XÂY DỰNG GIAO DIỆN (UI)
# ==========================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class StudentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Sinh Viên - B-Tree Indexing")
        self.geometry("1000x600")

        # Layout chính
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- FRAME BÊN TRÁI (NHẬP LIỆU) ---
        self.left_frame = ctk.CTkFrame(self, width=300, corner_radius=10)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.left_frame, text="THÔNG TIN SINH VIÊN", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        self.entry_id = ctk.CTkEntry(self.left_frame, placeholder_text="Mã Sinh Viên (VD: 24520042)")
        self.entry_id.pack(pady=10, padx=20, fill="x")

        self.entry_name = ctk.CTkEntry(self.left_frame, placeholder_text="Họ và Tên")
        self.entry_name.pack(pady=10, padx=20, fill="x")

        self.entry_gender = ctk.CTkComboBox(self.left_frame, values=["Nam", "Nữ", "Khác"])
        self.entry_gender.pack(pady=10, padx=20, fill="x")
        self.entry_gender.set("Nam")

        self.btn_add = ctk.CTkButton(self.left_frame, text="Thêm Sinh Viên", command=self.add_student)
        self.btn_add.pack(pady=10, padx=20, fill="x")

        self.btn_del = ctk.CTkButton(self.left_frame, text="Xóa theo Mã SV", fg_color="#C0392B", hover_color="#922B21", command=self.delete_student)
        self.btn_del.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.left_frame, text="TÌM KIẾM (B-TREE)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(30, 10))
        
        self.btn_search_id = ctk.CTkButton(self.left_frame, text="Tìm theo Mã SV", fg_color="#27AE60", hover_color="#1E8449", command=self.search_id)
        self.btn_search_id.pack(pady=5, padx=20, fill="x")

        self.btn_search_name = ctk.CTkButton(self.left_frame, text="Tìm theo Họ Tên", fg_color="#27AE60", hover_color="#1E8449", command=self.search_name)
        self.btn_search_name.pack(pady=5, padx=20, fill="x")

        # --- FRAME BÊN PHẢI ---
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=3) # Table chiếm 3 phần
        self.right_frame.grid_rowconfigure(1, weight=1) # Log chiếm 1 phần
        self.right_frame.grid_columnconfigure(0, weight=1)

        # 1. Bảng hiển thị dữ liệu (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])

        columns = ("RowID", "Mã SV", "Họ Tên", "Giới Tính", "Trạng thái")
        self.tree = ttk.Treeview(self.right_frame, columns=columns, show="headings")
        
        self.tree.heading("RowID", text="RowID")
        self.tree.heading("Mã SV", text="Mã SV")
        self.tree.heading("Họ Tên", text="Họ và Tên")
        self.tree.heading("Giới Tính", text="Giới Tính")
        self.tree.heading("Trạng thái", text="Trạng Thái (Bảng Gốc)")

        self.tree.column("RowID", width=50, anchor="center")
        self.tree.column("Mã SV", width=120, anchor="center")
        self.tree.column("Họ Tên", width=250, anchor="w")
        self.tree.column("Giới Tính", width=80, anchor="center")
        self.tree.column("Trạng thái", width=120, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 2. Màn hình Console Log
        self.log_box = ctk.CTkTextbox(self.right_frame, text_color="#00FF00", font=ctk.CTkFont(family="Consolas", size=13))
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.log_box.insert("end", "--- HỆ THỐNG SẴN SÀNG ---\n")
        self.log_box.configure(state="disabled")

    def log(self, message):
        """Hàm in ra màn hình Log"""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ==========================================
    # 3. CÁC HÀM XỬ LÝ SỰ KIỆN
    # ==========================================
    def is_valid_name(self, name):
        """Kiểm tra tên: Chỉ cho phép chữ cái (hỗ trợ full Tiếng Việt) và khoảng trắng"""
        return all(char.isalpha() or char.isspace() for char in name)

    def remove_accents(self, input_str):
        """Xóa dấu tiếng Việt, đưa về chữ thường và xóa khoảng trắng thừa"""
        s = unicodedata.normalize('NFKD', input_str).encode('ASCII', 'ignore').decode('utf-8')
        return ' '.join(s.lower().split())

    def add_student(self):
        raw_id = self.entry_id.get()
        sv_id = raw_id.strip()
        name = self.entry_name.get().strip()
        gender = self.entry_gender.get().strip()

        # 1. Kiểm tra rỗng
        if not raw_id or not name:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đủ Mã sinh viên và Họ Tên!")
            return

        # 2. Kiểm tra Mã Sinh Viên (Không có dấu cách và phải là số)
        if " " in raw_id:
            messagebox.showerror("Lỗi định dạng", "Mã sinh viên tuyệt đối không được chứa khoảng trắng!")
            return
            
        if not sv_id.isdigit():
            messagebox.showerror("Lỗi định dạng", "Mã sinh viên chỉ được phép chứa các chữ số!")
            return

        # 3. Kiểm tra định dạng Họ Tên
        if not self.is_valid_name(name):
            self.log(f"[LỖI] Tên '{name}' không hợp lệ (chứa số hoặc ký tự đặc biệt).")
            messagebox.showerror("Lỗi định dạng", "Họ tên chỉ được chứa chữ cái và khoảng trắng!")
            return

        # --- CHUẨN BỊ DỮ LIỆU ---
        norm_name = self.remove_accents(name)
        
        b_id = sv_id.encode('utf-8')
        b_name = name.encode('utf-8')
        b_gender = gender.encode('utf-8')
        b_norm_name = norm_name.encode('utf-8')

        # Truyền cả tên gốc lẫn tên không dấu xuống C++
        rowId = core.add_student(b_id, b_name, b_gender, b_norm_name)
        
        # Thêm vào UI Table
        self.tree.insert("", "end", iid=sv_id, values=(rowId, sv_id, name, gender, "Tồn tại"))

        # In log minh họa
        self.log(f"[THÊM] Mã SV: {sv_id}")
        self.log(f"   ├─ Bảng gốc: Lưu tên gốc '{name}'. Cấp phát RowID = {rowId}.")
        self.log(f"   ├─ Index Mã SV: Chèn khóa '{sv_id}' (Trỏ đến RowID={rowId}) vào B-Tree bậc 3.")
        self.log(f"   └─ Index Tên  : B-Tree chèn khóa '{norm_name}' (Trỏ đến RowID={rowId}).")
        
        self.entry_id.delete(0, 'end')
        self.entry_name.delete(0, 'end')

    def delete_student(self):
        sv_id = self.entry_id.get().strip()
        if not sv_id:
            messagebox.showwarning("Lỗi", "Vui lòng nhập Mã SV cần xóa!")
            return

        b_id = sv_id.encode('utf-8')
        success = core.delete_student_by_id(b_id)

        if success:
            # Cập nhật UI: Đổi trạng thái hiển thị thay vì xóa hẳn dòng
            if self.tree.exists(sv_id):
                item_values = self.tree.item(sv_id, 'values')
                self.tree.item(sv_id, values=(item_values[0], item_values[1], item_values[2], item_values[3], "[ĐÃ XÓA MỀM]"), tags=('deleted',))
                self.tree.tag_configure('deleted', foreground='gray')

            self.log(f"[XÓA] Mã SV: {sv_id}")
            self.log(f"   ├─ Bảng gốc: Chuyển cờ isDeleted = true.")
            self.log(f"   └─ Index     : Gỡ bỏ khóa khỏi cây B-Tree (Kích hoạt merge/borrow nếu cần).")
        else:
            messagebox.showinfo("Kết quả", f"Không tìm thấy Mã SV: {sv_id} để xóa.")

    def search_id(self):
        sv_id = self.entry_id.get().strip()
        if not sv_id:
            return

        self.log(f"[TÌM KIẾM MÃ SV] Duyệt B-Tree tìm khóa '{sv_id}'...")
        b_id = sv_id.encode('utf-8')
        rowId = core.search_by_id(b_id)

        self._handle_search_result(rowId)

    def search_name(self):
        name = self.entry_name.get().strip()
        if not name:
            return

        norm_name = self.remove_accents(name)
        self.log(f"[TÌM KIẾM TÊN] Duyệt B-Tree tìm khóa '{norm_name}'...")
        b_norm_name = norm_name.encode('utf-8')
        rowId = core.search_by_name(b_norm_name)

        self._handle_search_result(rowId)

    def _handle_search_result(self, rowId):
        if rowId != -1:
            # Chuẩn bị buffer hứng dữ liệu từ C++
            out_id = ctypes.create_string_buffer(20)
            out_name = ctypes.create_string_buffer(100)
            out_gender = ctypes.create_string_buffer(10)
            
            core.get_student_info(rowId, out_id, out_name, out_gender)
            
            # C++ trả về mảng rỗng nếu sinh viên đã bị xóa mềm
            if out_id.value: 
                s_id = out_id.value.decode('utf-8')
                s_name = out_name.value.decode('utf-8')
                
                self.log(f"   └─ THÀNH CÔNG: Tìm thấy tại RowID = {rowId}.")
                self.log(f"      Truy xuất bảng gốc: [{s_id}] - {s_name}")
                messagebox.showinfo("Tìm thấy", f"Mã sinh viên: {s_id}\nHọ tên: {s_name}\nGiới tính: {out_gender.value.decode('utf-8')}")
                
                # Highlight dòng trong bảng
                self.tree.selection_set(s_id)
            else:
                self.log("   └─ THẤT BẠI: Tìm thấy Index nhưng dữ liệu bảng gốc đã bị xóa mềm.")
                messagebox.showwarning("Cảnh báo", "Sinh viên này đã bị xóa khỏi hệ thống!")
        else:
            self.log("   └─ THẤT BẠI: Không tồn tại khóa này trên B-Tree.")
            messagebox.showinfo("Kết quả", "Không tìm thấy sinh viên!")

if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()