import os
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path
import mimetypes
import cv2
import numpy as np
import camelot

# If using Windows, set tesseract path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Global Tesseract config with whitelist for numbers, decimals, units
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,:/-()% '

def clean_ocr_output(text):
    """
    Correct common OCR mistakes in medical reports.
    """
    text = text.replace(',', '.').replace('O', '0').replace('l', '1')
    # Adjust further based on real OCR mistakes in your data
    return text

def preprocess_image(image_path, resize=True, scale_percent=200):
    """
    Preprocesses image with contrast enhancement, optional resizing, and Gaussian blur.
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Increase contrast using convertScaleAbs instead of histogram equalization
    alpha = 1.5  # Contrast control
    beta = 0     # Brightness control
    gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    # Light Gaussian blur to reduce noise while preserving dots/decimals
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Optional resizing to enhance small text
    if resize:
        width = int(gray.shape[1] * scale_percent / 100)
        height = int(gray.shape[0] * scale_percent / 100)
        gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

    return gray

def extract_text_from_image(image_path):
    """
    Extracts text from image with optimized pre-processing and cleaning.
    """
    preprocessed_img = preprocess_image(image_path, resize=True)

    # Save preprocessed image for debugging (optional)
    # cv2.imwrite("debug_preprocessed.png", preprocessed_img)

    text = pytesseract.image_to_string(preprocessed_img, config=custom_config)
    text = clean_ocr_output(text)
    return text

def extract_tables_from_pdf(pdf_path):
    """
    Uses Camelot to extract tables from PDFs (works only for text-based PDFs).
    Returns list of DataFrame tables.
    """
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')  # 'stream' works better for lab reports
    return tables

def extract_text_from_pdf(pdf_path):
    text = ""

    # First, try Camelot table extraction for text-based PDFs
    try:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        if tables and tables.n > 0:
            print(f"Found {tables.n} tables using Camelot.")
            for idx, table in enumerate(tables):
                text += f"--- Table {idx+1} ---\n"
                text += table.df.to_string(index=False) + "\n"
            return text  # Return table extraction as priority
    except Exception as e:
        print(f"Camelot extraction failed: {e}")

    # Fallback to OCR for scanned PDFs
    images = convert_from_path(pdf_path, dpi=400)
    for i, img_page in enumerate(images):
        temp_image_path = f"temp_page_{i}.png"
        img_page.save(temp_image_path)
        preprocessed = preprocess_image(temp_image_path, resize=True)
        
        # Save preprocessed image for debugging (optional)
        # cv2.imwrite(f"debug_preprocessed_page_{i}.png", preprocessed)
        
        page_text = pytesseract.image_to_string(preprocessed, config=custom_config)
        text += clean_ocr_output(page_text) + "\n"

        # Cleanup temp image file
        os.remove(temp_image_path)

    return text

def get_file_type(file_path):
    """
    Determines the MIME type of the file.
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type

def extract_text(file_path):
    """
    Main function to extract text based on file type (PDF or image).
    """
    file_type = get_file_type(file_path)
    if not file_type:
        return "Cannot determine file type."

    if "pdf" in file_type:
        print("Detected PDF file.")
        return extract_text_from_pdf(file_path)

    elif "image" in file_type:
        print("Detected image file.")
        return extract_text_from_image(file_path)

    else:
        return "Unsupported file type."

# Example usage:
if __name__ == "__main__":
    file_path = "blood_report.png"  # Replace with your file path

    extracted_text = extract_text(file_path)
    print("Extracted Text:\n", extracted_text)
