import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageTk, ImageWin
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32print
import win32ui
import os

class SahajiActionStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("SAHAJI ACTION STUDIO - Pro PVC Solution")
        self.root.geometry("1200x780")
        self.root.configure(bg="#0f172a")

        # --- Sidebar / Controls ---
        sidebar = tk.Frame(root, bg="#1e293b", width=350)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)

        # Branding
        tk.Label(sidebar, text="SAHAJI ACTION", font=("Verdana", 22, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=30)

        # Settings
        lbl_style = {"bg": "#1e293b", "fg": "#94a3b8", "font": ("Arial", 9, "bold")}
        
        tk.Label(sidebar, text="--- DEFAULT PRINTER ---", **lbl_style).pack(pady=(10,5))
        self.printers = [p[2] for p in win32print.EnumPrinters(2)]
        self.printer_var = tk.StringVar()
        self.p_combo = ttk.Combobox(sidebar, textvariable=self.printer_var, values=self.printers, state="readonly", width=35)
        self.p_combo.pack(pady=5, padx=20)
        if self.printers: self.p_combo.current(0)

        tk.Label(sidebar, text="--- PDF ACCESS PIN ---", **lbl_style).pack(pady=(15,5))
        self.password = tk.StringVar(value="RITI2000") # আপনার দেওয়া নতুন পাসওয়ার্ড
        tk.Entry(sidebar, textvariable=self.password, font=("Arial", 14), bg="#334155", fg="white", bd=0, justify="center").pack(fill="x", padx=40, pady=5)

        # Main Actions
        tk.Button(sidebar, text="📂 LOAD AADHAAR PDF", bg="#2563eb", fg="white", font=("Arial", 12, "bold"), bd=0, pady=18, cursor="hand2", command=self.load_pdf).pack(fill="x", padx=25, pady=40)
        
        tk.Label(sidebar, text="--- PRINT CONTROLS ---", **lbl_style).pack(pady=5)
        tk.Button(sidebar, text="🖨️ PRINT FRONT SIDE", bg="#059669", fg="white", font=("Arial", 11, "bold"), bd=0, pady=15, command=lambda: self.execute_print("front")).pack(fill="x", padx=25, pady=10)
        tk.Button(sidebar, text="🖨️ PRINT BACK SIDE", bg="#dc2626", fg="white", font=("Arial", 11, "bold"), bd=0, pady=15, command=lambda: self.execute_print("back")).pack(fill="x", padx=25, pady=10)

        # --- Preview Canvas (Right) ---
        display_area = tk.Frame(root, bg="#0f172a")
        display_area.pack(side="right", fill="both", expand=True)

        self.f_label = tk.Label(display_area, text="FRONT PREVIEW", bg="#1e293b", fg="#475569", font=("Arial", 14))
        self.f_label.pack(pady=20, padx=50, fill="both", expand=True)
        
        self.b_label = tk.Label(display_area, text="BACK PREVIEW", bg="#1e293b", fg="#475569", font=("Arial", 14))
        self.b_label.pack(pady=20, padx=50, fill="both", expand=True)

        self.img_f = None
        self.img_b = None

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path: return
        try:
            doc = fitz.open(path)
            if doc.is_encrypted:
                doc.authenticate(self.password.get())
            
            # High Resolution Rendering
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(6, 6))
            full = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # নিখুঁত ক্রপিং প্যারামিটার (ই-আধার লেআউট অনুযায়ী)
            # নিচের বাম পাশের অংশ (Back) এবং নিচের ডান পাশের অংশ (Front)
            self.img_f = full.crop((3260, 3200, 5950, 4900)).resize((1012, 638), Image.LANCZOS)
            self.img_b = full.crop((410, 3200, 3100, 4900)).resize((1012, 638), Image.LANCZOS)

            # প্রিভিউ আপডেট
            f_p = ImageTk.PhotoImage(self.img_f.resize((480, 302), Image.LANCZOS))
            b_p = ImageTk.PhotoImage(self.img_b.resize((480, 302), Image.LANCZOS))

            self.f_label.config(image=f_p, text="")
            self.f_label.image = f_p
            self.b_label.config(image=b_p, text="")
            self.b_label.image = b_p
            messagebox.showinfo("Sahaji Studio", "Aadhaar Card Loaded Successfully!")

        except Exception as e:
            messagebox.showerror("Error", "পাসওয়ার্ড ভুল অথবা ফাইলটি সঠিক নয়!")

    def execute_print(self, side):
        card = self.img_f if side == "front" else self.img_b
        if not card:
            messagebox.showwarning("Warning", "আগে আধার ফাইলটি লোড করুন!")
            return

        printer = self.printer_var.get()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer)
        hDC.StartDoc(f"Sahaji_{side}")
        hDC.StartPage()
        
        dib = ImageWin.Dib(card)
        # প্রিন্টিং পজিশন (Center on PVC Area)
        dib.draw(hDC.GetHandleOutput(), (120, 120, 1132, 758)) 
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiActionStudio(root)
    root.mainloop()
