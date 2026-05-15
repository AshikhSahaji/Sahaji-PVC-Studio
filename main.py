import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageWin
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import win32print
import win32ui

class SahajiProStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Sahaji Net Point - Advanced PVC Studio")
        self.root.geometry("550x700")
        self.root.configure(bg="#1e272e")

        # Branding
        tk.Label(root, text="SAHAJI NET POINT", font=("Arial", 26, "bold"), bg="#1e272e", fg="#0fbcf9").pack(pady=20)
        
        # Printer Selection Frame
        p_frame = tk.LabelFrame(root, text=" Select Your Printer ", bg="#1e272e", fg="white", font=("Arial", 10))
        p_frame.pack(pady=10, padx=20, fill="x")
        
        self.printer_list = [p[2] for p in win32print.EnumPrinters(2)]
        self.selected_printer = tk.StringVar()
        self.printer_combo = ttk.Combobox(p_frame, textvariable=self.selected_printer, values=self.printer_list, state="readonly", width=40)
        self.printer_combo.pack(pady=10, padx=10)
        if self.printer_list: self.printer_combo.current(0)

        # Action Buttons
        btn_style = {"font": ("Arial", 12, "bold"), "width": 30, "pady": 12, "fg": "white", "cursor": "hand2"}
        
        tk.Button(root, text="ADHAAR (1-CLICK ACTION)", bg="#e67e22", command=lambda: self.process("aadhaar"), **btn_style).pack(pady=10)
        tk.Button(root, text="VOTER / PAN ACTION", bg="#05c46b", command=lambda: self.process("voter"), **btn_style).pack(pady=10)
        tk.Button(root, text="HEALTH / ABHA ACTION", bg="#3c40c6", command=lambda: self.process("health"), **btn_style).pack(pady=10)

        self.status = tk.Label(root, text="Select Printer & Card Type to Start", bg="#1e272e", fg="#d2dae2")
        self.status.pack(side="bottom", pady=20)

    def process(self, mode):
        file = filedialog.askopenfilename(filetypes=[("PDF/Images", "*.pdf *.jpg *.png")])
        if not file: return
        
        self.status.config(text="Extracting High Quality Images...", fg="#ffdd59")
        self.root.update()

        try:
            doc = fitz.open(file)
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(6, 6))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pvc = (1012, 638) # Standard PVC Size

            if mode == "aadhaar":
                f, b = img.crop((450, 2900, 3100, 4700)), img.crop((3200, 2900, 5900, 4700))
            elif mode == "voter":
                f, b = img.crop((500, 3200, 3300, 5000)), img.crop((3400, 3200, 6200, 5000))
            else:
                f, b = img.crop((500, 500, 3500, 2500)), img.crop((500, 2600, 3500, 4600))

            f, b = self.clean(f.resize(pvc, Image.LANCZOS)), self.clean(b.resize(pvc, Image.LANCZOS))
            
            # Print Choice Dialog
            choice = messagebox.askyesnocancel("Print Option", "YES: Print FRONT Side\nNO: Print BACK Side\nCancel: Just Save")
            
            if choice is True: # Front
                self.direct_print(f, "Front_Side")
            elif choice is False: # Back
                self.direct_print(b, "Back_Side")
            else:
                save_dir = filedialog.askdirectory()
                if save_dir:
                    f.save(os.path.join(save_dir, "Sahaji_Front.png"))
                    b.save(os.path.join(save_dir, "Sahaji_Back.png"))
                    messagebox.showinfo("Success", "Images Saved Successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clean(self, img):
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.4)
        return img

    def direct_print(self, img, title):
        printer = self.selected_printer.get()
        if not printer: 
            messagebox.showwarning("Warning", "Please select a printer first!")
            return

        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer)
        hDC.StartDoc(f"Sahaji_{title}")
        hDC.StartPage()
        
        # Center card on the page
        dib = ImageWin.Dib(img)
        dib.draw(hDC.GetHandleOutput(), (100, 100, 1112, 738)) 
        
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
        self.status.config(text=f"{title} Sent to Printer", fg="#2ecc71")

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiProStudio(root)
    root.mainloop()
