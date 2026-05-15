import fitz  # PyMuPDF
from PIL import Image, ImageEnhance
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class SahajiNetPoint:
    def __init__(self, root):
        self.root = root
        self.root.title("Sahaji Net Point - PVC Studio")
        self.root.geometry("450x600")
        self.root.configure(bg="#1a1a1a")

        tk.Label(root, text="SAHAJI NET POINT", font=("Arial", 22, "bold"), bg="#1a1a1a", fg="#00d2ff").pack(pady=20)
        
        btn_frame = tk.Frame(root, bg="#1a1a1a")
        btn_frame.pack(pady=10)

        style = {"font": ("Arial", 11, "bold"), "width": 28, "pady": 10, "cursor": "hand2", "fg": "white"}
        
        tk.Button(btn_frame, text="Aadhaar 1-Click Print", bg="#2980b9", command=lambda: self.process("Aadhaar"), **style).pack(pady=8)
        tk.Button(btn_frame, text="Voter / PAN Card", bg="#27ae60", command=lambda: self.process("Voter"), **style).pack(pady=8)
        tk.Button(btn_frame, text="Health / ABHA Card", bg="#e67e22", command=lambda: self.process("Health"), **style).pack(pady=8)
        tk.Button(btn_frame, text="Ration / Others", bg="#8e44ad", command=lambda: self.process("Other"), **style).pack(pady=8)

        self.status = tk.Label(root, text="System Ready", bg="#1a1a1a", fg="#777")
        self.status.pack(side="bottom", pady=20)

    def process(self, mode):
        path = filedialog.askopenfilename(filetypes=[("PDF/Images", "*.pdf *.jpg *.png")])
        if not path: return
        self.status.config(text="Processing...", fg="#f1c40f")
        self.root.update()
        try:
            doc = fitz.open(path)
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(5, 5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pvc = (1012, 638)
            if mode == "Aadhaar":
                f, b = img.crop((400, 2900, 3100, 4700)), img.crop((3200, 2900, 5900, 4700))
            else:
                f, b = img.crop((500, 500, 3500, 2500)), img.crop((500, 2600, 3500, 4600))
            f, b = f.resize(pvc, Image.LANCZOS), b.resize(pvc, Image.LANCZOS)
            save_path = filedialog.askdirectory()
            if save_path:
                f.save(os.path.join(save_path, "Front.png"), dpi=(300, 300))
                b.save(os.path.join(save_path, "Back.png"), dpi=(300, 300))
                messagebox.showinfo("Success", "Card Saved!")
                self.status.config(text="Done!", fg="#2ecc71")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiNetPoint(root)
    root.mainloop()
