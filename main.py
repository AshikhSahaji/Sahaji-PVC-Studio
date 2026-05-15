import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageTk, ImageWin
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32print
import win32ui
import os

class SahajiPVCStudioPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Sahaji PVC Studio v4.0 - All-in-One Indian Card Action")
        self.root.geometry("1200x800")
        self.root.configure(bg="#111827")

        # --- Navbar ---
        navbar = tk.Frame(root, bg="#1f2937", height=50)
        navbar.pack(fill="x")
        tk.Label(navbar, text="SAHAJI PVC STUDIO v4.0", font=("Verdana", 15, "bold"), bg="#1f2937", fg="#10b981").pack(side="left", padx=20)

        # --- Sidebar ---
        sidebar = tk.Frame(root, bg="#1f2937", width=300)
        sidebar.pack(side="left", fill="y", padx=2, pady=2)

        # Card Type Selection (যেমন ভিডিওতে ছিল)
        tk.Label(sidebar, text="SELECT CARD TYPE", bg="#1f2937", fg="#9ca3af", font=("Arial", 9, "bold")).pack(pady=(20,5))
        self.card_type = tk.StringVar(value="White Aadhaar Card")
        card_menu = ttk.Combobox(sidebar, textvariable=self.card_type, values=["White Aadhaar Card", "Voter Card", "PAN Card", "Health / ABHA Card", "Ration Card"], state="readonly")
        card_menu.pack(fill="x", padx=20, pady=5)

        # Password Access
        tk.Label(sidebar, text="PDF PASSWORD", bg="#1f2937", fg="#9ca3af", font=("Arial", 9, "bold")).pack(pady=(15,5))
        self.password = tk.StringVar(value="RITI2000")
        tk.Entry(sidebar, textvariable=self.password, font=("Arial", 12), bg="#374151", fg="white", bd=0, justify="center").pack(fill="x", padx=20, pady=5)

        # Printing Performance/Setup
        tk.Label(sidebar, text="--- PRINT SETTINGS ---", bg="#1f2937", fg="#9ca3af", font=("Arial", 9, "bold")).pack(pady=(20,5))
        self.printers = [p[2] for p in win32print.EnumPrinters(2)]
        self.p_var = tk.StringVar()
        self.p_combo = ttk.Combobox(sidebar, textvariable=self.p_var, values=self.printers, state="readonly")
        self.p_combo.pack(fill="x", padx=20, pady=5)
        if self.printers: self.p_combo.current(0)

        # Action Buttons
        tk.Button(sidebar, text="SELECT CARD FILE", bg="#10b981", fg="white", font=("Arial", 11, "bold"), bd=0, pady=15, cursor="hand2", command=self.open_action).pack(fill="x", padx=20, pady=30)
        
        tk.Button(sidebar, text="PRINT FRONT SIDE", bg="#3b82f6", fg="white", font=("Arial", 11, "bold"), bd=0, pady=10, command=lambda: self.print_job("front")).pack(fill="x", padx=20, pady=5)
        tk.Button(sidebar, text="PRINT BACK SIDE", bg="#ef4444", fg="white", font=("Arial", 11, "bold"), bd=0, pady=10, command=lambda: self.print_job("back")).pack(fill="x", padx=20, pady=5)

        # --- Preview Canvas (The 'Ready for Output' Area) ---
        self.preview_area = tk.Frame(root, bg="#111827")
        self.preview_area.pack(side="right", fill="both", expand=True)

        self.f_label = tk.Label(self.preview_area, text="[ FRONT PREVIEW ]", bg="#1f2937", fg="#4b5563", font=("Arial", 14))
        self.f_label.pack(pady=20, padx=50, fill="both", expand=True)
        
        self.b_label = tk.Label(self.preview_area, text="[ BACK PREVIEW ]", bg="#1f2937", fg="#4b5563", font=("Arial", 14))
        self.b_label.pack(pady=20, padx=50, fill="both", expand=True)

        self.front_img = None
        self.back_img = None

    def open_action(self):
        file = filedialog.askopenfilename(filetypes=[("Card Files", "*.pdf *.jpg *.png")])
        if not file: return
        try:
            doc = fitz.open(file)
            if doc.is_encrypted: doc.authenticate(self.password.get())
            
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(6, 6))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # PVC Card Size Calibration (3.375 x 2.125 inches at 300 DPI)
            pvc_w, pvc_h = 1012, 638 
            
            # Action Mapping (ফটোশপ একশনের মতো কার্ড অনুযায়ী ক্রপিং)
            ctype = self.card_type.get()
            if "Aadhaar" in ctype:
                self.front_img = img.crop((3260, 3190, 5950, 4880)).resize((pvc_w, pvc_h), Image.LANCZOS)
                self.back_img = img.crop((410, 3190, 3100, 4880)).resize((pvc_w, pvc_h), Image.LANCZOS)
            elif "Voter" in ctype:
                self.front_img = img.crop((500, 3000, 3300, 4800)).resize((pvc_w, pvc_h), Image.LANCZOS)
                self.back_img = img.crop((3400, 3000, 6200, 4800)).resize((pvc_w, pvc_h), Image.LANCZOS)
            else: # General Auto-Action
                self.front_img = img.crop((500, 500, 3500, 2500)).resize((pvc_w, pvc_h), Image.LANCZOS)
                self.back_img = img.crop((500, 2600, 3500, 4600)).resize((pvc_w, pvc_h), Image.LANCZOS)

            # Update Previews
            f_p = ImageTk.PhotoImage(self.front_img.resize((500, 315), Image.LANCZOS))
            b_p = ImageTk.PhotoImage(self.back_img.resize((500, 315), Image.LANCZOS))
            self.f_label.config(image=f_p, text="")
            self.f_label.image = f_p
            self.b_label.config(image=b_p, text="")
            self.b_label.image = b_p

        except Exception as e:
            messagebox.showerror("Error", f"Could not process card: {e}")

    def print_job(self, side):
        img = self.front_img if side == "front" else self.back_img
        if not img: return
        
        printer = self.p_var.get()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer)
        hDC.StartDoc(f"Sahaji_PVC_{side}")
        hDC.StartPage()
        
        dib = ImageWin.Dib(img)
        # Position for PVC Tray / Sheet
        dib.draw(hDC.GetHandleOutput(), (120, 120, 1132, 758)) 
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiPVCStudioPro(root)
    root.mainloop()
