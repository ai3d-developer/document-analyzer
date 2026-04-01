import os
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load Environment Variables from .env file
load_dotenv()

from utils.extractors import extract_text
from utils.ai_analyzer import analyze_document_text

app = FastAPI(title="AI-Powered Document Analysis API")

# Authentication Dependency Server API Key
def verify_api_key(request: Request):
    """Verify that the Authorization or API-Key header matches the API_KEY environment variable."""
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        print("WARNING: API_KEY not set in environment.")
        return None  # Allow bypass if no key strictly set for testing
    
    auth_header = request.headers.get("Authorization")
    api_key_header = request.headers.get("api-key") or request.headers.get("x-api-key")

    token = None
    if auth_header:
        token = auth_header.replace("Bearer ", "").strip()
    elif api_key_header:
        token = api_key_header.strip()

    if token != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API Key or Authorization header")

    return token

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    token: str = Depends(verify_api_key)
):
    """
    Endpoint for Document Analysis & Extraction.
    Receives a PDF, DOCX, or Image file.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        # Read file contents entirely into memory
        file_bytes = await file.read()
        
        # 1. Extract Text based on file type
        try:
            extracted_text = extract_text(file_bytes, file.filename, file.content_type)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Failed to extract document: {str(e)}"})
            
        if not extracted_text:
             return JSONResponse(status_code=400, content={"error": "Document contains no readable text."})
        
        # 2. Analyze Text using AI (Gemini)
        try:
             analysis_result = analyze_document_text(extracted_text)
        except Exception as e:
             return JSONResponse(status_code=500, content={"error": str(e)})

        # Return standardized JSON Structure
        # Expected Format:
        # {
        #   "summary": "...",
        #   "entities": ["entity1", "entity2", ...],
        #   "sentiment": "positive" | "negative" | "neutral"
        # }
        return analysis_result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal server error during analysis."})
