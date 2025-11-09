import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import pytesseract
import re
import requests
import webbrowser
import os
from groq import Groq

# ---------------- API CONFIG ----------------
# Option 1: Load from environment variable (recommended)
api_key = os.environ.get("GROQ_API_KEY")

# Option 2: Hardcode directly for testing (⚠ not safe for production)
# api_key = "gsk_your_real_api_key_here"

if not api_key:
    raise ValueError("❌ No API key found. Set GROQ_API_KEY in environment or hardcode it.")

client = Groq(api_key=api_key)

# Groq API endpoint
OPENROUTER_API_KEY = api_key
OPENROUTER_URL = "https://api.groq.com/openai/v1/chat/completions"

# ---------------- OCR CONFIG ----------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------- MOCK DATA ----------------
mock_doctors = {
    'General Physician': [
        {"name": "Dr. Rajesh Sharma", "specialty": "General Medicine", "experience": "15 years",
         "contact": "+91 98765 43210", "address": "Care Hospital", "distance": "2.3 km"},
        {"name": "Dr. Priya Patel", "specialty": "Family Medicine", "experience": "12 years",
         "contact": "+91 98765 43211", "address": "Fortis Hospital", "distance": "3.1 km"},
    ],
    'Cardiologist': [
        {"name": "Dr. Sunita Mehta", "specialty": "Cardiology", "experience": "20 years",
         "contact": "+91 98765 43213", "address": "Sahyadri Hospital", "distance": "2.8 km"},
    ],
    'Neurologist': [
        {"name": "Dr. Neha Singh", "specialty": "Neurology", "experience": "14 years",
         "contact": "+91 98765 43215", "address": "Deenanath Hospital", "distance": "2.1 km"},
    ],
    'Orthopedic': [
        {"name": "Dr. Sanjay Kulkarni", "specialty": "Orthopedics", "experience": "13 years",
         "contact": "+91 98765 43217", "address": "Aditya Birla Hospital", "distance": "2.9 km"},
    ]
}


