import tkinter as tk
from tkinter import messagebox
import random
import time
import sqlite3
import os

class CasinoApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Python Casino Royale")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        self.bg_color = "#2c3e50"
        self.accent_color = "#f1c40f"
        self.btn_color = "#e74c3c"
        self.win_color = "#2ecc71"
        self.text_color = "#ecf0f1"

        self.root.configure(bg=self.bg_color)

        self.init_db()
        self.symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣", "🍇"]
        self.is_spinning = False

        self.create_widgets()

    def init_db(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "casino_data.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT balance FROM users WHERE username=?", (self.username,))
        result = self.cursor.fetchone()
        if result:
            self.balance = result[0]
        else:
            self.balance = 0

    def save_balance(self):
        self.cursor.execute("UPDATE users SET balance=? WHERE username=?", (self.balance, self.username))
        self.conn.commit()

    def create_widgets(self):
        title_label = tk.Label(
            self.root, 
            text="🎰 LUCKY SLOTS 🎰", 
            font=("Helvetica", 28, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(pady=20)

        self.balance_label = tk.Label(
            self.root,
            text=f"Balance: ${self.balance}",
            font=("Helvetica", 18),
            bg=self.bg_color,
            fg=self.win_color
        )
        self.balance_label.pack(pady=10)

        self.slots_frame = tk.Frame(self.root, bg="#34495e", bd=5, relief="sunken")
        self.slots_frame.pack(pady=20, padx=20)

        self.reel_labels = []
        for i in range(3):
            lbl = tk.Label(
                self.slots_frame,
                text="❓",
                font=("Segoe UI Emoji", 48),
                width=2,
                bg="#ecf0f1",
                fg="#2c3e50"
            )
            lbl.grid(row=0, column=i, padx=10, pady=10)
            self.reel_labels.append(lbl)

        bet_frame = tk.Frame(self.root, bg=self.bg_color)
        bet_frame.pack(pady=20)

        tk.Label(bet_frame, text="Bet: $", font=("Helvetica", 14), bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
        
        self.bet_entry = tk.Entry(bet_frame, font=("Helvetica", 14), width=10, justify="center")
        self.bet_entry.insert(0, "100")
        self.bet_entry.pack(side=tk.LEFT, padx=5)

        self.spin_btn = tk.Button(
            self.root,
            text="SPIN",
            font=("Helvetica", 16, "bold"),
            bg=self.btn_color,
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            command=self.start_spin,
            cursor="hand2",
            relief="raised",
            bd=3
        )
        self.spin_btn.pack(pady=20, ipadx=20, ipady=5)

        self.bj_btn = tk.Button(
            self.root,
            text="Play BLACKJACK",
            font=("Helvetica", 12, "bold"),
            bg="#8e44ad",
            fg="white",
            activebackground="#9b59b6",
            activeforeground="white",
            command=self.open_blackjack
        )
        self.bj_btn.pack(pady=5, ipadx=10)

        self.rl_btn = tk.Button(
            self.root,
            text="Play ROULETTE",
            font=("Helvetica", 12, "bold"),
            bg="#16a085",
            fg="white",
            activebackground="#1abc9c",
            activeforeground="white",
            command=self.open_roulette
        )
        self.rl_btn.pack(pady=5, ipadx=10)

        self.status_label = tk.Label(
            self.root,
            text="Good Luck!",
            font=("Helvetica", 12),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.status_label.pack(pady=10)

    def open_blackjack(self):
        BlackjackGame(self.root, self)

    def open_roulette(self):
        RouletteGame(self.root, self)

    def start_spin(self):
        if self.is_spinning:
            return

        try:
            bet_amount = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
            return

        if bet_amount <= 0:
            messagebox.showwarning("Warning", "Bet must be greater than 0!")
            return
        
        if bet_amount > self.balance:
            messagebox.showerror("Insufficient Funds", "You don't have enough money for this bet.")
            return

        self.balance -= bet_amount
        self.update_balance()
        self.status_label.config(text="Spinning...", fg=self.accent_color)
        
        self.is_spinning = True
        self.spin_btn.config(state="disabled")
        self.animate_reels(0, bet_amount)

    def animate_reels(self, count, bet_amount):
        if count < 15:
            temp_results = [random.choice(self.symbols) for _ in range(3)]
            for i, symbol in enumerate(temp_results):
                self.reel_labels[i].config(text=symbol)

            self.root.after(100, lambda: self.animate_reels(count + 1, bet_amount))
        else:
            self.finalize_spin(bet_amount)

    def finalize_spin(self, bet_amount):
        final_results = [random.choice(self.symbols) for _ in range(3)]
        
        for i, symbol in enumerate(final_results):
            self.reel_labels[i].config(text=symbol)

        if final_results[0] == final_results[1] == final_results[2]:
            win_amount = bet_amount * 10
            self.balance += win_amount
            self.status_label.config(text=f"🎉 JACKPOT! You won ${win_amount}!", fg=self.win_color)
            messagebox.showinfo("JACKPOT!", f"Congratulations! You won ${win_amount}")
        elif final_results[0] == final_results[1] or final_results[1] == final_results[2] or final_results[0] == final_results[2]:
            win_amount = bet_amount * 2
            self.balance += win_amount
            self.status_label.config(text=f"✨ Small Win! You won ${win_amount}!", fg=self.accent_color)
        else:
            self.status_label.config(text="You lost. Try again!", fg="#e74c3c")

        self.update_balance()
        self.is_spinning = False
        self.spin_btn.config(state="normal")

    def update_balance(self):
        self.balance_label.config(text=f"Balance: ${self.balance}")
        self.save_balance()

class BlackjackGame:
    def __init__(self, master, app):
        self.window = tk.Toplevel(master)
        self.window.title("Blackjack 21")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        self.app = app
        self.bg_color = "#20523e"
        self.window.configure(bg=self.bg_color)
        
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.bet = 0
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="♠♥ BLACKJACK ♦♣", font=("Helvetica", 24, "bold"), bg=self.bg_color, fg="#f1c40f").pack(pady=10)
        
        self.dealer_frame = tk.Frame(self.window, bg=self.bg_color)
        self.dealer_frame.pack(pady=10)
        tk.Label(self.dealer_frame, text="Dealer", font=("Helvetica", 12), bg=self.bg_color, fg="white").pack()
        self.dealer_lbl = tk.Label(self.dealer_frame, text="", font=("Segoe UI Emoji", 24), bg=self.bg_color, fg="white")
        self.dealer_lbl.pack()
        
        self.player_frame = tk.Frame(self.window, bg=self.bg_color)
        self.player_frame.pack(pady=10)
        tk.Label(self.player_frame, text="You", font=("Helvetica", 12), bg=self.bg_color, fg="white").pack()
        self.player_lbl = tk.Label(self.player_frame, text="", font=("Segoe UI Emoji", 24), bg=self.bg_color, fg="white")
        self.player_lbl.pack()
        
        controls = tk.Frame(self.window, bg=self.bg_color)
        controls.pack(pady=20)
        
        tk.Label(controls, text="Bet:", bg=self.bg_color, fg="white").grid(row=0, column=0)
        self.bet_entry = tk.Entry(controls, width=8)
        self.bet_entry.insert(0, "100")
        self.bet_entry.grid(row=0, column=1, padx=5)
        
        self.deal_btn = tk.Button(controls, text="DEAL", command=self.deal, bg="#e67e22", fg="white")
        self.deal_btn.grid(row=0, column=2, padx=5)
        
        self.hit_btn = tk.Button(controls, text="HIT", command=self.hit, state="disabled", bg="#3498db", fg="white")
        self.hit_btn.grid(row=0, column=3, padx=5)
        
        self.stand_btn = tk.Button(controls, text="STAND", command=self.stand, state="disabled", bg="#e74c3c", fg="white")
        self.stand_btn.grid(row=0, column=4, padx=5)
        
        self.status_lbl = tk.Label(self.window, text="", font=("Helvetica", 12), bg=self.bg_color, fg="#f1c40f")
        self.status_lbl.pack(pady=10)

    def get_deck(self):
        suits = ["♠", "♥", "♦", "♣"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        deck = [(r, s) for s in suits for r in ranks]
        random.shuffle(deck)
        return deck

    def calculate_score(self, hand):
        score = 0
        aces = 0
        for r, s in hand:
            if r in ["J", "Q", "K"]: score += 10
            elif r == "A": aces += 1; score += 11
            else: score += int(r)
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def display_hands(self, hide_dealer=True):
        p_text = " ".join([f"{r}{s}" for r, s in self.player_hand])
        self.player_lbl.config(text=f"{p_text} ({self.calculate_score(self.player_hand)})")
        
        if hide_dealer:
            d_text = f"{self.dealer_hand[0][0]}{self.dealer_hand[0][1]} 🂠"
        else:
            d_text = " ".join([f"{r}{s}" for r, s in self.dealer_hand])
            d_text += f" ({self.calculate_score(self.dealer_hand)})"
        self.dealer_lbl.config(text=d_text)

    def deal(self):
        try: self.bet = int(self.bet_entry.get())
        except: return
        if self.bet > self.app.balance or self.bet <= 0:
            messagebox.showerror("Error", "Invalid Bet", parent=self.window)
            return
        
        self.app.balance -= self.bet
        self.app.update_balance()
        self.deck = self.get_deck()
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.hit_btn.config(state="normal"); self.stand_btn.config(state="normal"); self.deal_btn.config(state="disabled")
        self.display_hands()
        self.status_lbl.config(text="Game Started!")

    def hit(self):
        self.player_hand.append(self.deck.pop())
        self.display_hands()
        if self.calculate_score(self.player_hand) > 21:
            self.end_game(False)

    def stand(self):
        while self.calculate_score(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())
        p_score = self.calculate_score(self.player_hand)
        d_score = self.calculate_score(self.dealer_hand)
        if d_score > 21 or p_score > d_score: self.end_game(True)
        elif p_score < d_score: self.end_game(False)
        else: self.end_game("Push")

    def end_game(self, win):
        self.display_hands(hide_dealer=False)
        self.hit_btn.config(state="disabled"); self.stand_btn.config(state="disabled"); self.deal_btn.config(state="normal")
        if win == True:
            self.app.balance += self.bet * 2
            self.status_lbl.config(text=f"You Win! (+${self.bet * 2})")
        elif win == "Push":
            self.app.balance += self.bet
            self.status_lbl.config(text="Push! Bet returned.")
        else:
            self.status_lbl.config(text="Dealer Wins!")
        self.app.update_balance()

class RouletteGame:
    def __init__(self, master, app):
        self.window = tk.Toplevel(master)
        self.window.title("Roulette")
        self.window.geometry("500x450")
        self.window.resizable(False, False)
        self.app = app
        self.bg_color = "#006400"
        self.window.configure(bg=self.bg_color)
        
        self.red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="🎡 ROULETTE 🎡", font=("Helvetica", 24, "bold"), bg=self.bg_color, fg="gold").pack(pady=10)
        
        self.result_lbl = tk.Label(self.window, text="?", font=("Helvetica", 48, "bold"), bg="white", width=4)
        self.result_lbl.pack(pady=20)
        
        control_frame = tk.Frame(self.window, bg=self.bg_color)
        control_frame.pack(pady=10)
        
        tk.Label(control_frame, text="Bet Amount:", bg=self.bg_color, fg="white").grid(row=0, column=0, padx=5)
        self.bet_entry = tk.Entry(control_frame, width=10)
        self.bet_entry.insert(0, "100")
        self.bet_entry.grid(row=0, column=1, padx=5)
        
        self.bet_type = tk.StringVar(value="color")
        type_frame = tk.Frame(self.window, bg=self.bg_color)
        type_frame.pack(pady=5)
        
        tk.Radiobutton(type_frame, text="Color (Red/Black)", variable=self.bet_type, value="color", bg=self.bg_color, fg="white", selectcolor="#2c3e50", command=self.toggle_inputs).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="Number (0-36)", variable=self.bet_type, value="number", bg=self.bg_color, fg="white", selectcolor="#2c3e50", command=self.toggle_inputs).pack(side=tk.LEFT, padx=10)
        
        self.input_frame = tk.Frame(self.window, bg=self.bg_color)
        self.input_frame.pack(pady=10)
        
        self.color_var = tk.StringVar(value="Red")
        self.red_btn = tk.Radiobutton(self.input_frame, text="RED", variable=self.color_var, value="Red", bg="red", fg="white", indicatoron=0, width=10)
        self.black_btn = tk.Radiobutton(self.input_frame, text="BLACK", variable=self.color_var, value="Black", bg="black", fg="white", indicatoron=0, width=10)
        
        self.num_entry = tk.Entry(self.input_frame, width=5)
        
        self.toggle_inputs()
        
        tk.Button(self.window, text="SPIN WHEEL", command=self.spin, font=("Helvetica", 14, "bold"), bg="#f39c12", fg="white").pack(pady=20)
        
        self.status_lbl = tk.Label(self.window, text="", font=("Helvetica", 12), bg=self.bg_color, fg="white")
        self.status_lbl.pack()

    def toggle_inputs(self):
        for widget in self.input_frame.winfo_children():
            widget.grid_forget()
            
        if self.bet_type.get() == "color":
            self.red_btn.grid(row=0, column=0, padx=5)
            self.black_btn.grid(row=0, column=1, padx=5)
        else:
            tk.Label(self.input_frame, text="Number (0-36):", bg=self.bg_color, fg="white").grid(row=0, column=0)
            self.num_entry.grid(row=0, column=1)

    def spin(self):
        try: bet = int(self.bet_entry.get())
        except: return
        
        if bet > self.app.balance or bet <= 0:
            messagebox.showerror("Error", "Invalid Bet", parent=self.window)
            return
            
        winning_num = random.randint(0, 36)
        winning_color = "Red" if winning_num in self.red_numbers else ("Black" if winning_num != 0 else "Green")
        
        self.app.balance -= bet
        self.app.update_balance()
        
        self.result_lbl.config(text=str(winning_num), fg="white", bg="red" if winning_color == "Red" else ("black" if winning_color == "Black" else "green"))
        
        win = False
        payout = 0
        
        if self.bet_type.get() == "color":
            chosen = self.color_var.get()
            if chosen == winning_color:
                win = True
                payout = bet * 2
        else:
            try: chosen_num = int(self.num_entry.get())
            except: return
            if chosen_num == winning_num:
                win = True
                payout = bet * 36
                
        if win:
            self.app.balance += payout
            self.status_lbl.config(text=f"WIN! {winning_color} {winning_num} (+${payout})", fg="gold")
        else:
            self.status_lbl.config(text=f"LOST. Result: {winning_color} {winning_num}", fg="white")
        
        self.app.update_balance()

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(root)
        self.win.title("Casino Login")
        self.win.geometry("300x250")
        self.win.configure(bg="#2c3e50")
        self.win.protocol("WM_DELETE_WINDOW", self.root.destroy)
        
        tk.Label(self.win, text="Welcome", font=("Helvetica", 16), bg="#2c3e50", fg="white").pack(pady=10)
        
        tk.Label(self.win, text="Username:", bg="#2c3e50", fg="white").pack()
        self.user_entry = tk.Entry(self.win)
        self.user_entry.pack(pady=5)
        
        tk.Label(self.win, text="Password:", bg="#2c3e50", fg="white").pack()
        self.pass_entry = tk.Entry(self.win, show="*")
        self.pass_entry.pack(pady=5)
        
        tk.Button(self.win, text="LOGIN", command=self.login, bg="#2ecc71", fg="white", width=15).pack(pady=10)
        tk.Button(self.win, text="REGISTER", command=self.register, bg="#3498db", fg="white", width=15).pack()

    def get_db(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "casino_data.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance INTEGER)")
        conn.commit()
        return conn, cursor

    def login(self):
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        conn, cursor = self.get_db()
        cursor.execute("SELECT password FROM users WHERE username=?", (user,))
        res = cursor.fetchone()
        conn.close()
        
        if res and res[0] == pwd:
            self.win.destroy()
            self.root.deiconify()
            CasinoApp(self.root, user)
        else:
            messagebox.showerror("Error", "Invalid credentials", parent=self.win)

    def register(self):
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        if not user or not pwd:
            messagebox.showerror("Error", "Fields cannot be empty", parent=self.win)
            return
            
        conn, cursor = self.get_db()
        try:
            cursor.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, 1000)", (user, pwd))
            conn.commit()
            messagebox.showinfo("Success", "Registered! Please Login.", parent=self.win)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists", parent=self.win)
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    LoginWindow(root)
    root.mainloop()