import os
import requests

def get_multiple_unsplash_images(keyword, count=3):
    """Unsplash API에서 키워드 관련 이미지 URL을 지정한 개수만큼 가져오기"""
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        print("UNSPLASH_ACCESS_KEY가 설정되지 않았습니다.")
        return []

    url = f"https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {access_key}"}
    params = {
        "query": keyword,
        "per_page": count,
        "orientation": "landscape"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            image_urls = [photo["urls"]["regular"] for photo in results]
            return image_urls
        else:
            print(f"Unsplash API 오류: {response.status_code}")
            return []
    except Exception as e:
        print(f"Unsplash 이미지 수집 중 예외 발생: {e}")
        return []

def upload_image_to_wordpress(image_url, wp_url, wp_user, wp_password, alt_text=""):
    """이미지 URL을 다운로드하여 워드프레스 미디어 라이브러리에 업로드"""
    try:
        img_res = requests.get(image_url)
        if img_res.status_code != 200:
            return None

        filename = f"image_{os.urandom(4).hex()}.jpg"
        media_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/media"
        
        headers = {
            "Content-Type": "image/jpeg",
            "Content-Disposition": f'attachment; filename="{filename}"'
        }

        res = requests.post(
            media_url,
            auth=(wp_user, wp_password),
            headers=headers,
            data=img_res.content
        )

        if res.status_code in [200, 201]:
            media_id = res.json()["id"]
            if alt_text:
                requests.post(
                    f"{media_url}/{media_id}",
                    auth=(wp_user, wp_password),
                    json={"alt_text": alt_text}
                )
            return media_id
    except Exception as e:
        print(f"이미지 업로드 중 오류: {e}")
    return None
