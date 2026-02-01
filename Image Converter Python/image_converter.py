import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        self.root.geometry("500x450")
        self.root.configure(bg="#2c3e50")

        self.file_path = None

        tk.Label(root, text="🖼️ Image Converter", font=("Helvetica", 20, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=20)

        self.select_btn = tk.Button(root, text="Select Image", command=self.select_image, font=("Helvetica", 12), bg="#3498db", fg="white")
        self.select_btn.pack(pady=10)

        self.file_label = tk.Label(root, text="No file selected", bg="#2c3e50", fg="#bdc3c7", wraplength=400)
        self.file_label.pack(pady=5)

        options_frame = tk.Frame(root, bg="#2c3e50")
        options_frame.pack(pady=20)

        tk.Label(options_frame, text="Convert to:", bg="#2c3e50", fg="white").grid(row=0, column=0, padx=5)
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, values=["PNG", "JPEG", "BMP", "WEBP", "ICO"], state="readonly", width=10)
        self.format_combo.current(1) # Default JPEG
        self.format_combo.grid(row=0, column=1, padx=5)

        tk.Label(options_frame, text="Resize (Optional):", bg="#2c3e50", fg="white").grid(row=1, column=0, padx=5, pady=15)
        
        self.width_entry = tk.Entry(options_frame, width=8)
        self.width_entry.insert(0, "Width")
        self.width_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.width_entry, "Width"))
        self.width_entry.grid(row=1, column=1, padx=2)

        tk.Label(options_frame, text="x", bg="#2c3e50", fg="white").grid(row=1, column=2)

        self.height_entry = tk.Entry(options_frame, width=8)
        self.height_entry.insert(0, "Height")
        self.height_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.height_entry, "Height"))
        self.height_entry.grid(row=1, column=3, padx=2)

        self.convert_btn = tk.Button(root, text="Convert & Save", command=self.convert_image, font=("Helvetica", 14, "bold"), bg="#27ae60", fg="white", state="disabled")
        self.convert_btn.pack(pady=20)

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def select_image(self):
        file_types = [("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp;*.tiff")]
        path = filedialog.askopenfilename(filetypes=file_types)
        if path:
            self.file_path = path
            self.file_label.config(text=os.path.basename(path))
            self.convert_btn.config(state="normal")

    def convert_image(self):
        if not self.file_path:
            return

        try:
            img = Image.open(self.file_path)
            
            w_val = self.width_entry.get()
            h_val = self.height_entry.get()
            
            if w_val.isdigit() and h_val.isdigit():
                new_size = (int(w_val), int(h_val))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            target_format = self.format_var.get()
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=f".{target_format.lower()}",
                filetypes=[(f"{target_format} File", f"*.{target_format.lower()}")],
                initialfile=f"converted_image.{target_format.lower()}"
            )

            if save_path:
                if target_format == "JPEG":
                    img = img.convert("RGB") 
                
                img.save(save_path, format=target_format)
                messagebox.showinfo("Success", f"Image saved successfully!\n{save_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()