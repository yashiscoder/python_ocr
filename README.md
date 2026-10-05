# Marksheet OCR

A lightweight OCR web application for extracting information from marksheet images using **PaddleOCR** and **FastAPI**.

The application allows a user to upload a marksheet image through a web interface, processes the image using PaddleOCR, and returns the extracted information as structured JSON.

> **Project Status:** Testing / Development

---

## Overview

Manually extracting information from marksheets can be time-consuming, especially when dealing with a large number of documents.

This project provides a simple OCR pipeline that takes a marksheet image as input and converts the visible text into structured data that can be consumed by other applications through a REST API.

The project consists of two main components:

- **Python OCR backend** — FastAPI + PaddleOCR
- **Web frontend** — HTML, CSS and JavaScript

The frontend communicates with the FastAPI backend through the `/ocr` endpoint.

---

## How It Works

```text
                 ┌──────────────────────┐
                 │       User           │
                 │                      │
                 │ Upload Marksheet     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      Frontend        │
                 │  HTML/CSS/JavaScript │
                 └──────────┬───────────┘
                            │
                     POST /ocr
                            │
                            ▼
                 ┌──────────────────────┐
                 │       FastAPI        │
                 │      Backend         │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     PaddleOCR        │
                 │                      │
                 │ Text Detection       │
                 │ Text Recognition     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   OCR Processing     │
                 │   & Extraction       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │    JSON Response     │
                 └──────────────────────┘
```

---

## Features

- Upload marksheet images
- Drag and drop image support
- Image validation
- OCR processing using PaddleOCR
- FastAPI REST API
- Structured JSON response
- JSON result viewer
- Copy JSON result to clipboard
- Temporary file processing
- Automatic temporary file cleanup
- Swagger API documentation through FastAPI

---

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| PaddlePaddle | Deep learning framework |
| PaddleOCR | OCR engine |
| PaddleX | PaddleOCR inference pipeline |

### Frontend

| Technology | Purpose |
|---|---|
| HTML | Page structure |
| CSS | UI styling |
| JavaScript | File upload and API communication |

---

## Project Structure

```text
OCR/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── ocr/
│   ├── samples/
│   │   └── 12th.jpg
│   │
│   ├── main.py
│   ├── ocr_service.py
│   └── test_ocr.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

### Backend Files

#### `main.py`

Contains the FastAPI application and API endpoints.

The main OCR endpoint is:

```text
POST /ocr
```

It accepts an uploaded image and sends it to the OCR service.

#### `ocr_service.py`

Contains the PaddleOCR processing logic.

This is where the uploaded marksheet image is passed to PaddleOCR and the extracted information is processed.

#### `test_ocr.py`

Used for testing the OCR service directly without going through the web interface.

---

## Frontend

The frontend provides a simple interface for interacting with the OCR API.

The user can:

1. Select a marksheet image.
2. Drag and drop an image.
3. Start OCR processing.
4. View the extracted JSON.
5. Copy the JSON result.

The frontend communicates with the backend using:

```javascript
fetch("/ocr", {
    method: "POST",
    body: formData
});
```

---

# Installation

## Prerequisites

Make sure the following are installed:

- Python 3.12
- Git
- pip

Python **3.12** is recommended for this project because the PaddlePaddle environment used by the project is configured for Python 3.12.

---

## 1. Clone the Repository

```bash
git clone https://github.com/<username>/<repository>.git
```

Move into the project:

```bash
cd OCR
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
py -3.12 -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

After activation, the terminal should show:

```text
(.venv)
```

Verify Python:

```powershell
python --version
```

Expected:

```text
Python 3.12.x
```

---

## 3. Install Dependencies

Install the required Python packages:

```powershell
python -m pip install -r requirements.txt
```

---

# Running the Application

## Start FastAPI

Navigate to the backend directory:

```powershell
cd ocr
```

Start the development server:

```powershell
python -m uvicorn main:app --reload
```

The API will start at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically generates interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

You can test the `/ocr` endpoint directly from Swagger UI.

---

# API

## `GET /`

Health check endpoint.

### Response

```json
{
    "message": "OCR Service is running"
}
```

---

## `POST /ocr`

Processes an uploaded image using PaddleOCR.

### Request

