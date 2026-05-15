import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageTk, ImageWin
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32print
import win32ui
import os

class SahajiPVCStudioV6:
    def __init__(self, root):
        self.root = root
        self.root.title("SAHAJI PVC STUDIO v6.0 - Epson Easy Card Action")
        self.root.geometry("1250x850")
        self.root.configure(bg="#0f172a")

        # --- Sidebar Controls ---
        sidebar = tk.Frame(root, bg="#1e293b", width=350)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(sidebar, text="SAHAJI ACTION STUDIO", font=("Segoe UI", 18, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=25)

        # কার্ড টাইপ মেনু
        tk.Label(sidebar, text="SELECT SMART ACTION", bg="#1e293b", fg="#94a3b8", font=("Arial", 9, "bold")).pack(pady=(10, 5))
        self.card_action = tk.StringVar(value="Aadhaar Card (Color)")
        actions = ["Aadhaar Card (Color)", "Voter Card (New PVC)", "PAN Card Action", "Health/Ayushman Action"]
        self.action_menu = ttk.Combobox(sidebar, textvariable=self.card_action, values=actions, state="readonly")
        self.action_menu.pack(fill="x", padx=30, pady=5)

        # প্রিন্টার সেটিংস
        tk.Label(sidebar, text="PRINTER PERFORMANCE SETTINGS", bg="#1e293b", fg="#94a3b8", font=("Arial", 9, "bold")).pack(pady=(20, 5))
        self.printers = [p[2] for p in win32print.EnumPrinters(2)]
        self.p_var = tk.StringVar()
        self.p_combo = ttk.Combobox(sidebar, textvariable=self.p_var, values=self.printers, state="readonly")
        self.p_combo.pack(fill="x", padx=30, pady=5)
        if self.printers: self.p_combo.current(0)

        # মেইন বাটন
        tk.Button(sidebar, text="📂 LOAD & RUN ACTION", bg="#2563eb", fg="white", font=("Arial", 11, "bold"), bd=0, pady=18, command=self.execute_action).pack(fill="x", padx=30, pady=40)

        # প্রিন্ট বাটন
        tk.Button(sidebar, text="🖨️ PRINT FRONT", bg="#059669", fg="white", font=("Arial", 11, "bold"), bd=0, pady=12, command=lambda: self.send_to_printer("front")).pack(fill="x", padx=30, pady=8)
        tk.Button(sidebar, text="🖨️ PRINT BACK", bg="#dc2626", fg="white", font=("Arial", 11, "bold"), bd=0, pady=12, command=lambda: self.send_to_printer("back")).pack(fill="x", padx=30, pady=8)

        # --- Preview Pane ---
        display = tk.Frame(root, bg="#0f172a")
        display.pack(side="right", fill="both", expand=True)

        self.f_view = tk.Label(display, text="FRONT PREVIEW", bg="#1e293b", fg="#475569", font=("Arial", 14))
        self.f_view.pack(pady=20, padx=40, fill="both", expand=True)
        
        self.b_view = tk.Label(display, text="BACK PREVIEW", bg="#1e293b", fg="#475569", font=("Arial", 14))
        self.b_view.pack(pady=20, padx=40, fill="both", expand=True)

        self.front_card = None
        self.back_card = None

    def execute_action(self):
        file_path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.jpg *.png")])
        if not file_path: return
        try:
            doc = fitz.open(file_path)
            # ভোটার কার্ড বা আধারের জন্য পাসওয়ার্ড চেক
            if doc.is_encrypted: doc.authenticate("RITI2000")
            
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(6, 6))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            pvc_w, pvc_h = 1012, 638 
            mode = self.card_action.get()

            # আপনার EPSON ACTION l8050 অনুযায়ী ক্রপিং রুলস
            if "Voter" in mode:
                # নতুন ভোটার কার্ডের সামনের ও পেছনের অংশ 
                self.front_card = img.crop((400, 300, 3200, 2050)).resize((pvc_w, pvc_h), Image.LANCZOS)
                self.back_card = img.crop((400, 2150, 3200, 3900)).resize((pvc_w, pvc_h), Image.LANCZOS)
            elif "Aadhaar" in mode:
                self.front_card = img.crop((3260, 3190, 5950, 4880)).resize((pvc_w, pvc_h), Image.LANCZOS)
                self.back_card = img.crop((410, 3190, 3100, 4880)).resize((pvc_w, pvc_h), Image.LANCZOS)
            
            # Action Levels  প্রয়োগ করা
            self.front_card = self.apply_enhance(self.front_card)
            self.back_card = self.apply_enhance(self.back_card)

            # প্রিভিউ আপডেট
            f_img = ImageTk.PhotoImage(self.front_card.resize((500, 315), Image.LANCZOS))
            b_img = ImageTk.PhotoImage(self.back_card.resize((500, 315), Image.LANCZOS))
            self.f_view.config(image=f_img, text="")
            self.f_view.image = f_img
            self.b_view.config(image=b_img, text="")
            self.b_view.image = b_img

        except Exception as e:
            messagebox.showerror("Error", f"Action failed: {e}")

    def apply_enhance(self, img):
        # অ্যাকশন ফাইলের Levels এবং Contrast এর মতো এনহ্যান্সমেন্ট [cite: 839, 870]
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Sharpness(img).enhance(1.4)
        return img

    def send_to_printer(self, side):
        target = self.front_card if side == "front" else self.back_card
        if not target: return
        
        p_name = self.p_var.get()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(p_name)
        hDC.StartDoc(f"Sahaji_Action_{side}")
        hDC.StartPage()
        
        dib = ImageWin.Dib(target)
        # Epson Easy Card Tray এর জন্য নির্দিষ্ট মার্জিন 
        dib.draw(hDC.GetHandleOutput(), (120, 120, 1132, 758)) 
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiPVCStudioV6(root)
    root.mainloop()
