import os
from PIL import Image
import magic
import pytesseract
import re
from main import UPLOAD_DIR

# Set path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# TO Check Mime Type
with open("sample6.pdf", "rb") as f:
    file_bytes = f.read()
    
    mime = magic.from_buffer(file_bytes, mime=True)
    print (f"Detected MIME type: {mime}")


# Load image
image = Image.open("sample5.pdf")  


# Extract text
text = pytesseract.image_to_string(image)

print("=== OCR RESULT ===")
print(text)