The request must contain a multipart form-data field:

```text
file
```

Example using cURL:

```bash
curl -X POST \
  http://127.0.0.1:8000/ocr \
  -F "file=@samples/12th.jpg"
```

---

## Response

The endpoint returns the extracted marksheet information as JSON.

The exact JSON structure depends on the extraction logic implemented in:

```text
ocr/ocr_service.py
```

Example:

```json
{
    "name": "Student Name",
    "roll_number": "123456",
    "subjects": [
        {
            "subject": "English",
            "marks": 85
        },
        {
            "subject": "Mathematics",
            "marks": 91
        }
    ],
    "total": 520,
    "percentage": 86.67
}
```

---

# Testing OCR Directly

You can test PaddleOCR without the web interface.

From the `ocr` directory:

```powershell
python test_ocr.py
```

The test script processes the sample marksheet:

```text
ocr/samples/12th.jpg
```

This is useful for verifying that the OCR pipeline is working before testing the API or frontend.

---

# Frontend Usage

Once the application is running:

1. Open the frontend.
2. Select a marksheet image.
3. The selected file will appear in the upload area.
4. Click **Extract Text**.
5. The image will be sent to the FastAPI `/ocr` endpoint.
6. PaddleOCR processes the image.
7. The extracted JSON will be displayed on the page.
8. Click **Copy JSON** to copy the result.

---

# OCR Pipeline

The OCR processing consists of several stages:

```text
Input Image
     │
     ▼
Document Processing
     │
     ▼
Text Detection
     │
     ▼
Text Recognition
     │
     ▼
Extracted Text
     │
     ▼
Marksheet Data Processing
     │
     ▼
JSON
```

PaddleOCR handles the core text detection and recognition process, while the project's Python logic processes the OCR output into the required JSON structure.

---

# Dependencies

The project uses the following major packages:

```text
PaddlePaddle
PaddleOCR
PaddleX
FastAPI
Uvicorn
python-multipart
```

The exact versions used by the project are maintained in:

```text
requirements.txt
```

---

# Model Files

PaddleOCR downloads the required model files when they are first used.

The first OCR execution may therefore take longer because the models need to be downloaded and initialized.

After the models have been downloaded, subsequent OCR requests should use the cached models.

Model files should **not** be committed to the Git repository.

---

# Configuration

The project currently runs PaddleOCR using CPU inference.

For local development, the application can be started using:

```powershell
python -m uvicorn main:app --reload
```

For deployment, the application should be started without the development reload option.

---

# Deployment

The project is intended to be deployable as a single application.

Recommended architecture:

```text
                 GitHub
                   │
                   ▼
             Hosting Platform
                   │
          ┌────────┴────────┐
          │                 │
       FastAPI           Frontend
          │
          ▼
      PaddleOCR
```

The frontend and backend can be served from the same application so that the frontend can communicate with the API using:

```javascript
fetch("/ocr")
```

This avoids hardcoding a local address such as:

```text
http://127.0.0.1:8000
```

---

# Current Limitations

This project is currently intended for testing and development.

Some limitations include:

- OCR accuracy depends on image quality.
- Different marksheet layouts may require different extraction logic.
- Handwritten text may not be recognized reliably.
- Very large images may require additional preprocessing.
- The application currently focuses on marksheet images.
- Production-level authentication and rate limiting are not implemented.
- The application has not yet been optimized for high-volume OCR processing.

---

# Future Improvements

Possible improvements include:

- Support multiple marksheet formats
- Improve marksheet field extraction
- Add image preprocessing
- Add OCR confidence scores
- Support PDF marksheets
- Add batch processing
- Add authentication
- Add request validation
- Add API rate limiting
- Add database support
- Improve error handling
- Add production logging
- Optimize OCR model loading
- Deploy the application publicly

---

# Development

This project is being developed as a lightweight OCR service for experimenting with marksheet data extraction using Python and PaddleOCR.

The architecture is intentionally simple:

```text
Frontend
   ↓
FastAPI
   ↓
OCR Service
   ↓
PaddleOCR
   ↓
JSON
```

This makes the OCR service easy to test independently and allows the backend to be integrated with other applications in the future.

---

# License

This project is intended for educational, development, and testing purposes.
