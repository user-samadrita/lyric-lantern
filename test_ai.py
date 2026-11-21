import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=40000),
)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Write one cozy rainy-night song line.",
)
print(response.text)