import os
from google import genai

# Set your API key
os.environ["GEMINI_API_KEY"] = "AIzaSyA0k9SGya9EIkPrL3KCFF-fDCQQUpEw4xI"

client = genai.Client()

print("Available Gemini models for your API key:")
for model in client.models.list():
    print(model.name)
