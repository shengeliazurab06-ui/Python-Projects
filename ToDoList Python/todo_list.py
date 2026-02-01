import tkinter as tk
from tkinter import messagebox
import sqlite3

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My To-Do List")
        self.root.geometry("400x500")
        self.root.configure(bg="#f0f2f5")

        self.conn = sqlite3.connect("todo_list.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT)")
        self.conn.commit()

        tk.Label(root, text="📝 Daily Tasks", font=("Helvetica", 20, "bold"), bg="#f0f2f5", fg="#333").pack(pady=15)

        input_frame = tk.Frame(root, bg="#f0f2f5")
        input_frame.pack(pady=10)

        self.task_entry = tk.Entry(input_frame, font=("Helvetica", 12), width=25)
        self.task_entry.pack(side=tk.LEFT, padx=5)
        
        add_btn = tk.Button(input_frame, text="+", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=3, command=self.add_task)
        add_btn.pack(side=tk.LEFT)

        self.listbox = tk.Listbox(root, font=("Helvetica", 12), width=40, height=15, selectmode=tk.SINGLE, bd=0)
        self.listbox.pack(pady=10, padx=20)

        btn_frame = tk.Frame(root, bg="#f0f2f5")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Delete Selected", command=self.delete_task, bg="#e74c3c", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Clear All", command=self.clear_all, bg="#34495e", fg="white").pack(side=tk.LEFT, padx=10)

        self.load_tasks()

    def add_task(self):
        task = self.task_entry.get()
        if task:
            self.cursor.execute("INSERT INTO tasks (title) VALUES (?)", (task,))
            self.conn.commit()
            self.task_entry.delete(0, tk.END)
            self.load_tasks()
        else:
            messagebox.showwarning("Warning", "Task cannot be empty!")

    def delete_task(self):
        try:
            index = self.listbox.curselection()[0]
            task_id = self.task_ids[index]
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.conn.commit()
            self.load_tasks()
        except IndexError:
            messagebox.showwarning("Warning", "Select a task to delete")

    def clear_all(self):
        if messagebox.askyesno("Confirm", "Delete all tasks?"):
            self.cursor.execute("DELETE FROM tasks")
            self.conn.commit()
            self.load_tasks()

    def load_tasks(self):
        self.listbox.delete(0, tk.END)
        self.task_ids = []
        self.cursor.execute("SELECT * FROM tasks")
        for row in self.cursor.fetchall():
            self.task_ids.append(row[0])
            self.listbox.insert(tk.END, f"• {row[1]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()