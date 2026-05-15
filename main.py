import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageTk, ImageWin
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32print
import win32ui
import os

class SahajiActionProV4:
    def __init__(self, root):
        self.root = root
        self.root.title("Sahaji PVC Studio v4.0 - Action Driven Studio")
        self.root.geometry("1200x800")
        self.root.configure(bg="#111827")

        # --- Sidebar / Action Controls ---
        sidebar = tk.Frame(root, bg="#1f2937", width=350)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(sidebar, text="SAHAJI STUDIO", font=("Arial", 20, "bold"), bg="#1f2937", fg="#10b981").pack(pady=20)

        # কার্ড সিলেকশন মেনু
        tk.Label(sidebar, text="CHOOSE ACTION TEMPLATE", bg="#1f2937", fg="#9ca3af", font=("Arial", 9, "bold")).pack(pady=(10,5))
        self.action_type = tk.StringVar(value="Aadhaar Card (Color)")
        action_list = ["Aadhaar Card (White)", "Aadhaar Card (Color)", "Voter Card (New)", "PAN Card (NSDL/UTI)", "Ayushman Card", "Health / ABHA Card"]
        self.action_menu = ttk.Combobox(sidebar, textvariable=self.action_type, values=action_list, state="readonly", width=35)
        self.action_menu.pack(pady=5, padx=20)

        # প্রিন্টার সেটিংস
        tk.Label(sidebar, text="SELECT PRINTER", bg="#1f2937", fg="#9ca3af", font=("Arial", 9, "bold")).pack(pady=(15,5))
        self.printers = [p[2] for p in win32print.EnumPrinters(2)]
        self.p_var = tk.StringVar()
        self.p_combo = ttk.Combobox(sidebar, textvariable=self.p_var, values=self.printers, state="readonly", width=35)
        self.p_combo.pack(pady=5, padx=20)
        if self.printers: self.p_combo.current(0)

        # পাসওয়ার্ড ইনপুট
        tk.Label(sidebar, text="PDF PASSWORD (if any)", bg="#1f2937", fg="#9ca3af", font=("Arial", 9, "bold")).pack(pady=(15,5))
        self.password = tk.StringVar(value="RITI2000")
        tk.Entry(sidebar, textvariable=self.password, font=("Arial", 12), bg="#374151", fg="white", bd=0, justify="center").pack(fill="x", padx=40, pady=5)

        # মেইন বাটন
        tk.Button(sidebar, text="📂 LOAD & RUN ACTION", bg="#10b981", fg="white", font=("Arial", 12, "bold"), bd=0, pady=15, command=self.run_card_action).pack(fill="x", padx=25, pady=35)
        
        tk.Label(sidebar, text="PRINT CONTROLS", bg="#1f2937", fg="#9ca3af", font=("Arial", 9, "bold")).pack(pady=5)
        tk.Button(sidebar, text="PRINT FRONT SIDE", bg="#3b82f6", fg="white", font=("Arial", 11, "bold"), bd=0, pady=12, command=lambda: self.print_action("front")).pack(fill="x", padx=25, pady=8)
        tk.Button(sidebar, text="PRINT BACK SIDE", bg="#ef4444", fg="white", font=("Arial", 11, "bold"), bd=0, pady=12, command=lambda: self.print_action("back")).pack(fill="x", padx=25, pady=8)

        # --- Display Panel ---
        display = tk.Frame(root, bg="#111827")
        display.pack(side="right", fill="both", expand=True)

        self.f_preview = tk.Label(display, text="FRONT PREVIEW", bg="#1f2937", fg="#4b5563", font=("Arial", 16))
        self.f_preview.pack(pady=20, padx=40, fill="both", expand=True)
        
        self.b_preview = tk.Label(display, text="BACK PREVIEW", bg="#1f2937", fg="#4b5563", font=("Arial", 16))
        self.b_preview.pack(pady=20, padx=40, fill="both", expand=True)

        self.img_f = None
        self.img_b = None

    def run_card_action(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF/Images", "*.pdf *.jpg *.png")])
        if not file_path: return
        try:
            doc = fitz.open(file_path)
            if doc.is_encrypted: doc.authenticate(self.password.get())
            
            # Action ফাইল অনুযায়ী হাই-রেজোলিউশন (300 DPI) সেটআপ
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(6, 6))
            full = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            pvc_w, pvc_h = 1012, 638 
            selected = self.action_type.get()

            # ফটোশপ অ্যাকশন ফাইল অনুযায়ী ক্রপিং কোঅর্ডিনেট সেটআপ
            if "Aadhaar" in selected:
                # আপনার অ্যাকশন ফাইলের মতোই ফ্রন্ট এবং ব্যাক আলাদা করা
                self.img_f = full.crop((3260, 3190, 5950, 4880)).resize((pvc_w, pvc_h), Image.LANCZOS)
                self.img_b = full.crop((410, 3190, 3100, 4880)).resize((pvc_w, pvc_h), Image.LANCZOS)
            elif "Voter" in selected:
                self.img_f = full.crop((500, 3050, 3300, 4850)).resize((pvc_w, pvc_h), Image.LANCZOS)
                self.img_b = full.crop((3350, 3050, 6150, 4850)).resize((pvc_w, pvc_h), Image.LANCZOS)
            else: # প্যান বা হেলথ কার্ডের জন্য ডিফল্ট অ্যাকশন
                self.img_f = full.crop((500, 500, 3500, 2500)).resize((pvc_w, pvc_h), Image.LANCZOS)
                self.img_b = full.crop((500, 2600, 3500, 4600)).resize((pvc_w, pvc_h), Image.LANCZOS)

            # অটো-এনহ্যান্সমেন্ট (অ্যাকশন ফাইলের Levels কমান্ডের মতো)
            self.img_f = self.apply_action_effects(self.img_f)
            self.img_b = self.apply_action_effects(self.img_b)

            # প্রিভিউ আপডেট
            f_p = ImageTk.PhotoImage(self.img_f.resize((480, 302), Image.LANCZOS))
            b_p = ImageTk.PhotoImage(self.img_b.resize((480, 302), Image.LANCZOS))
            self.f_preview.config(image=f_p, text="")
            self.f_preview.image = f_p
            self.b_preview.config(image=b_p, text="")
            self.b_preview.image = b_p

        except Exception as e:
            messagebox.showerror("Error", f"Action execution failed: {e}")

    def apply_action_effects(self, img):
        # অ্যাকশন ফাইলের 'Levels' এবং 'Contrast' কমান্ড নকল করা
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Sharpness(img).enhance(1.5)
        img = ImageEnhance.Brightness(img).enhance(1.05)
        return img

    def print_action(self, side):
        card = self.img_f if side == "front" else self.img_b
        if not card: return
        
        p_name = self.p_var.get()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(p_name)
        hDC.StartDoc(f"Sahaji_Action_{side}")
        hDC.StartPage()
        
        dib = ImageWin.Dib(card)
        # আপনার প্রিন্টার ট্রের পজিশন অনুযায়ী মার্জিন সেটআপ
        dib.draw(hDC.GetHandleOutput(), (120, 120, 1132, 758)) 
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiActionProV4(root)
    root.mainloop()
