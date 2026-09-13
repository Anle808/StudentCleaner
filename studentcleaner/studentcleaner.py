import os
import shutil
import tempfile
import tkinter as tk
from tkinter import messagebox
import logging
import sys

# Kiểm tra thư viện phụ thuộc
try:
    import winshell
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Lỗi Phụ Thuộc", "Thư viện 'winshell' chưa được cài đặt.\nCài bằng lệnh: pip install winshell")
    sys.exit(1)

try:
    import winreg
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Lỗi Phụ Thuộc", "Thư viện 'winreg' chỉ khả dụng trên Windows.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_temp_directory():
    temp_dir = tempfile.gettempdir()
    logging.info(f"Dọn dẹp thư mục tạm: {temp_dir}")
    items_deleted = 0
    for item in os.listdir(temp_dir):
        item_path = os.path.join(temp_dir, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                items_deleted += 1
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                items_deleted += 1
        except Exception as e:
            logging.error(f"Không thể xóa {item_path}: {e}")
    logging.info(f"Hoàn tất. Đã xóa {items_deleted} mục.")

def empty_recycle_bin_safely():
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        logging.info("Thùng rác đã được làm trống.")
    except Exception as e:
        logging.error(f"Không thể làm trống Thùng rác: {e}")
        messagebox.showerror("Lỗi Thùng Rác", f"Không thể làm trống Thùng rác: {e}")

def scan_and_clean_registry_run_entries():
    registry_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    deleted_count = 0
    logging.info("Bắt đầu quét registry...")
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key_path, 0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if isinstance(value, str) and not os.path.exists(value):
                        logging.warning(f"Entry '{name}' không tồn tại: {value}. Đang xóa...")
                        try:
                            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key_path, 0, winreg.KEY_SET_VALUE) as write_key:
                                winreg.DeleteValue(write_key, name)
                            deleted_count += 1
                        except Exception as e:
                            logging.error(f"Không thể xóa '{name}': {e}")
                            messagebox.showwarning("Registry", f"Không thể xóa '{name}': {e}")
                    i += 1
                except OSError:
                    break
        logging.info(f"Hoàn tất quét registry. Đã xóa {deleted_count} mục.")
        if deleted_count > 0:
            messagebox.showinfo("Registry", f"Đã xóa {deleted_count} mục registry không hợp lệ.")
    except FileNotFoundError:
        messagebox.showerror("Lỗi Registry", f"Không tìm thấy khóa: {registry_key_path}")
    except Exception as e:
        messagebox.showerror("Lỗi Registry", f"Lỗi khi quét registry: {e}")

def run_system_cleaner():
    try:
        clean_temp_directory()
        empty_recycle_bin_safely()
        scan_and_clean_registry_run_entries()
        messagebox.showinfo("Hoàn tất", "Đã dọn rác và quét registry thành công!")
    except Exception as e:
        logging.critical(f"Lỗi nghiêm trọng: {e}")
        messagebox.showerror("Lỗi Hệ Thống", f"Đã xảy ra lỗi nghiêm trọng: {e}")

def create_gui():
    root = tk.Tk()
    root.title("StudentCleaner")
    root.geometry("300x150")
    tk.Label(root, text="Nhấn nút để dọn dẹp hệ thống.", wraplength=280).pack(pady=10)
    tk.Button(root, text="Dọn máy tính", command=run_system_cleaner,
              bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
              padx=10, pady=5).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    create_gui()
