import os
import json
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT, get_article_prompt

def generate_article_data(title, summary):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY가 설정되지 않았습니다.")
        return None

    client = genai.Client(api_key=api_key)
    prompt = get_article_prompt(title, summary)

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI 콘텐츠 생성 실패: {e}")
        return None
