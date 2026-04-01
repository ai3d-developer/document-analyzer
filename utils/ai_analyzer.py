import os
import json
from openai import OpenAI

def analyze_document_text(text: str) -> dict:
    """Analyzes the extracted text using OpenRouter API"""
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
        "Your task is to analyze the text and return a structured JSON response EXACTLY with three keys:\n"
        "1. 'summary': A concise summary of the document's content.\n"
        "2. 'entities': A list of key named entities (e.g., people, organizations, locations, monetary amounts, dates).\n"
        "3. 'sentiment': The overall sentiment of the text. Must be exactly 'positive', 'negative', or 'neutral'.\n"
        "You MUST output valid JSON only, without any markdown blocks or additional text."
    )

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-4o-mini",
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
