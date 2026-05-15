import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32print
import win32ui
import win32con

class SahajiPrintStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Sahaji Net Point - PVC Print Studio v3.0")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e1e")

        # Navbar / Header
        header = tk.Frame(root, bg="#2d3436", height=60)
        header.pack(fill="x")
        tk.Label(header, text="SAHAJI NET POINT STUDIO", font=("Arial", 18, "bold"), bg="#2d3436", fg="#00cec9").pack(side="left", padx=20, pady=10)

        # Main Layout (Left: Controls, Right: Preview)
        main_frame = tk.Frame(root, bg="#1e1e1e")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Sidebar / Controls ---
        sidebar = tk.Frame(main_frame, bg="#2d3436", width=250)
        sidebar.pack(side="left", fill="y", padx=5)

        tk.Label(sidebar, text="SETTINGS", font=("Arial", 12, "bold"), bg="#2d3436", fg="white").pack(pady=10)

        # Password Entry
        tk.Label(sidebar, text="PDF Password:", bg="#2d3436", fg="#dfe6e9").pack(anchor="w", padx=10)
        self.password = tk.StringVar(value="RITIC2000")
        tk.Entry(sidebar, textvariable=self.password, font=("Arial", 11), bg="#3b3b3b", fg="white", insertbackground="white").pack(fill="x", padx=10, pady=5)

        # Printer List
        tk.Label(sidebar, text="Select Printer:", bg="#2d3436", fg="#dfe6e9").pack(anchor="w", padx=10, pady=(10,0))
        self.printers = [p[2] for p in win32print.EnumPrinters(2)]
        self.printer_var = tk.StringVar()
        self.p_combo = ttk.Combobox(sidebar, textvariable=self.printer_var, values=self.printers, state="readonly")
        self.p_combo.pack(fill="x", padx=10, pady=5)
        if self.printers: self.p_combo.current(0)

        # Print Mode
        tk.Label(sidebar, text="Print Selection:", bg="#2d3436", fg="#dfe6e9").pack(anchor="w", padx=10, pady=(10,0))
        self.print_mode = tk.StringVar(value="Front Only")
        mode_menu = ttk.Combobox(sidebar, textvariable=self.print_mode, values=["Front Only", "Back Only", "Both Sides"], state="readonly")
        mode_menu.pack(fill="x", padx=10, pady=5)

        # Action Buttons
        tk.Button(sidebar, text="CHOOSE PDF FILE", bg="#0984e3", fg="white", font=("Arial", 10, "bold"), pady=10, command=self.load_pdf).pack(fill="x", padx=10, pady=20)
        tk.Button(sidebar, text="PRINT NOW 🖨️", bg="#00b894", fg="white", font=("Arial", 12, "bold"), pady=15, command=self.execute_print).pack(fill="x", padx=10, pady=10)

        # --- Preview Area (Right) ---
        self.preview_frame = tk.Frame(main_frame, bg="#121212")
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.front_label = tk.Label(self.preview_frame, text="FRONT PREVIEW", bg="#121212", fg="#636e72")
        self.front_label.pack(pady=20)
        self.back_label = tk.Label(self.preview_frame, text="BACK PREVIEW", bg="#121212", fg="#636e72")
        self.back_label.pack(pady=20)

        self.front_img = None
        self.back_img = None

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path: return

        try:
            doc = fitz.open(file_path)
            if doc.is_encrypted:
                doc.authenticate(self.password.get())
            
            page = doc[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(5, 5))
            full_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # High-Precision Cropping for Aadhaar
            # coordinates are calibrated for standard UIDAI Layout
            self.front_img = full_img.crop((3250, 3180, 5950, 4880)).resize((1012, 638), Image.LANCZOS)
            self.back_img = full_img.crop((400, 3180, 3100, 4880)).resize((1012, 638), Image.LANCZOS)

            # UI Preview Scaling
            f_prev = ImageTk.PhotoImage(self.front_img.resize((400, 252), Image.LANCZOS))
            b_prev = ImageTk.PhotoImage(self.back_img.resize((400, 252), Image.LANCZOS))

            self.front_label.config(image=f_prev, text="")
            self.front_label.image = f_prev
            self.back_label.config(image=b_prev, text="")
            self.back_label.image = b_prev

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")

    def execute_print(self):
        if not self.front_img:
            messagebox.showwarning("Empty", "Please load a PDF first!")
            return

        mode = self.print_mode.get()
        if mode == "Front Only":
            self.send_to_printer(self.front_img, "Front")
        elif mode == "Back Only":
            self.send_to_printer(self.back_img, "Back")
        else:
            self.send_to_printer(self.front_img, "Front")
            messagebox.showinfo("Next", "Front side done. Flip your PVC card and press OK to print Back side.")
            self.send_to_printer(self.back_img, "Back")

    def send_to_printer(self, pil_img, side_name):
        printer_name = self.printer_var.get()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        
        # Adjusting print positioning
        hDC.StartDoc(f"Sahaji_Print_{side_name}")
        hDC.StartPage()
        
        from PIL import ImageWin
        dib = ImageWin.Dib(pil_img)
        # Positioned roughly at the center of the PVC card area on printer
        dib.draw(hDC.GetHandleOutput(), (100, 100, 1112, 738)) 
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiPrintStudio(root)
    root.mainloop()
