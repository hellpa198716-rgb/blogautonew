import os
import requests

def post_to_wordpress(title, content, image_url=None):
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_password = os.getenv("WP_APP_PASSWORD")

    if not all([wp_url, wp_user, wp_password]):
        print("워드프레스 인증 정보가 누락되었습니다.")
        return False

    # 워드프레스 API 엔드포인트 설정
    api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": title,
        "content": content,
        "status": "publish"  # 바로 발행하려면 publish, 임시저장은 draft
    }

    try:
        response = requests.post(
            api_url,
            json=payload,
            auth=(wp_user, wp_password),
            headers=headers
        )
        
        if response.status_code == 201:
            print("워드프레스 포스팅 성공!")
            return True
        else:
            print(f"포스팅 실패 (상태 코드 {response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"워드프레스 연동 중 오류 발생: {e}")
        return False
