import os
import re
import requests

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

def publish_to_wordpress(article_data, featured_media_id=None, body_image_url=None):
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_pass = os.getenv("WP_APP_PASSWORD")

    if not all([wp_url, wp_user, wp_pass]):
        print("워드프레스 접속 환경변수가 부족합니다.")
        return False

    focus_kw = article_data.get("focus_keyword", "")
    content = article_data.get("content", "")

    # Rank Math SEO 필수: 본문 이미지 + 포커스 키워드 ALT 태그 삽입
    if body_image_url and focus_kw:
        img_html = f'<figure class="wp-block-image"><img src="{body_image_url}" alt="{focus_kw}" class="wp-image"/><figcaption>{focus_kw}</figcaption></figure>'
        if "</h2>" in content:
            content = content.replace("</h2>", f"</h2>\n{img_html}\n", 1)
        else:
            content = img_html + "\n" + content

    endpoint = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    payload = {
        "title": article_data.get("seo_title"),
        "content": content,
        "status": "publish",
        "slug": slugify(focus_kw) if focus_kw else None,
        "featured_media": featured_media_id,
        # Rank Math REST API 데이터 주입
        "meta": {
            "rank_math_focus_keyword": focus_kw,
            "rank_math_title": article_data.get("seo_title"),
            "rank_math_description": article_data.get("meta_description")
        }
    }

    try:
        res = requests.post(endpoint, json=payload, auth=(wp_user, wp_pass), timeout=15)
        if res.status_code == 201:
            print("성공적으로 발행되었습니다!")
            return True
        else:
            print(f"발행 실패 ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"워드프레스 전송 오류: {e}")
    return False
