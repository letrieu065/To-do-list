import datetime
import random
import json
import tkinter as tk
from tkinter import messagebox, ttk, Text


# ==========================================
# BACKEND: Quản lý Dữ liệu
# ==========================================
class Task:
    # Đã thêm created_at vào để khởi tạo và load từ JSON
    def __init__(self, title, is_completed, created_at=None):
        self.title = title
        self.is_completed = is_completed
        # Lưu ngày dưới dạng string ISO (VD: '2023-10-27') để dễ lưu vào JSON
        self.created_at = created_at or datetime.date.today().isoformat()

    def to_dict(self):
        return {
            "title": self.title,
            "is_completed": self.is_completed,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["title"], data["is_completed"], data.get("created_at"))


class Award:
    @staticmethod
    def random_award():
        awards = ['Candy', '15min Break', 'New Game']
        weights = [20, 75, 5]
        return random.choices(awards, weights, k=1)[0]

    """@staticmethod
    def show_award():
        TodoApp.reward_label.config(text=f"Phần thưởng: {Award.random_award()}")
        #messagebox.showinfo("Phần thưởng", f"Bạn nhận được: {Award.random_award()}")"""


class SaveLoad:
    @staticmethod
    def load(filename):
        try:
            with open(filename, 'r', encoding="utf-8") as f:
                data = json.load(f)

                # Kiểm tra nếu data là từ điển (cấu trúc mới)
                if isinstance(data, dict):
                    danh_sach_task = [Task.from_dict(item) for item in data.get("tasks", [])]
                    diem_streak = data.get("current_streak", 0)
                    ngay_cuoi = data.get("last_date", None)
                # Nếu data là danh sách (cấu trúc cũ)
                elif isinstance(data, list):
                    danh_sach_task = [Task.from_dict(item) for item in data]
                    diem_streak = 0
                    ngay_cuoi = None
                else:
                    return [], 0, None

                return danh_sach_task, diem_streak, ngay_cuoi

        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return [], 0, None

    @staticmethod
    def save(filename, tasks, current_streak, last_day):
        data_to_save = {
            "tasks": [task.to_dict() for task in tasks],
            "current_streak": current_streak,
            "last_date": last_day
        }
        # Đã thêm encoding="utf-8"
        with open(filename, 'w', encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# ==========================================
# FRONTEND: Quản lý Giao diện (Đã gom vào Class)
# ==========================================
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-do List App")  # Đã đổi tên
        self.root.geometry("480x500")
        self.root.resizable(width=False, height=False)
        self.root.configure(background="white")
        self.editing_index = None
        self.current_streak = 0
        self.last_date = None

        # Load dữ liệu ngay khi khởi tạo app
        self.all_tasks, self.current_streak, self.last_date = SaveLoad.load("tasks.json")

        self.setup_ui()
        self.update_task_list()

    def setup_ui(self):
        tk.Label(self.root, text="To-do list", font=('Arial', 40, 'bold'), bg="white").pack(pady=10)

        self.reward_label = tk.Label(self.root,text=f"Phần thưởng:", font=('Arial', 12, 'bold'), bg="gold")
        self.reward_label.pack()

        self.streak_label = tk.Label(self.root,text=f"Chuỗi:{self.current_streak}", font=('Arial', 12, 'bold'), bg="blue")
        self.streak_label.pack()

        self.task_entry = tk.Entry(self.root, font=('Arial', 14), width=30)
        self.task_entry.pack(pady=5)
        # Phím tắt Enter
        self.root.bind('<Return>', lambda event: self.handle_add_task())

        # Các nút bấm
        tk.Button(self.root, text='Add task', font=('Arial', 12, 'bold'), command=self.handle_add_task).pack(pady=5)
        tk.Button(self.root, text='Edit task', font=('Arial', 12, 'bold'), command=self.handle_edit_task).pack(pady=5)
        tk.Button(self.root, text='Remove task', font=('Arial', 12, 'bold'), command=self.handle_delete_task).pack(
            pady=5)
        tk.Button(self.root, text='Complete task', font=('Arial', 12, 'bold'), command=self.handle_complete_task).pack(
            pady=5)

        """self.list_box = tk.Listbox(self.root, font=('Arial', 12, 'bold'), width=40, height=10)
        self.list_box.pack(pady=10)"""

        self.tree = ttk.Treeview(self.root, columns=("Task", "Date", "Status"), show="headings", height=10)
        self.tree.heading("Task", text="Nhiệm vụ")
        self.tree.heading("Date", text="Ngày tạo")
        self.tree.heading("Status", text="Trạng thái")

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(pady=10)
        self.tree.configure(yscrollcommand=scrollbar.set)

    # Các hàm xử lý sự kiện
    def handle_add_task(self):
        task_name = self.task_entry.get().strip()
        if task_name:
            if task_name in [task.title for task in self.all_tasks]:
                messagebox.showwarning("Cảnh báo", "Nhiệm vụ này đã tồn tại!")
                return

            if self.editing_index is not None:
                self.all_tasks[self.editing_index].title = task_name
                self.editing_index = None
            else:
                self.all_tasks.append(Task(task_name, False))

            self.task_entry.delete(0, "end")
            self.update_task_list()
            SaveLoad.save("tasks.json", self.all_tasks, self.current_streak, self.last_date)

    def handle_edit_task(self):
        selection = self.tree.selection()
        if selection:
            index = int(selection[0])
            self.editing_index = index
            task = self.all_tasks[index]
            self.task_entry.delete(0, "end")
            self.task_entry.insert(0, task.title)
            self.update_task_list()

    def handle_delete_task(self):
        selection = self.tree.selection()
        if selection:
            danh_sach_index = sorted([int(item) for item in selection], reverse=True)
            if messagebox.askyesno("Cảnh báo", "Bạn có muốn xóa các task đã chọn?"):
                for index in danh_sach_index:
                    self.all_tasks.pop(index)
                self.update_task_list()
                SaveLoad.save("tasks.json", self.all_tasks, self.current_streak, self.last_date)

    def handle_complete_task(self):
        today = datetime.date.today()
        selection = self.tree.selection()
        if selection:
            index = int(selection[0])
            task = self.all_tasks[index]

            if not task.is_completed:
                if self.last_date is None or (today - datetime.date.fromisoformat(self.last_date)).days > 1:
                    self.current_streak = 1
                elif (today - datetime.date.fromisoformat(self.last_date)).days == 1:
                    self.current_streak += 1
                task.is_completed = True
                self.update_task_list()
                self.show_award()
                self.last_date = today.isoformat()
                SaveLoad.save("tasks.json", self.all_tasks, self.current_streak, self.last_date)

    def update_task_list(self):
        self.tree.delete(*self.tree.get_children())

        for index, task in enumerate(self.all_tasks):
            status = "✅" if task.is_completed else "⏳"
            tag = "done" if task.is_completed else "pending"
            self.tree.insert("", "end", values=(task.title, task.created_at, status), iid=index, tags=(tag,))

            self.tree.tag_configure("done", foreground="green")
            self.tree.tag_configure("pending", foreground="gray")
        self.streak_label.config(text=f"Chuỗi: {self.current_streak}")

    def show_award(self):
        self.reward_label.config(text=f"Phần thưởng: {Award.random_award()}")

# ==========================================
# KHỞI CHẠY CHƯƠNG TRÌNH
# ==========================================
if __name__ == "__main__":
    windows = tk.Tk()
    app = TodoApp(windows)
    windows.mainloop()