from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ocr_service import extract_marksheet
import tempfile
import os
from ocr_service import extract_marksheet


app = FastAPI(
    title="OCR",
    description="PaddleOCR"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "OCR Service is running"
    }

@app.post("/ocr")
async def process_ocr(file: UploadFile = File(...)):
    # Create temporary file
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name


    try:
        # Send image to our OCR service
        result = extract_marksheet(temp_path)
        return result
    
    finally:
        # Delete temporary image
        if os.path.exists(temp_path):
            os.remove(temp_path)
