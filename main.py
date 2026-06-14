import os
import io
import magic
import torch
import pytesseract
import re
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdf2image import convert_from_bytes
from PIL import Image
from transformers import AutoTokenizer, AutoModelForCausalLM


# ================= OCR CONFIG =================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ================= APP =================
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ================= DEVICE =================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ================= MODEL LOAD =================
LLM_MODEL_PATH = "./sarvam_local"

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(LLM_MODEL_PATH).to(device)
model.eval()
print("Model loaded!")


# ================= REQUEST MODELS =================
class PromptRequest(BaseModel):
    prompt: str

class SummarizationRequest(BaseModel):
    text: str
    target_language: str

class TranslationRequest(BaseModel):
    text: str
    target_language: str


def clean_translation_output(text: str):
    text = re.sub(r"Translate.*?OUTPUT:", "", text, flags=re.S)
    text = re.sub(r"Text:.*", "", text)
    return text.strip()

# ================= CLEAN OUTPUT =================
def clean_output(text: str):

    if not text:
        return ""

    markers = [
        "User:",
        "AI Assistant:",
        "Assistant:",
        "Human:",
        "Similar Q",
        "Explanation",
        "Q&A",
        "###"
    ]

    for marker in markers:
        if marker in text:
            text = text.split(marker)[0]

    return text.strip()

#-----------Clean Translation Output-----------
import re

def clean_translation_output(text):

    text = text.replace("</s>", "")
    text = text.replace("[/INST]", "")

    match = re.search(
        r"TEXT OUTPUT \(Translation\):\s*(.*)",
        text,
        re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return text.strip()
#-----pdf fucntion-------

from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
import io

def extract_pdf_smart(file_bytes: bytes) -> str:
    # STEP 1: Try normal extraction
    reader = PdfReader(io.BytesIO(file_bytes))

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    # If text found → return
    if text.strip():
        return text.strip()

    # STEP 2: OCR fallback (scanned PDF)
 

def extract_pdf_ocr(file_bytes: bytes):
    images = convert_from_bytes(
        file_bytes,
     POPPLER_PATH = r"C:\Users\Acer\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin"
    )

    ocr_text = ""

    for img in images:
        ocr_text += pytesseract.image_to_string(img) + "\n"

    return ocr_text.strip()
# ================= INFERENCE =================
def run_inference(prompt: str) -> str:

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    inputs = {
        k: v.to(device)
        for k, v in inputs.items()
    }

    with torch.no_grad():

     outputs= model.generate(
        **inputs,
        max_new_tokens=80,
        do_sample=False,
        temperature=0.1,
        repetition_penalty=1.2,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    )

    stop_markers = [
        "User:",
        "Human:",
        "Assistant:",
        "AI Assistant:",
        "Question:",
        "Input:"
    ]

    for marker in stop_markers:
        if marker in response:
            response = response.split(marker)[0]

    return response.strip()
# ================= FILE TYPE DETECTOR =================
def detect_file_type(file_bytes: bytes):
    mime = magic.from_buffer(file_bytes, mime=True)

    if mime in ["image/jpeg", "image/png", "image/jpg"]:
        return "image", mime
    elif mime == "application/pdf":
        return "pdf", mime
    else:
        return None, mime


# ================= OCR IMAGE =================
def extract_text_with_tesseract(image: Image.Image) -> str:
    image = image.convert("RGB")
    return pytesseract.image_to_string(image).strip()


# ================= OCR PDF =================
POPPLER_PATH = r"C:\Users\Acer\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin"

def extract_text_from_pdf(file_bytes: bytes):

    images = convert_from_bytes(
        file_bytes,
        poppler_path=POPPLER_PATH
    )

    text = ""

    for page in images:

        text += pytesseract.image_to_string(
            page.convert("RGB")
        )

        text += "\n"

    return text.strip()


# ================= DOCUMENT PROCESSOR =================
def process_document(text: str):
    prompt = f"""
You are a strict AI document analyzer.

RULES:
- Do NOT generate user explanation
- Do NOT generate Q&A
- Do NOT repeat input text
- Do NOT add extra explanation
- Follow format exactly

FORMAT:

Summary:
- short points

Key Points:
- bullet points

Simple Explanation:
- simple version

TEXT:
{text}
"""
    return run_inference(prompt)

#=================ENDPOINTS=================
# ================= ROUTES =================

@app.get("/")
def home():
    return {"message": "AI Backend Running"}


@app.get("/chat")
def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


# ================= ENDPOINT GENERATE =================
@app.post("/generate")
def generate_text(request: PromptRequest):

    prompt = f"""
Answer the question briefly.

Question:
{request.prompt}

Answer:
"""

    response = run_inference(prompt)

    return {
        "response": response
    }


# ================= ENDPOINT SUMMARIZE =================
@app.post("/summarize")
def summarize_text(request: SummarizationRequest):

    clean_text = clean_output(request.text)

    prompt = f"""
Summarize the text in {request.target_language}.
Reply ONLY in {request.target_language}.

Text:
{clean_text}
"""
    return {"response": run_inference(prompt)}
# ================= ENDPOINT TRANSLATE =================
@app.post("/translate")
def translate_text(request: TranslationRequest):

    text = request.text.strip()
    lang = request.target_language.strip()

    prompt = f"""
You are a professional translator.

RULES:
- Translate ONLY the text below
- Do NOT repeat instructions
- Do NOT add explanations
- Output ONLY translation

TARGET LANGUAGE: {lang}

TEXT:
{text}
"""

    result = run_inference(prompt)

    return {
    "response": clean_translation_output(result)
}


# ================= ENDPOINT UPLOAD (OCR + LLM) =================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()

    file_type, mime = detect_file_type(content)

    if file_type is None:
        raise HTTPException(status_code=400, detail=f"Unsupported file: {mime}")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(content)

    if file_type == "image":
        image = Image.open(io.BytesIO(content))
        extracted_text = extract_text_with_tesseract(image)

    elif file_type == "pdf":
        extracted_text = extract_text_from_pdf(content)

    analysis = process_document(extracted_text)

    return {
        "filename": file.filename,
        "mime_type": mime,
        "stored_path": file_path,
        "extracted_text": extracted_text,
        "analysis": analysis
    }


# ================= ENDPOINT OCR ONLY =================
@app.post("/extract-text")
async def extract_text_api(file: UploadFile = File(...)):
    try:
        content = await file.read()

        file_type, mime = detect_file_type(content)

        if file_type is None:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime}")

        if file_type == "image":
            image = Image.open(io.BytesIO(content))
            text = extract_text_with_tesseract(image)

        elif file_type == "pdf":
            text = extract_text_from_pdf(content)

        analysis = ""

        if len(text.strip()) > 20:
            analysis = process_document(text[:2000])
        return {
            "filename": file.filename,
            "mime_type": mime,
            "text": text,
            "text_length": len(text),
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    