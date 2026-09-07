import os
import json
import google.generativeai as genai
from prompts import get_system_prompt, build_user_prompt

def generate_article_data(title, summary="", source_url=""):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY가 설정되지 않았습니다.")
        return None

    genai.configure(api_key=api_key)

    # E-E-A-T 검증 및 사실에 기반한 수치 작성을 유도하는 프롬프트 가져오기
    system_prompt = get_system_prompt()
    user_prompt = build_user_prompt(title, summary, source_url)

    # Gemini 모델 설정 (실제 존재하는 gemini-1.5-flash 모델로 변경)
    model = genai.GenerativeModel(
        model_name="gemini-3.6-flash",
        system_instruction=system_prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        response = model.generate_content(user_prompt)
        # JSON 문자열 파싱
        article_json = json.loads(response.text)
        return article_json

    except json.JSONDecodeError as e:
        print(f"JSON 파싱 실패: {e}")
        print(f"원문 응답: {getattr(response, 'text', '응답 없음')}")
        return None
    except Exception as e:
        print(f"Gemini API 호출 중 오류 발생: {e}")
        return None
