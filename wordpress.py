import os
import requests

def get_or_create_category_id(category_name, wp_url, wp_user, wp_password):
    """카테고리 이름을 기반으로 워드프레스 카테고리 ID를 조회하거나 생성"""
    if not category_name:
        return None
    
    auth = (wp_user, wp_password)
    cat_api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/categories"
    
    try:
        # 기존 카테고리 조회
        res = requests.get(cat_api_url, params={"search": category_name}, auth=auth)
        if res.status_code == 200 and res.json():
            for cat in res.json():
                if cat["name"].strip().lower() == category_name.strip().lower():
                    return cat["id"]
        
        # 없으면 신규 생성
        create_res = requests.post(cat_api_url, json={"name": category_name}, auth=auth)
        if create_res.status_code in [200, 201]:
            return create_res.json()["id"]
    except Exception as e:
        print(f"카테고리 처리 중 오류: {e}")
    
    return None

def get_or_create_tag_ids(tags, wp_url, wp_user, wp_password):
    if not tags or not isinstance(tags, list):
        return []

    tag_ids = []
    auth = (wp_user, wp_password)
    tag_api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/tags"

    for tag_name in tags:
        tag_name = str(tag_name).strip()
        if not tag_name:
            continue
            
        try:
            res = requests.get(tag_api_url, params={"search": tag_name}, auth=auth)
            if res.status_code == 200 and res.json():
                matched = next((t for t in res.json() if t["name"].lower() == tag_name.lower()), None)
                if matched:
                    tag_ids.append(matched["id"])
                    continue

            create_res = requests.post(tag_api_url, json={"name": tag_name}, auth=auth)
            if create_res.status_code in [200, 201]:
                tag_ids.append(create_res.json()["id"])
        except Exception as e:
            print(f"태그 처리 중 오류 ('{tag_name}'): {e}")

    return tag_ids

def post_to_wordpress(article_data, media_id=None):
    wp_url = os.getenv("WP_URL")
    wp_user = os.getenv("WP_USER")
    wp_password = os.getenv("WP_APP_PASSWORD")

    if not all([wp_url, wp_user, wp_password]):
        print("워드프레스 인증 정보가 누락되었습니다.")
        return False

    api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
    headers = {"Content-Type": "application/json"}
    
    title = article_data.get("title", "")
    content = article_data.get("content", "")
    meta_desc = article_data.get("meta_description", "")
    focus_kw = article_data.get("focus_keyword", "")
    slug = article_data.get("slug", "")
    
    # 카테고리 명칭을 ID로 자동 변환
    category_name = article_data.get("category_name", "일반")
    category_id = get_or_create_category_id(category_name, wp_url, wp_user, wp_password)

    # SEO 내/외부 링크 보완 (콘텐츠 하단에 자동 추가)
    external_link = f'<p style="margin-top:30px; font-size:0.9em; color:#666;">참고 출처: <a href="https://news.google.com" target="_blank" rel="dofollow">Google News</a></p>'
    internal_link = f'<p style="font-size:0.9em; color:#666;">관련 글 더보기: <a href="{wp_url.rstrip("/")}">블로그 홈으로 이동</a></p>'
    content += f"\n{external_link}\n{internal_link}"

    tag_ids = get_or_create_tag_ids(article_data.get("tags", []), wp_url, wp_user, wp_password)

    payload = {
        "title": title,
        "content": content,
        "excerpt": meta_desc,
        "status": "publish"
    }

    if slug:
        payload["slug"] = slug

    if category_id:
        payload["categories"] = [category_id]
    
    if tag_ids:
        payload["tags"] = tag_ids

    if media_id:
        payload["featured_media"] = int(media_id)

    # Rank Math & Yoast SEO 메타 설정
    if meta_desc or focus_kw:
        payload["meta"] = {
            "rank_math_title": title,
            "rank_math_description": meta_desc,
            "rank_math_focus_keyword": focus_kw,
            "_yoast_wpseo_metadesc": meta_desc,
            "_yoast_wpseo_focuskw": focus_kw
        }

    try:
        response = requests.post(api_url, json=payload, auth=(wp_user, wp_password), headers=headers)
        if response.status_code in [200, 201]:
            print("워드프레스 고품질 SEO 포스팅 성공!")
            return True
        else:
            print(f"포스팅 실패 (상태 코드 {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"워드프레스 연동 오류: {e}")
        return False
