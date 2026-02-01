import tkinter as tk
from tkinter import messagebox, filedialog
import qrcode
from PIL import Image, ImageTk

class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("400x550")
        self.root.configure(bg="#2c3e50")

        tk.Label(root, text="QR Code Generator", font=("Helvetica", 20, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=20)

        tk.Label(root, text="Enter URL or Text:", bg="#2c3e50", fg="white").pack()
        self.entry = tk.Entry(root, font=("Helvetica", 12), width=30)
        self.entry.pack(pady=5)

        tk.Button(root, text="Generate QR", command=self.generate_qr, bg="#27ae60", fg="white", font=("Helvetica", 12, "bold")).pack(pady=15)

        self.qr_label = tk.Label(root, bg="#2c3e50")
        self.qr_label.pack(pady=10)

        self.save_btn = tk.Button(root, text="Save Image", command=self.save_qr, bg="#e74c3c", fg="white", font=("Helvetica", 12), state="disabled")
        self.save_btn.pack(pady=10)

        self.qr_image = None

    def generate_qr(self):
        data = self.entry.get()
        if not data:
            messagebox.showwarning("Warning", "Please enter some text!")
            return

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        self.qr_image = img
        
        img_tk = ImageTk.PhotoImage(img.resize((250, 250)))
        self.qr_label.config(image=img_tk)
        self.qr_label.image = img_tk 
        
        self.save_btn.config(state="normal")

    def save_qr(self):
        if self.qr_image:
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if path:
                self.qr_image.save(path)
                messagebox.showinfo("Success", "QR Code Saved Successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()