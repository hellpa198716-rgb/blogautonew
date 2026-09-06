# wordpress.py
import os
import requests
from requests.auth import HTTPBasicAuth

def publish_to_wordpress(article_data, featured_media_id=None, body_image_url=None):
    wp_url = os.getenv("WP_URL").rstrip('/')
    wp_user = os.getenv("WP_USER")
    wp_password = os.getenv("WP_APP_PASSWORD")
    
    api_endpoint = f"{wp_url}/wp-json/wp/v2/posts"
    
    title = article_data.get("seo_title")
    content = article_data.get("content", "")
    focus_keyword = article_data.get("focus_keyword", "")
    meta_desc = article_data.get("meta_description", "")

    # 본문 중간에 ALT 태그 포함된 이미지 삽입
    if body_image_url and focus_keyword:
        image_html = f'<figure class="wp-block-image"><img src="{body_image_url}" alt="{focus_keyword}" /><figcaption>{focus_keyword} 관련 안내</figcaption></figure>'
        # 서론 지나 첫 H2 태그 직전에 이미지 삽입
        if "<h2>" in content:
            content = content.replace("<h2>", f"{image_html}<h2>", 1)
        else:
            content = image_html + content

    payload = {
        "title": title,
        "content": content,
        "status": "publish",
        "slug": focus_keyword.replace(" ", "-"),
        "featured_media": featured_media_id if featured_media_id else 0,
        "meta": {
            "rank_math_focus_keyword": focus_keyword,
            "rank_math_title": title,
            "rank_math_description": meta_desc
        }
    }
    
    response = requests.post(
        api_endpoint,
        json=payload,
        auth=HTTPBasicAuth(wp_user, wp_password)
    )
    
    if response.status_code == 201:
        print(f"성공적으로 워드프레스에 발행되었습니다 (포커스 키워드: {focus_keyword})")
        return True
    else:
        print(f"발행 실패: {response.status_code} - {response.text}")
        return False
