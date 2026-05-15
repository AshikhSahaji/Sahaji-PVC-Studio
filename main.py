import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageTk, ImageWin
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32print
import win32ui
import os

class SahajiActionStudioV3:
    def __init__(self, root):
        self.root = root
        self.root.title("Sahaji Net Point - All-in-One PVC Studio (v2.0)")
        self.root.geometry("1100x750")
        self.root.configure(bg="#121212")

        # --- Sidebar Controls ---
        sidebar = tk.Frame(root, bg="#1e1e1e", width=300)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)

        # Branding
        tk.Label(sidebar, text="SAHAJI STUDIO", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="#00cec9").pack(pady=20)

        # Printer Section
        tk.Label(sidebar, text="--- PRINTER SETUP ---", bg="#1e1e1e", fg="#636e72", font=("Arial", 8, "bold")).pack()
        self.printers = [p[2] for p in win32print.EnumPrinters(2)]
        self.printer_var = tk.StringVar()
        self.p_combo = ttk.Combobox(sidebar, textvariable=self.printer_var, values=self.printers, state="readonly", width=35)
        self.p_combo.pack(pady=5, padx=20)
        if self.printers: self.p_combo.current(0)

        # Action Buttons
        btn_style = {"font": ("Arial", 10, "bold"), "bd": 0, "pady": 12, "cursor": "hand2", "fg": "white"}
        
        tk.Button(sidebar, text="📂 OPEN AADHAAR (AUTO)", bg="#0984e3", command=lambda: self.process_pdf("aadhaar"), **btn_style).pack(fill="x", padx=25, pady=20)
        
        tk.Label(sidebar, text="--- PRINT ACTIONS ---", bg="#1e1e1e", fg="#636e72", font=("Arial", 8, "bold")).pack()
        tk.Button(sidebar, text="🖨️ PRINT FRONT SIDE", bg="#00b894", command=lambda: self.print_card("front"), **btn_style).pack(fill="x", padx=25, pady=8)
        tk.Button(sidebar, text="🖨️ PRINT BACK SIDE", bg="#d63031", command=lambda: self.print_card("back"), **btn_style).pack(fill="x", padx=25, pady=8)

        # --- Preview Panel ---
        preview_pane = tk.Frame(root, bg="#0f0f0f")
        preview_pane.pack(side="right", fill="both", expand=True)

        self.f_preview = tk.Label(preview_pane, text="[ FRONT SIDE PREVIEW ]", bg="#1a1a1a", fg="#444", font=("Arial", 14))
        self.f_preview.pack(pady=15, padx=20, fill="both", expand=True)
        
        self.b_preview = tk.Label(preview_pane, text="[ BACK SIDE PREVIEW ]", bg="#1a1a1a", fg="#444", font=("Arial", 14))
        self.b_preview.pack(pady=15, padx=20, fill="both", expand=True)

        self.front_data = None
        self.back_data = None

    def process_pdf(self, mode):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path: return
        try:
            doc = fitz.open(path)
            if doc.is_encrypted:
                doc.authenticate("RITIC2000") # আপনার দেওয়া পাসওয়ার্ড
            
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(6, 6))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Dizi Print স্টাইল ক্রপিং (অরিজিনাল আধার লেআউট অনুযায়ী)
            self.front_data = img.crop((3260, 3190, 5950, 4880)).resize((1012, 638), Image.LANCZOS)
            self.back_data = img.crop((410, 3190, 3100, 4880)).resize((1012, 638), Image.LANCZOS)

            # প্রিভিউ দেখানো
            f_img = ImageTk.PhotoImage(self.front_data.resize((480, 302), Image.LANCZOS))
            b_img = ImageTk.PhotoImage(self.back_data.resize((480, 302), Image.LANCZOS))

            self.f_preview.config(image=f_img, text="")
            self.f_preview.image = f_img
            self.b_preview.config(image=b_img, text="")
            self.b_preview.image = b_img
            messagebox.showinfo("Sahaji Studio", "Card is ready for printing!")

        except Exception as e:
            messagebox.showerror("Error", "ফাইলটি ওপেন করা সম্ভব হয়নি। পাসওয়ার্ড বা ফাইল চেক করুন।")

    def print_card(self, side):
        img_to_print = self.front_data if side == "front" else self.back_data
        if not img_to_print:
            messagebox.showwarning("Warning", "আগে একটি পিডিএফ ফাইল লোড করুন!")
            return

        p_name = self.printer_var.get()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(p_name)
        hDC.StartDoc(f"Sahaji_Print_{side}")
        hDC.StartPage()
        
        dib = ImageWin.Dib(img_to_print)
        # প্রিন্টারের কাগজে সঠিক পজিশনে কার্ড বসানো
        dib.draw(hDC.GetHandleOutput(), (120, 120, 1132, 758)) 
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiActionStudioV3(root)
    root.mainloop()
