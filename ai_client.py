import os
import json
import google.generativeai as genai
from prompts import SYSTEM_PROMPT, get_article_prompt

def generate_article_data(title, summary):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY가 설정되지 않았습니다.")
        return None

    genai.configure(api_key=api_key)

    # 404 에러 방지를 위해 호환 모델명 지정 (gemini-1.5-flash-latest 또는 gemini-2.0-flash)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        system_instruction=SYSTEM_PROMPT,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }
    )

    prompt = get_article_prompt(title, summary)

    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"AI 콘텐츠 생성 실패: {e}")
        return None
