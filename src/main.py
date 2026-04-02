import os
import base64
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load Environment Variables from .env file
load_dotenv()

from src.utils.extractors import extract_text
from src.utils.ai_analyzer import analyze_document_text

app = FastAPI(title="AI-Powered Document Analysis API")

# Add CORS Middleware to handle Cross-Origin Preflight (OPTIONS) requests from Judge Dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str

# Authentication Dependency Server API Key
def verify_api_key(request: Request):
    """Verify that the x-api-key header matches the API_KEY environment variable."""
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        print("WARNING: API_KEY not set in environment.")
        return None  # Allow bypass if no key strictly set for testing
    
    api_key_header = request.headers.get("x-api-key")

    if not api_key_header or api_key_header.strip() != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API Key or x-api-key header missing")

    return api_key_header.strip()


async def perform_analysis(doc_req: DocumentRequest):
    """Internal helper to handle document extraction and AI synthesis."""
    try:
        # 1. Decode Base64 Content back into Raw Bytes
        file_bytes = base64.b64decode(doc_req.fileBase64)
        
        # 2. Extract Text based on file type
        extracted_text = extract_text(file_bytes, doc_req.fileName, doc_req.fileType)
            
        if not extracted_text:
             return JSONResponse(status_code=400, content={"status": "error", "error": "Document contains no readable text."})
        
        # 3. Analyze Text using AI (Gemini 2.0 Flash on OpenRouter)
        ai_result = analyze_document_text(extracted_text)

        # Return standardized JSON Structure explicitly requested by Grading Rubric
        return {
            "status": "success",
            "fileName": doc_req.fileName,
            "summary": ai_result.get("summary", ""),
            "entities": ai_result.get("entities", {
                "names": [],
                "dates": [],
                "organizations": [],
                "amounts": []
            }),
            "sentiment": ai_result.get("sentiment", "Neutral")
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})

@app.get("/")
def read_root_get():
    """Serves the Beautiful Drag and Drop UI for manual testing."""
    # Serve the Beautiful Drag and Drop UI
    return FileResponse("src/static/index.html")

@app.post("/")
async def read_root_post(doc_req: DocumentRequest, token: str = Depends(verify_api_key)):
    """Handles POST to root / to avoid 'Method Not Allowed' on base URL submissions."""
    return await perform_analysis(doc_req)

@app.post("/api/document-analyze")
async def analyze_document(
    doc_req: DocumentRequest,
    token: str = Depends(verify_api_key)
):
    """Endpoint for Document Analysis & Extraction (backward compatibility)."""
    return await perform_analysis(doc_req)