# ---------------- APP CLASS ----------------
class MediCareApp:
    SPECIALTY_KEYWORDS = {
        "General Physician": ["fever", "cold", "cough", "pain", "infection"],
        "Cardiologist": ["heart", "cardiac", "hypertension"],
        "Neurologist": ["brain", "nerve", "migraine", "seizure"],
        "Orthopedic": ["bone", "joint", "fracture", "sprain"],
    }

    def __init__(self, root):
        self.root = root
        self.root.title("MediCare Assistant")
        self.root.geometry("900x650")

        self.selected_image = None
        self.ocr_text = ""
        self.gemini_info = ""
        self.recommended_specialty = "General Physician"

        self.create_header()
        self.create_tabs()
        self.create_content_frame()
        self.show_medicine_scanner()

    def create_header(self):
        header = tk.Frame(self.root, bg="#f5e6f7")
        header.pack(fill="x")

        tk.Label(header, text="🌟 MediCare Assistant", font=("Helvetica", 20, "bold"),
                 bg="#f5e6f7", fg="#800080").pack(side="left", padx=20)
        tk.Label(header, text="📍 Pune, Maharashtra", font=("Helvetica", 12),
                 bg="#f5e6f7").pack(side="right", padx=20)

    def create_tabs(self):
        tabs = tk.Frame(self.root)
        tabs.pack(fill="x")

        self.medicine_btn = ttk.Button(tabs, text="💊 Medicine Scanner", command=self.show_medicine_scanner)
        self.doctor_btn = ttk.Button(tabs, text="🩺 Find Doctors", command=self.show_doctors)

        self.medicine_btn.pack(side="left", expand=True, fill="x")
        self.doctor_btn.pack(side="left", expand=True, fill="x")

    def create_content_frame(self):
        self.content = tk.Frame(self.root)
        self.content.pack(fill="both", expand=True)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_medicine_scanner(self):
        self.clear_content()

        tk.Label(self.content, text="Upload Medicine Image", font=("Helvetica", 14)).pack(pady=10)
        upload_btn = ttk.Button(self.content, text="Select Image", command=self.select_image)
        upload_btn.pack(pady=10)

        self.image_label = tk.Label(self.content)
        self.image_label.pack()

        analyze_btn = ttk.Button(self.content, text="Analyze Medicine", command=self.analyze_image)
        analyze_btn.pack(pady=10)

        self.result_box = tk.Text(self.content, height=15, width=100, wrap="word")
        self.result_box.pack(pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            self.tk_img = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.tk_img)
            self.selected_image = file_path

    def analyze_image(self):
        if not self.selected_image:
            messagebox.showwarning("No Image", "Please select an image first.")
            return

        text = self.perform_ocr(self.selected_image)
        self.ocr_text = text

        gemini_ans = self.ask_gemini_for_usage_and_warning(text)
        self.gemini_info = gemini_ans

        self.result_box.delete(1.0, tk.END)
        self.result_box.insert(tk.END, gemini_ans)

        next_btn = ttk.Button(self.content, text=f"Find {self.recommended_specialty} Nearby",
                              command=lambda: self.show_doctors(self.recommended_specialty))
        next_btn.pack(pady=10)

    def perform_ocr(self, image_path):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast = cv2.convertScaleAbs(gray, alpha=1.8, beta=30)

        config = r'--oem 1 --psm 6'
        raw_text = pytesseract.image_to_string(contrast, config=config)
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', raw_text.lower()).strip()
        print("\n🔎 OCR Raw:\n", raw_text)
        print("\n🧼 OCR Cleaned:\n", cleaned)

        return cleaned

    def ask_gemini_for_usage_and_warning(self, text):
        prompt = f"""
I scanned this text from a medicine box:
\"{text}\"

👉 Please:
1️⃣ Identify the correct medicine name.
2️⃣ State the usual dose and strength clearly.
3️⃣ Explain what it is used for in simple words.
4️⃣ Give clear instructions for how a patient should take it.
5️⃣ Mention any important safety warnings in simple language.

💡 Write this in plain, friendly English for someone with no medical background.
Keep it short, clear and easy to read.
Use short sentences.
"""

        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",  # ✅ supported model
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            data = response.json()
            print("⚙ RAW OpenRouter response:\n", data)

            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                print("❌ Model error:", error_msg)
                return f"Error from model: {error_msg}"

            answer = data["choices"][0]["message"]["content"]

            self.recommended_specialty = "General Physician"
            for specialty, keywords in self.SPECIALTY_KEYWORDS.items():
                if any(keyword in answer.lower() for keyword in keywords):
                    self.recommended_specialty = specialty
                    break

            return answer

        except Exception as e:
            print("❌ Exception:", e)
            return "Something went wrong while getting response from the AI."

    def show_doctors(self, specialty=None):
        self.clear_content()

        tk.Label(self.content, text="Choose Specialty", font=("Helvetica", 14)).pack(pady=10)
        specialties = ["General Physician", "Cardiologist", "Neurologist", "Orthopedic"]

        for spec in specialties:
            btn = ttk.Button(self.content, text=spec, command=lambda s=spec: self.show_doctor_list(s))
            btn.pack(pady=5, padx=20, fill="x")

        if specialty:
            self.show_doctor_list(specialty)

    def show_doctor_list(self, specialty):
        self.clear_content()
        tk.Label(self.content, text=f"{specialty} Doctors Near You", font=("Helvetica", 14, "bold")).pack(pady=10)

        for doc in mock_doctors.get(specialty, []):
            frame = tk.LabelFrame(self.content, text=doc['name'], padx=10, pady=5)
            frame.pack(fill="x", padx=20, pady=5)

            info = f"{doc['specialty']} | {doc['experience']}\n📞 {doc['contact']}\n📍 {doc['address']} ({doc['distance']})"
            tk.Label(frame, text=info, anchor="w", justify="left").pack(fill="x")

        tk.Button(
            self.content,
            text=f"🔍 Search {specialty} doctors near me on Google",
            command=lambda: webbrowser.open(f"https://www.google.com/search?q={specialty}+doctor+near+me")
        ).pack(pady=5)

        tk.Button(
            self.content,
            text=f"🗺 Open {specialty} doctors on Google Maps",
            command=lambda: webbrowser.open(f"https://www.google.com/maps/search/{specialty}+doctor+near+me")
        ).pack(pady=5)

        tk.Button(
            self.content,
            text=f"📞 See {specialty} doctors on Justdial",
            command=lambda: webbrowser.open(f"https://www.justdial.com/search?q={specialty}+doctor+near+me")
        ).pack(pady=5)


# ---------------- RUN APP ----------------
root = tk.Tk()
app = MediCareApp(root)
root.mainloop()
