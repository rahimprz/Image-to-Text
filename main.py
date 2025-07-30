import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Text, Label, Button, Frame
from PIL import Image, ImageTk, ImageDraw
import pytesseract
import os

# Set Tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Image OCR with Bounding Boxes")
        self.root.geometry("1000x750")
        self.root.configure(bg="#1e1e1e")

        Label(root, text="Image to Text OCR", bg="#1e1e1e", fg="white",
              font=("Helvetica", 18, "bold")).pack(pady=10)

        control_frame = Frame(root, bg="#1e1e1e")
        control_frame.pack(pady=10)

        Button(control_frame, text="Upload Image", command=self.upload_image,
               bg="#3a3a3a", fg="white", font=("Arial", 11), width=15).grid(row=0, column=0, padx=10)

        Button(control_frame, text="Clear", command=self.clear_content,
               bg="#444", fg="white", font=("Arial", 11), width=10).grid(row=0, column=1, padx=10)

        Button(control_frame, text="Save Text", command=self.save_text,
               bg="#2e8b57", fg="white", font=("Arial", 11), width=12).grid(row=0, column=2, padx=10)

        # Canvas for image with bounding boxes
        self.canvas = tk.Canvas(root, bg="#1e1e1e", width=500, height=400, highlightthickness=0)
        self.canvas.pack(pady=10)

        # Text output
        Label(root, text="Extracted Text:", bg="#1e1e1e", fg="white",
              font=("Arial", 12, "bold")).pack()

        self.text_box = Text(root, wrap="word", height=10, font=("Consolas", 11),
                             bg="#282828", fg="white", insertbackground="white")
        self.text_box.pack(padx=20, pady=(5, 10), fill="both", expand=True)

        scrollbar = Scrollbar(self.text_box)
        scrollbar.pack(side="right", fill="y")
        self.text_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_box.yview)

        self.status_label = Label(root, text="Ready", bg="#1e1e1e", fg="lightgray", font=("Arial", 9), anchor="w")
        self.status_label.pack(fill="x", side="bottom")

        self.original_image = None
        self.tk_image = None
        self.ocr_text = ""

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff")
        ])
        if file_path:
            try:
                self.original_image = Image.open(file_path).convert("RGB")
                draw = ImageDraw.Draw(self.original_image)
                data = pytesseract.image_to_data(self.original_image, output_type=pytesseract.Output.DICT)

                self.ocr_text = ""
                for i in range(len(data['text'])):
                    word = data['text'][i]
                    if int(data['conf'][i]) > 60 and word.strip():
                        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                        draw.rectangle([x, y, x+w, y+h], outline="lime", width=2)
                        draw.text((x, y - 10), word, fill="lime")
                        self.ocr_text += word + " "

                # Resize for display
                display_image = self.original_image.copy()
                display_image.thumbnail((600, 400))
                self.tk_image = ImageTk.PhotoImage(display_image)

                self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
                self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

                self.text_box.delete(1.0, tk.END)
                self.text_box.insert(tk.END, self.ocr_text.strip())
                self.status_label.config(text="Text and boxes extracted successfully.")

            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status_label.config(text="OCR failed.")

    def clear_content(self):
        self.canvas.delete("all")
        self.original_image = None
        self.tk_image = None
        self.ocr_text = ""
        self.text_box.delete(1.0, tk.END)
        self.status_label.config(text="Cleared.")

    def save_text(self):
        text = self.text_box.get(1.0, tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "No text to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            self.status_label.config(text=f"Text saved to: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
