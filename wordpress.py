import os
import requests

def get_or_create_tag_ids(tags, wp_url, wp_user, wp_password):
    """문자열 태그 목록을 워드프레스 태그 ID(integer) 목록으로 변환"""
    if not tags or not isinstance(tags, list):
        return []

    tag_ids = []
    headers = {"Content-Type": "application/json"}
    auth = (wp_user, wp_password)
    tag_api_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/tags"

    for tag_name in tags:
        tag_name = str(tag_name).strip()
        if not tag_name:
            continue
            
        try:
            # 1. 기존 태그 검색
            res = requests.get(tag_api_url, params={"search": tag_name}, auth=auth)
            if res.status_code == 200 and res.json():
                # 정확히 이름이 일치하는 태그 찾기
                matched = next((t for t in res.json() if t["name"].lower() == tag_name.lower()), None)
                if matched:
                    tag_ids.append(matched["id"])
                    continue

            # 2. 존재하지 않으면 새 태그 생성
            create_res = requests.post(tag_api_url, json={"name": tag_name}, auth=auth, headers=headers)
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
    excerpt = article_data.get("excerpt") or article_data.get("meta_description", "")
    category_id = article_data.get("category_id")
    raw_tags = article_data.get("tags", [])
    slug = article_data.get("slug", "")

    # 문자열 태그 목록을 워드프레스 Tag ID(숫자) 목록으로 변환
    tag_ids = get_or_create_tag_ids(raw_tags, wp_url, wp_user, wp_password)

    payload = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "status": "publish"
    }

    if slug:
        payload["slug"] = slug

    if category_id:
        payload["categories"] = [int(category_id)]
    
    # 숫자 ID 형태의 태그 배열 전달
    if tag_ids:
        payload["tags"] = tag_ids

    if media_id:
        payload["featured_media"] = int(media_id)

    # SEO 메타데이터 (Rank Math / Yoast SEO)
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
        
        if response.status_code in [200, 201]:
            print("워드프레스 고품질 SEO 포스팅 성공!")
            return True
        else:
            print(f"포스팅 실패 (상태 코드 {response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"워드프레스 연동 중 오류 발생: {e}")
        return False
