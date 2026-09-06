# ai_client.py
import os
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT, get_article_prompt

def generate_article_content(title, source_text):
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
        ),
    )

    result = response.text
    if "```html" in result:
        result = result.split("```html")[1].split("```")[0].strip()
    elif "```" in result:
        result = result.split("```")[1].split("```")[0].strip()

    return result
