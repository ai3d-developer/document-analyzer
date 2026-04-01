import os
import json
from openai import OpenAI

def analyze_document_text(text: str) -> dict:
    """Analyzes the extracted text using OpenRouter API to match the required rubric JSON schema."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set in environment variables.")

    # Initialize OpenAI Client pointing to OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    system_instruction = (
        "You are an AI Document Analyzer. You will receive the text of a document.\n"
        "Your task is to analyze the text and return a structured JSON response EXACTLY with these keys:\n"
        "1. 'summary': A concise summary of the document's content.\n"
        "2. 'entities': An object containing exactly four arrays: 'names', 'dates', 'organizations', and 'amounts'.\n"
        "   IMPORTANT: ONLY extract words or phrases that physically exist in the source text. NEVER guess or hallucinate entities.\n"
        "   - 'names': List of people or human groups explicitly mentioned in the text.\n"
        "   - 'dates': List of exact dates explicitly mentioned in the text.\n"
        "   - 'organizations': List organizations strictly from the document. Include: Company names, employers, institutions (schools, universities), brands, and event names. EXCLUDE: software/tools (e.g., Adobe, Figma), skills or technologies (e.g., Python, React), generic words, and UI text. ONLY return real organizations explicitly mentioned in the content. Do not guess or hallucinate.\n"
        "   - 'amounts': List of monetary amounts explicitly mentioned in the text.\n"
        "3. 'sentiment': The overall sentiment of the text. Must be exactly 'Positive', 'Negative', or 'Neutral'.\n"
        "You MUST output valid JSON only, without any markdown blocks or additional text."
    )

    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        response_text = completion.choices[0].message.content
        if response_text:
            return json.loads(response_text)
        else:
            raise ValueError("Empty response from AI model")

    except Exception as e:
        raise ValueError(f"AI Analysis Failed: {str(e)}")
