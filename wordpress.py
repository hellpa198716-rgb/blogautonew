import os
import requests

def get_category_id_by_name(category_name, wp_url, wp_user, wp_password):
    """
    기존 워드프레스 카테고리 이름을 매핑하여 해당 ID를 반환
    """
    category_map = {
        "정부지원금·복지": ["정부지원금·복지", "경제·IT", "경제", "복지"],
        "생활·금융정보": ["생활·금융정보", "생활·트렌드", "생활", "금융"],
        "IT·디지털팁": ["IT·디지털팁", "시사·사회", "IT", "디지털"]
    }
    
    target_name = category_name.strip() if category_name else "생활·금융정보"
    auth = (wp_user, wp_password)
    cat_api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/categories"
    
    try:
        res = requests.get(cat_api_url, params={"per_page": 100}, auth=auth)
        if res.status_code == 200 and res.json():
            wp_categories = res.json()
            
            # 매핑 테이블 기반 ID 조회
            for key, aliases in category_map.items():
                if target_name in aliases or key == target_name:
                    for cat in wp_categories:
                        if cat["name"].strip() in aliases:
                            return cat["id"]
            
            # 직접 일치하는 이름 조회
            for cat in wp_categories:
                if cat["name"].strip().lower() == target_name.lower():
                    return cat["id"]
    except Exception as e:
        print(f"카테고리 ID 조회 중 오류: {e}")
        
    return None

def get_or_create_tag_ids(tags, wp_url, wp_user, wp_password):
    """문자열 태그를 워드프레스 태그 ID 배열로 변환 (400 Bad Request 방지)"""
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
        print("워드프레스 인증 정보 누락")
        return False

    api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/posts"
    headers = {"Content-Type": "application/json"}
    
    title = article_data.get("title", "")
    content = article_data.get("content", "")
    meta_desc = article_data.get("meta_description", "")
    focus_kw = article_data.get("focus_keyword", "")
    slug = article_data.get("slug", "")
    
    # 1. 기존 카테고리 ID 매핑 조회
    category_name = article_data.get("category_name", "생활·금융정보")
    matched_cat_id = get_category_id_by_name(category_name, wp_url, wp_user, wp_password)

    # 2. 카테고리 구성 (요청사항: '트렌드 이슈' ID=1 필수 포함)
    categories = [1]  # ID=1 카테고리 기본 포함
    if matched_cat_id and matched_cat_id != 1:
        categories.append(matched_cat_id)

    # SEO 링크 요소 자동 보완 (DoFollow 외부 링크 및 내부 블로그 링크)
    external_link = f'<p style="margin-top:30px; font-size:0.9em; color:#666;">공식 세부 정보 확인: <a href="https://www.gov.kr" target="_blank" rel="dofollow">정부24 공식 홈페이지</a></p>'
    internal_link = f'<p style="font-size:0.9em; color:#666;">관련 가이드 더보기: <a href="{wp_url.rstrip("/")}">블로그 메인으로 이동</a></p>'
    content += f"\n{external_link}\n{internal_link}"

    tag_ids = get_or_create_tag_ids(article_data.get("tags", []), wp_url, wp_user, wp_password)

    payload = {
        "title": title,
        "content": content,
        "excerpt": meta_desc,
        "status": "publish",
        "categories": categories
    }

    if slug:
        payload["slug"] = slug

    if tag_ids:
        payload["tags"] = tag_ids

    if media_id:
        payload["featured_media"] = int(media_id)

    # Rank Math 및 Yoast SEO 메타 설정
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
            print("워드프레스 정보형 SEO 포스팅 성공!")
            return True
        else:
            print(f"포스팅 실패 (상태 코드 {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"워드프레스 포스팅 예외 발생: {e}")
        return False
