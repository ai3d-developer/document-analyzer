import os
import json
from pydantic import BaseModel
from typing import List, Optional
from google import genai
from google.genai import types

class AnalysisResult(BaseModel):
    summary: str
    entities: List[str]
    sentiment: str

def analyze_document_text(text: str) -> dict:
    """Analyzes the extracted text using Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")

    # Initialize Gemini Client
    client = genai.Client(api_key=api_key)

    system_instruction = (
        "You are an AI Document Analyzer. You will receive the text of a document.\n"
        "Your task is to analyze the text and return a structured JSON response with three keys:\n"
        "1. 'summary': A concise summary of the document's content.\n"
        "2. 'entities': A list of key named entities (e.g., people, organizations, locations, monetary amounts, dates).\n"
        "3. 'sentiment': The overall sentiment of the text. Must be exactly 'positive', 'negative', or 'neutral'."
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=AnalysisResult,
                temperature=0.2,
            ),
        )

        # Parse the output
        if response.text:
            return json.loads(response.text)
        else:
            raise ValueError("Empty response from AI model")

    except Exception as e:
        raise ValueError(f"AI Analysis Failed: {str(e)}")
