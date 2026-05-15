import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageWin
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import win32print
import win32ui

class SahajiNetPointV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Sahaji Net Point - Pro PVC Studio")
        self.root.geometry("500x650")
        self.root.configure(bg="#2c3e50")

        # Branding
        tk.Label(root, text="SAHAJI NET POINT", font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=20)
        
        # Action Buttons Frame
        btn_frame = tk.Frame(root, bg="#2c3e50")
        btn_frame.pack(pady=10)

        self.add_button(btn_frame, "ADHAAR ACTION (1-CLICK)", "#e67e22", lambda: self.process_card("aadhaar"))
        self.add_button(btn_frame, "VOTER CARD ACTION", "#3498db", lambda: self.process_card("voter"))
        self.add_button(btn_frame, "PAN CARD ACTION", "#27ae60", lambda: self.process_card("pan"))
        self.add_button(btn_frame, "HEALTH/ABHA CARD", "#8e44ad", lambda: self.process_card("health"))

        # Status
        self.status = tk.Label(root, text="System Ready for Action", bg="#2c3e50", fg="#95a5a6", font=("Arial", 10))
        self.status.pack(side="bottom", pady=20)

    def add_button(self, frame, text, color, cmd):
        btn = tk.Button(frame, text=text, bg=color, fg="white", font=("Arial", 12, "bold"), 
                        width=30, pady=12, relief="flat", cursor="hand2", command=cmd)
        btn.pack(pady=8)

    def process_card(self, card_type):
        file_path = filedialog.askopenfilename(filetypes=[("PDF/Images", "*.pdf *.jpg *.png")])
        if not file_path: return
        
        self.status.config(text="Extracting and Optimizing...", fg="#f1c40f")
        self.root.update()

        try:
            # Load Document
            doc = fitz.open(file_path)
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(6, 6)) # High Res for Sharp Print
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # PVC standard size (approx. 3.375 x 2.125 inches)
            pvc_w, pvc_h = 1011, 638 

            # Precision Cropping (Based on Standard Indian PDF Layouts)
            if card_type == "aadhaar":
                front = img.crop((450, 3100, 3150, 4850)) # Aadhaar Bottom Left
                back = img.crop((3200, 3100, 5900, 4850)) # Aadhaar Bottom Right
            elif card_type == "voter":
                front = img.crop((500, 3200, 3300, 5000)) 
                back = img.crop((3400, 3200, 6200, 5000))
            else: # General for others
                front = img.crop((500, 500, 3500, 2500))
                back = img.crop((500, 2600, 3500, 4600))

            front = self.enhance(front.resize((pvc_w, pvc_h), Image.LANCZOS))
            back = self.enhance(back.resize((pvc_w, pvc_h), Image.LANCZOS))

            # Combine for one A4 page print view
            final_sheet = Image.new('RGB', (2480, 3508), (255, 255, 255))
            final_sheet.paste(front, (200, 200))
            final_sheet.paste(back, (200, 900))

            # Save and Ask for Print
            save_path = "temp_print.png"
            final_sheet.save(save_path, dpi=(300, 300))
            
            if messagebox.askyesno("Action Ready", "Card is ready for Sahaji Net Point. Send to Printer?"):
                self.print_image(save_path)
                self.status.config(text="Print Job Sent!", fg="#2ecc71")
            
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong: {e}")

    def enhance(self, img):
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Sharpness(img).enhance(1.5)
        return img

    def print_image(self, filename):
        printer_name = win32print.GetDefaultPrinter()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        bmp = Image.open(filename)
        
        hDC.StartDoc("Sahaji Print Job")
        hDC.StartPage()
        dib = ImageWin.Dib(bmp)
        dib.draw(hDC.GetHandleOutput(), (0, 0, 2480, 3508))
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

if __name__ == "__main__":
    root = tk.Tk()
    app = SahajiNetPointV2(root)
    root.mainloop()
