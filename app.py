import streamlit as st
import os
from PIL import Image
import tempfile
from trial import extract_text, extract_text_from_image, extract_text_from_pdf
import requests
import json
import pytesseract
import google.generativeai as genai

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set page config
st.set_page_config(
    page_title="MediBot - Medical Report Analyzer",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .upload-box {
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: white;
    }
    h1 {
        color: #2c3e50;
    }
    .result-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🏥 MediBot - Medical Report Analyzer")
st.markdown("### Upload your medical report (image or PDF) for intelligent analysis")

# Sidebar
with st.sidebar:
    st.header("📋 About")
    st.info("""
    **MediBot** helps you understand your medical reports by:
    - 📄 Extracting text from images and PDFs
    - 🔍 Analyzing medical values
    - 💡 Providing insights and explanations
    - ⚠️ Highlighting abnormal values
    """)
    
    st.header("⚙️ Settings")
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Full Analysis", "Quick Summary", "Value Extraction Only"]
    )

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Upload Medical Report")
    uploaded_file = st.file_uploader(
        "Choose an image or PDF file",
        type=["png", "jpg", "jpeg", "pdf"],
        help="Supported formats: PNG, JPG, JPEG, PDF"
    )
    
    if uploaded_file is not None:
        # Display uploaded file
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show preview for images
        if uploaded_file.type.startswith('image'):
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

with col2:
    st.markdown("### 📊 Analysis Results")
    
    if uploaded_file is not None:
        if st.button("🔬 Analyze Report", use_container_width=True):
            with st.spinner("🔄 Processing your medical report..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    # Extract text using your backend
                    extracted_text = extract_text(tmp_file_path)
                    
                    # Display extracted text
                    with st.expander("📝 Extracted Text", expanded=False):
                        st.text_area("Raw OCR Output", extracted_text, height=200)
                    
                    # Analyze with Gemini using REST API
                    if extracted_text and extracted_text.strip():
                        GEMINI_API_KEY = "AIzaSyA0k9SGya9EIkPrL3KCFF-fDCQQUpEw4xI"
                        genai.configure(api_key=GEMINI_API_KEY)
                        
                        model = genai.GenerativeModel('gemini-2.5-flash')  # Use Gemini 2.5
                        prompt = f"""
                        Analyze this medical report and provide:
                        1. **Report Type**: Identify what kind of medical test/report this is
                        2. **Key Values**: List all important medical values with their units
                        3. **Normal Ranges**: Show normal ranges for each value
                        4. **Interpretation**: Explain what the values mean in simple terms
                        5. **Abnormal Findings**: Highlight any values outside normal range
                        6. **Recommendations**: Suggest if consultation with a doctor is needed
                        
                        Medical Report Text:
                        {extracted_text}
                        
                        Format your response clearly with headers and bullet points.
                        """
                        response = model.generate_content(prompt)
                        st.markdown("### 🤖 AI Analysis")
                        st.markdown(response.text)
                        st.download_button(
                            label="📥 Download Analysis",
                            data=f"EXTRACTED TEXT:\n{extracted_text}\n\n{'='*50}\n\nAI ANALYSIS:\n{response.text}",
                            file_name="medical_report_analysis.txt",
                            mime="text/plain"
                        )
                
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                
                finally:
                    # Cleanup temp file
                    if os.path.exists(tmp_file_path):
                        os.remove(tmp_file_path)
    else:
        st.info("👆 Please upload a medical report to begin analysis")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>⚠️ <strong>Disclaimer:</strong> This tool is for informational purposes only. 
    Always consult with healthcare professionals for medical advice.</p>
    <p>Made with ❤️ using Streamlit & Google Gemini AI</p>
</div>
""", unsafe_allow_html=True)
