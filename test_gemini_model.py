import os
from google import generativeai as genai

os.environ["GOOGLE_API_KEY"] = "AIzaSyA0k9SGya9EIkPrL3KCFF-fDCQQUpEw4xI"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")  # Use "gemini-2.5-flash" for Gemini 2.5
response = model.generate_content("Explain how AI works in a few words")
print(response.text)
