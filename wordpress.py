import os
import requests

def post_to_wordpress(article_data, media_id=None):
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_password = os.getenv("WP_APP_PASSWORD")

    if not all([wp_url, wp_user, wp_password]):
        print("워드프레스 인증 정보가 누락되었습니다.")
        return False

    api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # article_data 딕셔너리에서 값 추출
    title = article_data.get("title", "")
    content = article_data.get("content", "")
    category_id = article_data.get("category_id")

    payload = {
        "title": title,
        "content": content,
        "status": "publish"  # 즉시 발행
    }

    # 카테고리가 전달된 경우 추가
    if category_id:
        payload["categories"] = [category_id]

    # 업로드된 미디어(이미지) ID가 있는 경우 대표 이미지(Featured Image)로 지정
    if media_id:
        payload["featured_media"] = media_id

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
