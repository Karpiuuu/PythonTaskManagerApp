import tkinter as tk
from tkinter import ttk
import json
import os


class TaskField:
    """Deskryptor do zarządzania polami zadania."""
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name, "")

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class Task:
    name = TaskField("name")
    status = TaskField("status")
    description = TaskField("description")

    def __init__(self, name, status, description):
        self.name = name
        self.status = status
        self.description = description


def log_action(func):
    def wrapper(*args, **kwargs):
        print(f"Wykonywanie akcji: {func.__name__}")
        result = func(*args, **kwargs)
        return result
    return wrapper


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prosty system zarządzania zadaniami")
        self.root.geometry("900x800")
        self.root.resizable(False, False)

        # File to save tasks
        self.tasks_file = "tasks.json"
        self.tasks = []

        # Apply modern theme
        self.apply_theme()

        # UI setup
        self.setup_ui()

        # Load tasks from file
        self.load_tasks()

    def apply_theme(self):
        try:
            import sv_ttk
            sv_ttk.set_theme("dark")
        except ImportError:
            self.root.tk.call("source", "azure.tcl")
            self.root.tk.call("set_theme", "light")

    def setup_ui(self):
        """Set up the user interface."""
        # Canvas for scrolling
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollable Frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Main Frame
        self.main_frame = ttk.Frame(self.scrollable_frame, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Left Frame for Task List and Form
        self.left_frame = ttk.Frame(self.main_frame, padding=10)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Right Frame for Task Description
        self.right_frame = ttk.LabelFrame(self.main_frame, text="Opis zadania", padding=10, width=300)
        self.right_frame.pack(side="right", fill="y", expand=False)

        # Label for task description
        self.description_text = tk.Text(self.right_frame, wrap="word", height=20, width=40)
        self.description_text.pack(fill="both", expand=True)
        self.description_text.configure(state="disabled")

        # Task List Frame
        self.task_list_frame = ttk.Frame(self.left_frame)
        self.task_list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Scrollbar for the Treeview
        self.tree_scrollbar = ttk.Scrollbar(self.task_list_frame, orient="vertical")
        self.tree_scrollbar.grid(row=0, column=1, sticky="ns")

        # Treeview for tasks
        self.task_tree = ttk.Treeview(
            self.task_list_frame,
            columns=("Task", "Status"),
            show="headings",
            height=10,
            yscrollcommand=self.tree_scrollbar.set,
        )
        self.tree_scrollbar.config(command=self.task_tree.yview)

        self.task_tree.heading("Task", text="Zadanie")
        self.task_tree.column("Task", width=300, anchor="w")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.column("Status", width=100, anchor="center")

        self.task_tree.tag_configure("do_zrobienia", foreground="red")
        self.task_tree.tag_configure("w_trakcie", foreground="orange")
        self.task_tree.tag_configure("zakonczone", foreground="green")
        self.task_tree.grid(row=0, column=0, sticky="nsew")

        # Bind selection event to populate fields
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)

        # Task Form Frame
        self.task_form_frame = ttk.LabelFrame(self.left_frame, text="Dodaj/Edytuj zadanie", padding=10)
        self.task_form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(self.task_form_frame, text="Nazwa zadania:").grid(row=0, column=0, sticky="w")
        self.task_name_entry = ttk.Entry(self.task_form_frame, width=30)
        self.task_name_entry.grid(row=0, column=1, sticky="w", pady=5)

        ttk.Label(self.task_form_frame, text="Status:").grid(row=1, column=0, sticky="w")
        self.task_status_combobox = ttk.Combobox(self.task_form_frame, values=["Do zrobienia", "W trakcie", "Zakonczone"], state="readonly", width=27)
        self.task_status_combobox.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(self.task_form_frame, text="Opis zadania:").grid(row=2, column=0, sticky="nw")
        self.task_description_text = tk.Text(self.task_form_frame, width=30, height=5, wrap="word")
        self.task_description_text.grid(row=2, column=1, sticky="w", pady=5)

        # Buttons Frame
        self.buttons_frame = ttk.Frame(self.task_form_frame)
        self.buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.add_button = ttk.Button(self.buttons_frame, text="Dodaj zadanie", command=self.add_task)
        self.add_button.grid(row=0, column=0, padx=5)

        self.edit_button = ttk.Button(self.buttons_frame, text="Edytuj zadanie", command=self.edit_task)
        self.edit_button.grid(row=0, column=1, padx=5)

        self.delete_button = ttk.Button(self.buttons_frame, text="Usuń zadanie", command=self.delete_task)
        self.delete_button.grid(row=0, column=2, padx=5)

    def on_task_select(self, event):
        selected_item = self.task_tree.selection()
        if selected_item:
            item = self.task_tree.item(selected_item)
            task_name, task_status = item["values"]

            for task in self.tasks:
                if task.name == task_name and task.status == task_status:
                    description = task.description
                    break
            else:
                description = ""

            # Populate fields
            self.task_name_entry.delete(0, tk.END)
            self.task_name_entry.insert(0, task_name)
            self.task_status_combobox.set(task_status)
            self.task_description_text.delete(1.0, tk.END)
            self.task_description_text.insert(tk.END, description)

            # Update description box
            self.description_text.configure(state="normal")
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(tk.END, description)
            self.description_text.configure(state="disabled")

    @log_action
    def add_task(self):
        task_name = self.task_name_entry.get()
        task_status = self.task_status_combobox.get()
        task_description = self.task_description_text.get(1.0, tk.END).strip()
        if task_name and task_status:
            task = Task(task_name, task_status, task_description)
            self.tasks.append(task)
            self.task_tree.insert("", "end", values=(task.name, task.status), tags=(task.status,))
            self.save_tasks()
            self.clear_form()

    @log_action
    def edit_task(self):
        selected_item = self.task_tree.selection()
        if selected_item:
            item = self.task_tree.item(selected_item)
            task_name, task_status = item["values"]

            new_name = self.task_name_entry.get()
            new_status = self.task_status_combobox.get()
            new_description = self.task_description_text.get(1.0, tk.END).strip()

            for task in self.tasks:
                if task.name == task_name and task.status == task_status:
                    task.name = new_name
                    task.status = new_status
                    task.description = new_description
                    break

            self.task_tree.item(selected_item, values=(new_name, new_status), tags=(new_status,))
            self.save_tasks()
            self.clear_form()

    @log_action
    def delete_task(self):
        selected_item = self.task_tree.selection()
        if selected_item:
            item = self.task_tree.item(selected_item)
            task_name, task_status = item["values"]

            self.tasks = [task for task in self.tasks if not (task.name == task_name and task.status == task_status)]
            self.task_tree.delete(selected_item)
            self.save_tasks()
            self.clear_form()

    def clear_form(self):
        self.task_name_entry.delete(0, tk.END)
        self.task_status_combobox.set("")
        self.task_description_text.delete(1.0, tk.END)

    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, "r") as file:
                data = json.load(file)
                for item in data:
                    task = Task(item["name"], item["status"], item["description"])
                    self.tasks.append(task)
                    self.task_tree.insert("", "end", values=(task.name, task.status), tags=(task.status,))

    def save_tasks(self):
        with open(self.tasks_file, "w") as file:
            json.dump([task.__dict__ for task in self.tasks], file, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()
