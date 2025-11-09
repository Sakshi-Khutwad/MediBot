<<<<<<< HEAD
import os
from google import generativeai as genai

# Use the API key from the environment variable GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Explain how AI works in a few words")
from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)
