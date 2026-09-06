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
    
    # article_data 딕셔너리 데이터 추출
    title = article_data.get("title", "")
    content = article_data.get("content", "")
    excerpt = article_data.get("excerpt") or article_data.get("meta_description", "")
    category_id = article_data.get("category_id")
    tags = article_data.get("tags", [])
    slug = article_data.get("slug", "")

    payload = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "status": "publish"
    }

    if slug:
        payload["slug"] = slug

    # SEO 핵심: 카테고리 및 태그 지정
    if category_id:
        payload["categories"] = [int(category_id)]
    
    if tags and isinstance(tags, list):
        payload["tags"] = tags

    # SEO 핵심: 대표 이미지(Featured Media) 지정
    if media_id:
        payload["featured_media"] = int(media_id)

    # Rank Math / Yoast SEO 플러그인 호환 메타 데이터 추가
    meta_desc = article_data.get("meta_description", "")
    focus_kw = article_data.get("focus_keyword", "")
    if meta_desc or focus_kw:
        payload["meta"] = {
            "rank_math_title": title,
            "rank_math_description": meta_desc,
            "rank_math_focus_keyword": focus_kw,
            "_yoast_wpseo_metadesc": meta_desc,
            "_yoast_wpseo_focuskw": focus_kw
        }

    try:
        response = requests.post(
            api_url,
            json=payload,
            auth=(wp_user, wp_password),
            headers=headers
        )
        
        if response.status_code == 201:
            print("워드프레스 고품질 SEO 포스팅 성공!")
            return True
        else:
            print(f"포스팅 실패 (상태 코드 {response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"워드프레스 연동 중 오류 발생: {e}")
        return False
