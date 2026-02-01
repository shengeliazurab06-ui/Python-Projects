import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("600x450")
        self.root.configure(bg="#ecf0f1")
        
        self.init_db()
        
        tk.Label(root, text="💰 My Expenses", font=("Helvetica", 20, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=10)
        
        input_frame = tk.Frame(root, bg="#ecf0f1")
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Item:", bg="#ecf0f1").grid(row=0, column=0)
        self.item_entry = tk.Entry(input_frame, width=20)
        self.item_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(input_frame, text="Amount ($):", bg="#ecf0f1").grid(row=0, column=2)
        self.amount_entry = tk.Entry(input_frame, width=10)
        self.amount_entry.grid(row=0, column=3, padx=5)
        
        add_btn = tk.Button(input_frame, text="Add", command=self.add_expense, bg="#27ae60", fg="white")
        add_btn.grid(row=0, column=4, padx=10)
        
        # ცხრილი (Treeview)
        columns = ("ID", "Item", "Amount")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Item", text="Item")
        self.tree.heading("Amount", text="Amount ($)")
        
        self.tree.column("ID", width=50)
        self.tree.column("Item", width=200)
        self.tree.column("Amount", width=100)
        
        self.tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.load_data()

    def init_db(self):
        self.conn = sqlite3.connect("expenses.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, item TEXT, amount REAL)")
        self.conn.commit()

    def add_expense(self):
        item = self.item_entry.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return
            
        if item and amount:
            self.cursor.execute("INSERT INTO expenses (item, amount) VALUES (?, ?)", (item, amount))
            self.conn.commit()
            self.item_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.cursor.execute("SELECT * FROM expenses")
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()