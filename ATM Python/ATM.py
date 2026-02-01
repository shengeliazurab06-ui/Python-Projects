import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
try:
    from playsound import playsound
except ImportError:
    playsound = None
try:
    import requests
except ImportError:
    requests = None

import json
import shutil
import os
import hashlib
import secrets
from datetime import datetime
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

DB_FILE = "users.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_users(users_data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, indent=4, ensure_ascii=False)

class AnimatedButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        if 'cursor' not in kwargs:
            kwargs['cursor'] = 'hand2'
        super().__init__(master, **kwargs)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        if "Link.TButton" in str(self['style']):
            return
        self.configure(padding=(12, 12, 8, 8))

    def on_release(self, event):
        if "Link.TButton" in str(self['style']):
            return
        self.configure(padding=(10, 10))

class ATM_App:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Samtredia ATM Banking")
        self.root.geometry("400x750")
        self.root.resizable(False, False)

        script_dir_icon = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir_icon, "atm_icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#f0f2f5", "primary": "#5e72e4", "accent": "#324cdd",
                "success": "#2dce89", "text": "#525f7f", "light_text": "#8898aa",
                "entry_bg": "#ffffff", "entry_border": "#cad1d7", "btn_text": "#ffffff"
            },
            "dark": {
                "bg": "#1e1e2f", "primary": "#5e72e4", "accent": "#324cdd",
                "success": "#2dce89", "text": "#f5f6fa", "light_text": "#a4b0be",
                "entry_bg": "#2f3640", "entry_border": "#4b4b4b", "btn_text": "#ffffff"
            }
        }
        
        self.last_screen_func = self.create_main_screen
        self.apply_theme()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        wav_path = os.path.join(script_dir, "click.wav")
        mp3_path = os.path.join(script_dir, "Click.mp3")

        if os.path.exists(wav_path):
            self.click_sound_path = wav_path
        elif os.path.exists(mp3_path):
            self.click_sound_path = mp3_path
        else:
            self.click_sound_path = None

        self.users = load_users()
        self.current_user = None
        self.create_main_screen()

    def apply_theme(self):
        colors = self.themes[self.current_theme]
        self.colors = colors
        
        self.root.configure(bg=colors["bg"])
        
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["text"], font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground=colors["primary"])
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 12), foreground=colors["light_text"])
        self.style.configure("Balance.TLabel", font=("Segoe UI", 32, "bold"), foreground=colors["success"])

        self.style.configure("TButton", 
            font=("Segoe UI", 12, "bold"), 
            padding=(10, 10), 
            borderwidth=0,
            relief="flat",
            background=colors["primary"]
        )
        self.style.map("TButton",
            foreground=[('!active', colors["btn_text"]), ('active', colors["btn_text"])],
            background=[('!active', colors["primary"]), ('active', colors["accent"])]
        )

        self.style.configure("Link.TButton", 
            background=colors["bg"], 
            foreground=colors["primary"], 
            font=("Segoe UI", 10, "underline"), 
            relief="flat", 
            padding=0,
            borderwidth=0
        )
        self.style.map("Link.TButton",
            foreground=[('active', colors["accent"])],
            background=[('active', colors["bg"])]
        )

        self.style.configure("TEntry",
            font=("Segoe UI", 12), padding=10, relief="flat", borderwidth=2, fieldbackground=colors["entry_bg"]
        )
        self.style.map("TEntry",
            lightcolor=[('focus', colors["primary"]), ('!focus', colors["entry_border"])],
            darkcolor=[('focus', colors["primary"]), ('!focus', colors["entry_border"])]
        )
        
        self.style.configure("Treeview", 
            background=colors["entry_bg"],
            foreground=colors["text"],
            fieldbackground=colors["entry_bg"],
            rowheight=25
        )
        self.style.configure("Treeview.Heading", 
            font=("Segoe UI", 10, "bold"),
            background=colors["primary"],
            foreground=colors["btn_text"],
            relief="flat"
        )
        self.style.map("Treeview.Heading",
            background=[('!active', colors["primary"]), ('active', colors["accent"])]
        )

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.last_screen_func()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def play_click_sound(self):
        if playsound and self.click_sound_path:
            try:
                playsound(self.click_sound_path, block=False)
            except Exception as e:
                print(f"Warning: Could not play sound. {e}")

    def with_sound(self, func):
        def wrapper():
            self.play_click_sound()
            func()
        return wrapper

    def create_main_screen(self):
        self.clear_frame()
        self.last_screen_func = self.create_main_screen
        self.current_user = None

        frame = ttk.Frame(self.root, padding=40)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="🏦", font=("Segoe UI Emoji", 48)).pack(pady=(0, 10))
        ttk.Label(frame, text="Welcome to Bank", style="Header.TLabel").pack(pady=(0, 5))
        ttk.Label(frame, text="Your trusted banking partner", style="Subheader.TLabel").pack(pady=(0, 40))

        AnimatedButton(frame, text="Login", command=self.with_sound(self.login_screen), cursor="hand2").pack(pady=10, fill='x')
        AnimatedButton(frame, text="Register", command=self.with_sound(self.register_screen), cursor="hand2").pack(pady=10, fill='x')
        ttk.Separator(frame, orient='horizontal').pack(pady=25, fill='x')
        AnimatedButton(frame, text="Exit Application", command=self.with_sound(self.root.quit), cursor="hand2").pack(pady=10, fill='x')
        
        theme_text = "🌙 Dark Mode" if self.current_theme == "light" else "☀️ Light Mode"
        AnimatedButton(frame, text=theme_text, style="Link.TButton", command=self.with_sound(self.toggle_theme), cursor="hand2").pack(pady=5)

    def register_screen(self):
        self.clear_frame()

        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Create Your Account", style="Header.TLabel").pack(pady=(20, 30))

        ttk.Label(frame, text="Choose a Username").pack(anchor='w', pady=(15, 5))
        self.reg_username_entry = ttk.Entry(frame)
        self.reg_username_entry.pack(fill='x', pady=(0, 20))

        ttk.Label(frame, text="Set a Secure Password").pack(anchor='w', pady=(15, 5))
        self.reg_password_entry = ttk.Entry(frame, show="*")
        self.reg_password_entry.pack(fill='x', pady=(0, 30))

        AnimatedButton(frame, text="Register", command=self.with_sound(self.handle_register), cursor="hand2").pack(fill='x', pady=10)
        AnimatedButton(frame, text="Back to Main Menu", command=self.with_sound(self.create_main_screen), cursor="hand2").pack(fill='x', pady=10)

    def handle_register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if username in self.users:
            messagebox.showerror("Error", "A user with this name already exists.")
            return

        salt = secrets.token_hex(16)
        hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

        self.users[username] = {
            "auth": {
                "salt": salt,
                "hash": hashed_password
            },
            "balance": 0,
            "transactions": []
        }
        save_users(self.users)
        messagebox.showinfo("Success", "Registration successful. You can now log in.")
        self.login_screen()

    def login_screen(self):
        self.clear_frame()

        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Welcome Back", style="Header.TLabel").pack(pady=(20, 30))

        ttk.Label(frame, text="Username").pack(anchor='w', pady=(15, 5))
        self.login_username_entry = ttk.Entry(frame)
        self.login_username_entry.pack(fill='x', pady=(0, 20))

        ttk.Label(frame, text="Password").pack(anchor='w', pady=(15, 5))
        self.login_password_entry = ttk.Entry(frame, show="*")
        self.login_password_entry.pack(fill='x', pady=(0, 30))

        AnimatedButton(frame, text="Login", command=self.with_sound(self.handle_login), cursor="hand2").pack(fill='x', pady=10)
        AnimatedButton(frame, text="Back to Main Menu", command=self.with_sound(self.create_main_screen), cursor="hand2").pack(fill='x', pady=10)

        forgot_password_btn = AnimatedButton(frame, text="Forgot Password?", style="Link.TButton", command=self.with_sound(self.forgot_password_screen), cursor="hand2")
        forgot_password_btn.pack(pady=(20, 0))

    def handle_login(self):
        username = self.login_username_entry.get()
        password = self.login_password_entry.get()

        user_data = self.users.get(username)

        if not user_data:
            messagebox.showerror("Error", "Incorrect username or password.")
            return

        is_login_successful = False
        if "auth" in user_data:
            salt = user_data["auth"]["salt"]
            stored_hash = user_data["auth"]["hash"]
            entered_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            if entered_hash == stored_hash:
                is_login_successful = True
        elif "password" in user_data and user_data["password"] == password:
            is_login_successful = True
            
            salt = secrets.token_hex(16)
            hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            
            user_data["auth"] = {
                "salt": salt,
                "hash": hashed_password
            }
            del user_data["password"]
            save_users(self.users)

        if is_login_successful:
            self.current_user = username
            self.account_screen()
        else:
            messagebox.showerror("Error", "Incorrect username or password.")

    def forgot_password_screen(self):
        username = simpledialog.askstring("Password Recovery", "Please enter your username:", parent=self.root)

        if not username:
            return

        if username not in self.users:
            messagebox.showerror("Error", "User not found.")
            return

        new_password = simpledialog.askstring("New Password", "Enter your new password:", parent=self.root, show='*')
        if not new_password:
            messagebox.showwarning("Cancelled", "Password recovery cancelled.")
            return

        confirm_password = simpledialog.askstring("Confirm Password", "Confirm your new password:", parent=self.root, show='*')
        if not confirm_password:
            messagebox.showwarning("Cancelled", "Password recovery cancelled.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match. Please try again.")
            return

        salt = secrets.token_hex(16)
        hashed_password = hashlib.sha256((new_password + salt).encode('utf-8')).hexdigest()

        self.users[username]["auth"] = {
            "salt": salt,
            "hash": hashed_password
        }

        if "password" in self.users[username]:
            del self.users[username]["password"]

        save_users(self.users)
        messagebox.showinfo("Success", "Your password has been successfully updated. You can now log in with your new password.")
        self.login_screen()

    def account_screen(self):
        self.clear_frame()
        self.last_screen_func = self.account_screen

        frame = ttk.Frame(self.root, padding=(30, 20))
        frame.pack(expand=True, fill="both")

        if Image and ImageTk:
            pic_path = self.users[self.current_user].get("profile_pic")
            if pic_path and os.path.exists(pic_path):
                img = Image.open(pic_path)
            else:
                img = Image.new('RGB', (100, 100), color=self.colors['light_text'])
            
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            self.profile_photo = ImageTk.PhotoImage(img)
            ttk.Label(frame, image=self.profile_photo).pack(pady=(0, 10))
            AnimatedButton(frame, text="📷 Upload Photo", style="Link.TButton", command=self.with_sound(self.upload_profile_pic), cursor="hand2").pack(pady=(0, 10))

        balance = self.users[self.current_user]["balance"]
        ttk.Label(frame, text=f"Welcome, {self.current_user}!", font=("Segoe UI", 18, "bold"), foreground=self.colors["text"]).pack(pady=(5, 2))
        ttk.Label(frame, text="Available Balance", style="Subheader.TLabel").pack()
        self.balance_label = ttk.Label(frame, text=f"{balance:,.2f} GEL", style="Balance.TLabel")
        self.balance_label.pack(pady=(5, 20))

        self.auto_update_balance()
        
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill='x', pady=10)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        AnimatedButton(buttons_frame, text="Deposit", command=self.with_sound(self.deposit), cursor="hand2").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        AnimatedButton(buttons_frame, text="Withdraw", command=self.with_sound(self.withdraw), cursor="hand2").grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        AnimatedButton(buttons_frame, text="Transfer", command=self.with_sound(self.transfer), cursor="hand2").grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        AnimatedButton(buttons_frame, text="History", command=self.with_sound(self.show_history), cursor="hand2").grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        AnimatedButton(buttons_frame, text="Converter", command=self.with_sound(self.currency_converter), cursor="hand2").grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        AnimatedButton(buttons_frame, text="Password", command=self.with_sound(self.change_password), cursor="hand2").grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        
        if self.current_user == "admin":
            AnimatedButton(frame, text="👑 Admin Panel", command=self.with_sound(self.admin_panel_screen), cursor="hand2").pack(pady=5, fill='x')
        
        AnimatedButton(frame, text="Logout", command=self.with_sound(self.create_main_screen), cursor="hand2").pack(pady=20, fill='x')
        
        theme_text = "🌙" if self.current_theme == "light" else "☀️"
        AnimatedButton(frame, text=theme_text, style="Link.TButton", command=self.with_sound(self.toggle_theme), cursor="hand2").place(relx=0.9, rely=0.02, anchor="ne")

    def auto_update_balance(self):
        try:
            if not hasattr(self, 'balance_label') or not self.balance_label.winfo_exists():
                return
            
            self.users = load_users()
            if self.current_user in self.users:
                balance = self.users[self.current_user]["balance"]
                self.balance_label.config(text=f"{balance:,.2f} GEL")
            
            self.root.after(5000, self.auto_update_balance)
        except Exception:
            pass

    def upload_profile_pic(self):
        if not Image:
            messagebox.showerror("Error", "PIL library not installed. Run: pip install Pillow")
            return
            
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return
            
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile_pics")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        ext = os.path.splitext(file_path)[1]
        new_filename = f"{self.current_user}_{int(datetime.now().timestamp())}{ext}"
        dest_path = os.path.join(save_dir, new_filename)
        
        try:
            shutil.copy(file_path, dest_path)
            self.users[self.current_user]["profile_pic"] = dest_path
            save_users(self.users)
            self.account_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload: {e}")

    def get_usd_to_gel_rate(self):
        default_rate = 2.80
        if not requests:
            return default_rate
        try:
            url = "https://open.er-api.com/v6/latest/USD"
            response = requests.get(url, timeout=5)
            response.raise_for_status()  
            data = response.json()
            rate = data.get("rates", {}).get("GEL")
            if rate:
                return float(rate)
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch currency rate from API: {e}. Using default rate.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Using default rate.")
        return default_rate

    def currency_converter(self):
        rate = self.get_usd_to_gel_rate()
        amount_usd = simpledialog.askfloat("Currency Converter", f"Enter amount in USD (1 USD ≈ {rate:.2f} GEL):", parent=self.root, minvalue=0.01)
        if amount_usd is not None:
            amount_gel = amount_usd * rate
            messagebox.showinfo("Conversion Result", f"{amount_usd:.2f} USD is approximately {amount_gel:.2f} GEL.")

    def deposit(self):
        amount = simpledialog.askfloat("Deposit", "Enter amount:", parent=self.root, minvalue=0.01)
        if amount is not None:
            self.users[self.current_user]["balance"] += amount
            transaction = {
                "timestamp": datetime.now().isoformat(),
                "type": "deposit",
                "amount": amount
            }
            self.users[self.current_user]["transactions"].append(transaction)
            save_users(self.users)
            messagebox.showinfo("Success", f"{amount:.2f} GEL has been deposited.")
            self.account_screen()

    def withdraw(self):
        amount = simpledialog.askfloat("Withdraw", "Enter amount:", parent=self.root, minvalue=0.01)
        if amount is not None:
            current_balance = self.users[self.current_user]["balance"]
            min_balance = 10.00
            if current_balance - amount < min_balance:
                messagebox.showerror("Error", f"Insufficient funds. You must maintain a minimum balance of {min_balance:.2f} GEL.")
                return

            daily_limit = 1000.00
            today_str = datetime.now().strftime('%Y-%m-%d')
            withdrawn_today = 0.0
            
            for tx in self.users[self.current_user]["transactions"]:
                if isinstance(tx, dict) and tx.get("type") == "withdrawal":
                    tx_date = datetime.fromisoformat(tx["timestamp"]).strftime('%Y-%m-%d')
                    if tx_date == today_str:
                        withdrawn_today += tx.get("amount", 0)
            
            if withdrawn_today + amount > daily_limit:
                remaining_limit = max(0, daily_limit - withdrawn_today)
                messagebox.showerror("Limit Exceeded", f"Daily withdrawal limit is {daily_limit:.2f} GEL.\nYou have withdrawn {withdrawn_today:.2f} GEL today.\nRemaining limit: {remaining_limit:.2f} GEL.")
                return

            if amount <= current_balance:
                self.users[self.current_user]["balance"] -= amount
                transaction = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "withdrawal",
                    "amount": amount
                }
                self.users[self.current_user]["transactions"].append(transaction)
                save_users(self.users)
                messagebox.showinfo("Success", f"{amount:.2f} GEL has been withdrawn.")
                self.account_screen()
            else:
                messagebox.showerror("Error", "Insufficient funds on your balance.")

    def transfer(self):
        recipient_name = simpledialog.askstring("Transfer", "Enter recipient username:", parent=self.root)
        if not recipient_name:
            return
        
        if recipient_name not in self.users:
            messagebox.showerror("Error", "Recipient not found.")
            return
            
        if recipient_name == self.current_user:
            messagebox.showerror("Error", "You cannot transfer money to yourself.")
            return

        amount = simpledialog.askfloat("Transfer", "Enter amount:", parent=self.root, minvalue=0.01)
        if amount is not None:
            current_balance = self.users[self.current_user]["balance"]
            if amount <= current_balance:
                self.users[self.current_user]["balance"] -= amount
                self.users[self.current_user]["transactions"].append({"timestamp": datetime.now().isoformat(), "type": "transfer_out", "amount": amount, "to": recipient_name})

                self.users[recipient_name]["balance"] += amount
                self.users[recipient_name]["transactions"].append({"timestamp": datetime.now().isoformat(), "type": "transfer_in", "amount": amount, "from": self.current_user})

                save_users(self.users)
                messagebox.showinfo("Success", f"{amount:.2f} GEL transferred to {recipient_name}.")
                self.account_screen()
            else:
                messagebox.showerror("Error", "Insufficient funds.")

    def change_password(self):
        current_password = simpledialog.askstring("Change Password", "Enter current password:", parent=self.root, show='*')
        if not current_password:
            return

        user_data = self.users[self.current_user]
        is_valid = False
        
        if "auth" in user_data:
            salt = user_data["auth"]["salt"]
            stored_hash = user_data["auth"]["hash"]
            entered_hash = hashlib.sha256((current_password + salt).encode('utf-8')).hexdigest()
            if entered_hash == stored_hash:
                is_valid = True
        elif "password" in user_data and user_data["password"] == current_password:
            is_valid = True

        if not is_valid:
            messagebox.showerror("Error", "Incorrect current password.")
            return

        new_password = simpledialog.askstring("Change Password", "Enter new password:", parent=self.root, show='*')
        if not new_password:
            return

        confirm_password = simpledialog.askstring("Change Password", "Confirm new password:", parent=self.root, show='*')
        if not confirm_password:
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        salt = secrets.token_hex(16)
        hashed_password = hashlib.sha256((new_password + salt).encode('utf-8')).hexdigest()

        self.users[self.current_user]["auth"] = {
            "salt": salt,
            "hash": hashed_password
        }
        
        if "password" in self.users[self.current_user]:
            del self.users[self.current_user]["password"]

        save_users(self.users)
        messagebox.showinfo("Success", "Password changed successfully.")

    def show_history(self):
        history = self.users[self.current_user]["transactions"]
        if not history:
            messagebox.showinfo("History", "No transactions found.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("Transaction History")
        history_window.geometry("500x500")
        history_window.configure(bg=self.colors["bg"])

        ttk.Label(history_window, text="Transaction History", style="Header.TLabel").pack(pady=20)

        text_frame = ttk.Frame(history_window, padding=10)
        text_frame.pack(fill="both", expand=True)
        
        history_text_widget = tk.Text(text_frame, height=15, width=50, font=("Consolas", 11), 
                                    bg=self.colors["entry_bg"], 
                                    fg=self.colors["text"],
                                    relief="solid", borderwidth=1, padx=10, pady=10)
        history_text_widget.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=history_text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        history_text_widget.config(yscrollcommand=scrollbar.set)
        
        history_text_widget.tag_config("green", foreground=self.colors["success"])
        history_text_widget.tag_config("red", foreground="#f5365c")
        history_text_widget.tag_config("black", foreground=self.colors["light_text"])

        for tx in reversed(history):
            if isinstance(tx, dict):
                try:
                    ts = datetime.fromisoformat(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    
                    raw_type = tx.get('type', 'unknown')
                    if raw_type == 'transfer_out':
                        tx_type = "Transfer"
                    elif raw_type == 'transfer_in':
                        tx_type = "Transfer"
                    else:
                        tx_type = raw_type.capitalize()
                    
                    amount = tx.get('amount', 0.0)
                    
                    if raw_type in ["deposit", "transfer_in"]:
                        sign = "+"
                        tag = "green"
                    else:
                        sign = "-"
                        tag = "red"
                    
                    details = ""
                    if "to" in tx:
                        details = f" (To: {tx['to']})"
                    elif "from" in tx:
                        details = f" (From: {tx['from']})"
                    
                    line = f"{ts} | {tx_type}: {sign}{amount:.2f} GEL{details}\n"
                    history_text_widget.insert("end", line, tag)
                except Exception as e:
                    print(f"Skipping invalid transaction: {e}")
            elif isinstance(tx, str):
                history_text_widget.insert("end", tx + "\n", "black")

        history_text_widget.config(state="disabled")

        AnimatedButton(history_window, text="Close", command=self.with_sound(history_window.destroy), cursor="hand2").pack(pady=15)

    def admin_panel_screen(self):
        if self.current_user != "admin":
            messagebox.showerror("Access Denied", "You do not have permission to access this panel.")
            return

        admin_window = tk.Toplevel(self.root)
        admin_window.title("Administrator Panel")
        admin_window.geometry("600x400")
        admin_window.configure(bg=self.colors["bg"])
        admin_window.transient(self.root)
        admin_window.grab_set()

        tk.Label(admin_window, text="User Management", font=("Segoe UI", 16, "bold"), bg=self.colors["bg"], fg=self.colors["primary"]).pack(pady=20)

        tree_frame = ttk.Frame(admin_window)
        tree_frame.pack(pady=10, padx=20, fill="both", expand=True)

        columns = ("username", "balance", "transactions")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        tree.heading("username", text="Username")
        tree.heading("balance", text="Balance (GEL)")
        tree.heading("transactions", text="Transactions")
        
        tree.column("username", width=150)
        tree.column("balance", width=150, anchor="e")
        tree.column("transactions", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        all_users = load_users()
        for username, data in all_users.items():
            balance = data.get("balance", 0)
            num_transactions = len(data.get("transactions", []))
            tree.insert("", "end", values=(username, f"{balance:,.2f}", num_transactions))

        AnimatedButton(admin_window, text="Close", command=admin_window.destroy, cursor="hand2").pack(pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = ATM_App(root)
    root.mainloop()