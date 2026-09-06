import os
import requests

def get_unsplash_image(query):
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        return None
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={access_key}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()['urls']['regular']
    except Exception as e:
        print(f"Unsplash 이미지 가져오기 실패: {e}")
    return None

def upload_image_to_wordpress(image_url, wp_url, wp_user, wp_app_pass, alt_text=""):
    if not image_url:
        return None
    try:
        # 이미지 다운로드
        img_res = requests.get(image_url, timeout=15)
        if img_res.status_code != 200:
            return None
        
        headers = {
            "Content-Disposition": "attachment; filename=featured_image.jpg",
            "Content-Type": "image/jpeg"
        }
        
        # 워드프레스 미디어 라이브러리에 업로드
        upload_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/media"
        res = requests.post(
            upload_url,
            auth=(wp_user, wp_app_pass),
            headers=headers,
            data=img_res.content,
            timeout=30
        )
        
        if res.status_code == 201:
            media_data = res.json()
            media_id = media_data.get("id")
            
            # ALT 태그 지정
            if alt_text and media_id:
                requests.post(
                    f"{upload_url}/{media_id}",
                    auth=(wp_user, wp_app_pass),
                    json={"alt_text": alt_text}
                )
            return media_id
    except Exception as e:
        print(f"워드프레스 미디어 업로드 실패: {e}")
    return None
