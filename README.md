# 🏥 MediBot - Medical Report Analyzer

An intelligent medical report analyzer that uses OCR and AI to extract and interpret medical test results.

## 🚀 Features

- 📄 Extract text from medical reports (images and PDFs)
- 🔍 OCR with advanced preprocessing
- 🤖 AI-powered analysis using Google Gemini
- 📊 Clean and intuitive Streamlit interface
- 💾 Download analysis results

## 📦 Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install system dependencies:
   - **Tesseract OCR**: [Download here](https://github.com/tesseract-ocr/tesseract)
   - **Poppler** (for PDF support): [Download here](http://blog.alivate.com.au/poppler-windows/)
   - **Ghostscript** (for Camelot): [Download here](https://www.ghostscript.com/)

3. Set up API key:
   - The Gemini API key is already configured in the code
   - Or set it as environment variable: `export GEMINI_API_KEY=your_key_here`

## 🎯 Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
Medibot/
├── app.py              # Streamlit frontend
├── trial.py            # OCR backend logic
├── medicare_gui.py     # Alternative Tkinter GUI
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## ⚠️ Disclaimer

This tool is for informational purposes only. Always consult healthcare professionals for medical advice.
