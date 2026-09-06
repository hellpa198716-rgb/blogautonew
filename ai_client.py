# ai_client.py
import os
import json
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT, get_article_prompt

def generate_article_data(title, source_text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)
    prompt = get_article_prompt(title, source_text)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            response_mime_type="application/json"
        ),
    )

    try:
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
        return None
