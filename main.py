import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageTk, ImageWin
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32print
import win32ui
import os

class SahajiActionPro:
    def __init__(self, root):
        self.root = root
        self.root.title("SAHAJI NET POINT - ADVANCED PVC STUDIO")
        self.root.geometry("1100x750")
        self.root.configure(bg="#0f172a")

        # --- Sidebar / Controls ---
        sidebar = tk.Frame(root, bg="#1e293b", width=320)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)

        # লোগো বা দোকানের নাম
        tk.Label(sidebar, text="SAHAJI ACTION", font=("Verdana", 20, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=30)

        # প্রিন্টার সেটিংস
        tk.Label(sidebar, text="--- SELECT PRINTER ---", bg="#1e293b", fg="#94a3b8", font=("Arial", 9, "bold")).pack(pady=(10,5))
        self.printers = [p[2] for p in win32print.EnumPrinters(2)]
        self.printer_var = tk.StringVar()
        self.p_combo = ttk.Combobox(sidebar, textvariable=self.printer_var, values=self.printers, state="readonly", width=35)
        self.p_combo.pack(pady=5, padx=20)
        if self.printers: self.p_combo.current(0)

        # পাসওয়ার্ড সেটিংস
        tk.Label(sidebar, text="--- PDF PASSWORD ---", bg="#1e293b", fg="#94a3b8", font=("Arial", 9, "bold")).pack(pady=(15,5))
        self.password = tk.StringVar(value="RITIC2000")
        tk.Entry(sidebar, textvariable=self.password, font=("Arial", 12), bg="#334155", fg="white", bd=0, justify="center").pack(fill="x", padx=40, pady=5)

        # ফাইল ওপেন বাটন
        tk.Button(sidebar, text="📂 OPEN ORIGINAL AADHAAR", bg="#2563eb", fg="white", font=("Arial", 11, "bold"), bd=0, pady=15, cursor="hand2", command=self.load_pdf).pack(fill="x", padx=25, pady=40)
        
        # প্রিন্ট বাটন সমূহ
        tk.Label(sidebar, text="--- PRINT OPERATIONS ---", bg="#1e293b", fg="#94a3b8", font=("Arial", 9, "bold")).pack(pady=5)
        tk.Button(sidebar, text="🖨️ PRINT FRONT SIDE", bg="#059669", fg="white", font=("Arial", 11, "bold"), bd=0, pady=12, command=lambda: self.print_card("front")).pack(fill="x", padx=25, pady=8)
        tk.Button(sidebar, text="🖨️ PRINT BACK SIDE", bg="#dc2626", fg="white", font=("Arial", 11, "bold"), bd=0, pady=12, command=lambda: self.print_card("back")).pack(fill="x", padx=25, pady=8)

        # --- Preview Canvas (Right Side) ---
        preview_area = tk.Frame(root, bg="#0f172a")
        preview_area.pack(side="right", fill="both", expand=True)

        self.f_label = tk.Label(preview_area, text="[ FRONT PREVIEW ]", bg="#1e293b", fg="#475569", font=("Arial", 14))
        self.f_label.pack(pady=20, padx=40, fill="both", expand=True)
        
        self.b_label = tk.Label(preview_area, text="[ BACK PREVIEW ]", bg="#1e293b", fg="#475569", font=("Arial", 14))
        self.b_label.pack(pady=20, padx=40, fill="both", expand=True)

        self.img_f = None
        self.img_b = None

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path: return
        try:
            doc = fitz.open(path)
            if doc.is_encrypted:
                doc.authenticate(self.password.get())
            
            # হাই-রেজোলিউশন রেন্ডারিং
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(6, 6))
            full = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # আধার কার্ডের নিচের অংশের নিখুঁত ক্রপিং (PVC Standard)
            # Coordinates optimized for Original E-Aadhaar PDF
            self.img_f = full.crop((3260, 3190, 5950, 4880)).resize((1012, 638), Image.LANCZOS)
            self.img_b = full.crop((410, 3190, 3100, 4880)).resize((1012, 638), Image.LANCZOS)

            # ছবি স্ক্রিনে দেখানোর জন্য
            f_prev = ImageTk.PhotoImage(self.img_f.resize((450, 284), Image.LANCZOS))
            b_prev = ImageTk.PhotoImage(self.img_b.resize((450, 284), Image.LANCZOS))

            self.f_label.config(image=f_prev, text="")
            self.f_label.image = f_prev
            self.b_label.config(image=b_prev, text="")
            self.b_label.image = b_prev
            messagebox.showinfo("Sahaji Studio", "Card Loaded! Select side to print.")

        except Exception as e:
            messagebox.showerror("Error", "ফাইলটি খুলতে সমস্যা হচ্ছে। পাসওয়ার্ড সঠিক কি না দেখুন।")

    def print_card(self, side):
        card_to_print = self.img_f if side == "front" else self.img_b
        if not card_to_print:
            messagebox.showwarning("Warning", "আগে একটি আধার ফাইল লোড করুন!")
            return

        printer_name = self.printer_var.get()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        hDC.StartDoc(f"Sahaji_Print_{side}")
        hDC.StartPage()
        
        dib = ImageWin.Dib(card_to_print)
        # প্রিন্টারের ট্রে-তে কার্ড পজিশন অ্যাডজাস্টমেন্ট
        dib.draw(hDC.GetHandleOutput(), (120, 120, 1132, 758)) 
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiActionPro(root)
    root.mainloop()
