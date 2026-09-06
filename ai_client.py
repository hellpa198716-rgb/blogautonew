# ai_client.py
import os
from openai import OpenAI
from prompts import SYSTEM_PROMPT, get_article_prompt

def generate_article_content(title, source_text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    
    client = OpenAI(api_key=api_key)
    prompt = get_article_prompt(title, source_text)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # 비용 효율적이면서 성능이 뛰어난 모델
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3, # 환각 방지를 위해 낮게 설정
    )
    
    result = response.choices[0].message.content
    # 마크다운 코드블록 정제
    if "```html" in result:
        result = result.split("```html")[1].split("```")[0].strip()
    elif "```" in result:
        result = result.split("```")[1].split("```")[0].strip()
        
    return result