import os
import requests

def post_to_wordpress(article_data, media_id=None):
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_app_pass = os.getenv("WP_APP_PASS")

    if not all([wp_url, wp_user, wp_app_pass]):
        print("워드프레스 인증 정보가 누락되었습니다.")
        return False

    # AI가 지정한 category_id (기본값: 시사·사회 122217)
    category_id = article_data.get("category_id", 122217)

    payload = {
        "title": article_data["title"],
        "content": article_data["content"],
        "status": "publish",
        "categories": [category_id]
    }

    if media_id:
        payload["featured_media"] = media_id

    url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    try:
        res = requests.post(
            url, 
            auth=(wp_user, wp_app_pass), 
            json=payload, 
            timeout=30
        )
        if res.status_code == 201:
            print(f"포스팅 성공: {article_data['title']} (카테고리 ID: {category_id})")
            return True
        else:
            print(f"포스팅 실패 (상태 코드 {res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"워드프레스 API 요청 오류: {e}")
        return False
